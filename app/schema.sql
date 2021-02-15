DROP TABLE IF EXISTS meeting;
DROP TABLE IF EXISTS contact;
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS revoked_token;
DROP TABLE IF EXISTS meetings_to_contacts;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL
);

CREATE TABLE meeting (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  datetime TEXT NOT NULL,
  user_id INTEGER NOT NULL,
  FOREIGN KEY (user_id) REFERENCES user(id)
);

CREATE TABLE contact (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  first_name TEXT NOT NULL,
  second_name TEXT,
  telephone TEXT,
  user_id INTEGER NOT NULL,
  FOREIGN KEY (user_id) REFERENCES user(id)
);

CREATE TABLE meetings_to_contacts (
  meeting_id INTEGER NOT NULL,
  contact_id INTEGER NOT NULL,
  FOREIGN KEY (meeting_id) REFERENCES meeting(id),
  FOREIGN KEY (contact_id) REFERENCES contact(id),
  PRIMARY KEY (meeting_id, contact_id)
);

CREATE TABLE revoked_token (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  token TEXT NOT NULL
);