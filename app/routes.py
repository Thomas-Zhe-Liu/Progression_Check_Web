from app import app
from flask import Flask, redirect, render_template, request, url_for
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

@app.route('/step2/<program_code>/<commence_year>/<major>', methods=["GET", "POST"])
def step2(program_code, commence_year, major):
	print(program_code + " " + str(commence_year) + " " + major)
	return render_template('step2.html', program_code = program_code, commence_year = commence_year, major = major)

@app.route('/step3')
def step3():
	return render_template('step3.html')

# @app.route("/step2/<program_code>/<commence_year>/<major>", methods=["GET", "POST"])
# def step2(program_code, commence_year, major):
# 	return render_template('step2.html', program_code = program_code, commence_year = commence_year, major = major)