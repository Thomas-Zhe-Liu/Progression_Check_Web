from course import *
from major import *
def plan_courses(schedule,remaining_courses, starting_semester):
	#schedule is a list of semetsers that contains 3 courses maximum, 9 elements in total as the whole degree will be 3 years maximum
	for course_code in remaining_courses:
		#print("curr course: " + course_code)
		offered_semesters = get_offered_semesters(course_code)
		#1 means offerd, 0 vice versa
		schedule_count = starting_semester - 1
		while True:
			# check course is offered and there's room in your schedule
			if not offered_semesters[schedule_count%3] or len(schedule[schedule_count]) >= 3:
				schedule_count += 1
				continue

			# schedule the course
			schedule[schedule_count].append(course_code)
			schedule_count += 1
			break
	return schedule

#delete the empty lists before the first list with content
def clean_before_planner(schedule):
	for semetser in schedule:
		if semetser:
			return schedule[schedule.index(semetser):]
	return schedule

#delete the empty list in schedule
def clean_planner(schedule):
	new_schedule = [semetser for semetser in schedule if semetser != []]
	return new_schedule
'''
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
'''
def fit_schedule_with_name(schedule_with_name, elective_uoc, gene_uoc, free_uoc):
	elective_uoc = int(elective_uoc)
	gene_uoc = int(gene_uoc)
	free_uoc = int(free_uoc)
	for semetser in schedule_with_name:
		while(len(semetser) < 3 and (elective_uoc > 0 or gene_uoc > 0 or free_uoc > 0)):
			if (elective_uoc > 0):
				elective_uoc -= 6
				semetser.append(['COMPXXXX', 'COMP ELECTIVE'])
			elif(gene_uoc > 0):
				gene_uoc -= 6
				semetser.append(['GENEXXXX', 'GEBERAL EDUCATION'])
			elif(free_uoc > 0):
				free_uoc -= 6
				semetser.append(['FREEXXXX', 'FREE ELECTIVE'])
				
	return schedule_with_name
'''
#test fit_schedule_with_name
schedule_with_name = [[['MATH1081', 'Discrete Mathematics'], ['MATH1131', 'Mathematics 1A'], ['MATH1231', 'Mathematics 1B']], [['COMP1511', 'Programming Fundamentals'], ['COMP1521', 'Computer Systems Fundamentals'], ['COMP2511', 'Object-Oriented Design & Programming']], [['COMP1531', 'Software Engineering Fundamentals'], ['COMP2521', 'Data Structures and Algorithms'], ['COMP3311', 'Database Systems']], [['COMP3121', 'Algorithms and Programming Techniques'], ['COMP3900', 'Computer Science Project']], [['COMP9313', 'Big Data Management'], ['COMP9315', 'Database Systems Implementation']], [['COMP4920', 'Management and Ethics'], ['COMP6714', 'Information Retrieval and Web Search']], [], [], []]
schedule_with_name = fit_schedule_with_name(schedule_with_name, 18, 12, 12)
for semetser in schedule_with_name:
	print(semetser)
'''