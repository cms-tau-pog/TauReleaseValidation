''' Produces plots for tau release/data validation using the trees produced by
produceTauValTree.py
Authors: Yuta Takahashi, Michal Bluj, Jan Steggemann.
'''

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

from ROOT import gROOT, gStyle, TH1F, TFile, TCanvas, TPad, TLegend, TGraphAsymmErrors, Double, TLatex
from officialStyle import officialStyle
from array import array
import warnings
from collections import namedtuple
import argparse
from variables import vardict, hvardict

from relValTools import addArguments
from compareTools import overlay, hoverlay, ensureDir, save, configureLegend, findLooseId, shiftAlongX, makeEffPlotsVars, fillSampledic

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
    debug = args.debug
    inputfiles = args.inputfiles

    runtype = args.runtype
    releases = args.releases
    globaltags = args.globalTags
    if debug: print 'Producing plots for runtype', runtype, '\nReleases:', releases, '\nGlobal tags:', globaltags
    sampledict = fillSampledic(globaltags, releases, runtype, inputfiles, debug)

    RuntypeOptions = namedtuple("RuntypeOptions", "tlabel xlabel xlabel_eta")
    options_dict = {
        'ZTT':      RuntypeOptions(tlabel = 'Z #rightarrow #tau#tau',           xlabel = 'gen. tau p_{T}^{vis} (GeV)',  xlabel_eta = 'gen. tau #eta^{vis}'),
        'ZEE':      RuntypeOptions(tlabel = 'Z #rightarrow ee',                 xlabel = 'electron p_{T} (GeV)',        xlabel_eta = 'electron #eta'),
        'ZMM':      RuntypeOptions(tlabel = 'Z #rightarrow #mu#mu',             xlabel = 'muon p_{T} (GeV)',            xlabel_eta = 'muon #eta'),
        'QCD':      RuntypeOptions(tlabel = 'QCD, flat #hat{p}_{T} 15-3000GeV', xlabel = 'jet p_{T} (GeV)',             xlabel_eta = 'jet #eta'),
        'TTbar':    RuntypeOptions(tlabel = 'TTbar',                            xlabel = 'jet p_{T} (GeV)',             xlabel_eta = 'jet #eta'),
        'TTbarTau': RuntypeOptions(tlabel = 'TTbar #rightarrow #tau+X',         xlabel = 'gen. tau p_{T}^{vis} (GeV)',  xlabel_eta = 'gen. tau #eta^{vis}')
    }

    ptPlotsBinning  = array('d', [20, 200]) if args.onebin else array('d', [20, 30, 40, 50, 60, 70, 80, 100, 150, 200])
    etaPlotsBinning = array('d', [-2.4, 2]) if args.onebin else array('d', [round(-2.4 + i*0.4,1) for i in range(0, 12 + 1)])
    reco_cut = 'tau_pt > 20 && abs(tau_eta) < 2.3'
    #loose_id = 'tau_decayModeFindingOldDMs > 0.5 && tau_byLooseCombinedIsolationDeltaBetaCorr3Hits > 0.5'
    loose_id = 'tau_decayModeFindingOldDMs > 0.5 && tau_byLooseIsolationMVArun2v1DBoldDMwLT > 0.5'
    loose_id_17v2 = 'tau_decayModeFindingOldDMs > 0.5 && tau_byLooseIsolationMVArun2017v2DBoldDMwLT2017 > 0.5'

    print "First part of plots"
    if part in [0, 1]:
        for hname, hdict in vardict.items():
            if debug:
                print '\n', "*"*10, "\nhname:", hname
            hists = []
            histseta = []
            oneOfTheInputHasNoLeaf = False

            for rel, rdict in sampledict.items():
                if debug:
                    print "\trel:", rel
                tree = rdict['tree']
                if not set(hdict['checkTree']).issubset([ x.GetName() for x in tree.GetListOfLeaves()]):
                    warnings.warn(hname + ' is minning in input file ' + rdict['file'].GetName())
                    oneOfTheInputHasNoLeaf = True
                    break
                num_sel = reco_cut
                den_sel = '1'
                den_sel_17v2 = '1'
                discriminators = {"loose_id": den_sel}
                if 'against' in hname:
                    den_sel = reco_cut + ' && ' + loose_id
                    den_sel_17v2 = reco_cut + ' && ' + loose_id_17v2
                    discriminators["loose_id"] = den_sel
                    discriminators["loose_id_17v2"] = den_sel_17v2


                for mvaIDname, sel in discriminators.items():
                    print "\n\tmvaIDname:", mvaIDname, "hdict['var']:", hdict['var']

                    hists.append(makeEffPlotsVars(tree=tree,
                        varx='tau_genpt',
                        numeratorAddSelection=num_sel + '&&' + hdict['var'],
                        baseSelection=sel + '&& abs(tau_eta) < 2.3',
                        xtitle=options_dict[runtype].xlabel,
                        header=rel + mvaIDname, addon=rel + mvaIDname,
                        option='pt',
                        marker=rdict['marker'] + 1 * (mvaIDname == "loose_id_17v2"),
                        col=rdict['col'],
                        ptPlotsBinning=ptPlotsBinning,
                        debug=True)
                    )

                    histseta.append(makeEffPlotsVars(tree=tree,
                        varx='tau_geneta',
                        numeratorAddSelection=num_sel + '&&' + hdict['var'],
                        baseSelection=sel + '&& tau_pt>20',
                        xtitle=options_dict[runtype].xlabel_eta,
                        header=rel + mvaIDname, addon=rel + mvaIDname,
                        option='eta',
                        marker=rdict['marker'] + 1 * (mvaIDname == "loose_id_17v2"),
                        col=rdict['col'],
                        ptPlotsBinning=etaPlotsBinning,
                        debug=False)
                    )
            if oneOfTheInputHasNoLeaf: continue
            overlay(hists=hists, ytitle=hname,
                header=hname,
                addon=hdict['title'],
                runtype=runtype,
                tlabel=options_dict[runtype].tlabel,
                xlabel=options_dict[runtype].xlabel,
                dryrun=dryRun,
                debug=True)

            overlay(hists=histseta, ytitle=hname,
                header=hname + '_eta',
                addon=hdict['title'] + '_eta',
                runtype=runtype,
                tlabel=options_dict[runtype].tlabel,
                xlabel=options_dict[runtype].xlabel,
                dryrun=dryRun,
                debug=False)

    if part == 1: exit()

    print "Second part of plots"
    for index, (hname, hdict) in enumerate(hvardict.iteritems()):
        print  index, ":", hname
        if   part == 2 and index >  len(hvardict.items()) / 2: exit()
        elif part == 3 and index <= len(hvardict.items()) / 2: continue
        elif part == 3 and index - 1 == len(hvardict.items()) / 2: print "Third part of plots"

        if runtype not in ['ZTT', 'TTbarTau'] and hname.find('pt_resolution') != -1: continue

        hists = []
        oneOfTheInputHasNoLeaf = False
        for rel, rdict in sampledict.items():
            tree = rdict['tree']
            if not set(hdict['checkTree']).issubset([ x.GetName() for x in tree.GetListOfLeaves()]):
                warnings.warn(hname + ' is minning in input file ' + rdict['file'].GetName())
                oneOfTheInputHasNoLeaf = True
                break
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

        if oneOfTheInputHasNoLeaf: continue
        hoverlay(hists=hists,
            xtitle=hdict['title'],
            ytitle='a.u.',
            name=hname,
            runtype=runtype,
            tlabel=options_dict[runtype].tlabel,
            xlabel=options_dict[runtype].xlabel,
            xlabel_eta=options_dict[runtype].xlabel_eta,
            dryrun=dryRun)

    print "Finished"
