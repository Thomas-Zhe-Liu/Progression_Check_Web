import requests
from bs4 import BeautifulSoup
import re

# get all UNSW program codes from this UNSW website
hb_program_base = "https://www.handbook.unsw.edu.au/undergraduate/programs/2019/"
program_codes = requests.get("http://www.gettingstarted.unsw.edu.au/uac-codes-and-corresponding-unsw-undergraduate-program-codes");
code_soup = BeautifulSoup(program_codes.content, 'html.parser')
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
    for row in table.find_all("tr"):
        prog_code = row.find_all("td")[1].text.strip().replace(" ", "")
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

        # check if there are program wide core courses
        # assume all courses found here are mandatory for the program
        core_course_headers = prog_soup.find_all("h4", {"data-hbui" : "readmore__heading"}, text=re.compile('Core Courses'))
        for header in core_course_headers:
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

            # Check if they're flexi cores
            if re.match(r'^Flex', header.text):
                # get number of courses that must be taken in the list
                uoc_p = course_info.find("p", text=re.compile(r'^Students'))
                num_uoc = re.match(r'.*?(\d{1,2}) UOC', uoc_p.text).group(1)
                print("Must take %s UOC of flex courses\n" % num_uoc)

            course_list = core_courses.find("div", {"data-hbui" : "course-list"}).find_all("div", recursive=False)
            for course in course_list:
                course_data = course.find("a")['aria-label'].replace('\n', '').split(",")
                course_code = course_data[0].split(":")[1].replace(' ', '')
                course_name = course_data[1].split(".")[0].strip()
                print("Course code: %s" % course_code)
                print("Course name: %s" % course_name)
