q_overall_results_exist = """
select count(*) as num_records from results_overall
where racekey = '{selected_option}'
"""

q_select_overall_results = """
select 
race_rank_overall,
name,
class,
gender,
run1,
run2,
total,
from results_overall
where racekey = '{selected_option}'
and insert_ts = (select max(insert_ts) from results_overall where racekey = '{selected_option}')
order by race_rank_overall, run1, run2
"""

q_insert_overall_results = """
insert into results_overall as
with results_with_dsq as (
select raceseries, division, mountain, racekey, racetype, racedate, bib, name, ussanumber, class, gender, ingest_ts, season, run1_dnf, run2_dnf,
run2,
run2_dsq,
run1,
run1_dsq,
case when (run1_dsq is not null or run2_dsq is not null) then null else total end as total
from results_vw where racekey = '{selected_option}'
)
  
, ranked_results as (
select *,
rank() over (partition by racekey order by total) as race_rank_overall
from results_with_dsq
)

, corrected_points as (
select raceseries, season, division, mountain, racekey, racetype, racedate, bib, name, ussanumber, class, gender, run1, run2, total, ingest_ts, run1_dsq, run2_dsq, run1_dnf, run2_dnf,
case when total is null then null else race_rank_overall end as race_rank_overall,
from ranked_results
)
  
select
a.season,
a.mountain,
a.racekey,
a.racetype,
a.racedate,
a.name,
a.ussanumber,
a.class,
a.gender,
a.race_rank_overall,
case when run1_dsq = '1' then 'DSQ'
when run1_dnf = 1 then 'DNF'
when run1 is null and run2 is null then 'DNS'
when run1 is null and run2 is not null then 'DNS'
else substring(((a.run1/60000)::text || ':' || lpad((floor(((a.run1-((a.run1/60000)*60000))::decimal/1000),2)::text),12,'0')) from 1 for 7) end as run1,
case 
when run2_dsq = '1' then 'DSQ'
when run2_dnf = 1 then 'DNF'
when run1 is null and run2 is null then 'DNS'
when run2 is null and run1 is not null then 'DNS' 
else substring(((a.run2/60000)::text || ':' || lpad((floor(((a.run2-((a.run2/60000)*60000))::decimal/1000),2)::text),12,'0')) from 1 for 7) end as run2,
substring(((a.total/60000)::text || ':' || lpad((floor(((a.total-((a.total/60000)*60000))::decimal/1000),2)::text),12,'0')) from 1 for 7) as total,
date_trunc('second', current_timestamp()) as insert_ts
from
corrected_points a;
"""