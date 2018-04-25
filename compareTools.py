import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
from ROOT import gROOT, gStyle, TH1F, TFile, TCanvas, TPad, TLegend, TGraphAsymmErrors, Double, TLatex


def makeEffPlotsVars(tree, varx, numeratorAddSelection, baseSelection, xtitle='', header='', addon='', option='pt', marker=20, col=1, ptPlotsBinning = None, plotSeparateEff=False):

    if ptPlotsBinning:
        _denomHist_  = TH1F( 'h_effp_' + addon,  'h_effp' + addon, len(ptPlotsBinning) - 1, ptPlotsBinning)
        _nominatorHist_ = TH1F('ah_effp_' + addon, 'ah_effp' + addon, len(ptPlotsBinning) - 1, ptPlotsBinning)
    else: raise ValueError("Wrong binning passed to makeEffPlotsVars with option == %s"%('eta'))

    tree.Draw(varx + ' >> ' +  _denomHist_.GetName(), baseSelection)
    tree.Draw(varx + ' >> ' + _nominatorHist_.GetName(), baseSelection + ' && ' + numeratorAddSelection)

    g_efficiency = TGraphAsymmErrors()
    g_efficiency.Divide(_nominatorHist_, _denomHist_, "cl=0.683 b(1,1) mode")
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

    if plotSeparateEff:
        canvas = TCanvas()
        leg = TLegend(0.2, 0.7, 0.5, 0.9)
        configureLegend(leg, 1)
        legname = g_efficiency.GetName()
        hist.GetPoint(0, x, y)
        leg.AddEntry(hist, legname, 'lep')
        leg.Draw()
        g_efficiency.Draw()
        save(canvas, "plots/makeEffPlotsVars/" + addon)

    return g_efficiency