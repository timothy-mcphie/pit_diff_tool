class Score(object):
    """
    Store results of a set of mutants
    """

    def __init__(self, score_type, mutants=0, killed=0, survived=0, no_coverage=0):
        self.score_type=score_type
        self.mutants=mutants
        self.killed=killed
        self.survived=survived
        self.no_coverage=no_coverage

    def __str__(self):
        return self.score_type+' mutants: '+str(self.mutants)+' Killed: '+str(self.killed)+ \
        ' Survived: '+str(self.survived)+' No Coverage: '+str(self.no_coverage)

    def update(self, mutant):
        """
        Update score given a mutant
        """
        self.mutants += 1
        if mutant.status == 'no_coverage':
            self.no_coverage += 1
        elif mutant.status == 'survived':
            self.survived += 1
        elif mutant.status == 'killed': 
            self.killed += 1

class Mutation_score(object):
    """
    Abstract ish class
    """
    def __init__(self, name, parent, children=True):
        self.name = str(name)
        self.new = Score('[NEW]')
        self.changed = Score('[CHANGED]')
        self.unchanged = Score('[UNCHANGED]')
        self.removed = Score('[REMOVED]')
        self.parent = parent
        if children:
            self.children = {} #switch to using list of tuples if memory low

    def get_child(self, Class, key):
        if key not in self.children:
            self.children[key] = Class(key, self)
        return self.children[key]

    def update_new(self, mutant):
        self.new.update(mutant)

    def update_changed(self, mutant):
        self.changed.update(mutant)

    def update_unchanged(self, mutant):
        self.unchanged.update(mutant)

    def update_removed(self, mutant):
        self.removed.update(mutant)

    def __str__(self):
        return type(self).__name__+' '+self.name+'\n'+str(self.new)+'\n'+str(self.changed)+'\n'+str(self.unchanged)+'\n'+str(self.removed)

class Method_score(Mutation_score):
    """
    Store scores for new/changed mutants across a method.
    """
    def __init__(self, name, src_class):
        Mutation_score.__init__(self, name, src_class, False)
        #append mutants within methods for output purposes?

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
        self.get_child(Method_score, mutant.mut_method).update_removed(mutant)

class Report_score(Mutation_score):
    """
    Store scores for new/changed mutants across a report.
    """
    #Can refactor so interface has attribute which can be the class type of the children

    def get_filename(self, mutant):
        if mutant.target_file is not None:
            return mutant.target_file #use the new snapshot filename as the key
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
        self.get_child(Method_score, self.get_filename(mutant)).update_removed(mutant)

    def total_old(self):
        return self.changed.mutants + self.unchanged.mutants + self.removed.mutants
