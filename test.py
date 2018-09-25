# test the prereq parser
import re
coderx = r'[A-Z]{4}\d{4}'
coderx_g = r'([A-Z]{4}\d{4})'

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
    print("merging %s and %s" % (str1, str2))
    ret_str = ''
    first_insert = True
    prereqs = []

    # remove double braces
    str1 = re.sub(r'^[^\(]*\(\(', '(', str1)
    str1 = re.sub(r'\)\)\s*$', ')', str1)
    str2 = re.sub(r'^[^\(]*\(\(', '(', str2)
    str2 = re.sub(r'\)\)\s*$', ')', str2)

    # check if leading link related to earlier group
    leading_link = re.search(r'^\s*(and|or)', str1, re.I)
    if leading_link is not None:
        leading_link = leading_link.group(1)
        str1 = re.sub(r'^\s*(and|or)', '', str1, flags=re.I)

    # SPLIT ON OR LINK!!!!
    groups1 = list(filter(None, mark_outside_or(str1).split('!')))
    groups2 = list(filter(None, mark_outside_or(str2).split('!')))
    
    '''
    print("groups1: ")
    print(groups1)
    print("groups2:")
    print(groups2)
    '''

    # match all groups in group1 with all groups in group2
    # assuming all has been converted to 'or' groups already
    for group1 in groups1:
        group1 = clean_str(group1)
        for group2 in groups2:
            group2 = clean_str(group2)
            if (first_insert):
                ret_str = '(' + group1 + " and " + group2 + ')'
                first_insert = False
            else:
                ret_str = ret_str + ' or ' + '(' + group1 + ' and ' + group2 + ')'

    if leading_link:
        return leading_link + ret_str

    return ret_str

def clean_str(bool_group):
    bool_group = bool_group.strip()
    # remove prereq string
    bool_group = re.sub(r'^\s*prerequisites?:?\s*', '', bool_group, flags=re.I)
    # remove leading link word
    bool_group = re.sub(r'^\s*and\s*\(?', '', bool_group, flags=re.I)
    # remove trailing link word
    bool_group = re.sub(r'\s*or\s*$', '', bool_group, flags=re.I)
    # remove braces for single code bool groups
    bool_group = re.sub(r'^\s*\(?(%s)\)?\s*$' % coderx, r'\1', bool_group)
    #bool_group = re.sub(r'\)\s*$', '', bool_group)

    # remove double brace
    #group2 = re.sub(r'\(\(', '(', group2)
    #group2 = re.sub(r'\)\)', ')', group2)
    #print("group2: %s" % group2)

    return bool_group

def mark_outside_brace(prerequisites):
    '''
        mark c that is one level in braces
    '''
    brace_count = 0
    i = 0
    while i < len(prerequisites):
        #print("curr: " + prerequisites[i])
        if prerequisites[i] == "(":
            #print("inc on " + prerequisites[i])
            brace_count += 1
        elif prerequisites[i] == ")":
            #print("dec on " + prerequisites[i])
            brace_count -= 1
            if brace_count == 0:
                # mark
                prerequisites = prerequisites[:i+1] + "!" + prerequisites[i+1:]
        i = i + 1

    return prerequisites

def mark_outside_or(prerequisites):
    '''
        mark or that is one level in braces
    '''
    brace_count = 0
    i = 0
    while i < len(prerequisites):
        #print("curr: " + prerequisites[i])
        if prerequisites[i] == "(":
            #print("inc on " + prerequisites[i])
            brace_count += 1
        elif prerequisites[i] == ")":
            brace_count -= 1
        elif prerequisites[i] == "O" or prerequisites[i] == "o":
            if prerequisites[i+1] == "R" or prerequisites[i+1] == "r":
                if brace_count == 0:
                    # mark
                    prerequisites = prerequisites[:i+2] + "!" + prerequisites[i+2:]
        i = i + 1

    return prerequisites

def to_or_groups(prerequisites):
    # if only 1 code return
    #print("Incoming pre: %s" % prerequisites)
    codes = re.findall(coderx, prerequisites)
    if len(codes) <= 1:
        print("one code, returning")
        return prerequisites

    # remove double braces
    print("prereqs before: %s" % prerequisites)
    prerequisites = re.sub(r'(^|and|or)([^\(]*)\(\(', r'\1\2(', prerequisites, re.I)
    prerequisites = re.sub(r'\)\)\s*$', ')', prerequisites)
    print("prereqs after: %s" % prerequisites)

    prerequisites = mark_outside_brace(prerequisites)
    print("outside braces marked: %s" % prerequisites)

    # split on outside braces
    groups = list(filter(None, prerequisites.split("!")))
    print("groups: ")
    print(groups)

    i = 0
    while i < len(groups):
        # parenthesize or groups
        groups[i] = re.sub(r'(\(%s)\s*[^\)]\s*or' % coderx, r'(\1) OR', groups[i], flags=re.I)
        groups[i] = re.sub(r'or\s*(%s\s*\))' % coderx, r'OR (\1)', groups[i], flags=re.I)
        groups[i] = re.sub(r'or\s*(%s)\s*or' % coderx, r'OR (\1) OR', groups[i], flags=re.I)
        i = i + 1

    # merge all inner groups if you just split into multiple groups
    if (len(groups) > 1):
        i =0
        while i < len(groups):
            groups[i] = to_or_groups(groups[i])
            i  = i + 1

    # merge the outer groups
    i = 0
    while i < len(groups)-1:
        # merge groups 0 and 1
        # error
        print("curr grp 0: %s" % groups[0])
        print("curr grp 1: %s" % groups[1])
        link_word = re.search(r'^\s*(and|or)', groups[1], re.I).group(1).lower()
        if link_word == "or":
            # or groups are an easy merge
            new_group = groups[0] + groups[1]

        elif link_word == "and":
            # merge groups
            new_group = merge(groups[0], groups[1])

        print("The merged group: %s" % new_group)
        groups.pop(0)
        groups.pop(0)
        groups.insert(0, new_group)

    return groups[0]
     

def parse_prereqs(prerequisites):
    '''
        Take the UNSW prereq string from handbook and return
        list of prereqs in form
        [[course1, course2],[course3], [course4]]
        where in list commas are AND, while out of list
        commas are OR
    '''
    
    # groups with braces
    prerequisites = to_braces(prerequisites)
    prereqs = []

    # check if they're even using groups
    if (len(list(filter(None, prerequisites.split("(")))) == 1):
        print("NO GROUPS")
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

        return prereqs

    #print("Braced: %s" % prerequisites)
    # sometimes single prereqs aren't fully parenthesised e.g. MARK3082
    prerequisites = complete_groups(prerequisites)
    #print("Grouped: %s" % prerequisites)
    prerequisites = to_or_groups(prerequisites)            
    print("After or groupsing: %s" % prerequisites)

    groups = mark_outside_brace(prerequisites).split('!')
    # empty lists ruin things
    groups = list(filter(None, groups))
 
    # using and groups - easy, can put straight into prereqs
    for group in groups:
        and_group = []
        for code in re.findall(coderx, group):
            and_group.append(code)
        prereqs.append(and_group)

    return prereqs

    '''
    groups = prerequisites.split(')')
    # empty lists ruin things
    groups = list(filter(None, groups))
    #print("groups:")
    #print(groups)

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
         groups could be 'or' groups or 'and' groups
        and groups can go straight into list, but or
        groups need to be manipulated to become and groups

        # group type determined by link word, which is first seen in group 2
        group_link = re.search(r'^\s*(\w+)', groups[1])
        if group_link is None:
            # irregular format e.g. MGMT2718
            return [[]]

        group_link = group_link.group(1)
        if re.match("and", group_link, re.I): 
            they're using or groups - this is tricky
            thank god I took discrete math to turn
            (A or B) AND C into 
            (A AND C) OR (B AND C)
            i.e. convert or groups to and groups
            # parenthesize properly for the merge
            for i in range(len(groups)):
                groups[i] = groups[i].replace("(", "")
                print("old: %s" % groups[i])
                groups[i] = re.sub(coderx_g, r'(\1)', groups[i])
                print("new: %s" % groups[i])

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
    '''
    return prereqs

# test cases
test1 = "Prerequisite: MARK1012 AND (MARK2051 OR MARK2151) AND MARK2052"
test2 = "Prerequisite: ECON1101 or ECON1102"
test3 = "Prerequisite: ECON1101 and ECON1102"
test4 = "Prerequisite: COMP1921 or COMP1927 or MTRN3500, or (COMP1521, and COMP2521 or MTRN3500)"
test5 = "Prerequisite: COMP0000 and (MATH1111 or MATH1112)"
tests = [test1, test2, test3, test4, test5]
for test in tests:
    print("Test string: %s" % test)
    print("After parsing:")
    print(parse_prereqs(test))
