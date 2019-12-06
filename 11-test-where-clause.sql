CREATE TABLE test_1 (
  id TINYINT UNIQUE,
  name TEXT NOT NULL,
  salary INT NOT NULL
);

insert into test_1 (id, name, salary) values (1, 'Micheal Jordan', 48000);
insert into test_1 (id, name, salary) values (2, 'Jeff Bezos', 350);

create index test_1 (id);
create index test_1 (name);
create index test_1 (salary);

debug '*******************************';
insert into test_1 (id, name, salary) values (3, 'George Washington', 1);
insert into test_1 (id, name, salary) values (4, 'Jeb', 123);
debug '*******************************';

-- Should fail - UNIQUE constraint error
insert into test_1 (id, name, salary) values (4, 'abc', 123);

-- Should fail - NOT NULL constraint error
insert into test_1 (id, salary) values (5, 123);

select * from test_1 where id >= 2;
select * from test_1 where id = 3;
select * from test_1 where id <= 3;
select * from test_1 where name = 'Jeb';
select * from test_1 where name != 'def';

