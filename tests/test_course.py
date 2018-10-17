from .. import course

#Test sort_course
courses = get_core_courses('COMPA1', 2019)
print("before: ", courses)
sorted_courses = sort_courses(courses)
print("after: ", sorted_courses)


#Test get_pre_requisite
r = get_pre_requisite('COMP2511')
print(r)
r = get_pre_requisite('COMP1511')
print(r)

# Test is_core
assert(is_core('1111', '2019', 'COMPA1', 'COMP3331') == False)
assert (is_core('1111', '2019', 'COMPA1', 'COMP1511') == True)

# Test is_elective
assert(is_elective('3778', '2019', 'COMPA1', 'COMP3331') == True)
assert(is_elective('3778', '2019', 'COMPA1', 'COMP2331') == False)

# Test is_gene
assert(is_gene('2019', 'COMP2511') == True)
assert(is_gene('2019', 'COMP3131') == False)
