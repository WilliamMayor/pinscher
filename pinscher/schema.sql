BEGIN TRANSACTION;
CREATE TABLE Credentials(
    domain TEXT,
    username TEXT, 
    password TEXT,
    iv TEXT,
    PRIMARY KEY (domain, username)
);
CREATE INDEX credentials_domain_index ON Credentials(domain);
CREATE INDEX credentials_username_index ON Credentials(username);
COMMIT;