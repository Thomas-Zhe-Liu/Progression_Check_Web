from helper_functions import *

# get_all_program for each result in results results[0] = program_code, results[1] = commence_year
# results[2] = program_name, results[3] = flexi_core_course INTEGER, --how many core courses are flexible(exchangeable) course in this program
def get_all_programs_info():
	query = "SELECT * FROM PROGRAM"
	payload = ()
	results = dbselect(query, payload)
	return results

'''
#######testing######
results = get_all_programs_info()
for r in results:
	print(r)
'''

#get all the programs code and name program[0] = program_code, program[1] = program name
def get_all_programs_code_name():
	l = get_all_programs_info()
	results = []
	for i in l:
		results.append([i[0],i[2]])
	return results;

'''
#######testing######
results = get_all_programs_code_name()
for r in results:
	print(r)
'''