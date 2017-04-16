import sys
import os
import csv
from pit_diff import cmd, diff, git_diff, scores as s
#TODO: Use a logging function instead of prints - can ditch the [FNAME] tag - output status of cmds to file

global MAX_CONSECUTIVE_BUILD_FAILS
MAX_CONSECUTIVE_BUILD_FAILS = 15

def parse_report_score(report_score):
    """
    Get two lists of directly changed mutants (those in modified files) 
    and the indirectly changed mutants (those in unmodified files) 
    """ 
    modified = s.Mutation_score("modified", None)
    unmodified = s.Mutation_score("unmodified", None)
    for file_score in report_score.children.values(): 
        if file_score.modified:
            modified.add_changed(file_score.changed)
        else:
            unmodified.add_changed(file_score.changed)
    return (modified, unmodified)

def output_score(total_modified, total_unmodified, new_commit, report_score, report_dir, output_file, csv=False): 
    """
    Output and append to a csv file the change a new_commit introduces to the mutation score
    """
    (modified, unmodified) = parse_report_score(report_score)
    print "[PIT_EXP] retrieved modified with ", modified.total_changed(), " unmodified with ", unmodified.total_changed()
    #with open(output_file, "a+") as f:
    #    w = csv.writer(f, delimiter=",")
    #    w.writerow([new_commit])
    #    w.writerow(["modified"]+modified.changed)
    #    w.writerow(["unmodified"]+unmodified.changed) 
    total_modified.add_changed(modified.changed) 
    total_unmodified.add_changed(unmodified.changed) 

def load_output(report_dir, output_file, total_modified, total_unmodified):
    """
    Parse an output csv - loading the results of any previous pit_diffs on reports
    """
    #TODO: Only reload output if they are commits newer than start_commit and return the start and end commits of the previous output
    if not os.path.isfile(output_file):
        print "[PIT_EXP] no output_file ", output_file, " found to load from"
        return
    with open(output_file, "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=",") 
        for row in reader:
            if str(row[0]) == "modified":
                total_modified.add_changed(row[1:])
            elif str(row[0]) == "unmodified":
                total_unmodified.add_changed(row[1:])
    print "[PIT_EXP] Found previous output of experiment in ", output_file
    print "[PIT_EXP] Currently Modified files have ", total_modified.total_changed(), " mutants"
    print "[PIT_EXP] Currently Unmodified files have ", total_unmodified.total_changed(), " mutants"
    return

def copy_build_files(repo):
    build_files = repo+"/../build_files-commons-collections"
    if not os.path.isdir(repo+"/lib"):
        print "[PIT_EXP] making lib dir in ", repo
        if cmd.run_cmd(["mkdir", repo+"/lib"]):
            print "[PIT_EXP] Failed to make lib dir for dependencies"
            return False
    print "[PIT_EXP] Copying files from ", build_files, " to ", repo
    if cmd.run_cmd(["cp", "-a", build_files+"/lib", repo+"/lib"]):
        print "[PIT_EXP] Failed to copy dependencies to lib"
        return False
    return True

def checkout_commit(repo, commit):
    if cmd.run_cmd(["git", "-C", repo, "checkout", commit, "-f"], "/dev/null") != 0:
        print "[PIT_EXP] Cannot check out commit ", commit, " in repo ", repo
        return False
    return True 

def mvn_compile(repo):
    if not os.path.isfile(repo+"/pom.xml"):
        print "[PIT_EXP] No pom.xml found in repo ", repo, " building with maven not possible"
        sys.exit(1)
    print "[PIT_EXP] repo is ", repo
    try:
        os.chdir(repo)
    except OSError as e:
        print "[PIT_EXP] Could not cd to repo ", repo, " ", e
        sys.exit(1)
    if cmd.run_cmd(["mvn", "test"]) != 0:
        #can do multi threading with -T x, where x is an integer, however some builds aren't threadsafe - causes failures
        return False
    return True

def get_mvn_classpath(repo):
    """
    Extract the classpath from the maven build - pit searches this for classes to mutate
    """
    cp_file = repo+"/cp.txt"
    if cmd.run_cmd(["mvn", "dependency:build-classpath", "-Dmdep.outputFile="+cp_file]) != 0:
        print "[PIT_EXP] Failed to extract classpath from maven"
        return None
    cp = None
    try:
        with open(cp_file, "r") as f:
            cp = f.readline()
    except:
        print "[PIT_EXP]couldn't perform open on ", cp_file
        return None
    if cmd.run_cmd(["rm", cp_file]) != 0: 
        print "[PIT_EXP] Failed to delete remaining classpath file from maven"
        return None
    return cp.strip()

def get_pit_report(repo, commit, report_dir, pit_filter):
    """
    Checkout, build and generate pit report for a repo snapshot
    """
    report_path = cmd.get_report_name(report_dir, commit)
    if os.path.isfile(report_path):
        print "[PIT_EXP] Found report previously generated at ", report_path
        return report_path
    if not checkout_commit(repo, commit): 
        print "[PIT_EXP] Failed to checkout commit ", commit, " exiting"
        sys.exit(1) 
    if not copy_build_files(repo):
        print "[PIT_EXP] Could not set up build environment in ", repo, " exiting"
        sys.exit(1) 
    if not mvn_compile(repo):
        print "[PIT_EXP] Build of ", commit, " failed - skipping this snapshot"
        return None
    print "[PIT_EXP] getting maven classpath of ", commit
    mvn_classpath = get_mvn_classpath(repo)
    if mvn_classpath is None:
        print "[PIT_EXP] failed to get classpath from maven for snapshot ", commit, " - skipping this snapshot"
        return None 
    print "[PIT_EXP] Running pit on ", commit

    classpath = repo+"/lib/pitest-command-line-1.1.11.jar:"+\
repo+"/lib/pitest-1.1.11.jar:"+\
repo+"/lib/junit-4.11.jar:"+\
mvn_classpath+":"+\
repo+"/target/classes:"+\
repo+"/target/test-classes:"
    target_classes = target_tests = pit_filter
    src_dir = repo+"/src"
    threads = "4"

    if cmd.run_pit(repo, classpath, report_dir, target_classes, target_tests, src_dir, threads) is None:
        print "[PIT_EXP] Pit report of ", commit, " failed to generate"
        return None
    report_path = cmd.rename_file(report_dir+"/mutations.xml", report_path)
    if report_path is None:
        print "[PIT_EXP] Failed to complete rename"
    return report_path

def main(repo, start_commit, end_commit, report_dir, pit_filter, output_file):
    """
    Iterate backwards over commits in a repo running pit
    """ 
    #TODO: Speed up with PIT incremental analysis by iterating forwards
    if not cmd.is_repo(repo):
        print "[PIT_EXP] This is not a valid git repository ", repo
        return
    start_commit = cmd.get_commit_hash(repo, start_commit)
    if start_commit is None:
        print "[PIT_EXP] Failed to get hash of supplied commit ", commit
        return 
    total_modified = s.Mutation_score("total_modified", None)
    total_unmodified = s.Mutation_score("total_unmodified", None) 
    load_output(report_dir, output_file, total_modified, total_unmodified)

    new_report = get_pit_report(repo, start_commit, report_dir, pit_filter)
    new_commit = old_commit = start_commit #old_commit is the historically older snapshot of the project 
    failed_streak = 0
    while True:
        old_commit = cmd.get_commit_hash(repo, old_commit+"^")
        if old_commit is None or old_commit == end_commit:
            print "[PIT_EXP] End of commit history, exiting"
            break
        print "[PIT_EXP] Parsing diff of commits ", old_commit, " to ", new_commit
        modified_files = git_diff.process_git_info(old_commit, new_commit, repo)
        print "[PIT_EXP] Edited files: ", str([str(key) for key in modified_files.keys()])
        if not modified_files:
            print "[PIT_EXP] Skipping commits with no java source files edited, no probable change to mutation score"
            continue
        old_report = get_pit_report(repo, old_commit, report_dir, pit_filter)
        if old_report is None:
            failed_streak += 1
            if failed_streak >= MAX_CONSECUTIVE_BUILD_FAILS:
                print "[PIT_EXP] Couldn't build ", MAX_CONSECUTIVE_BUILD_FAILS, " consecutive commits exiting"
                break
            continue
        failed_streak = 0
        print "[PIT_EXP] Extracting pit diff of ", old_commit, " and ", new_commit
        report_score = diff.get_pit_diff(old_commit, new_commit, repo, old_report, new_report, modified_files)
        print "[PIT_EXP] pit diff of ", old_commit, " and ", new_commit, " was:"
        print "[PIT_EXP] ", report_score.str_changed()
        #report_score is an object containing information on the mutation score delta
        output_score(total_modified, total_unmodified, new_commit, report_score, report_dir, output_file)
        new_report = old_report
        new_commit = old_commit
    print "[PIT_EXP] ", total_modified.str_changed()
    print "[PIT_EXP] ", total_unmodified.str_changed()
    total_unmodified.add_changed(total_modified.changed)
    print "[PIT_EXP] TOTAL", total_unmodified.str_changed()
    print "[PIT_EXP] FINISHED"

def process_input():
    """
    Load arguments from the command line, if there is already an output file -> load its results
    REQUIRED:
    pit_filter - the package name of classes/tests under mutation followed by kleene star
    repo_path - the path to the git repository being tested
    OPTIONAL:
    start_commit - the commit from which to start generating pit reports from, defaults to HEAD
    end_commit - the last commit to stop generating pit reports from
    report_dir - path to directory to contain pit xml mutation reports
    output_file - name and path to the file to contain output of experiment results
    EXAMPLE:
    pypy pit_experiment.py org.joda.time* /Users/tim/Code/joda-time HEAD e705d60f83a20366aa50407485f55e9c4b15ff1b /Users/tim/Code/pitReports/joda /Users/tim/Code/pitReports/joda/output.csv 

    """
    #TODO: Add check that start_commit is newer than end_commit
    #TODO: Use argparse module
    usage_string = "pypy pit_experiment.py [pit_filter] [repo_path] [OPTIONAL: start_commit] [OPTIONAL: end_commit] [OPTIONAL:report_dir] [OPTIONAL:output_file]"
    if len(sys.argv) < 3:
        print usage_string
        return
    pit_filter = str(sys.argv[1])
    repo = str(sys.argv[2]) 

    start_commit = "HEAD"
    if len(sys.argv) >= 4:
        start_commit = str(sys.argv[3])

    end_commit = ""
    if len(sys.argv) >= 5:
        end_commit = str(sys.argv[4])

    report_dir = repo+"/pitReports"
    if len(sys.argv) >= 6:
        report_dir = str(sys.argv[5])
    if not os.path.isdir(report_dir):
        if cmd.run_cmd(["mkdir", report_dir]):
            print "[PIT_EXP] Failed to make report_dir ", report_dir
            return

    output_file = report_dir+"/output.csv" 
    if len(sys.argv) >= 7:
        output_file = str(sys.argv[6])
    print report_dir
    main(repo, start_commit, end_commit, report_dir, pit_filter, output_file)
    return

process_input()
