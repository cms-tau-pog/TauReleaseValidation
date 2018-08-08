''' Currently serves as an example of how to use the roc_tools to produce ROC
curves. Should ideally be updated to a simple script with command line arguments
that can produce general ROC curves.
'''


from collections import namedtuple

from ROOT import TH1F, TGraph, TChain

from roc_tools import histsToRoc, makeROCPlot

# Settings that are likely to be invariant
selection_signal = 'tau_genpt > 20. && abs(tau_geneta)<2.3'
selection_background = 'tau_genpt > 20. && abs(tau_geneta)<2.3' # It's the same in fact, even though these are jets
tree_name = 'per_tau'
selection_denominator = '1'


scan_vars = [
    ('tau_chargedIsoPtSum', 'chargedIso'),
    ('tau_byCombinedIsolationDeltaBetaCorrRaw3Hits', 'combIso'),
    ('(tau_byCombinedIsolationDeltaBetaCorrRaw3Hits + 10e4*(tau_photonPtSumOutsideSignalCone/tau_pt>0.1))', 'combIsoPtOuter'),
    ('1.-0.5*tau_byIsolationMVArun2v1DBoldDMwLTraw', 'mva')
]

for scan_var, scan_var_name in scan_vars:

    # Define such that signal -> 1, background -> 0
    scan_variable = '(tau_decayModeFinding && tau_pt>20. && abs(tau_eta)<2.3) * (1./(1.+{}))'.format(scan_var)

    # Settings that may vary for each ROC curve
    DiscSetup = namedtuple('DiscSetup', ' '.join(['name', 'title', 'signal_files', 'background_files', 'scan_variable']))

    setups = [
        DiscSetup(name='standard',
                  title='Dynamic strip',
                  signal_files=['Myroot_CMSSW_9_4_0_pre2_PU25ns_94X_mc2017_realistic_v1-v1_ZTT_oldtaus.root'],
                  background_files=['Myroot_CMSSW_9_4_0_pre2_PU25ns_94X_mc2017_realistic_v1-v1_QCD_genJets_oldtaus.root'],
                  scan_variable=scan_variable),
        # DiscSetup(name='standard_newdm',
        #           title='Dynamic strip, newDM',
        #           signal_files=['Myroot_CMSSW_9_4_0_pre2_PU25ns_94X_mc2017_realistic_v1-v1_ZTT_oldtaus.root'],
        #           background_files=['Myroot_CMSSW_9_4_0_pre2_PU25ns_94X_mc2017_realistic_v1-v1_QCD_genJets_oldtaus.root'],
        #           scan_variable=scan_variable.replace('tau_decayModeFinding', '1')),
        DiscSetup(name='rereco',
                  title='Modified strips',
                  signal_files=['Myroot_CMSSW_9_4_0_pre2_PU25ns_94X_mc2017_realistic_v1-v1_ZTT_rereco.root'],
                  background_files=['Myroot_CMSSW_9_4_0_pre2_PU25ns_94X_mc2017_realistic_v1-v1_QCD_genJets_rereco.root'],
                  scan_variable=scan_variable),
        # DiscSetup(name='rereco_newdm',
        #           title='Modified strips, new DM',
        #           signal_files=['Myroot_CMSSW_9_4_0_pre2_PU25ns_94X_mc2017_realistic_v1-v1_ZTT_rereco.root'],
        #           background_files=['Myroot_CMSSW_9_4_0_pre2_PU25ns_94X_mc2017_realistic_v1-v1_QCD_genJets_rereco.root'],
        #           scan_variable=scan_variable.replace('tau_decayModeFinding', '1'))
        ]

    rocs = []
    for setup in setups:
        chain_s = TChain(tree_name)
        for f_signal in setup.signal_files:
            chain_s.Add(f_signal)
        h_s = TH1F('signal'+setup.name, '', 1000, 0., 1.000001)
        chain_s.Draw(setup.scan_variable + '>>' + h_s.GetName(), '&&'.join([selection_signal, selection_denominator]))

        chain_b = TChain(tree_name)
        for f_b in setup.background_files:
            chain_b.Add(f_b)
        h_b = TH1F('background'+setup.name, '', 1000, 0., 1.000001)
        chain_b.Draw(setup.scan_variable + '>>' + h_b.GetName(), '&&'.join([selection_signal, selection_denominator]))

        roc = histsToRoc(h_s, h_b, True)
        roc.title = setup.title
        rocs.append(roc)

    makeROCPlot(rocs, 'rocs/'+scan_var_name, xmin=0.4, xmax=0.9, ymin=0.0001 if 'mva' in scan_var_name else 0.001, logy=True)
