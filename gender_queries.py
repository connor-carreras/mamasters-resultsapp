q_gender_results_exist = """
select count(*) as num_records from results_by_gender
where racekey = '{selected_option}'
"""

q_select_results_by_gender = """
select 
race_rank_by_gender,
name,
class,
gender,
run1,
run2,
total,
worldcup_points_by_gender,
race_points as race_points
from results_by_gender
where racekey = '{selected_option}'
and insert_ts = (select max(insert_ts) from results_by_gender where racekey = '{selected_option}')
and gender = '{gender}'
order by race_rank_by_gender, run1, run2
"""

q_insert_results_by_gender = """
insert into results_by_gender
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
rank() over (partition by racekey, gender order by total) as race_rank_by_gender
from results_with_dsq
)

, wc_points as (
select r.*, 
ifnull(p.points,0) as worldcup_points_by_gender
from ranked_results r 
left join worldcup_points p 
on r.race_rank_by_gender = p.place
)

, corrected_points as (
select raceseries, season, division, mountain, racekey, racetype, racedate, bib, name, ussanumber, class, gender, run1, run2, total, ingest_ts, run1_dsq, run2_dsq, run1_dnf, run2_dnf,
case when total is null then null else race_rank_by_gender end as race_rank_by_gender,
case when total is null then 0 else worldcup_points_by_gender end as worldcup_points_by_gender
from wc_points
)

, members as (
select cp.*,
case when m.ussanum is not null then 'Y' else 'N' end as member_status
from corrected_points cp 
left join 
(select * from members_vw where season = '{selected_season}') m
on cp.ussanumber = m.ussanum
)

  
, fastest_total as (
select min(total) as winning_time, gender, racetype 
from results_vw
where racekey = '{selected_option}'
group by all 
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
a.worldcup_points_by_gender,
a.race_rank_by_gender,
round((((a.total::numeric/1000)/(a.winning_time::numeric/1000))-1) * f.f_value,2) as race_points,
a.member_status,
date_trunc('second', current_timestamp()) as insert_ts
from
(select m.*, t.winning_time 
from members m, fastest_total t 
where m.racetype = t.racetype
and m.gender = t.gender) a
inner join (select * from f_values where season = '{selected_season}') f
on a.racetype = f.discipline
"""

q_get_genders = """
select case when gender = 'F' then 'Women' when gender = 'M' then 'Men' end as gender_header, gender
from (
select distinct(gender) as gender
 from results_vw where racekey='{selected_option}') order by 1 desc
"""