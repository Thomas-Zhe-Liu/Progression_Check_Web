from helper_functions import *
from course import *


class elective_group():
	def __init__(self, group_uoc, group_course_list):
		self.group_uoc = group_uoc
		self.group_course_list = group_course_list

# get all major info based on program_code and commence year for each result in results results[0] = major_code, results[1] = major_name
# results[2] = how many lv1 electives, results[3] = how many lv2 electives,
#results[4] = how many lv3 electives, results[5] = program_code, results[6] = commence year
def get_all_major_info(program_code, commence_year):
	query = "SELECT * FROM MAJOR WHERE program_code = ? AND commence_year = ?"
	payload = (program_code,commence_year)
	results = dbselect(query, payload)
	return results


# get all the major code and name beased on program_code and commence_year, results[0] = major_code, results[1] = major_name
def get_majors_of_a_program(program_code, commence_year):
	l = get_all_major_info(program_code, commence_year)
	results = []
	for i in l:
		results.append([i[0],i[1]])
	return results;


#get the UOC of Major_Required_ELECTIVEs without consideration of what courses have been done, return e.g 36 for(6 courses)
def get_elective_uoc(commence_year, major_code):
	query = "SELECT * FROM MAJOR_REQUIRED_ELECTIVE WHERE major_code = ?"
	payload = (major_code,)
	results = dbselect(query, payload)

	# Right now, I'm just summing up the total elective uoc and not
	# differentiating on the basis of what level etc., & also not taking into
	# account the specific elective table
	group= -1
	uoc_sum = 0
	for result in results:
		curr_group = result[4]
		if curr_group != group:
			uoc_sum += result[3]
			group = curr_group

	return uoc_sum

'''
	Return an array of class elective group for each specific elective
	group listed on the major's handbook page
'''
def get_specific_elective_groups(commence_year, major_code):
	query = "SELECT course_code, course_amount, group_id UOC FROM MAJOR_REQUIRED_ELECTIVE_SPECIFIC WHERE major_code = ? ORDER BY group_id"
	payload = (major_code,)
	results = dbselect(query, payload)
	if len(results) == 0:
		return []

	elective_groups = []
	elective_list = []
	curr_group_id = 0
	curr_uoc = results[0][1]
	for result in results:
		if result[2] != curr_group_id:
			# new group
			elective_groups.append(elective_group(curr_uoc, elective_list))
			elective_list_list = []
			curr_uoc = result[1]
			curr_group_id += 1
		
		elective_list.append(result[0])

	return elective_groups

'''
	This function will check if the course is in an elective group
	If so, subtract course uoc from that elective group , and removed the course
'''
def is_specific_elective(commence_year, course, elective_groups):
	for group in elective_groups:
		if course in group.group_course_list and group.group_uoc > 0:
			group.group_uoc -= 6
			group.group_course_list.remove(course)
			return True

	return False

#returns what specific_electives needs to eb taken
def determine_specific_electives(elective_groups):
	electives = []
	for group in elective_groups:
		group.group_course_list = sort_courses(group.group_course_list)
		num_courses = group.group_uoc/6
		electives += group.group_course_list[:int(num_courses)]
	return electives



