from officialStyle import officialStyle
from array import array
from ROOT import gROOT, gStyle, TH1F, TH1D, TF1, TFile, TCanvas, TPad, TH2F, TLegend, TGraphAsymmErrors, Double, TLatex
import os
import copy
import sys

gROOT.SetBatch(True)
officialStyle(gStyle)
gStyle.SetOptTitle(0)
# set_palette("color")
# gStyle.SetPaintTextFormat("2.0f")


argvs = sys.argv
argc = len(argvs)

if argc != 2:
    print 'Please specify the runtype : python tauPOGplot.py <ZTT, ZEE, ZMM, QCD>'
    sys.exit(0)

runtype = argvs[1]
print 'You selected', runtype


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


def ensureDir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def save(canvas, name):
    ensureDir('compare_' + runtype)
    canvas.SaveAs(name.replace(' ', '').replace('&&', '')+'.pdf')
    canvas.SaveAs(name.replace(' ', '').replace('&&', '')+'.gif')


def LegendSettings(leg, ncolumn):
    leg.SetNColumns(ncolumn)
    leg.SetBorderSize(0)
    leg.SetFillColor(10)
    leg.SetLineColor(0)
    leg.SetFillStyle(0)
    leg.SetTextSize(0.03)
    leg.SetTextFont(42)


def makeCompareVars(tree, var, sel, leglist, nbin, xmin, xmax, xtitle, ytitle, scale, name):

    #    print leglist

    c = TCanvas()

    hists = []
    col = [1, 2, 4, 8, 6]
    ymax = 0

    for ii, isel in enumerate(sel):
        hist = TH1F('h_' + str(ii), 'h_' + str(ii), nbin, xmin, xmax)
        hist.GetXaxis().SetTitle(xtitle)
        hist.GetYaxis().SetTitle(ytitle)
        hist.GetYaxis().SetNdivisions(507)
        hist.SetLineColor(col[ii])
        hist.SetLineWidth(len(sel)+1-ii)
        hist.SetLineStyle(1)
        hist.SetMarkerSize(0)
        hist.SetMinimum(0)
        hist.Sumw2()

#        print hist.GetName(), var, isel
        tree.Project(hist.GetName(), var, isel)
        hist.Scale(1./hist.Integral(0, hist.GetNbinsX()+1))

        if ymax < hist.GetMaximum():
            ymax = hist.GetMaximum()

        hists.append(hist)

    leg = TLegend(0.6, 0.65, 0.91, 0.9)
    LegendSettings(leg, 1)

    if var.find('PtSum') != -1 or var.find('outOfConePt') != -1 or var.find('IsoRaw') != -1:
        c.SetLogy()

    for ii, ihist in enumerate(hists):
        ihist.SetMaximum(ymax*1.2)
        ihist.SetMinimum(0.)
        if c.GetLogy > 0:
            ihist.SetMinimum(0.001)

        if ii == 0:
            ihist.Draw('h')
        else:
            ihist.Draw('hsame')

        if leglist[ii] != 'None':
            leg.AddEntry(ihist, leglist[ii], "l")

    if leglist[0] != 'None':
        leg.Draw()


#    save(c, 'compare_' + runtype + '/compare_' + name)


def overlay(hists, ytitle, header, addon):

    print 'number of histograms = ', len(hists)

    canvas = TCanvas()
    leg = TLegend(0.2, 0.7, 0.5, 0.9)
    LegendSettings(leg, 1)

    col = [1, 2, 4, 6, 8, 9, 12]

    ymax = -1
    ymin = 100

    # if header.find('against')!=-1 and (runtype.find('ZMM')!=-1 or runtype.find('ZEE')!=-1):
    #    canvas.SetLogy()

    for ii, hist in enumerate(hists):
        hist.GetYaxis().SetTitle('efficiency')
        # hist.SetLineColor(col[ii])
        # hist.SetMarkerColor(col[ii])
        hist.SetLineWidth(2)
        hist.SetMarkerSize(1)

        for ip in range(hist.GetN()):
            x = Double(-1)
            y = Double(-1)
            hist.GetPoint(ip, x, y)

            if ymin > y:
                ymin = y
            if ymax < y:
                ymax = y

#
#        if ymax < hist.GetMaximum():
#            ymax = hist.GetMaximum()
#        if ymin > hist.GetMinimum():
#            ymin = hist.GetMinimum()

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
    LegendSettings(leg, 1)

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

    c = TCanvas()

    if option == 'pt':
        _hist_ = TH1F('h_effp_' + addon, 'h_effp' + addon,
                      len(binning)-1, array('d', binning))
        _ahist_ = TH1F('ah_effp_' + addon, 'ah_effp' + addon,
                       len(binning)-1, array('d', binning))
    elif option == 'eta':
        _hist_ = TH1F('h_effp_' + addon, 'h_effp' + addon, nbinx, xmin, xmax)
        _ahist_ = TH1F('ah_effp_' + addon, 'ah_effp' +
                       addon, nbinx, xmin, xmax)
    elif option == 'nvtx':
        _hist_ = TH1F('h_effp_' + addon, 'h_effp' + addon,
                      len(vbinning)-1, array('d', vbinning))
        _ahist_ = TH1F('ah_effp_' + addon, 'ah_effp' + addon,
                       len(vbinning)-1, array('d', vbinning))

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

    return copy.deepcopy(g_efficiency)


if __name__ == '__main__':

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

    reco_cut = 'tau_pt > 20 && abs(tau_eta) < 2.3'
    #loose_id = 'tau_decayModeFindingOldDMs > 0.5 && tau_byLooseCombinedIsolationDeltaBetaCorr3Hits > 0.5'
    loose_id = 'tau_decayModeFindingOldDMs > 0.5 && tau_byLooseIsolationMVArun2v1DBoldDMwLT > 0.5'

    sampledict = {
        #'7_6_0_pre7':{'file':'Myroot_7_6_0_pre7_' + runtype + '.root', 'col':2, 'marker':20, 'width':3},
        #        '7_6_0':{'file':'Myroot_7_6_0_' + runtype + '.root', 'col':1, 'marker':21, 'width':4},
        #'7_6_1':{'file':'Myroot_7_6_1_' + runtype + '.root', 'col':4, 'marker':22, 'width':2},
        #'7_6_1_v3':{'file':'Myroot_7_6_1_v3_' + runtype + '.root', 'col':3, 'marker':23, 'width':1},
        #'7_6_3':{'file':'Myroot_7_6_3_' + runtype + '.root', 'col':1, 'marker':23, 'width':2},
        #'8_0_1':{'file':'Myroot_8_0_1_' + runtype + '.root', 'col':2, 'marker':21, 'width':2},
        #'8_0_3_newGT':{'file':'Myroot_8_0_3_' + runtype + '.root', 'col':4, 'marker':22, 'width':2},
        #'8_0_3_newGT':{'file':'Myroot_8_0_3_' + runtype + '.root', 'col':1, 'marker':23, 'width':2},
        #'8_1_0_pre6':{'file':'Myroot_8_1_0_pre6_' + runtype + '.root', 'col':2, 'marker':21, 'width':2},
        #'8_1_0_pre7':{'file':'Myroot_8_1_0_pre7_' + runtype + '.root', 'col':4, 'marker':22, 'width':2},
        #'8_1_0_pre12':{'file':'Myroot_8_1_0_pre12_' + runtype + '.root', 'col':1, 'marker':23, 'width':2},
        #'8_1_0_pre12_2017ref':{'file':'Myroot_8_1_0_pre12_2017_' + runtype + '.root', 'col':2, 'marker':21, 'width':2},
        #'8_1_0_pre12_2017ph1':{'file':'Myroot_8_1_0_pre12_2017ph1_' + runtype + '.root', 'col':4, 'marker':22, 'width':2},
        #'8_1_0_2016ref':{'file':'Myroot_8_1_0_' + runtype + '.root', 'col':2, 'marker':21, 'width':2},
        #'8_1_0_2017ph1':{'file':'Myroot_8_1_0_2017ph1_' + runtype + '.root', 'col':4, 'marker':22, 'width':2},
        #'Spring16':{'file':'Myroot_8_0_11_spr16_' + runtype + '.root', 'col':2, 'marker':21, 'width':2},
        #'Summer16':{'file':'Myroot_8_0_21_sum16_' + runtype + '.root', 'col':4, 'marker':22, 'width':2},
        #'9_0_0_pre4':{'file':'Myroot_9_0_0_pre4_' + runtype + '.root', 'col':2, 'marker':21, 'width':2},
        #'9_0_0_pre5':{'file':'Myroot_9_0_0_pre5_' + runtype + '.root', 'col':4, 'marker':22, 'width':2},
        #'9_0_0_pre5':{'file':'Myroot_9_0_0_pre5_' + runtype + '.root', 'col':8, 'marker':20, 'width':2},
        #'9_0_0_pre6':{'file':'Myroot_9_0_0_pre6_' + runtype + '.root', 'col':2, 'marker':21, 'width':2},
        #'9_0_0':{'file':'Myroot_9_0_0_' + runtype + '.root', 'col':4, 'marker':22, 'width':2},
        #'9_1_0_pre1':{'file':'Myroot_9_1_0_pre1_' + runtype + '.root', 'col':1, 'marker':21, 'width':2},
        #'9_1_0_pre2':{'file':'Myroot_9_1_0_pre2_' + runtype + '.root', 'col':2, 'marker':20, 'width':2},
        #'9_1_0_pre2_2017':{'file':'Myroot_9_1_0_pre2_' + runtype + '.root', 'col':4, 'marker':22, 'width':2},
        #'9_1_0_pre2_2023':{'file':'Myroot_9_1_0_pre2_2023_' + runtype + '.root', 'col':2, 'marker':21, 'width':2},
        #'9_2_2':{'file':'Myroot_9_2_2_' + runtype + '.root', 'col':4, 'marker':22, 'width':2},
        #'9_2_7':{'file':'Myroot_9_2_7_' + runtype + '.root', 'col':2, 'marker':21, 'width':2},
        #'9_3_0_pre1':{'file':'Myroot_9_3_0_pre1_' + runtype + '.root', 'col':7, 'marker':24, 'width':2},
        #'9_3_0_pre2':{'file':'Myroot_9_3_0_pre2_' + runtype + '.root', 'col':8, 'marker':25, 'width':2},
        #'9_3_0_pre3':{'file':'Myroot_9_3_0_pre3_' + runtype + '.root', 'col':7, 'marker':24, 'width':2},
        # 'MCv1_9_2_8': {'file': 'Myroot_9_2_8_default_' + runtype + '.root', 'col': 4, 'marker': 22, 'width': 2},
        'ZSfix_9_2_8': {'file': 'Myroot_9_2_8_ZSfix_' + runtype + '.root', 'col': 8, 'marker': 25, 'width': 2},
        # 'RelVal_9_2_8': {'file': 'Myroot_9_2_8_' + runtype + '.root', 'col': 2, 'marker': 21, 'width': 2},
    }

    for hname, hdict in sorted(vardict.iteritems()):

        hists = []
        histseta = []

        for rel, rdict in sorted(sampledict.iteritems()):

            if rel.find('7_6_1') == -1 and rel.find('7_6_3') == -1 and rel.find('8_0_') == -1 and rel.find('8_1_') == -1 and rel.find('9_') == -1 and rel.find('Spring16') == -1 and rel.find('Summer16') == -1 and (hname.find('MVA6') != -1 or hname.find('MVArun2') != -1):
                continue

            tfile = TFile(rdict['file'])
            tree = tfile.Get('per_tau')

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


#            if rel=='7_6_1' and (hname.find('MVA5')!=-1 or hname.find('IsolationMVA3')!=-1):
#                xvar = hdict['var'].replace('IsolationMVA3', 'IsolationMVArun2v1DB').replace('MVA5','MVA6')
#                print 'adding', xvar
#
#                hists.append(makeEffPlotsVars(tree, 'tau_genpt', num_sel + '&&' + xvar, den_sel, 30, 0, 300, hdict['nbin'], hdict['min'], hdict['max'], xlabel, hdict['title'], '', rel + '(' + xvar.replace('tau_','').replace('> 0.5','').replace(' && decayModeFindingOldDMs ','') + ')', rel, 'pt', rdict['marker'], rdict['col']))

        overlay(hists, hname, hname, hdict['title'])
        overlay(histseta, hname, hname+'_eta', hdict['title']+'_eta')

    hvardict = {
        'tau_pt': {'var': 'tau_pt', 'nbin': 24, 'min': 0., 'max': 120, 'title': 'p_T [GeV]', 'sel': 'tau_genpt>0&&tau_pt>0'},
        'tau_phi': {'var': 'tau_phi', 'nbin': 16, 'min': -3.2, 'max': 3.2, 'title': 'phi', 'sel': 'tau_genpt>0&&tau_pt>0'},
        'tau_eta': {'var': 'tau_eta', 'nbin': 12, 'min': -2.4, 'max': 2.4, 'title': 'eta', 'sel': 'tau_genpt>0&&tau_pt>0'},
        'tau_dm': {'var': 'tau_dm', 'nbin': 12, 'min': 0., 'max': 12, 'title': 'decay Mode', 'sel': 'tau_genpt>0&&tau_pt>0'},
        'tau_dm_chiso': {'var': 'tau_dm', 'nbin': 12, 'min': 0., 'max': 12, 'title': 'decay Mode', 'sel': 'tau_genpt>0&&tau_pt>0&&tau_chargedIsoPtSum < 2.5'},
        'tau_dm_combiso': {'var': 'tau_dm', 'nbin': 12, 'min': 0., 'max': 12, 'title': 'decay Mode', 'sel': 'tau_genpt>0&&tau_pt>0&&tau_byLooseCombinedIsolationDeltaBetaCorr3Hits > 0.5'},
        'charged_isoPt': {'var': 'tau_chargedIsoPtSum', 'nbin': 20, 'min': 0., 'max': 10, 'title': 'charged iso [GeV]', 'sel': 'tau_genpt>0&&tau_pt>0'},
        'charged_isoPt_diff': {'var': '2.*(tau_chargedIsoPtSum-tau_iso_dz02)/(tau_chargedIsoPtSum+tau_iso_dz02)', 'nbin': 40, 'min': -2., 'max': 2, 'title': '2*(charged iso-iso02)/(charged iso+iso02)', 'sel': 'tau_genpt>0&&tau_pt>0&&tau_chargedIsoPtSum+tau_iso_dz02>0'},
        #'charged_isoPt02':{'var':'tau_iso_dz02', 'nbin':20, 'min':0., 'max':10, 'title':'charged iso (|dz|<0.2cm) [GeV]', 'sel':'tau_genpt>0&&tau_pt>0'},
        #'charged_isoPt01':{'var':'tau_iso_dz02', 'nbin':20, 'min':0., 'max':10, 'title':'charged iso (|dz|<0.1cm) [GeV]', 'sel':'tau_genpt>0&&tau_pt>0'},
        #'charged_isoPt001':{'var':'tau_iso_dz001', 'nbin':20, 'min':0., 'max':10, 'title':'charged iso (|dz|<0.015cm) [GeV]', 'sel':'tau_genpt>0&&tau_pt>0'},
        #'charged_isoPt003':{'var':'tau_iso_dz001', 'nbin':20, 'min':0., 'max':10, 'title':'charged iso (|dz|<0.03cm) [GeV]', 'sel':'tau_genpt>0&&tau_pt>0'},
        'charged_isoPtPV': {'var': 'tau_iso_pv', 'nbin': 20, 'min': 0., 'max': 10, 'title': 'charged iso (PV) [GeV]', 'sel': 'tau_genpt>0&&tau_pt>0'},
        'charged_isoPtNoPV': {'var': 'tau_iso_nopv', 'nbin': 20, 'min': 0., 'max': 10, 'title': 'charged iso (npPV) [GeV]', 'sel': 'tau_genpt>0&&tau_pt>0'},
        'charged_isoPtNoPV_frac': {'var': 'tau_iso_nopv/(tau_iso_dz02+0.005)', 'nbin': 20, 'min': 0., 'max': 1, 'title': 'charged iso npPV fraction', 'sel': 'tau_genpt>0&&tau_pt>0'},
        'neutral_isoPt': {'var': 'tau_neutralIsoPtSum', 'nbin': 20, 'min': 0., 'max': 10, 'title': 'neutral iso [GeV]', 'sel': 'tau_genpt>0&&tau_pt>0'},
        'neutral_isoPt_diff': {'var': '2.*(tau_neutralIsoPtSum-tau_iso_neu)/(tau_neutralIsoPtSum+tau_iso_neu)', 'nbin': 40, 'min': -2., 'max': 2, 'title': '2*(neutral iso AOD-MiniAOD)/(neutral iso AOD+MiniAOD)', 'sel': 'tau_genpt>0&&tau_pt>0&&tau_neutralIsoPtSum+tau_iso_neu>0'},
        'neutral_isoPt_corr': {'var': 'max(0,tau_neutralIsoPtSum-0.2*tau_puCorrPtSum)', 'nbin': 20, 'min': 0, 'max': 10, 'title': 'neutral-iso - 0.2*PU-Pt-Sum [GeV]', 'sel': 'tau_genpt>0&&tau_pt>0'},
        'neutral_isoPt_corr2': {'var': 'max(0,tau_neutralIsoPtSum-0.2*tau_puCorrPtSum)', 'nbin': 20, 'min': 0, 'max': 10, 'title': 'out-of-cone-Pt/Pt < 0.1; neutral-iso - 0.2*PU-Pt-Sum [GeV]', 'sel': 'tau_genpt>0&&tau_pt>0&&tau_photonPtSumOutsideSignalCone/tau_pt<0.1'},
        'outOfConePt_over_pt': {'var': 'tau_photonPtSumOutsideSignalCone/tau_pt', 'nbin': 25, 'min': 0., 'max': 0.25, 'title': 'out-of-cone-Pt/Pt', 'sel': 'tau_genpt>0&&tau_pt>0'},
        'pu_isoPt': {'var': 'tau_puCorrPtSum', 'nbin': 50, 'min': 0., 'max': 100, 'title': 'PU charged PtSum [GeV]', 'sel': 'tau_genpt>0&&tau_pt>0'},
        'tau_mass_1prong': {'var': 'tau_mass', 'nbin': 30, 'min': 0., 'max': 2.5, 'title': 'Tau mass, 1prong', 'sel': 'tau_genpt>0&&tau_pt>0&&tau_dm==0'},
        'tau_mass_1prongp0': {'var': 'tau_mass', 'nbin': 30, 'min': 0., 'max': 2.5, 'title': 'Tau mass, 1prong+#pi^{0}', 'sel': 'tau_genpt>0&&tau_pt>0&&tau_dm==1'},
        'tau_mass_2prong': {'var': 'tau_mass', 'nbin': 30, 'min': 0., 'max': 2.5, 'title': 'Tau mass, 2prong', 'sel': 'tau_genpt>0&&tau_pt>0&&(tau_dm==5 || tau_dm==6)'},
        'tau_mass_3prong': {'var': 'tau_mass', 'nbin': 30, 'min': 0., 'max': 2.5, 'title': 'Tau mass, 3prong (+#pi^{0})', 'sel': 'tau_genpt>0&&tau_pt>0&&(tau_dm==10 || tau_dm==11)'},
        'tau_mass_3prong_old': {'var': 'tau_mass', 'nbin': 30, 'min': 0., 'max': 2.5, 'title': 'Tau mass, 3prong (0#pi^{0})', 'sel': 'tau_genpt>0&&tau_pt>0&&tau_dm==10'},
        'tau_mass_oldDM': {'var': 'tau_mass', 'nbin': 30, 'min': 0., 'max': 2.5, 'title': 'Tau mass (oldDMs)', 'sel': 'tau_genpt>0&&tau_pt>0&&tau_decayModeFindingOldDMs > 0.5'},
        'tau_MVAIsoRaw': {'var': 'tau_byIsolationMVArun2v1DBoldDMwLTraw', 'nbin': 40, 'min': -1., 'max': 1, 'title': 'Raw IsoMVA (oldDMs)', 'sel': 'tau_genpt>0&&tau_pt>0&&tau_decayModeFindingOldDMs > 0.5'},
        # as before but w/o Iso in the name to not use log scale (dirty)
        'tau_MVARaw': {'var': 'tau_byIsolationMVArun2v1DBoldDMwLTraw', 'nbin': 40, 'min': -1., 'max': 1, 'title': 'Raw IsoMVA (oldDMs)', 'sel': 'tau_genpt>0&&tau_pt>0&&tau_decayModeFindingOldDMs > 0.5'},
        'tau_CombIsoRaw': {'var': 'tau_byCombinedIsolationDeltaBetaCorrRaw3Hits', 'nbin': 20, 'min': 0., 'max': 10, 'title': 'combined iso (oldDMs) (GeV)', 'sel': 'tau_genpt>0&&tau_pt>0&&tau_decayModeFindingOldDMs > 0.5'},
        'nVertex': {'var': 'tau_vertex', 'nbin': 50, 'min': 0., 'max': 50, 'title': 'no. of vertices', 'sel': '1'},
        'nPU': {'var': 'tau_nPU', 'nbin': 50, 'min': 0., 'max': 50, 'title': 'no. of pileup', 'sel': '1'},
        'tau_dxy': {'var': 'tau_dxy', 'nbin': 50, 'min': 0., 'max': 0.1, 'title': 'tau_dxy', 'sel': 'tau_genpt>0&&tau_pt>0'},
        'tau_dxy_err': {'var': 'tau_dxy_err', 'nbin': 40, 'min': 0., 'max': 0.02, 'title': 'tau_dxy_err', 'sel': 'tau_genpt>0&&tau_pt>0'},
        'tau_dxy_sig': {'var': 'tau_dxy_sig', 'nbin': 25, 'min': 0., 'max': 5, 'title': 'tau_dxy_sig', 'sel': 'tau_genpt>0&&tau_pt>0'},
        'tau_ip3d': {'var': 'tau_ip3d', 'nbin': 50, 'min': 0., 'max': 0.1, 'title': 'tau_ipd3', 'sel': 'tau_genpt>0&&tau_pt>0'},
        'tau_ip3d_err': {'var': 'tau_ip3d_err', 'nbin': 40, 'min': 0., 'max': 0.02, 'title': 'tau_ip3d_err', 'sel': 'tau_genpt>0&&tau_pt>0'},
        'tau_ip3d_sig': {'var': 'tau_ip3d_sig', 'nbin': 25, 'min': 0., 'max': 5, 'title': 'tau_ip3d_sig', 'sel': 'tau_genpt>0&&tau_pt>0'},
        'tau_flightLength': {'var': 'tau_flightLength', 'nbin': 50, 'min': 0., 'max': 0.1, 'title': 'tau_flightLength', 'sel': 'tau_genpt>0&&tau_pt>0&&tau_flightLength>=0'},
        'tau_flightLength_sig': {'var': 'tau_flightLength_sig', 'nbin': 25, 'min': 0., 'max': 5, 'title': 'tau_flightLength_sig', 'sel': 'tau_genpt>0&&tau_pt>0&&tau_flightLength>=0'},

        'pt_resolution_1prong': {'var': '(tau_genpt-tau_pt)/(tau_genpt)', 'nbin': 30, 'min': -1., 'max': 1., 'title': 'pT resolution, 1prong', 'sel': 'tau_genpt>0&&tau_pt>0&&tau_dm==0'},
        'pt_resolution_1prongp0': {'var': '(tau_genpt-tau_pt)/(tau_genpt)', 'nbin': 30, 'min': -1., 'max': 1., 'title': 'pT resolution, 1prong+#pi^{0}', 'sel': 'tau_genpt>0&&tau_pt>0&&tau_dm==1'},
        'pt_resolution_2prong': {'var': '(tau_genpt-tau_pt)/(tau_genpt)', 'nbin': 30, 'min': -1., 'max': 1., 'title': 'pT resolution, 2prong', 'sel': 'tau_genpt>0&&tau_pt>0&&(tau_dm==5 || tau_dm==6)'},
        'pt_resolution_3prong': {'var': '(tau_genpt-tau_pt)/(tau_genpt)', 'nbin': 30, 'min': -1., 'max': 1., 'title': 'pT resolution, 3prong (+#pi^{0})', 'sel': 'tau_genpt>0&&tau_pt>0&&(tau_dm==10 || tau_dm==11)'},
        'pt_resolution_3prong_old': {'var': '(tau_genpt-tau_pt)/(tau_genpt)', 'nbin': 30, 'min': -1., 'max': 1., 'title': 'pT resolution, 3prong (0#pi^{0})', 'sel': 'tau_genpt>0&&tau_pt>0&&tau_dm==10'},
    }

    for hname, hdict in sorted(hvardict.iteritems()):

        hists = []

        if runtype != 'ZTT' and runtype != 'TTbarTau' and hname.find('pt_resolution') != -1:
            continue

        for rel, rdict in sorted(sampledict.iteritems()):

            tfile = TFile(rdict['file'])
            tree = tfile.Get('per_tau')

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

            hists.append(copy.deepcopy(hist))

        hoverlay(hists, hdict['title'], 'a.u.', hname)
