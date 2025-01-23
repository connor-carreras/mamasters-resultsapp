q_teams_list = """
select distinct team, team_rank, 
team_total, worldcup_points_by_team as points
from team_results where racekey='{selected_option}' and insert_ts = (select max(insert_ts) from team_results where racekey='{selected_option}' ) order by team_rank
"""

q_team_results_exist = """
select count(*) as num_records from team_results
where racekey = '{selected_option}'
"""

q_team_results = """
select 
name,
class,
gender,
run1_adjusted,
run2_adjusted,
total_adjusted,
ranking,
counting_score
from team_results where racekey='{selected_option}' and insert_ts = (select max(insert_ts) from team_results where racekey='{selected_option}') and team='{team}'
"""

q_insert_teams = """
insert into team_results
with results_with_dsq as (
select raceseries, division, mountain, racekey, racetype, racedate, bib, name, ussanumber, class, gender, ingest_ts, season, run1_dnf, run2_dnf,
run2,
run2_dsq,
run1,
run1_dsq,
total
from results_vw where racekey = '{selected_option}'
)

, handicapped_times as (
select a.*, b.handicap, 
floor(a.run1*b.handicap) as run1_adjusted,
floor(a.run2*b.handicap) as run2_adjusted,
floor(a.total*b.handicap) as total_adjusted
from
(select r.racekey, r.racedate, r.racetype, r.name, r.ussanumber, m.team, r.class, r.gender, r.run1, r.run2, r.total, r.season, r.run1_dsq, r.run2_dsq, r.run1_dnf, r.run2_dnf
from results_with_dsq r 
inner join 
(select * from members_vw where team <> '' and season = '{selected_season}') m
on r.ussanumber = m.ussanum
) a 
inner join 
(select * from team_handicaps
where hc_label = 'MAMS-HC2') b 
on a.racetype = b.discipline
and a.class = b.class::text
and a.gender = b.gender
)

, ghost as (
select * from
(select 
team,
concat('Ghost Racer ',series) as name,
ghost_total/2 as run1,
ghost_total/2 as run2,
ghost_total as total,
from (
select max(total_adjusted)+30000 as ghost_total,
array_distinct(array_agg(team)) as team_array,
series
from handicapped_times, generate_series(1,4,1) r(series)
group by all
), unnest(team_array) as r(team)
)
cross join
(select distinct racekey, racedate, racetype, season from handicapped_times)
)

,ranked_and_filtered as (
select *, 
case when ranking <= 4 then 'x' else '' end as counting_score
from (
select *, 
dense_rank() over (partition by team order by total_adjusted, name) as ranking
from
(
select season, racedate, racekey, racetype, name, team, class, gender, run1_adjusted, run2_adjusted, total_adjusted, run1_dsq, run2_dsq, run1_dnf, run2_dnf 
from handicapped_times
union 
select season, racedate, racekey, racetype, name, team, 'N/A', 'N/A', 
run1, run2, total, null, null, null, null from ghost
)
)
where 
(name not like 'Ghost Racer%')
or (name like 'Ghost Racer%' and ranking <= 4)
)


,team_totals as (
select a.*, b.team_total, b.team_rank
from (select * from ranked_and_filtered) a 
inner join (
select *, rank() over (order by team_total) as team_rank from (
select sum(total_adjusted) as team_total, team from ranked_and_filtered
where counting_score = 'x'
group by all
)
) b
on a.team = b.team
)

select 
  season,
  racedate,
  racekey,
  racetype,
  name,
  team,
  class,
  gender,
  run1_adjusted,
  run2_adjusted,
  total_adjusted,
  case when (run1_adjusted ilike 'D%' or run2_adjusted ilike 'D%') then null else ranking end as ranking,
  counting_score,
  team_total,
  team_rank,
  ifnull(p.points,0) as worldcup_points_by_team, 
  date_trunc('second', current_timestamp()) as insert_ts
  from (  
select 
  season,
  racedate,
  racekey,
  racetype,
team,
name,
class,
gender,
case when run1_dsq = '1' then 'DSQ'
when run1_dnf = 1 then 'DNF'
when run1 is null and run2 is null then 'DNS'
when run1 is null and run2 is not null then 'DNS'
else 
  floor(run1_adjusted::integer/60000)::text || ':' ||
substring(lpad(((run1_adjusted-(floor(run1_adjusted/60000)*60000))/1000)::text,12,'0') from 1 for 5) end as run1_adjusted,
case 
when run2_dsq = '1' then 'DSQ'
when run2_dnf = 1 then 'DNF'
when run1 is null and run2 is null then 'DNS'
when run2 is null and run1 is not null then 'DNS' 
else 
floor(run2_adjusted::integer/60000)::text || ':' ||
substring(lpad(((run2_adjusted-(floor(run2_adjusted/60000)*60000))/1000)::text,12,'0') from 1 for 5) end as run2_adjusted,
floor(total_adjusted::integer/60000)::text || ':' || 
substring(lpad(((total_adjusted-(floor(total_adjusted/60000)*60000))/1000)::text,12,'0') from 1 for 5) as total_adjusted,
ranking,
counting_score,
  team_rank,
  floor(team_total::integer/60000)::text || ':' || 
substring(lpad(((team_total-(floor(team_total/60000)*60000))/1000)::text,12,'0') from 1 for 5) as team_total
from team_totals) t
left join worldcup_points p
on t.team_rank = p.place
"""