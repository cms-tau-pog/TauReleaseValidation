import os
import argparse
import subprocess
import pprint
import sys

from relValTools import addArguments
#import Validation.RecoTau.webplotting as webplotting


pp = pprint.PrettyPrinter(indent=4)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    addArguments(parser, produce=True, compare=True)
    args = parser.parse_args()

    skipProduce = sys.argv[-1]
    skipProduceTauValTree = False
    if skipProduce == '--skip' :
        skipProduceTauValTree = True


    runtype = args.runtype
    globalTags = args.globalTags
    maxEvents = args.maxEvents
    relVals = args.releases
    useRecoJets = args.useRecoJets
    storageSite = args.storageSite
    tauCollection = args.tauCollection
    onebin = args.onebin
    debug = args.debug
    globaldebug = args.debug
    dryRun = args.dryRun
    inputfiles = args.inputfiles
    outputFileName = args.outputFileName
    totalparts = args.totalparts

    localdir = args.localdir
    if len(localdir) > 1 and localdir[-1] is not '/':
        localdir += '/'

    mvaidstr = ' --mvaid ' + ' '.join(args.mvaid)

    scriptPath = os.path.realpath(__file__)[0:os.path.realpath(__file__).rfind('/') + 1]

    dd = '--dryRun' if dryRun else ''
    if debug:
        dd += ' --debug'

    if skipProduceTauValTree==False :
        for i, relval in enumerate(relVals):
            inputfile = ' --inputfile ' + inputfiles[i] if len(inputfiles) > 0 else ''

            command = 'python ' + scriptPath + 'produceTauValTree.py --release ' + relval + \
                ' --globalTag ' + globalTags[i] + \
                inputfile + \
                ' --runtype ' + runtype + \
                ' --maxEvents ' + str(maxEvents) + \
                useRecoJets * ' -u ' + \
                ' -s ' + storageSite + \
                ' -l ' + localdir + \
                ' --tauCollection ' + tauCollection + mvaidstr + dd
            + (len(outputFileName) > 0) * (' --outputFileName ' + outputFileName)

        print '===================='
        print command
        print '===================='
        os.system(command)

    onebin = ' -b' if onebin else ''
    globalTagsstr = ' '.join(globalTags)
    releases = ' '.join(relVals)

    commands = []
    for i in range(totalparts):
        commands.append('python ' + scriptPath + 'compare.py --releases ' + releases + ' --globalTags ' + globalTagsstr + ' --runtype ' + str(runtype) + onebin + ' -p ' + str(i+1) + dd)

    for command in commands:
        print '===================='
        print command
        print '===================='
        os.system(command)


    #webplotting.webplotting(input_dir="./compare_{0}".format(runtype), recursive=True)
    print "FINISHED SUCCESSFULLY"
