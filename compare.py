''' Produces plots for tau release/data validation using the trees produced by
produceTauValTree.py
Authors: Yuta Takahashi, Michal Bluj, Jan Steggemann.
'''

import re
import warnings
from array import array
from collections import namedtuple

# The following needs to come before any other ROOT import and before argparse
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
from officialStyle import officialStyle
from variables import vardict, hvardict
from compareTools import overlay, hoverlay, makeEffPlotsVars, fillSampledic, findLooseId, shiftAlongX

from ROOT import gROOT, gStyle, TH1F

import argparse
from relValTools import addArguments, dprint

gROOT.SetBatch(True)
officialStyle(gStyle)
gStyle.SetOptTitle(0)

RuntypeOptions = namedtuple("RuntypeOptions", "tlabel xlabel xlabel_eta")
options_dict = {
    'ZTT': RuntypeOptions(tlabel='Z #rightarrow #tau#tau', xlabel='gen. tau p_{T}^{vis} (GeV)', xlabel_eta='gen. tau #eta^{vis}'),
    'ZEE': RuntypeOptions(tlabel='Z #rightarrow ee', xlabel='electron p_{T} (GeV)', xlabel_eta='electron #eta'),
    'ZMM': RuntypeOptions(tlabel='Z #rightarrow #mu#mu', xlabel='muon p_{T} (GeV)', xlabel_eta='muon #eta'),
    'QCD': RuntypeOptions(tlabel='QCD, flat #hat{p}_{T} 15-3000GeV', xlabel='jet p_{T} (GeV)', xlabel_eta='jet #eta'),
    'TTbar': RuntypeOptions(tlabel='TTbar', xlabel='jet p_{T} (GeV)', xlabel_eta='jet #eta'),
    'TTbarTau': RuntypeOptions(tlabel='TTbar #rightarrow #tau+X', xlabel='gen. tau p_{T}^{vis} (GeV)', xlabel_eta='gen. tau #eta^{vis}'),
    'TenTaus': RuntypeOptions(tlabel='Ten taus', xlabel='gen. tau p_{T}^{vis} (GeV)', xlabel_eta='gen. tau #eta^{vis}'),
}


def is_number(s):
    try:
        float(s)
    except ValueError:
        return False
    return True


def word_finder(expr):
    words = re.compile(r'\w+').findall(expr)
    return [w for w in words if not is_number(w) and w not in ['min', 'max']]


def efficiency_plots(d_sample, var_name, hdict):
    graphs = []
    graphs_eta = []

    for rel, rdict in d_sample.items():
        tree = rdict['tree']
        if 'leaves' not in rdict:
            rdict['leaves'] = [leaf.GetName() for leaf in tree.GetListOfLeaves()]
        used_vars = word_finder(hdict['var'])
        if not set(used_vars).issubset(rdict['leaves']):
            warnings.warn(
                var_name + ' is missing in input file ' + rdict['file'].GetName())
            return
        num_sel = reco_cut
        den_sel = '1'
        discriminators = {"loose_id": den_sel}
        if 'against' in var_name:
            den_sel = reco_cut + ' && ' + loose_id

        for mvaIDname, sel in discriminators.items():
            graphs.append(makeEffPlotsVars(tree=tree,
                                           varx='tau_genpt',
                                           numeratorAddSelection=num_sel +
                                           '&&' + hdict['var'],
                                           baseSelection=sel +
                                           '&& abs(tau_eta) < 2.3',
                                           binning=ptPlotsBinning,
                                           xtitle=options_dict[runtype].xlabel,
                                           header=rel + mvaIDname, addon=rel + mvaIDname,
                                           marker=rdict['marker'],
                                           col=rdict['col']))

            graphs_eta.append(makeEffPlotsVars(tree=tree,
                                               varx='tau_geneta',
                                               numeratorAddSelection=num_sel +
                                               '&&' + hdict['var'],
                                               baseSelection=sel + '&& tau_pt>20',
                                               binning=etaPlotsBinning,
                                               xtitle=options_dict[runtype].xlabel_eta,
                                               header=rel + mvaIDname, addon=rel + mvaIDname,
                                               marker=rdict['marker'],
                                               col=rdict['col']))

    overlay(graphs=graphs,
            header=var_name,
            addon=hdict['title'],
            runtype=runtype,
            tlabel=options_dict[runtype].tlabel)

    overlay(graphs=graphs_eta,
            header=var_name + '_eta',
            addon=hdict['title'] + '_eta',
            runtype=runtype,
            tlabel=options_dict[runtype].tlabel)


def eff_plots_single(d_sample, vars_to_compare, var_dict):
    '''Adapted from Olena's code - can possibly merge it with efficiency_plots
    '''
    if not vars_to_compare:
        return

    hists = []
    histseta = []

    for index, var_name in enumerate(vars_to_compare):
        hdict = var_dict[var_name]
        if varyLooseId and 'IsolationMVA' in var_name:
            loose_id = 'tau_decayModeFindingOldDMs > 0.5 && ' + findLooseId(var_name)

        for _, rdict in d_sample.items():
            tree = rdict['tree']
            if 'leaves' not in rdict:
                rdict['leaves'] = [leaf.GetName() for leaf in tree.GetListOfLeaves()]
            used_vars = word_finder(hdict['var'])
            if not set(used_vars).issubset(rdict['leaves']):
                warnings.warn(
                    var_name + ' is missing in input file ' + rdict['file'].GetName())
                return
            num_sel = reco_cut
            den_sel = '1'
            discriminators = {"loose_id": den_sel}
            if 'against' in var_name:
                den_sel = reco_cut + ' && ' + loose_id

            for mvaIDname, sel in discriminators.items():
                dprint("\n\tmvaIDname:", mvaIDname, "hdict['var']:", hdict['var'])

                hists.append(makeEffPlotsVars(tree=tree,
                                              varx='tau_genpt',
                                              numeratorAddSelection=num_sel + '&&' + hdict['var'],
                                              baseSelection=sel + '&& abs(tau_eta) < 2.3',
                                              binning=ptPlotsBinning,
                                              xtitle=options_dict[runtype].xlabel,
                                              header=var_name + mvaIDname, addon=var_name + mvaIDname,
                                              marker=rdict['marker'],
                                              col=int(colors[index])))

                shiftAlongX(hists[-1], len(vars_to_compare), index)

                histseta.append(makeEffPlotsVars(tree=tree,
                                                 varx='tau_geneta',
                                                 numeratorAddSelection=num_sel + '&&' + hdict['var'],
                                                 baseSelection=sel + '&& tau_pt>20',
                                                 binning=etaPlotsBinning,
                                                 xtitle=options_dict[runtype].xlabel_eta,
                                                 header=var_name + mvaIDname, addon=var_name + mvaIDname,
                                                 marker=rdict['marker'],
                                                 col=int(colors[index])))

                shiftAlongX(histseta[-1], len(vars_to_compare), index)

    overlay(graphs=hists,
            header=vars_to_compare[0],
            addon=hdict['title'],
            runtype=runtype,
            tlabel=options_dict[runtype].tlabel,
            comparePerReleaseSuffix="_comparePerRelease")

    overlay(graphs=histseta,
            header=vars_to_compare[0] + '_eta',
            addon=hdict['title'] + '_eta',
            runtype=runtype,
            tlabel=options_dict[runtype].tlabel,
            comparePerReleaseSuffix="_comparePerRelease")


def var_plots(d_sample, var_name, hdict):
    hists = []
    for rel, rdict in d_sample.items():
        tree = rdict['tree']
        if 'leaves' not in rdict:
            rdict['leaves'] = [leaf.GetName() for leaf in tree.GetListOfLeaves()]
        used_vars = word_finder(hdict['var'])
        if not set(used_vars).issubset(rdict['leaves']):
            warnings.warn(
                var_name + ' is missing in input file ' + rdict['file'].GetName())
            return
        hist = TH1F('h_' + var_name + '_' + rel, 'h_' + var_name +
                    '_' + rel, hdict['nbin'], hdict['min'], hdict['max'])

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

    hoverlay(hists=hists,
             xtitle=hdict['title'],
             ytitle='a.u.',
             name=var_name,
             runtype=runtype,
             tlabel=options_dict[runtype].tlabel,
             xlabel=options_dict[runtype].xlabel,
             xlabel_eta=options_dict[runtype].xlabel_eta)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    addArguments(parser, produce=False, compare=True)
    args = parser.parse_args()
    part = args.part
    inputfiles = args.inputfiles

    runtype = args.runtype
    releases = args.releases
    globaltags = args.globalTags
    # The following three are for Olena's variable comparison
    variables = args.variables
    varyLooseId = args.varyLooseId
    colors = args.colors

    sampledict = fillSampledic(
        globaltags, releases, runtype, inputfiles)

    ptPlotsBinning = array('d', [20, 200]) if args.onebin else array(
        'd', [20, 30, 40, 50, 60, 70, 80, 100, 150, 200])
    etaPlotsBinning = array('d', [-2.4, 2]) if args.onebin else array(
        'd', [round(-2.4 + i * 0.4, 1) for i in range(13)])
    reco_cut = 'tau_pt > 20 && abs(tau_eta) < 2.3'
    # loose_id = 'tau_decayModeFinding > 0.5 && tau_byLooseCombinedIsolationDeltaBetaCorr3Hits > 0.5'
    loose_id = 'tau_decayModeFinding > 0.5 && tau_byLooseIsolationMVArun2v1DBoldDMwLT > 0.5'

    print "First part of plots"
    if part in [0, 1]:
        for h_name, h_dict in vardict.items():
            efficiency_plots(sampledict, h_name, h_dict)

        # Add Olena's per-release/GT plots into this script
        if variables and len(releases) == 1 and len(globaltags) == 1:
            eff_plots_single(sampledict, variables, vardict)

    print "End first part of plots"
    if part == 1:
        exit()

    if part == 2:
        print "Second part of plots"
    for index, (h_name, h_dict) in enumerate(hvardict.iteritems()):
        print index, ":", h_name
        if part == 2 and index > len(hvardict.items()) / 2:
            break
        elif part == 3 and index <= len(hvardict.items()) / 2:
            continue
        elif part == 3 and index - 1 == len(hvardict.items()) / 2:
            print "Third part of plots"

        if runtype not in ['ZTT', 'TTbarTau'] and h_name.find('pt_resolution') != -1:
            continue

        var_plots(sampledict, h_name, h_dict)

    print "Finished"
