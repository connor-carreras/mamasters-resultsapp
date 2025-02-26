q_2025_new_by_gender = """
with ranked_points as (
select season, name, ussanumber, gender, racekey, wc_points_ranking, run1, run2, total, race_rank_by_gender,  worldcup_points_by_gender,
case when wc_points_ranking <=11 then 'count' else 'discard' end as counting_race
from (
select *,
row_number() over(partition by ussanumber, gender, season order by worldcup_points_by_gender desc) as wc_points_ranking
from results_by_gender_vw
where run1 <> 'DNS'
and gender = '{gender}'
and season = '2024-2025'
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
(select season, any(name) as name, ussanumber, gender, 
sum(case when counting_race = 'count' then worldcup_points_by_gender else 0 end) as total_wc_points, 
count(distinct racekey) as unique_starts, 
sum(case when total is not null then 1 else 0 end) as unique_finishes,
from add_members
group by all) b
on a.season = b.season
and a.ussanumber = b.ussanumber
and a.gender = b.gender
order by gender, season_rank_by_gender, wc_points_ranking
)


, final_results as (
select r.*,
m.season_rank_by_gender_members,
date_trunc('second',current_timestamp()) as insert_ts
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


select 
season_rank_by_gender, 
name, 
total_wc_points,
unique_starts,
unique_finishes,
case when max(score1) is null then '--' else max(score1) end as score1,
case when max(score2) is null then '--' else max(score2) end as score2,
  case when max(score3) is null then '--' else max(score3) end as score3,
  case when max(score4) is null then '--' else max(score4) end as score4,
  case when max(score5) is null then '--' else max(score5) end as score5,
  case when max(score6) is null then '--' else max(score6) end as score6,
  case when max(score7) is null then '--' else max(score7) end as score7,
  case when max(score8) is null then '--' else max(score8) end as score8,
  case when max(score9) is null then '--' else max(score9) end as score9,
  case when max(score10) is null then '--' else max(score10) end as score10,
  case when max(score11) is null then '--' else max(score11) end as score11,
  case when max(discards) is null then null else array_to_string(array_filter(x -> x is not null, array_agg(discards)),', ') end as discards
from(
select  
  season_rank_by_gender,
  name,
  unique_starts,
  unique_finishes,
  total_wc_points,
  case when wc_points_ranking = 1 then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as score1,
  case when wc_points_ranking = 2 then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as score2,
  case when wc_points_ranking = 3 then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as score3,
  case when wc_points_ranking = 4 then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as score4,
  case when wc_points_ranking = 5 then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as score5,
  case when wc_points_ranking = 6 then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as score6,
  case when wc_points_ranking = 7 then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as score7,
  case when wc_points_ranking = 8 then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as score8,
  case when wc_points_ranking = 9 then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as score9,
  case when wc_points_ranking = 10 then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as score10,
  case when wc_points_ranking = 11 then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as score11,
  case when wc_points_ranking >11 then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as discards,
  counting_race,
  worldcup_points_by_gender,
  race_rank_by_gender,
  racekey
  from final_results
  )
group by all
order by season_rank_by_gender
"""

q_2025_members_by_gender = """
with ranked_points as (
select season, name, ussanumber, gender, racekey, wc_points_ranking, run1, run2, total, race_rank_by_gender,  worldcup_points_by_gender,
case when wc_points_ranking <=11 then 'count' else 'discard' end as counting_race
from (
select *,
row_number() over(partition by ussanumber, gender, season order by worldcup_points_by_gender desc) as wc_points_ranking
from results_by_gender_vw
where run1 <> 'DNS'
and gender = '{gender}'
and season = '2024-2025'
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
(select season, any(name) as name, ussanumber, gender, 
sum(case when counting_race = 'count' then worldcup_points_by_gender else 0 end) as total_wc_points, 
count(distinct racekey) as unique_starts, 
sum(case when total is not null then 1 else 0 end) as unique_finishes,
from add_members
group by all) b
on a.season = b.season
and a.ussanumber = b.ussanumber
and a.gender = b.gender
order by gender, season_rank_by_gender, wc_points_ranking
)


, final_results as (
select r.*,
m.season_rank_by_gender_members,
date_trunc('second',current_timestamp()) as insert_ts
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


select 
season_rank_by_gender_members as season_rank_by_gender, 
name, 
total_wc_points,
unique_starts,
unique_finishes,
case when max(score1) is null then '--' else max(score1) end as score1,
case when max(score2) is null then '--' else max(score2) end as score2,
  case when max(score3) is null then '--' else max(score3) end as score3,
  case when max(score4) is null then '--' else max(score4) end as score4,
  case when max(score5) is null then '--' else max(score5) end as score5,
  case when max(score6) is null then '--' else max(score6) end as score6,
  case when max(score7) is null then '--' else max(score7) end as score7,
  case when max(score8) is null then '--' else max(score8) end as score8,
  case when max(score9) is null then '--' else max(score9) end as score9,
  case when max(score10) is null then '--' else max(score10) end as score10,
  case when max(score11) is null then '--' else max(score11) end as score11,
  case when max(discards) is null then null else array_to_string(array_filter(x -> x is not null, array_agg(discards)),', ') end as discards
from(
select  
  season_rank_by_gender_members,
  name,
  unique_starts,
  unique_finishes,
  total_wc_points,
  case when wc_points_ranking = 1 then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as score1,
  case when wc_points_ranking = 2 then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as score2,
  case when wc_points_ranking = 3 then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as score3,
  case when wc_points_ranking = 4 then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as score4,
  case when wc_points_ranking = 5 then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as score5,
  case when wc_points_ranking = 6 then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as score6,
  case when wc_points_ranking = 7 then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as score7,
  case when wc_points_ranking = 8 then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as score8,
  case when wc_points_ranking = 9 then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as score9,
  case when wc_points_ranking = 10 then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as score10,
  case when wc_points_ranking = 11 then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as score11,
  case when wc_points_ranking >11 then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as discards,
  counting_race,
  worldcup_points_by_gender,
  race_rank_by_gender,
  racekey
  from final_results
  where season_rank_by_gender_members is not null
  )
group by all
order by season_rank_by_gender_members
"""

q_2025_by_gender_details = """
with ranked_points as (
select season, name, ussanumber, gender, racekey, wc_points_ranking, run1, run2, total, race_rank_by_gender,  worldcup_points_by_gender,
case when wc_points_ranking <=13 then 'count' else 'discard' end as counting_race
from (
select *,
row_number() over(partition by ussanumber, gender, season order by worldcup_points_by_gender desc) as wc_points_ranking
from results_by_gender_vw
where run1 <> 'DNS'
and gender = '{gender}'
and season = '2024-2025'
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
(select season, any(name) as name, ussanumber, gender, 
sum(case when counting_race = 'count' then worldcup_points_by_gender else 0 end) as total_wc_points, 
count(distinct racekey) as unique_starts, 
sum(case when total is not null then 1 else 0 end) as unique_finishes,
from add_members
group by all) b
on a.season = b.season
and a.ussanumber = b.ussanumber
and a.gender = b.gender
order by gender, season_rank_by_gender, wc_points_ranking
)


, final_results as (
select r.*,
m.season_rank_by_gender_members,
date_trunc('second',current_timestamp()) as insert_ts
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

select 
season_rank_by_gender, 
name, 
total_wc_points,
unique_starts,
unique_finishes,
case when max(goresl) is null then '--' else max(goresl) end as goresl,
case when max(huntergs) is null then '--' else max(huntergs) end as huntergs,
  case when max(huntersl1) is null then '--' else max(huntersl1) end as huntersl1,
  case when max(huntersl2) is null then '--' else max(huntersl2) end as huntersl2,
  case when max(mtsnowgs1) is null then '--' else max(mtsnowgs1) end as mtsnowgs1,
  case when max(mtsnowgs2) is null then '--' else max(mtsnowgs2) end as mtsnowgs2,
  case when max(willardsl) is null then '--' else max(willardsl) end as willardsl,
  case when max(willardgs1) is null then '--' else max(willardgs1) end as willardgs1,
  case when max(willardgs2) is null then '--' else max(willardgs2) end as willardgs2,
  case when max(strattonsg1) is null then '--' else max(strattonsg1) end as strattonsg1,
  case when max(strattonsg2) is null then '--' else max(strattonsg2) end as strattonsg2,
  case when max(strattongs) is null then '--' else max(strattongs) end as strattongs,
  case when max(greekgs1) is null then '--' else max(greekgs1) end as greekgs1,
    case when max(greekgs2) is null then '--' else max(greekgs2) end as greekgs2,
    case when max(westsg) is null then '--' else max(westsg) end as westsg,
    case when max(westgs) is null then '--' else max(westgs) end as westgs,
    case when max(westsl) is null then '--' else max(westsl) end as westsl,
    case when max(bouldersl) is null then '--' else max(bouldersl) end as bouldersl,
    case when max(montagegs) is null then '--' else max(montagegs) end as montagegs,
    case when max(montagesl) is null then '--' else max(montagesl) end as montagesl,
    case when max(catamountgs) is null then '--' else max(catamountgs) end as catamountgs,
    case when max(finalsgs) is null then '--' else max(finalsgs) end as finalsgs,
  from(
select  
  season_rank_by_gender,
  name,
  unique_starts,
  unique_finishes,
  total_wc_points,
  case when racekey = 'GORE MOUNTAIN, SLALOM, 2024-03-10' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as goresl,
case when racekey = 'HUNTER MOUNTAIN, GIANT SLALOM, 2025-01-10' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as huntergs,
case when racekey = 'HUNTER MOUNTAIN, SLALOM 1, 2025-01-11' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as huntersl1,
case when racekey = 'HUNTER MOUNTAIN, SLALOM 2, 2025-01-11' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as huntersl2,
case when racekey = 'MOUNT SNOW GIANT SLALOM 1, 2025-01-17' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as mtsnowgs1,
case when racekey = 'MOUNT SNOW GIANT SLALOM 2, 2025-01-17' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as mtsnowgs2,
case when racekey = 'WILLARD MOUNTAIN, SLALOM, 2025-01-18' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as willardsl,
case when racekey = 'WILLARD MOUNTAIN, GIANT SLALOM 1, 2025-01-19' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as willardgs1,
case when racekey = 'WILLARD MOUNTAIN GIANT SLALOM 2, 2025-01-19' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as willardgs2,
case when racekey = 'STRATTON MOUNTAIN, SUPERG 1, 2025-01-24' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as strattonsg1,
case when racekey = 'STRATTON MOUNTAIN, SUPERG 2, 2025-01-24' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as strattonsg2,
case when racekey = 'STRATTON MOUNTAIN, GIANT SLALOM, 2025-01-25' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as strattongs,
case when racekey = 'GREEK PEAK, GIANT SLALOM 1, 2025-02-02' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as greekgs1,
case when racekey = 'GREEK PEAK, GIANT SLALOM 2, 2025-02-02' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as greekgs2,
case when racekey = 'WEST MOUNTAIN, SUPERG, 2025-02-14' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as westsg,
case when racekey = 'WEST MOUNTAIN, GIANT SLALOM, 2025-02-15' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as westgs,
case when racekey = 'WEST MOUNTAIN, SLALOM, 2025-02-16' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as westsl,
case when racekey = 'BIG BOULDER, SLALOM, 2025-02-21' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as bouldersl,
case when racekey = 'MONTAGE MOUNTAIN, GIANT SLALOM, 2025-02-23' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as montagegs,
case when racekey = 'MONTAGE MOUNTAIN, SLALOM, 2025-02-23' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as montagesl,
case when racekey = 'CATAMOUNT RESORT, GIANT SLALOM, 2025-03-02' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as catamountgs,
case when racekey = 'HUNTER MOUNTAIN, FINALS GS 1, 2025-03-07' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as finalsgs
  from final_results
  )
group by all
order by season_rank_by_gender
"""

q_2025_members_by_gender_details = """
with ranked_points as (
select season, name, ussanumber, gender, racekey, wc_points_ranking, run1, run2, total, race_rank_by_gender,  worldcup_points_by_gender,
case when wc_points_ranking <=13 then 'count' else 'discard' end as counting_race
from (
select *,
row_number() over(partition by ussanumber, gender, season order by worldcup_points_by_gender desc) as wc_points_ranking
from results_by_gender_vw
where run1 <> 'DNS'
and gender = '{gender}'
and season = '2024-2025'
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
(select season, any(name) as name, ussanumber, gender, 
sum(case when counting_race = 'count' then worldcup_points_by_gender else 0 end) as total_wc_points, 
count(distinct racekey) as unique_starts, 
sum(case when total is not null then 1 else 0 end) as unique_finishes,
from add_members
group by all) b
on a.season = b.season
and a.ussanumber = b.ussanumber
and a.gender = b.gender
order by gender, season_rank_by_gender, wc_points_ranking
)


, final_results as (
select r.*,
m.season_rank_by_gender_members,
date_trunc('second',current_timestamp()) as insert_ts
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

select 
season_rank_by_gender_members  as season_rank_by_gender, 
name, 
total_wc_points,
unique_starts,
unique_finishes,
case when max(goresl) is null then '--' else max(goresl) end as goresl,
case when max(huntergs) is null then '--' else max(huntergs) end as huntergs,
  case when max(huntersl1) is null then '--' else max(huntersl1) end as huntersl1,
  case when max(huntersl2) is null then '--' else max(huntersl2) end as huntersl2,
  case when max(mtsnowgs1) is null then '--' else max(mtsnowgs1) end as mtsnowgs1,
  case when max(mtsnowgs2) is null then '--' else max(mtsnowgs2) end as mtsnowgs2,
  case when max(willardsl) is null then '--' else max(willardsl) end as willardsl,
  case when max(willardgs1) is null then '--' else max(willardgs1) end as willardgs1,
  case when max(willardgs2) is null then '--' else max(willardgs2) end as willardgs2,
  case when max(strattonsg1) is null then '--' else max(strattonsg1) end as strattonsg1,
  case when max(strattonsg2) is null then '--' else max(strattonsg2) end as strattonsg2,
  case when max(strattongs) is null then '--' else max(strattongs) end as strattongs,
  case when max(greekgs1) is null then '--' else max(greekgs1) end as greekgs1,
    case when max(greekgs2) is null then '--' else max(greekgs2) end as greekgs2,
    case when max(westsg) is null then '--' else max(westsg) end as westsg,
    case when max(westgs) is null then '--' else max(westgs) end as westgs,
    case when max(westsl) is null then '--' else max(westsl) end as westsl,
    case when max(bouldersl) is null then '--' else max(bouldersl) end as bouldersl,
    case when max(montagegs) is null then '--' else max(montagegs) end as montagegs,
    case when max(montagesl) is null then '--' else max(montagesl) end as montagesl,
    case when max(catamountgs) is null then '--' else max(catamountgs) end as catamountgs,
    case when max(finalsgs) is null then '--' else max(finalsgs) end as finalsgs,
  from(
select  
  season_rank_by_gender_members,
  name,
  unique_starts,
  unique_finishes,
  total_wc_points,
  case when racekey = 'GORE MOUNTAIN, SLALOM, 2024-03-10' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as goresl,
case when racekey = 'HUNTER MOUNTAIN, GIANT SLALOM, 2025-01-10' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as huntergs,
case when racekey = 'HUNTER MOUNTAIN, SLALOM 1, 2025-01-11' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as huntersl1,
case when racekey = 'HUNTER MOUNTAIN, SLALOM 2, 2025-01-11' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as huntersl2,
case when racekey = 'MOUNT SNOW GIANT SLALOM 1, 2025-01-17' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as mtsnowgs1,
case when racekey = 'MOUNT SNOW GIANT SLALOM 2, 2025-01-17' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as mtsnowgs2,
case when racekey = 'WILLARD MOUNTAIN, SLALOM, 2025-01-18' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as willardsl,
case when racekey = 'WILLARD MOUNTAIN, GIANT SLALOM 1, 2025-01-19' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as willardgs1,
case when racekey = 'WILLARD MOUNTAIN GIANT SLALOM 2, 2025-01-19' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as willardgs2,
case when racekey = 'STRATTON MOUNTAIN, SUPERG 1, 2025-01-24' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as strattonsg1,
case when racekey = 'STRATTON MOUNTAIN, SUPERG 2, 2025-01-24' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as strattonsg2,
case when racekey = 'STRATTON MOUNTAIN, GIANT SLALOM, 2025-01-25' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as strattongs,
case when racekey = 'GREEK PEAK, GIANT SLALOM 1, 2025-02-02' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as greekgs1,
case when racekey = 'GREEK PEAK, GIANT SLALOM 2, 2025-02-02' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as greekgs2,
case when racekey = 'WEST MOUNTAIN, SUPERG, 2025-02-14' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as westsg,
case when racekey = 'WEST MOUNTAIN, GIANT SLALOM, 2025-02-15' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as westgs,
case when racekey = 'WEST MOUNTAIN, SLALOM, 2025-02-16' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as westsl,
case when racekey = 'BIG BOULDER, SLALOM, 2025-02-21' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as bouldersl,
case when racekey = 'MONTAGE MOUNTAIN, GIANT SLALOM, 2025-02-23' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as montagegs,
case when racekey = 'MONTAGE MOUNTAIN, SLALOM, 2025-02-23' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as montagesl,
case when racekey = 'CATAMOUNT RESORT, GIANT SLALOM, 2025-03-02' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as catamountgs,
case when racekey = 'HUNTER MOUNTAIN, FINALS GS 1, 2025-03-07' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as finalsgs
  from final_results
  where season_rank_by_gender_members is not null
  )
group by all
order by season_rank_by_gender_members
"""

q_2024_by_gender = """
with ranked_points as (
select season, name, ussanumber, gender, racekey, wc_points_ranking, run1, run2, total, race_rank_by_gender,  worldcup_points_by_gender,
case when wc_points_ranking <=6 then 'count' else 'discard' end as counting_race
from (
select *,
row_number() over(partition by ussanumber, gender, season order by worldcup_points_by_gender desc) as wc_points_ranking
from results_by_gender_vw
where run1 <> 'DNS'
and gender = '{gender}'
and season = '2023-2024'
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
(select season, any(name) as name, ussanumber, gender, 
sum(case when counting_race = 'count' then worldcup_points_by_gender else 0 end) as total_wc_points, 
count(distinct racekey) as unique_starts, 
sum(case when total is not null then 1 else 0 end) as unique_finishes,
from add_members
group by all) b
on a.season = b.season
and a.ussanumber = b.ussanumber
and a.gender = b.gender
order by gender, season_rank_by_gender, wc_points_ranking
)

, final_results as (
select r.*,
m.season_rank_by_gender_members,
date_trunc('second',current_timestamp()) as insert_ts
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


select 
season_rank_by_gender, 
name, 
total_wc_points,
unique_starts,
unique_finishes,
case when max(goresl) is null then '--' else max(goresl) end as goresl,
case when max(huntersl1) is null then '--' else max(huntersl1) end as huntersl1,
  case when max(huntersl2) is null then '--' else max(huntersl2) end as huntersl2,
  case when max(huntergs) is null then '--' else max(huntergs) end as huntergs,
  case when max(montagegs) is null then '--' else max(montagegs) end as montagegs,
  case when max(montagesl) is null then '--' else max(montagesl) end as montagesl,
  case when max(beargs) is null then '--' else max(beargs) end as beargs,
  case when max(southsl1) is null then '--' else max(southsl1) end as southsl1,
  case when max(southsl2) is null then '--' else max(southsl2) end as southsl2,
  case when max(westsg) is null then '--' else max(westsg) end as westsg,
  case when max(westgs) is null then '--' else max(westgs) end as westgs,
  case when max(westsl) is null then '--' else max(westsl) end as westsl,
  case when max(catamountgs) is null then '--' else max(catamountgs) end as catamountgs,
  case when max(goresg1) is null then '--' else max(goresg1) end as goresg1,
  case when max(goresg2) is null then '--' else max(goresg2) end as goresg2,
    case when max(goregs) is null then '--' else max(goregs) end as goregs,
from
(
select 
season_rank_by_gender, 
total_wc_points,
name, 
gender, 
unique_starts,
unique_finishes,
case when racekey = 'GORE MOUNTAIN, SLALOM, 2023-03-05' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as goresl,
case when racekey = 'HUNTER MOUNTAIN, SLALOM 1, 2024-01-06' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as huntersl1,
case when racekey = 'HUNTER MOUNTAIN, SLALOM 2, 2024-01-06' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as huntersl2,
case when racekey = 'HUNTER MOUNTAIN, GIANT SLALOM, 2024-01-07' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as huntergs,
case when racekey = 'MONTAGE MOUNTAIN, GIANT SLALOM, 2024-01-20' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as montagegs,
case when racekey = 'MONTAGE MOUNTAIN, SLALOM, 2024-01-20' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as montagesl,
case when racekey = 'BEAR CREEK, GIANT SLALOM, 2024-01-21' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as beargs,
case when racekey = 'MT. SOUTHINGTON, SLALOM 1, 2024-02-03' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as southsl1,
case when racekey = 'MT. SOUTHINGTON, SLALOM 2, 2024-02-03' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as southsl2,
case when racekey = 'WEST MOUNTAIN, SUPER G, 2024-02-16' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as westsg,
case when racekey = 'WEST MOUNTAIN, GIANT SLALOM, 2024-02-17' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as westgs,
case when racekey = 'WEST MOUNTAIN, SLALOM, 2024-02-18' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as westsl,
case when racekey = 'CATAMOUNT RESORT, GIANT SLALOM, 2024-03-03' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as catamountgs,
case when racekey = 'GORE MOUNTAIN, SUPER G 1, 2024-03-08' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as goresg1,
case when racekey = 'GORE MOUNTAIN, SUPER G 2, 2024-03-08' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as goresg2,
case when racekey = 'GORE MOUNTAIN, GIANT SLALOM, 2024-03-09' then worldcup_points_by_gender || ' ('||(case when race_rank_by_gender is null then 'DNF' else race_rank_by_gender::text end)||')' else null end as goregs
from final_results
)
group by all
order by season_rank_by_gender
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
where season = '{selected_season}') 
  where raceclass not like 'U%'
  and raceclass is not null
  order by 2, 3 desc
"""

q_2025_new_by_class = """
with ranked_points as (
select season, name, ussanumber, gender, racekey, wc_points_ranking, run1, run2, total, race_rank_by_gender_class,  worldcup_points_by_gender_class, class,
case when wc_points_ranking <=11 then 'count' else 'discard' end as counting_race
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
and season = '2024-2025'
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
(select season, any(name) as name, ussanumber, gender, 
sum(case when counting_race = 'count' then worldcup_points_by_gender_class else 0 end) as total_wc_points, 
count(distinct racekey) as unique_starts, 
sum(case when total is not null then 1 else 0 end) as unique_finishes,
from add_members
group by all) b
on a.season = b.season
and a.ussanumber = b.ussanumber
and a.gender = b.gender
order by gender, season_rank_by_gender_class, wc_points_ranking
)

, final_results as (
select r.*,
m.season_rank_by_gender_members,
date_trunc('second',current_timestamp()) as insert_ts
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


select 
season_rank_by_gender_class, 
name, 
total_wc_points,
unique_starts,
unique_finishes,
case when max(score1) is null then '--' else max(score1) end as score1,
case when max(score2) is null then '--' else max(score2) end as score2,
case when max(score3) is null then '--' else max(score3) end as score3,
case when max(score4) is null then '--' else max(score4) end as score4,
case when max(score5) is null then '--' else max(score5) end as score5,
case when max(score6) is null then '--' else max(score6) end as score6,
case when max(score7) is null then '--' else max(score7) end as score7,
case when max(score8) is null then '--' else max(score8) end as score8,
case when max(score9) is null then '--' else max(score9) end as score9,
case when max(score10) is null then '--' else max(score10) end as score10,
case when max(score11) is null then '--' else max(score11) end as score11,
case when max(discards) is null then null else array_to_string(array_filter(x -> x is not null, array_agg(discards)),', ') end as discards
from
(
select 
season_rank_by_gender_class, 
total_wc_points,
name, 
gender, 
class,
unique_starts,
unique_finishes,
case when wc_points_ranking = 1 then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as score1,
  case when wc_points_ranking = 2 then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as score2,
  case when wc_points_ranking = 3 then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as score3,
  case when wc_points_ranking = 4 then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as score4,
  case when wc_points_ranking = 5 then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as score5,
  case when wc_points_ranking = 6 then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as score6,
  case when wc_points_ranking = 7 then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as score7,
  case when wc_points_ranking = 8 then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as score8,
  case when wc_points_ranking = 9 then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as score9,
  case when wc_points_ranking = 10 then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as score10,
  case when wc_points_ranking = 11 then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as score11,
  case when wc_points_ranking >11 then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as discards,
from final_results
)
group by all
order by season_rank_by_gender_class
"""

q_2025_members_by_class = """
with ranked_points as (
select season, name, ussanumber, gender, racekey, wc_points_ranking, run1, run2, total, race_rank_by_gender_class,  worldcup_points_by_gender_class, class,
case when wc_points_ranking <=11 then 'count' else 'discard' end as counting_race
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
and season = '2024-2025'
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
(select season, any(name) as name, ussanumber, gender, 
sum(case when counting_race = 'count' then worldcup_points_by_gender_class else 0 end) as total_wc_points, 
count(distinct racekey) as unique_starts, 
sum(case when total is not null then 1 else 0 end) as unique_finishes,
from add_members
group by all) b
on a.season = b.season
and a.ussanumber = b.ussanumber
and a.gender = b.gender
order by gender, season_rank_by_gender_class, wc_points_ranking
)

, final_results as (
select r.*,
m.season_rank_by_gender_members,
date_trunc('second',current_timestamp()) as insert_ts
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


select 
season_rank_by_gender_members  as season_rank_by_class, 
name, 
total_wc_points,
unique_starts,
unique_finishes,
case when max(score1) is null then '--' else max(score1) end as score1,
case when max(score2) is null then '--' else max(score2) end as score2,
case when max(score3) is null then '--' else max(score3) end as score3,
case when max(score4) is null then '--' else max(score4) end as score4,
case when max(score5) is null then '--' else max(score5) end as score5,
case when max(score6) is null then '--' else max(score6) end as score6,
case when max(score7) is null then '--' else max(score7) end as score7,
case when max(score8) is null then '--' else max(score8) end as score8,
case when max(score9) is null then '--' else max(score9) end as score9,
case when max(score10) is null then '--' else max(score10) end as score10,
case when max(score11) is null then '--' else max(score11) end as score11,
case when max(discards) is null then null else array_to_string(array_filter(x -> x is not null, array_agg(discards)),', ') end as discards
from
(
select 
season_rank_by_gender_members, 
total_wc_points,
name, 
gender, 
class,
unique_starts,
unique_finishes,
case when wc_points_ranking = 1 then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as score1,
  case when wc_points_ranking = 2 then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as score2,
  case when wc_points_ranking = 3 then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as score3,
  case when wc_points_ranking = 4 then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as score4,
  case when wc_points_ranking = 5 then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as score5,
  case when wc_points_ranking = 6 then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as score6,
  case when wc_points_ranking = 7 then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as score7,
  case when wc_points_ranking = 8 then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as score8,
  case when wc_points_ranking = 9 then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as score9,
  case when wc_points_ranking = 10 then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as score10,
  case when wc_points_ranking = 11 then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as score11,
  case when wc_points_ranking >11 then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as discards,
from final_results
where season_rank_by_gender_members is not null
)
group by all
order by season_rank_by_gender_members
"""

q_2024_by_class = """
with ranked_points as (
select season, name, ussanumber, gender, racekey, wc_points_ranking, run1, run2, total, race_rank_by_gender_class,  worldcup_points_by_gender_class, class,
case when wc_points_ranking <=11 then 'count' else 'discard' end as counting_race
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
(select season, any(name) as name, ussanumber, gender, 
sum(case when counting_race = 'count' then worldcup_points_by_gender_class else 0 end) as total_wc_points, 
count(distinct racekey) as unique_starts, 
sum(case when total is not null then 1 else 0 end) as unique_finishes,
from add_members
group by all) b
on a.season = b.season
and a.ussanumber = b.ussanumber
and a.gender = b.gender
order by gender, season_rank_by_gender_class, wc_points_ranking
)


, final_results as (
select r.*,
m.season_rank_by_gender_members,
date_trunc('second',current_timestamp()) as insert_ts
from
(select * from rankings) r
left join
(select season, ussanumber, dense_rank() over(partition by season, gender, class order by total_wc_points desc) as season_rank_by_gender_members
from (select season, ussanumber, gender, class, is_mid_atl_member,max(total_wc_points) as total_wc_points from rankings group by all)
where is_mid_atl_member = 'Y'
) m
on r.season=m.season
and r.ussanumber=m.ussanumber
)


select 
season_rank_by_gender_class, 
name, 
total_wc_points,
unique_starts,
unique_finishes,
case when max(goresl) is null then '--' else max(goresl) end as goresl,
case when max(huntersl1) is null then '--' else max(huntersl1) end as huntersl1,
  case when max(huntersl2) is null then '--' else max(huntersl2) end as huntersl2,
  case when max(huntergs) is null then '--' else max(huntergs) end as huntergs,
  case when max(montagegs) is null then '--' else max(montagegs) end as montagegs,
  case when max(montagesl) is null then '--' else max(montagesl) end as montagesl,
  case when max(beargs) is null then '--' else max(beargs) end as beargs,
  case when max(southsl1) is null then '--' else max(southsl1) end as southsl1,
  case when max(southsl2) is null then '--' else max(southsl2) end as southsl2,
  case when max(westsg) is null then '--' else max(westsg) end as westsg,
  case when max(westgs) is null then '--' else max(westgs) end as westgs,
  case when max(westsl) is null then '--' else max(westsl) end as westsl,
  case when max(catamountgs) is null then '--' else max(catamountgs) end as catamountgs,
  case when max(goresg1) is null then '--' else max(goresg1) end as goresg1,
  case when max(goresg2) is null then '--' else max(goresg2) end as goresg2,
    case when max(goregs) is null then '--' else max(goregs) end as goregs,
from
(
select 
season_rank_by_gender_class, 
total_wc_points,
name, 
gender, 
class,
unique_starts,
unique_finishes,
case when racekey = 'GORE MOUNTAIN, SLALOM, 2023-03-05' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as goresl,
case when racekey = 'HUNTER MOUNTAIN, SLALOM 1, 2024-01-06' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as huntersl1,
case when racekey = 'HUNTER MOUNTAIN, SLALOM 2, 2024-01-06' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as huntersl2,
case when racekey = 'HUNTER MOUNTAIN, GIANT SLALOM, 2024-01-07' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as huntergs,
case when racekey = 'MONTAGE MOUNTAIN, GIANT SLALOM, 2024-01-20' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as montagegs,
case when racekey = 'MONTAGE MOUNTAIN, SLALOM, 2024-01-20' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as montagesl,
case when racekey = 'BEAR CREEK, GIANT SLALOM, 2024-01-21' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as beargs,
case when racekey = 'MT. SOUTHINGTON, SLALOM 1, 2024-02-03' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as southsl1,
case when racekey = 'MT. SOUTHINGTON, SLALOM 2, 2024-02-03' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as southsl2,
case when racekey = 'WEST MOUNTAIN, SUPER G, 2024-02-16' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as westsg,
case when racekey = 'WEST MOUNTAIN, GIANT SLALOM, 2024-02-17' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as westgs,
case when racekey = 'WEST MOUNTAIN, SLALOM, 2024-02-18' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as westsl,
case when racekey = 'CATAMOUNT RESORT, GIANT SLALOM, 2024-03-03' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as catamountgs,
case when racekey = 'GORE MOUNTAIN, SUPER G 1, 2024-03-08' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as goresg1,
case when racekey = 'GORE MOUNTAIN, SUPER G 2, 2024-03-08' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as goresg2,
case when racekey = 'GORE MOUNTAIN, GIANT SLALOM, 2024-03-09' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as goregs
from final_results
)
group by all
order by season_rank_by_gender_class
"""

q_2025_by_class_details = """
with ranked_points as (
select season, name, ussanumber, gender, racekey, wc_points_ranking, run1, run2, total, race_rank_by_gender_class,  worldcup_points_by_gender_class, class,
case when wc_points_ranking <=11 then 'count' else 'discard' end as counting_race
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
and season = '2024-2025'
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
(select season, any(name) as name, ussanumber, gender, 
sum(case when counting_race = 'count' then worldcup_points_by_gender_class else 0 end) as total_wc_points, 
count(distinct racekey) as unique_starts, 
sum(case when total is not null then 1 else 0 end) as unique_finishes,
from add_members
group by all) b
on a.season = b.season
and a.ussanumber = b.ussanumber
and a.gender = b.gender
order by gender, season_rank_by_gender_class, wc_points_ranking
)

, final_results as (
select r.*,
m.season_rank_by_gender_members,
date_trunc('second',current_timestamp()) as insert_ts
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


select 
season_rank_by_gender_class, 
name, 
total_wc_points,
unique_starts,
unique_finishes,
case when max(goresl) is null then '--' else max(goresl) end as goresl,
case when max(huntergs) is null then '--' else max(huntergs) end as huntergs,
  case when max(huntersl1) is null then '--' else max(huntersl1) end as huntersl1,
  case when max(huntersl2) is null then '--' else max(huntersl2) end as huntersl2,
  case when max(mtsnowgs1) is null then '--' else max(mtsnowgs1) end as mtsnowgs1,
  case when max(mtsnowgs2) is null then '--' else max(mtsnowgs2) end as mtsnowgs2,
  case when max(willardsl) is null then '--' else max(willardsl) end as willardsl,
  case when max(willardgs1) is null then '--' else max(willardgs1) end as willardgs1,
  case when max(willardgs2) is null then '--' else max(willardgs2) end as willardgs2,
  case when max(strattonsg1) is null then '--' else max(strattonsg1) end as strattonsg1,
  case when max(strattonsg2) is null then '--' else max(strattonsg2) end as strattonsg2,
  case when max(strattongs) is null then '--' else max(strattongs) end as strattongs,
  case when max(greekgs1) is null then '--' else max(greekgs1) end as greekgs1,
  case when max(greekgs2) is null then '--' else max(greekgs2) end as greekgs2,
  case when max(westsg) is null then '--' else max(westsg) end as westsg,
  case when max(westgs) is null then '--' else max(westgs) end as westgs,
  case when max(westsl) is null then '--' else max(westsl) end as westsl,
  case when max(bouldersl) is null then '--' else max(bouldersl) end as bouldersl,
  case when max(montagegs) is null then '--' else max(montagegs) end as montagegs,
  case when max(montagesl) is null then '--' else max(montagesl) end as montagesl,
  case when max(catamountgs) is null then '--' else max(catamountgs) end as catamountgs,
  case when max(finalsgs) is null then '--' else max(finalsgs) end as finalsgs,
from
(
select 
season_rank_by_gender_class, 
total_wc_points,
name, 
gender, 
class,
unique_starts,
unique_finishes,
case when racekey = 'GORE MOUNTAIN, SLALOM, 2024-03-10' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as goresl,
case when racekey = 'HUNTER MOUNTAIN, GIANT SLALOM, 2025-01-10' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as huntergs,
case when racekey = 'HUNTER MOUNTAIN, SLALOM 1, 2025-01-11' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as huntersl1,
case when racekey = 'HUNTER MOUNTAIN, SLALOM 2, 2025-01-11' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as huntersl2,
case when racekey = 'MOUNT SNOW GIANT SLALOM 1, 2025-01-17' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as mtsnowgs1,
case when racekey = 'MOUNT SNOW GIANT SLALOM 2, 2025-01-17' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as mtsnowgs2,
case when racekey = 'WILLARD MOUNTAIN, SLALOM, 2025-01-18' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as willardsl,
case when racekey = 'WILLARD MOUNTAIN, GIANT SLALOM 1, 2025-01-19' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as willardgs1,
case when racekey = 'WILLARD MOUNTAIN GIANT SLALOM 2, 2025-01-19' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as willardgs2,
case when racekey = 'STRATTON MOUNTAIN, SUPERG 1, 2025-01-24' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as strattonsg1,
case when racekey = 'STRATTON MOUNTAIN, SUPERG 2, 2025-01-24' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as strattonsg2,
case when racekey = 'STRATTON MOUNTAIN, GIANT SLALOM, 2025-01-25' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as strattongs,
case when racekey = 'GREEK PEAK, GIANT SLALOM 1, 2025-02-02' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as greekgs1,
case when racekey = 'GREEK PEAK, GIANT SLALOM 2, 2025-02-02' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as greekgs2,
case when racekey = 'WEST MOUNTAIN, SUPERG, 2025-02-14' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as westsg,
case when racekey = 'WEST MOUNTAIN, GIANT SLALOM, 2025-02-15' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as westgs,
case when racekey = 'WEST MOUNTAIN, SLALOM, 2025-02-16' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as westsl,
case when racekey = 'BIG BOULDER, SLALOM, 2025-02-21' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as bouldersl,
case when racekey = 'MONTAGE MOUNTAIN, GIANT SLALOM, 2025-02-23' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as montagegs,
case when racekey = 'MONTAGE MOUNTAIN, SLALOM, 2025-02-23' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as montagesl,
case when racekey = 'CATAMOUNT RESORT, GIANT SLALOM, 2025-03-02' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as catamountgs,
case when racekey = 'HUNTER MOUNTAIN, FINALS GS 1, 2025-03-07' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as finalsgs
from final_results
)
group by all
order by season_rank_by_gender_class
"""

q_2025_members_by_class_details = """
with ranked_points as (
select season, name, ussanumber, gender, racekey, wc_points_ranking, run1, run2, total, race_rank_by_gender_class,  worldcup_points_by_gender_class, class,
case when wc_points_ranking <=11 then 'count' else 'discard' end as counting_race
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
and season = '2024-2025'
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
(select season, any(name) as name, ussanumber, gender, 
sum(case when counting_race = 'count' then worldcup_points_by_gender_class else 0 end) as total_wc_points, 
count(distinct racekey) as unique_starts, 
sum(case when total is not null then 1 else 0 end) as unique_finishes,
from add_members
group by all) b
on a.season = b.season
and a.ussanumber = b.ussanumber
and a.gender = b.gender
order by gender, season_rank_by_gender_class, wc_points_ranking
)

, final_results as (
select r.*,
m.season_rank_by_gender_members,
date_trunc('second',current_timestamp()) as insert_ts
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


select 
season_rank_by_gender_members as season_rank_by_gender, 
name, 
total_wc_points,
unique_starts,
unique_finishes,
case when max(goresl) is null then '--' else max(goresl) end as goresl,
case when max(huntergs) is null then '--' else max(huntergs) end as huntergs,
  case when max(huntersl1) is null then '--' else max(huntersl1) end as huntersl1,
  case when max(huntersl2) is null then '--' else max(huntersl2) end as huntersl2,
  case when max(mtsnowgs1) is null then '--' else max(mtsnowgs1) end as mtsnowgs1,
  case when max(mtsnowgs2) is null then '--' else max(mtsnowgs2) end as mtsnowgs2,
  case when max(willardsl) is null then '--' else max(willardsl) end as willardsl,
  case when max(willardgs1) is null then '--' else max(willardgs1) end as willardgs1,
  case when max(willardgs2) is null then '--' else max(willardgs2) end as willardgs2,
  case when max(strattonsg1) is null then '--' else max(strattonsg1) end as strattonsg1,
  case when max(strattonsg2) is null then '--' else max(strattonsg2) end as strattonsg2,
  case when max(strattongs) is null then '--' else max(strattongs) end as strattongs,
  case when max(greekgs1) is null then '--' else max(greekgs1) end as greekgs1,
  case when max(greekgs2) is null then '--' else max(greekgs2) end as greekgs2,
  case when max(westsg) is null then '--' else max(westsg) end as westsg,
  case when max(westgs) is null then '--' else max(westgs) end as westgs,
  case when max(westsl) is null then '--' else max(westsl) end as westsl,
  case when max(bouldersl) is null then '--' else max(bouldersl) end as bouldersl,
  case when max(montagegs) is null then '--' else max(montagegs) end as montagegs,
  case when max(montagesl) is null then '--' else max(montagesl) end as montagesl,
  case when max(catamountgs) is null then '--' else max(catamountgs) end as catamountgs,
  case when max(finalsgs) is null then '--' else max(finalsgs) end as finalsgs,
from
(
select 
season_rank_by_gender_members, 
total_wc_points,
name, 
gender, 
class,
unique_starts,
unique_finishes,
case when racekey = 'GORE MOUNTAIN, SLALOM, 2024-03-10' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as goresl,
case when racekey = 'HUNTER MOUNTAIN, GIANT SLALOM, 2025-01-10' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as huntergs,
case when racekey = 'HUNTER MOUNTAIN, SLALOM 1, 2025-01-11' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as huntersl1,
case when racekey = 'HUNTER MOUNTAIN, SLALOM 2, 2025-01-11' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as huntersl2,
case when racekey = 'MOUNT SNOW GIANT SLALOM 1, 2025-01-17' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as mtsnowgs1,
case when racekey = 'MOUNT SNOW GIANT SLALOM 2, 2025-01-17' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as mtsnowgs2,
case when racekey = 'WILLARD MOUNTAIN, SLALOM, 2025-01-18' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as willardsl,
case when racekey = 'WILLARD MOUNTAIN, GIANT SLALOM 1, 2025-01-19' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as willardgs1,
case when racekey = 'WILLARD MOUNTAIN GIANT SLALOM 2, 2025-01-19' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as willardgs2,
case when racekey = 'STRATTON MOUNTAIN, SUPERG 1, 2025-01-24' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as strattonsg1,
case when racekey = 'STRATTON MOUNTAIN, SUPERG 2, 2025-01-24' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as strattonsg2,
case when racekey = 'STRATTON MOUNTAIN, GIANT SLALOM, 2025-01-25' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as strattongs,
case when racekey = 'GREEK PEAK, GIANT SLALOM 1, 2025-02-02' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as greekgs1,
case when racekey = 'GREEK PEAK, GIANT SLALOM 2, 2025-02-02' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as greekgs2,
case when racekey = 'WEST MOUNTAIN, SUPERG, 2025-02-14' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as westsg,
case when racekey = 'WEST MOUNTAIN, GIANT SLALOM, 2025-02-15' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as westgs,
case when racekey = 'WEST MOUNTAIN, SLALOM, 2025-02-16' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as westsl,
case when racekey = 'BIG BOULDER, SLALOM, 2025-02-21' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as bouldersl,
case when racekey = 'MONTAGE MOUNTAIN, GIANT SLALOM, 2025-02-23' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as montagegs,
case when racekey = 'MONTAGE MOUNTAIN, SLALOM, 2025-02-23' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as montagesl,
case when racekey = 'CATAMOUNT RESORT, GIANT SLALOM, 2025-03-02' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as catamountgs,
case when racekey = 'HUNTER MOUNTAIN, FINALS GS 1, 2025-03-07' then worldcup_points_by_gender_class || ' ('||(case when race_rank_by_gender_class is null then 'DNF' else race_rank_by_gender_class::text end)||')' else null end as finalsgs
from final_results
where season_rank_by_gender_members is not null
)
group by all
order by season_rank_by_gender_members
"""

q_team_season = """
with unique_results as (
select distinct team, racedate, racekey, team_total, team_rank, worldcup_points_by_team,
from team_results
  where season = '2024-2025')

select 
team_ranking,
  team,
  max(total_points) as total_points,
case when max(goresl) is null then '--' else max(goresl) end as goresl,
case when max(huntergs) is null then '--' else max(huntergs) end as huntergs,
  case when max(huntersl1) is null then '--' else max(huntersl1) end as huntersl1,
  case when max(huntersl2) is null then '--' else max(huntersl2) end as huntersl2,
  case when max(mtsnowgs1) is null then '--' else max(mtsnowgs1) end as mtsnowgs1,
  case when max(mtsnowgs2) is null then '--' else max(mtsnowgs2) end as mtsnowgs2,
  case when max(willardsl) is null then '--' else max(willardsl) end as willardsl,
  case when max(willardgs1) is null then '--' else max(willardgs1) end as willardgs1,
  case when max(willardgs2) is null then '--' else max(willardgs2) end as willardgs2,
  case when max(strattonsg1) is null then '--' else max(strattonsg1) end as strattonsg1,
  case when max(strattonsg2) is null then '--' else max(strattonsg2) end as strattonsg2,
  case when max(strattongs) is null then '--' else max(strattongs) end as strattongs,
  case when max(greekgs1) is null then '--' else max(greekgs1) end as greekgs1,
    case when max(greekgs2) is null then '--' else max(greekgs2) end as greekgs2,
    case when max(westsg) is null then '--' else max(westsg) end as westsg,
    case when max(westgs) is null then '--' else max(westgs) end as westgs,
    case when max(westsl) is null then '--' else max(westsl) end as westsl,
    case when max(bouldersl) is null then '--' else max(bouldersl) end as bouldersl,
    case when max(montagegs) is null then '--' else max(montagegs) end as montagegs,
    case when max(montagesl) is null then '--' else max(montagesl) end as montagesl,
    case when max(catamountgs) is null then '--' else max(catamountgs) end as catamountgs,
    case when max(finalsgs) is null then '--' else max(finalsgs) end as finalsgs,
from
(select *, dense_rank() over (order by total_points desc) as team_ranking
  from
  (
select 
team, 
sum(worldcup_points_by_team) over (partition by team) as total_points, 
case when racekey = 'GORE MOUNTAIN, SLALOM, 2024-03-10' then worldcup_points_by_team || ' ('||(team_rank)||')' else null end as goresl,
case when racekey = 'HUNTER MOUNTAIN, GIANT SLALOM, 2025-01-10' then worldcup_points_by_team || ' ('||(team_rank)||')' else null end as huntergs,
case when racekey = 'HUNTER MOUNTAIN, SLALOM 1, 2025-01-11' then worldcup_points_by_team || ' ('||(team_rank)||')' else null end as huntersl1,
case when racekey = 'HUNTER MOUNTAIN, SLALOM 2, 2025-01-11' then worldcup_points_by_team || ' ('||(team_rank)||')' else null end as huntersl2,
case when racekey = 'MOUNT SNOW GIANT SLALOM 1, 2025-01-17' then worldcup_points_by_team || ' ('||(team_rank)||')' else null end as mtsnowgs1,
case when racekey = 'MOUNT SNOW GIANT SLALOM 2, 2025-01-17' then worldcup_points_by_team || ' ('||(team_rank)||')' else null end as mtsnowgs2,
case when racekey = 'WILLARD MOUNTAIN, SLALOM, 2025-01-18' then worldcup_points_by_team || ' ('||(team_rank)||')' else null end as willardsl,
case when racekey = 'WILLARD MOUNTAIN, GIANT SLALOM 1, 2025-01-19' then worldcup_points_by_team || ' ('||(team_rank)||')' else null end as willardgs1,
case when racekey = 'WILLARD MOUNTAIN GIANT SLALOM 2, 2025-01-19' then worldcup_points_by_team || ' ('||(team_rank)||')' else null end as willardgs2,
case when racekey = 'STRATTON MOUNTAIN, SUPERG 1, 2025-01-24' then worldcup_points_by_team || ' ('||(team_rank)||')' else null end as strattonsg1,
case when racekey = 'STRATTON MOUNTAIN, SUPERG 2, 2025-01-24' then worldcup_points_by_team || ' ('||(team_rank)||')' else null end as strattonsg2,
case when racekey = 'STRATTON MOUNTAIN, GIANT SLALOM, 2025-01-25' then worldcup_points_by_team || ' ('||(team_rank)||')' else null end as strattongs,
case when racekey = 'GREEK PEAK, GIANT SLALOM 1, 2025-02-02' then worldcup_points_by_team || ' ('||(team_rank)||')' else null end as greekgs1,
case when racekey = 'GREEK PEAK, GIANT SLALOM 2, 2025-02-02' then worldcup_points_by_team || ' ('||(team_rank)||')' else null end as greekgs2,
case when racekey = 'WEST MOUNTAIN, SUPERG, 2025-02-14' then worldcup_points_by_team || ' ('||(team_rank)||')' else null end as westsg,
case when racekey = 'WEST MOUNTAIN, GIANT SLALOM, 2025-02-15' then worldcup_points_by_team || ' ('||(team_rank)||')' else null end as westgs,
case when racekey = 'WEST MOUNTAIN, SLALOM, 2025-02-16' then worldcup_points_by_team || ' ('||(team_rank)||')' else null end as westsl,
case when racekey = 'BIG BOULDER, SLALOM, 2025-02-21' then worldcup_points_by_team || ' ('||(team_rank)||')' else null end as bouldersl,
case when racekey = 'MONTAGE MOUNTAIN, GIANT SLALOM, 2025-02-23' then worldcup_points_by_team || ' ('||(team_rank)||')' else null end as montagegs,
case when racekey = 'MONTAGE MOUNTAIN, SLALOM, 2025-02-23' then worldcup_points_by_team || ' ('||(team_rank)||')' else null end as montagesl,
case when racekey = 'CATAMOUNT RESORT, GIANT SLALOM, 2025-03-02' then worldcup_points_by_team || ' ('||(team_rank)||')' else null end as catamountgs,
case when racekey = 'HUNTER MOUNTAIN, FINALS GS 1, 2025-03-07' then worldcup_points_by_team || ' ('||(team_rank)||')' else null end as finalsgs
from unique_results
)
  )
group by all
order by total_points desc
"""
