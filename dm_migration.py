import argparse

from ROOT import gStyle, TCanvas, TH2F, TFile

from officialStyle import officialStyle
officialStyle(gStyle)
gStyle.SetTitleOffset(1.65, "Y")
gStyle.SetPadLeftMargin(0.20)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-i', '--inputFile', default='Myroot_CMSSW_9_4_0_pre2_PU25ns_94X_mc2017_realistic_v1-v1_ZTT.root', help='Input file name')
    parser.add_argument('-l', '--label', default='standard', help='Label for plot output')
    parser.add_argument('-t', '--treeName', default='per_tau', help='Name of TTree in file')
    args = parser.parse_args()

    f_name = args.inputFile
    title = args.label
    tree_prod_name = args.treeName

    canvas = TCanvas('decay_mode_matrix')

    f_in = TFile(f_name)
    tree = f_in.Get(tree_prod_name)

    tau_dm_string = '(tau_pt>20)*((tau_dm==0 || tau_dm==1 || tau_dm==2 || tau_dm==10 || tau_dm==11)*(tau_dm - 8*(tau_dm==10) - 8*(tau_dm==11) - 1*(tau_dm==2)) - 1 *(!(tau_dm==0 || tau_dm==1 || tau_dm==2|| tau_dm==10|| tau_dm==11) && tau_dm>0 && tau_dm<200) - 2 *(!(tau_dm==0 || tau_dm==1 || tau_dm==2 || tau_dm==10 || tau_dm==11) && (tau_dm<0 || tau_dm>=200))) - 2*(tau_pt<20)'
    cut = 'tau_genpt>20 && abs(tau_geneta)<2.3'

    h_migration = TH2F('migration{}'.format(title), '', 5, -1., 4., 6, -2, 4.)
    tree.Project(h_migration.GetName(), tau_dm_string+':'+tau_dm_string.replace('tau_', 'tau_gen'), cut)

    label = ['None', 'Other', '#pi', '#pi#pi^{0}s', '#pi#pi#pi', '#pi#pi#pi#pi^{0}s']
    for ybin in range(1, h_migration.GetYaxis().GetNbins()+1):
        h_migration.GetYaxis().SetBinLabel(ybin, label[ybin-1])
    for xbin in range(1, h_migration.GetXaxis().GetNbins()+1):
        h_migration.GetXaxis().SetBinLabel(xbin, label[xbin])

    h_migration.GetYaxis().SetTitle('Offline DM')
    h_migration.GetXaxis().SetTitle('Gen DM')

    for xbin in xrange(1, h_migration.GetNbinsX()+1):
        int_y = sum(h_migration.GetBinContent(xbin, ybin) for ybin in xrange(1, h_migration.GetNbinsY()+1))
        if int_y == 0.:
            int_y = 1.
        for ybin in xrange(1, h_migration.GetNbinsY()+1):
            # cont = round(h_migration.GetBinContent(xbin, ybin)/int_y, 2)
            h_migration.SetBinContent(xbin, ybin, h_migration.GetBinContent(xbin, ybin)/int_y)

    h_migration.Draw('TEXT')
    h_migration.SetMarkerColor(1)
    h_migration.SetMarkerSize(2.2)
    gStyle.SetPaintTextFormat("1.2f")

    canvas.Print('dm_migration_{}.pdf'.format(title))
