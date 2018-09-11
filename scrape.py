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
    def __init__(self, course_code, course_name, t1, t2, t3, prereqs, flex):
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
        print(header.text)
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
        ret_list.append(Major(major_code, major_name, 0, 0, 0, []))

    return ret_list

def get_core_links():
    ret_list = []
    core_course_headers = prog_soup.find_all("h4", {"data-hbui" : "readmore__heading"}, text=re.compile('Core Courses'))
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

        course_list = core_courses.find("div", {"data-hbui" : "course-list"}).find_all("div", recursive=False)
        for course in course_list:
            '''
            course_data = course.find("a")['aria-label'].replace('\n', '').split(",")
            course_code = course_data[0].split(":")[1].replace(' ', '')
            course_name = course_data[1].split(".")[0].strip()
            print("Course code: %s" % course_code)
            print("Course name: %s" % course_name)
            '''
            ret_list.append(hb_base + course.find("a")['href'].strip())

    return ret_list

def get_courses(course_links, flex):
    '''
        Take in list of links to core pages
        Return list of core objects
    '''

    ret_list = []
    for course_link in course_links:
        # go to course page
        course_page = requests.get(course_link);
        course_soup = BeautifulSoup(course_page.content, 'html.parser')
        # get course info
        course_name = course_soup.find("span", {"data-hbui" : "module-title"}).text
        course_code = course_soup.find("strong", class_="code").text
        #//TODO get course data e.g. prereqa
        ret_list.append(Course(course_code, course_name, 0, 0, 0, [], flex))

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
        core_links = get_core_links()
        cores = get_courses(core_links, False)
        for core in cores:
            print("Core code: %s" % core.code)
            print("Core name: %s" % core.name)
        
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
    break
