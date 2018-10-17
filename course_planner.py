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

#test plan_courses for core courses
schedule = [[],[],[],[],[],[],[],[],[]]
courses = get_core_courses('COMPA1', 2019)
sorted_courses = sort_courses(courses)
schedule = plan_courses(schedule,sorted_courses, 2)
print("schedule fore core courses: ",schedule)

#test plan_courses for major required specific courses
specific_elective_groups = get_specific_elective_groups(2019, 'COMPD1')
specific_electives = determine_specific_electives(specific_elective_groups)
print("specfic electives:" , specific_electives)
schedule = plan_courses(schedule, specific_electives,2)
print("schedule fore specific elective: ",schedule)

