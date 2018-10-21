
from app import app
from flask import Flask, redirect, render_template, request, url_for, flash
from course import *
from core_course import *
from program import *
from major import *
from course_planner import *
#import weasyprint
#from app.forms import RegisterForm
from app.models import Users
from app.forms import RegisterForm, LoginForm
from flask_login import current_user, logout_user, login_user, login_required, login_manager
#this list will be used throughout the process
selected_courses_code = []
#this list is for step 2 to display the slected course only
selected_courses_code_name = []
#initilize 4 lists in accordance to let the courses being filtered be appended into a  list in step 3
finished_electives = []
finished_genes = []
finished_free_electives = []
finished_cores = []
finished_specific_electives = []

#@app.route("/", methods=["GET", "POST"])
@app.route('/')
def index():
	return render_template('index.html')


@app.route('/step1', methods=["GET", "POST"])
def step1():
	#user input program_code, commence_year and major code, get these data and redirect to step2.html
	if not current_user.is_authenticated:
		flash('You must be logged in to use this functionality')
		return redirect(url_for('login'))
	if request.method == "POST":
		#request.form["program"] return 3778 Computer Science, we need to get 3778
		program_code = request.form["program"].split()[0]
		commence_year = int(request.form["c_year"])
		#request.form["major"] return COMPA1 COMPUTER SCIENCE, we need to get COMPA1
		major = request.form["major"].split()[0]
		current_year = request.form["current_year"]
		current_sem = request.form["current_semester"].split()[1]
		return redirect(url_for("step2", program_code = program_code, commence_year = commence_year, major = major, current_year = current_year, current_sem = current_sem))
	all_programs = get_all_programs_code_name()
	#hard coded needs to replace later
	all_majors = get_majors_of_a_program(3778, 2019)
	return render_template('step1.html', all_programs = all_programs, all_majors = all_majors)



@app.route('/step2/<program_code>/<commence_year>/<major>/<current_year>/<current_sem>', methods=["GET", "POST"])
def step2(program_code, commence_year, major, current_year, current_sem):
	#initalize a empty error
	error = None
	if request.method == "POST":
#########################################step2 preperation##########################################################
		#this post request is for adding courses
		if request.form["submit"] == "add":
			#get program_code form request.form, make the first 4 characters uppercase
			course_code = request.form["p_code"].upper()
			if(not is_valid_course(course_code)):
				error = "Invalid Course, please re-enter the course code :)"
			#check if the same code has been input before already
			elif course_code not in selected_courses_code:
				selected_courses_code.append(course_code)
####################################################################################################################

#########################################step3 preperation##########################################################
		#this post request is to progress to step 3 after all the courses have done are input
		if request.form["submit"] == "Continue":
			return redirect(url_for("step3", program_code=program_code, commence_year=commence_year, major=major, current_year = current_year, current_sem = current_sem))
####################################################################################################################
	# selected_courses_code_name append code and course_name
	for code in selected_courses_code:
		course_name = get_course_by_course_code(code)[1]
		# check if the same tuple is alreday inserted, need to justify later
		if [code, course_name] not in selected_courses_code_name:
			selected_courses_code_name.append([code, course_name])
			
	return render_template('step2.html', program_code = program_code, commence_year = commence_year, major = major, selected_courses_code_name = selected_courses_code_name, error = error)


#the system filter out from selected_courses_code, get lists: remaining_core_all_info , finished_electives, finished_genes, finished_free_electives
@app.route('/step3/<program_code>/<commence_year>/<major>/<current_year>/<current_sem>', methods=["GET", "POST"])
def step3(program_code, commence_year, major, current_year, current_sem):
	
	#####################################CSE only###################################################################
	#cse is a bit special in terms of prgram structure, need to address this later
	#get all the uoc requirement of major_requried_electives, general education and free_electives: e.g. elective_uoc = 36
	elective_uoc = get_elective_uoc(commence_year,major)
	gene_uoc = get_gene_uoc(program_code, commence_year)
	free_uoc = get_free_uoc(program_code, commence_year)
	#specific_elective_UOC = get_specific_elective_UOC(commence_year, major_code)

	elective_groups = get_specific_elective_groups(commence_year, major)
	
	#iterate through each course_code in selected_course_code and determine whether this course is core, elective, general education or free elective
	for course_code in selected_courses_code:
		# it's a core and it is not excluded
		if(is_core(program_code, commence_year, major, course_code) and not excluded(course_code, finished_cores)):			
			if course_code not in finished_cores:				
				finished_cores.append(course_code)
			continue
		elif is_specific_elective(commence_year, course_code, elective_groups):
			# do nothing, above function will modify the UOC in the appropriate group
			if course_code not in finished_specific_electives:
				finished_specific_electives.append(course_code) 
			continue
		elif(is_elective(program_code, commence_year, major, course_code) and elective_uoc - 6 >= 0):
			if course_code not in finished_electives:
				elective_uoc -= 6
				finished_electives.append(course_code)
			continue
		elif(is_gene(commence_year, course_code) and gene_uoc - 6 >= 0):
			if course_code not in finished_genes:
				finished_genes.append(course_code)
				gene_uoc -= 6
			continue
		elif(free_uoc - 6 >= 0):
			if course_code not in finished_free_electives:
				finished_free_electives.append(course_code)
				free_uoc -= 6

	# get the specific elective UOC remaining
	specific_uoc = 0
	for group in elective_groups:
		specific_uoc += group.group_uoc

	#######################################step4#####################################
	if request.method == "POST":
		if request.form["submit"] == "Continue":
			return redirect(url_for("step4", program_code=program_code, commence_year=commence_year, major=major, current_year = current_year, current_sem = current_sem, elective_uoc = elective_uoc, free_uoc = free_uoc, gene_uoc = gene_uoc))
	#get all the remaining course code
	remaining_required_courses = get_remaining_cores(program_code, commence_year, major, selected_courses_code)
	# sort the remainin_required_course based on their list
	remaining_required_courses = sort_courses(remaining_required_courses)
	#################################################################################################################
	#pdf = weasyprint.HTML('http://localhost:5000/',program_code,'/',commence_year,'/',major).write_pdf('/tmp/example.pdf')
	#create a new list that has the name of a course to display
	remaining_core_all_info = get_course_list_with_name(remaining_required_courses)
	finished_specific_electives_all_info = get_course_list_with_name(finished_specific_electives)
	finished_electives_all_info = get_course_list_with_name(finished_electives)
	finished_genes_all_info = get_course_list_with_name(finished_genes)
	finished_free_electives_all_info = get_course_list_with_name(finished_free_electives)
	
	return render_template('step3.html', program_code = program_code, commence_year = commence_year, major = major, remaining_core_all_info = remaining_core_all_info, specific_uoc = specific_uoc, elective_uoc = elective_uoc, free_uoc = free_uoc, gene_uoc = gene_uoc, 
		finished_specific_electives_all_info = finished_specific_electives_all_info ,finished_electives_all_info = finished_electives_all_info, finished_genes_all_info = finished_genes_all_info, finished_free_electives_all_info = finished_free_electives_all_info)



@app.route('/step4/<program_code>/<commence_year>/<major>/<current_year>/<current_sem>/<elective_uoc>/<free_uoc>/<gene_uoc>', methods=["GET", "POST"])
def step4(program_code, commence_year, major, current_year, current_sem, elective_uoc, free_uoc, gene_uoc):
	#initalize a new scehdule 
	schedule = [[],[],[],[],[],[],[],[],[]]
	#sort the remaining course 
	remaining_required_courses = get_remaining_cores(program_code, commence_year, major, selected_courses_code)
	remaining_required_courses = sort_courses(remaining_required_courses)

	#get the year of next planner trismester
	plan_year = next_planner_year(current_year, current_sem)
	#get the semester of next planner trismester
	plan_sem = next_planner_semester(current_sem)
	#schedule based on remaining core course
	schedule = plan_courses(schedule,remaining_required_courses, plan_sem)
	#schedule based on major specific electives
	specific_elective_groups = get_specific_elective_groups(current_year, major)
	specific_electives = determine_specific_electives(specific_elective_groups)
	schedule = plan_courses(schedule, specific_electives,plan_sem)
	#cleans the lists in schedule before the first list with content
	schedule = clean_before_planner(schedule)
	#get names for all the courses
	schedule_with_name = []
	for semester in schedule:
		new_semester = get_course_list_with_name(semester)
		schedule_with_name.append(new_semester)
	#fit into all the uoc for electives, gene and free elctives
	schedule_with_name = fit_schedule_with_name(schedule_with_name, elective_uoc, gene_uoc, free_uoc)
	#now clean the whole schedule- delte all the list without contents
	schedule_with_name = clean_planner(schedule_with_name)
	return render_template('step4.html', program_code = program_code, commence_year = commence_year, major = major, plan_year = plan_year, plan_sem = plan_sem, schedule = schedule_with_name)

@app.route('/register', methods=['GET','POST'])
def register():
	form = RegisterForm()
	if form.validate_on_submit():
		#print('validated')
		#   flash('validated')
		conn = sqlite3.connect('Gradget.db')
		cursor = conn.cursor()
		cursor.execute("select * from USER where z_ID = ?", (form.zid.data,))

		#cursor.execute("select * from USER")

		user = cursor.fetchone()
		print(user)
		if user is None:
			print(form.password.data)
			cursor.execute("insert into USER values(?,?)", (form.zid.data, form.password.data))
			conn.commit()
			conn.close()
			flash('You have been successfully registered')
			return redirect(url_for("index"))
		flash('This user is already registered')

	return render_template('register.html', form=form)


@app.route('/login', methods=['GET','POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = Users(form.zid.data,form.password.data)
		if not user.is_authenticated():
		#if user is None:
			flash("Invalid credentials")
			return redirect(url_for('login'))

		login_user(user)
		print('logged in as ', user.z_id)
		print('current user is ', current_user.z_id)
		flash('You have been successfully logged in', current_user.z_id)

		return redirect(url_for('index'))
	return render_template('login.html', form=form)


@app.route('/logout', methods=['GET','POST'])
def logout():
	logout_user()
	flash('You have been successfully logged out')
	#clean all the list
	selected_courses_code = []
	selected_courses_code_name = []
	finished_electives = []
	finished_genes = []
	finished_free_electives = []
	finished_cores = []
	finished_specific_electives = []
	return redirect(url_for('index'))


