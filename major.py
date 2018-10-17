from helper_functions import *

# get all major info based on program_code and commence year for each result in results results[0] = major_code, results[1] = major_name
# results[2] = how many lv1 electives, results[3] = how many lv2 electives,
#results[4] = how many lv3 electives, results[5] = program_code, results[6] = commence year
def get_all_major_info(program_code, commence_year):
	query = "SELECT * FROM MAJOR WHERE program_code = ? AND commence_year = ?"
	payload = (program_code,commence_year)
	results = dbselect(query, payload)
	return results

'''
##testing#####
results = get_all_major_info(3778, 2019)
for r in results:
	print(r)
'''

# get all the major code and name beased on program_code and commence_year, results[0] = major_code, results[1] = major_name
def get_majors_of_a_program(program_code, commence_year):
	l = get_all_major_info(program_code, commence_year)
	results = []
	for i in l:
		results.append([i[0],i[1]])
	return results;

'''
#######testing######
results = get_majors_of_a_program(3778, 2019)
for r in results:
	print(r)
'''

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

def get_specific_electives(commence_year, major_code):
	query = "SELECT * FROM MAJOR_REQUIRED_ELECTIVE_SPECIFIC WHERE major_code = ?"
	payload = (major_code,)
	results = dbselect(query, payload)

	# return the array of required electives with groupid
	return results

# Test get_elective_uoc
assert(get_elective_uoc('2019', 'COMPA1') == 30)
# Test get_specific_electives
db_electives = get_specific_electives('2019', 'COMPA1')
assert(len(db_electives) == 0)
db_electives = get_specific_electives('2019', 'COMPD1')
expected_db_electives = ['COMP6714', 'COMP9313', 'COMP9315', 'COMP9318', 'COMP9319']
for elective in db_electives:
	expected_db_electives.remove(elective[1])

assert(len(expected_db_electives) == 0)