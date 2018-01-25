''' Produces a flat tree for tau release/data validation.
Authors: Yuta Takahashi, Michal Bluj, Jan Steggemann.
'''

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

import math
import sys
import re
import argparse
import numpy as num

from das_client import get_data, x509
from DataFormats.FWLite import Events, Handle
from PhysicsTools.HeppyCore.utils.deltar import deltaR, bestMatch
from PhysicsTools.Heppy.physicsutils.TauDecayModes import tauDecayModes

import eostools

ROOT.gROOT.SetBatch(True)


class Var:
    def __init__(self, name, type):
        self.name = name
        self.type = type
        self.storage = None

    def reset(self):
        self.storage[0] = -999

    def fill(self, val):
        self.storage[0] = val

    def add(self, val):
        self.storage[0] += val

    def __str__(self):
        return 'Var: name={}, type={}, val={:.2f}'.format(self.name, self.type, self.storage[0])


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

    p4 = sum((d.p4() for d in final_ds if abs(d.pdgId()) not in [
             12, 14, 16]), ROOT.math.XYZTLorentzVectorD())

    return p4


def getFilesFromEOS(path):
    '''Give path in form /store/relval/CMSSW_9_4_0_pre2/...'''
    dirs = eostools.listFiles('/eos/cms'+path)
    files = []
    for sub_path in dirs:
        files += ['root://eoscms.cern.ch/' +
         x for x in eostools.listFiles(sub_path) if re.match('.*root', x)]
    return files

def getFilesFromDAS(release, runtype, globalTag):
    '''Get proxy with "voms-proxy-init -voms cms" to use this option.'''
    print "Getting files from DAS. May take a while...."
    host = 'https://cmsweb.cern.ch'
    capath = '/etc/grid-security/certificates'

    query = "file dataset=/*{0}*/*{1}*{2}*/MINIAODSIM".format(runtype, release, globalTag, )
    output = get_data(host = host,
                      query=query,
                      idx=0,
                      limit=0,
                      debug=0,
                      cert=x509(),
                      capath=capath )
    files = []

    for entry in output["data"]:
        file = "root://cms-xrd-global.cern.ch/"+str( entry["file"][0]["name"] )
        if "/".join([release,runtype,"MINIAODSIM",globalTag]) in file:
            files.append(file)

    return files

if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('runtype', choices=['ZTT', 'ZEE', 'ZMM', 'QCD', 'TTbar', 'TTbarTau', 'ZpTT'], help='choose sample type')

    parser.add_argument('-r', '--relval',  help='Release string', default='CMSSW_9_4_0_pre2')
    parser.add_argument('-g', '--globalTag',  help='Global tag', default='PU25ns_94X_mc2017_realistic_v1-v1')
    parser.add_argument('-n', '--maxEvents',  help='Number of events that will be analyzed (-1 = all events)', default=-1)
    parser.add_argument('-u', '--useRecoJets', action="store_true",  help='Use RecoJets', default=False)
    parser.add_argument('-s', '--storageSite', help="Choose between samples store on eos or DAS",  choices=['eos','das'], default='eos')

    args = parser.parse_args()
        
    maxEvents = args.maxEvents
    RelVal = args.relval
    globalTag = args.globalTag
    useRecoJets = args.useRecoJets
    storageSite = args.storageSite

    runtype = args.runtype

    print 'Running with'
    print 'runtype', runtype
    print 'RelVal', RelVal
    print 'globalTag', globalTag
    print 'storageSite', storageSite

    filelist = []
    
    runtype_to_sample = {
        'ZTT':'RelValZTT_13',
        'ZMM':'RelValZpMM_13',
        'QCD':'RelValQCD_FlatPt_15_3000HS_13',
        'TTbar':'RelValTTbar_13',
        'TTbarTau':'RelValTTbar_13',
        'ZpTT':'RelValZpTT_1500_13'
    }

    path = '/store/relval/{}/{}/MINIAODSIM/{}'.format(RelVal, runtype_to_sample[runtype], globalTag)

    if storageSite == "eos": filelist = getFilesFromEOS(path)
    if storageSite == "das": filelist = getFilesFromDAS(RelVal, runtype_to_sample[runtype], globalTag)

    if len(filelist) == 0:
        print 'Sample', RelVal, runtype, 'does not exist in', path
        sys.exit(0)

    events = Events(filelist)
    print len(filelist), 'files will be analyzed'
    if maxEvents > 0:
        print maxEvents, 'events will be analyzed'
    else:
        print 'All events will be analyzed (maxEvents = %i)' % maxEvents

    outputname = 'Myroot_' + RelVal + '_' + globalTag + '_' + runtype + '.root'
    if not useRecoJets and (runtype == 'QCD' or runtype == 'TTBar'):
        outputname = 'Myroot_' + RelVal + '_' + globalTag + '_' + runtype + 'genJets.root'
    file = ROOT.TFile(outputname, 'recreate')

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
        Var('tau_againstMuonLoose3', int),
        Var('tau_againstMuonTight3', int),
        Var('tau_byIsolationMVA3oldDMwLTraw', float),
        Var('tau_byLooseIsolationMVA3oldDMwLT', int),
        Var('tau_byMediumIsolationMVA3oldDMwLT', int),
        Var('tau_byTightIsolationMVA3oldDMwLT', int),
        Var('tau_byVLooseIsolationMVA3oldDMwLT', int),
        Var('tau_byVTightIsolationMVA3oldDMwLT', int),
        Var('tau_byVVTightIsolationMVA3oldDMwLT', int),
        Var('tau_byCombinedIsolationDeltaBetaCorrRaw3Hits', float),
        Var('tau_byLooseCombinedIsolationDeltaBetaCorr3Hits', int),
        Var('tau_byMediumCombinedIsolationDeltaBetaCorr3Hits', int),
        Var('tau_byTightCombinedIsolationDeltaBetaCorr3Hits', int),
        Var('tau_chargedIsoPtSum', float),
        Var('tau_neutralIsoPtSum', float),
        Var('tau_puCorrPtSum', float),
        Var('tau_neutralIsoPtSumWeight', float),
        Var('tau_footprintCorrection', float),
        Var('tau_photonPtSumOutsideSignalCone', float),
        Var('tau_decayModeFindingOldDMs', int),
        Var('tau_decayModeFindingNewDMs', int),
        Var('tau_againstElectronVLooseMVA6', int),
        Var('tau_againstElectronLooseMVA6', int),
        Var('tau_againstElectronMediumMVA6', int),
        Var('tau_againstElectronTightMVA6', int),
        Var('tau_againstElectronVTightMVA6', int),
        Var('tau_againstElectronMVA6raw', float),
        Var('tau_byIsolationMVArun2v1DBoldDMwLTraw', float),
        Var('tau_byVLooseIsolationMVArun2v1DBoldDMwLT', int),
        Var('tau_byLooseIsolationMVArun2v1DBoldDMwLT', int),
        Var('tau_byMediumIsolationMVArun2v1DBoldDMwLT', int),
        Var('tau_byTightIsolationMVArun2v1DBoldDMwLT', int),
        Var('tau_byVTightIsolationMVArun2v1DBoldDMwLT', int),
        Var('tau_byVVTightIsolationMVArun2v1DBoldDMwLT', int),
        Var('tau_byIsolationMVArun2v1PWoldDMwLTraw', float),
        Var('tau_byLooseIsolationMVArun2v1PWoldDMwLT', int),
        Var('tau_byMediumIsolationMVArun2v1PWoldDMwLT', int),
        Var('tau_byTightIsolationMVArun2v1PWoldDMwLT', int),
        Var('tau_byVLooseIsolationMVArun2v1PWoldDMwLT', int),
        Var('tau_byVTightIsolationMVArun2v1PWoldDMwLT', int),
        Var('tau_byVVTightIsolationMVArun2v1PWoldDMwLT', int),
        Var('tau_dxy', float),
        Var('tau_dxy_err', float),
        Var('tau_dxy_sig', float),
        Var('tau_ip3d', float),
        Var('tau_ip3d_err', float),
        Var('tau_ip3d_sig', float),
        Var('tau_flightLength', float),
        Var('tau_flightLength_sig', float)
    ]

    all_var_dict = {var.name: var for var in all_vars}

    for var in all_vars:
        var.storage = num.zeros(1, dtype=var.type)
        tau_tree.Branch(var.name, var.storage, var.name +
                        '/'+('I' if var.type == int else 'D'))

    evtid = 0
    doPrint = True  # FIXME, for debug

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

        event.getByLabel("slimmedTaus", tauH)
        event.getByLabel("offlineSlimmedPrimaryVertices", vertexH)
        event.getByLabel("slimmedAddPileupInfo", puH)
        event.getByLabel('prunedGenParticles', genParticlesH)
        event.getByLabel("slimmedJets", jetH)
        event.getByLabel("slimmedGenJets", genJetH)

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
        genElectrons = [p for p in genParticles if(abs(p.pdgId()) == 11 and p.status() == 1 and (
            p.isPromptFinalState() or p.isDirectPromptTauDecayProductFinalState()) and p.pt() > 20 and abs(p.eta()) < 2.3)]
        genMuons = [p for p in genParticles if (abs(p.pdgId()) == 13 and p.status() == 1 and (
            p.isPromptFinalState() or p.isDirectPromptTauDecayProductFinalState()) and p.pt() > 20 and abs(p.eta()) < 2.3)]
        # gen leptons to clean jets with respect to them (e.g. for TTBar)
        genLeptons = [p for p in genParticles if p.status() == 1 and p.pt() > 15
                      and (((abs(p.pdgId()) == 11 or abs(p.pdgId()) == 13) and p.isPromptFinalState()) or (abs(p.pdgId()) == 15 and p.isPromptDecayed()))]

        jets = []
        for jet in jets1:
            keepjet = True
            for lep in genLeptons:
                if deltaR(jet.eta(), jet.phi(), lep.eta(), lep.phi()) < 0.5:
                    keepjet = False
            if keepjet:
                jets.append(jet)
        if len(jets1) != len(jets):
            print 'genLep', len(genLeptons), 'jets1: ', len(jets1), 'jets', len(jets)
            if runtype != 'ZTT' and runtype != 'ZEE' and runtype != 'ZMM' and runtype != 'TTbarTau':
                for lep in genLeptons:
                    print 'lep pt=', lep.pt(), 'eta=', lep.eta(), 'pdgid=', lep.pdgId()
        genJets = []
        for jet in genJets1:
            keepjet = True
            for lep in genLeptons:
                if deltaR(jet.eta(), jet.phi(), lep.eta(), lep.phi()) < 0.5:
                    keepjet = False
            if keepjet:
                genJets.append(jet)
        if len(genJets1) != len(genJets):
            print 'genLep', len(genLeptons), 'genJets1: ', len(genJets1), 'genJets', len(genJets)
            if runtype != 'ZTT' and runtype != 'ZEE' and runtype != 'ZMM' and runtype != 'TTbarTau':
                for lep in genLeptons:
                    print 'lep pt=', lep.pt(), 'eta=', lep.eta(), 'pdgid=', lep.pdgId()

        ##########
        refObjs = []

        if runtype == 'ZTT' or runtype == 'TTbarTau':
            for igen in genTaus:
                visP4 = visibleP4(igen)

                gen_dm = tauDecayModes.genDecayModeInt(
                    [d for d in finalDaughters(igen) if abs(d.pdgId()) not in [12, 14, 16]])
                if abs(visP4.eta()) > 2.3:
                    continue
                if visP4.pt() < 10:
                    continue
                if(gen_dm == -11 or gen_dm == -13):
                    continue
                refObjs.append(igen)

                #gp = _genparticle_[0]
                #tau_gendm[0] = gp.decaymode
                #tau_gendm_rough[0] = returnRough(gp.decaymode)
                #tau_genpt[0] = gp.vis.pt()
                #tau_geneta[0] = gp.vis.eta()
                #tau_genphi[0] = gp.vis.phi()
        elif runtype == 'QCD' or runtype == 'TTbar':
            if useRecoJets:
                for ijet in jets:
                    refObjs.append(ijet)
            else:
                for ijet in genJets:
                    refObjs.append(ijet)
        elif runtype == 'ZEE':
            for ie in genElectrons:
                refObjs.append(ie)
        elif runtype == 'ZMM':
            for imu in genMuons:
                refObjs.append(imu)

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

            tau, _dr_ = bestMatch(refObj, taus)
            if _dr_ > 0.5:
                tau = None

            tau_vtxTovtx_dz = 99
            for i in range(0, len(vertices)-1):
                for j in range(i+1, len(vertices)):
                    vtxdz = abs(vertices[i].z()-vertices[j].z())
                    if vtxdz < tau_vtxTovtx_dz:
                        tau_vtxTovtx_dz = vtxdz
            all_var_dict['tau_vtxTovtx_dz'].fill(tau_vtxTovtx_dz)

            # Fill reco-tau variables if it exists...
            if tau != None:

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
                for i in range(0, len(vertices)):
                    if i == tau_vertex_idxpf:
                        continue
                    vtxdz = abs(vertices[i].z()-vertices[tau_vertex_idxpf].z())
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
                    tt = cand.pseudoTrack()
                    # if cand.pt()<=0.5 or tt.normalizedChi2()>=100. or
                    # tt.dxy(vertices[tau_vertex_idxpf].position())>=0.1 or
                    # cand.numberOfHits()<3:
                    # MB use candidate methods only
                    if cand.pt() <= 0.5 or cand.dxy(vertices[tau_vertex_idxpf].position()) >= 0.1:
                        continue
                    # if cand.pt()>0.95: #check this when possible (in MiniAOD 2016
                    # track information only above 0.95GeV, 0.5GeV for 2017)
                    if cand.numberOfHits() > 0:  # check this when possible (if at least one hit stored it means that track information is there, NB, we do not expect tracks with 0 hits!)
                        if tt.normalizedChi2() >= 100. or cand.numberOfHits() < 3:
                            continue
                    #dz_tt = tt.dz(vertices[tau_vertex_idxpf].position())
                    # MB use cand methods only
                    dz_tt = cand.dz(vertices[tau_vertex_idxpf].position())
                    if abs(dz_tt) < 0.2:
                        all_var_dict['tau_iso_dz02'].add(cand.pt())
                        all_var_dict['tau_iso_puppi'].add(
                            cand.pt()*cand.puppiWeight())
                        all_var_dict['tau_iso_puppiNoL'].add(
                            cand.pt()*cand.puppiWeightNoLep())
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
                        cand.pt()*cand.puppiWeight())
                    all_var_dict['tau_iso_puppiNoL'].add(
                        cand.pt()*cand.puppiWeightNoLep())

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

                all_var_dict['tau_againstMuonLoose3'].fill(
                    tau.tauID('againstMuonLoose3'))
                all_var_dict['tau_againstMuonTight3'].fill(
                    tau.tauID('againstMuonTight3'))

                all_var_dict['tau_byCombinedIsolationDeltaBetaCorrRaw3Hits'].fill(tau.tauID(
                    'byCombinedIsolationDeltaBetaCorrRaw3Hits'))
                all_var_dict['tau_byLooseCombinedIsolationDeltaBetaCorr3Hits'].fill(tau.tauID(
                    'byLooseCombinedIsolationDeltaBetaCorr3Hits'))
                all_var_dict['tau_byMediumCombinedIsolationDeltaBetaCorr3Hits'].fill(tau.tauID(
                    'byMediumCombinedIsolationDeltaBetaCorr3Hits'))
                all_var_dict['tau_byTightCombinedIsolationDeltaBetaCorr3Hits'].fill(tau.tauID(
                    'byTightCombinedIsolationDeltaBetaCorr3Hits'))
                all_var_dict['tau_chargedIsoPtSum'].fill(
                    tau.tauID('chargedIsoPtSum'))
                all_var_dict['tau_neutralIsoPtSum'].fill(
                    tau.tauID('neutralIsoPtSum'))
                all_var_dict['tau_puCorrPtSum'].fill(tau.tauID('puCorrPtSum'))

                all_var_dict['tau_neutralIsoPtSumWeight'].fill(
                    tau.tauID('neutralIsoPtSumWeight'))
                all_var_dict['tau_footprintCorrection'].fill(
                    tau.tauID('footprintCorrection'))
                all_var_dict['tau_photonPtSumOutsideSignalCone'].fill(tau.tauID(
                    'photonPtSumOutsideSignalCone'))
                all_var_dict['tau_decayModeFindingOldDMs'].fill(
                    tau.tauID('decayModeFinding'))
                all_var_dict['tau_decayModeFindingNewDMs'].fill(
                    tau.tauID('decayModeFindingNewDMs'))

                all_var_dict['tau_againstElectronVLooseMVA6'].fill(tau.tauID(
                    'againstElectronVLooseMVA6'))
                all_var_dict['tau_againstElectronLooseMVA6'].fill(tau.tauID(
                    'againstElectronLooseMVA6'))
                all_var_dict['tau_againstElectronMediumMVA6'].fill(tau.tauID(
                    'againstElectronMediumMVA6'))
                all_var_dict['tau_againstElectronTightMVA6'].fill(tau.tauID(
                    'againstElectronTightMVA6'))
                all_var_dict['tau_againstElectronVTightMVA6'].fill(tau.tauID(
                    'againstElectronVTightMVA6'))
                all_var_dict['tau_againstElectronMVA6raw'].fill(tau.tauID(
                    'againstElectronMVA6Raw'))

                all_var_dict['tau_byIsolationMVArun2v1DBoldDMwLTraw'].fill(tau.tauID(
                    'byIsolationMVArun2v1DBoldDMwLTraw'))
                all_var_dict['tau_byLooseIsolationMVArun2v1DBoldDMwLT'].fill(tau.tauID(
                    'byLooseIsolationMVArun2v1DBoldDMwLT'))
                all_var_dict['tau_byMediumIsolationMVArun2v1DBoldDMwLT'].fill(tau.tauID(
                    'byMediumIsolationMVArun2v1DBoldDMwLT'))
                all_var_dict['tau_byTightIsolationMVArun2v1DBoldDMwLT'].fill(tau.tauID(
                    'byTightIsolationMVArun2v1DBoldDMwLT'))
                all_var_dict['tau_byVLooseIsolationMVArun2v1DBoldDMwLT'].fill(tau.tauID(
                    'byVLooseIsolationMVArun2v1DBoldDMwLT'))
                all_var_dict['tau_byVTightIsolationMVArun2v1DBoldDMwLT'].fill(tau.tauID(
                    'byVTightIsolationMVArun2v1DBoldDMwLT'))
                all_var_dict['tau_byVVTightIsolationMVArun2v1DBoldDMwLT'].fill(tau.tauID(
                    'byVVTightIsolationMVArun2v1DBoldDMwLT'))

                all_var_dict['tau_byIsolationMVArun2v1PWoldDMwLTraw'].fill(tau.tauID(
                    'byIsolationMVArun2v1PWoldDMwLTraw'))
                all_var_dict['tau_byLooseIsolationMVArun2v1PWoldDMwLT'].fill(tau.tauID(
                    'byLooseIsolationMVArun2v1PWoldDMwLT'))
                all_var_dict['tau_byMediumIsolationMVArun2v1PWoldDMwLT'].fill(tau.tauID(
                    'byMediumIsolationMVArun2v1PWoldDMwLT'))
                all_var_dict['tau_byTightIsolationMVArun2v1PWoldDMwLT'].fill(tau.tauID(
                    'byTightIsolationMVArun2v1PWoldDMwLT'))
                all_var_dict['tau_byVLooseIsolationMVArun2v1PWoldDMwLT'].fill(tau.tauID(
                    'byVLooseIsolationMVArun2v1PWoldDMwLT'))
                all_var_dict['tau_byVTightIsolationMVArun2v1PWoldDMwLT'].fill(tau.tauID(
                    'byVTightIsolationMVArun2v1PWoldDMwLT'))
                all_var_dict['tau_byVVTightIsolationMVArun2v1PWoldDMwLT'].fill(tau.tauID(
                    'byVVTightIsolationMVArun2v1PWoldDMwLT'))
                if doPrint:
                    print 'Release ', RelVal, ': reading Run-2 MVA-based  discriminants'
                    print all_var_dict['tau_byIsolationMVArun2v1DBoldDMwLTraw']
                    print all_var_dict['tau_byMediumIsolationMVArun2v1DBoldDMwLT']
                    print all_var_dict['tau_againstElectronMVA6raw']
                    print all_var_dict['tau_againstElectronMediumMVA6']
                    doPrint = False

            tau_tree.Fill()

    print evtid, 'events are processed !'

    file.Write()
    file.Close()
