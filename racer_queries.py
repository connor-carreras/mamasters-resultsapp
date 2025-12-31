q_racer_results = """
with by_gender as (
select 
a.racekey, 
a.race_rank_by_gender::text || ' (' || b.total_participants::text || ')' as race_rank_by_gender,
a.class,
a.gender,
a.run1,
a.run2,
a.total,
a.race_points as race_points_by_gender,
a.season
from results_by_gender a 
inner join 
  (select racekey, gender, max(race_rank_by_gender) as total_participants from results_by_gender group by all) b
  on a.racekey = b.racekey and a.gender = b.gender
where a.name = '{name}'
and a.season = '{selected_season}'
)

, by_class as (
select 
a.racekey, 
a.race_rank_by_gender_class::text || ' (' || b.total_participants::text || ')' as race_rank_by_gender_class,
from results_by_class a 
  inner join 
  (select racekey, gender, class, max(race_rank_by_gender_class) as total_participants from results_by_class group by all) b
  on a.racekey = b.racekey and a.gender = b.gender and a.class = b.class
where a.name = '{name}'
and a.season = '{selected_season}'
)

, overall as (
select 
a.racekey, 
a.race_rank_overall::text || ' (' || b.total_participants::text || ')' as race_rank_overall
from results_overall a 
  inner join 
  (select racekey, max(race_rank_overall) as total_participants from results_overall group by all) b
  on a.racekey = b.racekey
where a.name = '{name}'
and a.season = '{selected_season}'
)

select 
  a.racekey, 
  a.class, 
  a.gender, 
  c.race_rank_overall, 
  a.race_rank_by_gender,
  b.race_rank_by_gender_class,
  a.race_points_by_gender,
  a.run1,
  a.run2,
  a.total,
  'https://mamasters-resultsapp.onrender.com/?season=' || a.season || '&race=' || url_encode(a.racekey) || '&scoring=None' as link
  from
by_gender a 
left join by_class b 
on a.racekey = b.racekey 
left join overall c 
on a.racekey = c.racekey;
"""

q_best_discipline = """
select arg_min(racetype, avg_race_points) as best_discipline
from (
select  racetype, avg(race_points) as avg_race_points,
from results_by_gender_vw
where name = '{name}'
and season = '{selected_season}'
group by all
)
"""

q_best_result = """
with results as (
select 
a.racekey, 
a.race_rank_overall,
b.total_participants,
a.class,
a.gender,
a.run1,
a.run2,
a.total,
row_number() over (partition by a.name order by a.race_rank_overall, b.total_participants desc) as best_race
from results_overall a 
inner join 
  (select racekey, max(race_rank_overall) as total_participants from results_overall group by all) b
  on a.racekey = b.racekey
where a.name = '{name}'
and a.season = '{selected_season}'
)

select racekey, 
race_rank_overall || ' out of ' || total_participants || ' racers' as description
from results where best_race = 1;
"""

q_similar_racers = """
with selected_racer as (
select
name, 
round(avg(race_points),2) as avg_race_points 
from results_by_gender_vw
where gender = (select distinct gender from results_by_gender_vw where name = '{name}')
and name = '{name}'
and season = '{selected_season}'
group by all
)

, other_racers as (
select 
name as other_name, 
round(avg(race_points),2) as other_avg_race_points
from results_by_gender_vw 
where gender = (select distinct gender from results_by_gender_vw where name = '{name}')
and name <> '{name}'
and season = '{selected_season}'
group by all
having count(distinct racedate) > 2
)

from (select 
name, 
avg_race_points,
other_name,
other_avg_race_points,
abs(avg_race_points - other_avg_race_points) as points_diff
from (
select 
a.*, b.*
from selected_racer a
cross join other_racers b
)
)
select 
unnest(min_by(other_name, points_diff, 5),
        recursive := 1) as Competitors,

group by all
"""

q_by_discipline = """
with by_gender as (
select 
a.racekey, 
a.race_rank_by_gender::text || ' (' || b.total_participants::text || ')' as race_rank_by_gender,
a.class,
a.gender,
a.run1,
a.run2,
a.total,
a.race_points as race_points_by_gender,
a.season
from results_by_gender_vw a 
inner join 
  (select racekey, gender, max(race_rank_by_gender) as total_participants from results_by_gender group by all) b
  on a.racekey = b.racekey and a.gender = b.gender
where a.name = '{name}'
and a.season = '{selected_season}'
and a.racetype = '{discipline}'
)

, by_class as (
select 
a.racekey, 
a.race_rank_by_gender_class::text || ' (' || b.total_participants::text || ')' as race_rank_by_gender_class,
from results_by_class_vw a 
  inner join 
  (select racekey, gender, class, max(race_rank_by_gender_class) as total_participants from results_by_class group by all) b
  on a.racekey = b.racekey and a.gender = b.gender and a.class = b.class
where a.name = '{name}'
and a.season = '{selected_season}'
and a.racetype = '{discipline}'
)

, overall as (
select 
a.racekey, 
a.race_rank_overall::text || ' (' || b.total_participants::text || ')' as race_rank_overall
from results_overall a 
  inner join 
  (select racekey, max(race_rank_overall) as total_participants from results_overall group by all) b
  on a.racekey = b.racekey
where a.name = '{name}'
and a.season = '{selected_season}'
and a.racetype = '{discipline}'
)

select 
  a.racekey, 
  a.class, 
  a.gender, 
  c.race_rank_overall, 
  a.race_rank_by_gender,
  b.race_rank_by_gender_class,
  a.race_points_by_gender,
  a.run1,
  a.run2,
  a.total,
  'https://mamasters-resultsapp.onrender.com/?season=' || a.season || '&race=' || url_encode(a.racekey) || '&scoring=None' as link
  from
by_gender a 
left join by_class b 
on a.racekey = b.racekey 
left join overall c 
on a.racekey = c.racekey;
"""