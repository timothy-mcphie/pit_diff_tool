import sys
import os
from subprocess import call, Popen, PIPE

def run_cmd(cmd_arr, stdout=None, stderr=None):
    """
    Helper function for running shell commands
    """
    #stderr = stdout = "/dev/null"
    fd2 = fd = None
    if stdout is not None:
        fd = open(stdout, "w")#might need wb instead - write in binary
    if stderr is not None:
        fd2 = open(stderr, "w")
    try:
        status = call(cmd_arr, stdout=fd, stderr=fd2)
        if status != 0:
            print "[CMD] Call to ", str(cmd_arr), "terminated with non zero exit code", status
        else:
            #print "[CMD] Call to ", str(cmd_arr), "successful", status
            pass
    except OSError as e:
        print "[CMD] Failed to call ", str(cmd_arr), "successfully", e
        print "[CMD] EXITING"
        sys.exit(1)
    if fd is not None:
        fd.close() 
    return status

def get_report_name(report_dir, commit):
    report_path = report_dir+"/"+commit+".xml"
    print "[CMD] report path is", report_path
    return report_path

def rename_file(old_path, new_path):
    if old_path is None or not old_path:
        print "[CMD] old report_path was invalid ", old_path
        return None
    elif new_path is None or not new_path:
        print "[CMD] new report_path was invalid ", new_path
        return None
    status = run_cmd(["mv", old_path, new_path])
    if status != 0:
        print "[CMD] Failed to rename the ", old_path, " to ", new_path
        sys.exit(1)
    print "[CMD] Rename successful from ", old_path, " to ", new_path
    return new_path

def get_commit_hash(repo, commit):
    """
    Use for getting hash of HEAD or HEAD^ etc
    """
    try:
        p = Popen(["git", "-C", repo, "rev-parse", commit], stdout=PIPE, stderr=PIPE)
        output, err = p.communicate()
        rc = p.returncode
    except OSError as e:
        print "[CMD] Failed to call git rev-parse successfully", e
        print "[CMD] EXITING"
        sys.exit(1)
    if rc != 0:
        print "[CMD] Unsuccessful call to rev-parse on commit ", commit, " in repo ", repo
        print "[CMD] Error ", err
        return None
    output = output.strip()
    print "[CMD] commit hash is ", output
    return output

def checkout_commit(repo, commit):
    if run_cmd(["git", "-C", repo, "checkout", commit, "-f"]) != 0:
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
    if run_cmd(["mvn", "test"]) != 0:
        #can do multi threading with -T x, where x is an integer, however some builds aren't threadsafe - causes failures
        return False
    return True

def get_mvn_classpath(repo):
    """
    Extract the classpath from the maven build - pit searches this for classes to mutate
    """
    cp_file = repo+"/cp.txt"
    if run_cmd(["mvn", "dependency:build-classpath", "-Dmdep.outputFile="+cp_file]) != 0:
        print "[PIT_EXP] Failed to extract classpath from maven"
        return None
    cp = None
    try:
        with open(cp_file, "r") as f:
            cp = f.readline()
    except:
        print "[PIT_EXP]couldn't perform open on ", cp_file
        return None
    if run_cmd(["rm", cp_file]) != 0: 
        print "[PIT_EXP] Failed to delete remaining classpath file from maven"
        return None
    return cp.strip()

def copy_build_files(repo, lib_dir):
    if not os.path.isdir(repo+"/lib"):
        print "[PIT_EXP] making lib dir in ", repo
        if run_cmd(["mkdir", repo+"/lib"]):
            print "[PIT_EXP] Failed to make lib dir for dependencies"
            return False
    print "[PIT_EXP] Copying files from ", lib_dir, " to ", repo
    if run_cmd(["cp", lib_dir+"/junit-4.11.jar", lib_dir+"/pitest-command-line-1.1.11.jar", lib_dir+"/pitest-1.1.11.jar", repo+"/lib"]):
        print "[PIT_EXP] Failed to copy pit dependencies to lib"
        return False
    return True 

def get_pit_report(repo, commit, report_dir, pit_filter, lib_dir):
    """
    Checkout, build and generate pit report for a repo snapshot
    """
    report_path = get_report_name(report_dir, commit)
    if os.path.isfile(report_path):
        print "[PIT_EXP] Found report previously generated at ", report_path
        return report_path
    if not checkout_commit(repo, commit): 
        print "[PIT_EXP] Failed to checkout commit ", commit, " exiting"
        sys.exit(1) 
    if not copy_build_files(repo, lib_dir):
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
    print "[PIT_EXP] classpath from maven is ", mvn_classpath
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

    if run_pit(repo, classpath, report_dir, target_classes, target_tests, src_dir, threads) is None:
        print "[PIT_EXP] Pit report of ", commit, " failed to generate"
        return None
    report_path = rename_file(report_dir+"/mutations.xml", report_path)
    if report_path is None:
        print "[PIT_EXP] Failed to complete rename"
    return report_path

def is_repo(repo):
    if run_cmd(["git", "-C", repo, "status"]) != 0:
        print "[CMD] Cannot query the Git repo at ", repo
        return False
    return True

def run_pit(repo, classpath, report_dir, target_classes, target_tests, src_dir, threads):
    """
    Runs pit on a given git repository, returns a path to a uniquely named mutation report
    Edit classpath, src_dir, targetClasses, reportDir, to match those of project.
    """
    status = run_cmd(["java", "-cp", classpath, \
            "org.pitest.mutationtest.commandline.MutationCoverageReport", \
            "--reportDir", report_dir, \
            "--targetClasses", target_classes, \
            "--targetTests", target_tests, \
            "--sourceDir", src_dir, \
            "--threads", threads, \
            "--outputFormats", "XML", \
            "--timestampedReports", "false"])
    if status != 0:
        return None
    return report_dir+"/mutations.xml"

