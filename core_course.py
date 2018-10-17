from helper_functions import *
from course import *

#get_core_course based on major_code and commence_year
#this function assumes that major_code is unique- no 2 major has the sam emajor code, commence year not used for this function right now
def get_core_courses(major_code, commence_year):
	query = "SELECT course_code FROM MAJOR_REQUIRED_COURSE WHERE major_code = ?"
	payload = (major_code,)
	results = dbselect(query, payload)
	#results now is ("COMP1511",) need to filter
	f_results = []
	for r in results:
		f_results.append(r[0])
	return f_results

#pass, program_code, commence_year and courses_have_done(course_code) to return a list of core_courses that should be dont later
def get_remaining_cores(program_code, commence_year, major_code, courses_have_done):
	return set(get_core_courses(major_code, commence_year)) - set(courses_have_done)

'''
##MATH1131, MATH1231, COMP1917 in db for program 3978, 2016, expected outcome is MATH1231
results = cse_get_remaining_cores('COMP3778', 2019, 'COMPA1', ['COMP1911', 'COMP1531'])
for r in results:
	print("hello" + r)
'''

# Test cse_get_remaining_courses
to_complete = ['COMP1511']
expected_to_complete = ['COMP1521', 'COMP1531', 'COMP2511', 'COMP2521', 'COMP3121', 'COMP3900', 'COMP4920', 'MATH1081', 'MATH1131', 'MATH1141',
						 'MATH1231', 'MATH1241']
assert(set(get_remaining_cores('', '', 'COMPA1', to_complete)) == set(expected_to_complete))
expected_to_complete.remove('MATH1241')
to_complete.append('MATH1241')
assert(set(get_remaining_cores('', '', 'COMPA1', to_complete)) == set(expected_to_complete))
