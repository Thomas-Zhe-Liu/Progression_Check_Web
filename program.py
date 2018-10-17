from helper_functions import *

# get_all_program for each result in results results[0] = program_code, results[1] = commence_year
# results[2] = program_name, results[3] = flexi_core_course INTEGER, --how many core courses are flexible(exchangeable) course in this program
def get_all_programs_info():
	query = "SELECT * FROM PROGRAM"
	payload = ()
	results = dbselect(query, payload)
	return results

def get_program(program_code):
	query = "SELECT * FROM PROGRAM WHERE program_code = ?"
	payload = (program_code,)
	results = dbselect(query, payload)
	if len(results) == 0:
		return None

	return results[0]
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

#get the UOC of general education course without consideration of what courses have been done, return e.g 36 for(6 courses)
def get_gene_uoc(program_code, commence_year):
	prog = get_program(program_code)
	if prog is None:
		# invalid prog code
		return 0

	return prog[3]

#get the UOC of free_elective without consideration of what courses have been done, return e.g 36 for(6 courses)
def get_free_uoc(program_code, commence_year):
	prog = get_program(program_code)
	if prog is None:
		# invalid prog code
		return 0
		
	return prog[4]
