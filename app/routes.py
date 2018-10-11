from app import app
from flask import Flask, redirect, render_template, request, url_for
from course import *
from core_course import *
from program import *
from major import *

#@app.route("/", methods=["GET", "POST"])
@app.route('/')
def index():
    return render_template('index.html')

# def index():
# 	if request.method == "POST":
# 		program_code = request.form["program_code"]
# 		#check if it is a integer, beeter be drop list
# 		commence_year = int(request.form["commence_year"])
# 		major = request.form["major"]
# 		#check if all the form is selected
# 		return redirect(url_for("step2", program_code=program_code, commence_year=commence_year, major=major))
# 	return render_template('index.html')

@app.route('/step1', methods=["GET", "POST"])
def step1():
	#user input program_code, commence_year and major code, get these data and redirect to step2.html
	if request.method == "POST":
		#request.form["program"] return 3778 Computer Science, we need to get 3778
		program_code = request.form["program"].split()[0]
		commence_year = int(request.form["c_year"])
		#request.form["major"] return COMPA1 COMPUTER SCIENCE, we need to get COMPA1
		major = request.form["major"].split()[0]
		return redirect(url_for("step2", program_code = program_code, commence_year = commence_year, major = major))
	all_programs = get_all_programs_code_name()
	#hard coded needs to replace later
	all_majors = get_majors_of_a_program(3778, 2019)
	return render_template('step1.html', all_programs = all_programs, all_majors = all_majors)



#need to justify having this 2 variable out here again later
selected_courses_code = []
selected_courses_code_name = []
@app.route('/step2/<program_code>/<commence_year>/<major>', methods=["GET", "POST"])
def step2(program_code, commence_year, major):
	if request.method == "POST":
#########################################step2 preperation##########################################################
		#this post request is for adding courses
		if request.form["submit"] == "add":
			#get program_code form request.form, need error handling
			program_code = request.form["p_code"]
			#check if the same code has been input before already
			if program_code not in selected_courses_code:
				selected_courses_code.append(program_code)
####################################################################################################################

#########################################step3 preperation##########################################################
		#this post request is to progress to step 3 after all the courses have done are input
		if request.form["submit"] == "continue":
			#list_separated = '-'.join(selected_courses_code)
			return redirect(url_for("step3", program_code=program_code, commence_year=commence_year, major=major))
####################################################################################################################
	# selected_courses_code_name append code and course_name
	for code in selected_courses_code:
		course_name = get_course_by_course_code(code)[1]
		# check if the same tuple is alreday inserted, need to justify later
		if [code, course_name] not in selected_courses_code_name:
			selected_courses_code_name.append([code, course_name])
			
	return render_template('step2.html', program_code = program_code, commence_year = commence_year, major = major, selected_courses_code_name = selected_courses_code_name)




@app.route('/step3/<program_code>/<commence_year>/<major>', methods=["GET", "POST"])
def step3(program_code, commence_year, major):
	
	#####################################CSE only###################################################################
	#get all the remainning core course
	#cse is a bit special in terms of prgram structure, need to address this later
	remaining_core_all_info = []
	if program_code == "3778":
		#get all the remaining course code
		remaining_required_courses = cse_get_remaining_cores(program_code, commence_year, major, selected_courses_code)
		#get all the remaining course code
		for course_code in remaining_required_courses:
			c = get_course_by_course_code(course_code)
			remaining_core_all_info.append(c)
	#################################################################################################################
		
				
	return render_template('step3.html', program_code = program_code, commence_year = commence_year, major = major, remaining_core_all_info = remaining_core_all_info)

# @app.route("/step2/<program_code>/<commence_year>/<major>", methods=["GET", "POST"])
# def step2(program_code, commence_year, major):
# 	return render_template('step2.html', program_code = program_code, commence_year = commence_year, major = major)