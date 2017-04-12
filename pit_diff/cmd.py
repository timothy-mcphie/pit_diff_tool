import sys
import os
from subprocess import call, Popen, PIPE

def run_cmd(cmd_arr, stdout=None, stderr=None):
    """
    Helper function for running shell commands
    """
    fd2 = fd = None
    if stdout is not None:
        fd = open(stdout, "w")#might need wb instead - write in binary
    if stderr is not None:
        fd2 = open(stderr, "w")#might need wb instead - write in binary
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

def rename_report(report_path, commit):
    if report_path is None or not report_path:
        print "[CMD] report_path was invalid"
        return None
    new_report_path = os.path.dirname(report_path)+"/"+commit+".xml"
    print "[CMD] new report path is", new_report_path
    status = run_cmd(["mv", report_path, new_report_path])
    if status != 0:
        print "[CMD] Failed to rename the report path to mutation report ", commit
        sys.exit(1)
    return new_report_path

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

def is_repo(repo):
    if run_cmd(["git", "-C", repo, "status"], "/dev/null") != 0:
        print "[CMD] Cannot query the Git repo at ", repo
        return False
    return True

def run_pit(repo, classpath, report_dir, target_classes, target_tests, src_dir, threads):
    """
    Runs pit on a given git repository, returns a path to a uniquely named mutation report
    Edit classpath, src_dir, targetClasses, reportDir, to match those of project.
    reportDir must terminate in "/"
    """
    status = run_cmd(["java", "-cp", classpath, \
            "org.pitest.mutationtest.commandline.MutationCoverageReport", \
            "--reportDir", report_dir, \
            "--targetClasses", target_classes, \
            "--targetTests", target_tests, \
            "--sourceDir", src_dir, \
            "--threads", threads, \
            "--outputFormats", "XML", \
            "--timestampedReports", "false"], "/dev/null")
    if status != 0:
        return None
    return report_dir+"mutations.xml"

