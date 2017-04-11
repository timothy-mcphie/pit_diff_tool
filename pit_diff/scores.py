class Score(object):
    """
    Store results of a set of mutants
    """

    def __init__(self, score_type, mutants=0, killed=0, survived=0, no_coverage=0, timed_out=0):
        self.score_type=score_type
        self.mutants=mutants
        self.killed=killed
        self.survived=survived
        self.no_coverage=no_coverage
        self.timed_out=timed_out

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
            #NB time outs may be inconsistent in different runs
            self.timed_out += 1

class Mutation_score(object):
    """
    Abstract ish class
    """
    def __init__(self, name, parent, children=True, modified=True, renamed=True):
        self.name = str(name)
        self.new = Score("[NEW]")
        self.changed = Score("[CHANGED]")
        self.unchanged = Score("[UNCHANGED]")
        self.removed = Score("[REMOVED]")
        self.parent = parent
        self.modified = modified
        self.renamed = renamed
        if children:
            self.children = {} #switch to using list of tuples if memory low

    def get_child(self, Class, key):
        if key not in self.children:
            self.children[key] = Class(key, self)
        return self.children[key]

    @property
    def total_new(self):
        return self.new.mutants+self.changed.mutants+self.unchanged.mutants

    @property
    def total_old(self):
        return self.removed.mutants+self.changed.mutants+self.unchanged.mutants

    def delta_tuple(self):
        return (self.new.mutants+self.changed.mutants, \
                self.total_new(), self.total_old())

    def update_new(self, mutant):
        self.new.update(mutant)

    def update_changed(self, mutant):
        self.changed.update(mutant)

    def update_unchanged(self, mutant):
        self.unchanged.update(mutant)

    def update_removed(self, mutant):
        self.removed.update(mutant)

    def __str__(self):
        return type(self).__name__+" "+self.name+"\n"+str(self.new)+"\n"+str(self.changed)+"\n"+str(self.unchanged)+"\n"+str(self.removed)

class Method_score(Mutation_score):
    """
    Store scores for new/changed mutants across a method.
    """
    def __init__(self, name, src_class):
        Mutation_score.__init__(self, name, src_class, False)
        self.changed_mutants = None #append refs to changed mutants

    def update_changed(self, mutant):
        if self.changed_mutants is None:
            self.changed_mutants = []
        self.changed_mutants.append(mutant)
        self.changed.update(mutant)

class Class_score(Mutation_score):
    """
    Store scores for new/changed mutants across a class.
    """
    def update_new(self, mutant):
        Mutation_score.update_new(self, mutant)
        self.get_child(Method_score, mutant.mut_method).update_new(mutant)

    def update_changed(self, mutant):
        Mutation_score.update_changed(self, mutant)
        self.get_child(Method_score, mutant.mut_method).update_changed(mutant)

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

    def update_changed(self, mutant):
        Mutation_score.update_changed(self, mutant)
        self.get_child(Class_score, mutant.mut_class).update_changed(mutant)

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
        restore a new mutant"s new snapshot file name to be used as a key in the score
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

    def update_changed(self, mutant):
        Mutation_score.update_changed(self, mutant)
        self.get_child(File_score, self.get_filename(mutant)).update_changed(mutant)

    def update_unchanged(self, mutant):
        Mutation_score.update_unchanged(self, mutant)
        self.get_child(File_score, self.get_filename(mutant)).update_unchanged(mutant)

    def update_removed(self, mutant):
        Mutation_score.update_removed(self, mutant)
        self.get_child(File_score, self.get_filename(mutant)).update_removed(mutant)#get_filename not needed, old mutants can"t be renamed.
