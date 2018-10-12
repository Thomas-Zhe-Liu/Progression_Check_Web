import requests
from bs4 import BeautifulSoup
import re
import sqlite3
import sys

# global url info I'll use
hb_base = "https://www.handbook.unsw.edu.au"
hb_program_base = hb_base + "/undergraduate/programs/2019/"
hb_code_base = hb_base + "undergraduate/courses/2019/"
program_codes = requests.get("http://www.gettingstarted.unsw.edu.au/uac-codes-and-corresponding-unsw-undergraduate-program-codes");
code_soup = BeautifulSoup(program_codes.content, 'html.parser')

# regex patterns I use frequenetly
coderx = r'[A-Z]{4}\d{4}'
coderx_g = r'([A-Z]{4}\d{4})'

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

class Program:
    def __init__(self, prog_code, prog_name, commence_yr, flex_uoc, gen_uoc, free_elective_uoc, majors, core_courses):
        self.code = prog_code
        self.name = prog_name
        self.year = commence_yr
        self.flex = flex_uoc
        self.gen_uoc = gen_uoc
        self.free_elective_uoc = free_elective_uoc
        # list of major codes
        self.majors = majors
        # list of core codes
        self.cores = core_courses

class Major:
    def __init__(self, major_code, major_name, lv3, lv2, lv1, core_courses, prog_code, level_electives, specific_electives):
        self.code = major_code
        self.name = major_name
        self.lv3 = lv3
        self.lv2 = lv2
        self.lv1 = lv1
        # list of course codes
        self.cores = core_courses
        self.prog = prog_code
        # electives
        self.specific_electives = specific_electives
        self.level_electives = level_electives

class Course:
    def __init__(self, course_code, course_name, t1, t2, t3, summer, prereqs, exclusions, flex, gened):
        self.code = course_code
        self.name = course_name
        self.t1 = t1
        self.t2 = t2
        self.t3 = t3
        self.summer = summer
        self.prereqs = prereqs
        self.flex = flex
        self.exclusions = exclusions
        self.gened = gened

def get_core_links(card):
    ret_list = []

    # some programs don't list cores - just have info e.g. last box of prog 3475
    if card is None:
        return ret_list

    # check if they're conditional core courses i.e. specific to a 
    # major but for some reason on the program site- e.g. program 3475
    course_info = card.find("div", class_="m-accordion-header")
    not_mandatory = course_info.find("p", text=re.compile(r'^If you select'))
    if not_mandatory is not None:
        print("Cores are not mandatory - they're conditional on major")
        return ret_list

    course_lists = card.find_all("div", {"data-hbui" : "course-list"})
    for course_list in course_lists:
        for course in course_list.find_all("div", recursive=False):
            ret_list.append(hb_base + course.find("a")['href'].strip())

    return ret_list

def get_major_links(card):
    ret_list = []
    # some programs don't list any content - e.g. heading 'Double major' in Commerce
    if card is None:
        return ret_list

    # need to find the 'course list' that actually has data - some are empty
    major_lists = card.find_all("div", {"data-hbui" : "course-list"})
    for major_list in major_lists:
        for major in major_list.find_all("div", recursive=False):
            if re.search(r'minor', major['data-hbui-filter-item'], re.I) is not None:
                # sometimes they list minors which is dumb
                continue

            ret_list.append(hb_base + major.find("a")['href'].strip())

    return ret_list

def get_flex_links(card, program):
    ret_list = []
    # get number of courses that must be taken in the list
    course_info = card.find("div", class_="m-accordion-header")
    uoc_p = course_info.find("p", text=re.compile(r'^Students'))
    num_uoc = re.search(r'(\d{1,2}) UOC', uoc_p.text).group(1)
    # update program's flex requirements
    program.flex = num_uoc

    course_list = card.find("div", {"data-hbui" : "course-list"}).find_all("div", recursive=False)
    for course in course_list:
        ret_list.append(hb_base + course.find("a")['href'].strip())

    return ret_list

def get_course_code(link):
    match = re.search(coderx_g, link)
    if match is not None:
        return match.group(1)
    else:
        return ""

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
        print(major_code)
        major_name = major_soup.find("span", {"data-hbui" : "module-title"}).text
        major_cores = []
        specific_electives = []
        level_electives = []
        headers = major_soup.find_all("div", {"class" : "m-accordion-group-header"})
        groupid = -1
        for header in headers:
            # core course header
            card = header.find_next_sibling("div")
            if re.search(r'Core Courses?', header.text.strip()):
                core_links = get_core_links(card)
                major_cores = major_cores + get_courses(core_links, False)

            elif re.search(r'Free Electives?', header.text.strip(), re.I):
                print("Free elective header")

            # elective header
            elif re.search(r'Electives?', header.text.strip()):
                # use this list as a store of codes used to avoid duplicates e.g. COMPN1
                specific_codes = []
                groupid = groupid + 1
                # get number of uoc of this elective list we need to complete
                elective_uoc = get_header_uoc(card)
                # check if these electives are grouped e.g. lv3 comp courses
                course_lists = card.find_all("div", {"data-hbui" : "course-list"})
                for course_list in course_lists:
                    for course in course_list.find_all("div", recursive=False):
                        # check if it's specific or level elective
                        if course.find("a").has_attr("aria-label"):
                            # specific
                            course_code = get_course_code(course.find("a")['href'])
                            if course_code in specific_codes:
                                continue

                            specific_electives.append([course_code, elective_uoc, groupid])
                            specific_codes.append(course_code)
                        else:
                            # level
                            #//TODO add code to the elective table e.g. https://www.handbook.unsw.edu.au/undergraduate/specialisations/2019/BINFAH
                            info = course.find("p", text=re.compile(r'^any'))
                            lv = re.search(r'level (\d+)', info.text).group(1)
                            level_electives.append([lv, elective_uoc, groupid])

        # there are cases where courses are double listed e.g. in "CEICDH", so make major_cores unique
        # same for specific electives e.g. COMPN1
        Majors[major_code] = Major(major_code, major_name, 0, 0, 0, list(set(major_cores)), prog_code, level_electives, specific_electives)

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
            course_code = course.find("span", text=re.compile(coderx))
            if course_code is not None:
                ret_list.append(course_code.text)

    # there are cases where courses are double listed e.g. in "ELEC1111", so make major_cores unique
    return list(set(ret_list))

def get_terms(soup):
    ret_list = [0, 0, 0, 0]
    terms = soup.find("div", class_="o-attributes-table").find_all("div", recursive=False)[3].find("p").text
    # assume csv
    terms = terms.split(",")
    for term in terms:
        term_num = re.search(r'(\d)', term)
        if term_num is None:
            # could be summer term
            if re.search(r'summer', term, re.I):
                ret_list[3] = 1
        else:
            ret_list[int(term_num.group(1))-1] = 1

    return ret_list

def is_gened(soup):
    if soup.find("p", text=re.compile(r'^This course is offered as General Education')):
        return True
    return False

def get_header_uoc(card):
    card_info = card.find("div", class_="m-accordion-header").find("p", text=re.compile(r'\d+ UOC'))
    if card_info is None:
        return 0
    else:
        uoc = re.search(r'(\d+) UOC', card_info.text).group(1)
        return int(uoc)

def to_braces(prerequisites):
    # check if there are commas
    if prerequisites.count(',') == 0:
        return prerequisites

    groups = prerequisites.split(',')
    # add starting brace
    for i in range(len(groups)):
        groups[i] = re.sub(coderx_g, r'(\1', groups[i], 1)
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
    # check if theyr're even using groups - if not just return
    if "(" not in prerequisites:
        return prerequisites
    
    # single code group not parenthesised at beginning of bool group
    prerequisites = re.sub(r'(%s)(\s*(?:and|or)\s*\()' % coderx, r'(\1)\2', prerequisites, flags=re.I)
    # single code group not parenthesised at end of bool group
    prerequisites = re.sub(r'(\)\s*(?:and|or)\s*)(%s)(?:\)|$)' % coderx, r'\1(\2)', prerequisites, flags=re.I)

    return prerequisites


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
        codes = re.findall(coderx, prerequisites)
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
                groups[i] = re.sub(coderx_g, r'(\1)', groups[i])

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
            for code in re.findall(coderx, group):
                and_group.append(code)
            prereqs.append(and_group)

    return prereqs

def get_courses(course_links, flex):
    '''
        Take in list of links to course pages
        Return list of course codes
        Append courses Courses list to be inserted into db
        if not already there
    '''

    ret_list = []
    for course_link in course_links:
        # check if this course is already in the courses dictionary
        course_code = get_course_code(course_link) 
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
                    excluded = re.findall(coderx, exclusion)

                prereqs = parse_prereqs(prerequisites)

        # check wasn't already filled above
        if not excluded:
            excluded = get_excluded(course_soup)

        # get terms offered
        terms = get_terms(course_soup)
        gened = is_gened(course_soup)
        Courses[course_code] = Course(course_code, course_name, terms[0], terms[1], terms[2], terms[3], prereqs, excluded, flex, gened)

    return ret_list

#testing = ['3778', '3707', '3502']
'''
    UNSW search isn't working from requests so to make sure we get all courses
    go through at the start the entire course list on the UNSW handbook and
    insert them into the db
'''
home_page = requests.get(hb_base)
home_soup = BeautifulSoup(home.content, 'html.parser')

'''
    Go through each program and insert the program, its majors and
    its electives into the db
'''
testing = ['3778']
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
        prog_name = prog_soup.find("span", {"data-hbui" : "module-title"}).text
        print("On handbook page for program code %s, name %s" % (prog_code, prog_name))

        # create new program object
        prog = Program(prog_code, prog_name, 2019, 0, 0, 0, [], [])

        # check if there are program wide core courses
        # assume all courses found here are mandatory for the program
        headers = prog_soup.find_all("div", {"class" : "m-accordion-group-header"})
        for header in headers:
            # flex core header
            if re.search(r'Flex', header.text.strip()):
                # pass program in so it can update the program 
                flex_links = get_flex_links(header.find_next_sibling("div"), prog)
                prog.cores = prog.cores + get_courses(flex_links, True)

            # core course header
            if re.search(r'Core Courses?', header.text.strip()):
                core_links = get_core_links(header.find_next_sibling("div"))
                prog.cores = prog.cores + get_courses(core_links, False)

            # major header
            elif re.search(r'Majors', header.text.strip()):
                major_links = get_major_links(header.find_next_sibling("div"))
                prog.majors = prog.majors + get_majors(major_links, prog_code)

            # gened header
            # use \s* coz header "General Education Maturity Req"
            elif re.search(r'General Education\s*$', header.text.strip()):
                prog.gen_uoc = get_header_uoc(header.find_next_sibling("div"))

            # free elective header
            elif re.search(r'Free Elective', header.text.strip()):
                prog.free_elective_uoc = get_header_uoc(header.find_next_sibling("div"))


        # queue this program to be inserted into db
        Programs[prog_code] = prog

        # debugging print's 
        print("program geneds uoc: %d" % prog.gen_uoc)
        print("program free electives uoc: %d" % prog.free_elective_uoc)
        
        for major in prog.majors:
            # get major object
            major_obj = Majors[major]
            print("Major code: %s" % major)
            print("Major name: %s" % major_obj.name)

            print("specific electives: ")
            print(major_obj.specific_electives)

            print("lv electives: ")
            print(major_obj.level_electives)

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
                if course_obj.gened:
                    print("It is a gened!!!")

# insert into db
for key in Programs:
    curr_prog = Programs[key]
    # insert program
    command = "INSERT INTO PROGRAM (program_code, commence_year, program_name, general_course, free_elective, flexi_core_course) VALUES (?,?,?,?,?,?)"
    payload = (int(curr_prog.code), curr_prog.year, curr_prog.name, curr_prog.gen_uoc, curr_prog.free_elective_uoc, curr_prog.flex)
    change_db(command, payload)
    # insert bridge to core courses
    #//TODO flex
    for core in curr_prog.cores:
        command = "INSERT INTO CORE_COURSE (course_code, program_code, commence_year, is_flexi) VALUES(?,?,?,?)"
        payload = (core, int(curr_prog.code), curr_prog.year, 0)
        change_db(command, payload)

for key in Majors:
    curr_major = Majors[key]
    command = "INSERT INTO MAJOR (major_code, major_name, lv1elective, lv2elective, lv3elective, program_code, commence_year) VALUES(?,?,?,?,?,?,?)"
    payload = (curr_major.code, curr_major.name, curr_major.lv1, curr_major.lv2, curr_major.lv3, int(curr_major.prog), '2019')
    change_db(command, payload)
    for core in curr_major.cores:
        command = "INSERT INTO MAJOR_REQUIRED_COURSE(major_code, course_code) VALUES (?,?)" 
        payload = (curr_major.code, core)
        change_db(command, payload)
    for elective in curr_major.level_electives:
        command = "INSERT INTO MAJOR_REQUIRED_ELECTIVE(major_code, course_level, course_amount, group_id) VALUES (?,?,?,?)"
        payload = (curr_major.code, elective[0], elective[1], elective[2])
        #print("command: %s, code: %s, level: %s, amount: %s, id: %s\n" % (command, curr_major.code, elective[0], elective[1], elective[2]))
        change_db(command, payload)
    for elective in curr_major.specific_electives:
        command = "INSERT INTO MAJOR_REQUIRED_ELECTIVE_SPECIFIC(major_code, course_code, course_amount, group_id) VALUES (?,?,?,?)"
        payload = (curr_major.code, elective[0], elective[1], elective[2])
        #print("command: %s, major code: %s, course code: %s, amount: %s, id: %s\n" % (command, curr_major.code, elective[0], elective[1], elective[2]))
        change_db(command, payload)

for key in Courses:
    curr_course = Courses[key]
    command = "INSERT INTO COURSE (course_code, course_name, t1, t2, t3, summer, is_gen) VALUES(?,?,?,?,?,?,?)"
    payload = (curr_course.code, curr_course.name, curr_course.t1, curr_course.t2, curr_course.t3, curr_course.summer, curr_course.gened)
    change_db(command, payload)
    for excluded in curr_course.exclusions:
        command = "INSERT INTO EXCLUDE (course_code, program_code, commence_year, replaced_course, group_id) VALUES(?,?,?,?,?)"
        payload = (curr_course.code, 0, '2019', excluded, 0)
        #print("command: %s, code: %s, excluded:  %s\n" % (command, curr_course.code, excluded))
        change_db(command, payload)
    i = 0
    for prereq_group in curr_course.prereqs:
        #//TODO this in here because of COMP3331
        prereq_group = list(set(prereq_group))
        for prereq in prereq_group:
            command = "INSERT INTO PREREQUISITE (course_code, program_code, commence_year, prerequisite_course, group_id) VALUES(?,?,?,?,?)"
            payload = (curr_course.code, 0, '2019', prereq, i)
            change_db(command, payload)
        i = i + 1
