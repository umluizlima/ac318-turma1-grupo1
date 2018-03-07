create table if not exists users (
  id integer primary key autoincrement,
  username text not null,
  'password' text not null,
  constraint username_unique unique (username)
);

create table if not exists emails (
    id integer primary key autoincrement,
    userId integer not null,    
    tag text not null,
    email text not null,
    foreign key (userId) references users (id)
);

create table if not exists phones (
    id integer primary key autoincrement,
    userId integer not null,
    tag text not null,
    phone text not null,
    foreign key (userId) references users (id)
);