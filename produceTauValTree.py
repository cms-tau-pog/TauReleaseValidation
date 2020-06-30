#!/usr/bin/env python

''' Produces a flat tree for tau release/data validation.
Authors: Yuta Takahashi, Michal Bluj, Jan Steggemann.
'''

import math
import sys
import os
import copy
import subprocess
from time import time
from datetime import datetime, timedelta

import ROOT
import argparse  # needs to come after ROOT import

from DataFormats.FWLite import Events, Handle
from PhysicsTools.HeppyCore.utils.deltar import deltaR, bestMatch, deltaR2
from PhysicsTools.Heppy.physicsutils.TauDecayModes import tauDecayModes
from Var import Var
from tau_ids import all_tau_ids, lepton_tau_ids, \
    tau_ids, fill_tau_ids


from relValTools import addArguments, getFilesFromEOS, \
    getFilesFromDAS, getNeventsFromDAS, is_above_cmssw_version, \
    runtype_to_sample, dprint

ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(True)

tau_run_types = ['DYToLL', 'ZTT', 'ZpTT', 'TTbarTau', 'TenTaus']
jet_run_types = ['QCD', 'TTbar']
muon_run_types = ['ZMM', 'ZpMM']
ele_run_types = ['ZEE']
fill_pf_cands = False  # Slows down processing
fill_lost_cands = False  # Slows down processing


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
    gen.final_ds = finalDaughters(gen)
    return sum(
        (d.p4() for d in gen.final_ds
            if abs(d.pdgId()) not in [12, 14, 16]),
        ROOT.math.XYZTLorentzVectorD()
    )


def removeOverlap(all_jets, gen_leptons, dR2=0.25): # dR2=0.25  ==  dR=0.5
    non_tau_jets = []
    for j_cand in all_jets:
        if not any(deltaR2(j_cand, lep) < dR2 for lep in gen_leptons):
            non_tau_jets.append(j_cand)

    return non_tau_jets


def isGenLepton(lep_cand, pid):
    # more relaxed definition of leptons faking taus:
    # select also particles that radiated
    # and would otherwise fail isPromptFinalState()
    return (
        abs(lep_cand.pdgId()) == pid and
        (
            lep_cand.statusFlags().isPrompt() or
            lep_cand.isDirectPromptTauDecayProductFinalState()
        ) and
        lep_cand.pt() > 20 and
        abs(lep_cand.eta()) < 2.3
    )

def MatchTausToJets(refObjs):

  # For each Jet, get the closest RecoTau
  Match = {}
  for jetidx,refObj in enumerate(refObjs):
      tau, _dr2_ = bestMatch(refObj, taus) # dR2=0.25  ==  dR=0.5
      for tauidx,itau in enumerate(taus):
        if itau==tau: break
      if _dr2_ < 0.25: Match[jetidx]=tauidx

  # Is the same Tau assinged to more than one Jet?
  DoubleCheck = []
  for ijet,itau in Match.iteritems():
    for jjet,jtau in Match.iteritems():
      if jjet >= ijet: continue
      if itau==jtau:
        if ijet not in DoubleCheck: DoubleCheck.append(ijet)
        if jjet not in DoubleCheck: DoubleCheck.append(jjet)

  # Get all distances between all conflicting Jets and corresponding Taus
  Distances = {}
  for ijet in DoubleCheck:
    for jjet in DoubleCheck:
      itau = Match[jjet]
      Distances[str(ijet)+"_"+str(itau)] = deltaR(taus[itau].eta(), taus[itau].phi(), refObjs[ijet].eta(), refObjs[ijet].phi())
  #print Distances

  # Remove all conflicting Jets, to re-assign later
  for ijet in DoubleCheck:
    del Match[ijet]

  # Assign shortest distance between Tau and Jet, then move on ignoring the already assigned Taus/Jets
  while Distances != {}:
    keepthis = min(Distances, key=Distances.get)
    thisjet = int(keepthis[:keepthis.find("_")])
    thistau = int(keepthis[keepthis.rfind("_")+1:])
    Match[thisjet] = thistau
    deletethis = []
    for element in Distances:
      if element.startswith(str(thisjet)) or element.endswith(str(thistau)): deletethis.append(element)
    for element in deletethis: del Distances[element]

  return Match


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    addArguments(parser, produce=True, compare=False)
    args = parser.parse_args()

    runtype = args.runtype
    globaldebug = args.debug
    maxEvents = args.maxEvents
    RelVal = args.release
    globalTag = args.globalTag
    exact = args.exact
    useRecoJets = args.useRecoJets
    storageSite = args.storageSite
    localdir = args.localdir
    tauCollection = args.tauCollection
    mvaid = args.mvaid
    no_anti_lepton = args.noAntiLepton
    if len(localdir) > 1 and localdir[-1] != "/":
        localdir += "/"
    inputfiles = args.inputfiles

    dprint('Running with')
    dprint('runtype', runtype)
    dprint('RelVal', RelVal)
    dprint('globalTag', globalTag)
    dprint('storageSite', storageSite)

    filelist = []

    if inputfiles:
        filelist = inputfiles
    else:
        path = '/store/relval/{}/{}/MINIAODSIM/{}'.format(
            RelVal,
            runtype_to_sample[runtype],
            globalTag
        )

        if storageSite == "eos":
            filelist = getFilesFromEOS(path)
        elif storageSite == "das":
            filelist = getFilesFromDAS(
                RelVal, runtype_to_sample[runtype], globalTag, exact)
        elif storageSite == 'loc':
            filelist = getFilesFromEOS(
                localdir + runtype_to_sample[runtype] +
                "/" + RelVal + '-' + globalTag + '/',
                cmseospath=False)

        if not filelist:
            print 'Sample', RelVal, runtype, 'does not exist in', path
            sys.exit(0)

    events = Events(filelist)
    if maxEvents < 0 and storageSite == "das":
      maxEvents=getNeventsFromDAS(RelVal, runtype_to_sample[runtype], globalTag, exact)
    print len(filelist), "files will be analyzed:", filelist, '\nEvents will be analyzed: %i' % maxEvents

    # +++++++ Output file +++++++++
    outputFileName = args.outputFileName
    if not outputFileName:
        if storageSite == 'loc':
            outputFileName = localdir + \
                runtype_to_sample[runtype] + "/" + RelVal + \
                '-' + globalTag + '/' + 'TauValTree/'
            if not os.path.isdir(outputFileName):
                result = subprocess.check_output(
                    "mkdir -p {outputFileName}".format(
                        outputFileName=outputFileName
                    ),
                    shell=True
                )

        genSuffix = ""
        if not useRecoJets and (runtype in jet_run_types):
            genSuffix = "_genJets"
        if runtype in muon_run_types:
            genSuffix = "_genMuon"
        if runtype in ele_run_types:
            genSuffix = "_genEle"

        outputFileName += 'Myroot_' + RelVal + '_' + \
            globalTag + '_' + runtype + genSuffix + '.root'

    else:
        if "/" in outputFileName and outputFileName[0] != "/":
            print "location of output file has a dir structure " \
                  " but doesn't start with dash"
            sys.exit(0)
        if outputFileName[-5:] != ".root":
            outputFileName += '.root'
            print "output file should have a root format" \
                  " - added automatically:", outputFileName

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
        Var('tau_pt', float),
        Var('tau_eta', float),
        Var('tau_phi', float),
        Var('tau_mass', float),
        Var('tau_chargedpt', float),
        Var('tau_neutralpt', float),
        Var('tau_gendm', int),
        Var('tau_genpt', float),
        Var('tau_geneta', float),
        Var('tau_genphi', float),
        Var('tau_genchargedpt', float),
        Var('tau_genneutralpt', float),
        Var('tau_vertex', int),
        Var('tau_nTruePU', float),
        Var('tau_nPU', int),
        # Var('tau_vtxTovtx_dz', float),
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

    if not no_anti_lepton:
        all_tau_ids += lepton_tau_ids

    for mva_id in mvaid:
        all_tau_ids += tau_ids[mva_id]

    for (tau_id, v_type) in all_tau_ids:
        all_vars.append(Var('tau_' + tau_id, v_type))

    all_var_dict = {var.name: var for var in all_vars}

    for var in all_vars:
        tau_tree.Branch(var.name, var.storage, var.name +
                        '/' + ('I' if var.type == int else 'D'))

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

    start = time()
    for event in events:
        evtid += 1
        eid = event.eventAuxiliary().id().event()

        if evtid % 1000 == 0 and maxEvents>0:
            if storageSite == "das":
              percentage = float(evtid)/maxEvents*100.
              speed = float(evtid)/(time()-start)
              ETA = datetime.now() + timedelta(seconds=(maxEvents-evtid) / max(0.1, speed))
              print '===> processing %d / %d event \t completed %.1f%s \t %.1f ev/s \t ETA %s s' %(evtid, maxEvents, percentage, '%', speed, ETA.strftime('%Y-%m-%d %H:%M:%S'))
            else:
              print 'Event ', evtid, 'processed'
        if maxEvents > 0 and evtid > maxEvents:
            break

        event.getByLabel(tauCollection, tauH)
        event.getByLabel("offlineSlimmedPrimaryVertices", vertexH)
        event.getByLabel("slimmedAddPileupInfo", puH)
        event.getByLabel('prunedGenParticles', genParticlesH)

        if fill_pf_cands:
            event.getByLabel("packedPFCandidates", candH)
            pfCands = candH.product()
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
        if fill_lost_cands:
            event.getByLabel("lostTracks", lostH)
            lostCands = lostH.product()
            for cand in lostCands:
                h_lost_pt.Fill(cand.pt())
                h_lost_phi.Fill(cand.phi())
                h_lost_eta.Fill(cand.eta())

        taus = tauH.product()
        vertices = vertexH.product()
        puInfo = puH.product()
        genParticles = genParticlesH.product()

        genTaus = [p for p in genParticles if abs(
            p.pdgId()) == 15 and p.isPromptDecayed()]

        genElectrons = [
            p for p in genParticles if isGenLepton(p, 11)]
        genMuons = [
            p for p in genParticles if isGenLepton(p, 13)]

        # gen leptons to clean jets with respect to them (e.g. for TTBar)
        genLeptons = [
            p for p in genParticles
            if (
                p.status() == 1 and
                p.pt() > 15 and
                (
                    (
                        (
                            abs(p.pdgId()) == 11 or
                            abs(p.pdgId()) == 13
                        ) and
                        p.isPromptFinalState()
                    ) or
                    (
                        abs(p.pdgId()) == 15 and
                        p.isPromptDecayed()
                    )
                )
            )
        ]

        refObjs = []
        if runtype in tau_run_types:
            for gen_tau in genTaus:
                gen_tau.visP4 = visibleP4(gen_tau)

                gen_dm = tauDecayModes.genDecayModeInt(
                    [d for d in gen_tau.final_ds
                        if abs(d.pdgId()) not in [12, 14, 16]]
                )
                if abs(gen_tau.visP4.eta()) > 2.3:
                    continue
                if gen_tau.visP4.pt() < 10:
                    continue
                if gen_dm == -11 or gen_dm == -13:
                    continue
                # For the 10-tau sample, remove gen taus that have overlap
                if any(deltaR(other_tau, gen_tau) < 0.5
                       for other_tau in genTaus if other_tau is not gen_tau):
                    continue

                refObjs.append(gen_tau)

        elif runtype in jet_run_types:
            if useRecoJets:
                event.getByLabel("slimmedJets", jetH)
                all_jets = [
                    jet for jet in jetH.product()
                    if (jet.pt() > 20 and
                        abs(jet.eta()) < 2.3 and
                        jet.pt() < 200.5)
                ]
                jets = removeOverlap(all_jets, genLeptons)
                refObjs = copy.deepcopy(jets)
            else:
                event.getByLabel("slimmedGenJets", genJetH)
                all_gen_jets = [
                    jet for jet in genJetH.product()
                    if (jet.pt() > 20 and
                        abs(jet.eta()) < 2.3 and
                        jet.pt() < 200.5)
                ]
                gen_jets = removeOverlap(all_gen_jets, genLeptons)
                refObjs = copy.deepcopy(gen_jets)
        elif runtype in ele_run_types:
            refObjs = copy.deepcopy(genElectrons)
        elif runtype in muon_run_types:
            refObjs = copy.deepcopy(genMuons)

        ###
        Matched = MatchTausToJets(refObjs)

        ###
        h_ngen.Fill(len(refObjs))
        for refidx,refObj in enumerate(refObjs):
            for var in all_vars:
                var.reset()
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

            if runtype in tau_run_types:
                gen_dm = tauDecayModes.genDecayModeInt(
                    [d for d in finalDaughters(refObj)
                        if (abs(d.pdgId()) not in [12, 14, 16])]
                )

                all_var_dict['tau_gendm'].fill(gen_dm)
                all_var_dict['tau_genpt'].fill(refObj.visP4.pt())
                all_var_dict['tau_geneta'].fill(refObj.visP4.eta())
                all_var_dict['tau_genphi'].fill(refObj.visP4.phi())
                charged_p4 = sum(
                    (d.p4() for d in refObj.final_ds
                        if d.charge()),
                    ROOT.math.XYZTLorentzVectorD())
                neutral_p4 = sum(
                    (d.p4() for d in refObj.final_ds
                        if (abs(d.pdgId()) not in [12, 14, 16] and
                            not d.charge())),
                    ROOT.math.XYZTLorentzVectorD())
                all_var_dict['tau_genchargedpt'].fill(charged_p4.pt())
                all_var_dict['tau_genneutralpt'].fill(neutral_p4.pt())
            else:
                all_var_dict['tau_gendm'].fill(-1)
                all_var_dict['tau_genpt'].fill(refObj.pt())
                all_var_dict['tau_geneta'].fill(refObj.eta())
                all_var_dict['tau_genphi'].fill(refObj.phi())

            if refidx in Matched:
                tau = taus[Matched[refidx]]
                # Fill reco-tau variables if it exists...
                NMatchedTaus += 1

                all_var_dict['tau_dm'].fill(tau.decayMode())
                all_var_dict['tau_pt'].fill(tau.pt())
                all_var_dict['tau_eta'].fill(tau.eta())
                all_var_dict['tau_phi'].fill(tau.phi())
                all_var_dict['tau_mass'].fill(tau.mass())

                all_var_dict['tau_chargedpt'].fill(
                    sum((d.p4() for d in tau.signalChargedHadrCands()),
                        ROOT.math.XYZTLorentzVectorD()).pt())
                all_var_dict['tau_neutralpt'].fill(
                    sum((d.p4() for d in tau.signalGammaCands()),
                        ROOT.math.XYZTLorentzVectorD()).pt()
                )

                # Use candidate to vertex associaton as in MiniAOD
                tau_vertex_idxpf = tau.leadChargedHadrCand().vertexRef().key()

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
                    if deltaR(tau.eta(),
                              tau.phi(),
                              cand.eta(),
                              cand.phi()) > 0.5:
                        continue

                    def get_track(charged_cand):
                        if is_above_cmssw_version(9, 2, 0):
                            if charged_cand.hasTrackDetails():
                                return charged_cand.pseudoTrack()
                            return None
                        return charged_cand.pseudoTrack()

                    # MB use candidate methods only
                    if (cand.pt() <= 0.5 or
                            cand.dxy(
                                vertices[tau_vertex_idxpf].position()
                    ) >= 0.1):
                        continue

                    cand_track = get_track(cand)
                    if not cand_track:
                        continue
                    if (cand.numberOfHits() > 0 and
                            (cand_track.normalizedChi2() >= 100. or
                             cand.numberOfHits() < 3)):
                        continue
                    # dz_tt = tt.dz(vertices[tau_vertex_idxpf].position())

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

                    if (cand.vertexRef().key() == tau_vertex_idxpf and
                            cand.pvAssociationQuality() > 4):
                        all_var_dict['tau_iso_pv'].add(cand.pt())

                    elif (cand.vertexRef().key() != tau_vertex_idxpf and
                          abs(dz_tt) < 0.2):
                        all_var_dict['tau_iso_nopv'].add(cand.pt())

                for cand in tau.isolationGammaCands():
                    if abs(cand.charge()) > 0 or abs(cand.pdgId()) != 22:
                        continue
                    if deltaR(tau.eta(),
                              tau.phi(),
                              cand.eta(),
                              cand.phi()) > 0.5:
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

                fill_tau_ids(all_var_dict, tau, all_tau_ids)
            tau_tree.Fill()
    print "MATCHED TAUS:", NMatchedTaus
    print evtid, 'events are processed !'

    out_file.Write()
    out_file.Close()
