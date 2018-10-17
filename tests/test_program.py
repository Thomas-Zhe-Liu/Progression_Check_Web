from .. import program

# Test get_gene_uoc
assert(get_gene_uoc('3778', '2019') == 12)

# Test get_free_uoc
assert(get_free_uoc('3778', '2019') == 36)
