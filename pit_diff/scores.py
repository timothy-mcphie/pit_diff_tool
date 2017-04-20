class Score(object):
    """
    Store results of a set of mutants
    """

    def __init__(self, score_type):
        self.score_type=score_type
        self.mutants=0

        self.no_coverage=0
        self.survived=0
        self.killed=0
        self.timed_out=0
        self.memory_error=0
        self.run_error=0

    def __str__(self):
        return self.score_type+" mutants: "+str(self.mutants)+" Killed: "+str(self.killed)+ \
        " Survived: "+str(self.survived)+" No Coverage: "+str(self.no_coverage)

    def update(self, mutant):
        """
        Update score given a mutant
        """
        self.mutants += 1
        if mutant.status == "no_coverage":
            self.no_coverage += 1
        elif mutant.status == "survived":
            self.survived += 1
        elif mutant.status == "killed": 
            self.killed += 1
        elif mutant.status == "timed_out":
            self.timed_out += 1
        elif mutant.status == "memory_error":
            self.memory_error += 1
        elif mutant.status == "run_error":
            self.run_error += 1
        #NB the last three may be inconsistent in different runs

class Mutation_score(object):
    """
    Abstract ish class
    """
    def __init__(self, name, parent, children=True):
        self.name = str(name)
        #Use an 9 element array initialised to 0 translate the mutants to get index
        #don't care about time outs, memory or run errors
        self.changed = [0 for x in range(0,9)]

        self.new = Score("[NEW]")
        self.unchanged = Score("[UNCHANGED]")
        self.removed = Score("[REMOVED]")

        self.parent = parent
        self.modified = False
        if children:
            self.children = {} #switch to using list of tuples if memory low

    def get_child(self, Class, key):
        if key not in self.children:
            self.children[key] = Class(key, self)
        return self.children[key]

    def update_new(self, mutant):
        self.new.update(mutant) 

    def update_unchanged(self, mutant):
        self.unchanged.update(mutant)

    def update_removed(self, mutant):
        self.removed.update(mutant)

    def update_changed(self, old_mutant, mutant):
        #TODO: add check to see if indices are equal - there has been no change.
        if mutant.get_index() < 3 or old_mutant.get_index() < 3:
            self.changed[old_mutant.get_index()*3+mutant.get_index()] += 1

    def str_row_changed(self, start):
        return " no_coverage " + str(self.changed[start]) +\
        " survived " + str(self.changed[start + 1]) +\
        " killed " + str(self.changed[start + 2])

    def str_changed(self):
        #TODO: create property method in mutant class returns a status given an index use in loop to build string - neater 
        return "no_coverage TO" + self.str_row_changed(0) + "\n" + \
        "survived TO" + self.str_row_changed(3) + "\n" + \
        "killed TO" + self.str_row_changed(6)

    def add_changed(self, addee):
        for i in range(0,36):
            self.changed[i] += int(addee[i])

    def total_changed(self):
        return sum(self.changed)

    def __str__(self):
        return type(self).__name__+" "+self.name+"\n"+str(self.new)+"\n"+"\n"+str(self.unchanged)+"\n"+str(self.removed)

    """
    def total_new(self):
        return self.new.mutants+self.changed.mutants+self.unchanged.mutants

    def total_old(self):
        return self.removed.mutants+self.changed.mutants+self.unchanged.mutants

    def delta_tuple(self):
        return (self.new.mutants+self.changed.mutants, \
                self.total_new(), self.total_old()) 
    """

class Method_score(Mutation_score):
    """
    Store scores for new/changed mutants across a method.
    """
    def __init__(self, name, src_class):
        Mutation_score.__init__(self, name, src_class, False)
        self.changed_mutants = None #append refs to changed mutants

    def update_changed(self, old_mutant, mutant):
        if self.changed_mutants is None:
            self.changed_mutants = []
        self.changed_mutants.append(mutant)

class Class_score(Mutation_score):
    """
    Store scores for new/changed mutants across a class.
    """
    def update_new(self, mutant):
        Mutation_score.update_new(self, mutant)
        self.get_child(Method_score, mutant.mut_method).update_new(mutant)

    def update_changed(self, old_mutant, mutant):
        Mutation_score.update_changed(self, old_mutant, mutant)
        self.get_child(Method_score, mutant.mut_method).update_changed(old_mutant, mutant)

    def update_unchanged(self, mutant):
        Mutation_score.update_unchanged(self, mutant)
        self.get_child(Method_score, mutant.mut_method).update_unchanged(mutant)

    def update_removed(self, mutant):
        Mutation_score.update_removed(self, mutant)
        self.get_child(Method_score, mutant.mut_method).update_removed(mutant)

class File_score(Mutation_score):
    """
    Store scores for new/changed mutants across a source file..
    """
    def update_new(self, mutant):
        Mutation_score.update_new(self, mutant)
        self.get_child(Class_score, mutant.mut_class).update_new(mutant)

    def update_changed(self, old_mutant, mutant, modified):
        self.modified = modified
        Mutation_score.update_changed(self, old_mutant, mutant)
        self.get_child(Class_score, mutant.mut_class).update_changed(old_mutant, mutant)

    def update_unchanged(self, mutant):
        Mutation_score.update_unchanged(self, mutant)
        self.get_child(Class_score, mutant.mut_class).update_unchanged(mutant)

    def update_removed(self, mutant):
        Mutation_score.update_removed(self, mutant)
        self.get_child(Class_score, mutant.mut_method).update_removed(mutant)

class Report_score(Mutation_score):
    """
    Store scores for new/changed mutants across a report.
    """
    #Can refactor so interface has attribute which can be the class type of the children

    def get_filename(self, mutant):
        """
        restore a new mutant's new snapshot file name to be used as a key in the score
        restore the line number so a changed mutant will display the correct tuples
        """
        if mutant.target_file is not None:
            mutant.source_file = mutant.target_file
        if mutant.target_line_no is not None:
            mutant.source_line_no = mutant.target_line_no
        return mutant.source_file

    def update_new(self, mutant):
        Mutation_score.update_new(self, mutant)
        self.get_child(File_score, self.get_filename(mutant)).update_new(mutant)

    def update_changed(self, old_mutant, mutant, modified):
        Mutation_score.update_changed(self, old_mutant, mutant)
        self.get_child(File_score, self.get_filename(mutant)).update_changed(old_mutant, mutant, modified)

    def update_unchanged(self, mutant):
        Mutation_score.update_unchanged(self, mutant)
        self.get_child(File_score, self.get_filename(mutant)).update_unchanged(mutant)

    def update_removed(self, mutant):
        Mutation_score.update_removed(self, mutant)
        self.get_child(File_score, self.get_filename(mutant)).update_removed(mutant)#get_filename not needed, old mutants can"t be renamed.
