DROP TABLE CORE_COURSE;
DROP TABLE MAJOR_REQUIRED_ELECTIVE;
DROP TABLE MAJOR_REQUIRED_ELECTIVE_SPECIFIC;
DROP TABLE MAJOR_REQUIRED_COURSE;
DROP TABLE MAJOR;
DROP TABLE PREREQUISITE;
DROP TABLE EXCLUDE;
DROP TABLE PROGRAM;
DROP TABLE COURSE;

PRAGMA foreign_keys = ON;


CREATE TABLE COURSE
(
	course_code TEXT PRIMARY KEY,
	course_name TEXT,
	t1 INTEGER NOT NULL, --1 for offered, 0 for not
	t2 INTEGER NOT NULL, --1 for offered, 0 for not
	t3 INTEGER NOT NULL,  --1 for offered, 0 for not
	summer INTEGER NOT NULL,  --1 for offered, 0 for not
	is_gen INTEGER NOT NULL  --1 for this course is  a general education course, 0 is not
);
--INSERT INTO COURSE (course_code, course_name, t1, t2, t3, summer, is_gen) VALUES ('COMP1917', 'Best Course', 1, 0, 0, 1, 1);
--INSERT INTO COURSE (course_code, course_name, t1, t2, t3, summer, is_gen) VALUES ('MATH1141', 'Best Course', 1, 0, 0, 0, 0);
--INSERT INTO COURSE (course_code, course_name, t1, t2, t3, summer, is_gen) VALUES ('MATH1131', 'Best Course', 1, 0, 0, 1, 1);
--INSERT INTO COURSE (course_code, course_name, t1, t2, t3, summer, is_gen) VALUES ('MATH1231', 'Best Course', 1, 0, 0, 0, 1);

CREATE TABLE PROGRAM
(
	program_code INTEGER,
	commence_year INTEGER,
	program_name TEXT,
	general_course INTEGER, --indicates how many general courses are required in the program
	free_elective INTEGER, --indicates how many free_electives are required in the program
	flexi_core_course INTEGER, --how many core courses are flexible(exchangeable) course in this progra,
	PRIMARY KEY(program_code, commence_year)  --Program 3978 commenced in 2017 has difference course requirements with 3978 in 2016
);
--INSERT INTO PROGRAM (program_code, commence_year, program_name, general_course, free_elective, flexi_core_course) VALUES ('COMP3978',2016, 'Computer Science', 5, 5, 1);

CREATE TABLE CORE_COURSE
(
	course_code TEXT,
	program_code INTEGER,
	commence_year INTEGER,
	is_flexi INTEGER DEFAULT 0, --1 for is a flexible core course, 0 for not   
	PRIMARY KEY(program_code, commence_year, course_code),
	FOREIGN KEY(program_code, commence_year) REFERENCES PROGRAM(program_code, commence_year),
	FOREIGN KEY(course_code) REFERENCES COURSE(course_code)
);
--INSERT INTO CORE_COURSE (course_code, program_code, commence_year, is_flexi) VALUES ('COMP1917', 'COMP3978',2016, 0);
--INSERT INTO CORE_COURSE (course_code, program_code, commence_year, is_flexi) VALUES ('MATH1131', 'COMP3978',2016, 1);
--INSERT INTO CORE_COURSE (course_code, program_code, commence_year, is_flexi) VALUES ('MATH1231', 'COMP3978',2016, 1);


---------------------------------------------------^ MVP ^ ----------------------------------------------
--Assumption: Major does not have flexi courses, major_code is uniq 
CREATE TABLE MAJOR
(
	major_code TEXT PRIMARY KEY,
	major_name TEXT,
	lv1elective INTEGER NOT NULL, --number of lv1 electives required in the major apart from the complusory ones.
	lv2elective INTEGER NOT NULL, --number of lv2 electives required in the major apart from the complusory ones.
	lv3elective INTEGER NOT NULL, --number of lv3 electives required in the major apart from the complusory ones.
	program_code INTEGER,
	commence_year INTEGER,
	FOREIGN KEY(program_code, commence_year) REFERENCES PROGRAM(program_code, commence_year)
);
--INSERT INTO MAJOR (major_code, major_name, lv1elective, lv2elective, lv3elective, program_code, commence_year) VALUES('COMPA1', 'COMP SCIENCE', 0, 2, 5, 'COMP3978', 2016);

CREATE TABLE MAJOR_REQUIRED_COURSE
(
	major_code TEXT,
	course_code TEXT,
	PRIMARY KEY(major_code, course_code),
	FOREIGN KEY(major_code) REFERENCES MAJOR(major_code),
	FOREIGN KEY(course_code) REFERENCES COURSE(course_code)
);
--INSERT INTO MAJOR_REQUIRED_COURSE(major_code, course_code) VALUES ('COMPA1', 'COMP1917');

--this table address the amount of each lv electives one major needs to take
CREATE TABLE MAJOR_REQUIRED_ELECTIVE
(
	major_code TEXT,
	course_level INTEGER, --what level the course has to be at
	course_amount INTEGER, --how many this lvl courses needs to be taken, if exists interchangeable courses, the course_aount in each relevant tuple will be the same
	group_id INTEGER, --interchangable courses will have the same group id
	PRIMARY KEY(major_code, course_level, group_id),
	FOREIGN KEY(major_code) REFERENCES MAJOR(major_code)
);
--INSERT INTO MAJOR_REQUIRED_ELECTIVE(major_code, course_level, course_amount, group_id) VALUES ('COMPA1', 3, 5, 0);
--INSERT INTO MAJOR_REQUIRED_ELECTIVE(major_code, course_level, course_amount, group_id) VALUES ('COMPA1', 4, 5, 0);
--INSERT INTO MAJOR_REQUIRED_ELECTIVE(major_code, course_level, course_amount, group_id) VALUES ('COMPA1', 6, 5, 0);
--INSERT INTO MAJOR_REQUIRED_ELECTIVE(major_code, course_level, course_amount, group_id) VALUES ('COMPA1', 9, 5, 0);

--this table address the scenario where the user has to completed part of a group of specified course. E.G: in COMPA1 students have to complete 3 out of 4 given electives
CREATE TABLE MAJOR_REQUIRED_ELECTIVE_SPECIFIC
(
	major_code TEXT,
	course_code TEXT, --specific courses code 
	course_amount INTEGER, --the amount of courses which is part of a given course list that needs to be taken
	group_id INTEGER, --interchangable courses will have the same group id
	PRIMARY KEY(major_code, course_code, group_id),
	FOREIGN KEY(major_code) REFERENCES MAJOR(major_code)
);
--INSERT INTO MAJOR_REQUIRED_ELECTIVE_SPECIFIC(major_code, course_code, course_amount, group_id) VALUES ('COMPA1', 'MATH1131', 3, 0);


--table "EXCLUDE" reflects scenario like MATH1131 + MATH1231 can replace MATH1141 + MATH1241
--"replaced_course" is the course being replaced, if MATH1131 can replace MATH1141, then course_code is MATH1131 and replaced_course is MATH1141
--reason to include program code and year is based on the assumption that the one course can replace different courses in different programs
--group_id addresses the issue of multiple courses replacement
CREATE TABLE EXCLUDE
(
	course_code TEXT,
	program_code INTEGER,
	commence_year INTEGER,
	replaced_course TEXT,
	group_id INTEGER,
	PRIMARY KEY(program_code, commence_year, course_code, replaced_course, group_id),
	FOREIGN KEY(program_code, commence_year) REFERENCES PROGRAM(program_code, commence_year),
	FOREIGN KEY(course_code) REFERENCES COURSE(course_code),
	FOREIGN KEY(replaced_course) REFERENCES COURSE(course_code)
);
--INSERT INTO EXCLUDE (course_code, program_code, commence_year, replaced_course, group_id) VALUES ('MATH1131', 'COMP3978',2016, 'MATH1141', 1);

--table "PREREQUISITE" reflects scenario like MATH1131 is prerequisite for 
--"prerequisite_course" is the course that needs to be taken before the course refered in "course_code", if MATH1131 is prerequisite for MATH1231, then course_code is MATH1231 and prerequisite_course is MATH1131
--group_id addresses the issue of Prerequisite: COMP1917 or (COMP1911 + COMP1531)
CREATE TABLE PREREQUISITE
(
	course_code TEXT,
	program_code INTEGER,
	commence_year INTEGER,
	prerequisite_course TEXT,
	group_id INTEGER,
	PRIMARY KEY(program_code, commence_year, course_code, prerequisite_course, group_id),
	FOREIGN KEY(program_code, commence_year) REFERENCES PROGRAM(program_code, commence_year),
	FOREIGN KEY(course_code) REFERENCES COURSE(course_code),
	FOREIGN KEY(prerequisite_course) REFERENCES COURSE(course_code)
);
--INSERT INTO PREREQUISITE (course_code, program_code, commence_year, prerequisite_course, group_id) VALUES ('MATH1131', 'COMP3978',2016, 'MATH1231',1);