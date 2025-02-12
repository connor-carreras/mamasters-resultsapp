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

q_insert_vola_temp = """
insert into vola_results_temp 
select
'{selected_season}' as season,
upper('{selected_race}') as racekey,
regexp_replace_all(json_pointer_extract(full_text, '/Fisresults/Raceheader/Discipline'),'\"','') as racetype,  
upper(regexp_replace_all(json_pointer_extract(full_text, '/Fisresults/Raceheader/Place'),'\"','')) as mountain,
regexp_replace_all(json_pointer_extract(full_text, '/Fisresults/Raceheader/Eventname'),'\"','') as racename,
to_date(
    (regexp_replace_all(json_pointer_extract(full_text, '/Fisresults/Raceheader/Racedate/Year'),'\"','')::text || '-' ||
    regexp_replace_all(json_pointer_extract(full_text, '/Fisresults/Raceheader/Racedate/Month'),'\"','')::text || '-' ||
  regexp_replace_all(json_pointer_extract(full_text, '/Fisresults/Raceheader/Racedate/Day'),'\"','')::text), 'YYYY-MM-DD'
) as racedate,
regexp_replace_all(json_pointer_extract(results_array,'/Bib'),'\"','') as bib,
regexp_replace_all(json_pointer_extract(results_array,'/Competitor/Lastname'),'\"','') || ', ' || regexp_replace_all(json_pointer_extract(results_array,'/Competitor/Firstname'),'\"','') as name,
regexp_replace_all(json_pointer_extract(results_array,'/Competitor/NAT_code'),'\"','') as ussanumber,
regexp_replace_all(json_pointer_extract(results_array,'/Competitor/Yearofbirth'),'\"','') as year_of_birth,
regexp_replace_all(json_pointer_extract(results_array, '/Competitor/Gender'),'\"','') as gender,
regexp_replace_all(json_pointer_extract(results_array, '/MA_result/Timerun1'),'\"','') as run1,
regexp_replace_all(json_pointer_extract(results_array, '/MA_result/Timerun2'),'\"','') as run2,
regexp_replace_all(json_pointer_extract(results_array, '/MA_result/Totaltime'),'\"','') as total,
$source_file_timestamp as ingest_ts
from ex_vola_results,
unnest(JSON_POINTER_EXTRACT_ARRAY(full_text, '/Fisresults/MA_race/MA_classified/MA_ranked')) as r(results_array)
where TO_YYYYMMDD($source_file_timestamp) = to_yyyymmdd(current_date())
union all
select
'{selected_season}' as season,
upper('{selected_race}') as racekey,
regexp_replace_all(json_pointer_extract(full_text, '/Fisresults/Raceheader/Discipline'),'\"','') as racetype,  
upper(regexp_replace_all(json_pointer_extract(full_text, '/Fisresults/Raceheader/Place'),'\"','')) as mountain,
regexp_replace_all(json_pointer_extract(full_text, '/Fisresults/Raceheader/Eventname'),'\"','') as racename,
to_date(
    (regexp_replace_all(json_pointer_extract(full_text, '/Fisresults/Raceheader/Racedate/Year'),'\"','')::text || '-' ||
    regexp_replace_all(json_pointer_extract(full_text, '/Fisresults/Raceheader/Racedate/Month'),'\"','')::text || '-' ||
  regexp_replace_all(json_pointer_extract(full_text, '/Fisresults/Raceheader/Racedate/Day'),'\"','')::text), 'YYYY-MM-DD'
) as racedate,
regexp_replace_all(json_pointer_extract(results_array,'/Bib'),'\"','') as bib,
regexp_replace_all(json_pointer_extract(results_array,'/Competitor/Lastname'),'\"','') || ', ' || regexp_replace_all(json_pointer_extract(results_array,'/Competitor/Firstname'),'\"','') as name,
regexp_replace_all(json_pointer_extract(results_array,'/Competitor/NAT_code'),'\"','') as ussanumber,
regexp_replace_all(json_pointer_extract(results_array,'/Competitor/Yearofbirth'),'\"','') as year_of_birth,
regexp_replace_all(json_pointer_extract(results_array, '/Competitor/Gender'),'\"','') as gender,
regexp_replace_all(json_pointer_extract(results_array, '/MA_result/Timerun1'),'\"','') as run1,
regexp_replace_all(json_pointer_extract(results_array, '/MA_result/Timerun2'),'\"','') as run2,
regexp_replace_all(json_pointer_extract(results_array, '/MA_result/Totaltime'),'\"','') as total,
$source_file_timestamp as ingest_ts
from ex_vola_results,
unnest(JSON_POINTER_EXTRACT_ARRAY(full_text, '/Fisresults/MA_race/MA_notclassified/MA_notranked')) as r(results_array)
where TO_YYYYMMDD($source_file_timestamp) = to_yyyymmdd(current_date())
"""

q_insert_vola_to_results = """
insert into results
with add_classes as (
select r.* exclude year_of_birth, c.class
  from vola_results_temp r
  inner join classes c 
  on r.year_of_birth::integer >= c.start_year
  and r.year_of_birth::integer <= c.end_year
  where c.season = '{selected_season}'
)

select 
season, 
racekey, 
  mountain as raceseries, 
  mountain as division, 
  mountain, 
  racename, 
  case when racetype = 'SG' then 'Super-G'
  when racetype = 'GS' then 'Giant Slalom'
  when racetype = 'SL' then 'Slalom'
  else racetype end
  as racetype, 
  racedate, 
  bib, 
  name, 
  ussanumber, 
  class, 
  case when gender = 'L' then 'F' else gender end as gender, 
case when (case when run1 not ilike 'D%' then split_part(run1, '.',2)::integer*10 else 0 end +
  case when substring(run1 from 0 for position(':' in run1)) != '' then substring(run1 from 0 for position(':' in run1))::integer*60*1000 else 0 end +
  case when run1 not ilike 'D%' then substring(substring(run1 from position(':' in run1)+1 for (position('.' in run1)-position(':' in run1))) from 0 for 3)::integer*1000 else 0 end) = 0 then null else
  (case when run1 not ilike 'D%' then split_part(run1, '.',2)::integer*10 else 0 end +
  case when substring(run1 from 0 for position(':' in run1)) != '' then substring(run1 from 0 for position(':' in run1))::integer*60*1000 else 0 end +
  case when run1 not ilike 'D%' then substring(substring(run1 from position(':' in run1)+1 for (position('.' in run1)-position(':' in run1))) from 0 for 3)::integer*1000 else 0 end) end as run1,
  case when run1 = 'DNF' then 1 else null end as run1_dnf,
case when run1 = 'DSQ' then 1 else null end as run1_dsq, 
case when 
  (case when run2 not ilike 'D%' then split_part(run2, '.',2)::integer*10 else 0 end +
  case when substring(run2 from 0 for position(':' in run2)) != '' then substring(run2 from 0 for position(':' in run2))::integer*60*1000 else 0 end +
  case when run2 not ilike 'D%' then substring(substring(run2 from position(':' in run2)+1 for (position('.' in run2)-position(':' in run2))) from 0 for 3)::integer*1000 else 0 end) = 0 then null else
  (case when run2 not ilike 'D%' then split_part(run2, '.',2)::integer*10 else 0 end +
  case when substring(run2 from 0 for position(':' in run2)) != '' then substring(run2 from 0 for position(':' in run2))::integer*60*1000 else 0 end +
  case when run2 not ilike 'D%' then substring(substring(run2 from position(':' in run2)+1 for (position('.' in run2)-position(':' in run2))) from 0 for 3)::integer*1000 else 0 end) end as run2,
  case when run2 = 'DNF' then 1 else null end as run2_dnf, 
  case when run2 = 'DSQ' then 1 else null end as run2_dsq, 
case when 
  (case when total not ilike 'D%' then split_part(total, '.',2)::integer*10 else 0 end +
  case when substring(total from 0 for position(':' in total)) != '' then substring(total from 0 for position(':' in total))::integer*60*1000 else 0 end +
  case when total not ilike 'D%' then substring(substring(total from position(':' in total)+1 for (position('.' in total)-position(':' in total))) from 0 for 3)::integer*1000 else 0 end) = 0 then null else
  (case when total not ilike 'D%' then split_part(total, '.',2)::integer*10 else 0 end +
  case when substring(total from 0 for position(':' in total)) != '' then substring(total from 0 for position(':' in total))::integer*60*1000 else 0 end +
  case when total not ilike 'D%' then substring(substring(total from position(':' in total)+1 for (position('.' in total)-position(':' in total))) from 0 for 3)::integer*1000 else 0 end) end as total,
   ingest_ts
from add_classes;
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

