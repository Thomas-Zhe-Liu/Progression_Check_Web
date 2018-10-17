from helper_functions import *
from course import *



#get_core_course based on major_code and commence_year
#this function assumes that major_code is unique- no 2 major has the sam emajor code, commence year not used for this function right now
def cse_get_core_courses(major_code, commence_year):
	query = "SELECT course_code FROM MAJOR_REQUIRED_COURSE WHERE major_code = ?"
	payload = (major_code,)
	results = dbselect(query, payload)
	#results now is ("COMP1511",) need to filter
	f_results = []
	for r in results:
		f_results.append(r[0])
	return f_results


'''
## test: result should return a all the core_courses in COMP3978
results = cse_get_core_courses('COMPA1', 2016)
for r in results:
	print(r)

'''
#pass, program_code, commence_year and courses_have_done(course_code) to return a list of core_courses that should be dont later
def cse_get_remaining_cores(program_code, commence_year, major_code, courses_have_done):
	all_courses = cse_get_core_courses(major_code, commence_year)
	#make a copy of the list and delete the ones that have be done
	#what if I input a random course, error handling
	remaining_courses = list(all_courses)
	for course in all_courses:
		#need error checking...
		if(course in courses_have_done):
			#print("the course " + course[0] + " is done")
			remaining_courses.remove(course)

	return remaining_courses

'''
##MATH1131, MATH1231, COMP1917 in db for program 3978, 2016, expected outcome is MATH1231
results = cse_get_remaining_cores('COMP3778', 2019, 'COMPA1', ['COMP1911', 'COMP1531'])
for r in results:
	print("hello" + r)
'''


