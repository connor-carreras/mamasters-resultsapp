create external table ex_results (
  full_text text
)
CREDENTIALS = (AWS_ROLE_ARN = '')
URL = ''
OBJECT_PATTERN = '*.json'
TYPE = (JSON PARSE_AS_TEXT=TRUE)

create table results (
  season text null,
  racekey text null,
  raceseries text null,
  division text null,
  mountain text  null,
  racename text  null,
  racetype text  null,
  racedate date  null,
  bib text  null,
  name text  null, 
  ussanumber text null,
  class text  null,
  gender text  null,
  run1 integer null,
  run2 integer null,
  total integer null,
  ingest_ts timestamp  null
) primary index season, racekey, gender, class;

insert into results
select 
(upper(regexp_replace_all(json_pointer_extract(full_text, '/SST_USSA_FIS_Race/Men/Header/SkiAreaName'),'\"',''))||', '||upper(regexp_replace_all(json_pointer_extract(full_text, '/SST_USSA_FIS_Race/Men/RTData/RTRaceType'),'\"',''))||', '||to_date(date_add('day',regexp_replace_all(json_pointer_extract(full_text, '/SST_USSA_FIS_Race/Men/Header/RaceDate'),'\"','')::integer,'1899-12-30')::text,'YYYY-MM-DD')) as racekey,
upper(regexp_replace_all(json_pointer_extract(full_text, '/SST_USSA_FIS_Race/Men/Header/ClubName'),'\"','')) as raceseries,  
upper(regexp_replace_all(json_pointer_extract(full_text, '/SST_USSA_FIS_Race/Men/Header/Division'),'\"','')) as division,
upper(regexp_replace_all(json_pointer_extract(full_text, '/SST_USSA_FIS_Race/Men/Header/SkiAreaName'),'\"','')) as mountain,
regexp_replace_all(json_pointer_extract(full_text, '/SST_USSA_FIS_Race/Men/Header/RaceName'),'\"','') as racename,
regexp_replace_all(json_pointer_extract(full_text, '/SST_USSA_FIS_Race/Men/RTData/RTRaceType'),'\"','') as racetype,
to_date(date_add('day',regexp_replace_all(json_pointer_extract(full_text, '/SST_USSA_FIS_Race/Men/Header/RaceDate'),'\"','')::integer,'1899-12-30')::text,'YYYY-MM-DD') as racedate,
regexp_replace_all(json_pointer_extract(results_array,'/Bib'),'\"','') as bib,
regexp_replace_all(json_pointer_extract(results_array,'/Name'),'\"','') as name,
regexp_replace_all(json_pointer_extract(results_array,'/USSANumber'),'\"','') as ussanumber,
regexp_replace_all(json_pointer_extract(results_array,'/CompClass'),'\"','') as class,
regexp_replace_all(json_pointer_extract(results_array, '/MastersSex'),'\"','') as gender,
(regexp_replace_all(json_pointer_extract(results_array, '/Time1/MicroFinish'),'\"','')::bigint -
regexp_replace_all(json_pointer_extract(results_array, '/Time1/MicroStart'),'\"','')::bigint) / 1000::integer as run1,
(regexp_replace_all(json_pointer_extract(results_array, '/Time2/MicroFinish'),'\"','')::bigint - 
regexp_replace_all(json_pointer_extract(results_array, '/Time2/MicroStart'),'\"','')::bigint) /1000::integer as run2,
((regexp_replace_all(json_pointer_extract(results_array, '/Time1/MicroFinish'),'\"','')::bigint -
regexp_replace_all(json_pointer_extract(results_array, '/Time1/MicroStart'),'\"','')::bigint) / 1000) +
((regexp_replace_all(json_pointer_extract(results_array, '/Time2/MicroFinish'),'\"','')::bigint - 
regexp_replace_all(json_pointer_extract(results_array, '/Time2/MicroStart'),'\"','')::bigint) /1000)::integer as total,
$source_file_timestamp as ingest_ts
from ex_results,
unnest(JSON_POINTER_EXTRACT_ARRAY(full_text, '/SST_USSA_FIS_Race/Men/Comp')) as r(results_array)
where TO_YYYYMMDD($source_file_timestamp) = to_yyyymmdd(current_date());


CREATE VIEW results_vw AS
SELECT
  season,
  racekey,
  raceseries,
  division,
  mountain,
  racename,
  racetype,
  racedate,
  bib,
  name,
  CASE
    WHEN (ussanumber IS NULL) THEN lower(name)
    ELSE ussanumber
  END AS ussanumber,
  class,
  gender,
  run1,
  run1_dnf,
  case when racetype = 'Super-G' and run1 is not null then 0 else run2 end as run2,
  run2_dnf,
  case when racetype = 'Super-G' and run1 is not null then run1 else total end as total,
  ingest_ts
FROM
  (SELECT DISTINCT * FROM results 
  WHERE concat(ingest_ts, racekey) IN (SELECT concat(max, racekey) FROM (SELECT max(ingest_ts) AS max, racekey FROM results GROUP BY all))
  ) AS r;


create aggregating index agg_idx_max_ingest_ts on results (
  max(ingest_ts)
);

create table worldcup_points (
  place integer not null,
  points integer not null
  );

create table team_handicaps (
hc_label text not null,
discipline text not null,
class integer not null,
gender text not null,
handicap numeric not null
)
;

insert into team_handicaps
  values
('MAMS-HC2','GS',1,'M',1.0),
('MAMS-HC2','GS',2,'M',0.99),
('MAMS-HC2','GS',3,'M',0.98),
('MAMS-HC2','GS',4,'M',0.968),
('MAMS-HC2','GS',5,'M',0.955),
('MAMS-HC2','GS',6,'M',0.94),
('MAMS-HC2','GS',7,'M',0.925),
('MAMS-HC2','GS',8,'M',0.91),
('MAMS-HC2','GS',9,'M',0.89),
('MAMS-HC2','GS',10,'M',0.863),
('MAMS-HC2','GS',11,'M',0.83),
('MAMS-HC2','GS',12,'M',0.78),
('MAMS-HC2','GS',13,'M',0.72),
('MAMS-HC2','GS',14,'M',0.63),
('MAMS-HC2','GS',15,'M',0.52),
('MAMS-HC2','GS',1,'F',0.94),
('MAMS-HC2','GS',2,'F',0.93),
('MAMS-HC2','GS',3,'F',0.905),
('MAMS-HC2','GS',4,'F',0.885),
('MAMS-HC2','GS',5,'F',0.86),
('MAMS-HC2','GS',6,'F',0.84),
('MAMS-HC2','GS',7,'F',0.86),
('MAMS-HC2','GS',8,'F',0.78),
('MAMS-HC2','GS',9,'F',0.73),
('MAMS-HC2','GS',10,'F',0.69),
('MAMS-HC2','GS',11,'F',0.625),
('MAMS-HC2','GS',12,'F',0.54),
('MAMS-HC2','GS',13,'F',0.44),
('MAMS-HC2','GS',14,'F',0.33),
('MAMS-HC2','GS',15,'F',0.23),
('MAMS-HC2','SL',1,'M',1.0),
('MAMS-HC2','SL',2,'M',0.995),
('MAMS-HC2','SL',3,'M',0.985),
('MAMS-HC2','SL',4,'M',0.975),
('MAMS-HC2','SL',5,'M',0.968),
('MAMS-HC2','SL',6,'M',0.955),
('MAMS-HC2','SL',7,'M',0.94),
('MAMS-HC2','SL',8,'M',0.925),
('MAMS-HC2','SL',9,'M',0.908),
('MAMS-HC2','SL',10,'M',0.883),
('MAMS-HC2','SL',11,'M',0.85),
('MAMS-HC2','SL',12,'M',0.81),
('MAMS-HC2','SL',13,'M',0.76),
('MAMS-HC2','SL',14,'M',0.705),
('MAMS-HC2','SL',15,'M',0.63),
('MAMS-HC2','SL',1,'F',0.94),
('MAMS-HC2','SL',2,'F',0.93),
('MAMS-HC2','SL',3,'F',0.923),
('MAMS-HC2','SL',4,'F',0.913),
('MAMS-HC2','SL',5,'F',0.90),
('MAMS-HC2','SL',6,'F',0.89),
('MAMS-HC2','SL',7,'F',0.878),
('MAMS-HC2','SL',8,'F',0.858),
('MAMS-HC2','SL',9,'F',0.84),
('MAMS-HC2','SL',10,'F',0.81),
('MAMS-HC2','SL',11,'F',0.775),
('MAMS-HC2','SL',12,'F',0.73),
('MAMS-HC2','SL',13,'F',0.68),
('MAMS-HC2','SL',14,'F',0.61),
('MAMS-HC2','SL',15,'F',0.525),
('MAMS-HC1','GS',1,'M',1.0),
('MAMS-HC1','GS',2,'M',0.995),
('MAMS-HC1','GS',3,'M',0.985),
('MAMS-HC1','GS',4,'M',0.975),
('MAMS-HC1','GS',5,'M',0.96),
('MAMS-HC1','GS',6,'M',0.94),
('MAMS-HC1','GS',7,'M',0.925),
('MAMS-HC1','GS',8,'M',0.905),
('MAMS-HC1','GS',9,'M',0.88),
('MAMS-HC1','GS',10,'M',0.855),
('MAMS-HC1','GS',11,'M',0.825),
('MAMS-HC1','GS',12,'M',0.785),
('MAMS-HC1','GS',13,'M',0.73),
('MAMS-HC1','GS',14,'M',0.67),
('MAMS-HC1','GS',15,'M',0.59),
('MAMS-HC1','GS',1,'F',0.95),
('MAMS-HC1','GS',2,'F',0.945),
('MAMS-HC1','GS',3,'F',0.935),
('MAMS-HC1','GS',4,'F',0.925),
('MAMS-HC1','GS',5,'F',0.91),
('MAMS-HC1','GS',6,'F',0.895),
('MAMS-HC1','GS',7,'F',0.875),
('MAMS-HC1','GS',8,'F',0.855),
('MAMS-HC1','GS',9,'F',0.83),
('MAMS-HC1','GS',10,'F',0.805),
('MAMS-HC1','GS',11,'F',0.775),
('MAMS-HC1','GS',12,'F',0.735),
('MAMS-HC1','GS',13,'F',0.68),
('MAMS-HC1','GS',14,'F',0.62),
('MAMS-HC1','GS',15,'F',0.54),
('MAMS-HC1','SL',1,'M',1.0),
('MAMS-HC1','SL',2,'M',0.99),
('MAMS-HC1','SL',3,'M',0.98),
('MAMS-HC1','SL',4,'M',0.97),
('MAMS-HC1','SL',5,'M',0.955),
('MAMS-HC1','SL',6,'M',0.94),
('MAMS-HC1','SL',7,'M',0.925),
('MAMS-HC1','SL',8,'M',0.91),
('MAMS-HC1','SL',9,'M',0.885),
('MAMS-HC1','SL',10,'M',0.85),
('MAMS-HC1','SL',11,'M',0.81),
('MAMS-HC1','SL',12,'M',0.76),
('MAMS-HC1','SL',13,'M',0.71),
('MAMS-HC1','SL',14,'M',0.763),
('MAMS-HC1','SL',15,'M',0.52),
('MAMS-HC1','SL',1,'F',0.94),
('MAMS-HC1','SL',2,'F',0.93),
('MAMS-HC1','SL',3,'F',0.92),
('MAMS-HC1','SL',4,'F',0.91),
('MAMS-HC1','SL',5,'F',0.895),
('MAMS-HC1','SL',6,'F',0.883),
('MAMS-HC1','SL',7,'F',0.86),
('MAMS-HC1','SL',8,'F',0.84),
('MAMS-HC1','SL',9,'F',0.81),
('MAMS-HC1','SL',10,'F',0.775),
('MAMS-HC1','SL',11,'F',0.73),
('MAMS-HC1','SL',12,'F',0.68),
('MAMS-HC1','SL',13,'F',0.615),
('MAMS-HC1','SL',14,'F',0.525),
('MAMS-HC1','SL',15,'F',0.40);

insert into worldcup_points
values
  (1,100),
  (2,80),
  (3,60),
  (4,50),
  (5,45),
  (6,40),
  (7,36),
  (8,32),
  (9,29),
  (10,26),
  (11,24),
  (12,22),
  (13,20),
  (14,18),
  (15,16),
  (16,15),
  (17,14),
  (18,13),
  (19,12),
  (20,11),
  (21,10),
  (22,9),
  (23,8),
  (24,7),
  (25,6),
  (26,5),
  (27,4),
  (28,3),
  (29,2),
  (30,1)


create table if not exists members (
  "firstname" text not null,
  "lastname" text not null,
  "yob" integer not null,
  "gender" text not null,
  "ussanum" text null,
  "team" text null,
  "registration_date" text not null,
  "ussa_status" text null,
  "last_update_ts" timestamp not null,
  "season" text null
) primary index season, last_update_ts;

copy members 
  (
  firstname $2,
  lastname $3,
  yob $4,
  gender $5,
  ussanum $6,
  team $9,
  registration_date $10,
  ussa_status $11,
  last_update_ts $source_file_timestamp
  )
  from 
''
WITH 
  CREDENTIALS = (AWS_ROLE_ARN = '')
  TYPE=CSV HEADER=TRUE;

update members set season = '2023-2024' where last_update_ts = (select max(last_update_ts) from members);



create table team_results (
  season text null,
  racedate date not null,
  racekey text null,
  racetype text not null,
  name text null,
  team text null,
  class text null,
  gender text null,
  run1_adjusted text null,
  run2_adjusted text null,
  total_adjusted text null,
  ranking integer null,
  counting_score text null,
  team_total text null,
  team_rank integer null,
  worldcup_points_by_team integer null,
  insert_ts timestamp not null
) primary index season, racekey, team, insert_ts
;


create table f_values (
  discipline text not null,
  f_value numeric not null,
  season text not null
);

insert into f_values
values
('Downhill',1250.00, '2024-2025'),
('Slalom', 730.00, '2024-2025'),
('Giant Slalom', 1010.00, '2024-2025'),
('Super-G', 1190.00, '2024-2025'),
('Alpine Combined', 1360.00, '2024-2025')
  ('Downhill',1250.00, '2023-2024'),
('Slalom', 730.00, '2023-2024'),
('Giant Slalom', 1010.00, '2023-2024'),
('Super-G', 1190.00, '2023-2024'),
('Alpine Combined', 1360.00, '2023-2024');

create table results_by_class (
  season text null,
  mountain text null,
  racekey text null,
  racetype text null,
  racedate date null,
  name text null,
  ussanumber text null,
  class text null,
  gender text null,
  run1 text null,
  run2 text null,
  total text null,
  worldcup_points_by_gender_class integer null,
  race_rank_by_gender_class integer null,
  race_points numeric null,
  member_status text null,
  insert_ts timestamp null
) primary index season, racekey, gender, class
  ;


create table results_by_gender (
  season text null,
  mountain text null,
  racekey text null,
  racetype text null,
  racedate date null,
  name text null,
  ussanumber text null,
  class text null,
  gender text null,
  run1 text null,
  run2 text null,
  total text null,
  worldcup_points_by_gender integer null,
  race_rank_by_gender integer null,
  race_points numeric null,
  member_status text null,
  insert_ts timestamp null
) primary index season, racekey, gender
  ;

create view results_by_gender_vw as 
select * from results_by_gender 
  where concat(racekey, insert_ts) in(select concat(racekey, max) from (select max(insert_ts) as max, racekey from results_by_gender group by all));

create view results_by_class_vw as 
select * from results_by_class
  where concat(racekey, insert_ts) in(select concat(racekey, max) from (select max(insert_ts) as max, racekey from results_by_class group by all));


CREATE TABLE "dsq" (
  "racedate" text NULL,
  "mountain" text NULL,
  "discipline" text NULL,
  "racename" text NULL,
  "run" text NULL,
  "racers" array(text NULL) NULL
) primary index racename;

create view members_vw as (
  select
  firstname, lastname, yob, gender, class, 
  max_by(ussanum, last_update_ts) as ussanum, 
  max_by(team, last_update_ts) as team, 
  max_by(registration_date, last_update_ts) as registration_date, 
  max_by(ussa_status, last_update_ts) as ussa_status,
  max(last_update_ts) as last_update_ts,
  season
  from
  (select firstname, lastname, yob, gender, c.class,
  case when ussanum is null then (lower(lastname)||', '||lower(firstname)) else ussanum end as ussanum,
  team,
  registration_date,
  ussa_status,
  last_update_ts,
  m.season
  from members m, classes c 
  where m.season = c.season
  and (m.yob >= c.start_year and m.yob <= c.end_year)
  )
  group by all
)
;

create table seasons (
  season text null,
  start_date date null,
  end_date date null
) primary index season;


insert into seasons values 
('2023-2024','2023-03-05', '2024-03-09'),
('2024-2025', '2024-03-10', '2025-03-08');

create table classes (
  class integer null,
  season text null,
  start_year integer null,
  end_year integer null
);

insert into classes values 
(1,'2023-2024', 1994, 2005),
(2,'2023-2024', 1989, 1993),
(3, '2023-2024', 1984, 1988),
(4, '2023-2024', 1979, 1983),
(5, '2023-2024', 1974, 1978),
(6, '2023-2024', 1969, 1973),
(7, '2023-2024', 1964, 1968),
(8, '2023-2024', 1959, 1963),
(9, '2023-2024', 1954, 1958),
(10, '2023-2024', 1949, 1953),
(11, '2023-2024', 1944, 1948),
(12, '2023-2024', 1939, 1943),
(13, '2023-2024', 1934, 1938),
(14, '2023-2024', 1900, 1933),
(1,'2024-2025', 1995, 2006),
(2,'2024-2025', 1990, 1994),
(3, '2024-2025', 1985, 1989),
(4, '2024-2025', 1980, 1984),
(5, '2024-2025', 1975, 1979),
(6, '2024-2025', 1970, 1974),
(7, '2024-2025', 1965, 1969),
(8, '2024-2025', 1960, 1964),
(9, '2024-2025', 1955, 1959),
(10, '2024-2025', 1950, 1954),
(11, '2024-2025', 1945, 1949),
(12, '2024-2025', 1940, 1944),
(13, '2024-2025', 1935, 1939),
(14, '2024-2025', 1900, 1934);


create table schedule (
  season text null,
  racename text null,
  racedate date null
);

insert into schedule values
('2023-2024','Gore Mountain, Slalom, 2023-03-05','2023-03-05'),
('2023-2024', 'Hunter Mountain, Slalom 1, 2024-01-06','2024-01-06'),
('2023-2024', 'Hunter Mountain, Slalom 2, 2024-01-06','2024-01-06'),
('2023-2024','Hunter Mountain, Giant Slalom, 2024-01-07','2024-01-07'),
('2023-2024','Montage Mountain, Giant Slalom, 2024-01-20','2024-01-20'),
('2023-2024','Montage Mountain, Slalom, 2024-01-20','2024-01-20'),
('2023-2024','Bear Creek, Giant Slalom, 2024-01-21','2024-01-21'),
('2023-2024','Mt. Southington, Slalom 1, 2024-02-03','2024-02-03'),
('2023-2024','Mt. Southington, Slalom 2, 2024-02-03','2024-02-03'),
('2023-2024','West Mountain, SuperG, 2024-02-16','2024-02-16'),
('2023-2024','West Mountain, Giant Slalom, 2024-02-17','2024-02-17'),
('2023-2024','West Mountain, Slalom, 2024-02-18','2024-02-18'),
('2023-2024','Catamount Resort, Giant Slalom, 2024-03-03','2024-03-03'),
('2023-2024','Gore Mountain, SuperG 1, 2024-03-08','2024-03-08'),
('2023-2024','Gore Mountain, SuperG 2, 2024-03-08','2024-03-08'),
('2023-2024','Gore Mountain, Giant Slalom, 2024-03-09','2024-03-09'),
('2024-2025', 'Gore Mountain, Slalom, 2024-03-10','2024-03-10'),
('2024-2025', 'Hunter Mountain, Giant Slalom, 2025-01-10','2025-01-10'),
  ('2024-2025','Hunter Mountain, Slalom 1, 2025-01-11','2025-01-11'),
  ('2024-2025','Hunter Mountain, Slalom 2, 2025-01-11','2025-01-11'),
  ('2024-2025','Willard Mountain, Slalom, 2025-01-18','2025-01-18'),
  ('2024-2025','Willard Mountain, Giant Slalom, 2025-01-19','2025-01-19'),
  ('2024-2025','Stratton Mountain, SuperG 1, 2025-01-24','2025-01-24'),
  ('2024-2025','Stratton Mountain, SuperG 2, 2025-01-24','2025-01-24'),
  ('2024-2025','Stratton Mountain, Giant Slalom, 2025-01-25','2025-01-25'),
  ('2024-2025','Labrador Mountain, Slalom 1, 2025-02-01','2025-02-01'),
  ('2024-2025','Labrador Mountain, Slalom 2, 2025-02-01','2025-02-01'),
  ('2024-2025','Greek Peak, Giant Slalom 1, 2025-02-02','2025-02-02'),
  ('2024-2025','Greek Peak, Giant Slalom 2, 2025-02-02','2025-02-02'),
  ('2024-2025','West Mountain, SuperG, 2025-02-14','2025-02-14'),
  ('2024-2025','West Mountain, Giant Slalom, 2025-02-15','2025-02-15'),
  ('2024-2025','West Mountain, Slalom, 2025-02-16','2025-02-16'),
  ('2024-2025','Big Boulder, Slalom, 2025-02-21','2025-02-21'),
  ('2024-2025','Montage Mountain, Giant Slalom, 2025-02-23','2025-02-23'),
  ('2024-2025','Montage Mountain, Slalom, 2025-02-23','2025-02-23'),
  ('2024-2025','Catamount Resort, Giant Slalom, 2025-03-02', '2025-03-02'),
  ('2024-2025','Hunter Mountain, Finals GS 1, 2025-03-07','2025-03-07'),
  ('2024-2025','Hunter Mountain, Finals GS 2, 2025-03-08','2025-03-08'),
  ('2025-2026','Hunter Mountain, Slalom, 2025-03-09','2025-03-09')
  ;

