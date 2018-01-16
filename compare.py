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
    ensureDir(name[0:name.find("/")])
    ensureDir(name[0:name.rfind("/")])
    #ensureDir('compare_' + runtype)

    #canvas.SaveAs(name.replace(' ', '').replace('&&', '')+'.pdf')
    #canvas.SaveAs(name.replace(' ', '').replace('&&', '')+'.gif')
    canvas.SaveAs(name.replace(' ', '').replace('&&', '')+'.png')


def configureLegend(leg, ncolumn):
    leg.SetNColumns(ncolumn)
    leg.SetBorderSize(0)
    leg.SetFillColor(10)
    leg.SetLineColor(0)
    leg.SetFillStyle(0)
    leg.SetTextSize(0.02)
    leg.SetTextFont(42)


def overlay(hists, ytitle, header, addon):
    #print 'number of histograms = ', len(hists)

    canvas = TCanvas()
    leg = TLegend(0.2, 0.7, 0.5, 0.9)
    configureLegend(leg, 1)

    ymax = -1
    ymin = 100

    for ii, hist in enumerate(hists):
        hist.GetYaxis().SetTitle('efficiency')
        hist.SetLineWidth(2)
        hist.SetMarkerSize(1)

        for ip in xrange(0,hist.GetN()):
            x = Double(-1)
            y = Double(-1)
            hist.GetPoint(ip, x, y)

            if ymin > y:
                ymin = y
            if ymax < y:
                ymax = y

    for ii, hist in enumerate(hists):
        hist.SetMaximum(ymax*1.4)
        hist.SetMinimum(ymin*0.80)
	#hist.GetXaxis().SetLimits(hist.GetXaxis().GetXmin()+(3*(ii-3)), hist.GetXaxis().GetXmax()+(3*(ii-3)))

    #for ii, hist in enumerate(hists):
        if ii == 0:
            hist.Draw("Ap")
        else:
            hist.Draw("psame")

        legname = hist.GetName()
	hist.GetPoint(0, x, y)

        leg.AddEntry(hist, legname, 'lep')



    leg.Draw()

    tex = TLatex(hists[-1].GetXaxis().GetXmin() + 0.01*(hists[-1].GetXaxis().GetXmax() -
                                                        hists[-1].GetXaxis().GetXmin()), ymax*1.4, addon.replace('tau_', ''))

    tex.SetTextAlign(10)
    tex.SetTextFont(42)
    tex.SetTextSize(0.03)
    tex.Draw()

    xshift = 0.87
    # xshift=0.7
    if tlabel.find('QCD') != -1:
        xshift = 0.6
    if runtype.find('TTbarTau') != -1:
        xshift = 0.78
    tex2 = TLatex(hists[-1].GetXaxis().GetXmin() + xshift*(hists[-1].GetXaxis(
    ).GetXmax() - hists[-1].GetXaxis().GetXmin()), ymax*1.4, tlabel)

    tex2.SetTextAlign(10)
    tex2.SetTextFont(42)
    tex2.SetTextSize(0.03)
    tex2.Draw()

    directory1 = ""
    directory1options = ["byLooseCombinedIsolationDeltaBetaCorr3Hits", "byMediumCombinedIsolationDeltaBetaCorr3Hits", "byTightCombinedIsolationDeltaBetaCorr3Hits", "byPtOutOfCone", "byLooseChargedIsolation", "byMediumChargedIsolation", "byTightChargedIsolation", "byLooseNeutralIsolation", "byMediumNeutralIsolation", "byTightNeutralIsolation", "byLooseNeutralIsolationUnCorr", "byMediumNeutralIsolationUnCorr", "byTightNeutralIsolationUnCorr", "byLooseIsolationMVArun2v1DBoldDMwLT", "byMediumIsolationMVArun2v1DBoldDMwLT", "byTightIsolationMVArun2v1DBoldDMwLT", "againstElectron", "againstMuon", "DecayModeFinding"]
    directory2 = ""
    directory2options = {"_1p":"1prong", "_2p":"2prong", "_3p":"3prong", "_modOldDM":"oldDM", "_newDM":"newDM"}
    directory22options = {"_1ppi0":"1prongpizero", "_3pold":"3prong_old"}


    for alpha in directory1options:
	if alpha in header: directory1 = alpha
    for alpha,beta in directory2options.items():
	if alpha in header: directory2 = beta
    for alpha,beta in directory22options.items():
	if alpha in header: directory2 = beta

    if "_eta" in header:
	if directory1 != "": directory1 += "_eta"
	if directory2 != "": directory2 += "_eta"

    if directory1 != "": save(canvas, 'compare_' + runtype + '/' + directory1 + '/' + header)
    if directory2 != "": save(canvas, 'compare_' + runtype + '/' + directory2 + '/' + header)
    if directory1 == "" and directory2 == "":  save(canvas, 'compare_' + runtype + '/' + header)
    if "_eta" in header:
        save(canvas, 'compare_' + runtype + '/all_eta/' + header)
    else:
        save(canvas, 'compare_' + runtype + '/all/' + header)


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

    leg = TLegend(0.2, 0.65, 0.91, 0.9)
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
    if runtype.find('TTbarTau') != -1:
        xshift = 0.78
    tex2 = TLatex(hists[0].GetXaxis().GetXmin(
    ) + xshift*(hists[0].GetXaxis().GetXmax() - hists[0].GetXaxis().GetXmin()), ymax*1.2, tlabel)

    tex2.SetTextAlign(10)
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

    save(c, 'compare_' + runtype + '/histograms/hist_' + name)


def makeEffPlotsVars(tree, varx, vary, sel, nbinx, xmin, xmax, nbiny, ymin, ymax, xtitle, ytitle, leglabel=None, header='', addon='', option='pt', marker=20, col=1):

    binning = [20, 200] if args.onebin else [20, 30, 40, 50, 60, 70, 80, 100, 150, 200]

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
    g_efficiency.Divide(_ahist_, _hist_, "cl=0.683 b(1,1) mode")
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
    parser.add_argument('-r', '--releases', help='comma separated list of releases', default='CMSSW_9_4_0_pre1,CMSSW_9_4_0_pre2')
    parser.add_argument('-g', '--globaltag', help='comma separated global tags of releases', default='93X_mc2017_realistic_v3-v1,94X_mc2017_realistic_v1-v1')
    parser.add_argument('-p', '--part',  help='Make WP plots(1), first half of histogram plots(2), second half of histogram plots(3), or everything at once(0) (This part needs to be split up to avoid a crash that happens for some reason)', default=0)
    parser.add_argument('-b', '--onebin', action="store_true",  help='Plot inclusive efficiencies by only using one bin', default=False)
    
    args = parser.parse_args()
    
    part = int(args.part)
    runtype = args.runtype
    print 'Producing plots for runtype', runtype
    
    releases = args.releases.split(',')
    globaltags = args.globaltag.split(',')
    
    print 'Releases', releases
    print 'Global tags', globaltags
    

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
        {'col': 41, 'marker': 20, 'width': 2},
        {'col': 1, 'marker': 26, 'width': 2},
        {'col': 6, 'marker': 22, 'width': 2},
    ]
    
    sampledict = {}
    for i_sample, release in enumerate(globaltags):
        sampledict[release] = styles[i_sample]
        tfile = sampledict[release]['file'] = TFile('Myroot_{}_{}_{}.root'.format(releases[i_sample], release, runtype))
        sampledict[release]['tree'] = tfile.Get('per_tau')

    if part<2:
        for hname, hdict in vardict.items():

            hists = []
            histseta = []

            for rel, rdict in sampledict.items():
                tree = rdict['tree']

                num_sel = reco_cut
                den_sel = '1'

                if hname.find('against') != -1:
                    #num_sel = '1'
                    num_sel = reco_cut
                    den_sel = reco_cut + ' && ' + loose_id

                hists.append(makeEffPlotsVars(tree, 'tau_genpt', num_sel + '&&' + hdict['var'], den_sel + '&& abs(tau_eta) < 2.3', 30, 0, 300, hdict['nbin'], hdict['min'], hdict['max'], xlabel, hdict['title'], '', rel, rel, 'pt', rdict['marker'], rdict['col']))
                histseta.append(makeEffPlotsVars(tree, 'tau_geneta', num_sel + '&&' + hdict['var'], den_sel + '&& tau_pt>20', 12, -2.4, 2.4, hdict['nbin'], hdict['min'], hdict['max'], xlabel_eta, hdict['title'], '', rel, rel, 'eta', rdict['marker'], rdict['col']))



            overlay(hists, hname, hname, hdict['title'])
            overlay(histseta, hname, hname+'_eta', hdict['title']+'_eta')

    if part==1: exit()
    i = 0
    for hname, hdict in hvardict.items():
	i+=1
        if part==2 and i>len(hvardict.items())/2:
            exit()
        elif part==3 and i<=len(hvardict.items())/2:
            continue

        hists = []

        if runtype != 'ZTT' and runtype != 'TTbarTau' and hname.find('pt_resolution') != -1:
            continue

        for rel, rdict in sampledict.items():
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
