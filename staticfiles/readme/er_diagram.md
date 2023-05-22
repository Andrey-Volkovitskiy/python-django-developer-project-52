// ER diagram builder - https://dbdiagram.io/d

Table Task {
  id integer [primary key]
  name varchar [unique]
  description text
  author integer [ref: > User.id]
  executor integer [null, ref: > User.id]
  status integer [ref: > Status.id]
  labels integer [null, ref: <> Label.id]
  created_at timestamp 
}

Table User {
  id integer [primary key]
  username varchar
  first_name varchar
  last_name varchar
  password varchar
  date_joined timestamp
}

Table Status {
  id integer [primary key]
  name varchar [unique]
  created_at timestamp 
}

Table Label {
  id integer [primary key]
  name varchar [unique]
  created_at timestamp 
}
