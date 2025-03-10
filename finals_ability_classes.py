q_class_list = """
select case when gender = 'F' then 'Women' when gender = 'M' then 'Men' end as gender_header, gender, 
case when ability_class = 'Super Elite' then 1
when ability_class = 'Elite' then 2
when ability_class = 'Class A' then 3
when ability_class = 'Class B' then 4
when ability_class = 'Class C' then 5 end as ordering,
ability_class
from (
select distinct gender, ability_class
from ability_classes where season='{selected_season}') order by 2, 3
"""

q_ability_scores = """
with results as (
select racekey, name, ussanumber, gender, ingest_ts, season, run1, run2, run1_dnf, run1_dsq, run2_dnf, run2_dsq,
case when (run1_dsq is not null or run2_dsq is not null) then null else total end as total
from results_vw where racekey in('HUNTER MOUNTAIN, FINALS GS 2, 2025-03-08')
)

, ability_participants as (
select r.*, p.ability_class 
  from results r 
inner join 
(select * from ability_classes 
where gender = '{gender}'
and ability_class = '{ability_class}') p 
on r.ussanumber = p.ussanum
and r.season = p.season
)

, ranked as (
  
select r.racekey, r.name, r.gender, r.ability_class,
  case when total is null then null else rank end as race_rank_by_ability_class,
  case when run1_dsq = '1' then 'DSQ'
when run1_dnf = 1 then 'DNF'
when run1 is null and run2 is null then 'DNS'
when run1 is null and run2 is not null then 'DNS'
else substring(((run1/60000)::text || ':' || lpad((floor(((run1-((run1/60000)*60000))::decimal/1000),2)::text),12,'0')) from 1 for 7) end as run1,
case 
when run2_dsq = '1' then 'DSQ'
when run2_dnf = 1 then 'DNF'
when run1 is null and run2 is null then 'DNS'
when run2 is null and run1 is not null then 'DNS' 
else substring(((run2/60000)::text || ':' || lpad((floor(((run2-((run2/60000)*60000))::decimal/1000),2)::text),12,'0')) from 1 for 7) end as run2,
substring(((total/60000)::text || ':' || lpad((floor(((total-((total/60000)*60000))::decimal/1000),2)::text),12,'0')) from 1 for 7) as total,

  from 
(select *,
rank() over (partition by racekey, gender, ability_class order by total) as rank
from ability_participants
) r

)

  select * from ranked;
"""