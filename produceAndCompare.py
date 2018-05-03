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
    mvaidstr = ""
    for id in mvaid:
        mvaidstr += id + " "

    scriptPath = os.path.realpath(__file__)[0:os.path.realpath(__file__).rfind("/")+1]


    for i, relval in enumerate(RelVals):
        print "===================="
        result = subprocess.check_output('python ' + scriptPath +
            'produceTauValTree.py -r ' + relval +
            ' -g ' + globalTags[i] +
            (len(inputfiles)>0) * ' --inputfile ' + inputfiles[i] +
            ' --runtype ' + runtype +
            ' -n ' + str(maxEvents) +
            useRecoJets * ' -u ' +
            ' -s ' + storageSite +
            " -l " + localdir +
            " --tauCollection " + tauCollection +
            (len(outputFileName) > 0) * (" --outputFileName " + outputFileName) +
            (len(mvaid) > 0) * (" --mvaid " + mvaidstr) +
            dryRun * ' --dryRun ' +
            debug * " --debug", shell=True)
        pp.pprint(result)

    commands = []
    commands.append('python ' + scriptPath + 'compare.py -r ' + args.releases + ' -g ' + args.globalTag + ' --runtype ' + runtype + onebin * ' -b'  + ' -p 1' + debug * " --debug")
    commands.append('python ' + scriptPath + 'compare.py -r ' + args.releases + ' -g ' + args.globalTag + ' --runtype ' + runtype + onebin * ' -b'  + ' -p 2' + debug * " --debug")
    commands.append('python ' + scriptPath + 'compare.py -r ' + args.releases + ' -g ' + args.globalTag + ' --runtype ' + runtype + onebin * ' -b'  + ' -p 3' + debug * " --debug")

    for command in commands:
        print "===================="
        print command
        print "===================="
        os.system(command)
