from app import app
from flask import Flask, redirect, render_template, request, url_for

@app.route("/", methods=["GET", "POST"])
def index():
	if request.method == "POST":
		program_code = request.form["program_code"]
		#check if it is a integer, beeter be drop list
		commence_year = int(request.form["commence_year"])
		major = request.form["major"]
		#check if all the form is selected
		print("hello " + str(commence_year))
		return redirect(url_for("step2", program_code=program_code, commence_year=commence_year, major=major))
	return render_template('index.html')

@app.route("/step2/<program_code>/<commence_year>/<major>", methods=["GET", "POST"])
def step2(program_code, commence_year, major):
	return render_template('step2.html', program_code = program_code, commence_year = commence_year, major = major)