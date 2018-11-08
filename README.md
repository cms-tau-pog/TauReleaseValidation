# Tau release validation suite

## Setup

Clone this repository within a CMSSW environment:

    git clone https://github.com/cms-tau-pog/TauReleaseValidation.git

If you plan to update the TauID list wrt the used CMSSW version do:

     wget https://raw.githubusercontent.com/greyxray/TauAnalysisTools/CMSSW_9_4_X_tau-pog_RunIIFall17/TauAnalysisTools/python/runTauIdMVA.py  -P $CMSSW_BASE/src/TauReleaseValidation/

Run the following commands to produce validation plots:

     python produceTauValTree.py ZTT
     python compare.py ZTT

Alternatively the command `produceAndCompare.py` will run `produceTauValTree.py` on all given combinations of Releases and GlobalTags, followed by running `compare.py` on these samples as well.

Example commands:

     python produceAndCompare.py --release CMSSW_10_3_0_pre1 --globalTag PU25ns_102X_upgrade2018_realistic_v9-v1 --runtype ZTT -s eos --debug
     python produceTauValTree.py --release CMSSW_10_3_0_pre1 --globalTag PU25ns_102X_upgrade2018_realistic_v9-v1 --runtype ZTT --maxEvents 1000 -s eos -l /eos/user/o/<YOU>/relValMVA/ --tauCollection slimmedTaus --mvaid
     python produceAndCompare.py --releases CMSSW_9_4_10 CMSSW_9_4_11_cand2 --globalTags PU25ns_94X_mcRun2_asymptotic_v3_FastSim-v1 PU25ns_94X_mc2017_realistic_v15_FastSim-v1 --runtype ZTT -s das

## Things to do/notes

* Uses eostools from cmg-cmssw since the one in CMSSW is broken
* Add more samples (VBF Higgs, H+, ZEE)
* Finish setting up the different samples
