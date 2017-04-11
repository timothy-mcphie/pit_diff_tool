from pit_diff import cmd, diff, git_diff
import sys

def output_score(score): 
    delta = diff.parse_report_score(score)
    for mut in score:
        print "[PIT_EXP] CHANGED ", str(d)

def checkout_commit(repo_path, commit):
    if cmd.run_cmd(["git", "-C", repo_path, "checkout", commit], "/dev/null") != 0:
        print "[PIT_EXP] Cannot check out commit ", commit, " in repo ", repo_path
        return False
    return True 

def ant_compile(repo_path):
    if cmd.run_cmd(["ant", "-f", repo_path+"build.xml", "compile", "compile.tests"], "/dev/null") != 0:
        #Is -Dbasedir=repo_path needed?
        return False
    return True

def get_pit_report(commit, repo_path):
    """
    Runs pit on a given git repository, returns a path to a uniquely named mutation report
    Edit classpath, src_dir, targetClasses, reportDir, to match those of project.
    """
    classpath = "/Users/tim/Code/commons-collections/lib/pitest-command-line-1.1.11.jar:\
            /Users/tim/Code/commons-collections/lib/pitest-1.1.11.jar:\
            /Users/tim/Code/commons-collections/lib/junit-4.11.jar:\
            /Users/tim/Code/commons-collections/lib/easymock-3.2.jar:\
            /Users/tim/Code/commons-collections/lib/hamcrest-core-1.3.jar:\
            /Users/tim/Code/commons-collections/target/classes:target/tests"
    reportDir = "~/pitReports/"
    targetClasses = targetTests = "org.apache.commons.collections4.*"
    src_dir = "/Users/tim/Code/commons-collections/src/"
    threads = "4"
    report_path = cmd.run_pit(repo_path, classpath, reportDir, targetClasses, targetTests, src_dir, threads)
    if report_path is None:
        print "[PIT_EXP] Pitest failed to run and generate a report on ", commit
        return None
    return cmd.rename_report(report_path, commit)

def main(commit, repo_path):
    """
    Iterate backwards over commits in a repo running pit
    """ 
    if not cmd.is_repo(repo_path):
        print "[PIT_EXP] This is not a valid git repository ", repo_path
        sys.exit(1)

    old_commit = new_commit = cmd.get_commit_hash(repo_path, commit)
    new_report = get_pit_report(repo_path, new_commit)
    """
    NB: old_commit is the historically older snapshot of the project - this bit is confusing lol
    """
    streak = 0
    while True:
        old_commit = cmd.get_commit_hash(repo, old_commit+"^")
        if old_commit is None:
            print "[PIT_EXP] End of commit history, exiting"
        print "[PIT_EXP] Parsing diff of commits ", old_commit, " to ", new_commit
        modified_files = diff.process_git_info(old_commit, new_commit, repo_path)
        if not modified_files:
            print "[PIT_EXP] Skipping commits with no java source files edited"
            #NB if source code is unedited in commits, new_report isn't updated, mutation score won't change            #if code hasn't changed, arguably the most recent version will be most stable
            continue

        if not checkout_commit(repo_path, commit): 
            print "[PIT_EXP] Failed to checkout commit ", commit, " cannot attempt to build"
            sys.exit(1)

        if not cmd.ant_compile(repo_path):
            print "[PIT_EXP] Build of ", commit, " failed - skipping this snapshot"
            streak += 1
            if streak > 10:
                print "[PIT_EXP] Couldn't build 10 consecutive commits exiting"
                sys.exit(1)
            continue
        streak = 0
        print "[PIT_EXP] Running pit on ", old_commit
        old_report = get_pit_report(old_commit, repo_path) 
        print "[PIT_EXP] Extracting diff of ", old_commit, " and ", new_commit
        delta = diff.get_pit_diff(old_commit, new_commit, repo_path, old_rep, new_rep, modified_files)
        new_report = old_report
        new_commit = old_commit

main("HEAD", "/Users/tim/Code/commons-collections/")
