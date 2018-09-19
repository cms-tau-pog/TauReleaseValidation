''' Currently serves as an example of how to use the roc_tools to produce ROC
curves. Should ideally be updated to a simple script with command line arguments
that can produce general ROC curves.
'''

import os
import subprocess
import argparse
from collections import namedtuple

from ROOT import TH1F, TChain

from roc_tools import histsToRoc, makeROCPlot


class ROCPlotter(object):

    scan_vars = [
        ('tau_chargedIsoPtSum', 'chargedIso'),
        ('tau_byCombinedIsolationDeltaBetaCorrRaw3Hits', 'combIso'),
        ('(tau_byCombinedIsolationDeltaBetaCorrRaw3Hits + 10e4*(tau_photonPtSumOutsideSignalCone/tau_pt>0.1))', 'combIsoPtOuter'),
        ('1.-0.5*tau_byIsolationMVArun2v1DBoldDMwLTraw', 'mva'),
    ]

    def __init__(self):

        self.parseArgs()
        self.roc_dir = self.getStandartizeDirectory(self.args.roc_dir)
        if not os.path.isdir(self.roc_dir):
            bashCommand = "mkdir --parents " + self.roc_dir
            process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
            output, error = process.communicate()
            if error is not None:
                print "\tmkdir::error:", error
                exit(1)

        # Settings that are likely to be invariant
        self.selection_signal = self.args.selection_signal
        self.selection_background = self.args.selection_background   # It's the same in fact, even though these are jets
        self.tree_name = self.args.tree_name
        self.selection_denominator = self.args.selection_denominator

        # Settings that may vary for each ROC curve
        self.DiscSetup = namedtuple('DiscSetup', ' '.join(['name', 'title', 'signal_files', 'background_files', 'scan_variable']))
        self.ds_name = self.args.ds_name
        self.ds_title = self.args.ds_title
        self.ds_signal_files = self.args.ds_signal_files
        self.ds_background_files = self.args.ds_background_files
        self.ds_scan_variable = self.args.ds_scan_variable

    @staticmethod
    def checkDirExists(path="", critical=False):
        if not os.path.isdir(path):
            if critical:
                print "Path ", path, "... does not exist"
                exit(1)
            else:
                return False
        return True

    def getStandartizeDirectory(self, path=""):
        if len(path) > 0 and self.checkDirExists(path) and path[-1] != "/":
            path += "/"
        return path

    def parseArgs(self):
        parser = argparse.ArgumentParser(description='movetoNFS.py parser')

        parser.add_argument('--ds-name', default=['standard'], type=str, nargs="*",
                            help='DiscSetup name')
        parser.add_argument('--ds-title', default=['Dynamic strip'], type=str, nargs="*",
                            help='DiscSetup title')
        parser.add_argument('--ds-signal-files', default=['Myroot_CMSSW_10_3_0_pre1_PU25ns_102X_upgrade2018_realistic_v9-v1_ZTT.root'], type=str, nargs="*",
                            help='DiscSetup signal-files. One file per one roc-curve. Ensure to hadd.')
        parser.add_argument('--ds-background-files', default=['Myroot_CMSSW_10_3_0_pre1_102X_upgrade2018_realistic_v9-v1_QCD_genJets.root'], type=str, nargs="*",
                            help='DiscSetup background-files')
        parser.add_argument('--ds-scan-variable', default=[], type=str, nargs="*",
                            help='DiscSetup scan-variable. One file per one roc-curve. Ensure to hadd.')

        parser.add_argument('--roc-dir', default='rocs/', type=str,
                            help='rocs dir')

        parser.add_argument('--selection-signal', default='tau_genpt > 20. && abs(tau_geneta)<2.3', type=str,
                            help='')
        parser.add_argument('--selection-background', default='tau_genpt > 20. && abs(tau_geneta)<2.3', type=str,
                            help='')
        parser.add_argument('--tree-name', default='per_tau', type=str,
                            help='')
        parser.add_argument('--selection-denominator', default='1', type=str,
                            help='')

        parser.add_argument('--debug', action='store_true', default=False,
                            help='debug')

        self.args = parser.parse_args()
        self.dpprint("Parsed arguments:", self.args.__dict__)

    def dprint(self, *text):
        if self.args.debug and text is not None:
            for t in text:
                print t,
            print
            # print " ".join(map(str, text))

    def dpprint(self, *text):
        import pprint
        pp = pprint.PrettyPrinter(indent=4)
        if self.args.debug and text is not None:
            for t in text:
                pp.pprint(t)
            # pp.pprint(" \n".join(map(str, text)))

    def getSetups(self):
        self.dprint("getSetups")
        setups = []
        for name, title, signal_files, background_files, scan_variable in zip(self.ds_name, self.ds_title, self.ds_signal_files, self.ds_background_files, self.ds_scan_variable):
            self.dprint("\tname", name)
            setups.append(self.DiscSetup(name=name,
                          title=title,
                          signal_files=signal_files,
                          background_files=background_files,
                          scan_variable=scan_variable))
        self.dpprint("setups:", setups)
        return setups

    def getROCs(self, setups=[]):
        rocs = []
        for setup in setups:
            chain_s = TChain(self.tree_name)
            chain_s.Add(setup.signal_files)
            # for f_signal in setup.signal_files:
            #     chain_s.Add(f_signal)
            h_s = TH1F('signal' + setup.name, '', 1000, 0., 1.000001)
            chain_s.Draw(setup.scan_variable + '>>' + h_s.GetName(), '&&'.join([self.selection_signal, self.selection_denominator]))

            chain_b = TChain(self.tree_name)
            chain_b.Add(setup.background_files)
            # for f_b in setup.background_files:
            #     chain_b.Add(f_b)
            h_b = TH1F('background' + setup.name, '', 1000, 0., 1.000001)
            chain_b.Draw(setup.scan_variable + '>>' + h_b.GetName(), '&&'.join([self.selection_signal, self.selection_denominator]))

            roc = histsToRoc(h_s, h_b, True)
            roc.title = setup.title
            rocs.append(roc)
        return rocs

    def run(self):

        for scan_var, scan_var_name in self.scan_vars:
            self.dprint("scanvars", scan_var, scan_var_name)

            # Define such that signal -> 1, background -> 0
            scan_variable = '(tau_decayModeFinding && tau_pt>20. && abs(tau_eta)<2.3) * (1./(1.+{}))'.format(scan_var)
            if self.args.ds_scan_variable == []:
                self.ds_scan_variable = [scan_variable] * len(self.args.ds_title)

            setups = self.getSetups()
            rocs = self.getROCs(setups)

            makeROCPlot(rocs, self.roc_dir + scan_var_name, xmin=0.4, xmax=0.9, ymin=0.0001 if 'mva' in scan_var_name else 0.001, logy=True)


if __name__ == '__main__':
    ROCPlotter().run()
