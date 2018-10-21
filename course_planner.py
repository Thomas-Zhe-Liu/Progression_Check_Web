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
