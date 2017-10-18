''' Produces plots for tau release/data validation using the trees produced by
produceTauValTree.py
Authors: Yuta Takahashi, Michal Bluj, Jan Steggemann.
'''
from officialStyle import officialStyle
from array import array
from ROOT import gROOT, gStyle, TH1F, TFile, TCanvas, TPad, TLegend, TGraphAsymmErrors, Double, TLatex
import os
import copy
import sys
from variables import vardict

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
    argvs = sys.argv
    argc = len(argvs)

    if argc != 2:
        print 'Please specify the runtype : python compare.py <ZTT, ZEE, ZMM, QCD>'
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

    reco_cut = 'tau_pt > 20 && abs(tau_eta) < 2.3'
    #loose_id = 'tau_decayModeFindingOldDMs > 0.5 && tau_byLooseCombinedIsolationDeltaBetaCorr3Hits > 0.5'
    loose_id = 'tau_decayModeFindingOldDMs > 0.5 && tau_byLooseIsolationMVArun2v1DBoldDMwLT > 0.5'

    styles = [
        {'col': 8, 'marker': 25, 'width': 2},
        {'col': 2, 'marker': 21, 'width': 2},
        {'col': 4, 'marker': 21, 'width': 2},
        {'col': 7, 'marker': 24, 'width': 2},
    ]
    releases = ['CMSSW_9_4_0_pre1', 'CMSSW_9_4_0_pre1']
    
    sampledict = {}
    for i_sample, release in enumerate(releases):
        sampledict[release] = styles[i_sample]
        sampledict[release]['file'] = 'Myroot_{}_{}.root'.format(release, runtype)

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
