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
  i DATETIME UNIQUE,
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

insert into bozo (b) values (23);
select * from bozo;

-- Causes errors below
insert into bozo (b) values (23);
insert into bozo (b) values (23);

insert into bozo (a, b, i) values (13, 23, '2001-12-23_04:21:00');

-- Should cause an error
insert into bozo (a, b, i) values (44, 56, '2001-12-23_04:20:00.00');
select * from bozo;

-- Bulk add
insert into bozo (a, b, c, d, e, f, g, h, i, j) values (-126, -17431, null, null, null, null, 88786.267860085, null, '3849-08-09 07:00:11', null);
insert into bozo (a, b, c, d, e, f, g, h, i, j) values (-124, -11271, 1824128946, -737671856866048618, null, null, -67705.203634412, '3:58', '3652-11-04 07:00:19', '2387-08-18');
insert into bozo (a, b, c, d, e, f, g, h, i, j) values (-73, -10118, -423511428, null, null, -2878.124659, null, null, '3455-01-22 12:25:02', null);
insert into bozo (a, b, c, d, e, f, g, h, i, j) values (-60, -4345, null, -1401872803225177340, null, null, null, '18:50', '3477-06-30 19:33:15', null);
insert into bozo (a, b, c, d, e, f, g, h, i, j) values (45, 3023, -1192398962, -3815648648031963600, -2545964231479416545, 1271.774543, null, '15:28', '2361-07-11 01:55:42', null);
insert into bozo (a, b, c, d, e, f, g, h, i, j) values (-96, -2371, -1754070351, -5591970076802725634, -6748202523423488995, null, 36162.162289208, '17:27', '3006-07-03 08:37:12', '2876-09-28');
insert into bozo (a, b, c, d, e, f, g, h, i, j) values (-80, -24029, null, null, 7340251052631038247, 7373.085028, -21933.800411898, null, '2103-08-04 13:03:07', null);
insert into bozo (a, b, c, d, e, f, g, h, i, j) values (-26, 23543, 1942131749, 380262217117386478, null, 3435.822432, 58744.424348438, '13:41', '2822-06-23 01:40:32', '3721-06-13');
insert into bozo (a, b, c, d, e, f, g, h, i, j) values (-55, 3411, null, -5226549234097104661, -8725176149607095869, -507.449975, -24909.199632594, null, '3840-11-25 03:29:26', null);
insert into bozo (a, b, c, d, e, f, g, h, i, j) values (15, -7236, null, null, null, -8790.96048, -98940.781449218, null, '2652-05-25 18:58:40', '3258-12-10');
insert into bozo (a, b, c, d, e, f, g, h, i, j) values (68, -12209, null, null, -6549101337776321762, 2498.467855, null, '21:13', '2824-06-24 06:21:34', '3875-03-19');
insert into bozo (a, b, c, d, e, f, g, h, i, j) values (51, -27104, 1977869721, 8290185982651111599, 4037275033535557478, 3206.045416, 33551.336365302, '14:49', '2493-11-25 06:43:34', null);
insert into bozo (a, b, c, d, e, f, g, h, i, j) values (-56, -24904, null, null, -527233092488888858, -4018.205954, null, null, '3807-06-23 16:07:26', null);
insert into bozo (a, b, c, d, e, f, g, h, i, j) values (108, 15068, null, null, null, -1322.613658, -96743.369779346, '7:26', '2284-09-28 11:03:00', null);
insert into bozo (a, b, c, d, e, f, g, h, i, j) values (58, -14020, null, null, null, -1300.791572, null, null, '2763-07-21 08:14:32', null);
insert into bozo (a, b, c, d, e, f, g, h, i, j) values (-81, -6176, null, null, null, null, null, '6:40', '3663-03-25 22:06:47', '2921-03-12');
insert into bozo (a, b, c, d, e, f, g, h, i, j) values (102, 31579, -1824526116, null, null, null, 24290.114523665, null, '3085-07-08 08:50:17', '2799-04-04');
insert into bozo (a, b, c, d, e, f, g, h, i, j) values (-93, 27765, 933612365, 5766455079488626361, -2884901129352286896, -4433.075924, 93350.590671511, null, '2115-01-14 16:20:30', '3093-06-02');
insert into bozo (a, b, c, d, e, f, g, h, i, j) values (-36, 10379, null, -5748721365613275442, -6191892222009836045, null, -29692.851732762, '19:38', '2145-01-07 05:37:59', null);
insert into bozo (a, b, c, d, e, f, g, h, i, j) values (-45, 1141, null, -5061531237318615951, 2933765053690513394, null, 61329.972806295, '16:59', '3753-11-16 17:14:44', null);
insert into bozo (a, b, c, d, e, f, g, h, i, j) values (-118, 18441, 236488891, 9212840367535773224, -2610905174059498151, null, -72816.351082509, null, '3287-04-30 09:02:14', null);
insert into bozo (a, b, c, d, e, f, g, h, i, j) values (-89, -8569, 136192824, 1031770121756118791, null, 9661.145635, null, null, '3677-05-16 00:27:06', '2047-03-16');
insert into bozo (a, b, c, d, e, f, g, h, i, j) values (null, 17705, null, -1437527779268510470, 3371525291303712940, 360.892363, null, '4:35', null, null);
insert into bozo (a, b, c, d, e, f, g, h, i, j) values (null, 23639, null, null, -5385768644429373275, 2659.254739, 35633.750991462, '21:32', null, null);
insert into bozo (a, b, c, d, e, f, g, h, i, j) values (-94, 28776, null, -6085521660326275017, null, null, 77055.263235608, '23:05', '2951-06-19 00:45:32', null);
insert into bozo (a, b, c, d, e, f, g, h, i, j) values (-20, -17206, null, null, 2753342733468756742, null, -71854.216823717, null, '2322-01-24 04:34:34', '1982-10-14');
insert into bozo (a, b, c, d, e, f, g, h, i, j) values (12, 11725, null, null, null, null, -51557.016617161, null, '2029-06-14 23:16:27', null);
insert into bozo (a, b, c, d, e, f, g, h, i, j) values (43, -3395, null, 8393751628482021177, -5898324103736305842, null, null, '16:15', '2739-04-19 23:08:11', '2139-11-19');
insert into bozo (a, b, c, d, e, f, g, h, i, j) values (-32, 6976, null, null, null, 9781.235977, null, '11:58', '3161-08-12 18:46:35', null);
insert into bozo (a, b, c, d, e, f, g, h, i, j) values (47, -7476, -49593112, 2276687574534751942, -5382648361202666807, null, 89724.156937694, '1:58', '3344-01-02 20:42:14', '3802-12-11');
insert into bozo (a, b, c, d, e, f, g, h, i, j) values (33, -109, null, -2854264772043674807, -7740738266629157307, null, -28193.018845079, '12:55', '2018-04-03 22:08:37', null);
insert into bozo (a, b, c, d, e, f, g, h, i, j) values (49, 21390, 978990415, -3017564108443694901, -6970723800491344507, -5735.17177, null, null, '3114-05-06 20:08:35', null);
insert into bozo (a, b, c, d, e, f, g, h, i, j) values (65, 4629, -1995597697, -2131109648088827527, null, 1940.056843, -30880.387927593, null, '2886-06-09 16:13:24', null);
insert into bozo (a, b, c, d, e, f, g, h, i, j) values (null, 6869, 797992325, -5019975916687331441, -8304234159825233355, null, 43804.729379357, null, null, '3254-04-07');
insert into bozo (a, b, c, d, e, f, g, h, i, j) values (36, -3139, null, null, null, -4255.738855, -88294.298849666, null, '2337-02-22 10:31:43', null);
insert into bozo (a, b, c, d, e, f, g, h, i, j) values (110, -4997, null, null, null, null, -28247.497976977, '6:31', '3082-12-28 02:38:54', null);
insert into bozo (a, b, c, d, e, f, g, h, i, j) values (-16, -30832, 1724801396, null, null, null, -8443.878311486, null, '3780-06-14 21:21:09', null);
insert into bozo (a, b, c, d, e, f, g, h, i, j) values (-50, 4073, null, null, -8593849639784669013, 8771.995054, 52832.62784547, '9:50', '3466-03-19 21:56:06', '3855-09-23');
insert into bozo (a, b, c, d, e, f, g, h, i, j) values (0, 5841, -1010986381, null, null, null, 94904.295168884, null, '3017-11-10 03:13:34', '3313-09-26');
insert into bozo (a, b, c, d, e, f, g, h, i, j) values (115, -1120, null, null, 7306529319039677338, null, 9745.421347586, '21:07', '2044-10-03 09:59:34', '2762-02-16');
insert into bozo (a, b, c, d, e, f, g, h, i, j) values (-87, -21771, -127237101, 5339051354264330907, null, -6639.950034, null, '12:13', '3117-05-27 02:17:07', null);
insert into bozo (a, b, c, d, e, f, g, h, i, j) values (127, 7806, null, 27
