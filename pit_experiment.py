from pit_diff.diff import *
#from diff import *

old_rep = "/Users/tim/Code/commons-collections/pitReports/201704062226/mutations.xml"
new_rep = "/Users/tim/Code/commons-collections/pitReports/201704062043/mutations.xml"
old_commit="cfffa7138c04b971d119a5da94b9a71d610bba0a"
new_commit="HEAD"
repo_path="/Users/tim/Code/commons-collections"

print str(get_pit_diff(old_commit, new_commit, repo_path, old_rep, new_rep))
