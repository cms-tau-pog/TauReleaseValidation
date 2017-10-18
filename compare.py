''' Produces plots for tau release/data validation using the trees produced by
produceTauValTree.py
Authors: Yuta Takahashi, Michal Bluj, Jan Steggemann.
'''

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

from ROOT import gROOT, gStyle, TH1F, TFile, TCanvas, TPad, TLegend, TGraphAsymmErrors, Double, TLatex
from officialStyle import officialStyle
from array import array
import os
import argparse
from variables import vardict, hvardict


gROOT.SetBatch(True)
officialStyle(gStyle)
gStyle.SetOptTitle(0)

# set_palette("color")
# gStyle.SetPaintTextFormat("2.0f")


def ensureDir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def save(canvas, name):
    ensureDir('compare_' + runtype)
    canvas.SaveAs(name.replace(' ', '').replace('&&', '')+'.pdf')
    canvas.SaveAs(name.replace(' ', '').replace('&&', '')+'.gif')


def configureLegend(leg, ncolumn):
    leg.SetNColumns(ncolumn)
    leg.SetBorderSize(0)
    leg.SetFillColor(10)
    leg.SetLineColor(0)
    leg.SetFillStyle(0)
    leg.SetTextSize(0.03)
    leg.SetTextFont(42)


def overlay(hists, ytitle, header, addon):
    print 'number of histograms = ', len(hists)

    canvas = TCanvas()
    leg = TLegend(0.2, 0.7, 0.5, 0.9)
    configureLegend(leg, 1)

    ymax = -1
    ymin = 100

    for ii, hist in enumerate(hists):
        hist.GetYaxis().SetTitle('efficiency')
        hist.SetLineWidth(2)
        hist.SetMarkerSize(1)

        for ip in xrange(hist.GetN()):
            x = Double(-1)
            y = Double(-1)
            hist.GetPoint(ip, x, y)

            if ymin > y:
                ymin = y
            if ymax < y:
                ymax = y

        if ii == 0:
            hist.Draw("Azp")
        else:
            hist.Draw("pzsame")

#        print hist.GetName(), hist.GetTitle()
        legname = hist.GetName()

        leg.AddEntry(hist, legname, 'lep')

    for hist in hists:
        hist.SetMaximum(ymax*2)
#        hist.SetMinimum(ymin*0.5)

    leg.Draw()

    tex = TLatex(hists[-1].GetXaxis().GetXmin() + 0.01*(hists[-1].GetXaxis().GetXmax() -
                                                        hists[-1].GetXaxis().GetXmin()), ymax*2.1, addon.replace('tau_', ''))

    tex.SetTextFont(42)
    tex.SetTextSize(0.03)
    tex.Draw()

    xshift = 0.87
    # xshift=0.7
    if tlabel.find('QCD') != -1:
        xshift = 0.6
    tex2 = TLatex(hists[-1].GetXaxis().GetXmin() + xshift*(hists[-1].GetXaxis(
    ).GetXmax() - hists[-1].GetXaxis().GetXmin()), ymax*2.1, tlabel)

    tex2.SetTextFont(42)
    tex2.SetTextSize(0.03)
    tex2.Draw()

    save(canvas, 'compare_' + runtype + '/' + header)


def hoverlay(hists, xtitle, ytitle, name):
    c = TCanvas()
    # Upper plot will be in pad1
    pad1 = TPad("pad1", "pad1", 0, 0.3, 1, 1.0)
    pad1.SetBottomMargin(0)  # Upper and lower plot are joined
    pad1.Draw()             # Draw the upper pad: pad1
    pad1.cd()              # pad1 becomes the current pad
    if hname.find('isoPt') > -1 or hname.find('outOfConePt') > -1 or hname.find('IsoRaw') > -1:
        # c.SetLogy()
        pad1.SetLogy()
    else:
        # c.SetLogy(0)
        pad1.SetLogy(0)

    ymax = 0
    for hist in hists:
        if ymax < hist.GetMaximum():
            ymax = hist.GetMaximum()

    leg = TLegend(0.6, 0.65, 0.91, 0.9)
    configureLegend(leg, 1)

    hratios = []
    for ii, ihist in enumerate(hists):
        ihist.SetMaximum(ymax*1.2)
        ihist.SetMinimum(0.)
        # if c.GetLogy > 0:
        if pad1.GetLogy > 0:
            ihist.SetMinimum(0.001)
        ihist.SetMarkerSize(0.)
        ihist.GetXaxis().SetTitle(xtitle)
        ihist.GetYaxis().SetTitle(ytitle)

        if ii == 0:
            ihist.Draw('h')
        else:
            ihist.Draw('hsame')
            ihr = ihist.Clone()
            # ihr.Sumw2()
            ihr.Divide(hists[0])
            ihr.SetStats(0)
            ihr.SetLineColor(ihist.GetLineColor())
            ihr.SetMarkerColor(ihist.GetMarkerColor())
            ihr.SetMarkerStyle(hist.GetMarkerStyle())
            hratios.append(ihr)

        leg.AddEntry(ihist, ihist.GetName(), "l")

    leg.Draw()

    xshift = 0.87
    # xshift=0.7
    if tlabel.find('QCD') != -1:
        xshift = 0.6
    tex2 = TLatex(hists[0].GetXaxis().GetXmin(
    ) + xshift*(hists[0].GetXaxis().GetXmax() - hists[0].GetXaxis().GetXmin()), ymax*1.25, tlabel)

    tex2.SetTextFont(42)
    # tex2.SetTextSize(0.03)
    tex2.SetTextSize(0.043)
    tex2.Draw()

    # lower plot will be in pad
    c.cd()          # Go back to the main canvas before defining pad2
    pad2 = TPad("pad2", "pad2", 0, 0.05, 1, 0.25)
    pad2.SetTopMargin(0)
    pad2.SetBottomMargin(0.25)
    pad2.Draw()
    pad2.cd()
    for ii, ihist in enumerate(hratios):
        ihist.GetYaxis().SetTitle('ratio')
        ihist.SetMinimum(0.75)
        ihist.SetMaximum(1.25)
        ihist.GetYaxis().SetTitleOffset(0.33)
        ihist.GetYaxis().SetTitleSize(0.193)
        ihist.GetYaxis().SetLabelSize(0.175)
        ihist.GetXaxis().SetTitleSize(0.193)
        ihist.GetXaxis().SetLabelSize(0.175)
        if ii == 0:
            ihist.Draw('ep')
        else:
            ihist.Draw('epsame')

    c.cd()          # Go back to the main canvas

    save(c, 'compare_' + runtype + '/hist_' + name)


def makeEffPlotsVars(tree, varx, vary, sel, nbinx, xmin, xmax, nbiny, ymin, ymax, xtitle, ytitle, leglabel=None, header='', addon='', option='pt', marker=20, col=1):

    binning = [20, 30, 40, 50, 60, 70, 80, 100, 150, 200]

    if option == 'pt':
        _hist_ = TH1F('h_effp_' + addon, 'h_effp' + addon,
                      len(binning)-1, array('d', binning))
        _ahist_ = TH1F('ah_effp_' + addon, 'ah_effp' + addon,
                       len(binning)-1, array('d', binning))
    elif option == 'eta':
        _hist_ = TH1F('h_effp_' + addon, 'h_effp' + addon, nbinx, xmin, xmax)
        _ahist_ = TH1F('ah_effp_' + addon, 'ah_effp' +
                       addon, nbinx, xmin, xmax)

    tree.Draw(varx + ' >> ' + _hist_.GetName(), sel)
    tree.Draw(varx + ' >> ' + _ahist_.GetName(), sel + ' && ' + vary)

    g_efficiency = TGraphAsymmErrors()
    g_efficiency.BayesDivide(_ahist_, _hist_)
    g_efficiency.GetXaxis().SetTitle(xtitle)
    g_efficiency.GetYaxis().SetTitle('efficiency')
    g_efficiency.GetYaxis().SetNdivisions(507)
    g_efficiency.SetLineWidth(3)
    g_efficiency.SetName(header)
    g_efficiency.SetMinimum(0.)
    g_efficiency.GetYaxis().SetTitleOffset(1.3)
    g_efficiency.SetMarkerStyle(marker)
    g_efficiency.SetMarkerSize(1)
    g_efficiency.SetMarkerColor(col)
    g_efficiency.SetLineColor(col)
    g_efficiency.Draw('ap')

#    save(c, 'plots/' + addon)
    return g_efficiency


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('runtype', choices=['ZTT', 'ZEE', 'ZMM', 'QCD', 'TTbar', 'TTbarTau', 'ZpTT'], help='choose sample type')
    parser.add_argument('--releases', help='comma separated list of releases', default='CMSSW_9_4_0_pre1,CMSSW_9_4_0_pre2')
    
    args = parser.parse_args()

    runtype = args.runtype
    print 'Producing plots for runtype', runtype
    
    releases = args.releases.split(',')
    
    print 'Releases', releases
    

    tlabel = 'Z #rightarrow #tau#tau'
    # tlabel = 'gg #rightarrow H(125) #rightarrow #tau#tau'
    xlabel = 'gen. tau p_{T}^{vis} (GeV)'
    xlabel_eta = 'gen. tau #eta^{vis}'

    if runtype == 'QCD':
        #tlabel = 'QCD'
        tlabel = 'QCD, flat #hat{p}_{T} 15-3000GeV'
        xlabel = 'jet p_{T} (GeV)'
        xlabel_eta = 'jet #eta'
    elif runtype == 'ZEE':
        tlabel = 'Z #rightarrow ee'
        xlabel = 'electron p_{T} (GeV)'
        xlabel_eta = 'electron #eta'
    elif runtype == 'ZMM':
        tlabel = 'Z #rightarrow #mu#mu'
        xlabel = 'muon p_{T} (GeV)'
        xlabel_eta = 'muon #eta'
    elif runtype == 'TTbar':
        tlabel = 'TTbar'
        xlabel = 'jet p_{T} (GeV)'
        xlabel_eta = 'jet #eta'
    elif runtype == 'TTbarTau':
        tlabel = 'TTbar #rightarrow #tau+X'
        xlabel = 'gen. tau p_{T}^{vis} (GeV)'
        xlabel_eta = 'gen. tau #eta^{vis}'

    reco_cut = 'tau_pt > 20 && abs(tau_eta) < 2.3'
    #loose_id = 'tau_decayModeFindingOldDMs > 0.5 && tau_byLooseCombinedIsolationDeltaBetaCorr3Hits > 0.5'
    loose_id = 'tau_decayModeFindingOldDMs > 0.5 && tau_byLooseIsolationMVArun2v1DBoldDMwLT > 0.5'

    styles = [
        {'col': 8, 'marker': 25, 'width': 2},
        {'col': 2, 'marker': 21, 'width': 2},
        {'col': 4, 'marker': 21, 'width': 2},
        {'col': 7, 'marker': 24, 'width': 2},
    ]
    
    sampledict = {}
    for i_sample, release in enumerate(releases):
        sampledict[release] = styles[i_sample]
        tfile = sampledict[release]['file'] = TFile('Myroot_{}_{}.root'.format(release, runtype))
        sampledict[release]['tree'] = tfile.Get('per_tau')

    for hname, hdict in sorted(vardict.iteritems()):

        hists = []
        histseta = []

        for rel, rdict in sorted(sampledict.iteritems()):
            tree = rdict['tree']

            num_sel = reco_cut
            den_sel = '1'

            if hname.find('against') != -1:
                #num_sel = '1'
                num_sel = reco_cut
                den_sel = reco_cut + ' && ' + loose_id

            hists.append(makeEffPlotsVars(tree, 'tau_genpt', num_sel + '&&' + hdict['var'], den_sel, 30, 0, 300, hdict[
                         'nbin'], hdict['min'], hdict['max'], xlabel, hdict['title'], '', rel, rel, 'pt', rdict['marker'], rdict['col']))
            histseta.append(makeEffPlotsVars(tree, 'tau_geneta', num_sel + '&&' + hdict['var'] + '&& tau_pt>20', den_sel + '&& tau_pt>20', 12, -2.4, 2.4, hdict[
                            'nbin'], hdict['min'], hdict['max'], xlabel_eta, hdict['title'], '', rel, rel, 'eta', rdict['marker'], rdict['col']))  # FIXME: use pt>20 or >30



        overlay(hists, hname, hname, hdict['title'])
        overlay(histseta, hname, hname+'_eta', hdict['title']+'_eta')

    

    for hname, hdict in sorted(hvardict.iteritems()):

        hists = []

        if runtype != 'ZTT' and runtype != 'TTbarTau' and hname.find('pt_resolution') != -1:
            continue

        for rel, rdict in sorted(sampledict.iteritems()):
            tree = rdict['tree']

            hist = TH1F('h_' + hname + '_' + rel, 'h_' + hname +
                        '_' + rel, hdict['nbin'], hdict['min'], hdict['max'])
            hist.GetYaxis().SetNdivisions(507)
            hist.SetLineColor(rdict['col'])
            hist.SetLineWidth(rdict['width'])
            hist.SetMinimum(0)
            hist.SetName(rel)
            hist.Sumw2()
            hist.GetXaxis().SetTitle(hdict['title'])

            tree.Project(hist.GetName(), hdict['var'], hdict['sel'])
            if hist.Integral(0, hist.GetNbinsX()+1) > 0:
                hist.Scale(1./hist.Integral(0, hist.GetNbinsX()+1))

            hists.append(hist)

        hoverlay(hists, hdict['title'], 'a.u.', hname)
