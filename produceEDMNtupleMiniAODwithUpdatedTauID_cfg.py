import FWCore.ParameterSet.Config as cms
import pprint
pp = pprint.PrettyPrinter(indent=4)

process = cms.Process("produceTauIdMVATrainingNtupleMiniAOD")
#process = cms.Process('TauID', eras.Run2_2017, eras.run2_nanoAOD_94XMiniAODv2)

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('FWCore/MessageService/MessageLogger_cfi')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')
process.load('Configuration/StandardSequences/FrontierConditions_GlobalTag_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.MessageLogger.cerr.FwkReport.reportEvery = 1000
process.MessageLogger.cerr.threshold = cms.untracked.string('INFO')
#process.load('Configuration.StandardSequences.Geometry_cff')
#process.load('Configuration.Geometry.GeometryIdeal_cff')

from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, '94X_mc2017_realistic_v10', '')# process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:phase1_2017_realistic', '')

# Input source
key = '2017MCv2_W3Jets'
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

process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(test_files[key]['file']),
    secondaryFileNames = cms.untracked.vstring()
)

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(1005))
process.options = cms.untracked.PSet(wantSummary = cms.untracked.bool(True))

# process.load("TrackingTools.TransientTrack.TransientTrackBuilder_cfi")

#--------------------------------------------------------------------------------
# define configuration parameter default values
type = test_files[key]['type']
#--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
# define "hooks" for replacing configuration parameters
# in case running jobs on the CERN batch system/grid
#
#__type = #type#
#
isMC = None
if type == 'SignalMC' or type == 'BackgroundMC': isMC = True
else: isMC = False

# information for cleaning against leptons
isSignal = None
dRClean = 0.5
if type == 'SignalMC':
    isSignal = True
    dRClean = 0.3
else: isSignal = False
#--------------------------------------------------------------------------------

from runTauIdMVA import *
na = TauIDEmbedder(process, cms,
    debug=True,
    toKeep = ["2017v1", "2017v2", "newDM2017v2", "dR0p32017v2", "2016v1", "newDM2016v1"]
)
na.runTauID()

print dir(process.loadRecoTauTagMVAsFromPrepDB.toGet)
print process.loadRecoTauTagMVAsFromPrepDB.toGet[-1]
#--------------------------------------------------------------------------------
# process.p = cms.Path(process.rerunMvaIsolationSequence * process.NewTauIDsEmbedded)

#--------------------------------------------------------------------------------

# Output definition (MiniAOD + updated taus)
# MiniAOD output
print("output prep")
process.out = cms.OutputModule("PoolOutputModule",
    compressionAlgorithm = cms.untracked.string('LZMA'),
    compressionLevel = cms.untracked.int32(4),
    dataset = cms.untracked.PSet(
        dataTier = cms.untracked.string('MINIAODSIM'),
        filterName = cms.untracked.string('')
    ),
    dropMetaData = cms.untracked.string('ALL'),
    eventAutoFlushCompressedSize = cms.untracked.int32(-900),
    fastCloning = cms.untracked.bool(False),
    fileName = cms.untracked.string('myOutputFile.root'),
    outputCommands = process.MINIAODSIMEventContent.outputCommands,
    overrideBranchesSplitLevel = cms.untracked.VPSet(cms.untracked.PSet(
        branch = cms.untracked.string('patPackedCandidates_packedPFCandidates__*'),
        splitLevel = cms.untracked.int32(99)
    ),
    cms.untracked.PSet(
        branch = cms.untracked.string('recoGenParticles_prunedGenParticles__*'),
        splitLevel = cms.untracked.int32(99)
    ), 
    cms.untracked.PSet(
        branch = cms.untracked.string('patTriggerObjectStandAlones_slimmedPatTrigger__*'),
        splitLevel = cms.untracked.int32(99)
    ), 
    cms.untracked.PSet(
        branch = cms.untracked.string('patPackedGenParticles_packedGenParticles__*'),
        splitLevel = cms.untracked.int32(99)
    ), 
    cms.untracked.PSet(
        branch = cms.untracked.string('patJets_slimmedJets__*'),
        splitLevel = cms.untracked.int32(99)
    ), 
    cms.untracked.PSet(
        branch = cms.untracked.string('recoVertexs_offlineSlimmedPrimaryVertices__*'),
        splitLevel = cms.untracked.int32(99)
    ), 
    cms.untracked.PSet(
        branch = cms.untracked.string('recoCaloClusters_reducedEgamma_reducedESClusters_*'),
        splitLevel = cms.untracked.int32(99)
    ), 
    cms.untracked.PSet(
        branch = cms.untracked.string('EcalRecHitsSorted_reducedEgamma_reducedEBRecHits_*'),
        splitLevel = cms.untracked.int32(99)
    ), 
    cms.untracked.PSet(
        branch = cms.untracked.string('EcalRecHitsSorted_reducedEgamma_reducedEERecHits_*'),
        splitLevel = cms.untracked.int32(99)
    ), 
    cms.untracked.PSet(
        branch = cms.untracked.string('recoGenJets_slimmedGenJets__*'),
        splitLevel = cms.untracked.int32(99)
    ), 
    cms.untracked.PSet(
        branch = cms.untracked.string('patJets_slimmedJetsPuppi__*'),
        splitLevel = cms.untracked.int32(99)
    ), 
    cms.untracked.PSet(
        branch = cms.untracked.string('EcalRecHitsSorted_reducedEgamma_reducedESRecHits_*'),
        splitLevel = cms.untracked.int32(99)
    )),
    overrideInputFileSplitLevels = cms.untracked.bool(True),
    splitLevel = cms.untracked.int32(0)
)
process.out.outputCommands.append('keep *_NewTauIDsEmbedded_*_*')

# Path and EndPath definitions
process.tauIDUpdate_step = cms.Path(process.rerunMvaIsolationSequence * process.NewTauIDsEmbedded)
process.endjob_step = cms.EndPath(process.endOfProcess)
process.out_step = cms.EndPath(process.out)
# process.tauIDUpdate_step = cms.Path(process.patTauMVAIDsSeq)
# process.endjob_step = cms.EndPath(process.endOfProcess)
# process.MINIAODSIMoutput_step = cms.EndPath(process.MINIAODSIMoutput)

# Schedule definition
process.schedule = cms.Schedule(process.tauIDUpdate_step, process.endjob_step, process.out_step)
# process.e = cms.EndPath(process.out)
# customisation of the process.

# Add early deletion of temporary data products to reduce peak memory need
from Configuration.StandardSequences.earlyDeleteSettings_cff import customiseEarlyDelete
process = customiseEarlyDelete(process)
# End adding early deletion
print "process.schedule:"
pp.pprint(process.schedule)


print "\n\n", "*"*10, "\nprocess.tauIDUpdate_step:"
pp.pprint(process.tauIDUpdate_step)

print "\n\n", "*"*10, "\nprocess.tauIDUpdate_step first element rerunDiscriminationByIsolationOldDMMVArun2017v2raw:"
pp.pprint(process.rerunDiscriminationByIsolationOldDMMVArun2017v2raw)

print "\n\n", "*"*10, "\nprocess.endjob_step:"
pp.pprint(process.endjob_step)

print "\n\n", "*"*10, "\nprocess.out_step:"
pp.pprint(process.out_step)
#Customize MessageLogger
print 'No. of events to process:', process.maxEvents.input.value()
if process.maxEvents.input.value() > 10:
     process.MessageLogger.cerr.FwkReport.reportEvery = process.maxEvents.input.value()//10
if process.maxEvents.input.value() > 10000 or process.maxEvents.input.value() < 0:
     process.MessageLogger.cerr.FwkReport.reportEvery = 1000

