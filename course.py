from helper_functions import *
import re
from core_course import *

# user input a course_code, get all course info. result[0] = course_code, result[1] = course_name, result[2] = t1(1 for offered 0 for not)
# result[3] = t2(1 for offered 0 for not), result[4] = t3(1 for offered 0 for not), result[5] = summer(1 for offered 0 for not)

def get_course_by_course_code(course_code):
	query = "SELECT * FROM COURSE WHERE course_code = ?"
	payload = (course_code,)
	results = dbselect(query, payload)
	results = results[0]
	return results
'''
## testing##############
for r in results:
	print(r)
'''
#take a list of course code and returns a list of coursescode + it name
def get_course_list_with_name(course_list):
	new_list = []
	#get all the remaining course code
	for course_code in course_list:
		c = get_course_by_course_code(course_code)
		new_list.append([c[0], c[1]])
	return new_list
'''
#test get_course_list_with_name
l = ['MATH1081', 'MATH1131']
print(get_course_list_with_name(l))
'''
#get offered semesters by cours_code
def get_offered_semesters(course_code):
	query = "SELECT t1, t2, t3 FROM COURSE WHERE course_code = ?"
	payload = (course_code,)
	results = dbselect(query, payload)
	results = results[0]
	return results
'''
#test get_offered_semester
semesters = get_offered_semesters('MATH1081')
print(semesters)
'''
#check if it is core, return true if the course if so , false otherwise
def is_core(program_code, commence_year, major_code, course_code):
	# TODO check if it's a program core - not relevant for COMPSCI

	# check if it's a major core
	query = "SELECT * FROM MAJOR_REQUIRED_COURSE WHERE major_code = ? and course_code = ?"
	payload = (major_code, course_code,)
	results = dbselect(query, payload)
	# if any result was returned, it's a core. Otherwise it's not
	if len(results) > 0:
		return True

	return False

#check if it is elective, return true if the course is elective, false otherwise
def is_elective(program_code, commence_year, major_code, course_code):
	# TODO check if it's a specific elective

	# check if it's a level elective
	match = re.search(r'([A-Z]{4})(\d{4})', course_code)
	course_prefix = match.group(1)
	level = int(match.group(2)[0])

	# make simplifying assumption that if prefix of course code and major
	# code are the same, we can ignore prefix field in db
	major_prefix = re.search(r'([A-Z]{4})', major_code).group(1)
	if major_prefix != course_prefix:
		return False

	query = "SELECT * FROM MAJOR_REQUIRED_ELECTIVE WHERE major_code = ?"
	payload = (major_code,)
	results = dbselect(query, payload)
	# check there is some uoc for this level
	for result in results:
		if result[2] == level:
			return True

	return False

#check if it is general eudcation, return true if the course is a general eductaion, false otherwise
def is_gene(commence_year, course_code):
	query = "SELECT * FROM COURSE WHERE course_code = ?"
	payload = (course_code,)
	results = dbselect(query, payload)
	if len(results) == 0:
		# invalid course
		return False

	# no loop needed as only one entry per course
	if results[0][-1] == 1:
		return True
	return False

#get pre-requisite of 
def get_pre_requisite (course_code):
	query = "SELECT prerequisite_course, group_id FROM PREREQUISITE WHERE course_code = ?"
	payload = (course_code,)
	results = dbselect(query, payload)
	#if course does not have prerequisites, return False
	if len(results) == 0:
		return False
	return results

#key function for sort_course, gets the postfix of a coruse_code
def sort_method(course_code):
	return int(re.search(r'[A-Z]{4}(\d{4})', course_code).group(1))
#sort a list of course code based on their post fix number e.g. MATH1101 come before COMP1200
def sort_courses(remaining_core_courses):
	return sorted(remaining_core_courses, key = sort_method)

#take exclusion into consideration, e.g if 1131 is taken, 1231 is taken
def excluded(course_code, selected_courses_code):
	for exluded_course in selected_courses_code:
		query = "SELECT * FROM EXCLUDE WHERE course_code = ? and replaced_course =?"
		payload = (course_code,exluded_course)
		results = dbselect(query, payload)
		if results:
			return True
	return False
'''
#test excluded
print(excluded('MATH1131', ['MATH1141', 'COMP1531']))
print(excluded('MATH1131', ['COMP1531', 'COMP1531']))
'''
def get_excluded_course(course_code):
	excluded_courses = []
	query = "SELECT * FROM EXCLUDE WHERE course_code = ?"
	payload = (course_code,)
	results = dbselect(query, payload)
	for result in results:
		excluded_courses.append(result[3])
	return excluded_courses
'''
#test get_excluded_course
print(get_excluded_course('MATH1131'))
'''
#pass, program_code, commence_year and courses_have_done(course_code) to return a list of core_courses that should be dont later
def get_remaining_cores(program_code, commence_year, major_code, courses_have_done):
	all_cores = get_core_courses(major_code, commence_year)
	#sort and reverse all the cores to imply take MATH1131 rather than MATH1141(low level)
	all_cores = sort_courses(all_cores)
	all_cores.reverse()
	#handles if MATH1131 is taken, then MATH1141 should not be in the remaining core 
	for course_code in courses_have_done:
		if(excluded(course_code, all_cores)):
			excluded_courses = get_excluded_course(course_code)
			for c in excluded_courses:
				try:
					all_cores.remove(c)
				except ValueError:
					pass
	#handles if MATH1131 is taken, then MATH1241 should not be in the remaining core 
	for course_code in all_cores:
		if(excluded(course_code, all_cores)):
			all_cores.remove(course_code)
	return list(set(all_cores) - set(courses_have_done))
	 
'''
#test get remaining cores
print(sort_courses(get_remaining_cores(3778,2019,'COMPA1',[])))
print(sort_courses(get_remaining_cores(3778,2019,'COMPA1',['MATH1131','MATH1141'])))
print(sort_courses(get_remaining_cores(3778,2019,'COMPA1',['MATH1131'])))
'''
#check if the course is valid course
def is_valid_course(course_code):
	#make the first 4 characters uppercase
	course_code =  course_code.upper()
	query = "SELECT * FROM COURSE WHERE course_code = ?"
	payload = (course_code,)
	results = dbselect(query, payload)
	if results:
		return True
	return False
'''
#test is_valid_course
print(is_valid_course('coMP1511'))
print(is_valid_course('COMP511'))
'''
