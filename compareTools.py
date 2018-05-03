import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
from ROOT import gROOT, gStyle, TH1F, TFile, TCanvas, TPad, TLegend, TGraphAsymmErrors, Double, TLatex

import os

import pprint
pp = pprint.PrettyPrinter(indent=4)


def ensureDir(file_path):
    if '/' not in file_path: return
    import errno
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(directory):
                pass
            else:
                print "Bad name for directory:", file_path
                raise

def save(canvas, name, extension='.png'):
    name = name.replace(' ', '').replace('&&', '')
    ensureDir(name)
    canvas.SaveAs(name + extension)

def configureLegend(leg, ncolumn):
    leg.SetNColumns(ncolumn)
    leg.SetBorderSize(0)
    leg.SetFillColor(10)
    leg.SetLineColor(0)
    leg.SetFillStyle(0)
    leg.SetTextSize(0.02)
    leg.SetTextFont(42)

def overlay(hists, ytitle, header, addon, runtype, tlabel, xlabel, comparePerReleaseSuffix="", dryrun=False, debug=False):
    if debug: print "\n\n\toverlay::len(hists)", len(hists)
    _eta = "_eta" * ("_eta" in header)
    directory1 = None
    directory2 = None
    directory1options = ["byLooseCombinedIsolationDeltaBetaCorr3Hits",
        "byMediumCombinedIsolationDeltaBetaCorr3Hits",
        "byTightCombinedIsolationDeltaBetaCorr3Hits",
        "byPtOutOfCone",
        "byLooseChargedIsolation",
        "byMediumChargedIsolation",
        "byTightChargedIsolation",
        "byLooseNeutralIsolation",
        "byMediumNeutralIsolation",
        "byTightNeutralIsolation",
        "byLooseNeutralIsolationUnCorr",
        "byMediumNeutralIsolationUnCorr",
        "byTightNeutralIsolationUnCorr",
        "byLooseIsolationMVArun2v1DBoldDMwLT",
        "byMediumIsolationMVArun2v1DBoldDMwLT",
        "byTightIsolationMVArun2v1DBoldDMwLT",
        "againstElectron",
        "againstMuon",
        "DecayModeFinding",
        'byLooseIsolationMVArun2017v2DBoldDMwLT2017',
        'byMediumIsolationMVArun2017v2DBoldDMwLT2017',
        'byTightIsolationMVArun2017v2DBoldDMwLT2017']

    directory2options  = {"_1p": "1prong", "_2p": "2prong", "_3p": "3prong", "_modOldDM": "oldDM", "_newDM": "newDM"}
    directory22options = {"_1ppi0": "1prongpizero", "_3pold": "3prong_old"}

    ymax = -1
    ymin = 100
    for hist in hists:
        for ip in xrange(hist.GetN()):
            x = Double(-1)
            y = Double(-1)
            hist.GetPoint(ip, x, y)
            if ymin > y: ymin = y
            if ymax < y: ymax = y

    canvas = TCanvas()
    leg = TLegend(0.2, 0.7, 0.5, 0.9)
    configureLegend(leg, 1)

    for ii, hist in enumerate(hists):

        hist.GetYaxis().SetTitle('efficiency')
        hist.SetLineWidth(2)
        hist.SetMarkerSize(1)
        hist.SetMaximum(ymax * 1.4)
        hist.SetMinimum(ymin * 0.80)
        #hist.GetXaxis().SetLimits(hist.GetXaxis().GetXmin()+(3*(ii-3)), hist.GetXaxis().GetXmax()+(3*(ii-3)))
        if ii == 0:
            hist.Draw("Ap")
            if debug:
                print "\t\tAp", ii, hist.GetName(), hist.GetMarkerColor()
                c1 = TCanvas()
                hist.Draw("Ap")
                save(c1, 'debug/compare_AP' + _eta + header)
                canvas.cd()
        else:
            hist.Draw("psame")
            if debug:
                print "\t\tpsame", ii, hist.GetName(), hist.GetMarkerColor()
                c1 = TCanvas()
                hist.Draw("p")
                save(c1, 'debug/compare_psame' + _eta + header)
                canvas.cd()

        legname = hist.GetName()
        hist.GetPoint(0, x, y)
        leg.AddEntry(hist, legname, 'lep')

    leg.Draw()
    # if header == "byLooseIsolationMVArun2017v2DBoldDMwLT2017": exit()

    tex = TLatex(hists[-1].GetXaxis().GetXmin() + 0.01*(hists[-1].GetXaxis().GetXmax() - hists[-1].GetXaxis().GetXmin()), ymax*1.4, addon.replace('tau_', ''))
    tex.SetTextAlign(10)
    tex.SetTextFont(42)
    tex.SetTextSize(0.03)
    tex.Draw()

    xshift = 0.87
    if tlabel.find('QCD') != -1:       xshift = 0.6
    if runtype.find('TTbarTau') != -1: xshift = 0.78
    tex2 = TLatex(hists[-1].GetXaxis().GetXmin() + xshift*(hists[-1].GetXaxis().GetXmax() - hists[-1].GetXaxis().GetXmin()), ymax*1.4, tlabel)
    tex2.SetTextAlign(10)
    tex2.SetTextFont(42)
    tex2.SetTextSize(0.03)
    tex2.Draw()

    if dryrun: return

    for key in directory1options:
        if key in header:
            directory1 = key + _eta
            save(canvas, 'compare_' + runtype + comparePerReleaseSuffix + '/' + directory1 + '/' + header)

    for key, value in directory2options.items() + directory22options.items():
        if key in header:
            directory2 = value + _eta
            save(canvas, 'compare_' + runtype + comparePerReleaseSuffix + '/' + directory2 + '/' + header)

    if not (directory1 or directory2): save(canvas, 'compare_' + runtype + '/' + header)

    save(canvas, 'compare_' + runtype + comparePerReleaseSuffix + '/all' + _eta + '/' + header)
    if header=="byLooseIsolationMVArun2017v2DBoldDMwLT2017": exit()

def hoverlay(hists, xtitle, ytitle, name, runtype, tlabel, xlabel, xlabel_eta, comparePerReleaseSuffix="", dryrun=False, debug=False):
    c = TCanvas()

    # Upper plot will be in pad1
    pad1 = TPad("pad1", "pad1", 0, 0.3, 1, 1.0)
    pad1.SetBottomMargin(0)  # Upper and lower plot are joined
    pad1.Draw()             # Draw the upper pad: pad1
    pad1.cd()              # pad1 becomes the current pad
    pad1.SetLogy(0)
    if hname.find('isoPt') > -1 or hname.find('outOfConePt') > -1 or hname.find('IsoRaw') > -1: pad1.SetLogy()

    ymax = max([hist.GetMaximum() for hist in hists])
    leg = TLegend(0.2, 0.65, 0.91, 0.9)
    configureLegend(leg, 1)

    hratios = []
    for ii, ihist in enumerate(hists):
        ihist.SetMaximum(ymax * 1.2)
        ihist.SetMinimum(0.)
        # if c.GetLogy > 0:
        if pad1.GetLogy > 0: ihist.SetMinimum(0.001)
        ihist.SetMarkerSize(0.)
        ihist.GetXaxis().SetTitle(xtitle)
        ihist.GetYaxis().SetTitle(ytitle)

        if ii == 0: ihist.Draw('h')
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
    if runtype.find('TTbarTau') != -1:
        xshift = 0.78
    tex2 = TLatex(hists[0].GetXaxis().GetXmin(
    ) + xshift*(hists[0].GetXaxis().GetXmax() - hists[0].GetXaxis().GetXmin()), ymax*1.2, tlabel)

    tex2.SetTextAlign(10)
    tex2.SetTextFont(42)
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
    if dryrun: return
    save(c, 'compare_' + runtype + comparePerReleaseSuffix + '/histograms/hist_' + name)

def findLooseId(hname, debug=False):
    if debug: print "findLooseId::"

    looseIdDict = {
        'tau_byLooseIsolationMVArun2v1DBoldDMwLT':  ['byLooseIsolationMVArun2v1DBoldDMwLT', 'byMediumIsolationMVArun2v1DBoldDMwLT', 'byTightIsolationMVArun2v1DBoldDMwLT'],
        'tau_byLooseIsolationMVArun2v1PWoldDMwLT': ['byLooseIsolationMVArun2v1PWoldDMwLT', 'byMediumIsolationMVArun2v1PWoldDMwLT', 'byTightIsolationMVArun2v1PWoldDMwLT'],

        'tau_byLooseIsolationMVArun2017v1DBoldDMwLT2017': ['byLooseIsolationMVArun2017v1DBoldDMwLT2017', 'byMediumIsolationMVArun2017v1DBoldDMwLT2017', 'byTightIsolationMVArun2017v1DBoldDMwLT2017'],
        'tau_byLooseIsolationMVArun2017v2DBoldDMwLT2017': ['byLooseIsolationMVArun2017v2DBoldDMwLT2017', 'byMediumIsolationMVArun2017v2DBoldDMwLT2017', 'byTightIsolationMVArun2017v2DBoldDMwLT2017'],
        'tau_byLooseIsolationMVArun2v1DBoldDMwLT2016': ['byLooseIsolationMVArun2v1DBoldDMwLT2016', 'byMediumIsolationMVArun2v1DBoldDMwLT2016', 'byTightIsolationMVArun2v1DBoldDMwLT2016'],
        'tau_byLooseIsolationMVArun2v1DBnewDMwLT2016': ['byLooseIsolationMVArun2v1DBnewDMwLT2016', 'byMediumIsolationMVArun2v1DBnewDMwLT2016', 'byTightIsolationMVArun2v1DBnewDMwLT2016'],
        'tau_byLooseIsolationMVArun2017v2DBoldDMdR0p3wLT2017': ['byLooseIsolationMVArun2017v2DBoldDMdR0p3wLT2017', 'byMediumIsolationMVArun2017v2DBoldDMdR0p3wLT2017', 'byTightIsolationMVArun2017v2DBoldDMdR0p3wLT2017']
    }
    for key, value in looseIdDict.items():
        if hname in value:
            if debug: print hname, 'in', value
            return key

    return 'tau_byLooseIsolationMVArun2v1DBoldDMwLT'

def shiftAlongX(tGraph, numberOfGraphs, index, debug=False):
    if debug: print "\tshiftAlongX::"

    for binNumber in xrange(tGraph.GetN()):
        x = Double(-1)
        y = Double(-1)
        tGraph.GetPoint(binNumber, x, y)
        shift = (tGraph.GetErrorXhigh(binNumber)) / (numberOfGraphs + 1)
        if debug:
            print "\t\tBin", binNumber, 'shift =', "(", tGraph.GetErrorXhigh(binNumber), ") / (", numberOfGraphs, "+", 1, ") =", shift, "; x =", x, "=>", x + shift * index
        x = x + shift * index
        tGraph.SetPoint(binNumber, x, y)

def makeEffPlotsVars(tree, varx, numeratorAddSelection, baseSelection, xtitle='', header='', addon='', option='pt', marker=20, col=1, ptPlotsBinning = None, plotSeparateEff=False, debug=False):
    if debug: print "\tmakeEffPlotsVars::", "header:", header, ";", "varx:", varx, ">>",

    if ptPlotsBinning:
        _denomHist_  = TH1F( 'h_effp_' + addon,  'h_effp' + addon, len(ptPlotsBinning) - 1, ptPlotsBinning)
        _nominatorHist_ = TH1F('ah_effp_' + addon, 'ah_effp' + addon, len(ptPlotsBinning) - 1, ptPlotsBinning)
    else:
        raise ValueError("Wrong binning passed to makeEffPlotsVars with option == %s"%('eta'))

    if debug:
        print "\t\t", _denomHist_.GetName(), "; >>", _nominatorHist_.GetName()
        print "\t\t", "varx:", varx
        print "\t\t", "_denomHist_.GetName():", _denomHist_.GetName()
        print "\t\t", "denom selection:", baseSelection
        print "\t\t", "nom selection:", baseSelection + ' && ' + numeratorAddSelection

    tree.Draw(varx + ' >> ' + _denomHist_.GetName(),     baseSelection)
    tree.Draw(varx + ' >> ' + _nominatorHist_.GetName(), baseSelection + ' && ' + numeratorAddSelection)

    g_efficiency = TGraphAsymmErrors()
    g_efficiency.Divide(_nominatorHist_, _denomHist_, "cl=0.683 b(1,1) mode")
    g_efficiency.GetXaxis().SetTitle(xtitle)
    g_efficiency.GetYaxis().SetTitle('efficiency')
    g_efficiency.GetYaxis().SetNdivisions(507)
    g_efficiency.SetLineWidth(3)
    if "loose_id_17v2" not in header and "loose_id" in header: g_efficiency.SetLineWidth(5)
    g_efficiency.SetName(header)
    g_efficiency.SetMinimum(0.)
    g_efficiency.GetYaxis().SetTitleOffset(1.3)
    g_efficiency.SetMarkerStyle(marker)
    g_efficiency.SetMarkerSize(1)
    if "loose_id_17v2" not in header and "loose_id" in header: g_efficiency.SetMarkerSize(3)
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


def fillSampledic(globaltags, releases, runtype, inputfiles='', debug=False):
    if debug: print "Collecting samples"

    sampledict = {}
    styles = [
        {'col': 8, 'marker': 25, 'width': 2},
        {'col': 2, 'marker': 21, 'width': 2},
        {'col': 4, 'marker': 21, 'width': 2},
        {'col': 7, 'marker': 24, 'width': 2},
        {'col': 41, 'marker': 20, 'width': 2},
        {'col': 1, 'marker': 26, 'width': 2},
        {'col': 6, 'marker': 22, 'width': 2},
    ]

    for index, globalTag in enumerate(globaltags):
        sampledict[globalTag] = styles[index]

        if len(inputfiles) == 0:
            sampledict[globalTag]['file'] = TFile('Myroot_{}_{}_{}.root'.format(releases[index], globalTag, runtype))
        else:
            sampledict[globalTag]['file'] = TFile(inputfiles[index])

        sampledict[globalTag]['tree'] = sampledict[globalTag]['file'].Get('per_tau')

    if debug:
        print "sampledict:"
        pp.pprint(sampledict)

    return sampledict
