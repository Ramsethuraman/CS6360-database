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
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (117, -24456, null, null, null, 3047.612987, null, 2009, null, '2350-02-06_05:06:29', null, 'Lycosa godeffroyi');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (27, 12003, -2139004759, null, -2234141688717590874, -4860.574565, -89165.110140421, 2006, null, '4005-08-14_15:23:51', '3583-08-17', 'Aegypius tracheliotus');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (-1, 25145, 417873496, 2186055800140216875, null, null, -97196.200180214, 2005, null, '3526-03-01_15:24:24', '2214-02-17', 'Tockus erythrorhyncus');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (60, 19998, -2106749458, null, null, 4027.243865, -84493.804288493, 2008, '10:33:24', '3129-01-18_18:00:42', '2323-08-19', null);
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (-17, -19772, null, -6530468778662656861, 2419353340792694584, -6909.565293, 16597.529228456, 1999, '16:27:12', '2763-06-29_05:33:16', null, null);
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (-46, -20147, null, 407443103660878789, 7095016723894694899, null, null, 1993, '21:43:41', '3747-10-24_08:40:17', '2289-01-13', null);
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (79, -27237, 441760635, -5024059849614041294, 58460729560816550, -2849.669895, null, 2009, null, '1976-10-25_23:26:14', '2778-06-07', null);
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (-28, 11193, null, -2989904546804858801, null, 9008.681747, -55893.821433966, 2007, '16:31:10', '2216-03-10_11:28:20', null, 'Buteo jamaicensis');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (-32, -17991, -499967197, 596738665927766130, 6631318904669678775, null, null, null, null, '3859-06-27_07:29:28', '2166-11-02', null);
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (33, 8635, 2046642272, null, 6792153935845916579, null, -71927.503860261, 1995, null, '3161-01-23_19:29:37', null, 'Macaca mulatta');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (-56, -25543, 158960105, null, null, null, -79477.686220759, 2002, '15:46:43', '3263-03-17_06:29:15', null, null);
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (50, -24198, null, 3317072150077113120, 6343132469925673110, 8653.469804, null, 1990, '16:09:05', '2897-06-15_22:15:23', null, 'Eubalaena australis');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (-122, -28220, null, 1003906835857704225, -2266567142302550935, -9721.656639, 63907.861899983, null, null, '2308-11-07_10:44:24', '4014-03-01', 'Fulica cristata');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (-66, 27607, null, -2926524626184338452, null, null, null, 2001, null, '2071-07-15_23:04:30', null, null);
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (-34, 5947, -1863735930, -1867382206260602996, 1367280239369153678, 6563.291126, -75880.977901488, 2005, '1:03:15', '3878-02-24_07:49:25', null, null);
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (118, -29655, -207805914, null, -613130712376944765, -7951.313398, null, 2003, '3:19:05', '3445-09-15_12:26:10', null, 'Ursus americanus');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (97, 16884, null, 5910196381018434543, null, 527.415192, 57685.676677103, 1993, null, '3258-08-06_07:11:19', '3517-02-12', null);
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (-83, 7242, null, 4573528044052556540, 5720210041423118516, -6309.46469, null, 1977, null, '2817-10-07_18:42:43', null, null);
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (45, -24521, -1398203247, null, -1247080163325781342, -9322.426749, null, null, '22:09:10', '2657-01-10_12:17:10', null, null);
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (-21, -8779, null, -6688500644662107102, null, -2230.024168, null, 1993, null, '2317-01-21_05:17:17', null, null);

create index bozo (a);
create index bozo (b);
create index bozo (c);
create index bozo (d);
create index bozo (e);
create index bozo (f);
create index bozo (ff);
create index bozo (g);
create index bozo (h);
create index bozo (i);
create index bozo (j);
create index bozo (k);

INsERt iNTo bozo (a, b, c, d, e, f, ff, g, h, i, j, k) vALUes (-37, 4965, 741291863, -502741653393595862, nULl, Null, -29506.644934554, 1992, NULL, '2808-08-31_14:53:03', '2503-09-28', 'Phalacrocorax brasilianus');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (52, -8718, 813860981, -947933739670181903, null, -7434.559123, null, 1994, '22:41:08', '2968-07-22_12:58:57', null, 'Larus sp.');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (60, 14785, 221416417, null, null, -3097.56309, null, 1991, '23:48:46', '3565-02-15_23:06:28', null, null);
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (91, 1843, -1053999320, null, null, 9986.134015, null, 2011, null, '2870-03-18_11:16:40', null, 'Vanessa indica');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (0, 17947, 1769347097, 3361162114291881095, null, null, -23196.391984082, 2005, null, '3994-06-24_07:21:07', null, 'Ovibos moschatus');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (-36, 6335, null, null, -1337639509366749197, -2459.127032, null, 1999, null, '2369-03-18_22:55:44', '2146-08-06', null);
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (-77, 3391, null, -4432459282029899671, 2138455609261178225, null, 20040.575708552, null, null, '3195-10-19_05:00:31', null, 'Gymnorhina tibicen');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (110, 22761, -1141231698, 6540912560575690165, null, 228.636498, null, 2010, null, '3210-06-03_05:03:42', '2160-11-25', 'Echimys chrysurus');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (-115, -4192, -562136622, -7817169798750196786, -3311106542775863326, null, null, 1992, null, '2458-10-28_00:20:14', '3076-06-12', 'Aonyx cinerea');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (42, -25240, 208831230, 3297963365524855609, 5331694333568698105, -6751.726108, 44601.902953284, 2009, null, '2299-10-23_04:12:49', null, null);
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (36, -6263, null, 5497296411611578718, null, -7242.470548, 90208.893600253, 2003, null, '2865-07-25_16:51:56', null, null);
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (-7, -14708, null, null, null, -6241.159607, null, 2007, '20:02:17', '2393-03-13_01:41:30', '3741-02-21', 'Ciconia episcopus');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (-117, -12245, -1463673666, null, null, -8377.20061, 92172.530868338, 2006, '6:22:52', '2579-03-13_21:35:59', null, 'Cyrtodactylus louisiadensis');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (119, 8237, 961565151, null, -9079327691925968181, null, 66848.61131473, 2012, '9:42:37', '2055-08-12_23:41:41', null, 'Oreamnos americanus');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (113, 32471, -1686370810, null, 6958199543655714659, -480.846293, 17973.500115102, 1999, '17:00:08', '2817-08-30_09:22:08', '2601-01-11', 'Amblyrhynchus cristatus');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (-98, -12940, -1640401341, -7927337282752067418, null, null, -5574.206323435, null, '14:15:25', '2941-04-05_00:40:34', null, null);
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (-82, 20827, null, null, null, null, null, null, '22:41:53', '2248-03-15_19:16:20', null, null);
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (-83, -19882, -241116486, null, null, 1252.278282, 42944.484638201, 2004, null, '2596-07-30_18:56:59', '3731-02-14', 'Uraeginthus angolensis');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (-56, 18364, null, null, null, null, null, 2012, '18:25:52', '3375-06-05_04:46:10', null, 'Gyps fulvus');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (-98, -29698, null, null, null, null, null, 1995, null, '3908-08-10_17:13:21', '2240-02-21', null);
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (-13, 15505, -1822452189, null, null, -2155.918253, null, 1969, '9:15:49', '3933-05-30_04:26:10', null, 'Phascogale calura');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (-88, 22832, null, null, -1345747008524767030, 2619.493914, 74051.020398709, 1984, null, '2051-07-30_01:40:28', null, 'Myotis lucifugus');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (-101, 25058, null, null, -2480108113935791461, -1060.481102, null, 2010, '19:10:09', '3797-10-28_14:01:49', null, 'Pavo cristatus');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (74, -28761, null, 1948721800692509046, null, null, -79447.973866174, null, '9:54:42', '4006-10-08_13:51:16', '3019-11-14', 'Herpestes javanicus');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (103, 30526, -830872164, 4074335931694101127, 5564640300868087015, null, null, 2000, null, '3204-01-08_15:25:37', '3942-04-21', 'Agkistrodon piscivorus');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (-6, -17190, null, null, -9019063346293692701, 122.626738, -58178.800816263, 2010, '8:38:07', '3853-05-10_22:15:36', null, null);
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (115, -9855, null, -5858646175904622984, -4152653164507553611, 3832.600889, null, 1987, null, '2993-02-07_13:53:51', null, 'Megaderma spasma');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (-33, 25137, null, null, null, null, 81592.921507294, null, null, '3592-08-20_00:37:12', '3870-04-13', null);
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (-102, 2488, 2021382671, null, null, -2202.367093, -56831.965746965, null, '12:41:10', '2894-12-12_17:12:21', null, 'Acanthaster planci');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (-45, 18844, 2051880856, 4566660419248947655, 5307142444106875908, -7996.149692, null, 1993, null, '2390-09-04_07:48:34', null, 'Cyrtodactylus louisiadensis');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (-81, -12486, null, 4869473167945249746, null, null, -75435.381979613, 2010, '11:48:29', '3977-12-24_12:16:01', '3299-10-10', 'Myrmecophaga tridactyla');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (-79, -10992, -1615593291, null, -5691427332331569465, null, null, 1993, null, '3546-03-14_05:32:00', null, 'Macropus rufogriseus');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (-97, -14868, null, 3944099696798453928, -5277188394755721372, 9660.449769, null, 2009, '14:43:08', '2416-06-19_22:01:17', null, null);
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (-59, 28456, 715789249, null, -6863767058874949238, null, 62997.196720756, 1990, '9:42:19', '3152-03-29_13:57:31', '2929-10-11', 'Merops nubicus');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (-37, -29312, null, null, 853057445518320741, null, null, 2011, null, '2262-11-07_23:38:21', null, null);
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (105, -11715, null, -4073583880729997908, null, 3494.192933, null, null, null, '3879-07-07_03:38:30', null, 'Coluber constrictor');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (-67, 7117, null, 948991751042846511, null, -8260.657751, 52238.482701904, 2008, '6:43:04', '3274-03-02_17:46:22', '2644-04-26', null);
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (23, 29941, null, null, 9214790524371935935, null, 31055.657061831, 2001, null, '2322-01-30_17:56:40', null, null);
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (-96, 12544, -153380500, -2084551134230996045, -573312392453959792, 5786.547488, 28855.343279033, null, '0:35:41', '3235-01-18_05:29:59', null, 'Chauna torquata');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (-121, 28886, 898443395, null, null, 3036.257891, 69962.319362501, 2003, '14:52:02', '2348-12-06_01:02:36', '3567-11-30', 'Lorythaixoides concolor');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (94, 10774, null, null, null, null, -81959.637132613, 1970, '2:13:00', '3873-11-19_21:27:39', '3288-09-15', 'Anthropoides paradisea');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (44, -20630, -1016719367, -4043639137884201921, null, -3068.356354, 6208.294360409, 1994, '5:57:10', '2006-04-13_23:47:57', null, 'Francolinus coqui');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (103, -9003, -76106914, null, null, -4311.156035, null, 2000, '11:11:42', '2186-11-16_03:13:33', null, 'Phoenicopterus ruber');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (108, -5053, null, 3707945522782392417, 9086835130987048195, -8421.101608, null, null, null, '2191-05-15_16:04:18', null, 'Geochelone radiata');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (36, -32012, null, -3487317153026696427, null, null, 76763.075595262, 1993, null, '2975-10-20_07:16:25', '2514-04-02', null);
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (null, 6025, null, -5016234605458205772, null, null, -91490.632498362, 2012, null, null, null, 'Felis chaus');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (-47, -14188, -486815283, 3692846280211773432, 5168346228318135520, null, null, 2011, '5:59:09', '2545-08-24_23:41:43', null, 'Cervus elaphus');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (-43, 1575, null, null, 6792577000284770896, null, null, 1997, '13:07:07', '3215-03-20_19:19:01', null, 'Leptoptilos crumeniferus');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (97, -26758, null, null, -293545473549721544, null, 54443.724284244, 2003, null, '2602-01-12_06:41:08', '2957-10-10', 'Corvus albus');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (5, -4787, 814037655, 1223665732253329954, null, -3006.803205, -70125.241974523, 2002, '0:01:42', '3377-09-25_18:53:25', null, null);
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (-19, 2614, 1416198012, 7338504794653973926, -4205713136191043995, null, 75961.772972047, 1998, '18:56:50', '2054-03-23_04:52:20', null, 'Ephipplorhynchus senegalensis');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (-84, 16900, null, null, null, 8267.898896, 4934.284859079, null, null, '3585-03-16_19:45:02', '2544-09-27', 'Casmerodius albus');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (104, -17642, null, 2259115768108878020, 1925324870397651546, 5811.364118, -6125.06342993, null, '7:55:18', '2801-05-22_02:06:54', null, 'Connochaetus taurinus');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (-107, 11537, -118190600, -430817676749338736, null, null, 87254.811853792, 1990, '6:01:34', '2304-06-25_00:27:47', '2852-01-30', 'Sceloporus magister');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (-5, 27580, 1115831407, -1700770198255523463, null, -4643.275813, -77003.542018985, 2010, '10:33:25', '3021-02-14_12:36:26', '2823-11-06', 'Cervus canadensis');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (-83, 11231, null, 3706809880348618524, -716270101001600460, 9475.364274, -24739.625526572, 1999, null, '1985-11-25_15:27:31', null, null);
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (98, -7919, -628753227, null, 1358699629226512619, null, 75966.958502056, 2012, null, '3183-12-06_13:50:24', null, null);
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (21, -23439, null, -579768456430920747, null, -8650.373047, 91057.072337035, 2004, '6:49:56', '2791-05-23_15:22:11', null, null);
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (-78, 23238, null, 1680015187477449043, null, 7034.58214, -12570.682913346, null, '9:06:59', '3596-06-01_12:32:46', null, null);
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (43, -13802, -95126182, null, null, null, null, null, '8:27:06', '2041-05-01_03:29:42', '3430-10-27', 'Neotis denhami');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (-49, 29293, 617449444, null, 7781050871897206843, null, 3123.042954031, 2000, null, '2649-04-06_22:41:47', '3999-03-05', 'Crotalus triseriatus');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (85, 8492, 1860907293, -8217975820513796209, -3647372294334837266, -7361.552576, -19627.532490115, null, '20:13:53', '2087-11-07_22:43:43', '3686-10-14', 'Gopherus agassizii');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (-91, -19670, 884935089, -7303241258448980894, -5036095013261740418, 201.426776, null, 2009, null, '2704-04-14_20:36:02', '2361-09-19', 'Ardea golieth');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (91, 27328, null, -1589469336050451407, -5355970010970492568, 8309.596634, null, 1999, null, '3206-03-26_20:21:54', '2586-06-29', 'Aonyx capensis');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (25, 27650, -1263650430, null, null, null, null, 2004, null, '3019-08-29_00:27:31', '3466-10-22', 'Tiliqua scincoides');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (90, -11757, -1308349002, 2149565041662423992, null, null, null, 2010, null, '3032-11-30_07:39:58', null, 'Macaca fuscata');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (-36, 17975, null, null, 7345310926912093686, -336.517992, -76792.384206314, null, null, '3596-02-19_18:23:33', '3107-06-02', 'Laniaurius atrococcineus');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (null, 3153, null, null, 5887892618924840203, 6050.762088, -6337.469204091, 1997, '9:39:03', null, '3127-11-04', 'Colobus guerza');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (-76, 15207, -336709248, 7128100551625052498, -7407655165748422734, null, null, null, null, '2173-09-10_06:37:38', null, null);
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (22, -13020, -1184839149, null, -688458017005839331, null, null, 1998, null, '2930-03-06_16:46:01', null, null);
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (62, -30849, -1634891096, -8149417560178700648, null, null, 32544.694537612, 1996, null, '3836-03-24_21:36:33', '3216-06-05', null);
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (35, 31656, null, 3927515170852283601, null, 1856.683971, null, 2001, null, '2497-12-31_05:28:06', null, 'Cervus unicolor');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (39, -15087, null, null, -5861377521953913876, 1956.621723, -34933.67735856, 2001, '4:47:56', '2838-10-10_17:08:31', '2482-12-23', 'Actophilornis africanus');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (-7, -15546, null, null, 3562315999456602047, null, null, 2011, null, '3942-10-08_15:09:28', '2373-06-20', 'Colaptes campestroides');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (14, -25228, -659664441, null, null, null, -1658.091177683, 2002, null, '2865-07-29_22:57:14', '2307-09-15', 'Spermophilus armatus');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (-122, -26959, null, 7512661216006682828, null, -8164.671989, 94035.19111252, 1994, '3:45:55', '2850-12-02_04:14:38', null, 'Fregata magnificans');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (-121, 26863, null, null, null, -7612.361618, -35912.08161669, null, '8:04:15', '3798-07-14_08:12:16', '2088-02-27', 'Echimys chrysurus');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (-75, 5491, -461670728, null, null, 8201.510561, -85791.670388553, 1997, null, '2537-11-27_16:34:17', '3759-11-05', 'Iguana iguana');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (-15, -11024, null, null, null, null, null, 2007, '11:33:28', '3722-05-08_21:13:46', '3681-05-13', 'Sarkidornis melanotos');
insert into bozo (a, b, c, d, e, f, ff, g, h, i, j, k) values (-120, -26376, -748631316, 2101580588768195916, null, -1328.096323, -76844.499951139, null, '0:45:01', '3008-08-28_05:20:00', null, 'Dicrurus adsimilis');

debug "***********************************";
debug "* SELECTIONS **********************";
debug "***********************************";

select * from bozo where e = -7407655165748422734;
select * from bozo where k = 'Iguana iguana';
select * from bozo where i = '3008-08-28_05:20:00';
select * from bozo where i < '3008-08-28_05:20:00';

sEleCT * FroM bozo wHErE h <= '11:33:28';

dElEte fRom tABLe bozo wHERe not h <= '11:33:28';

select * from bozo where h > '11:33:28';
select * from bozo where h >= '11:33:28';
select * from bozo where not h > '11:33:28';
select * from bozo;

delete from table bozo;
select * from bozo;

dROp tABle bozo;


