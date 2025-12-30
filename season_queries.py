md_season_by_class = """
with ranked_points as (
select season, name, ussanumber, gender, racekey, wc_points_ranking, run1, run2, total, race_rank_by_gender_class,  worldcup_points_by_gender_class, class,
case when wc_points_ranking <={scored_races} then 'count' else 'discard' end as counting_race
from (
select *,
row_number() over(partition by ussanumber, gender, season, class order by worldcup_points_by_gender_class desc) as wc_points_ranking
  from   
  (select r.* exclude class,
  case when m.class is not null then m.class::text else r.class::text end as class
  from results_by_class_vw r
  left join members_vw m
  on m.season = r.season 
  and m.ussanum = r.ussanumber)
where run1 <> 'DNS'
and gender = '{gender}'
and class = '{raceclass}'
and racekey in (select racename from schedule where counting_season = '{selected_season}')
)
)


, add_members as (
select r.*,
case when m.ussanum is null then 'N' else 'Y' end as is_mid_atl_member
from 
ranked_points r
left join 
members_vw m
on r.season = m.season
and r.ussanumber = m.ussanum
)

, rankings as (
select a.season, 
b.name,
a.ussanumber,
a.gender,
a.class,
a.is_mid_atl_member,
a.racekey,
a.wc_points_ranking,  
a.worldcup_points_by_gender_class,
a.race_rank_by_gender_class,
a.run1,
a.run2,
a.total,
a.counting_race,
b.total_wc_points,
b.unique_starts,
b.unique_finishes,
dense_rank() over(partition by a.season, a.gender, a.class order by total_wc_points desc) as season_rank_by_gender_class
from
(select * from add_members) a
inner join 
(select season, any_value(name) as name, ussanumber, gender, 
sum(case when counting_race = 'count' then worldcup_points_by_gender_class else 0 end) as total_wc_points, 
count(distinct racekey) as unique_starts, 
sum(case when total is not null then 1 else 0 end) as unique_finishes,
from add_members
group by all) b
on a.season = b.season
and a.ussanumber = b.ussanumber
and a.gender = b.gender
order by a.gender, season_rank_by_gender_class, wc_points_ranking
)

, final_results as (
select r.*,
case when counting_race = 'count' then 'Counting Score ' || lpad(r.wc_points_ranking::text, 2, '0') else 'Discarded Scores' end as pivot_col,
m.season_rank_by_gender_members,
date_trunc('second',current_localtimestamp()) as insert_ts
from
(select * from rankings) r
left join
(select season, ussanumber, row_number() over(partition by season, gender, class order by total_wc_points desc) as season_rank_by_gender_members
from (select season, ussanumber, gender, class, is_mid_atl_member,max(total_wc_points) as total_wc_points from rankings group by all)
where is_mid_atl_member = 'Y'
) m
on r.season=m.season
and r.ussanumber=m.ussanumber
)

PIVOT final_results
ON pivot_col
USING string_agg(worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')')
group by season_rank_by_gender_class, name, total_wc_points, unique_starts, unique_finishes
order by season_rank_by_gender_class asc;
"""

md_season_by_class_members = """
with ranked_points as (
select season, name, ussanumber, gender, racekey, wc_points_ranking, run1, run2, total, race_rank_by_gender_class,  worldcup_points_by_gender_class, class,
case when wc_points_ranking <={scored_races} then 'count' else 'discard' end as counting_race
from (
select *,
row_number() over(partition by ussanumber, gender, season, class order by worldcup_points_by_gender_class desc) as wc_points_ranking
  from   
  (select r.* exclude class,
  case when m.class is not null then m.class::text else r.class::text end as class
  from results_by_class_vw r
  left join members_vw m
  on m.season = r.season 
  and m.ussanum = r.ussanumber)
where run1 <> 'DNS'
and gender = '{gender}'
and class = '{raceclass}'
and racekey in (select racename from schedule where counting_season = '{selected_season}')
)
)


, add_members as (
select r.*,
case when m.ussanum is null then 'N' else 'Y' end as is_mid_atl_member
from 
ranked_points r
left join 
members_vw m
on r.season = m.season
and r.ussanumber = m.ussanum
)

, rankings as (
select a.season, 
b.name,
a.ussanumber,
a.gender,
a.class,
a.is_mid_atl_member,
a.racekey,
a.wc_points_ranking,  
a.worldcup_points_by_gender_class,
a.race_rank_by_gender_class,
a.run1,
a.run2,
a.total,
a.counting_race,
b.total_wc_points,
b.unique_starts,
b.unique_finishes,
dense_rank() over(partition by a.season, a.gender, a.class order by total_wc_points desc) as season_rank_by_gender_class
from
(select * from add_members where is_mid_atl_member = 'Y') a
inner join 
(select season, any_value(name) as name, ussanumber, gender, 
sum(case when counting_race = 'count' then worldcup_points_by_gender_class else 0 end) as total_wc_points, 
count(distinct racekey) as unique_starts, 
sum(case when total is not null then 1 else 0 end) as unique_finishes,
from add_members
group by all) b
on a.season = b.season
and a.ussanumber = b.ussanumber
and a.gender = b.gender
order by a.gender, season_rank_by_gender_class, wc_points_ranking
)

, final_results as (
select r.*,
case when counting_race = 'count' then 'Counting Score ' || lpad(r.wc_points_ranking::text, 2, '0') else 'Discarded Scores' end as pivot_col,
m.season_rank_by_gender_members,
date_trunc('second',current_localtimestamp()) as insert_ts
from
(select * from rankings where is_mid_atl_member = 'Y') r
left join
(select season, ussanumber, row_number() over(partition by season, gender, class order by total_wc_points desc) as season_rank_by_gender_members
from (select season, ussanumber, gender, class, is_mid_atl_member,max(total_wc_points) as total_wc_points from rankings group by all)
where is_mid_atl_member = 'Y'
) m
on r.season=m.season
and r.ussanumber=m.ussanumber
)

PIVOT final_results
ON pivot_col
USING string_agg(worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')')
group by season_rank_by_gender_members, name, total_wc_points, unique_starts, unique_finishes
order by season_rank_by_gender_members asc;
"""


md_season_by_gender_details = """
with ranked_points as (
select racedate, season, name, ussanumber, gender, racekey, wc_points_ranking, run1, run2, total, race_rank_by_gender,  worldcup_points_by_gender,
case when wc_points_ranking <={scored_races} then 'count' else 'discard' end as counting_race
from (
select *,
row_number() over(partition by ussanumber, gender, season order by worldcup_points_by_gender desc) as wc_points_ranking
from results_by_gender_vw
where run1 <> 'DNS'
and gender = '{gender}'
and racekey in (select racename from schedule where counting_season = '{selected_season}')

)

)
, add_members as (
select r.*,
case when m.ussanum is null then 'N' else 'Y' end as is_mid_atl_member
from 
ranked_points r
left join 
members_vw m
on r.season = m.season
and r.ussanumber = m.ussanum
)

, rankings as (
select a.season, 
b.name,
a.ussanumber,
a.gender,
a.is_mid_atl_member,
a.racekey,
a.racedate,
a.wc_points_ranking,  
a.worldcup_points_by_gender,
a.race_rank_by_gender,
a.run1,
a.run2,
a.total,
a.counting_race,
b.total_wc_points,
b.unique_starts,
b.unique_finishes,
dense_rank() over(partition by a.season, a.gender order by total_wc_points desc) as season_rank_by_gender
from
(select * from add_members) a
inner join 
(select season, any_value(name) as name, ussanumber, gender, 
sum(case when counting_race = 'count' then worldcup_points_by_gender else 0 end) as total_wc_points, 
count(distinct racekey) as unique_starts, 
sum(case when total is not null then 1 else 0 end) as unique_finishes,
from add_members
group by all) b
on a.season = b.season
and a.ussanumber = b.ussanumber
and a.gender = b.gender
order by a.gender, season_rank_by_gender, wc_points_ranking
)

, final_results as (
select r.*,
m.season_rank_by_gender_members,
date_trunc('second',current_localtimestamp()) as insert_ts
from
(select * from rankings) r
left join
(select season, ussanumber, dense_rank() over(partition by season, gender order by total_wc_points desc) as season_rank_by_gender_members
from (select season, ussanumber, gender, is_mid_atl_member,max(total_wc_points) as total_wc_points from rankings group by all)
where is_mid_atl_member = 'Y'
) m
on r.season=m.season
and r.ussanumber=m.ussanumber
)

PIVOT final_results
ON racekey
USING any_value(worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')')
group by season_rank_by_gender, name, total_wc_points, unique_starts, unique_finishes
order by season_rank_by_gender asc;
"""

md_season_by_gender_members_details = """
with ranked_points as (
select racedate, season, name, ussanumber, gender, racekey, wc_points_ranking, run1, run2, total, race_rank_by_gender,  worldcup_points_by_gender,
case when wc_points_ranking <={scored_races} then 'count' else 'discard' end as counting_race
from (
select *,
row_number() over(partition by ussanumber, gender, season order by worldcup_points_by_gender desc) as wc_points_ranking
from results_by_gender_vw
where run1 <> 'DNS'
and gender = '{gender}'
and racekey in (select racename from schedule where counting_season = '{selected_season}')

)

)
, add_members as (
select r.*,
case when m.ussanum is null then 'N' else 'Y' end as is_mid_atl_member
from 
ranked_points r
left join 
members_vw m
on r.season = m.season
and r.ussanumber = m.ussanum
)

, rankings as (
select a.season, 
b.name,
a.ussanumber,
a.gender,
a.is_mid_atl_member,
a.racekey,
a.racedate,
a.wc_points_ranking,  
a.worldcup_points_by_gender,
a.race_rank_by_gender,
a.run1,
a.run2,
a.total,
a.counting_race,
b.total_wc_points,
b.unique_starts,
b.unique_finishes,
dense_rank() over(partition by a.season, a.gender order by total_wc_points desc) as season_rank_by_gender
from
(select * from add_members) a
inner join 
(select season, any_value(name) as name, ussanumber, gender, 
sum(case when counting_race = 'count' then worldcup_points_by_gender else 0 end) as total_wc_points, 
count(distinct racekey) as unique_starts, 
sum(case when total is not null then 1 else 0 end) as unique_finishes,
from add_members
group by all) b
on a.season = b.season
and a.ussanumber = b.ussanumber
and a.gender = b.gender
order by a.gender, season_rank_by_gender, wc_points_ranking
)

, final_results as (
select r.*,
m.season_rank_by_gender_members,
date_trunc('second',current_localtimestamp()) as insert_ts
from
(select * from rankings where is_mid_atl_member = 'Y') r
left join
(select season, ussanumber, dense_rank() over(partition by season, gender order by total_wc_points desc) as season_rank_by_gender_members
from (select season, ussanumber, gender, is_mid_atl_member,max(total_wc_points) as total_wc_points from rankings group by all)
where is_mid_atl_member = 'Y'
) m
on r.season=m.season
and r.ussanumber=m.ussanumber
)

PIVOT final_results
ON racekey
USING any_value(worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')')
group by season_rank_by_gender_members, name, total_wc_points, unique_starts, unique_finishes
order by season_rank_by_gender_members asc;
"""

md_season_by_gender_members = """
with ranked_points as (
select season, name, ussanumber, gender, racekey, wc_points_ranking, run1, run2, total, race_rank_by_gender,  worldcup_points_by_gender,
case when wc_points_ranking <={scored_races} then 'count' else 'discard' end as counting_race
from (
select *,
row_number() over(partition by ussanumber, gender, season order by worldcup_points_by_gender desc) as wc_points_ranking
from results_by_gender_vw
where run1 <> 'DNS'
and gender = '{gender}'
and racekey in (select racename from schedule where counting_season = '{selected_season}')
)

)
, add_members as (
select r.*,
case when m.ussanum is null then 'N' else 'Y' end as is_mid_atl_member
from 
ranked_points r
left join 
members_vw m
on r.season = m.season
and r.ussanumber = m.ussanum
)

, rankings as (
select a.season, 
b.name,
a.ussanumber,
a.gender,
a.is_mid_atl_member,
a.racekey,
a.wc_points_ranking,  
a.worldcup_points_by_gender,
a.race_rank_by_gender,
a.run1,
a.run2,
a.total,
a.counting_race,
b.total_wc_points,
b.unique_starts,
b.unique_finishes,
dense_rank() over(partition by a.season, a.gender order by total_wc_points desc) as season_rank_by_gender
from
(select * from add_members) a
inner join 
(select season, any_value(name) as name, ussanumber, gender, 
sum(case when counting_race = 'count' then worldcup_points_by_gender else 0 end) as total_wc_points, 
count(distinct racekey) as unique_starts, 
sum(case when total is not null then 1 else 0 end) as unique_finishes,
from add_members
group by all) b
on a.season = b.season
and a.ussanumber = b.ussanumber
and a.gender = b.gender
order by a.gender, season_rank_by_gender, wc_points_ranking
)


, final_results as (
select r.*,
case when counting_race = 'count' then 'Counting Score ' || lpad(r.wc_points_ranking::text, 2, '0') else 'Discarded Scores' end as pivot_col,
m.season_rank_by_gender_members,
date_trunc('second',current_localtimestamp()) as insert_ts
from
(select * from rankings where is_mid_atl_member = 'Y') r
left join
(select season, ussanumber, dense_rank() over(partition by season, gender order by total_wc_points desc) as season_rank_by_gender_members
from (select season, ussanumber, gender, is_mid_atl_member,max(total_wc_points) as total_wc_points from rankings group by all)
where is_mid_atl_member = 'Y'
) m
on r.season=m.season
and r.ussanumber=m.ussanumber
)

PIVOT final_results
ON pivot_col
USING string_agg(worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')')
group by season_rank_by_gender_members, name, total_wc_points, unique_starts, unique_finishes
order by season_rank_by_gender_members asc;
"""

md_season_by_gender = """
with ranked_points as (
select season, name, ussanumber, gender, racekey, wc_points_ranking, run1, run2, total, race_rank_by_gender,  worldcup_points_by_gender,
case when wc_points_ranking <={scored_races} then 'count' else 'discard' end as counting_race
from (
select *,
row_number() over(partition by ussanumber, gender, season order by worldcup_points_by_gender desc) as wc_points_ranking
from results_by_gender_vw
where run1 <> 'DNS'
and gender = '{gender}'
and racekey in (select racename from schedule where counting_season = '{selected_season}')
)

)
, add_members as (
select r.*,
case when m.ussanum is null then 'N' else 'Y' end as is_mid_atl_member
from 
ranked_points r
left join 
members_vw m
on r.season = m.season
and r.ussanumber = m.ussanum
)

, rankings as (
select a.season, 
b.name,
a.ussanumber,
a.gender,
a.is_mid_atl_member,
a.racekey,
a.wc_points_ranking,  
a.worldcup_points_by_gender,
a.race_rank_by_gender,
a.run1,
a.run2,
a.total,
a.counting_race,
b.total_wc_points,
b.unique_starts,
b.unique_finishes,
dense_rank() over(partition by a.season, a.gender order by total_wc_points desc) as season_rank_by_gender
from
(select * from add_members) a
inner join 
(select season, any_value(name) as name, ussanumber, gender, 
sum(case when counting_race = 'count' then worldcup_points_by_gender else 0 end) as total_wc_points, 
count(distinct racekey) as unique_starts, 
sum(case when total is not null then 1 else 0 end) as unique_finishes,
from add_members
group by all) b
on a.season = b.season
and a.ussanumber = b.ussanumber
and a.gender = b.gender
order by a.gender, season_rank_by_gender, wc_points_ranking
)


, final_results as (
select r.*,
case when counting_race = 'count' then 'Counting Score ' || lpad(r.wc_points_ranking::text, 2, '0') else 'Discarded Scores' end as pivot_col,
m.season_rank_by_gender_members,
date_trunc('second',current_localtimestamp()) as insert_ts
from
(select * from rankings) r
left join
(select season, ussanumber, dense_rank() over(partition by season, gender order by total_wc_points desc) as season_rank_by_gender_members
from (select season, ussanumber, gender, is_mid_atl_member,max(total_wc_points) as total_wc_points from rankings group by all)
where is_mid_atl_member = 'Y'
) m
on r.season=m.season
and r.ussanumber=m.ussanumber
)

PIVOT final_results
ON pivot_col
USING string_agg(worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')')
group by season_rank_by_gender, name, total_wc_points, unique_starts, unique_finishes
order by season_rank_by_gender asc;

"""

md_season_by_class_details_members = """
with ranked_points as (
select season, name, ussanumber, gender, racekey, wc_points_ranking, run1, run2, total, race_rank_by_gender_class,  worldcup_points_by_gender_class, class,
case when wc_points_ranking <={scored_races} then 'count' else 'discard' end as counting_race
from (
select *,
row_number() over(partition by ussanumber, gender, season, class order by worldcup_points_by_gender_class desc) as wc_points_ranking
  from   
  (select r.* exclude class,
  case when m.class is not null then m.class::text else r.class::text end as class
  from results_by_class_vw r
  left join members_vw m
  on m.season = r.season 
  and m.ussanum = r.ussanumber)
where run1 <> 'DNS'
and gender = '{gender}'
and class = '{raceclass}'
and racekey in (select racename from schedule where counting_season = '{selected_season}')
)

)
, add_members as (
select r.*,
case when m.ussanum is null then 'N' else 'Y' end as is_mid_atl_member
from 
ranked_points r
left join 
members_vw m
on r.season = m.season
and r.ussanumber = m.ussanum
)

, rankings as (
select a.season, 
b.name,
a.ussanumber,
a.gender,
a.class,
a.is_mid_atl_member,
a.racekey,
a.wc_points_ranking,  
a.worldcup_points_by_gender_class,
a.race_rank_by_gender_class,
a.run1,
a.run2,
a.total,
a.counting_race,
b.total_wc_points,
b.unique_starts,
b.unique_finishes,
dense_rank() over(partition by a.season, a.gender, a.class order by total_wc_points desc) as season_rank_by_gender_class
from
(select * from add_members) a
inner join 
(select season, any_value(name) as name, ussanumber, gender, 
sum(case when counting_race = 'count' then worldcup_points_by_gender_class else 0 end) as total_wc_points, 
count(distinct racekey) as unique_starts, 
sum(case when total is not null then 1 else 0 end) as unique_finishes,
from add_members
group by all) b
on a.season = b.season
and a.ussanumber = b.ussanumber
and a.gender = b.gender
order by a.gender, season_rank_by_gender_class, wc_points_ranking
)

, final_results as (
select r.*,
m.season_rank_by_gender_members,
date_trunc('second',current_localtimestamp()) as insert_ts
from
(select * from rankings where is_mid_atl_member = 'Y') r
left join
(select season, ussanumber, row_number() over(partition by season, gender, class order by total_wc_points desc) as season_rank_by_gender_members
from (select season, ussanumber, gender, class, is_mid_atl_member,max(total_wc_points) as total_wc_points from rankings group by all)
where is_mid_atl_member = 'Y'
) m
on r.season=m.season
and r.ussanumber=m.ussanumber
)

PIVOT final_results
ON racekey
USING any_value(worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')')
group by season_rank_by_gender_members, name, total_wc_points, unique_starts, unique_finishes
order by season_rank_by_gender_members asc;
"""

md_season_by_class_details = """
with ranked_points as (
select season, name, ussanumber, gender, racekey, wc_points_ranking, run1, run2, total, race_rank_by_gender_class,  worldcup_points_by_gender_class, class,
case when wc_points_ranking <={scored_races} then 'count' else 'discard' end as counting_race
from (
select *,
row_number() over(partition by ussanumber, gender, season, class order by worldcup_points_by_gender_class desc) as wc_points_ranking
  from   
  (select r.* exclude class,
  case when m.class is not null then m.class::text else r.class::text end as class
  from results_by_class_vw r
  left join members_vw m
  on m.season = r.season 
  and m.ussanum = r.ussanumber)
where run1 <> 'DNS'
and gender = '{gender}'
and class = '{raceclass}'
and racekey in (select racename from schedule where counting_season = '{selected_season}')
)

)
, add_members as (
select r.*,
case when m.ussanum is null then 'N' else 'Y' end as is_mid_atl_member
from 
ranked_points r
left join 
members_vw m
on r.season = m.season
and r.ussanumber = m.ussanum
)

, rankings as (
select a.season, 
b.name,
a.ussanumber,
a.gender,
a.class,
a.is_mid_atl_member,
a.racekey,
a.wc_points_ranking,  
a.worldcup_points_by_gender_class,
a.race_rank_by_gender_class,
a.run1,
a.run2,
a.total,
a.counting_race,
b.total_wc_points,
b.unique_starts,
b.unique_finishes,
dense_rank() over(partition by a.season, a.gender, a.class order by total_wc_points desc) as season_rank_by_gender_class
from
(select * from add_members) a
inner join 
(select season, any_value(name) as name, ussanumber, gender, 
sum(case when counting_race = 'count' then worldcup_points_by_gender_class else 0 end) as total_wc_points, 
count(distinct racekey) as unique_starts, 
sum(case when total is not null then 1 else 0 end) as unique_finishes,
from add_members
group by all) b
on a.season = b.season
and a.ussanumber = b.ussanumber
and a.gender = b.gender
order by a.gender, season_rank_by_gender_class, wc_points_ranking
)

, final_results as (
select r.*,
m.season_rank_by_gender_members,
date_trunc('second',current_localtimestamp()) as insert_ts
from
(select * from rankings) r
left join
(select season, ussanumber, row_number() over(partition by season, gender, class order by total_wc_points desc) as season_rank_by_gender_members
from (select season, ussanumber, gender, class, is_mid_atl_member,max(total_wc_points) as total_wc_points from rankings group by all)
where is_mid_atl_member = 'Y'
) m
on r.season=m.season
and r.ussanumber=m.ussanumber
)

PIVOT final_results
ON racekey
USING any_value(worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')')
group by season_rank_by_gender_class, name, total_wc_points, unique_starts, unique_finishes
order by season_rank_by_gender_class asc;
"""

q_list_genders = """
select case when gender = 'F' then 'Women' when gender = 'M' then 'Men' end as gender_header, gender
from (
select distinct(gender) as gender
from results_vw) order by 1 desc
"""

q_class_list = """
select case when gender = 'F' then 'Women' when gender = 'M' then 'Men' end as gender_header, gender, raceclass::integer as raceclass
from (
select distinct gender, class as raceclass
from results_vw
where racekey in(select racename from schedule where counting_season = '{selected_season}')) 
  where raceclass not like 'U%'
  and raceclass is not null
  order by 2, 3 desc
"""


q_team_season = """
with unique_results as (
select distinct team, racedate, racekey, team_total, team_rank, worldcup_points_by_team,
from team_results
  where racekey in(select racename from schedule where counting_season = '{selected_season}')
  )

, final_results as (
(select *, dense_rank() over (order by total_points desc) as team_ranking
  from
  (
select 
team, racedate, racekey, team_total, team_rank, worldcup_points_by_team,
sum(worldcup_points_by_team) over (partition by team) as total_points
from unique_results )
)
)

PIVOT final_results
ON racekey
USING any_value(worldcup_points_by_team || ' ('||(case when team_rank is null then 'DNF' else team_rank::text end)||')')
group by team_ranking, team, total_points
order by team_ranking asc;
"""
