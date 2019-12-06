CREATE TABLE test_3 (
  id TINYINT UNIQUE,
  name TEXT NOT NULL,
  salary INT NOT NULL
);

insert into test_3 (id, name, salary) values (1, 'Micheal Jordan', 48000);
insert into test_3 (id, name, salary) values (2, 'Jeff Bezos', 350);
insert into test_3 (id, name, salary) values (3, 'George Washington', 1);
insert into test_3 (id, name, salary) values (4, 'Jeb', 123);

UPDATE test_3 SET name = 'Mikey' WHERE id = 1;

-- Won't update anything
UPDATE test_3 SET name = 'Mikey' WHERE id = 123;