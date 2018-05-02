''' Produces plots for tau release/data validation using the trees produced by
produceTauValTree.py
Authors: Yuta Takahashi, Michal Bluj, Jan Steggemann.
'''

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

from ROOT import gROOT, gStyle, TH1F, TFile, TCanvas, TPad, TLegend, TGraphAsymmErrors, Double, TLatex
from officialStyle import officialStyle
from array import array

from collections import namedtuple
import argparse
from variables import vardict, hvardict

from relValTools import *
from compareTools import *

gROOT.SetBatch(True)
officialStyle(gStyle)
gStyle.SetOptTitle(0)

# set_palette("color")
# gStyle.SetPaintTextFormat("2.0f")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    addArguments(parser, compare=True)
    args = parser.parse_args()
    part = args.part
    dryRun = args.dryRun
    ptPlotsBinning = array('d', [20, 200]) if args.onebin else array('d', [20, 30, 40, 50, 60, 70, 80, 100, 150, 200])
    etaPlotsBinning = array('d', [-2.4, 2]) if args.onebin else array('d', [ round(-2.4 + i*0.4,1) for i in range(0, 12 + 1)])

    runtype = args.runtype
    print 'Producing plots for runtype', runtype

    releases = args.releases.split(',')
    print args.globalTag

    globaltags = args.globalTag.split(',')
    print 'Releases', releases, '\nGlobal tags', globaltags

    RuntypeOptions = namedtuple("RuntypeOptions", "tlabel xlabel xlabel_eta")
    options_dict = {
        'ZTT': RuntypeOptions(tlabel = 'Z #rightarrow #tau#tau', xlabel = 'gen. tau p_{T}^{vis} (GeV)', xlabel_eta = 'gen. tau #eta^{vis}'),
        'ZEE': RuntypeOptions(tlabel = 'Z #rightarrow ee', xlabel = 'electron p_{T} (GeV)', xlabel_eta = 'electron #eta'),
        'ZMM': RuntypeOptions(tlabel = 'Z #rightarrow #mu#mu', xlabel = 'muon p_{T} (GeV)', xlabel_eta = 'muon #eta'),
        'QCD': RuntypeOptions(tlabel = 'QCD, flat #hat{p}_{T} 15-3000GeV', xlabel = 'jet p_{T} (GeV)', xlabel_eta = 'jet #eta'),
        'TTbar': RuntypeOptions(tlabel = 'TTbar', xlabel = 'jet p_{T} (GeV)', xlabel_eta = 'jet #eta'),
        'TTbarTau': RuntypeOptions( tlabel = 'TTbar #rightarrow #tau+X', xlabel = 'gen. tau p_{T}^{vis} (GeV)', xlabel_eta = 'gen. tau #eta^{vis}')
    }

    reco_cut = 'tau_pt > 20 && abs(tau_eta) < 2.3'
    #loose_id = 'tau_decayModeFindingOldDMs > 0.5 && tau_byLooseCombinedIsolationDeltaBetaCorr3Hits > 0.5'
    loose_id = 'tau_decayModeFindingOldDMs > 0.5 && tau_byLooseIsolationMVArun2v1DBoldDMwLT > 0.5'
    loose_id_17v2 = 'tau_decayModeFindingOldDMs > 0.5 && tau_byLooseIsolationMVArun2017v2DBoldDMwLT2017 > 0.5'

    styles = [
        {'col': 8, 'marker': 25, 'width': 2},
        {'col': 2, 'marker': 21, 'width': 2},
        {'col': 4, 'marker': 21, 'width': 2},
        {'col': 7, 'marker': 24, 'width': 2},
        {'col': 41, 'marker': 20, 'width': 2},
        {'col': 1, 'marker': 26, 'width': 2},
        {'col': 6, 'marker': 22, 'width': 2},
    ]
    
    print "Collecting samples"
    sampledict = {}
    for i_sample, release in enumerate(globaltags):
        sampledict[release] = styles[i_sample]
        tfile = sampledict[release]['file'] = TFile('Myroot_{}_{}_{}.root'.format(releases[i_sample], release, runtype))
        sampledict[release]['tree'] = tfile.Get('per_tau')
    print "sampledict:"
    pp.pprint(sampledict)

    print "First part of plots"
    if part < 2:
        for hname, hdict in vardict.items():
            hists = []
            histseta = []

            for rel, rdict in sampledict.items():
                tree = rdict['tree']
                num_sel = reco_cut
                den_sel = '1'
                den_sel_17v2 = '1'

                if hname.find('against') != -1:
                    #num_sel = '1'
                    num_sel = reco_cut
                    den_sel = reco_cut + ' && ' + loose_id
                    den_sel_17v2 = reco_cut + ' && ' + loose_id_17v2

                for mvaIDname, sel in {"loose_id": den_sel, "loose_id_17v2": den_sel_17v2}.items():
                    hists.append(makeEffPlotsVars(tree=tree,
                        varx='tau_genpt',
                        numeratorAddSelection=num_sel + '&&' + hdict['var'],
                        baseSelection=sel + '&& abs(tau_eta) < 2.3',
                        xtitle=options_dict[runtype].xlabel,
                        header=rel + mvaIDname, addon=rel + mvaIDname,
                        option='pt',
                        marker=rdict['marker'],
                        col=rdict['col'],
                        ptPlotsBinning=ptPlotsBinning)
                    )
                    histseta.append(makeEffPlotsVars(tree=tree,
                        varx='tau_geneta',
                        numeratorAddSelection=num_sel + '&&' + hdict['var'],
                        baseSelection=sel + '&& tau_pt>20',
                        xtitle=options_dict[runtype].xlabel_eta,
                        header=rel + mvaIDname, addon=rel + mvaIDname,
                        option='eta',
                        marker=rdict['marker'],
                        col=rdict['col'],
                        ptPlotsBinning=etaPlotsBinning)
                    )

            overlay(hists=hists, ytitle=hname,
                header=hname,
                addon=hdict['title'],
                runtype=runtype,
                tlabel=options_dict[runtype].tlabel,
                xlabel=options_dict[runtype].xlabel,
                dryrun=dryRun)

            overlay(hists=histseta, ytitle=hname,
                header=hname + '_eta',
                addon=hdict['title'] + '_eta',
                runtype=runtype,
                tlabel=options_dict[runtype].tlabel,
                xlabel=options_dict[runtype].xlabel,
                dryrun=dryRun)

    if part == 1: exit()
    print "Second part of plots"
    for index, (hname, hdict) in enumerate(hvardict.iteritems()):
        if   part == 2 and index > len(hvardict.items()) / 2: exit()
        elif part == 3 and index <= len(hvardict.items()) / 2: continue
        elif part == 3 and index - 1== len(hvardict.items()) / 2: print "Third part of plots"
        if runtype not in ['ZTT', 'TTbarTau'] and hname.find('pt_resolution') != -1: continue

        hists = []
        for rel, rdict in sampledict.items():
            tree = rdict['tree']
            hist = TH1F('h_' + hname + '_' + rel, 'h_' + hname + '_' + rel, hdict['nbin'], hdict['min'], hdict['max'])

            hist.GetYaxis().SetNdivisions(507)
            hist.SetLineColor(rdict['col'])
            hist.SetLineWidth(rdict['width'])
            hist.SetMinimum(0)
            hist.SetName(rel)
            hist.Sumw2()
            hist.GetXaxis().SetTitle(hdict['title'])

            tree.Project(hist.GetName(), hdict['var'], hdict['sel'])

            if hist.Integral(0, hist.GetNbinsX() + 1) > 0:
                hist.Scale(1. / hist.Integral(0, hist.GetNbinsX() + 1))

            hists.append(hist)

        hoverlay(hists, hdict['title'], 'a.u.', hname, runtype, options_dict[runtype].tlabel, options_dict[runtype].xlabel, options_dict[runtype].xlabel_eta, dryrun=dryRun)
