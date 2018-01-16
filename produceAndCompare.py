import os
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('runtype', choices=['ZTT', 'ZMM', 'QCD', 'TTbar', 'TTbarTau', 'ZpTT'], help='choose sample type')

    parser.add_argument('-r', '--relval',  help='Release strings, separated by comma', default='CMSSW_9_4_0_pre2,CMSSW_9_4_0_pre3')
    parser.add_argument('-g', '--globalTag',  help='Global tags, separated by comma', default='94X_mc2017_realistic_v1-v1,94X_mc2017_realistic_v4-v1')
    parser.add_argument('-n', '--maxEvents',  help='Number of events that will be analyzed (-1 = all events)', default=-1)
    parser.add_argument('-u', '--useRecoJets', action="store_true",  help='Use RecoJets', default=False)
    parser.add_argument('-b', '--onebin', action="store_true",  help='Plot inclusive efficiencies by only using one bin', default=False)

    args = parser.parse_args()
        
    maxEvents = ' -n'+args.maxEvents if args.maxEvents > -1 else ''
    RelVals = args.relval.split(',')
    globalTags = args.globalTag.split(',')
    useRecoJets = ' -u' if args.useRecoJets else ''
    onebin = ' -b' if args.onebin else ''
    path = os.path.realpath(__file__)[0:os.path.realpath(__file__).rfind("/")+1]

    runtype = ' '+args.runtype

    commands = []
    for i, relval in enumerate(RelVals):
        commands.append('python '+path+'produceTauValTree.py -r '+relval+' -g '+globalTags[i]+runtype+maxEvents+useRecoJets)
    commands.append('python '+path+'compare.py -r '+args.relval+' -g '+args.globalTag+runtype+onebin+' -p 1')
    commands.append('python '+path+'compare.py -r '+args.relval+' -g '+args.globalTag+runtype+onebin+' -p 2')
    commands.append('python '+path+'compare.py -r '+args.relval+' -g '+args.globalTag+runtype+onebin+' -p 3')

    for command in commands:
        print "===================="
        print command
        print "===================="
        os.system(command)
