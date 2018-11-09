import re
import os
import subprocess

import eostools

globaldebug = False

runtype_to_sample = {
    'ZTT': 'RelValZTT_13',
    'ZMM': 'RelValZMM_13',
    'ZpMM': 'RelValZpMM_13',
    'ZEE': 'RelValZEE_13',
    'QCD': 'RelValQCD_FlatPt_15_3000HS_13',
    'TTbar': 'RelValTTbar_13',
    'TTbarTau': 'RelValTTbar_13',
    'ZpTT': 'RelValZpTT_1500_13',
    'TenTaus': 'RelValTenTau_15_500',
}


def addArguments(parser, produce=True, compare=False):
    parser.add_argument('--runtype', choices=['ZTT', 'ZEE', 'ZMM', 'ZpMM', 'QCD', 'TTbar', 'TTbarTau', 'ZpTT', 'TenTaus'], help='choose sample type')
    parser.add_argument('-i', '--inputfiles', default=[], nargs='*', help="List of files locations [Default: %(default)s]")

    # useful for debugging
    parser.add_argument('-n', '--maxEvents', default=-1, type=int, help='Number of events that will be analyzed (-1 = all events) [Default: %(default)s]')
    parser.add_argument('--debug', default=False, help="Debug option [Default: %(default)s]", action="store_true")
    parser.add_argument('--dryRun', default=False, action="store_true",  help='Dry run - no plots [Default: %(default)s]')

    if produce:
        parser.add_argument('--release', default="CMSSW_9_4_0_pre1", help='Release')
        parser.add_argument('--globalTag', default='93X_mc2017_realistic_v3-v1', help='Global tag [Default: %(default)s]')
        parser.add_argument('-o', '--outputFileName', default='', help="Output file name [Default: %(default)s]")
        parser.add_argument('-s', '--storageSite', default='eos', choices=['eos', 'das', 'loc'], help="Choose between samples store on eos or DAS or in private local folder [Default: %(default)s]")
        parser.add_argument('-l', '--localdir', default='/eos/user/o/ohlushch/relValMVA/', help="Local dir where the samples are looked up [Default: %(default)s]")#
        parser.add_argument('-m', '--mvaid', default=[], nargs='*',
            help="Select mvaids that should be obtained via rerunning TAUId sequence: [2017v1, 2017v2, newDM2017v2, dR0p32017v2, 2016v1, newDM2016v1]. [Default: %(default)s]")
        parser.add_argument('-t', '--tauCollection', default='slimmedTaus', help="Tau collection to be used. Possible: NewTauIDsEmbedded; [Default: %(default)s].")
        parser.add_argument('-u', '--useRecoJets', default=False, action="store_true", help='Use RecoJets [Default: %(default)s]')
        parser.add_argument('--noAntiLepton', default=False, action='store_true', help='Do not access anti-lepton discriminators, e.g. if you use the tau reconstruction on top of MiniAOD that does not calculate them')

    if compare:
        parser.add_argument('-p', '--part', default=0, type=int, help='Make WP plots(1), fraction of histogram plots(2..totalparts), \
            , or everything at once(0) (This part needs to be split up to avoid a crash that happens for some reason)')
        parser.add_argument('--totalparts', default=6, type=int, help='How many parts the compare step should be split into. \
            Increase this value if root crashes occur.')
        parser.add_argument('-b', '--onebin', default=False, action="store_true", help='Plot inclusive efficiencies by only using one bin')
        parser.add_argument('--releases', default=["CMSSW_9_4_0_pre1", "CMSSW_9_4_0_pre2"], nargs='*', help='List of releases')
        parser.add_argument('--globalTags', default=['93X_mc2017_realistic_v3-v1', 'PU25ns_94X_mc2017_realistic_v1-v1'], nargs='*', help='List of global tags [Default: %(default)s]')

        parser.add_argument('-v', '--variables', default=[], nargs='*', help='Variables to place on a single plot (if only one release+GT)')
        parser.add_argument('-c', '--colors', default=[1, 4], nargs='*', help='Colors of variables to place on a single plot (if only one release+GT)')
        parser.add_argument('--varyLooseId', default=False, action="store_true", help='If the loose Id should be varied')
        parser.add_argument('--setLooseId', default='tau_byLooseIsolationMVArun2v1DBoldDMwLT', help='LooseId to be considered')


def dprint(*text):
    if globaldebug and text is not None:
        for t in text:
            print t,
        print
        # print " ".join(map(str, text))


def dpprint(*text):
    import pprint
    pp = pprint.PrettyPrinter(indent=4)
    if globaldebug and text is not None:
        for t in text:
            pp.pprint(t)
        # pp.pprint(" \n".join(map(str, text)))


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
    query = "file dataset=/{0}/{1}-{2}/MINIAODSIM".format(runtype, release, globalTag, )
    print "Getting files from DAS. query:", query
    result = subprocess.check_output("dasgoclient --query='" + query + "'", shell=True)
    if not result:
        query = "file dataset=/*{0}*/*{1}*{2}*/MINIAODSIM".format(runtype, release, globalTag, )
        print "First attempt unsuccessful. Generalizing query. May take a while.... query:", query
        result = subprocess.check_output("dasgoclient --query='" + query + "'", shell=True)
    files = ["root://cms-xrd-global.cern.ch/" + s.strip() for s in result.splitlines()]

    print "files:", files
    return files


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
