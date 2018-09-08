DROP TABLE CORE_COURSE;
DROP TABLE MAJOR_REQUIRED_COURSE;
DROP TABLE MAJOR;
DROP TABLE PROGRAM;
DROP TABLE COURSE;

PRAGMA foreign_keys = ON;


CREATE TABLE COURSE
(
	course_code TEXT PRIMARY KEY,
	course_name TEXT,
	t1 INTEGER NOT NULL, --1 for offered, 0 for not
	t2 INTEGER NOT NULL, --1 for offered, 0 for not
	t3 INTEGER NOT NULL  --1 for offered, 0 for not
);
INSERT INTO COURSE (course_code, course_name, t1, t2, t3) VALUES ('COMP1917', 'Best Course', 1, 0, 0);

CREATE TABLE PROGRAM
(
	program_code TEXT,
	commence_year INTEGER,
	program_name TEXT,
	flexi_core_course INTEGER, --how many core courses are flexible(exchangeable) course in this progra,
	PRIMARY KEY(program_code, commence_year)  --Program 3978 commenced in 2017 has difference course requirements with 3978 in 2016
);
INSERT INTO PROGRAM (program_code, commence_year, program_name, flexi_core_course) VALUES ('COMP3978',2016, 'Computer Science',1);

CREATE TABLE CORE_COURSE
(
	course_code TEXT,
	program_code TEXT,
	commence_year INTEGER,
	is_flexi INTEGER DEFAULT 0, --1 for is a flexible core course, 0 for not   
	PRIMARY KEY(program_code, commence_year, course_code),
	FOREIGN KEY(program_code, commence_year) REFERENCES PROGRAM(program_code, commence_year),
	FOREIGN KEY(course_code) REFERENCES COURSE(course_code)
);

INSERT INTO CORE_COURSE (course_code, program_code, commence_year, is_flexi) VALUES ('COMP1917', 'COMP3978',2016, 0);


---------------------------------------------------^ MVP ^ ----------------------------------------------
--Assumption: Major does not have flexi courses 
CREATE TABLE MAJOR
(
	major_code TEXT PRIMARY KEY,
	major_name TEXT,
	lv1elective INTEGER NOT NULL, --number of lv1 electives required in the major apart from the complusory ones.
	lv2elective INTEGER NOT NULL, --number of lv2 electives required in the major apart from the complusory ones.
	lv3elective INTEGER NOT NULL, --number of lv3 electives required in the major apart from the complusory ones.
	program_code TEXT,
	commence_year INTEGER,
	FOREIGN KEY(program_code, commence_year) REFERENCES PROGRAM(program_code, commence_year)
);
INSERT INTO MAJOR (major_code, major_name, lv1elective, lv2elective, lv3elective, program_code, commence_year) VALUES('COMPA1', 'COMP SCIENCE', 0, 2, 5, 'COMP3978', 2016);

CREATE TABLE MAJOR_REQUIRED_COURSE
(
	major_code TEXT,
	course_code TEXT,
	PRIMARY KEY(major_code, course_code),
	FOREIGN KEY(major_code) REFERENCES MAJOR(major_code),
	FOREIGN KEY(course_code) REFERENCES COURSE(course_code)
);
INSERT INTO MAJOR_REQUIRED_COURSE(major_code, course_code) VALUES ('COMPA1', 'COMP1917');

