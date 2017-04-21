import sys
import os
import csv
from pit_diff import cmd, diff, git_diff, scores as s
import numpy
import scipy
import scipy.stats
#import matplotlib
#matplotlib.use('Agg')
#import matplotlib.pyplot as plt
##TODO: Use a logging function instead of prints - can ditch the [FNAME] tag - output status of cmds to file
#
#
def create_stats(data):
    return [numpy.sum(data), numpy.mean(data), numpy.median(data), numpy.std(data), numpy.nanmin(data), numpy.nanmax(data), scipy.stats.skew(data)]
#
#    try:
#        nbins = int(options.bins)
#    except ValueError:
#        nbins = 50
#
#    fig = plt.figure()
#    plt.hist(data, bins=nbins)
#    fig.savefig("hist.png")
#    
#    # cdf
#    fig1 = plt.figure()
#    [y, x0, bs, xtra] = scipy.stats.cumfreq(data, nbins) # bin values, lowerlimit, binsize, extrapoints 
#    scale = 1.0/y[-1]
#    y *= scale
#    x = numpy.linspace(x0, x0 + nbins*bs, nbins)
#    plt.plot(x, y)
#    fig1.savefig("cdf.png")
#

def parse_score(out_file):
    
    #variables = 
    total_nc_sur  = []
    total_nc_k    = []
    total_sur_nc  = []
    total_sur_k   = []
    total_k_nc    = []
    total_k_sur   = []
    file_unmod_nc_sur   = []
    file_unmod_nc_k     = []
    file_unmod_sur_nc   = []
    file_unmod_sur_k    = []
    file_unmod_k_nc     = []
    file_unmod_k_sur    = []
    class_unmod_nc_sur  = []
    class_unmod_nc_k    = []
    class_unmod_sur_nc  = []
    class_unmod_sur_k   = []
    class_unmod_k_nc    = []
    class_unmod_k_sur   = []
    method_unmod_nc_sur = []
    method_unmod_nc_k   = []
    method_unmod_sur_nc = []
    method_unmod_sur_k  = []
    method_unmod_k_nc   = []
    method_unmod_k_sur  = []
    file_mod_nc_sur     = []
    file_mod_nc_k       = []
    file_mod_sur_nc     = []
    file_mod_sur_k      = []
    file_mod_k_nc       = []
    file_mod_k_sur      = []
    class_mod_nc_sur    = []
    class_mod_nc_k      = []
    class_mod_sur_nc    = []
    class_mod_sur_k     = []
    class_mod_k_nc      = []
    class_mod_k_sur     = []
    method_mod_nc_sur   = []
    method_mod_nc_k     = []
    method_mod_sur_nc   = []
    method_mod_sur_k    = []
    method_mod_k_nc     = []
    method_mod_k_sur    = []

    with open(output_file, "r") as f:
        reader = csv.reader(f, delimiter=",")
        next(reader, None)
        for row in reader: 
            total_nc_sur.append(int(row[2])+int(row[11]))
            total_nc_k.append(int(row[3])+int(row[12]))
            total_sur_nc.append(int(row[4])+int(row[13]))
            total_sur_k.append(int(row[6])+int(row[15]))
            total_k_nc.append(int(row[7])+int(row[16]))
            total_k_sur.append(int(row[8])+int(row[17]))
            file_mod_nc_sur.append(int(row[2]))
            file_mod_nc_k.append(int(row[3]))
            file_mod_sur_nc.append(int(row[4]))
            file_mod_sur_k.append(int(row[6]))
            file_mod_k_nc.append(int(row[7]))
            file_mod_k_sur.append(int(row[8]))
            file_unmod_nc_sur.append(int(row[11]))
            file_unmod_nc_k.append(int(row[12]))
            file_unmod_sur_nc.append(int(row[13]))
            file_unmod_sur_k.append(int(row[15]))
            file_unmod_k_nc.append(int(row[16]))
            file_unmod_k_sur.append(int(row[17]))
            class_mod_nc_sur.append(int(row[20]))
            class_mod_nc_k.append(int(row[21]))
            class_mod_sur_nc.append(int(row[22]))
            class_mod_sur_k.append(int(row[24]))
            class_mod_k_nc.append(int(row[25]))
            class_mod_k_sur.append(int(row[26]))
            class_unmod_nc_sur.append(int(row[29]))
            class_unmod_nc_k.append(int(row[30]))
            class_unmod_sur_nc.append(int(row[31]))
            class_unmod_sur_k.append(int(row[33]))
            class_unmod_k_nc.append(int(row[34]))
            class_unmod_k_sur.append(int(row[35]))
            method_mod_nc_sur.append(int(row[38]))
            method_mod_nc_k.append(int(row[39]))
            method_mod_sur_nc.append(int(row[40]))
            method_mod_sur_k.append(int(row[42]))
            method_mod_k_nc.append(int(row[43]))
            method_mod_k_sur.append(int(row[44]))
            method_unmod_nc_sur.append(int(row[47]))
            method_unmod_nc_k.append(int(row[48]))
            method_unmod_sur_nc.append(int(row[49]))
            method_unmod_sur_k.append(int(row[51]))
            method_unmod_k_nc.append(int(row[52]))
            method_unmod_k_sur.append(int(row[53]))

    with open("cc4.csv", "w") as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerow(["variable ", "sum", "mean", "median", "standard deviation", "min", "max", "skew"])
        writer.writerow(["total_nc_sur"]+  create_stats(total_nc_sur))
        writer.writerow(["total_nc_k"]+  create_stats(total_nc_k)     )
        writer.writerow(["total_sur_nc"]+  create_stats(total_sur_nc)   )
        writer.writerow(["total_sur_k"]+  create_stats(total_sur_k)    )
        writer.writerow(["total_k_nc"]+  create_stats(total_k_nc)     )
        writer.writerow(["total_k_sur"]+  create_stats(total_k_sur)    )
        writer.writerow(["file_unmod_nc_sur"]+  create_stats(file_unmod_nc_sur))
        writer.writerow(["file_unmod_nc_k"]+  create_stats(file_unmod_nc_k)     )
        writer.writerow(["file_unmod_sur_nc"]+  create_stats(file_unmod_sur_nc)   )
        writer.writerow(["file_unmod_sur_k"]+  create_stats(file_unmod_sur_k)    )
        writer.writerow(["file_unmod_k_nc"]+  create_stats(file_unmod_k_nc)     )
        writer.writerow(["file_unmod_k_sur"]+  create_stats(file_unmod_k_sur)    )
        writer.writerow(["class_unmod_nc_sur"]+  create_stats(class_unmod_nc_sur)  )
        writer.writerow(["class_unmod_nc_k"]+  create_stats(class_unmod_nc_k)    )
        writer.writerow(["class_unmod_sur_nc"]+  create_stats(class_unmod_sur_nc)  )
        writer.writerow(["class_unmod_sur_k"]+  create_stats(class_unmod_sur_k)   )
        writer.writerow(["class_unmod_k_nc"]+  create_stats(class_unmod_k_nc)    )
        writer.writerow(["class_unmod_k_sur"]+  create_stats(class_unmod_k_sur)   )
        writer.writerow(["method_unmod_nc_sur"]+  create_stats(method_unmod_nc_sur) )
        writer.writerow(["method_unmod_nc_k"]+  create_stats(method_unmod_nc_k)   )
        writer.writerow(["method_unmod_sur_nc"]+  create_stats(method_unmod_sur_nc) )
        writer.writerow(["method_unmod_sur_k"]+  create_stats(method_unmod_sur_k)  )
        writer.writerow(["method_unmod_k_nc"]+  create_stats(method_unmod_k_nc)   )
        writer.writerow(["method_unmod_k_sur"]+  create_stats(method_unmod_k_sur)  )
        writer.writerow(["file_mod_nc_sur"]+  create_stats(file_mod_nc_sur)    )
        writer.writerow(["file_mod_nc_k"]+  create_stats(file_mod_nc_k)    )
        writer.writerow(["file_mod_sur_nc"]+  create_stats(file_mod_sur_nc)    )
        writer.writerow(["file_mod_sur_k"]+  create_stats(file_mod_sur_k)    )
        writer.writerow(["file_mod_k_nc"]+  create_stats(file_mod_k_nc)    )
        writer.writerow(["file_mod_k_sur"]+  create_stats(file_mod_k_sur)    )
        writer.writerow(["class_mod_nc_sur"]+  create_stats(class_mod_nc_sur)    )
        writer.writerow(["class_mod_nc_k"]+  create_stats(class_mod_nc_k)    )
        writer.writerow(["class_mod_sur_nc"]+  create_stats(class_mod_sur_nc)    )
        writer.writerow(["class_mod_sur_k"]+  create_stats(class_mod_sur_k)    )
        writer.writerow(["class_mod_k_nc"]+  create_stats(class_mod_k_nc)    )
        writer.writerow(["class_mod_k_sur"]+  create_stats(class_mod_k_sur)    )
        writer.writerow(["method_mod_nc_sur"]+  create_stats(method_mod_nc_sur)   )
        writer.writerow(["method_mod_nc_k"]+  create_stats(method_mod_nc_k)    )
        writer.writerow(["method_mod_sur_nc"]+  create_stats(method_mod_sur_nc)   )
        writer.writerow(["method_mod_sur_k"]+  create_stats(method_mod_sur_k)    )
        writer.writerow(["method_mod_k_nc"]+  create_stats(method_mod_k_nc)    )
        writer.writerow(["method_mod_k_sur"]+  create_stats(method_mod_k_sur)    )


            
def get_header_changed(level, mod):
    l = ["nc_nc" , "nc_sur", "nc_k", "sur_nc" , "sur_sur", "sur_k", "k_nc" , "k_sur", "k_k"]
    return [level+" "+mod+" "+item for item in l]

def get_header():
    return ["commit"] + get_header_changed("file", "mod") + get_header_changed("file", "unmod") + get_header_changed("class", "mod") + get_header_changed("class", "unmod") + get_header_changed("method", "mod") + get_header_changed("method", "unmod")

def output_score(rows, output_file):
    """
    Output and append to a csv file the change a new_commit introduces to the mutation score
    """
    #TODO: add headers to csv

    #Use letters to replace 
    with open(output_file, "a+") as f:
        w = csv.writer(f, delimiter=",")
        w.writerow(get_header())
        for row in rows:
            w.writerow(row)

def main(repo, start_commit, end_commit, report_dir, pit_filter, output_file):
    """
    Iterate backwards over commits in a repo running pit
    """ 
    start_commit = cmd.get_commit_hash(repo, start_commit) 
    new_report = report_dir+"/"+start_commit+".xml" 
    new_commit = old_commit = start_commit
    missing_reps = 0
    fdc = 0
    reports = 1
    total_parsed = 0
    rows = []
    total_modified = s.Mutation_score("total_modified", None)
    total_unmodified = s.Mutation_score("total_unmodified", None) 
    while True:
        if reports >= 810:
                break
        old_commit = cmd.get_commit_hash(repo, old_commit+"^")
        if old_commit is None or old_commit == end_commit:
            print "[PIT_EXP] End of commit history, exiting"
            break
        try:
            modified_files = git_diff.process_git_info(old_commit, new_commit, repo)
        except:
            fdc += 1
            print "Couldn't parse diff"
            new_commit = old_commit
            continue
        if fdc > 1:
            print "[PIT_EXP] parsed git diff successfully after ", fdc, " failed diffs in a row - missing those reports"
        fdc = 0
        old_report = report_dir+"/"+old_commit+".xml" 
        if not os.path.isfile(old_report):
            print "[PIT_EXP] no file exists ", old_commit
            missing_reps += 1
            continue
        else:
            reports += 1
        if missing_reps > 0:
            print "gap between reports was ", missing_reps
        missing_reps = 0
        report_score = diff.get_pit_diff(old_commit, new_commit, repo, old_report, new_report, modified_files)
        (modified, unmodified) = diff.parse_file_score(report_score)
        (modified_class, unmodified_class, modified_method, unmodified_method) = diff.parse_class_method_score(report_score)
        print "[PIT_EXP] pit diffed successfuly ", old_commit, " to ", new_commit, " there were ", report_score.total_changed(), " changes"
        rows.append([new_commit]+modified.changed+unmodified.changed+modified_class.changed+unmodified_class.changed+modified_method.changed+unmodified_method.changed)
        total_parsed += 1
        new_report = old_report
        new_commit = old_commit
    output_score(rows, output_file)
    print "Total parse ", total_parsed

repo = "/Users/tim/Code/commons-collections"
start_commit = "HEAD"
end_commit = "aa048da715d8605f1ecc66d60ddb8d0c17323456" 
report_dir = "/Users/tim/Code/pitReports/cc4"
output_file = "output.csv"
#main(repo, start_commit, end_commit, report_dir, None, output_file)
parse_score(output_file)
