from helper_functions import *



#get_core_course based on program_code and commence_year
def get_core_courses(program_code, commence_year):
	query = "SELECT * FROM CORE_COURSE WHERE program_code = ? AND commence_year = ?"
	payload = (program_code, commence_year)
	results = dbselect(query, payload)
	return results


'''	
## test: result should return a all the core_courses in COMP3978
results = get_core_courses('COMP3978', 2016)
for r in results:
	print(r)
'''

#pass, program_code, commence_year and courses_have_done to return a list of core_courses that should be dont later
def get_remaining_cores(program_code, commence_year, courses_have_done):
	all_courses = get_core_courses(program_code, commence_year)
	#make a copy of the list and delete teh ones that have be done
	remaining_courses = list(all_courses)
	for course in all_courses:
		#need error checking...
		if(course[0] in courses_have_done):
			#print("the course " + course[0] + " is done")
			remaining_courses.remove(course)

	return remaining_courses

'''
##MATH1131, MATH1231, COMP1917 in db for program 3978, 2016, expected outcome is MATH1231
results = get_remaining_cores('COMP3978', 2016, ['MATH1131', 'COMP1917'])
for r in results:
	print(r)
'''

