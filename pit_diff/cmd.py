import sys
import os
from subprocess import call, Popen, PIPE

def run_cmd(cmd_arr, stdout=None):
    """
    Helper function for running shell commands
    """
    fd = None
    if stdout is not None:
        fd = open(stdout, "w")#might need wb instead - write in binary
    try:
        status = call(cmd_arr, stdout=fd)
        if status != 0:
            print "Call to ", str(cmd_arr), "terminated with non zero exit code", status
        else:
            #print "Call to ", str(cmd_arr), "successful", status
            pass
    except OSError as e:
        print "Failed to call ", str(cmd_arr), "successfully", e
        print "EXITING"
        sys.exit(1)
    if fd is not None:
        fd.close() 
    return status

def rename_commit(commit, report_path):
    if report_path is None or not report_path:
        print "report_path was invalid"
        return None
    new_report_path = os.path.dirname(report_path)+"/"+commit+".xml"
    status = run_cmd(["mv", report_path, new_report_path])
    if status != 0:
        print "Failed to rename the report path to mutation report ", commit
        sys.exit(1)
    return new_report_path

def get_commit_hash(repo_path, commit):
    """
    Use for getting hash of HEAD or HEAD^ etc
    """
    try:
        p = Popen(["git", "rev-parse", commit], stdout=PIPE)
        output, err = p.communicate()
        rc = p.returncode
    except OSError as e:
        print "Failed to call git rev-parse successfully", e
        print "EXITING"
        sys.exit(1)
    if rc != 0:
        return None
    return output.strip()

def is_repo(repo_path):
    if run_cmd(["git", "-C", repo_path, "status"], "/dev/null") != 0:
        print "Cannot query the Git repo at ", repo_path
        return False
    return True

def run_pit(repo_path, classpath, reportDir, targetClasses, targetTests, src_dir, threads):
    """
    reportDir must terminate in "/"
    """
    status = run_cmd(["java", "-cp", classpath, \
            "org.pitest.mutationtest.commandline.MutationCoverageReport", \
            "--reportDir", reportDir, \
            "--targetClasses", targetClasses, \
            "--targetTests", targetTests, \
            "--sourceDir", src_dir, \
            "--threads", threads, \
            "--outputFormats", "XML", \
            "--timestampedReports", "false"], "/dev/null")
    if status != 0:
        return None
    return reportDir+"mutations.xml"
