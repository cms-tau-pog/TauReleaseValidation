vardict = {
'againstMuonLoose3': {'var': 'tau_againstMuonLoose3 > 0.5', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'againstMuonLoose3'},
'againstMuonTight3': {'var': 'tau_againstMuonTight3 > 0.5', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'againstMuonTight3'},

#'againstElectronVLooseMVA5':{'var':'tau_againstElectronVLooseMVA5 > 0.5', 'nbin':2, 'min':-0.5, 'max':1.5, 'title':'againstElectronVLooseMVA5'},
#'againstElectronLooseMVA5':{'var':'tau_againstElectronLooseMVA5 > 0.5', 'nbin':2, 'min':-0.5, 'max':1.5, 'title':'againstElectronLooseMVA5'},
#'againstElectronMediumMVA5':{'var':'tau_againstElectronMediumMVA5 > 0.5', 'nbin':2, 'min':-0.5, 'max':1.5, 'title':'againstElectronMediumMVA5'},

'againstElectronVLooseMVA6': {'var': 'tau_againstElectronVLooseMVA6 > 0.5', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'againstElectronVLooseMVA6'},
'againstElectronLooseMVA6': {'var': 'tau_againstElectronLooseMVA6 > 0.5', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'againstElectronLooseMVA6'},
'againstElectronMediumMVA6': {'var': 'tau_againstElectronMediumMVA6 > 0.5', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'againstElectronMediumMVA6'},

'oldDecayModeFinding': {'var': 'tau_decayModeFindingOldDMs > 0.5', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'oldDecayModeFinding'},
'newDecayModeFinding': {'var': 'tau_decayModeFindingNewDMs > 0.5', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'newDecayModeFinding'},
#'oldDecayModeFindingModified':{'var':'tau_decayModeFindingNewDMs > 0.5 && tau_dm != 5 && tau_dm != 6', 'nbin':2, 'min':-0.5, 'max':1.5, 'title':'oldDecayModeFinding w/ 3p+#pi^{0}'},
'oldDecayModeFindingModified': {'var': '(tau_decayModeFindingOldDMs > 0.5 || tau_dm == 11)', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'oldDecayModeFinding w/ 3p+#pi^{0}'},

# oldDM
#'byLoosePileupWeightedIsolation3Hits':{'var':'tau_byLoosePileupWeightedIsolation3Hits > 0.5 && tau_decayModeFindingOldDMs > 0.5', 'nbin':2, 'min':-0.5, 'max':1.5, 'title':'byLoosePileupWeightedIsolation3Hits'},
#'byMediumPileupWeightedIsolation3Hits':{'var':'tau_byMediumPileupWeightedIsolation3Hits > 0.5 && tau_decayModeFindingOldDMs > 0.5', 'nbin':2, 'min':-0.5, 'max':1.5, 'title':'byMediumPileupWeightedIsolation3Hits'},
#'byTightPileupWeightedIsolation3Hits':{'var':'tau_byTightPileupWeightedIsolation3Hits > 0.5 && tau_decayModeFindingOldDMs > 0.5', 'nbin':2, 'min':-0.5, 'max':1.5, 'title':'byTightPileupWeightedIsolation3Hits'},

'byLooseCombinedIsolationDeltaBetaCorr3Hits': {'var': 'tau_byLooseCombinedIsolationDeltaBetaCorr3Hits > 0.5 && tau_decayModeFindingOldDMs > 0.5', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'byLooseCombinedIsolationDeltaBetaCorr3Hits'},
'byMediumCombinedIsolationDeltaBetaCorr3Hits': {'var': 'tau_byMediumCombinedIsolationDeltaBetaCorr3Hits > 0.5 && tau_decayModeFindingOldDMs > 0.5', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'byMediumCombinedIsolationDeltaBetaCorr3Hits'},
'byTightCombinedIsolationDeltaBetaCorr3Hits': {'var': 'tau_byTightCombinedIsolationDeltaBetaCorr3Hits > 0.5 && tau_decayModeFindingOldDMs > 0.5', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'byTightCombinedIsolationDeltaBetaCorr3Hits'},

'byPtOutOfCone': {'var': 'tau_photonPtSumOutsideSignalCone/tau_pt < 0.1 && tau_decayModeFindingOldDMs > 0.5', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'out-of-cone-Pt/Pt < 0.1'},
'byLooseChargedIsolation': {'var': 'tau_chargedIsoPtSum < 2.5 && tau_decayModeFindingOldDMs > 0.5', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'charged iso < 2.5 GeV'},
'byMediumChargedIsolation': {'var': 'tau_chargedIsoPtSum < 1.5 && tau_decayModeFindingOldDMs > 0.5', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'charged iso < 1.5 GeV'},
'byTightChargedIsolation': {'var': 'tau_chargedIsoPtSum < 0.8 && tau_decayModeFindingOldDMs > 0.5', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'charged iso < 0.8 GeV'},
'byLooseNeutralIsolation': {'var': 'max(0,tau_neutralIsoPtSum-0.2*tau_puCorrPtSum) < 1.5 && tau_decayModeFindingOldDMs > 0.5', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': '(neutral-iso - 0.2*PU-Pt-Sum) < 1.5 GeV'},
'byMediumNeutralIsolation': {'var': 'max(0,tau_neutralIsoPtSum-0.2*tau_puCorrPtSum) < 1.0 && tau_decayModeFindingOldDMs > 0.5', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': '(neutral-iso - 0.2*PU-Pt-Sum) < 1 GeV'},
'byTightNeutralIsolation': {'var': 'max(0,tau_neutralIsoPtSum-0.2*tau_puCorrPtSum) < 0.5 && tau_decayModeFindingOldDMs > 0.5', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': '(neutral-iso - 0.2*PU-Pt-Sum) < 0.5 GeV'},
'byLooseNeutralIsolationUnCorr': {'var': 'tau_neutralIsoPtSum < 6 && tau_decayModeFindingOldDMs > 0.5', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'neutral-iso < 6 GeV'},
'byMediumNeutralIsolationUnCorr': {'var': 'tau_neutralIsoPtSum < 5 && tau_decayModeFindingOldDMs > 0.5', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'neutral-iso < 5 GeV'},
'byTightNeutralIsolationUnCorr': {'var': 'tau_neutralIsoPtSum < 4 && tau_decayModeFindingOldDMs > 0.5', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'neutral-iso < 4 GeV'},

#'byLooseIsolationMVA3oldDMwLT':{'var':'tau_byLooseIsolationMVA3oldDMwLT > 0.5 && tau_decayModeFindingOldDMs > 0.5', 'nbin':2, 'min':-0.5, 'max':1.5, 'title':'byLooseIsolationMVA3oldDMwLT'},
#'byMediumIsolationMVA3oldDMwLT':{'var':'tau_byMediumIsolationMVA3oldDMwLT > 0.5 && tau_decayModeFindingOldDMs > 0.5', 'nbin':2, 'min':-0.5, 'max':1.5, 'title':'byMediumIsolationMVA3oldDMwLT'},
#'byTightIsolationMVA3oldDMwLT':{'var':'tau_byTightIsolationMVA3oldDMwLT > 0.5 && tau_decayModeFindingOldDMs > 0.5', 'nbin':2, 'min':-0.5, 'max':1.5, 'title':'byTightIsolationMVA3oldDMwLT'},

'byLooseIsolationMVArun2v1DBoldDMwLT': {'var': 'tau_byLooseIsolationMVArun2v1DBoldDMwLT > 0.5 && tau_decayModeFindingOldDMs > 0.5', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'byLooseIsolationMVArun2v1DBoldDMwLT'},
'byMediumIsolationMVArun2v1DBoldDMwLT': {'var': 'tau_byMediumIsolationMVArun2v1DBoldDMwLT > 0.5 && tau_decayModeFindingOldDMs > 0.5', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'byMediumIsolationMVArun2v1DBoldDMwLT'},
'byTightIsolationMVArun2v1DBoldDMwLT': {'var': 'tau_byTightIsolationMVArun2v1DBoldDMwLT > 0.5 && tau_decayModeFindingOldDMs > 0.5', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'byTightIsolationMVArun2v1DBoldDMwLT'},

# newDM
'byLooseCombinedIsolationDeltaBetaCorr3Hits_newDM': {'var': 'tau_byLooseCombinedIsolationDeltaBetaCorr3Hits > 0.5 && tau_decayModeFindingNewDMs > 0.5', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'byLooseCombinedIsolationDeltaBetaCorr3Hits'},
'byMediumCombinedIsolationDeltaBetaCorr3Hits_newDM': {'var': 'tau_byMediumCombinedIsolationDeltaBetaCorr3Hits > 0.5 && tau_decayModeFindingNewDMs > 0.5', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'byMediumCombinedIsolationDeltaBetaCorr3Hits'},
'byTightCombinedIsolationDeltaBetaCorr3Hits_newDM': {'var': 'tau_byTightCombinedIsolationDeltaBetaCorr3Hits > 0.5 && tau_decayModeFindingNewDMs > 0.5', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'byTightCombinedIsolationDeltaBetaCorr3Hits'},

'byPtOutOfCone_newDM': {'var': 'tau_photonPtSumOutsideSignalCone/tau_pt < 0.1 && tau_decayModeFindingNewDMs > 0.5', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'out-of-cone-Pt/Pt < 0.1'},
'byLooseChargedIsolation_newDM': {'var': 'tau_chargedIsoPtSum < 2.5 && tau_decayModeFindingNewDMs > 0.5', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'charged iso < 2.5 GeV'},
'byMediumChargedIsolation_newDM': {'var': 'tau_chargedIsoPtSum < 1.5 && tau_decayModeFindingNewDMs > 0.5', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'charged iso < 1.5 GeV'},
'byTightChargedIsolation_newDM': {'var': 'tau_chargedIsoPtSum < 0.8 && tau_decayModeFindingNewDMs > 0.5', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'charged iso < 0.8 GeV'},
'byLooseNeutralIsolation_newDM': {'var': 'max(0,tau_neutralIsoPtSum-0.2*tau_puCorrPtSum) < 1.5 && tau_decayModeFindingNewDMs > 0.5', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': '(neutral-iso - 0.2*PU-Pt-Sum) < 1.5 GeV'},
'byMediumNeutralIsolation_newDM': {'var': 'max(0,tau_neutralIsoPtSum-0.2*tau_puCorrPtSum) < 1.0 && tau_decayModeFindingNewDMs > 0.5', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': '(neutral-iso - 0.2*PU-Pt-Sum) < 1 GeV'},
'byTightNeutralIsolation_newDM': {'var': 'max(0,tau_neutralIsoPtSum-0.2*tau_puCorrPtSum) < 0.5 && tau_decayModeFindingNewDMs > 0.5', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': '(neutral-iso - 0.2*PU-Pt-Sum) < 0.5 GeV'},
'byLooseNeutralIsolationUnCorr_newDM': {'var': 'tau_neutralIsoPtSum < 6 && tau_decayModeFindingNewDMs > 0.5', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'neutral-iso < 6 GeV'},
'byMediumNeutralIsolationUnCorr_newDM': {'var': 'tau_neutralIsoPtSum < 5 && tau_decayModeFindingNewDMs > 0.5', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'neutral-iso < 5 GeV'},
'byTightNeutralIsolationUnCorr_newDM': {'var': 'tau_neutralIsoPtSum < 4 && tau_decayModeFindingNewDMs > 0.5', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'neutral-iso < 4 GeV'},

# modOldDM
'byLooseCombinedIsolationDeltaBetaCorr3Hits_modOldDM': {'var': 'tau_byLooseCombinedIsolationDeltaBetaCorr3Hits > 0.5 && tau_decayModeFindingNewDMs > 0.5 && tau_dm != 5 && tau_dm != 6', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'byLooseCombinedIsolationDeltaBetaCorr3Hits'},
'byMediumCombinedIsolationDeltaBetaCorr3Hits_modOldDM': {'var': 'tau_byMediumCombinedIsolationDeltaBetaCorr3Hits > 0.5 && tau_decayModeFindingNewDMs > 0.5 && tau_dm != 5 && tau_dm != 6', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'byMediumCombinedIsolationDeltaBetaCorr3Hits'},
'byTightCombinedIsolationDeltaBetaCorr3Hits_modOldDM': {'var': 'tau_byTightCombinedIsolationDeltaBetaCorr3Hits > 0.5 && tau_decayModeFindingNewDMs > 0.5 && tau_dm != 5 && tau_dm != 6', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'byTightCombinedIsolationDeltaBetaCorr3Hits'},

'byPtOutOfCone_modOldDM': {'var': 'tau_photonPtSumOutsideSignalCone/tau_pt < 0.1 && tau_decayModeFindingNewDMs > 0.5 && tau_dm != 5 && tau_dm != 6', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'out-of-cone-Pt/Pt < 0.1'},
'byLooseChargedIsolation_modOldDM': {'var': 'tau_chargedIsoPtSum < 2.5 && tau_decayModeFindingNewDMs > 0.5 && tau_dm != 5 && tau_dm != 6', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'charged iso < 2.5 GeV'},
'byMediumChargedIsolation_modOldDM': {'var': 'tau_chargedIsoPtSum < 1.5 && tau_decayModeFindingNewDMs > 0.5 && tau_dm != 5 && tau_dm != 6', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'charged iso < 1.5 GeV'},
'byTightChargedIsolation_modOldDM': {'var': 'tau_chargedIsoPtSum < 0.8 && tau_decayModeFindingNewDMs > 0.5 && tau_dm != 5 && tau_dm != 6', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'charged iso < 0.8 GeV'},
'byLooseNeutralIsolation_modOldDM': {'var': 'max(0,tau_neutralIsoPtSum-0.2*tau_puCorrPtSum) < 1.5 && tau_decayModeFindingNewDMs > 0.5 && tau_dm != 5 && tau_dm != 6', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': '(neutral-iso - 0.2*PU-Pt-Sum) < 1.5 GeV'},
'byMediumNeutralIsolation_modOldDM': {'var': 'max(0,tau_neutralIsoPtSum-0.2*tau_puCorrPtSum) < 1.0 && tau_decayModeFindingNewDMs > 0.5 && tau_dm != 5 && tau_dm != 6', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': '(neutral-iso - 0.2*PU-Pt-Sum) < 1 GeV'},
'byTightNeutralIsolation_modOldDM': {'var': 'max(0,tau_neutralIsoPtSum-0.2*tau_puCorrPtSum) < 0.5 && tau_decayModeFindingNewDMs > 0.5 && tau_dm != 5 && tau_dm != 6', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': '(neutral-iso - 0.2*PU-Pt-Sum) < 0.5 GeV'},
'byLooseNeutralIsolationUnCorr_modOldDM': {'var': 'tau_neutralIsoPtSum < 6 && tau_decayModeFindingNewDMs > 0.5 && tau_dm != 5 && tau_dm != 6', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'neutral-iso < 6 GeV'},
'byMediumNeutralIsolationUnCorr_modOldDM': {'var': 'tau_neutralIsoPtSum < 5 && tau_decayModeFindingNewDMs > 0.5 && tau_dm != 5 && tau_dm != 6', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'neutral-iso < 5 GeV'},
'byTightNeutralIsolationUnCorr_modOldDM': {'var': 'tau_neutralIsoPtSum < 4 && tau_decayModeFindingNewDMs > 0.5 && tau_dm != 5 && tau_dm != 6', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'neutral-iso < 4 GeV'},


# 1prong
'byLooseCombinedIsolationDeltaBetaCorr3Hits_1p': {'var': 'tau_byLooseCombinedIsolationDeltaBetaCorr3Hits > 0.5 && tau_dm == 0', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'byLooseCombinedIsolationDeltaBetaCorr3Hits'},
'byMediumCombinedIsolationDeltaBetaCorr3Hits_1p': {'var': 'tau_byMediumCombinedIsolationDeltaBetaCorr3Hits > 0.5 && tau_dm == 0', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'byMediumCombinedIsolationDeltaBetaCorr3Hits'},
'byTightCombinedIsolationDeltaBetaCorr3Hits_1p': {'var': 'tau_byTightCombinedIsolationDeltaBetaCorr3Hits > 0.5 && tau_dm == 0', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'byTightCombinedIsolationDeltaBetaCorr3Hits'},

'byPtOutOfCone_1p': {'var': 'tau_photonPtSumOutsideSignalCone/tau_pt < 0.1 && tau_dm == 0', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'out-of-cone-Pt/Pt < 0.1'},
'byLooseChargedIsolation_1p': {'var': 'tau_chargedIsoPtSum < 2.5 && tau_dm == 0', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'charged iso < 2.5 GeV'},
'byMediumChargedIsolation_1p': {'var': 'tau_chargedIsoPtSum < 1.5 && tau_dm == 0', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'charged iso < 1.5 GeV'},
'byTightChargedIsolation_1p': {'var': 'tau_chargedIsoPtSum < 0.8 && tau_dm == 0', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'charged iso < 0.8 GeV'},
'byLooseNeutralIsolation_1p': {'var': 'max(0,tau_neutralIsoPtSum-0.2*tau_puCorrPtSum) < 1.5 && tau_dm == 0', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': '(neutral-iso - 0.2*PU-Pt-Sum) < 1.5 GeV'},
'byMediumNeutralIsolation_1p': {'var': 'max(0,tau_neutralIsoPtSum-0.2*tau_puCorrPtSum) < 1.0 && tau_dm == 0', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': '(neutral-iso - 0.2*PU-Pt-Sum) < 1 GeV'},
'byTightNeutralIsolation_1p': {'var': 'max(0,tau_neutralIsoPtSum-0.2*tau_puCorrPtSum) < 0.5 && tau_dm == 0', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': '(neutral-iso - 0.2*PU-Pt-Sum) < 0.5 GeV'},
'byLooseNeutralIsolationUnCorr_1p': {'var': 'tau_neutralIsoPtSum < 6 && tau_dm == 0', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'neutral-iso < 6 GeV'},
'byMediumNeutralIsolationUnCorr_1p': {'var': 'tau_neutralIsoPtSum < 5 && tau_dm == 0', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'neutral-iso < 5 GeV'},
'byTightNeutralIsolationUnCorr_1p': {'var': 'tau_neutralIsoPtSum < 4 && tau_dm == 0', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'neutral-iso < 4 GeV'},

'byLooseIsolationMVArun2v1DBoldDMwLT_1p': {'var': 'tau_byLooseIsolationMVArun2v1DBoldDMwLT > 0.5 && tau_dm == 0', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'byLooseIsolationMVArun2v1DBoldDMwLT'},
'byMediumIsolationMVArun2v1DBoldDMwLT_1p': {'var': 'tau_byMediumIsolationMVArun2v1DBoldDMwLT > 0.5 && tau_dm == 0', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'byMediumIsolationMVArun2v1DBoldDMwLT'},
'byTightIsolationMVArun2v1DBoldDMwLT_1p': {'var': 'tau_byTightIsolationMVArun2v1DBoldDMwLT > 0.5 && tau_dm == 0', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'byTightIsolationMVArun2v1DBoldDMwLT'},

# 1prong+pi0's
'byLooseCombinedIsolationDeltaBetaCorr3Hits_1ppi0': {'var': 'tau_byLooseCombinedIsolationDeltaBetaCorr3Hits > 0.5 && (tau_dm == 1 || tau_dm == 2)', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'byLooseCombinedIsolationDeltaBetaCorr3Hits'},
'byMediumCombinedIsolationDeltaBetaCorr3Hits_1ppi0': {'var': 'tau_byMediumCombinedIsolationDeltaBetaCorr3Hits > 0.5 && (tau_dm == 1 || tau_dm == 2)', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'byMediumCombinedIsolationDeltaBetaCorr3Hits'},
'byTightCombinedIsolationDeltaBetaCorr3Hits_1ppi0': {'var': 'tau_byTightCombinedIsolationDeltaBetaCorr3Hits > 0.5 && (tau_dm == 1 || tau_dm == 2)', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'byTightCombinedIsolationDeltaBetaCorr3Hits'},

'byPtOutOfCone_1ppi0': {'var': 'tau_photonPtSumOutsideSignalCone/tau_pt < 0.1 && (tau_dm == 1 || tau_dm == 2)', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'out-of-cone-Pt/Pt < 0.1'},
'byLooseChargedIsolation_1ppi0': {'var': 'tau_chargedIsoPtSum < 2.5 && (tau_dm == 1 || tau_dm == 2)', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'charged iso < 2.5 GeV'},
'byMediumChargedIsolation_1ppi0': {'var': 'tau_chargedIsoPtSum < 1.5 && (tau_dm == 1 || tau_dm == 2)', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'charged iso < 1.5 GeV'},
'byTightChargedIsolation_1ppi0': {'var': 'tau_chargedIsoPtSum < 0.8 && (tau_dm == 1 || tau_dm == 2)', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'charged iso < 0.8 GeV'},
'byLooseNeutralIsolation_1ppi0': {'var': 'max(0,tau_neutralIsoPtSum-0.2*tau_puCorrPtSum) < 1.5 && (tau_dm == 1 || tau_dm == 2)', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': '(neutral-iso - 0.2*PU-Pt-Sum) < 1.5 GeV'},
'byMediumNeutralIsolation_1ppi0': {'var': 'max(0,tau_neutralIsoPtSum-0.2*tau_puCorrPtSum) < 1.0 && (tau_dm == 1 || tau_dm == 2)', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': '(neutral-iso - 0.2*PU-Pt-Sum) < 1 GeV'},
'byTightNeutralIsolation_1ppi0': {'var': 'max(0,tau_neutralIsoPtSum-0.2*tau_puCorrPtSum) < 0.5 && (tau_dm == 1 || tau_dm == 2)', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': '(neutral-iso - 0.2*PU-Pt-Sum) < 0.5 GeV'},
'byLooseNeutralIsolationUnCorr_1ppi0': {'var': 'tau_neutralIsoPtSum < 6 && (tau_dm == 1 || tau_dm == 2)', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'neutral-iso < 6 GeV'},
'byMediumNeutralIsolationUnCorr_1ppi0': {'var': 'tau_neutralIsoPtSum < 5 && (tau_dm == 1 || tau_dm == 2)', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'neutral-iso < 5 GeV'},
'byTightNeutralIsolationUnCorr_1ppi0': {'var': 'tau_neutralIsoPtSum < 4 && (tau_dm == 1 || tau_dm == 2)', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'neutral-iso < 4 GeV'},

'byLooseIsolationMVArun2v1DBoldDMwLT_1ppi0': {'var': 'tau_byLooseIsolationMVArun2v1DBoldDMwLT > 0.5 && (tau_dm == 1 || tau_dm == 2)', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'byLooseIsolationMVArun2v1DBoldDMwLT'},
'byMediumIsolationMVArun2v1DBoldDMwLT_1ppi0': {'var': 'tau_byMediumIsolationMVArun2v1DBoldDMwLT > 0.5 && (tau_dm == 1 || tau_dm == 2)', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'byMediumIsolationMVArun2v1DBoldDMwLT'},
'byTightIsolationMVArun2v1DBoldDMwLT_1ppi0': {'var': 'tau_byTightIsolationMVArun2v1DBoldDMwLT > 0.5 && (tau_dm == 1 || tau_dm == 2)', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'byTightIsolationMVArun2v1DBoldDMwLT'},

# 2prongs
'byLooseCombinedIsolationDeltaBetaCorr3Hits_2p': {'var': 'tau_byLooseCombinedIsolationDeltaBetaCorr3Hits > 0.5 && (tau_dm == 5 || tau_dm==6)', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'byLooseCombinedIsolationDeltaBetaCorr3Hits'},
'byMediumCombinedIsolationDeltaBetaCorr3Hits_2p': {'var': 'tau_byMediumCombinedIsolationDeltaBetaCorr3Hits > 0.5 && (tau_dm == 5 || tau_dm==6)', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'byMediumCombinedIsolationDeltaBetaCorr3Hits'},
'byTightCombinedIsolationDeltaBetaCorr3Hits_2p': {'var': 'tau_byTightCombinedIsolationDeltaBetaCorr3Hits > 0.5 && (tau_dm == 5 || tau_dm==6)', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'byTightCombinedIsolationDeltaBetaCorr3Hits'},

'byPtOutOfCone_2p': {'var': 'tau_photonPtSumOutsideSignalCone/tau_pt < 0.1 && (tau_dm == 5 || tau_dm==6)', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'out-of-cone-Pt/Pt < 0.1'},
'byLooseChargedIsolation_2p': {'var': 'tau_chargedIsoPtSum < 2.5 && (tau_dm == 5 || tau_dm==6)', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'charged iso < 2.5 GeV'},
'byMediumChargedIsolation_2p': {'var': 'tau_chargedIsoPtSum < 1.5 && (tau_dm == 5 || tau_dm==6)', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'charged iso < 1.5 GeV'},
'byTightChargedIsolation_2p': {'var': 'tau_chargedIsoPtSum < 0.8 && (tau_dm == 5 || tau_dm==6)', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'charged iso < 0.8 GeV'},
'byLooseNeutralIsolation_2p': {'var': 'max(0,tau_neutralIsoPtSum-0.2*tau_puCorrPtSum) < 1.5 && (tau_dm == 5 || tau_dm==6)', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': '(neutral-iso - 0.2*PU-Pt-Sum) < 1.5 GeV'},
'byMediumNeutralIsolation_2p': {'var': 'max(0,tau_neutralIsoPtSum-0.2*tau_puCorrPtSum) < 1.0 && (tau_dm == 5 || tau_dm==6)', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': '(neutral-iso - 0.2*PU-Pt-Sum) < 1 GeV'},
'byTightNeutralIsolation_2p': {'var': 'max(0,tau_neutralIsoPtSum-0.2*tau_puCorrPtSum) < 0.5 && (tau_dm == 5 || tau_dm==6)', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': '(neutral-iso - 0.2*PU-Pt-Sum) < 0.5 GeV'},
'byLooseNeutralIsolationUnCorr_2p': {'var': 'tau_neutralIsoPtSum < 6 && (tau_dm == 5 || tau_dm==6)', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'neutral-iso < 6 GeV'},
'byMediumNeutralIsolationUnCorr_2p': {'var': 'tau_neutralIsoPtSum < 5 && (tau_dm == 5 || tau_dm==6)', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'neutral-iso < 5 GeV'},
'byTightNeutralIsolationUnCorr_2p': {'var': 'tau_neutralIsoPtSum < 4 && (tau_dm == 5 || tau_dm==6)', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'neutral-iso < 4 GeV'},

# 3prongs
'byLooseCombinedIsolationDeltaBetaCorr3Hits_3p': {'var': 'tau_byLooseCombinedIsolationDeltaBetaCorr3Hits > 0.5 && (tau_dm == 10 || tau_dm == 11)', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'byLooseCombinedIsolationDeltaBetaCorr3Hits'},
'byMediumCombinedIsolationDeltaBetaCorr3Hits_3p': {'var': 'tau_byMediumCombinedIsolationDeltaBetaCorr3Hits > 0.5 && (tau_dm == 10 || tau_dm == 11)', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'byMediumCombinedIsolationDeltaBetaCorr3Hits'},
'byTightCombinedIsolationDeltaBetaCorr3Hits_3p': {'var': 'tau_byTightCombinedIsolationDeltaBetaCorr3Hits > 0.5 && (tau_dm == 10 || tau_dm == 11)', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'byTightCombinedIsolationDeltaBetaCorr3Hits'},

'byPtOutOfCone_3p': {'var': 'tau_photonPtSumOutsideSignalCone/tau_pt < 0.1 && (tau_dm == 10 || tau_dm == 11)', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'out-of-cone-Pt/Pt < 0.1'},
'byLooseChargedIsolation_3p': {'var': 'tau_chargedIsoPtSum < 2.5 && (tau_dm == 10 || tau_dm == 11)', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'charged iso < 2.5 GeV'},
'byMediumChargedIsolation_3p': {'var': 'tau_chargedIsoPtSum < 1.5 && (tau_dm == 10 || tau_dm == 11)', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'charged iso < 1.5 GeV'},
'byTightChargedIsolation_3p': {'var': 'tau_chargedIsoPtSum < 0.8 && (tau_dm == 10 || tau_dm == 11)', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'charged iso < 0.8 GeV'},
'byLooseNeutralIsolation_3p': {'var': 'max(0,tau_neutralIsoPtSum-0.2*tau_puCorrPtSum) < 1.5 && (tau_dm == 10 || tau_dm == 11)', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': '(neutral-iso - 0.2*PU-Pt-Sum) < 1.5 GeV'},
'byMediumNeutralIsolation_3p': {'var': 'max(0,tau_neutralIsoPtSum-0.2*tau_puCorrPtSum) < 1.0 && (tau_dm == 10 || tau_dm == 11)', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': '(neutral-iso - 0.2*PU-Pt-Sum) < 1 GeV'},
'byTightNeutralIsolation_3p': {'var': 'max(0,tau_neutralIsoPtSum-0.2*tau_puCorrPtSum) < 0.5 && (tau_dm == 10 || tau_dm == 11)', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': '(neutral-iso - 0.2*PU-Pt-Sum) < 0.5 GeV'},
'byLooseNeutralIsolationUnCorr_3p': {'var': 'tau_neutralIsoPtSum < 6 && (tau_dm == 10 || tau_dm == 11)', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'neutral-iso < 6 GeV'},
'byMediumNeutralIsolationUnCorr_3p': {'var': 'tau_neutralIsoPtSum < 5 && (tau_dm == 10 || tau_dm == 11)', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'neutral-iso < 5 GeV'},
'byTightNeutralIsolationUnCorr_3p': {'var': 'tau_neutralIsoPtSum < 4 && (tau_dm == 10 || tau_dm == 11)', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'neutral-iso < 4 GeV'},

# 3prongs classic
'byLooseCombinedIsolationDeltaBetaCorr3Hits_3pold': {'var': 'tau_byLooseCombinedIsolationDeltaBetaCorr3Hits > 0.5 && tau_dm == 10', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'byLooseCombinedIsolationDeltaBetaCorr3Hits'},
'byMediumCombinedIsolationDeltaBetaCorr3Hits_3pold': {'var': 'tau_byMediumCombinedIsolationDeltaBetaCorr3Hits > 0.5 && tau_dm == 10', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'byMediumCombinedIsolationDeltaBetaCorr3Hits'},
'byTightCombinedIsolationDeltaBetaCorr3Hits_3pold': {'var': 'tau_byTightCombinedIsolationDeltaBetaCorr3Hits > 0.5 && tau_dm == 10', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'byTightCombinedIsolationDeltaBetaCorr3Hits'},

'byPtOutOfCone_3pold': {'var': 'tau_photonPtSumOutsideSignalCone/tau_pt < 0.1 && tau_dm == 10', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'out-of-cone-Pt/Pt < 0.1'},
'byLooseChargedIsolation_3pold': {'var': 'tau_chargedIsoPtSum < 2.5 && tau_dm == 10', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'charged iso < 2.5 GeV'},
'byMediumChargedIsolation_3pold': {'var': 'tau_chargedIsoPtSum < 1.5 && tau_dm == 10', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'charged iso < 1.5 GeV'},
'byTightChargedIsolation_3pold': {'var': 'tau_chargedIsoPtSum < 0.8 && tau_dm == 10', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'charged iso < 0.8 GeV'},
'byLooseNeutralIsolation_3pold': {'var': 'max(0,tau_neutralIsoPtSum-0.2*tau_puCorrPtSum) < 1.5 && tau_dm == 10', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': '(neutral-iso - 0.2*PU-Pt-Sum) < 1.5 GeV'},
'byMediumNeutralIsolation_3pold': {'var': 'max(0,tau_neutralIsoPtSum-0.2*tau_puCorrPtSum) < 1.0 && tau_dm == 10', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': '(neutral-iso - 0.2*PU-Pt-Sum) < 1 GeV'},
'byTightNeutralIsolation_3pold': {'var': 'max(0,tau_neutralIsoPtSum-0.2*tau_puCorrPtSum) < 0.5 && tau_dm == 10', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': '(neutral-iso - 0.2*PU-Pt-Sum) < 0.5 GeV'},
'byLooseNeutralIsolationUnCorr_3pold': {'var': 'tau_neutralIsoPtSum < 6 && tau_dm == 10', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'neutral-iso < 6 GeV'},
'byMediumNeutralIsolationUnCorr_3pold': {'var': 'tau_neutralIsoPtSum < 5 && tau_dm == 10', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'neutral-iso < 5 GeV'},
'byTightNeutralIsolationUnCorr_3pold': {'var': 'tau_neutralIsoPtSum < 4 && tau_dm == 10', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'neutral-iso < 4 GeV'},

'byLooseIsolationMVArun2v1DBoldDMwLT_3pold': {'var': 'tau_byLooseIsolationMVArun2v1DBoldDMwLT > 0.5 && tau_dm == 10', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'byLooseIsolationMVArun2v1DBoldDMwLT'},
'byMediumIsolationMVArun2v1DBoldDMwLT_3pold': {'var': 'tau_byMediumIsolationMVArun2v1DBoldDMwLT > 0.5 && tau_dm == 10', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'byMediumIsolationMVArun2v1DBoldDMwLT'},
'byTightIsolationMVArun2v1DBoldDMwLT_3pold': {'var': 'tau_byTightIsolationMVArun2v1DBoldDMwLT > 0.5 && tau_dm == 10', 'nbin': 2, 'min': -0.5, 'max': 1.5, 'title': 'byTightIsolationMVArun2v1DBoldDMwLT'},
}