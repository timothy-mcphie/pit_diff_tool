import sys
import os
import csv
from pit_diff import cmd, diff, git_diff, scores
#TODO: Use a logging function instead of prints - can ditch the [FNAME] tag

def output_score(score, report_dir): 
    output_file = report_dir+"/output.csv"
    delta = diff.parse_report_score(score)
    with open output_file as f:
        for mut in score:
            print "[PIT_EXP] CHANGED ", str(d)

def checkout_commit(repo, commit):
    if cmd.run_cmd(["git", "-C", repo, "checkout", commit], "/dev/null") != 0:
        print "[PIT_EXP] Cannot check out commit ", commit, " in repo ", repo
        return False
    return True 

def ant_compile(repo):
    #TODO: Move away from hardcoded
    print "[PIT_EXP] repo is ", repo
    try:
        os.chdir(repo)
    except OSError as e:
        print "[PIT_EXP] Could not cd to repo ", repo, " ", e
        sys.exit(1)
    if cmd.run_cmd(["ant", "test"], "/dev/null") != 0:
        return False
    return True

def get_pit_report(repo, commit, report_dir):
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
    if not ant_compile(repo):
        print "[PIT_EXP] Build of ", commit, " failed - skipping this snapshot"
        return None

    print "[PIT_EXP] Running pit on ", commit
    #TODO: What if the classpath changes - build structure/dependencies change? Extract from ant/mvn?
    classpath = "/Users/tim/Code/commons-collections/lib/pitest-command-line-1.1.11.jar:\
/Users/tim/Code/commons-collections/lib/pitest-1.1.11.jar:\
/Users/tim/Code/commons-collections/lib/junit-4.11.jar:\
/Users/tim/Code/commons-collections/lib/easymock-3.2.jar:\
/Users/tim/Code/commons-collections/lib/hamcrest-core-1.3.jar:\
/Users/tim/Code/commons-collections/target/classes:\
/Users/tim/Code/commons-collections/target/tests"
    target_classes = target_tests = "org.apache.commons.collections4.*"
    src_dir = "/Users/tim/Code/commons-collections/src/"
    threads = "4"
    report_path = cmd.run_pit(repo, classpath, report_dir, target_classes, target_tests, src_dir, threads)
    if report_path is None:
        print "[PIT_EXP] Pit report of ", commit, " failed to generate"
        return None
    report_path = cmd.rename_report(report_dir+"/mutations.xml", report_path)
    if report_path is None:
        print "[PIT_EXP] Failed to complete rename"
    return report_path


def main(repo, commit, report_dir):
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
    new_report = get_pit_report(repo, commit, report_dir)
    new_commit = old_commit = commit #old_commit is the historically older snapshot of the project

    failed_streak = 0
    while True:
        old_commit = cmd.get_commit_hash(repo, old_commit+"^")
        #get parent commit
        if old_commit is None:
            print "[PIT_EXP] End of commit history, exiting"
            sys.exit(0)
        print "[PIT_EXP] Parsing diff of commits ", old_commit, " to ", new_commit
        modified_files = git_diff.process_git_info(old_commit, new_commit, repo)
        if not modified_files:
            print "[PIT_EXP] Skipping commits with no java source files edited"
            #if commit has no src code edits the old_report mutation score won't change
            #new_report will stay the same commit arguably the most recent version will be most stable
            continue
        old_report = get_pit_report(repo, old_commit, report_dir)
        if old_report is None:
            #TODO:If build or pit failed and there are child commits with non source edits that were skipped
            #Try these children - could have build file edits which fix the build
            failed_streak += 1
            if failed_streak >= 10:
                print "[PIT_EXP] Couldn't build 10 consecutive commits exiting"
                sys.exit(1)
            continue
        failed_streak = 0
        print "[PIT_EXP] Extracting diff of ", old_commit, " and ", new_commit
        delta = diff.get_pit_diff(old_commit, new_commit, repo, old_report, new_report, modified_files)
        output_score(delta, report_dir)
        new_report = old_report
        new_commit = old_commit

#TODO: Take command line args
#TODO: Default to taking out HEAD of trunk
repo = "/Users/tim/Code/commons-collections/"
commit = "HEAD"
report_dir = "/Users/tim/Google Drive/University/University Work - 4th Year/COMPM091 Final Year Individual Project/Code/pit_tool/pitReports/"
main(repo, commit, report_dir)
