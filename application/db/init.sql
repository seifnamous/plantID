
DROP DATABASE IF EXISTS Plants;
CREATE DATABASE Plants;
use Plants;

CREATE TABLE flowers
(
id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
file_name VARCHAR(10),
type VARCHAR(50) DEFAULT 'not known'
);

INSERT INTO flowers VALUES

(1,'p1.jpg','to be identified'),
(2,'p2.jpg','to be identified'),
(3,'p3.jpg','to be identified'),
(4,'p4.jpg','to be identified');
