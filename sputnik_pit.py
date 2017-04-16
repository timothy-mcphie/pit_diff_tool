#repo is directory that jenkins is in
pit_filter = str(sys.argv[1])
echo "we have ", pit_filter, " as pit_filter"

#Sputnik script calls rev-parse HEAD^ - if fails no prev commits
#extract cp maven
#run pitest
#save mutation report as rev-parse HEAD in repo
#find HEAD^ report - if not found
#git checkout and build with mvn
#extract cp maven
#run pitest
#run git diff HEAD^
#save mutation report as rev-parse HEAD^ in repo
#git diff
#run pit_diff

#return via a pipe
