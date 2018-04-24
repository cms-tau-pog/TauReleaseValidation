import eostools
import re

def getFilesFromEOS(path, cmseospath=True):
    '''Give path in form /store/relval/CMSSW_9_4_0_pre2/...'''
    if path[-1] == "/": path = path[:-1]
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
    print "Getting files from DAS. May take a while...."

    query = "file dataset=/*{0}*/*{1}*{2}*/MINIAODSIM".format(runtype, release, globalTag, )

    import subprocess
    result = subprocess.check_output("dasgoclient --query='" + "file dataset=/*{0}*/*{1}*{2}*/MINIAODSIM".format(runtype, release, globalTag, ) + "'", shell=True)
    files =  ["root://cms-xrd-global.cern.ch/" + s.strip() for s in result.splitlines()]

    print "files:", files
    return files

runtype_to_sample = {
    'ZTT':'RelValZTT_13',
    'ZMM':'RelValZpMM_13',
    'QCD':'RelValQCD_FlatPt_15_3000HS_13',
    'TTbar':'RelValTTbar_13',
    'TTbarTau':'RelValTTbar_13',
    'ZpTT':'RelValZpTT_1500_13'
}

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