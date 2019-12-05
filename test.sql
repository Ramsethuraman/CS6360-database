-- Create table
CREATE TABLE bozo (
  a TINYINT UNIQUE,
  b SMALLINT NOT NULL,
  c INT,
  d BIGINT,
  e LONG,
  ff FLOAT, 
  f DOUBLE,
  g YEAR,
  h TIME,
  i DATETIME,
  j DATE,
  k TEXT
-- TODO: primary keys
);

-- Check number of columns
select * from davisbase_columns where table_rowid= 3;

-- Insert an row
insert into bozo (a, b, c, d, e, ff, f, g, h, i, j, k) values (
  12, 1234, 2345444, 435234523235, -243545223452424, 2.3575435244,
  2.42345224343, 2017, '11:05:02', '2001-12-23_04:20:00', '2001-09-11', 
  'asjdkfljsa'
);

select * from bozo;
