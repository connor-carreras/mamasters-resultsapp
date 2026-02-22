q_class_list = """
select case when gender = 'F' then 'Women' when gender = 'M' then 'Men' end as gender_header, gender, ability_class
from (
select distinct gender, ability_class
from pa_cup where season='{selected_season}') order by 2, 3 desc
"""

q_pa_cup_2025 = """
with results as (
select racekey, name, ussanumber, gender, ingest_ts, season, 
case when (run1_dsq is not null or run2_dsq is not null) then null else total end as total
from mamasters.results_vw where racekey in(
select distinct racename from mamasters.schedule where is_pa_cup is true and season = '{selected_season}'
)
)

, pa_participants as (
select r.*, p.ability_class 
  from results r 
inner join mamasters.pa_cup p 
on r.ussanumber = p.ussanum
and r.season = p.season
where p.gender = '{gender}'
and p.ability_class = '{ability_class}'
)

, ranked as (
  select *, 
  sum(points) over (partition by name) as total_points 
  from
  (
select r.racekey, r.name, r.gender, r.ability_class,
  case when total is null then null else rank end as race_rank_by_ability_class,
  case when total is null then 0 else p.points end as points
  from 
(select *,
rank() over (partition by racekey, gender, ability_class order by total) as rank
from pa_participants
) r
left join mamasters.old_worldcup_points p 
on r.rank = p.place
)
)

  , sorted as (
  select *,
  dense_rank() over (partition by gender, ability_class order by total_points desc) as overall_rank
  from ranked
  )

PIVOT sorted
ON racekey
USING any_value(points || ' ('||(case when race_rank_by_ability_class is null then 'DNF' else race_rank_by_ability_class::text end)||')')
group by overall_rank, name, total_points, gender, ability_class
order by gender, ability_class, overall_rank asc;
"""