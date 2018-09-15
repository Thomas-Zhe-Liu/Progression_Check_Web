import requests
from bs4 import BeautifulSoup
import re
import sqlite3

# get all UNSW program codes from this UNSW website
hb_base = "https://www.handbook.unsw.edu.au"
hb_program_base = hb_base + "/undergraduate/programs/2019/"
hb_code_base = hb_base + "undergraduate/courses/2019/"
program_codes = requests.get("http://www.gettingstarted.unsw.edu.au/uac-codes-and-corresponding-unsw-undergraduate-program-codes");
code_soup = BeautifulSoup(program_codes.content, 'html.parser')

# list of programs to insert into db
Programs = {}
# list of majors to insert into db
Majors = {} 
# list of courses to insert into db
Courses = {}

def change_db(command, payload=None):
    """Execute command (with given payload, if any) in given database."""
    connection = sqlite3.connect('Gradget.db')
    cursor = connection.cursor()
    cursor.execute(command, payload)
    connection.commit()
    connection.close()

#//TODO define db insert functions for program class
class Program:
    def __init__(self, prog_code, prog_name, commence_yr, flex_uoc, majors, core_courses):
        self.code = prog_code
        self.name = prog_name
        self.year = commence_yr
        self.flex = flex_uoc
        # list of major codes
        self.majors = majors
        # list of core codes
        self.cores = core_courses

class Major:
    def __init__(self, major_code, major_name, lv3, lv2, lv1, core_courses, prog_code):
        self.code = major_code
        self.name = major_name
        self.lv3 = lv3
        self.lv2 = lv2
        self.lv1 = lv1
        # list of course codes
        self.cores = core_courses
        self.prog = prog_code

class Course:
    def __init__(self, course_code, course_name, t1, t2, t3, summer, prereqs, exclusions, flex):
        self.code = course_code
        self.name = course_name
        self.t1 = t1
        self.t2 = t2
        self.t3 = t3
        self.summer = summer
        self.prereqs = prereqs
        self.flex = flex
        self.exclusions = exclusions

def get_major_links(soup):
    ret_list = []
    headers = soup.find_all("h4", {"data-hbui" : "readmore__heading"}, text=re.compile("Majors"))
    for header in headers:
        content = header.find_next("div", class_="m-accordion")
        # some programs don't list any content - e.g. heading 'Double major' in Commerce
        if content is None:
            continue

        # need to find the 'course list' that actually has data - some are empty
        major_lists = content.find_all("div", {"data-hbui" : "course-list"})
        for major_list in major_lists:
            for major in major_list.find_all("div", recursive=False):
                if re.search(r'minor', major['data-hbui-filter-item'], re.I) is not None:
                    # sometimes they list minors which is dumb
                    continue

                ret_list.append(hb_base + major.find("a")['href'].strip())

    return ret_list

def get_majors(major_links, prog_code):
    '''
        Take in list of links to major pages
        Return list of major objects
    '''

    ret_list = []
    for major_link in major_links:
        # go to major page
        major_page = requests.get(major_link);
        major_soup = BeautifulSoup(major_page.content, 'html.parser')
        # check if major already in dictionary
        major_code = major_soup.find("strong", class_="code").text
        ret_list.append(major_code)
        if major_code in Majors:
            continue

        # get info
        major_name = major_soup.find("span", {"data-hbui" : "module-title"}).text
        major_core_links = get_core_links(major_soup)
        major_cores = get_courses(major_core_links, False)
        Majors[major_code] = Major(major_code, major_name, 0, 0, 0, major_cores, prog_code)

    return ret_list

def get_core_links(soup):
    ret_list = []
    core_course_headers = soup.find_all("h4", {"data-hbui" : "readmore__heading"}, text=re.compile(r'Core Courses?'))
    for header in core_course_headers:
        # Check if they're flexi cores - e.g. commerce
        if re.match(r'^Flex', header.text):
            continue

        print(header.text)
        core_courses = header.find_next("div", class_="m-accordion")
        # some programs don't list cores - just have info e.g. last box of prog 3475
        if core_courses is None:
            continue

        # check if they're conditional core courses i.e. specific to a 
        # major but for some reason on the program site- e.g. program 3475
        course_info = core_courses.find("div", class_="m-accordion-header")
        not_mandatory = course_info.find("p", text=re.compile(r'^If you select'))
        if not_mandatory is not None:
            print("Cores are not mandatory - they're conditional on major")
            continue

        course_lists = core_courses.find_all("div", {"data-hbui" : "course-list"})
        for course_list in course_lists:
            for course in course_list.find_all("div", recursive=False):
                ret_list.append(hb_base + course.find("a")['href'].strip())

    return ret_list

def get_excluded(soup):
    # assume course is already in db - just return list of course codes
    ret_list = []
    rules = soup.find("div", id="exclusion-rules")
    if rules is not None:
        course_list = rules.find("div", {"data-hbui" : "course-list"}).find_all("div", recursive=False)
        if course_list is None:
            return ret_list
        for course in course_list:
            course_code = course.find("span", text=re.compile(r'([A-Z]{4}\d{4})'))
            if course_code is not None:
                ret_list.append(course_code.text)

    return ret_list

def get_terms(soup):
    ret_list = [False, False, False, False]
    terms = soup.find("div", class_="o-attributes-table").find_all("div", recursive=False)[3].find("p").text
    # assume csv
    terms = terms.split(",")
    for term in terms:
        term_num = re.search(r'(\d)', term)
        if term_num is None:
            # could be summer term
            if re.search(r'summer', term, re.I):
                ret_list[3] = True
        else:
            ret_list[int(term_num.group(1))-1] = True

    return ret_list

def to_braces(prerequisites):
    # check if there are commas
    if prerequisites.count(',') == 0:
        return prerequisites

    groups = prerequisites.split(',')
    # add starting brace
    for i in range(len(groups)):
        groups[i] = re.sub(r'([A-Z]{4}\d{4})', r'(\1', groups[i], 1)
        if i == len(groups)-1:
            groups[i] = groups[i] + ')'
    # join on ending brace
    return ')'.join(groups)

def complete_groups(prerequisites):
    '''
        Fill in braces for single courses which aren't parenthesised
        e.g. "MARK1012 AND (MARK2051 OR MARK2151) AND MARK2052" becomes
        "(MARK1012) AND (MARK2051 OR MARK2151) AND (MARK2052)"
    '''
    # find link word
    link_word = ''
    if re.search(r'\)\s*and', prerequisites, re.I):
        # using or groups with and as link word
        link_word = "and"
    elif re.search(r'\)\s*or', prerequisites, re.I):
        # using and groups with or as link word
        link_word = "or"
    if link_word:
        # split on link word
        groups = re.split(link_word, prerequisites, flags=re.IGNORECASE)
        # parenthesise groups
        for i in range(len(groups)):
            groups[i] = groups[i].replace("(", "")
            groups[i] = groups[i].replace(")", "")
            groups[i] = groups[i].strip()
            groups[i] = '(' + groups[i] + ')'

        link_word = " " + link_word + " "
        ret_val = link_word.join(groups)
    else:
        ret_val = prerequisites

    return ret_val

def merge(str1, str2):
    ret_str = ''
    first_insert = True
    prereqs = []
    groups1 = str1.split(')')
    groups2 = str2.split(')')

    # match all groups in group1 with all groups in group2
    for group1 in groups1:
        # split sometimes returns empty strings
        if not group1:
            continue

        # remove leading and and or's
        group1 = re.sub(r'^[^\(]*', '', group1)

        for group2 in groups2:
            # split sometimes returns empty strings
            if not group2:
                continue

            # remove leading and and or's
            group2 = re.sub(r'^[^\(]*\(', '', group2)
            if (first_insert):
                ret_str = group1 + " and " + group2 + ')'
                first_insert = False
            else:
                ret_str = ret_str + ' or ' + group1 + ' and ' + group2 + ')'

    return ret_str

def parse_prereqs(prerequisites):
    '''
        Take the UNSW prereq string from handbook and return
        list of prereqs in form
        [[course1, course2],[course3], [course4]]
        where in list commas are AND, while out of list
        commas are OR
    '''
    
    prereqs = []
    # groups with braces
    prerequisites = to_braces(prerequisites)
    # sometimes single prereqs aren't fully parenthesised e.g. MARK3082
    prerequisites = complete_groups(prerequisites)
    # split into groups
    groups = prerequisites.split(')')
    # empty lists ruin things
    groups = list(filter(None, groups))

    if (len(groups) == 1):
        # no groups - just list like a and b and c
        codes = re.findall(r'[A-Z]{4}\d{4}', prerequisites)
        if (re.search(r'or', prerequisites)):
            # or list
            for code in codes:
                prereqs.append([code])
        else:
            # and list
            and_list = []
            for code in codes:
                and_list.append(code)
            prereqs.append(and_list)

    else:
        ''' groups could be 'or' groups or 'and' groups
        and groups can go straight into list, but or
        groups need to be manipulated to become and groups'''

        # group type determined by link word, which is first seen in group 2
        group_link = re.search(r'^\s*(\w+)', groups[1])
        if group_link is None:
            # irregular format e.g. MGMT2718
            return [[]]

        group_link = group_link.group(1)
        if re.match("and", group_link, re.I): 
            '''
            they're using or groups - this is tricky
            thank god I took discrete math to turn
            (A or B) AND C into 
            (A AND C) OR (B AND C)
            i.e. convert or groups to and groups
            '''
            # parenthesize properly for the merge
            for i in range(len(groups)):
                groups[i] = groups[i].replace("(", "")
                groups[i] = re.sub(r'([A-Z]{4}\d{4})', r'(\1)', groups[i])

            # merge 
            for i in range(len(groups)-1):
                new_group = merge(groups[0], groups[1])
                groups.pop(0)
                groups.pop(0)
                groups.insert(0, new_group)

            groups = groups[0].split(')')
            # empty lists ruin things
            groups = list(filter(None, groups))

        # using and groups - easy, can put straight into prereqs
        for group in groups:
            and_group = []
            for code in re.findall(r'[A-Z]{4}\d{4}', group):
                and_group.append(code)
            prereqs.append(and_group)
    
    return prereqs

def get_courses(course_links, flex):
    '''
        Take in list of links to coursre pages
        Return list of course codes
        Append courses Courses list to be inserted into db
        if not already there
    '''

    ret_list = []
    for course_link in course_links:
        # check if this course is already in the courses dictionary
        course_code = re.search(r'([A-Z]{4}\d{4})', course_link).group(1)
        ret_list.append(course_code)
        if course_code in Courses:
            # already have this course object in the dict
            continue

        # go to course page
        course_page = requests.get(course_link);
        course_soup = BeautifulSoup(course_page.content, 'html.parser')
        # get course info
        course_name = course_soup.find("span", {"data-hbui" : "module-title"}).text
        conditions = course_soup.find("div", id='SubjectConditions')
        prereqs = [[]]
        excluded = []
        if conditions is not None:
            prerequisites = conditions.find("div", text=re.compile(r'^Prerequisite:'))
            if prerequisites is not None:
                # sometimes excluded courses are also listed in same paragraph as prereqs
                # e.g. TABL2751
                prerequisites = prerequisites.text
                exclusion_match = re.search(r'(Excluded:.*$)', prerequisites)
                if exclusion_match is not None:
                    prerequisites = re.sub(r'Excluded:.*$','', prerequisites)
                    exclusion = exclusion_match.group(1)
                    # assume excluded courses are simple csv
                    excluded = re.findall(r'[A-Z]{4}\d{4}', exclusion)

                prereqs = parse_prereqs(prerequisites)

        # check wasn't already filled above
        if not excluded:
            excluded = get_excluded(course_soup)

        # get terms offered
        terms = get_terms(course_soup)
        #ret_list.append(Course(course_code, course_name, terms[0], terms[1], terms[2], terms[3], prereqs, excluded, flex))
        Courses[course_code] = Course(course_code, course_name, terms[0], terms[1], terms[2], terms[3], prereqs, excluded, flex)

    return ret_list

def get_flex_links(program):
    ret_list = []
    flex_headers = prog_soup.find_all("h4", {"data-hbui" : "readmore__heading"}, text=re.compile('^Flex'))
    for header in flex_headers:
        print(header.text)
        flex_courses = header.find_next("div", class_="m-accordion")
        # get number of courses that must be taken in the list
        course_info = flex_courses.find("div", class_="m-accordion-header")
        uoc_p = course_info.find("p", text=re.compile(r'^Students'))
        num_uoc = re.search(r'(\d{1,2}) UOC', uoc_p.text).group(1)
        # update program's flex requirements
        program.flex = num_uoc

        course_list = flex_courses.find("div", {"data-hbui" : "course-list"}).find_all("div", recursive=False)
        for course in course_list:
            ret_list.append(hb_base + course.find("a")['href'].strip())

    return ret_list

testing = [3778, 3707]
for table in code_soup.find_all("table"):

    # check the table's first column is "UAC Code"
    # Assume it's the correct table if it is
    check_table = table.find("tr").find("td");
    if check_table is None:
        continue;

    if not re.match(r'^UAC\s*Code\s*$', check_table.text):
        continue

    # Iterate through all program codes
    for row in table.find_all("tr"):
        prog_code = row.find_all("td")[1].text.strip().replace(" ", "")
        # check it's 4 digits
        if not re.match(r'\d{4}', prog_code):
            continue

        print(prog_code)

        # check we haven't already scraped this program
        if prog_code in Programs:
            continue

        #TODO remove here
        if prog_code not in testing:
            continue

        # go to program handbook site
        program = requests.get(hb_program_base + prog_code)
        prog_soup = BeautifulSoup(program.content, 'html.parser')
        # check if this is a valid program in the handbook (the codes may be outdated)
        title = prog_soup.find("title").text
        if (re.match(r'^Error', title)):
            print("Handbook page doesn't exist for program %s" % prog_code)
            continue

        # get program name
        prog_name = prog_soup.find("span", {"data-hbui" : "module-title"})
        print("On handbook page for program code %s, name %s" % (prog_code, prog_name.text))

        # create new program object
        prog = Program(prog_code, prog_name, 2019, 0, [], [])

        # check if there are program wide core courses
        # assume all courses found here are mandatory for the program
        core_links = get_core_links(prog_soup)
        prog.cores = get_courses(core_links, False)
        for core in prog.cores:
            print("Program core code: %s" % core)
            #print("Course prerequisites: %s" % ','.join(map(str, core.prereqs)))
        
        # check if there are flex courses e.g. commerce
        flex_links = get_flex_links(prog)
        flex = get_courses(flex_links, True)
        if flex:
            prog.cores = prog.cores + flex
            for f in flex:
                print("Flex code: %s" % f)

        # go to program majors to find program specific cores
        major_links = get_major_links(prog_soup)
        prog.majors = get_majors(major_links, prog_code)

        # queue this program to be inserted into db
        Programs[prog_code] = prog
        '''
        for major in prog.majors:
            # get major object
            major_obj = Majors[major]
            print("Major code: %s" % major)
            print("Major name: %s" % major_obj.name)
            print("Major cores: ")
            for core in major_obj.cores:
                # get the course object
                course_obj = Courses[core]
                print("Core code: %s" % core)
                print("Core name: %s" % course_obj.name)
                if not course_obj.prereqs:
                    print("No prereqs")
                    continue
                print("Core prerequisites:", end='')
                print(course_obj.prereqs)
                if not course_obj.exclusions:
                    print("No excluded courses")
                else:
                    print("Excluded courses", end='')
                    print(course_obj.exclusions)

                print("Offered in ", end='')
                if course_obj.t1:
                    print("t1 ", end='')
                if course_obj.t2:
                    print("t2 ", end='')
                if course_obj.t3:
                    print("t3 ", end='')
                if course_obj.summer:
                    print("summer ", end='')
                print()
        '''

# insert into db
for key in Programs:
    curr_prog = Programs[key]
    # insert program
    command = "INSERT INTO PROGRAM (program_code, commence_year, program_name, flexi_core_course) VALUES (?,?,?,?)"
    payload = [(curr_prog.code, curr_prog.year, curr_prog.name, curr_prog.flex)]
    change_db(command, payload)
    # insert bridge to core courses
    #//TODO flex
    for core in curr_prog.cores:
        command = "INSERT INTO CORE_COURSE (course_code, program_code, commence_year, is_flexi) VALUES (?,?,?,?)"
        payload = [(core, curr_prog.code, curr_prog.year, 0)]
        change_db(command, payload)

for key in Majors:
    curr_major = Majors[key]
    command = "INSERT INTO MAJOR (major_code, major_name, lv1elective, lv2elective, lv3elective, program_code, commence_year) VALUES(?,?,?,?,?,?,?)"
    payload = [(curr_major.code, curr_major.name, curr_major.lv1, curr_major.lv2, curr_major.lv3, curr_major.prog_code, '2019')]
    change_db(command, payload)
    for core in curr_major.cores:
        command = "INSERT INTO MAJOR_REQUIRED_COURSE(major_code, course_code) VALUES (?,?)" 
        payload = [(curr_major.code, core)]
        change_db(command, payload)

for course in Courses:
    command = "INSERT INTO COURSE (course_code, course_name, t1, t2, t3, summer) VALUES (?,?,?,?,?,?,?)"
    payload = [(course.code, course.name, course.t1, course.t2, course.t3, course.summer)]
    change_db(command, payload)
