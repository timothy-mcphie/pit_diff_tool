import sys
import os
import csv
from pit_diff import cmd, diff, git_diff, scores
#TODO: Use a logging function instead of prints - can ditch the [FNAME] tag

global pc_commits
pc_commits = ["0e11402b986da1eaf4a96a11c8c6318c51fa47f8",
"115198b9c94bc66c7a659a04d0e2f65959ce9297",
"121dba83e0de318f3b878d6a66f18ab347bad60c",
"159b36e66e6bc64039294c7c04bd147a9888fdd6",
"161aa07d8b2312d9143c7156fa529a4a1e1e9909",
"1918bb005e33c134564c4eea8531cc5fc78880e5",
"1a3337262c7bff09eae06e3b4247f6c7133f8fee",
"1ca637930fccd475b3966db8ec76c3c5ff4b7287",
"276552d5e73525cdd29d9e809659d35f34c5250e",
"27a92653a00658f76f91752f1fd88b93d8dfc7f8",
"2db7aa771a4ee5cd0cae28fe54d7d89fa62da81f",
"2eb1586bf77efcacf701df14ad98d1d6a704a35e",
"2edb7a20f3856723fc715f7c72e10e72ea7df385",
"30e5023265aa76e6c32d3ba43952aac964112ebc",
"32155107dd982360e813d10d0c76f6f7cc2cc7bd",
"39513f9142cb82b84181a11905b3866a49d5a3c0",
"3adcd2103d1be4feca870536e8f7a7549f6d492c",
"45a0337e1d9d23126dcaeff9c0ad96c5b4011957",
"4c818fb356563d9bb0cc01cfde94825aeef33ffa",
"583d96b0895beafad326793c0cd0d273013ff137",
"5d42c95c33cd0504b44fc28be817f278630ee703",
"6180e44ff32c32092c0f4bff6b81236c099ff113",
"6975b0567df3eb618ba30e245bc988f5c22d5bac",
"6ed868d4d0a48a7f8d086c16e3f6c45c5a973a3c",
"71d8237307da002389eba114c1525363b48a485a",
"83e81cb270dd412dba8609bbdf79f3b12a658084",
"8b04e571945fdeefb75a6278c4a53c493054c928",
"8b328d838ebc3d378c42f7e5d2100ae99ffc789b",
"8cb5cbc601f464f77432064c94acf9a00e6704fd",
"943e710f7c65cc6edb58e054bb418595129b64de",
"9843210e5755d2584efd3496d59e50e721187842",
"9acc3e824e2efa2e496df8458d207b5fb5722e6d",
"9cb3de671396635382b6a5052a67a12d752a2b01",
"9dbf8388c5bfa0c7beb15e835b3a5e6fc74ecbf8",
"9e64a3cb81d66793e0147d1b6f4b39a6caa24f62",
"a3b3b74ec6325cd19169fdbaea26f27a96a72fea",
"aafa5bb6a69e2e4e7d885c7591099d0b79998624",
"b1e21c8a6e008439d69785e2244591b664ceb6ee",
"b3fd2560172abe0a7cf78c89b461a50d97413fab",
"ba72be98b6cfad5268ef8208f21c17027e726973",
"c0e4ebfbb0f8c38ef672394015f47fd72ba06cda",
"c193f6556f7cba0fd7efc000653050457f09b9d3",
"c460996e75df489d6bbcb732763c10d01e62516f",
"c61154272699761265a1f2e5282ff1bdaf714b6a",
"db0582a60e34c0a143eeadd943d3e034582bf5f0",
"dd5e51e5b31f36b66431ea6e4b5a2a6bc4dcab34",
"e57282bd9cdde1c4f707dbe111459b4f8e370bde",
"e6cde856d76935ce2ca5323579d2557f5412c774",
"eb5e737f8fc9640b948878ce64f1ab84455d982c",
"f0b18d27f01492af6874baa8415ad17511eb5d4b",
"f30855735a40daaffda15794d7abbc6ab8c699d8",
"f59e419683d69e83bdf58139ed47fb0eeb74563d",
"fe95eebf7d6d34e843679b5b9368d9cf953f5002",
]
pc_commits = dict.fromkeys(pc_commits)


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
    if cmd.run_cmd(["mvn", "-T", "4", "test"]) != 0:
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
    if commit in pc_commits:
        print "[PIT_EXP] report previously generated on PC ", report_path 
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
repo+"/target/classes:"+\
repo+"/target/test-classes:"+\
mvn_classpath 
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
        #new_commit = old_commit

#TODO: Take command line args - if no commit is given, default to HEAD
#repo = "/Users/tim/Code/commons-collections"
#pit_filter="org.apache.commons.collections4.*"
#report_dir = "/Users/tim/Code/pitReports/cc4"
pit_filter="joda.org.time*"
report_dir = "/Users/tim/Code/pitReports/joda"
repo = "/Users/tim/Code/joda-time"
commit = "HEAD"
main(repo, commit, report_dir, pit_filter)
