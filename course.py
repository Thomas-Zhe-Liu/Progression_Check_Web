from helper_functions import *

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