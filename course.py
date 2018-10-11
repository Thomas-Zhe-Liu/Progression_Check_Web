from helper_functions import *
import re

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

# Test is_core
assert(is_core('1111', '2019', 'COMPA1', 'COMP3331') == False)
assert (is_core('1111', '2019', 'COMPA1', 'COMP1511') == True)

# Test is_elective
assert(is_elective('3778', '2019', 'COMPA1', 'COMP3331') == True)
assert(is_elective('3778', '2019', 'COMPA1', 'COMP2331') == False)

# Test is_gene
assert(is_gene('2019', 'COMP2511') == True)
assert(is_gene('2019', 'COMP3131') == False)