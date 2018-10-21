import sys
sys.path.append("..") # Adds higher directory to python modules path.
import course
import major
import program
import core_course.py

################
# Test course.py
################

# Test is_core
assert(is_core('1111', '2019', 'COMPA1', 'COMP3331') == False)
assert (is_core('1111', '2019', 'COMPA1', 'COMP1511') == True)

# Test is_elective
assert(is_elective('3778', '2019', 'COMPA1', 'COMP3331') == True)
assert(is_elective('3778', '2019', 'COMPA1', 'COMP2331') == False)

# Test is_gene
assert(is_gene('2019', 'COMP2511') == True)
assert(is_gene('2019', 'COMP3131') == False)

#test get_course_list_with_name
l = ['MATH1081', 'MATH1131']
res = get_course_list_with_name(l)

assert(res[0] == "Discrete Mathematics")
assert(res[1] == "Mathematics 1A")

#test get_offered_semester
semesters = get_offered_semesters('MATH1081')
assert(semesters[0] == True)
assert(semesters[1] == True)
assert(semesters[2] == True)

################
# Test course.py
################

# Test cse_get_remaining_courses
to_complete = ['COMP1511']
expected_to_complete = ['COMP1521', 'COMP1531', 'COMP2511', 'COMP2521', 'COMP3121', 'COMP3900', 'COMP4920', 'MATH1081', 'MATH1131', 'MATH1141',
						 'MATH1231', 'MATH1241']
################
# Test major.py
################

assert(set(get_remaining_cores('', '', 'COMPA1', to_complete)) == set(expected_to_complete))
expected_to_complete.remove('MATH1241')
to_complete.append('MATH1241')
assert(set(get_remaining_cores('', '', 'COMPA1', to_complete)) == set(expected_to_complete))

# Test get_elective_uoc
assert(get_elective_uoc('2019', 'COMPA1') == 30)

# Test get_specific_electives_groups
assert(len(get_specific_elective_groups(2019, 'COMPA1')) == 0)
groups = get_specific_elective_groups(2019, 'COMPD1')
assert(len(groups) == 1)
assert(groups[0].group_uoc == 18)
expected_db_electives = ['COMP6714', 'COMP9313', 'COMP9315', 'COMP9318', 'COMP9319']
assert(set(expected_db_electives) == set(groups[0].group_course_list))

# Test is_specific_elective()
assert(is_specific_elective('2019', 'COMP6714', groups) == True)
assert(is_specific_elective('2019', 'COMP1511', groups) == False)

################
# Test program.py
################

# Test get_gene_uoc
assert(get_gene_uoc('3778', '2019') == 12)

# Test get_free_uoc
assert(get_free_uoc('3778', '2019') == 36)

################
# By eye tests
################

#Test sort_course
'''
courses = get_core_courses('COMPA1', 2019)
print("before: ", courses)
sorted_courses = sort_courses(courses)
print("after: ", sorted_courses)
'''


#Test get_pre_requisite
'''
r = get_pre_requisite('COMP2511')
print(r)
r = get_pre_requisite('COMP1511')
print(r)
'''

'''
##testing#####
results = get_all_major_info(3778, 2019)
for r in results:
	print(r)
'''

'''
#######testing######
results = get_majors_of_a_program(3778, 2019)
for r in results:
	print(r)
'''

'''
#test excluded
print(excluded('MATH1131', ['MATH1141', 'COMP1531']))
print(excluded('MATH1131', ['COMP1531', 'COMP1531']))
'''

'''
#test get_excluded_course
print(get_excluded_course('MATH1131'))
'''

'''
#test get remaining cores
print(sort_courses(get_remaining_cores(3778,2019,'COMPA1',[])))
print(sort_courses(get_remaining_cores(3778,2019,'COMPA1',['MATH1131','MATH1141'])))
print(sort_courses(get_remaining_cores(3778,2019,'COMPA1',['MATH1131'])))
'''

'''
#test is_valid_course
print(is_valid_course('comp1531'))
print(is_valid_course('COMP511'))
'''
