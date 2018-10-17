from course import *
def plan_core_course(remaining_core_courses, starting_semester):
	schedule = [[],[],[],[],[],[],[],[],[]]
	for course_code in remaining_core_courses:
		#print("curr course: " + course_code)
		offered_semesters = get_offered_semesters(course_code)
		#1 means offerd, 0 vice versa
		schedule_count = -1
		while True:
			schedule_count += 1
			# check course is offered and there's room in your schedule
			if not offered_semesters[schedule_count%3] or len(schedule[schedule_count]) >= 3:
				continue

			# schedule the course
			schedule[schedule_count].append(course_code)
			break
	return schedule

courses = get_core_courses('COMPA1', 2019)
sorted_courses = sort_courses(courses)
schedule = plan_core_course(sorted_courses, 1)
print(schedule)


	#return [['COMP1911'], ['COMP1921', 'COMP2511'], ['COMP1911']]