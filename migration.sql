BEGIN;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> e87fdddfa319

CREATE TABLE users (
    id VARCHAR NOT NULL, 
    username VARCHAR NOT NULL, 
    password VARCHAR NOT NULL, 
    email VARCHAR NOT NULL, 
    CONSTRAINT users_id PRIMARY KEY (id), 
    UNIQUE (email), 
    CONSTRAINT email_un UNIQUE (email), 
    UNIQUE (username), 
    CONSTRAINT username_un UNIQUE (username)
);

CREATE INDEX ix_users_id ON users (id);

CREATE TABLE offers (
    id VARCHAR NOT NULL, 
    user_id VARCHAR NOT NULL, 
    text VARCHAR, 
    CONSTRAINT offers_id PRIMARY KEY (id), 
    FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE INDEX ix_offers_id ON offers (id);

INSERT INTO alembic_version (version_num) VALUES ('e87fdddfa319');

-- Running upgrade e87fdddfa319 -> 4675f7f77a12

ALTER TABLE offers ADD COLUMN title VARCHAR NOT NULL;

UPDATE alembic_version SET version_num='4675f7f77a12' WHERE alembic_version.version_num = 'e87fdddfa319';

-- Running upgrade 4675f7f77a12 -> 70ad0a56c17e

ALTER TABLE users ADD COLUMN salt VARCHAR NOT NULL;

ALTER TABLE users ADD CONSTRAINT salt_un UNIQUE (salt);

ALTER TABLE users ADD UNIQUE (salt);

UPDATE alembic_version SET version_num='70ad0a56c17e' WHERE alembic_version.version_num = '4675f7f77a12';

COMMIT;

