import os
import argparse
import subprocess

from relValTools import addArguments, getFilesFromEOS, getFilesFromDAS, get_cmssw_version, get_cmssw_version_number, versionToInt, is_above_cmssw_version, runtype_to_sample

import pprint
pp = pprint.PrettyPrinter(indent=4)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    addArguments(parser, compare=True)
    args = parser.parse_args()

    runtype = args.runtype
    globalTags = args.globalTags
    maxEvents = args.maxEvents
    RelVals = args.releases
    useRecoJets = args.useRecoJets
    storageSite = args.storageSite
    tauCollection = args.tauCollection
    onebin = args.onebin
    debug = args.debug
    dryRun = args.dryRun
    inputfiles = args.inputfiles
    outputFileName = args.outputFileName

    localdir = args.localdir
    if len(localdir) > 1 and localdir[-1] is not "/": localdir += "/"

    mvaid = args.mvaid
    mvaidstr = " --mvaid "
    for id in mvaid:
        mvaidstr += id + " "

    scriptPath = os.path.realpath(__file__)[0:os.path.realpath(__file__).rfind("/")+1]

    dd = ""
    if dryRun: dd = " --dryRun "
    if debug: dd += " --debug"



    for i, relval in enumerate(RelVals):
        print "===================="
        inputfile = ""
        if len(inputfiles) > 0:
            inputfile = ' --inputfile ' + inputfiles[i]
        subcommand = 'python ' + scriptPath + 'produceTauValTree.py -r ' + relval + ' -g ' + globalTags[i] + inputfile  + ' --runtype ' + runtype + ' -n ' + str(maxEvents) + useRecoJets * ' -u ' + ' -s ' + storageSite + " -l " + localdir + " --tauCollection " + tauCollection + mvaidstr + dd
        # + (len(outputFileName) > 0) * (" --outputFileName " + outputFileName)

        print subcommand
        result = subprocess.check_output(subcommand, shell=True)
        pp.pprint(result)

    if onebin: onebin = ' -b'
    else: onebin = ''

    globalTagsstr = ""
    for i in globalTags:
        globalTagsstr += str(i) + " "

    releases = ""
    for i in RelVals:
        releases += str(i) + " "

    commands = []
    commands.append('python ' + scriptPath + 'compare.py -r ' + releases + ' -g ' + globalTagsstr + ' --runtype ' + str(runtype) + onebin  + ' -p 1' + dd)
    commands.append('python ' + scriptPath + 'compare.py -r ' + releases + ' -g ' + globalTagsstr + ' --runtype ' + str(runtype) + onebin  + ' -p 2' + dd)
    commands.append('python ' + scriptPath + 'compare.py -r ' + releases + ' -g ' + globalTagsstr + ' --runtype ' + str(runtype) + onebin  + ' -p 3' + dd)

    for command in commands:
        print "===================="
        print command
        print "===================="
        os.system(command)
