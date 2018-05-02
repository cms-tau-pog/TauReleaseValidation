import FWCore.ParameterSet.Config as cms

from relValTools import *

######## Parsing options ########
from FWCore.ParameterSet.VarParsing import VarParsing
options = VarParsing('python')
options.register('runtype', '', VarParsing.multiplicity.singleton, VarParsing.varType.string, "choose sample type; choices=['ZTT', 'ZEE', 'ZMM', 'QCD', 'TTbar', 'TTbarTau', 'ZpTT']")
options.register('release', 'CMSSW_9_4_0_pre2', VarParsing.multiplicity.singleton, VarParsing.varType.string, 'Release string')
options.register('globalTag', 'PU25ns_94X_mc2017_realistic_v1-v1', VarParsing.multiplicity.singleton, VarParsing.varType.string, 'Global tag')
options.register('useRecoJets', False, VarParsing.multiplicity.singleton, VarParsing.varType.bool, 'Use RecoJets, 0 - false, 1 - true ')
options.register('storageSite', 'eos', VarParsing.multiplicity.singleton, VarParsing.varType.string, "Choose between samples store on eos or DAS or in private local folder. choices=['eos','das', 'loc']")
options.register('localdir', '', VarParsing.multiplicity.singleton, VarParsing.varType.string, "Local dir where the samples are looked up. \
    Output is always created under the local dir if this option is activated and the outputfile is not")
options.register('inputfile', '', VarParsing.multiplicity.singleton, VarParsing.varType.string, "Single file location for fast checks")
options.register('outputFileName', '', VarParsing.multiplicity.singleton, VarParsing.varType.string, "Single file location for fast checks")
options.register('debug', False, VarParsing.multiplicity.singleton, VarParsing.varType.bool, "Debug option")
options.register('key', '', VarParsing.multiplicity.singleton, VarParsing.varType.string, "Key for the input file")
options.parseArguments()

RelVal = options.release
globalTag = options.globalTag
useRecoJets = options.useRecoJets
storageSite = options.storageSite
localdir = options.localdir
debug = options.debug
runtype = options.runtype

key = options.key
if len(key) == 0:
    key = runtype_to_sample[runtype] + "_" + RelVal + "_" + globalTag

if len(localdir) > 1 and localdir[-1] is not "/": localdir += "/"


######## Input files ########
inputfile = options.inputfile
if inputfile != "": filelist = [inputfile]
else:
    path = '/store/relval/{}/{}/MINIAODSIM/{}'.format(RelVal, runtype_to_sample[runtype], globalTag)

    if   storageSite == "eos": filelist = getFilesFromEOS(path)
    elif storageSite == "das": filelist = getFilesFromDAS(RelVal, runtype_to_sample[runtype], globalTag)
    elif storageSite == 'loc': filelist = getFilesFromEOS(localdir + runtype_to_sample[runtype] + "/" + RelVal + '-' + globalTag + '/', cmseospath=False)

    if len(filelist) == 0:
        print 'Sample', RelVal, runtype, 'does not exist in', path
        sys.exit(0)

if storageSite == 'loc': filelist = ['file:' + x for x in filelist]

if key not in test_files.keys():
    test_files[key] = { 'file' : filelist }
else:
    print "!Warning! Such key already in the default list:", key

print "filelist:", filelist

######## Output file ########
outputFileName = options.outputFileName
if len(outputFileName) == 0:
    if storageSite == 'loc':
        outputFileName = localdir + runtype_to_sample[runtype] + "/" + RelVal + '-' + globalTag + '/' + 'Updated/'
        
        if not os.path.isdir(outputFileName):

            result = subprocess.check_output("mkdir -p {outputFileName}".format(outputFileName=outputFileName), shell=True)

    outputFileName += 'output.root'
else:
    if "/" in outputFileName and outputFileName[0] != "/":
        print "location of output file has a dir structure but doesn't start with dash"
        sys.exit(0)
    if outputFileName[-5:] != ".root":
        outputFileName += '.root'
        print "output file should have a root format - added automatically:", outputFileName

print "outputFileName:", outputFileName

#---------------------------------- Parameter Set --------------------------------------------

process = cms.Process("produceTauIdMVATrainingNtupleMiniAOD")
#process = cms.Process('TauID', eras.Run2_2017, eras.run2_nanoAOD_94XMiniAODv2)

######## Import of standard configurations ########
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
# process.load("TrackingTools.TransientTrack.TransientTrackBuilder_cfi")

from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, '94X_mc2017_realistic_v14', '')# process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:phase1_2017_realistic', '')

process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(test_files[key]['file']),
    secondaryFileNames = cms.untracked.vstring()
)

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(options.maxEvents))
process.options = cms.untracked.PSet(wantSummary = cms.untracked.bool(True))
#--------------------------------------------------------------------------------

from runTauIdMVA import *
na = TauIDEmbedder(process, cms,
    debug=False,
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
    fileName = cms.untracked.string(outputFileName),
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

# Schedule definition
process.schedule = cms.Schedule(process.tauIDUpdate_step, process.endjob_step, process.out_step)

# Add early deletion of temporary data products to reduce peak memory need
from Configuration.StandardSequences.earlyDeleteSettings_cff import customiseEarlyDelete
process = customiseEarlyDelete(process)
# End adding early deletion

#Customize MessageLogger
print 'No. of events to process:', process.maxEvents.input.value()
if process.maxEvents.input.value() > 10:
     process.MessageLogger.cerr.FwkReport.reportEvery = process.maxEvents.input.value()//10
if process.maxEvents.input.value() > 10000 or process.maxEvents.input.value() < 0:
     process.MessageLogger.cerr.FwkReport.reportEvery = 1000

