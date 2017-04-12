import sys
from pit_diff import cmd, diff, git_diff, scores

def output_score(score): 
    delta = diff.parse_report_score(score)
    for mut in score:
        print "[PIT_EXP] CHANGED ", str(d)

def checkout_commit(repo, commit):
    if cmd.run_cmd(["git", "-C", repo, "checkout", commit], "/dev/null") != 0:
        print "[PIT_EXP] Cannot check out commit ", commit, " in repo ", repo
        return False
    return True 

def ant_compile(repo):
    #TODO: Move away from hardcoded
    if cmd.run_cmd(["ant", "-f", repo+"build.xml", "compile", "compile.tests"], "/dev/null") != 0:
        #Is -Dbasedir=repo needed?
        return False
    return True


def get_pit_report(repo, commit):
    """
    Checkout, build and generate pit report for a repo snapshot
    """
    if not checkout_commit(repo, commit): 
        print "[PIT_EXP] Failed to checkout commit ", commit, " cannot attempt to build"
        sys.exit(1) 
    if not ant_compile(repo):
        print "[PIT_EXP] Build of ", commit, " failed - skipping this snapshot"
        return None

    print "[PIT_EXP] Running pit on ", commit
    classpath = "/Users/tim/Code/commons-collections/lib/pitest-command-line-1.1.11.jar:\
/Users/tim/Code/commons-collections/lib/pitest-1.1.11.jar:\
/Users/tim/Code/commons-collections/lib/junit-4.11.jar:\
/Users/tim/Code/commons-collections/lib/easymock-3.2.jar:\
/Users/tim/Code/commons-collections/lib/hamcrest-core-1.3.jar:\
/Users/tim/Code/commons-collections/target/classes:target/tests"
    report_dir = "/Users/tim/Google Drive/University/University Work - 4th Year/COMPM091 Final Year Individual Project/Code/pit_tool/pitReports/"
    target_classes = target_tests = "org.apache.commons.collections4.*"
    src_dir = "/Users/tim/Code/commons-collections/src/"
    threads = "4"
    report_path = cmd.run_pit(repo, classpath, report_dir, target_classes, target_tests, src_dir, threads)
    if report_path is None:
        print "[PIT_EXP] Pit report of ", commit, " failed to generate"
        return None
    report_path = cmd.rename_report(report_path, commit)
    print "[PIT_EXP] Report is at ", report_path
    return report_path


def main(commit, repo):
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
    new_report = get_pit_report(repo, commit)
    new_commit = old_commit = commit #old_commit is the historically older snapshot of the project
    failed_streak = 0
    while True:
        old_commit = cmd.get_commit_hash(repo, old_commit+"^")
        if old_commit is None:
            print "[PIT_EXP] End of commit history, exiting"
            sys.exit(0)
        print "[PIT_EXP] Parsing diff of commits ", old_commit, " to ", new_commit
        modified_files = git_diff.process_git_info(old_commit, new_commit, repo)
        if not modified_files:
            print "[PIT_EXP] Skipping commits with no java source files edited"
            #if source code is unedited in commits, new_report isn't updated, mutation score won't change
            #if code hasn't changed, arguably the most recent version will be most stable
            continue
        old_report = get_pit_report(repo, old_commit)
        if old_report is None:
            #build or pit report failed
            failed_streak += 1
            if failed_streak >= 10:
                print "[PIT_EXP] Couldn't build 10 consecutive commits exiting"
                sys.exit(1)
            continue
        failed_streak = 0
        print "[PIT_EXP] Extracting diff of ", old_commit, " and ", new_commit
        delta = diff.get_pit_diff(old_commit, new_commit, repo, old_report, new_report, modified_files)
        output_score(delta)
        new_report = old_report
        new_commit = old_commit

#TODO: Take command line args
main("HEAD", "/Users/tim/Code/commons-collections/")
