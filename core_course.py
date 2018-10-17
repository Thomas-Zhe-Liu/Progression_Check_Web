from helper_functions import *

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
