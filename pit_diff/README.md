cmd.py

Contains functions for executing shell commands from Python using the subprocess module \
useful for using the pit_diff tool.

diff.py

The pit_diff main tool. Its main function, get_pit_diff, takes two pit reports and their \
commits, and returns a reference to a score object with the differences in mutation score\
. This yields removed, new, changed and unchanged mutants, presented in a tree hierarchy \
giving file, class and method level granularity. The code in this file copes with renames\
 at file, class and method level.

git_diff.py

Code for parsing a diff of a repository between two commits. Loads this information into\
 a map which can be used by to identify on which lines and in which files mutants may \
have moved to due to additions and deletions.

mutant.py

Contains a class for representing a pit report mutant. Reports are parsed and turned into\
these. Pit_diff manipulates objects of this type.

scores.py

Contains classes for storing the results of a pit report and a tree which can be traversed\
 to get the results at different granularities.

