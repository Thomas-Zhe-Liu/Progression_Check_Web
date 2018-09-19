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