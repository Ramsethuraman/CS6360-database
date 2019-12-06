CREATE TABLE test_2 (
  id TINYINT UNIQUE,
  name TEXT NOT NULL,
  salary INT NOT NULL
);

insert into test_2 (id, name, salary) values (1, 'Micheal Jordan', 48000);
insert into test_2 (id, name, salary) values (2, 'Jeff Bezos', 350);
insert into test_2 (id, name, salary) values (3, 'George Washington', 1);
insert into test_2 (id, name, salary) values (4, 'Jeb', 123);

delete from table test_2 where id = 2;
delete from table test_2 where name = 'Jeb';

-- Won't delete anything
delete from table test_2 where name = 'notintable';