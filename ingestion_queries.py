q_insert_results = """
insert into results
select 
'{selected_season}' as season,
upper('{selected_race}') as racekey,
upper(regexp_replace_all(json_pointer_extract(full_text, '/SST_USSA_FIS_Race/Men/Header/ClubName'),'\"','')) as raceseries,  
upper(regexp_replace_all(json_pointer_extract(full_text, '/SST_USSA_FIS_Race/Men/Header/Division'),'\"','')) as division,
upper(regexp_replace_all(json_pointer_extract(full_text, '/SST_USSA_FIS_Race/Men/Header/SkiAreaName'),'\"','')) as mountain,
regexp_replace_all(json_pointer_extract(full_text, '/SST_USSA_FIS_Race/Men/Header/RaceName'),'\"','') as racename,
regexp_replace_all(json_pointer_extract(full_text, '/SST_USSA_FIS_Race/Men/RTData/RTRaceType'),'\"','') as racetype,
to_date(date_add('day',regexp_replace_all(json_pointer_extract(full_text, '/SST_USSA_FIS_Race/Men/Header/RaceDate'),'\"','')::integer,'1899-12-30')::text,'YYYY-MM-DD') as racedate,
regexp_replace_all(json_pointer_extract(results_array,'/Bib'),'\"','') as bib,
regexp_replace_all(json_pointer_extract(results_array,'/Name'),'\"','') as name,
regexp_replace_all(json_pointer_extract(results_array,'/USSANumber'),'\"','') as ussanumber,
regexp_replace_all(regexp_replace_all(json_pointer_extract(results_array,'/CompClass'),'\"',''), 'F|M','') as class,
regexp_replace_all(json_pointer_extract(results_array, '/MastersSex'),'\"','') as gender,
(regexp_replace_all(json_pointer_extract(results_array, '/Time1/MicroFinish'),'\"','')::bigint -
regexp_replace_all(json_pointer_extract(results_array, '/Time1/MicroStart'),'\"','')::bigint) / 1000::integer as run1,
  case when (regexp_replace_all(json_pointer_extract(results_array, '/Time1/Status'),'\"','')::bigint) = 2 then 1 else null end as run1_dnf,
case when (regexp_replace_all(json_pointer_extract(results_array, '/Time1/Status'),'\"','')::bigint) = 4 then 1 else null end as run1_dsq,
(regexp_replace_all(json_pointer_extract(results_array, '/Time2/MicroFinish'),'\"','')::bigint - 
regexp_replace_all(json_pointer_extract(results_array, '/Time2/MicroStart'),'\"','')::bigint) /1000::integer as run2,
   case when (regexp_replace_all(json_pointer_extract(results_array, '/Time2/Status'),'\"','')::bigint) = 2 then 1 else null end as run2_dnf,
case when (regexp_replace_all(json_pointer_extract(results_array, '/Time2/Status'),'\"','')::bigint) = 4 then 1 else null end as run2_dsq,
((regexp_replace_all(json_pointer_extract(results_array, '/Time1/MicroFinish'),'\"','')::bigint -
regexp_replace_all(json_pointer_extract(results_array, '/Time1/MicroStart'),'\"','')::bigint) / 1000) +
((regexp_replace_all(json_pointer_extract(results_array, '/Time2/MicroFinish'),'\"','')::bigint - 
regexp_replace_all(json_pointer_extract(results_array, '/Time2/MicroStart'),'\"','')::bigint) /1000)::integer as total,
$source_file_timestamp as ingest_ts
from ex_results,
unnest(JSON_POINTER_EXTRACT_ARRAY(full_text, '/SST_USSA_FIS_Race/Men/Comp')) as r(results_array)
where TO_YYYYMMDD($source_file_timestamp) = to_yyyymmdd(current_date())
"""

q_races_list = """
select upper(racename) as racename from schedule
where season = '{selected_season}'
order by racedate
"""

q_show_results = """
select * 
from results 
where ingest_ts = (select max(ingest_ts) from results)
order by gender,class
"""

q_copy_members = """
copy members 
(
firstname $2,
lastname $3,
yob $4,
gender $5,
ussanum $6,
team $9,
registration_date $10,
ussa_status $11,
last_update_ts $source_file_timestamp
)
from 
's3://mamasters-results/mam_members.csv'
WITH 
CREDENTIALS = (AWS_ROLE_ARN = 'arn:aws:iam::664418987828:role/firebolt-s3-access')
TYPE=CSV HEADER=TRUE;
"""

q_update_members = """
update members 
set season = '{selected_season}'
where last_update_ts = (select max(last_update_ts) 
from members);
"""

q_show_members = """
select * 
from members 
where last_update_ts = (select max(last_update_ts) from members)
"""

q_dsq_races_list = """
select racekey from (
select distinct racekey, racedate from results_vw 
where racekey in(select upper(racename) as racename from schedule
where season = '{selected_season}')
order by racedate
)
"""

q_dsq_mountain = """
select distinct mountain 
from results_vw
where racekey = '{selected_race}'
"""

q_dsq_date = """
select distinct racedate 
from results_vw
where racekey = '{selected_race}'
"""

q_dsq_type = """
select distinct racetype 
from results_vw
where racekey = '{selected_race}'
"""

q_dsq_names = """
select distinct name from results_vw
where racekey = '{selected_race}' order by 1;
"""

q_dsq_insert_run1 = """
insert into dsq values
('{datestring}', '{mountainstring}', '{typestring}', '{selected_race}', 'run1', {racers}, '{insert_time}');
"""

q_dsq_insert_run2 = """
insert into dsq values
('{datestring}', '{mountainstring}', '{typestring}', '{selected_race}', 'run2', {racers2}, '{insert_time}');
"""

q_dsq_exists = """
select count(distinct run) as num_records from dsq_vw
where racename = '{selected_race}'
"""

q_show_dsqs = """
select racename, run as dsq_run, racer
  from dsq_vw, unnest(racers) as r(racer)
  where racename = '{selected_race}'
order by 2, 3
"""

