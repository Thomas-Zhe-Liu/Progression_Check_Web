from .. import core_course.py

# Test cse_get_remaining_courses
to_complete = ['COMP1511']
expected_to_complete = ['COMP1521', 'COMP1531', 'COMP2511', 'COMP2521', 'COMP3121', 'COMP3900', 'COMP4920', 'MATH1081', 'MATH1131', 'MATH1141',
						 'MATH1231', 'MATH1241']
assert(set(get_remaining_cores('', '', 'COMPA1', to_complete)) == set(expected_to_complete))
expected_to_complete.remove('MATH1241')
to_complete.append('MATH1241')
assert(set(get_remaining_cores('', '', 'COMPA1', to_complete)) == set(expected_to_complete))
