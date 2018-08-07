import re
import os
import subprocess

import eostools


def addArguments(parser, compare=False):
    # for all, including produceTauValTree.py
    parser.add_argument('--runtype', choices=['ZTT', 'ZEE', 'ZMM', 'QCD', 'TTbar', 'TTbarTau', 'ZpTT', 'TenTaus'], help='choose sample type')

    # Only for produceTauValTree.py
    if not compare:
        parser.add_argument('-n', '--maxEvents', default=-1, type=int, help='Number of events that will be analyzed (-1 = all events) [Default: %(default)s]')
        parser.add_argument('-u', '--useRecoJets', default=False, action="store_true", help='Use RecoJets [Default: %(default)s]')
        parser.add_argument('-s', '--storageSite', default='eos', choices=['eos', 'das', 'loc'], help="Choose between samples store on eos or DAS or in private local folder [Default: %(default)s]")
        parser.add_argument('-l', '--localdir', default='/eos/user/o/ohlushch/relValMVA/', help="Local dir where the samples are looked up [Default: %(default)s]")
        parser.add_argument('-m', '--mvaid', default=[], nargs='*',
                            help="Select mvaids that should be obtained via rerunning TAUId sequence: [2017v1, 2017v2, newDM2017v2, dR0p32017v2, 2016v1, newDM2016v1]. [Default: %(default)s]")
        parser.add_argument('--noAntiLepton', default=False, action='store_true', help='Do not access anti-lepton discriminators, e.g. if you use the tau reconstruction on top of MiniAOD that does not calculate them')
        parser.add_argument('-t', '--tauCollection', default='slimmedTaus', help="Tau collection to be used. Possible: NewTauIDsEmbedded; [Default: %(default)s].")
        parser.add_argument('-o', '--outputFileName', default='', help="Output file name [Default: %(default)s]")

    if compare:
        parser.add_argument('-p', '--part', default=0, type=int, help='Make WP plots(1), first half of histogram plots(2), \
            second half of histogram plots(3), or everything at once(0) \
            (This part needs to be split up to avoid a crash that happens for some reason)')
        parser.add_argument('-b', '--onebin', default=False, action="store_true", help='Plot inclusive efficiencies by only using one bin')
        parser.add_argument('-r', '--releases', default=["CMSSW_9_4_0_pre1", "CMSSW_9_4_0_pre2"], nargs='*', help='List of releases')
        parser.add_argument('-g', '--globalTags', default=['93X_mc2017_realistic_v3-v1', 'PU25ns_94X_mc2017_realistic_v1-v1'], nargs='*', help='List of global tags [Default: %(default)s]')
        parser.add_argument('-i', '--inputfiles', default=[], nargs='*', help="List of files locations [Default: %(default)s]")

        parser.add_argument('-v', '--variables', default=[], nargs='*', help='Variables to place on a single plot (if only one release+GT)')
        parser.add_argument('-c', '--colors', default=[1, 4], nargs='*', help='Colors of variables to place on a single plot (if only one release+GT)')
        parser.add_argument('--varyLooseId', default=False, action="store_true", help='If the loose Id should be varied')
        parser.add_argument('--setLooseId', default='tau_byLooseIsolationMVArun2v1DBoldDMwLT', help='LooseId to be considered')

def getFilesFromEOS(path, cmseospath=True):
    '''Give path in form /store/relval/CMSSW_9_4_0_pre2/...'''
    if path[-1] == "/":
        path = path[:-1]
    dirs = eostools.listFiles(cmseospath * '/eos/cms' + path)
    print "getFilesFromEOS::path:", path
    print "getFilesFromEOS::dirs: ", dirs

    files = []
    for sub_path in dirs:
        print "\tsub_path:", sub_path
        files += [cmseospath * 'root://eoscms.cern.ch/' + x for x in eostools.listFiles(sub_path) if re.match('.*root', x)]

    print "files:", files
    return files


def getFilesFromDAS(release, runtype, globalTag):
    '''Get proxy with "voms-proxy-init -voms cms" to use this option.'''
    query = "file dataset=/*{0}*/*{1}*{2}*/MINIAODSIM".format(runtype, release, globalTag, )
    print "Getting files from DAS. May take a while.... query:", query
    result = subprocess.check_output("dasgoclient --query='" + "file dataset=/*{0}*/*{1}*{2}*/MINIAODSIM".format(runtype, release, globalTag, ) + "'", shell=True)
    files = ["root://cms-xrd-global.cern.ch/" + s.strip() for s in result.splitlines()]

    print "files:", files
    return files

runtype_to_sample = {
    'ZTT':'RelValZTT_13',
    'ZMM':'RelValZpMM_13',
    'QCD':'RelValQCD_FlatPt_15_3000HS_13',
    'TTbar':'RelValTTbar_13',
    'TTbarTau':'RelValTTbar_13',
    'ZpTT':'RelValZpTT_1500_13',
    'TenTaus':'RelValTenTau_15_500'
}

def get_cmssw_version():
    """returns 'CMSSW_X_Y_Z'"""
    return os.environ["CMSSW_RELEASE_BASE"].split('/')[-1]

def get_cmssw_version_number():
    """returns 'X_Y_Z' (without 'CMSSW_')"""
    return map(int, get_cmssw_version().split("CMSSW_")[1].split("_")[0:3])


def versionToInt(release=9, subversion=4, patch=0):
    return release * 10000 + subversion * 100 + patch

def is_above_cmssw_version(release=9, subversion=4, patch=0):
    split_cmssw_version = get_cmssw_version_number()
    if versionToInt(release, subversion, patch) > versionToInt(split_cmssw_version[0], split_cmssw_version[1], split_cmssw_version[2]):
        return False
    return True

# Input source
#key = '2017MCv2_W3Jets'
test_files = {
    'RelValQCD_FlatPt_15_3000HS_13_1': {
        'file' : '/store/relval/CMSSW_9_4_0_pre3/RelValQCD_FlatPt_15_3000HS_13/MINIAODSIM/PU25ns_94X_mc2017_realistic_v4-v1/10000/E89C4CD3-CEBB-E711-BF4F-0025905B856C.root',
        'type' : 'BackgroundMC',
        'comment' : "2017 MCv2, with 2016 training, phpt>1"
    },
    'RelValQCD_FlatPt_15_3000HS_13_2': {
        'file' : '/store/relval/CMSSW_9_4_0_pre3/RelValQCD_FlatPt_15_3000HS_13/MINIAODSIM/PU25ns_94X_mc2017_realistic_v4-v1/10000/EE4BC1EA-CEBB-E711-984B-0CC47A78A418.root',
        'type' : 'BackgroundMC',
        'comment' : "2017 MCv2, with 2016 training, phpt>1"
    },
    'RelValZTT_13_1': {
        'file' : '/store/relval/CMSSW_9_4_0_pre3/RelValZTT_13/MINIAODSIM/PU25ns_94X_mc2017_realistic_v4-v1/10000/0A99A363-65BB-E711-A1CF-003048FFD72C.root',
        'type' : 'SignalMC',
        'comment' : "2017 MCv2, with 2016 training, phpt>1"
    },
    'RelValZTT_13_2': {
        'file' :'/store/relval/CMSSW_9_4_0_pre3/RelValZTT_13/MINIAODSIM/PU25ns_94X_mc2017_realistic_v4-v1/10000/28E2B54E-65BB-E711-ABDD-0025905A606A.root',
        'type' : 'SignalMC',
        'comment' : "2017 MCv2, with 2016 training, phpt>1"
    },
    '2017MCv1_DY': {
        'file' :'/store/mc/RunIISummer17MiniAOD/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/MINIAODSIM/92X_upgrade2017_realistic_v10_ext1-v2/10000/00F9D855-E293-E711-B625-02163E014200.root',
        'type' : 'BackgroundMC',
        'comment' : "2017 MCv1, with 2016 training, phpt>0.5"
    },
    '2017MCv1_ggH': {
        'file' :'/store/mc/RunIISummer17MiniAOD/SUSYGluGluToHToTauTau_M-2600_TuneCUETP8M1_13TeV-pythia8/MINIAODSIM/92X_upgrade2017_realistic_v10-v2/50000/04BF6396-8F9C-E711-9BE4-0CC47A1DF620.root',
        'type' : 'SignalMC',
        'comment' : "2017 MCv1, with 2016 training, phpt>0.5"
    },
    '2017MCv2_W3Jets': {
        'file' :'/store/mc/RunIIFall17MiniAOD/W3JetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/MINIAODSIM/94X_mc2017_realistic_v10-v3/80000/02B37840-A50C-E811-B96F-008CFAF70DF6.root',
        'type' : 'BackgroundMC',
        'comment' : "2017 MCv2"
    }
}
