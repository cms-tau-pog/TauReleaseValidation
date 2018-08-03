''' Produces a flat tree for tau release/data validation.
Authors: Yuta Takahashi, Michal Bluj, Jan Steggemann.
'''

import math
import sys
import os
import argparse
import copy
import subprocess
import numpy as num

from DataFormats.FWLite import Events, Handle
from PhysicsTools.HeppyCore.utils.deltar import deltaR, bestMatch
from PhysicsTools.Heppy.physicsutils.TauDecayModes import tauDecayModes
from relValTools import addArguments, getFilesFromEOS, getFilesFromDAS, is_above_cmssw_version, runtype_to_sample

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

ROOT.gROOT.SetBatch(True)


class Var(object):
    def __init__(self, name, vtype):
        self.name = name
        self.type = vtype
        self.storage = None

    def reset(self):
        self.storage[0] = -999

    def fill(self, val):
        self.storage[0] = val

    def add(self, val):
        self.storage[0] += val

    def __str__(self):
        return 'Var: name={}, vtype={}, val={:.2f}'.format(self.name, self.type, self.storage[0])


def returnRough(dm):
    if dm in [0]:
        return 0
    elif dm in [1, 2]:
        return 1
    elif dm in [5, 6]:
        return 2
    elif dm in [10]:
        return 3
    elif dm in [11]:
        return 4
    else:
        return -1


def finalDaughters(gen, daughters=None):
    if daughters is None:
        daughters = []
    for i in range(gen.numberOfDaughters()):
        daughter = gen.daughter(i)
        if daughter.numberOfDaughters() == 0:
            daughters.append(daughter)
        else:
            finalDaughters(daughter, daughters)

    return daughters


def visibleP4(gen):
    final_ds = finalDaughters(gen)

    return sum((d.p4() for d in final_ds if abs(d.pdgId()) not in [12, 14, 16]), ROOT.math.XYZTLorentzVectorD())


def getNonTauJets(all_jets, gen_leptons):
    non_tau_jets = []
    for j_cand in all_jets:
        if not any(deltaR(j_cand, lep) < 0.5 for lep in gen_leptons):
            non_tau_jets.append(j_cand)

    return non_tau_jets

def fill_tau_ids(avd, tau_ids):
    for (tau_id, _) in tau_ids:
        avd['tau_'+tau_id].fill(tau.tauID(tau_id))

all_tau_ids = [
    ('againstMuonLoose3', int),
    ('againstMuonTight3', int),
    ('byIsolationMVA3oldDMwLTraw', float),
    ('byLooseIsolationMVA3oldDMwLT', int),
    ('byMediumIsolationMVA3oldDMwLT', int),
    ('byTightIsolationMVA3oldDMwLT', int),
    ('byVLooseIsolationMVA3oldDMwLT', int),
    ('byVTightIsolationMVA3oldDMwLT', int),
    ('byVVTightIsolationMVA3oldDMwLT', int),
    ('byCombinedIsolationDeltaBetaCorrRaw3Hits', float),
    ('byLooseCombinedIsolationDeltaBetaCorr3Hits', int),
    ('byMediumCombinedIsolationDeltaBetaCorr3Hits', int),
    ('byTightCombinedIsolationDeltaBetaCorr3Hits', int),
    ('byIsolationMVArun2v1DBoldDMwLTraw', float),
    ('byVLooseIsolationMVArun2v1DBoldDMwLT', int),
    ('byLooseIsolationMVArun2v1DBoldDMwLT', int),
    ('byMediumIsolationMVArun2v1DBoldDMwLT', int),
    ('byTightIsolationMVArun2v1DBoldDMwLT', int),
    ('byVTightIsolationMVArun2v1DBoldDMwLT', int),
    ('byVVTightIsolationMVArun2v1DBoldDMwLT', int),
    ('byIsolationMVArun2v1PWoldDMwLTraw', float),
    ('byLooseIsolationMVArun2v1PWoldDMwLT', int),
    ('byMediumIsolationMVArun2v1PWoldDMwLT', int),
    ('byTightIsolationMVArun2v1PWoldDMwLT', int),
    ('byVLooseIsolationMVArun2v1PWoldDMwLT', int),
    ('byVTightIsolationMVArun2v1PWoldDMwLT', int),
    ('byVVTightIsolationMVArun2v1PWoldDMwLT', int),
    ('byIsolationMVArun2v1DBdR03oldDMwLTraw', float),
    ('byLooseIsolationMVArun2v1DBdR03oldDMwLT', int),
    ('byMediumIsolationMVArun2v1DBdR03oldDMwLT', int),
    ('byTightIsolationMVArun2v1DBdR03oldDMwLT', int),
    ('byVLooseIsolationMVArun2v1DBdR03oldDMwLT', int),
    ('byVTightIsolationMVArun2v1DBdR03oldDMwLT', int),
    ('byVVTightIsolationMVArun2v1DBdR03oldDMwLT', int),
    ('chargedIsoPtSum', float),
    ('neutralIsoPtSum', float),
    ('puCorrPtSum', float),
    ('neutralIsoPtSumWeight', float),
    ('footprintCorrection', float),
    ('photonPtSumOutsideSignalCone', float),
    ('decayModeFindingOldDMs', int),
    ('decayModeFindingNewDMs', int),
    ('againstElectronVLooseMVA6', int),
    ('againstElectronLooseMVA6', int),
    ('againstElectronMediumMVA6', int),
    ('againstElectronTightMVA6', int),
    ('againstElectronVTightMVA6', int),
    ('againstElectronMVA6raw', float),
]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    addArguments(parser, compare=False)
    args = parser.parse_args()

    maxEvents = args.maxEvents
    RelVal = args.release
    globalTag = args.globalTag
    useRecoJets = args.useRecoJets
    storageSite = args.storageSite
    localdir = args.localdir
    tauCollection = args.tauCollection
    mvaid = args.mvaid
    if len(localdir) > 1 and localdir[-1] != "/":
        localdir += "/"
    debug = args.debug
    inputfile = args.inputfile

    runtype = args.runtype

    print 'Running with'
    print 'runtype', runtype
    print 'RelVal', RelVal
    print 'globalTag', globalTag
    print 'storageSite', storageSite

    filelist = []

    if inputfile != "":
        filelist = [inputfile]
    else:
        path = '/store/relval/{}/{}/MINIAODSIM/{}'.format(
            RelVal, runtype_to_sample[runtype], globalTag)

        if storageSite == "eos":
            filelist = getFilesFromEOS(path)
        elif storageSite == "das":
            filelist = getFilesFromDAS(
                RelVal, runtype_to_sample[runtype], globalTag)
        elif storageSite == 'loc':
            filelist = getFilesFromEOS(
                localdir + runtype_to_sample[runtype] + "/" + RelVal + '-' + globalTag + '/', cmseospath=False)

        if not filelist:
            print 'Sample', RelVal, runtype, 'does not exist in', path
            sys.exit(0)

    print len(filelist), "files will be analyzed:", filelist, '\nEvents will be analyzed: %i' % maxEvents
    events = Events(filelist)

    ######## Output file ########
    outputFileName = args.outputFileName
    if not outputFileName:
        if storageSite == 'loc':
            outputFileName = localdir + \
                runtype_to_sample[runtype] + "/" + RelVal + \
                '-' + globalTag + '/' + 'TauValTree/'
            if not os.path.isdir(outputFileName):
                result = subprocess.check_output(
                    "mkdir -p {outputFileName}".format(outputFileName=outputFileName), shell=True)

        genJetssuffix = ""
        if not useRecoJets and (runtype == 'QCD' or runtype == 'TTBar'):
            genJetssuffix = "_genJets"

        outputFileName += 'Myroot_' + RelVal + '_' + \
            globalTag + '_' + runtype + genJetssuffix + '.root'
    else:
        if "/" in outputFileName and outputFileName[0] != "/":
            print "location of output file has a dir structure but doesn't start with dash"
            sys.exit(0)
        if outputFileName[-5:] != ".root":
            outputFileName += '.root'
            print "output file should have a root format - added automatically:", outputFileName

    print "outputFileName:", outputFileName

    out_file = ROOT.TFile(outputFileName, 'recreate')

    h_ngen = ROOT.TH1F("h_ngen", "h_ngen", 10, 0, 10)
    h_pfch_pt = ROOT.TH1F("h_pfch_pt", "pfch;p_{T} (GeV)", 500, 0, 500)
    h_pfch_eta = ROOT.TH1F("h_pfch_eta", "pfch;#eta", 50, -2.5, 2.5)
    h_pfch_phi = ROOT.TH1F("h_pfch_phi", "pfch;#phi", 64, -3.2, 3.2)
    h_pfne_pt = ROOT.TH1F("h_pfne_pt", "pfne;p_{T} (GeV)", 500, 0, 500)
    h_pfne_eta = ROOT.TH1F("h_pfne_eta", "pfne;#eta", 50, -2.5, 2.5)
    h_pfne_phi = ROOT.TH1F("h_pfne_phi", "pfne;#phi", 64, -3.2, 3.2)
    h_pfph_pt = ROOT.TH1F("h_pfph_pt", "pfph;p_{T} (GeV)", 500, 0, 500)
    h_pfph_eta = ROOT.TH1F("h_pfph_eta", "pfph;#eta", 50, -2.5, 2.5)
    h_pfph_phi = ROOT.TH1F("h_pfph_phi", "pfph;#phi", 64, -3.2, 3.2)
    h_lost_pt = ROOT.TH1F("h_lost_pt", "lost;p_{T} (GeV)", 500, 0, 500)
    h_lost_eta = ROOT.TH1F("h_lost_eta", "lost;#eta", 50, -2.5, 2.5)
    h_lost_phi = ROOT.TH1F("h_lost_phi", "lost;#phi", 64, -3.2, 3.2)

    tau_tree = ROOT.TTree('per_tau', 'per_tau')

    all_vars = [
        Var('tau_eventid', int),
        Var('tau_id', int),
        Var('tau_dm', int),
        Var('tau_dm_rough', int),
        Var('tau_pt', float),
        Var('tau_eta', float),
        Var('tau_phi', float),
        Var('tau_mass', float),
        Var('tau_gendm', int),
        Var('tau_gendm_rough', int),
        Var('tau_genpt', float),
        Var('tau_geneta', float),
        Var('tau_genphi', float),
        Var('tau_vertex', int),
        Var('tau_nTruePU', float),
        Var('tau_nPU', int),
        Var('tau_vtxTovtx_dz', float),
        Var('tau_tauVtxTovtx_dz', float),
        Var('tau_iso_dz001', float),
        Var('tau_iso_dz02', float),
        Var('tau_iso_pv', float),
        Var('tau_iso_nopv', float),
        Var('tau_iso_neu', float),
        Var('tau_iso_puppi', float),
        Var('tau_iso_puppiNoL', float),
        Var('tau_dxy', float),
        Var('tau_dxy_err', float),
        Var('tau_dxy_sig', float),
        Var('tau_ip3d', float),
        Var('tau_ip3d_err', float),
        Var('tau_ip3d_sig', float),
        Var('tau_flightLength', float),
        Var('tau_flightLength_sig', float)
    ]

    if "2017v2" in mvaid:
        all_tau_ids += [("byIsolationMVArun2017v2DBoldDMwLTraw2017", float),
                         ("byVVLooseIsolationMVArun2017v2DBoldDMwLT2017", int),
                         ("byVLooseIsolationMVArun2017v2DBoldDMwLT2017", int),
                         ("byLooseIsolationMVArun2017v2DBoldDMwLT2017", int),
                         ("byMediumIsolationMVArun2017v2DBoldDMwLT2017", int),
                         ("byTightIsolationMVArun2017v2DBoldDMwLT2017", int),
                         ("byVTightIsolationMVArun2017v2DBoldDMwLT2017", int),
                         ("byVVTightIsolationMVArun2017v2DBoldDMwLT2017", int)]
    if "2017v1" in mvaid:
        all_tau_ids += [("byIsolationMVArun2017v1DBoldDMwLTraw2017", float),
                         ("byVVLooseIsolationMVArun2017v1DBoldDMwLT2017", int),
                         ("byVLooseIsolationMVArun2017v1DBoldDMwLT2017", int),
                         ("byLooseIsolationMVArun2017v1DBoldDMwLT2017", int),
                         ("byMediumIsolationMVArun2017v1DBoldDMwLT2017", int),
                         ("byTightIsolationMVArun2017v1DBoldDMwLT2017", int),
                         ("byVTightIsolationMVArun2017v1DBoldDMwLT2017", int),
                         ("byVVTightIsolationMVArun2017v1DBoldDMwLT2017", int)]
    if "2016v1" in mvaid:
        all_tau_ids += [("byIsolationMVArun2v1DBoldDMwLTraw2016", float),
                         ("byVLooseIsolationMVArun2v1DBoldDMwLT2016", int),
                         ("byLooseIsolationMVArun2v1DBoldDMwLT2016", int),
                         ("byMediumIsolationMVArun2v1DBoldDMwLT2016", int),
                         ("byTightIsolationMVArun2v1DBoldDMwLT2016", int),
                         ("byVTightIsolationMVArun2v1DBoldDMwLT2016", int),
                         ("byVVTightIsolationMVArun2v1DBoldDMwLT2016", int)]
    if "newDM2016v1" in mvaid:
        all_tau_ids += [("byIsolationMVArun2v1DBnewDMwLTraw2016", float),
                         ("byVLooseIsolationMVArun2v1DBnewDMwLT2016", int),
                         ("byLooseIsolationMVArun2v1DBnewDMwLT2016", int),
                         ("byMediumIsolationMVArun2v1DBnewDMwLT2016", int),
                         ("byTightIsolationMVArun2v1DBnewDMwLT2016", int),
                         ("byVTightIsolationMVArun2v1DBnewDMwLT2016", int),
                         ("byVVTightIsolationMVArun2v1DBnewDMwLT2016", int)]
    if "dR0p32017v2" in mvaid:
        all_tau_ids += [("byIsolationMVArun2017v2DBoldDMdR0p3wLTraw2017", float),
                         ("byVVLooseIsolationMVArun2017v2DBoldDMdR0p3wLT2017", int),
                         ("byVLooseIsolationMVArun2017v2DBoldDMdR0p3wLT2017", int),
                         ("byLooseIsolationMVArun2017v2DBoldDMdR0p3wLT2017", int),
                         ("byMediumIsolationMVArun2017v2DBoldDMdR0p3wLT2017", int),
                         ("byTightIsolationMVArun2017v2DBoldDMdR0p3wLT2017", int),
                         ("byVTightIsolationMVArun2017v2DBoldDMdR0p3wLT2017", int),
                         ("byVVTightIsolationMVArun2017v2DBoldDMdR0p3wLT2017", int)]

    for (tau_id, v_type) in all_tau_ids:
        all_vars.append('tau_'+tau_id, v_type)



    all_var_dict = {var.name: var for var in all_vars}

    for var in all_vars:
        var.storage = num.zeros(1, dtype=var.type)
        tau_tree.Branch(var.name, var.storage, var.name +
                        '/'+('I' if var.type == int else 'D'))

    evtid = 0

    NMatchedTaus = 0

    tauH = Handle('vector<pat::Tau>')
    vertexH = Handle('std::vector<reco::Vertex>')
    genParticlesH = Handle('std::vector<reco::GenParticle>')
    jetH = Handle('vector<pat::Jet>')
    genJetH = Handle('vector<reco::GenJet>')
    puH = Handle('std::vector<PileupSummaryInfo>')
    candH = Handle('vector<pat::PackedCandidate>')
    lostH = Handle('vector<pat::PackedCandidate>')

    for event in events:
        for var in all_vars:
            var.reset()

        evtid += 1
        eid = event.eventAuxiliary().id().event()

        if evtid % 1000 == 0:
            print 'Event ', evtid, 'processed'
        if evtid > maxEvents and maxEvents > 0:
            break

        event.getByLabel(tauCollection, tauH)
        event.getByLabel("offlineSlimmedPrimaryVertices", vertexH)
        event.getByLabel("slimmedAddPileupInfo", puH)
        event.getByLabel('prunedGenParticles', genParticlesH)
        event.getByLabel("slimmedJets", jetH)
        event.getByLabel("slimmedGenJets", genJetH)
        # event.getByLabel("slimmedGenJets", reRunTauID)

        event.getByLabel("packedPFCandidates", candH)
        pfCands = candH.product()
        event.getByLabel("lostTracks", lostH)
        lostCands = lostH.product()

        for cand in pfCands:
            if abs(cand.pdgId()) == 211:
                h_pfch_pt.Fill(cand.pt())
                h_pfch_phi.Fill(cand.phi())
                h_pfch_eta.Fill(cand.eta())
            elif abs(cand.pdgId()) == 22:
                h_pfph_pt.Fill(cand.pt())
                h_pfph_phi.Fill(cand.phi())
                h_pfph_eta.Fill(cand.eta())
            elif abs(cand.pdgId()) == 130:
                h_pfne_pt.Fill(cand.pt())
                h_pfne_phi.Fill(cand.phi())
                h_pfne_eta.Fill(cand.eta())
        for cand in lostCands:
            h_lost_pt.Fill(cand.pt())
            h_lost_phi.Fill(cand.phi())
            h_lost_eta.Fill(cand.eta())

        taus = tauH.product()
        vertices = vertexH.product()
        puInfo = puH.product()
        genParticles = genParticlesH.product()
        jets1 = [jet for jet in jetH.product() if jet.pt() > 20 and abs(
            jet.eta()) < 2.3 and jet.pt() < 200.5]
        genJets1 = [jet for jet in genJetH.product() if jet.pt(
        ) > 20 and abs(jet.eta()) < 2.3 and jet.pt() < 200.5]

        genTaus = [p for p in genParticles if abs(
            p.pdgId()) == 15 and p.isPromptDecayed()]

        def accompanyingLeptonCondition(p, pid): 
            return (abs(p.pdgId()) == pid
                    and p.status() == 1
                    and (p.isPromptFinalState() or p.isDirectPromptTauDecayProductFinalState())
                    and p.pt() > 20
                    and abs(p.eta()) < 2.3)

        genElectrons = [
            p for p in genParticles if accompanyingLeptonCondition(p, 11)]
        genMuons = [
            p for p in genParticles if accompanyingLeptonCondition(p, 13)]

        # gen leptons to clean jets with respect to them (e.g. for TTBar)
        genLeptons = [p for p in genParticles if
                      p.status() == 1 and p.pt() > 15
                      and (((abs(p.pdgId()) == 11 or abs(p.pdgId()) == 13) and p.isPromptFinalState())
                           or (abs(p.pdgId()) == 15 and p.isPromptDecayed()))]

        if debug:
            print "Jets processing:"
        jets = getNonTauJets(jets1, genLeptons)

        if debug:
            print "GenJets processing:"
        genJets = getNonTauJets(genJets1, genLeptons)

        refObjs = []
        if runtype in ['ZTT', 'TTbarTau']:
            for igen in genTaus:
                visP4 = visibleP4(igen)

                gen_dm = tauDecayModes.genDecayModeInt(
                    [d for d in finalDaughters(igen) if abs(d.pdgId()) not in [12, 14, 16]])
                if abs(visP4.eta()) > 2.3:
                    continue
                if visP4.pt() < 10:
                    continue
                if gen_dm == -11 or gen_dm == -13:
                    continue

                refObjs.append(igen)

                #gp = _genparticle_[0]
                #tau_gendm[0] = gp.decaymode
                #tau_gendm_rough[0] = returnRough(gp.decaymode)
                #tau_genpt[0] = gp.vis.pt()
                #tau_geneta[0] = gp.vis.eta()
                #tau_genphi[0] = gp.vis.phi()
        elif runtype in ['QCD', 'TTbar']:
            if useRecoJets:
                refObjs = copy.deepcopy(jets)
            else:
                refObjs = copy.deepcopy(genJets)
        elif runtype == 'ZEE':
            refObjs = copy.deepcopy(genElectrons)
        elif runtype == 'ZMM':
            refObjs = copy.deepcopy(genMuons)

        ###
        h_ngen.Fill(len(refObjs))
        for refObj in refObjs:
            all_var_dict['tau_id'].fill(evtid)
            all_var_dict['tau_eventid'].fill(eid)
            all_var_dict['tau_vertex'].fill(len(vertices))
            for iPuInfo in puInfo:
                if iPuInfo.getBunchCrossing() == 0:
                    all_var_dict['tau_nTruePU'].fill(
                        iPuInfo.getTrueNumInteractions())
                    all_var_dict['tau_nPU'].fill(
                        iPuInfo.getPU_NumInteractions())
                    break

            if runtype == 'ZTT' or runtype == 'TTbarTau':
                visP4 = visibleP4(refObj)
                gen_dm = tauDecayModes.genDecayModeInt(
                    [d for d in finalDaughters(refObj) if abs(d.pdgId()) not in [12, 14, 16]])
                all_var_dict['tau_gendm'].fill(gen_dm)
                all_var_dict['tau_gendm_rough'].fill(returnRough(gen_dm))
                all_var_dict['tau_genpt'].fill(visP4.pt())
                all_var_dict['tau_geneta'].fill(visP4.eta())
                all_var_dict['tau_genphi'].fill(visP4.phi())
            else:
                all_var_dict['tau_gendm'].fill(-1)
                all_var_dict['tau_gendm_rough'].fill(-1)
                all_var_dict['tau_genpt'].fill(refObj.pt())
                all_var_dict['tau_geneta'].fill(refObj.eta())
                all_var_dict['tau_genphi'].fill(refObj.phi())

            tau_vtxTovtx_dz = 99
            for i in range(0, len(vertices)-1):
                for j in range(i + 1, len(vertices)):

                    vtxdz = abs(vertices[i].z()-vertices[j].z())
                    if vtxdz < tau_vtxTovtx_dz:
                        tau_vtxTovtx_dz = vtxdz

            all_var_dict['tau_vtxTovtx_dz'].fill(tau_vtxTovtx_dz)

            tau, _dr_ = bestMatch(refObj, taus)
            if _dr_ < 0.5:
                # Fill reco-tau variables if it exists...
                NMatchedTaus += 1

                if debug:
                    print tau

                all_var_dict['tau_dm'].fill(tau.decayMode())
                all_var_dict['tau_dm_rough'].fill(returnRough(tau.decayMode()))
                all_var_dict['tau_pt'].fill(tau.pt())
                all_var_dict['tau_eta'].fill(tau.eta())
                all_var_dict['tau_phi'].fill(tau.phi())
                all_var_dict['tau_mass'].fill(tau.mass())

                # Use candidate to vertex associaton as in MiniAOD
                tau_vertex_idxpf = tau.leadChargedHadrCand().vertexRef().key()
                # or take vertex closest in dz as in tau code
                #min_dz = 99
                # for i in range(0,len(vertices)):
                #    tmp_dz = abs(tau.leadChargedHadrCand().dz(vertices[i].position()))
                #    if tmp_dz<min_dz:
                #        min_dz = tmp_dz
                #        tau_vertex_idxpf = i

                tau_tauVtxTovtx_dz = 99
                for i, vertex in enumerate(vertices):

                    if i == tau_vertex_idxpf:
                        continue

                    vtxdz = abs(vertex.z() - vertices[tau_vertex_idxpf].z())
                    if vtxdz < tau_tauVtxTovtx_dz:
                        tau_tauVtxTovtx_dz = vtxdz

                all_var_dict['tau_tauVtxTovtx_dz'].fill(tau_tauVtxTovtx_dz)
                all_var_dict['tau_iso_dz001'].fill(0.)
                all_var_dict['tau_iso_dz02'].fill(0.)
                all_var_dict['tau_iso_pv'].fill(0.)
                all_var_dict['tau_iso_nopv'].fill(0.)
                all_var_dict['tau_iso_neu'].fill(0.)
                all_var_dict['tau_iso_puppi'].fill(0.)
                all_var_dict['tau_iso_puppiNoL'].fill(0.)

                for cand in tau.isolationChargedHadrCands():

                    if not abs(cand.charge()) > 0:
                        continue
                    if deltaR(tau.eta(), tau.phi(), cand.eta(), cand.phi()) > 0.5:
                        continue

                    if is_above_cmssw_version(9, 2, 0, debug):
                        if cand.hasTrackDetails():
                            tt = cand.pseudoTrack()
                        elif debug:
                            print "no hasTrackDetails()"
                    else:
                        tt = cand.pseudoTrack()
                    # if cand.pt()<=0.5 or tt.normalizedChi2()>=100. or
                    # tt.dxy(vertices[tau_vertex_idxpf].position())>=0.1 or
                    # cand.numberOfHits()<3:

                    # MB use candidate methods only
                    if cand.pt() <= 0.5 or cand.dxy(vertices[tau_vertex_idxpf].position()) >= 0.1:
                        continue
                    # if cand.pt()>0.95: #check this when possible (in MiniAOD 2016
                    # track information only above 0.95GeV, 0.5GeV for 2017)
                    # check this when possible (if at least one hit stored it means that track information is there, NB, we do not expect tracks with 0 hits!)
                    if cand.numberOfHits() > 0 and (tt.normalizedChi2() >= 100. or cand.numberOfHits() < 3):
                        continue
                    #dz_tt = tt.dz(vertices[tau_vertex_idxpf].position())

                    # MB use cand methods only
                    dz_tt = cand.dz(vertices[tau_vertex_idxpf].position())
                    if abs(dz_tt) < 0.2:
                        all_var_dict['tau_iso_dz02'].add(cand.pt())
                        all_var_dict['tau_iso_puppi'].add(
                            cand.pt() * cand.puppiWeight())
                        all_var_dict['tau_iso_puppiNoL'].add(
                            cand.pt() * cand.puppiWeightNoLep())

                    if abs(dz_tt) < 0.015:
                        all_var_dict['tau_iso_dz001'].add(cand.pt())

                    if cand.vertexRef().key() == tau_vertex_idxpf and cand.pvAssociationQuality() > 4:
                        all_var_dict['tau_iso_pv'].add(cand.pt())

                    elif cand.vertexRef().key() != tau_vertex_idxpf and abs(dz_tt) < 0.2:
                        all_var_dict['tau_iso_nopv'].add(cand.pt())

                for cand in tau.isolationGammaCands():
                    if abs(cand.charge()) > 0 or abs(cand.pdgId()) != 22:
                        continue
                    if deltaR(tau.eta(), tau.phi(), cand.eta(), cand.phi()) > 0.5:
                        continue
                    if cand.pt() <= 0.5:
                        continue

                    all_var_dict['tau_iso_neu'].add(cand.pt())
                    all_var_dict['tau_iso_puppi'].add(
                        cand.pt() * cand.puppiWeight())
                    all_var_dict['tau_iso_puppiNoL'].add(
                        cand.pt() * cand.puppiWeightNoLep())

                all_var_dict['tau_dxy'].fill(tau.dxy())
                all_var_dict['tau_dxy_err'].fill(tau.dxy_error())
                all_var_dict['tau_dxy_sig'].fill(tau.dxy_Sig())
                all_var_dict['tau_ip3d'].fill(tau.ip3d())
                all_var_dict['tau_ip3d_err'].fill(tau.ip3d_error())
                all_var_dict['tau_ip3d_sig'].fill(tau.ip3d_Sig())

                if tau.hasSecondaryVertex():
                    all_var_dict['tau_flightLength'].fill(
                        math.sqrt(tau.flightLength().mag2()))
                    all_var_dict['tau_flightLength_sig'].fill(
                        tau.flightLengthSig())

                fill_tau_ids(all_var_dict, all_tau_ids)

                if debug:
                    print 'Release ', RelVal, ': reading Run-2 MVA-based  discriminants'
                    print all_var_dict['tau_byIsolationMVArun2v1DBoldDMwLTraw']
                    print all_var_dict['tau_byMediumIsolationMVArun2v1DBoldDMwLT']
                    print all_var_dict['tau_againstElectronMVA6raw']
                    print all_var_dict['tau_againstElectronMediumMVA6']

                    print all_var_dict['tau_mass']
                    # debug = False
                tau_tree.Fill()
    print "MATCHED TAUS:", NMatchedTaus
    print evtid, 'events are processed !'

    out_file.Write()
    out_file.Close()
