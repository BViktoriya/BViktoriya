CREATE TABLE IF NOT EXISTS users (
user_id integer primary key autoincrement not null,
fio text not null,
viber_id text not null unique,
t_last_answer timestamp null
);

CREATE TABLE IF NOT EXISTS learning (
user_id integer not null,
word text not null,
correct_answer integer not null default 0,
t_last_correct_answer timestamp null,
primary key (user_id, word),
foreign key (user_id) references users(user_id)
);

--CREATE TABLE IF NOT EXIST game (
--game_id integer primary key autoincrement not null,
--user_id integer not null,
--count_all integer not null,
--count_correct integer not null,
--foreign key (user_id) references users(user_id)
--);