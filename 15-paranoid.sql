CREATE TABLE test_3 (
  id DATE NOT NULL PRIMARY KEY,
  name TEXT NOT NULL,
  salary INT  NOT NULL
);

insert into test_3 (id, name, salary) values ('2015-11-01', 'Micheal Jordan', 48000);
insert into test_3 (id, name, salary) values ('2001-09-11', 'Jeff Bezos', 350);
insert into test_3 (id, name, salary) values ('1980-10-30', 'George Washington', 1);
insert into test_3 (id, name, salary) values ('1995-10-01', 'Jeb', 123);

UPDATE test_3 SET name = 'Mikey' WHERE id = '2001-09-11';

SELECT * FROM test_3;

-- Won't update anything
UPDATE test_3 SET name = 'Mikey' WHERE id >= '2000-10-30';

SELECT * FROM test_3;
