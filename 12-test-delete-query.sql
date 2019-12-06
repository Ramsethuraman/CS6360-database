CREATE TABLE test_2 (
  id TINYINT UNIQUE,
  name TEXT NOT NULL,
  salary INT NOT NULL
);

create index test_2 (id);

insert into test_2 (id, name, salary) values (1, 'Micheal Jordan', 48000);
insert into test_2 (id, name, salary) values (2, 'Jeff Bezos', 350);
insert into test_2 (id, name, salary) values (3, 'George Washington', 1);
insert into test_2 (id, name, salary) values (4, 'Jeb', 123);

select * from test_2;

delete from table test_2;

select * from test_2;

delete from table test_2 where name = 'Jeb';

insert into test_2 (id, name, salary) values (1, 'George Washington', 1);
insert into test_2 (id, name, salary) values (4, 'Jeb', 123);

select * from test_2;

-- Won't delete anything
delete from table test_2 where name = 'notintable';
