q_insert_results = """
insert into results
with base as (
select 
'{selected_season}' as season,
'{selected_race}' as racekey,
upper((json_extract_string(SST_USSA_FIS_Race, '/Men/Header/ClubName'))) as raceseries,  
upper((json_extract_string(SST_USSA_FIS_Race, '/Men/Header/Division'))) as division,
upper((json_extract_string(SST_USSA_FIS_Race, '/Men/Header/SkiAreaName'))) as mountain,
(json_extract_string(SST_USSA_FIS_Race, '/Men/Header/RaceName')) as racename,
(json_extract_string(SST_USSA_FIS_Race, '/Men/RTData/RTRaceType')) as racetype,
strptime((date '1899-12-30' + (json_extract_string(SST_USSA_FIS_Race, '/Men/Header/RaceDate'))::integer)::text,'%Y-%m-%d') as racedate,
unnest(json_extract(SST_USSA_FIS_Race, '/Men/Comp')::json[]) as results_array
from (select * from read_json(
's3://mamasters-results/{name}',
ignore_errors = true
)
)
)

select * exclude results_array,
(json_extract_string(results_array,'/Bib')) as bib,
(json_extract_string(results_array,'/Name')) as name,
(json_extract_string(results_array,'/USSANumber')) as ussanumber,
(json_extract_string(results_array,'/CompClass')) as class,
(json_extract_string(results_array, '/MastersSex')) as gender,
((json_extract_string(results_array, '/Time1/MicroFinish'))::bigint -
(json_extract_string(results_array, '/Time1/MicroStart'))::bigint) / 1000::integer as run1,
  case when ((json_extract_string(results_array, '/Time1/Status'))::bigint) = 2 then 1 else null end as run1_dnf,
case when ((json_extract_string(results_array, '/Time1/Status'))::bigint) = 4 then 1 else null end as run1_dsq,
((json_extract_string(results_array, '/Time2/MicroFinish'))::bigint - 
(json_extract_string(results_array, '/Time2/MicroStart'))::bigint) /1000::integer as run2,
  case when ((json_extract_string(results_array, '/Time2/Status'))::bigint) = 2 then 1 else null end as run2_dnf,
case when ((json_extract_string(results_array, '/Time2/Status'))::bigint) = 4 then 1 else null end as run2_dsq,
(((json_extract_string(results_array, '/Time1/MicroFinish'))::bigint -
(json_extract_string(results_array, '/Time1/MicroStart'))::bigint) / 1000) +
(((json_extract_string(results_array, '/Time2/MicroFinish'))::bigint - 
(json_extract_string(results_array, '/Time2/MicroStart'))::bigint) /1000)::integer as total,
current_localtimestamp() as ingest_ts
from base
;
"""

q_insert_vola_temp = """
insert into vola_results_temp 
with base1 as (
select
'{filename}',
'{selected_season}' as season,
'{selected_race}' as racekey,
json_extract_string(Fisresults, '/Raceheader/Discipline') as racetype,  
upper(json_extract_string(Fisresults, '/Raceheader/Place')) as mountain,
json_extract_string(Fisresults, '/Raceheader/Eventname') as racename,
strptime(json_extract_string(Fisresults, '/Raceheader/Racedate/Year')::text || '-' ||
    json_extract_string(Fisresults, '/Raceheader/Racedate/Month')::text || '-' ||
  json_extract_string(Fisresults, '/Raceheader/Racedate/Day')::text, '%Y-%m-%d'
) as racedate,
unnest(json_extract(Fisresults, '/MA_race/MA_classified/MA_ranked')::json[]) as results_array
from (select Fisresults from read_json(
's3://mamasters-results/{name}',
ignore_errors = true
)
)
)

, base2 as (
select
'{filename}',
'{selected_season}' as season,
'{selected_race}' as racekey,
json_extract_string(Fisresults, '/Raceheader/Discipline') as racetype,  
upper(json_extract_string(Fisresults, '/Raceheader/Place')) as mountain,
json_extract_string(Fisresults, '/Raceheader/Eventname') as racename,
strptime(json_extract_string(Fisresults, '/Raceheader/Racedate/Year')::text || '-' ||
    json_extract_string(Fisresults, '/Raceheader/Racedate/Month')::text || '-' ||
  json_extract_string(Fisresults, '/Raceheader/Racedate/Day')::text, '%Y-%m-%d'
) as racedate,
unnest(json_extract(Fisresults, '/MA_race/MA_classified/MA_notranked')::json[]) as results_array
from (select Fisresults from read_json(
's3://mamasters-results/{name}',
ignore_errors = true
)
)
)

select season,
racekey, 
racetype, 
mountain, 
racename, 
racedate, 
json_extract_string(results_array,'/Bib') as bib,
json_extract_string(results_array,'/Competitor/Lastname') || ', ' || json_extract_string(results_array,'/Competitor/Firstname') as name,
json_extract_string(results_array,'/Competitor/NAT_code') as ussanumber,
json_extract_string(results_array,'/Competitor/Yearofbirth') as year_of_birth,
json_extract_string(results_array, '/Competitor/Gender') as gender,
json_extract_string(results_array, '/MA_result/Timerun1') as run1,
json_extract_string(results_array, '/MA_result/Timerun2') as run2,
json_extract_string(results_array, '/MA_result/Totaltime') as total,
current_localtimestamp() as ingest_ts
from base1,
union all
select season,
racekey, 
racetype, 
mountain, 
racename, 
racedate, 
json_extract_string(results_array,'/Bib') as bib,
json_extract_string(results_array,'/Competitor/Lastname') || ', ' || json_extract_string(results_array,'/Competitor/Firstname') as name,
json_extract_string(results_array,'/Competitor/NAT_code') as ussanumber,
json_extract_string(results_array,'/Competitor/Yearofbirth') as year_of_birth,
json_extract_string(results_array, '/Competitor/Gender') as gender,
json_extract_string(results_array, '/MA_result/Timerun1') as run1,
json_extract_string(results_array, '/MA_result/Timerun2') as run2,
json_extract_string(results_array, '/MA_result/Totaltime') as total,
current_localtimestamp() as ingest_ts
from base2
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
select racename as racename from schedule
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
insert into members
select
"First Name" as firstname,
"Last Name" as lastname,
"YOB" as yob,
"Gender" as gender,
"USSA#" as ussanum,
"Team" as team,
"Registration Date" as registration_date,
"USSA# Status" as ussa_status,
current_localtimestamp() as last_update_ts,
'{selected_season}' as season
from read_csv(
's3://mamasters-results/mam_members.csv',
ignore_errors = true
)
"""

q_update_members = """
update members 
set season = '{selected_season}'
where last_update_ts = (select max(last_update_ts) from members);
"""

q_show_members = """
select * 
from members 
where last_update_ts = (select max(last_update_ts) from members)
"""


