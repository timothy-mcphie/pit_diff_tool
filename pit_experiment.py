import sys
import os
import csv
from pit_diff import cmd, diff, git_diff, scores as s
#TODO: Use a logging function instead of prints - can ditch the [FNAME] tag - output status of cmds to file

global MAX_CONSECUTIVE_BUILD_FAILS
MAX_CONSECUTIVE_BUILD_FAILS = 15

def output_score(score, report_dir): 
    """
    output_file = report_dir+"/output.csv"
    delta = diff.parse_report_score(score)
    with open output_file as f:
        for mut in score:
            print "[PIT_EXP] CHANGED ", str(d)
    """

def copy_build_files(repo):
    build_files = repo+"/../build_files-commons-collections"
    print "[PIT_EXP] Copying files from ", build_files, " to ", repo
    #if cmd.run_cmd(["mkdir", repo+"/lib"]):
    #    print "[PIT_EXP] Failed to make lib dir for dependencies"
    #    return False
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
    #TODO: Move away from hardcoded
    print "[PIT_EXP] repo is ", repo
    try:
        os.chdir(repo)
    except OSError as e:
        print "[PIT_EXP] Could not cd to repo ", repo, " ", e
        sys.exit(1)
    #if cmd.run_cmd(["mvn", "-T", "4", "test"]) != 0:
    if cmd.run_cmd(["mvn", "test"]) != 0: #not thread safe
        return False
    return True

def get_mvn_classpath(repo):
    
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
        print "[PIT_EXP] Failed to checkout commit ", commit, " cannot attempt to build"
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

#repo+"/target/classes:"+\
#repo+"/target/test-classes:"+\
#mvn_classpath
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

def main(repo, commit, report_dir, pit_filter):
    """
    Iterate backwards over commits in a repo running pit
    """ 
    #TODO: Switch to iterating forwards, checkout the initial commit and use PIT incremental analysis
    if not cmd.is_repo(repo):
        print "[PIT_EXP] This is not a valid git repository ", repo
        sys.exit(1) 
    commit = cmd.get_commit_hash(repo, commit)
    if commit is None:
        print "[PIT_EXP] Failed to get hash of supplied commit ", commit
        sys.exit(0)
    new_report = get_pit_report(repo, commit, report_dir, pit_filter)
    new_commit = old_commit = commit #old_commit is the historically older snapshot of the project

    failed_streak = 0
    while True:
        old_commit = cmd.get_commit_hash(repo, old_commit+"^")
        #get parent commit
        if old_commit == "d9f33d8ae9b288c5021fd688ff296c0d053a644e" or old_commit is None:
            old_commit = "634066471f2941eddfcca3ed2a62c9d254cabccb"
            #print "[PIT_EXP] End of commit history, exiting"
            #sys.exit(0)
        print "[PIT_EXP] Parsing diff of commits ", old_commit, " to ", new_commit
        modified_files = git_diff.process_git_info(old_commit, new_commit, repo)
        #TODO: Show what files are modified
        #if not modified_files:
        #    print "[PIT_EXP] Skipping commits with no java source files edited"
        #    #if commit has no src code edits the old_report mutation score won't change
        #    #new_report will stay the same commit arguably the most recent version will be most stable
        #    continue
        old_report = get_pit_report(repo, old_commit, report_dir, pit_filter)
        if old_report is None:
            #TODO:If build or pit failed and there are child commits with non source edits that were skipped
            #Try these children - could have build file edits which fix the build
            failed_streak += 1
            if failed_streak >= MAX_CONSECUTIVE_BUILD_FAILS:
                print "[PIT_EXP] Couldn't build ", MAX_CONSECUTIVE_BUILD_FAILS, " consecutive commits exiting"
                sys.exit(1)
            continue
        failed_streak = 0
        #print "[PIT_EXP] Extracting diff of ", old_commit, " and ", new_commit
        #delta = diff.get_pit_diff(old_commit, new_commit, repo, old_report, new_report, modified_files)
        #output_score(delta, report_dir)
        #new_report = old_report
        new_commit = old_commit

#TODO: Take command line args - if no commit is given, default to HEAD
#repo = "/Users/tim/Code/commons-collections"
#pit_filter="org.apache.commons.collections4.*"
#report_dir = "/Users/tim/Code/pitReports/cc4"
pit_filter="org.joda.time*"
report_dir = "/Users/tim/Code/pitReports/joda"
repo = "/Users/tim/Code/joda-time"
commit = "HEAD"
main(repo, commit, report_dir, pit_filter)

