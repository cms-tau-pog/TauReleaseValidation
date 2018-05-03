import os
import argparse
import subprocess
import pprint
pp = pprint.PrettyPrinter(indent=4)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('runtype', choices=['ZTT', 'ZMM', 'QCD', 'TTbar', 'TTbarTau', 'ZpTT'], help='choose sample type')

    parser.add_argument('-r', '--releases', help='Comma separated list of releases', default='CMSSW_9_4_0_pre2,CMSSW_9_4_0_pre3')
    parser.add_argument('-g', '--globalTag',  help='Global tags, separated by comma', default='94X_mc2017_realistic_v1-v1,94X_mc2017_realistic_v4-v1')
    parser.add_argument('-n', '--maxEvents',  help='Number of events that will be analyzed (-1 = all events)', default=-1, type=int)
    parser.add_argument('-u', '--useRecoJets', action="store_true",  help='Use RecoJets', default=False)
    parser.add_argument('-b', '--onebin', action="store_true",  help='Plot inclusive efficiencies by only using one bin', default=False)
    parser.add_argument('-s', '--storageSite', help="Choose between samples store on eos or DAS or in private local folder",  choices=['eos','das', 'loc'], default='eos')
    parser.add_argument('-l', '--localdir', help="Local dir where the samples are looked up",  default='/eos/user/o/ohlushch/relValMVA/')
    parser.add_argument('-d', '--debug', help="Debug option", action="store_true",  default=False)


    args = parser.parse_args()
        
    maxEvents = ' -n' + args.maxEvents if args.maxEvents > -1 else ''
    RelVals = args.releases.split(',')
    globalTags = args.globalTag.split(',')
    useRecoJets = ' -u' if args.useRecoJets else ''
    onebin = ' -b' if args.onebin else ''
    storageSite = args.storageSite
    localdir = args.localdir
    debug = args.debug
    scriptPath = os.path.realpath(__file__)[0:os.path.realpath(__file__).rfind("/")+1]

    runtype = ' ' + args.runtype

    commands = []
    for i, relval in enumerate(RelVals):
        print "===================="
        result = subprocess.check_output('python ' + scriptPath + 'produceTauValTree.py -r ' + relval + ' -g ' + globalTags[i] + runtype + maxEvents + useRecoJets + ' -s ' + storageSite + " -l " + location + " -d" + debug, shell=True)
        pp.pprint(result)
        # commands.append('python ' + scriptPath + 'produceTauValTree.py -r ' + relval + ' -g ' + globalTags[i] + runtype + maxEvents + useRecoJets + ' -s ' + storageSite + " -l " + location + " -d" + debug)

    for i in range(1, 3):
        print "===================="
        result = subprocess.check_output('python ' + scriptPath + 'produceTauValTree.py -r ' + relval + ' -g ' + globalTags[i] + runtype + maxEvents + useRecoJets + ' -s ' + storageSite + " -l " + location + " -d" + debug, shell=True)
        pp.pprint(result)
    commands.append('python ' + scriptPath + 'compare.py -r ' + args.releases + ' -g ' + args.globalTag + runtype + onebin + ' -p 1')
    commands.append('python ' + scriptPath + 'compare.py -r ' + args.releases + ' -g ' + args.globalTag + runtype + onebin + ' -p 2')
    commands.append('python ' + scriptPath + 'compare.py -r ' + args.releases + ' -g ' + args.globalTag + runtype + onebin + ' -p 3')

    for command in commands:
        print "===================="
        print command
        print "===================="
        os.system(command)
