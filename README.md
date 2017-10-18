# Tau release validation suite

## Setup

Clone this repository within a CMSSW environment:

    git clone https://github.com/cms-tau-pog/TauReleaseValidation.git

Run the following commands to produce validation plots:

     python produceTauValTree.py ZTT
     python compare.py ZTT

## Things to do

* Use argument parsing to pass releases and global tags
* Fix crash in compare.py
* Uses eostools from cmg-cmssw since the one in CMSSW is broken
