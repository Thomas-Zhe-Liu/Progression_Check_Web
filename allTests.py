import sys
sys.path.append("..") # Adds higher directory to python modules path.
from course import *
from major import *
from program import *
from course_planner import *

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
assert(res[0][1] == "Discrete Mathematics")
assert(res[1][1] == "Mathematics 1A")

#test get_offered_semester
semesters = get_offered_semesters('MATH1081')
assert(semesters[0] == True)
assert(semesters[1] == True)
assert(semesters[2] == True)

################
# Test course.py
################

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
courses = get_core_courses('COMPA1', 2019)
print("before: ", courses)
sorted_courses = sort_courses(courses)
print("after: ", sorted_courses)



#Test get_pre_requisite
r = get_pre_requisite('COMP2511')
print(r)
r = get_pre_requisite('COMP1511')
print(r)



##testing#####
results = get_all_major_info(3778, 2019)
for r in results:
	print(r)



#######testing######
results = get_majors_of_a_program(3778, 2019)
for r in results:
	print(r)



#test excluded
print(excluded('MATH1131', ['MATH1141', 'COMP1531']))
print(excluded('MATH1131', ['COMP1531', 'COMP1531']))


#test get_excluded_course
print(get_excluded_course('MATH1131'))



#test get remaining cores
print(sort_courses(get_remaining_cores(3778,2019,'COMPA1',[])))
print(sort_courses(get_remaining_cores(3778,2019,'COMPA1',['MATH1131','MATH1141'])))
print(sort_courses(get_remaining_cores(3778,2019,'COMPA1',['MATH1131'])))



#test is_valid_course
print(is_valid_course('comp1531'))
print(is_valid_course('COMP511'))


#test for next_planner_year
print(next_planner_year(2019, 2))
print(next_planner_year(2019, 3))

#test for next_planner_semester
print(next_planner_semester(1))
print(next_planner_semester(3))


#test plan_courses for core courses
schedule = [[],[],[],[],[],[],[],[],[]]
courses = get_core_courses('COMPA1', 2019)
sorted_courses = sort_courses(courses)
schedule = plan_courses(schedule,sorted_courses, 2)
print("schedule bfore core courses: ",schedule)

#test plan_courses for major required specific courses
specific_elective_groups = get_specific_elective_groups(2019, 'COMPD1')
specific_electives = determine_specific_electives(specific_elective_groups)
print("specfic electives:" , specific_electives)
schedule = plan_courses(schedule, specific_electives,2)
print("schedule fore specific elective: ",schedule)
#test for clean planner 
print("cleaned planner: ",clean_planner(schedule))


#test fit_schedule_with_name
schedule_with_name = [[['MATH1081', 'Discrete Mathematics'], ['MATH1131', 'Mathematics 1A'], ['MATH1231', 'Mathematics 1B']], [['COMP1511', 'Programming Fundamentals'], ['COMP1521', 'Computer Systems Fundamentals'], ['COMP2511', 'Object-Oriented Design & Programming']], [['COMP1531', 'Software Engineering Fundamentals'], ['COMP2521', 'Data Structures and Algorithms'], ['COMP3311', 'Database Systems']], [['COMP3121', 'Algorithms and Programming Techniques'], ['COMP3900', 'Computer Science Project']], [['COMP9313', 'Big Data Management'], ['COMP9315', 'Database Systems Implementation']], [['COMP4920', 'Management and Ethics'], ['COMP6714', 'Information Retrieval and Web Search']], [], [], []]
schedule_with_name = fit_schedule_with_name(schedule_with_name, 18, 12, 12)
for semetser in schedule_with_name:
	print(semetser)

