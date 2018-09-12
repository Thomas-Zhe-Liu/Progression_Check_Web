import requests
from bs4 import BeautifulSoup
import re

# get all UNSW program codes from this UNSW website
hb_base = "https://www.handbook.unsw.edu.au"
hb_program_base = hb_base + "/undergraduate/programs/2019/"
program_codes = requests.get("http://www.gettingstarted.unsw.edu.au/uac-codes-and-corresponding-unsw-undergraduate-program-codes");
code_soup = BeautifulSoup(program_codes.content, 'html.parser')

#//TODO define db insert functions for these classes
class Course:
    def __init__(self, course_code, course_name, t1, t2, t3, prereqs, exclusions, flex):
        self.code = course_code
        self.name = course_name
        self.t1 = t1
        self.t2 = t2
        self.t3 = t3
        self.prereqs = prereqs
        self.flex = flex

class Program:
    def __init__(self, prog_code, prog_name, commence_yr, flex_uoc, core_courses):
        self.code = prog_code
        self.name = prog_name
        self.year = commence_yr
        self.flex = flex_uoc
        self.cores = core_courses

class Major:
    def __init__(self, major_code, major_name, lv3, lv2, lv1, core_courses):
        self.code = major_code
        self.name = major_name
        self.lv3 = lv3
        self.lv2 = lv2
        self.lv1 = lv1
        self.cores = core_courses

def get_major_links():
    ret_list = []
    headers = prog_soup.find_all("h4", {"data-hbui" : "readmore__heading"}, text=re.compile("Majors"))
    for header in headers:
        content = header.find_next("div", class_="m-accordion")
        # some programs don't list any content - e.g. heading 'Double major' in Commerce
        if content is None:
            return None

        # need to find the 'course list' that actually has data - some are empty
        major_lists = content.find_all("div", {"data-hbui" : "course-list"})
        for major_list in major_lists:
            for major in major_list.find_all("div", recursive=False):
                ret_list.append(hb_base + major.find("a")['href'].strip())

    return ret_list

def get_majors(major_links):
    '''
        Take in list of links to major pages
        Return list of major objects
    '''

    ret_list = []
    for major_link in major_links:
        # go to major page
        major_page = requests.get(major_link);
        major_soup = BeautifulSoup(major_page.content, 'html.parser')
        # get major info
        major_name = major_soup.find("span", {"data-hbui" : "module-title"}).text
        major_code = major_soup.find("strong", class_="code").text
        major_core_links = get_core_links(major_soup)
        major_cores = get_courses(major_core_links, False)
        ret_list.append(Major(major_code, major_name, 0, 0, 0, major_cores))

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
            return None

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
            group2 = re.sub(r'^[^\(]*', '', group2)
            #//TODO can remove
            group2 = re.sub(r'^\(', '', group2)
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
    braces = False
    # check if there are groups - groups are split up by commas or braces
    if (re.match(r'^Prerequisites?:\s*\(', prerequisites)):
        # using braces
        braces = True
        groups = prerequisites.split(')')
    else:
        # using commas
        groups = prerequisites.split(',')

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
        group_link = re.search(r'^\s*(\w+)', groups[1]).group(1)
        if group_link == "and":
            '''
            they're using or groups - this is tricky
            thank god I took discrete math to turn
            (A or B) AND C into 
            (A AND C) OR (B AND C)
            i.e. convert or groups to and groups
            '''
            # parenthesize properly for the merge
            if braces:
                for i in range(len(groups)):
                    groups[i] = groups[i].replace("(", "")
                    groups[i] = re.sub(r'([A-Z]{4}\d{4})', r'(\1)', groups[i])
            else:
                prerequisites = re.sub(r'([A-Z]{4}\d{4})', r'(\1)', prerequisites)
                groups = prerequisites.split(",")

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
        Return list of course objects
    '''

    ret_list = []
    for course_link in course_links:
        # go to course page
        course_page = requests.get(course_link);
        course_soup = BeautifulSoup(course_page.content, 'html.parser')
        # get course info
        course_name = course_soup.find("span", {"data-hbui" : "module-title"}).text
        course_code = course_soup.find("strong", class_="code").text
        conditions = course_soup.find("div", id='SubjectConditions')
        prereqs = [[]]
        if conditions is not None:
            prerequisites = conditions.find("div", text=re.compile(r'^Prerequisite:'))
            if prerequisites is not None:
                prereqs = parse_prereqs(prerequisites.text)

        ret_list.append(Course(course_code, course_name, 0, 0, 0, prereqs, [], flex))

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

i = 0
for table in code_soup.find_all("table"):
    # check the table's first column is "UAC Code"
    # Assume it's the correct table if it is
    check_table = table.find("tr").find("td");
    if check_table is None:
        continue;

    if not re.match(r'^UAC\s*Code\s*$', check_table.text):
        continue

    # Iterate through all program codes
    i = 0
    for row in table.find_all("tr"):
        if i > 0:
            break
        i = i + 1

        prog_code = row.find_all("td")[1].text.strip().replace(" ", "")
        prog_code = "3502"
        # check it's 4 digits
        if not re.match(r'\d{4}', prog_code):
            continue

        print(prog_code)

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
        prog = Program(prog_code, prog_name, 2019, 0, [])

        # check if there are program wide core courses
        # assume all courses found here are mandatory for the program
        core_links = get_core_links(prog_soup)
        cores = get_courses(core_links, False)
        for core in cores:
            print("Core code: %s" % core.code)
            print("Core name: %s" % core.name)
            #print("Course prerequisites: %s" % ','.join(map(str, core.prereqs)))
        
        # check if there are flex courses e.g. commerce
        flex_links = get_flex_links(prog)
        flex = get_courses(flex_links, True)
        for f in flex:
            print("Flex code: %s" % f.code)
            print("Flex name: %s" % f.name)

        # go to program majors to find program specific cores
        major_links = get_major_links()
        majors = get_majors(major_links)
        for major in majors:
            print("Major code: %s" % major.code)
            print("Major name: %s" % major.name)
            print("Major cores: ")
            for core in major.cores:
                print("Core code: %s" % core.code)
                print("Core name: %s" % core.name)
                print("Core prerequisites:", end='')
                if not core.prereqs:
                    continue

                print(core.prereqs)
    break
