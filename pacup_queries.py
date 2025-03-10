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
from results_vw where racekey in('BIG BOULDER, SLALOM, 2025-02-21', 'MONTAGE MOUNTAIN, GIANT SLALOM, 2025-02-23', 'MONTAGE MOUNTAIN, SLALOM, 2025-02-23')
)

, pa_participants as (
select r.*, p.ability_class 
  from results r 
inner join pa_cup p 
on r.ussanumber = p.ussanum
and r.season = p.season
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
left join old_worldcup_points p 
on r.rank = p.place
)
)

  , sorted as (
  select *,
  dense_rank() over (partition by gender, ability_class order by total_points desc) as overall_rank
	from ranked
  )

select 
  overall_rank,
name, 
  gender,
  ability_class,
total_points,
case when max(bouldersl) is null then '--' else max(bouldersl) end as bouldersl,
    case when max(montagegs) is null then '--' else max(montagegs) end as montagegs,
    case when max(montagesl) is null then '--' else max(montagesl) end as montagesl,
      from(
select  
  overall_rank,
  name,
  gender,
  ability_class,
  total_points,
  case when racekey = 'BIG BOULDER, SLALOM, 2025-02-21' then points || ' ('||(case when race_rank_by_ability_class is null then 'DNF' else race_rank_by_ability_class::text end)||')' else null end as bouldersl,
case when racekey = 'MONTAGE MOUNTAIN, GIANT SLALOM, 2025-02-23' then points || ' ('||(case when race_rank_by_ability_class is null then 'DNF' else race_rank_by_ability_class::text end)||')' else null end as montagegs,
case when racekey = 'MONTAGE MOUNTAIN, SLALOM, 2025-02-23' then points || ' ('||(case when race_rank_by_ability_class is null then 'DNF' else race_rank_by_ability_class::text end)||')' else null end as montagesl,
  from sorted
  )
group by all
order by gender, ability_class desc, overall_rank;
"""