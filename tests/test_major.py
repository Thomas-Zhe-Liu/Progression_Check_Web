from .. import major


# Test get_elective_uoc
assert(get_elective_uoc('2019', 'COMPA1') == 30)

# Test get_specific_electives_groups
assert(len(get_specific_elective_groups(2019, 'COMPA1')) == 0)
groups = get_specific_elective_groups(2019, 'COMPD1')
assert(len(groups) == 1)
assert(groups[0].group_uoc == 18)
expected_db_electives = ['COMP6714', 'COMP9313', 'COMP9315', 'COMP9318', 'COMP9319']
assert(set(expected_db_electives) == set(groups[0].group_course_list))

# Test is_specific_elective()
assert(is_specific_elective('2019', 'COMP6714', groups) == True)
assert(is_specific_elective('2019', 'COMP1511', groups) == False)
