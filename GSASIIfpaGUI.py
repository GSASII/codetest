# -*- coding: utf-8 -*-
########### SVN repository information ###################
# $Date: $
# $Author: $
# $Revision: $
# $URL: $
# $Id: $
########### SVN repository information ###################
'''
*GSASIIfpaGUI: Fundamental Parameters Routines*
===============================================

This module contains routines for getting Fundamental Parameters 
Approach (FPA) input, setting up for running the NIST XRD Fundamental 
Parameters Code, plotting the convolutors and computing a set of peaks
generated by that code. 

'''
from __future__ import division, print_function
import wx
import os.path
import numpy as np

import NIST_profile as FP

import GSASIIpath
import GSASIIctrlGUI as G2G
import GSASIIdataGUI as G2gd
import GSASIIplot as G2plt
import GSASIImath as G2mth
import GSASIIpwd as G2pwd

simParms = {}
'''Parameters to set range for pattern simulation
'''

parmDict = {'numWave':2}
'''Parameter dict used for reading Topas-style values. These are 
converted to SI units and placed into :data:`NISTparms`
'''

NISTparms = {}
'''Parameters in a nested dict, with an entry for each concolutor. Entries in 
those dicts have values in SI units (of course). NISTparms can be 
can be input directly or can be from created from :data:`parmDict`
by :func:`XferFPAsettings`
'''

BraggBrentanoParms = [
    ('divergence', 0.5, 'Bragg-Brentano divergence angle (degrees)'),
    ('soller_angle', 2.0, 'Soller slit axial divergence (degrees)'),
    ('Rs', 220, 'Diffractometer radius (mm)'),
    ('filament_length', 12., 'X-ray tube line focus length (mm)'),
    ('sample_length', 12., 'Illuminated sample length in axial direction (mm)'),
    ('receiving_slit_length', 12., 'Length of receiving slit in axial direction (mm)'),
    ('LAC_cm', 0.,'Linear absorption coef. adjusted for packing density (cm-1)'),
    ('sample_thickness', 1., 'Depth of sample (mm)'),
    ('convolution_steps', 8, 'Number of Fourier-space bins per two-theta step'),
    ]
'''FPA dict entries used in :func:`MakeTopasFPASizer`. Tuple contains
a dict key, a default value and a description. These are the parameters
needed for all Bragg Brentano instruments
'''

BBPointDetector = [
    ('receiving_slit_width', 0.2, 'Width of receiving slit (mm)'),]
'''Additional FPA dict entries used in :func:`MakeTopasFPASizer` 
needed for Bragg Brentano instruments with point detectors.
'''

BBPSDDetector = [
    ('lpsd_th2_angular_range', 3.0, 'Angular range observed by PSD (degrees 2Theta)'),
    ('lpsd_equitorial_divergence', 0.1, 'Equatorial divergence of the primary beam (degrees)'),]
'''Additional FPA dict entries used in :func:`MakeTopasFPASizer` 
needed for Bragg Brentano instruments with linear (1-D) PSD detectors.
'''

Citation = '''MH Mendenhall, K Mullen && JP Cline. (2015) J. Res. of NIST 120, 223-251. doi:10.6028/jres.120.014.
'''
    
def SetCu2Wave():
    '''Set the parameters to the two-line Cu K alpha 1+2 spectrum
    '''
    parmDict['wave'] = {i:v for i,v in enumerate((1.540596,1.544493))}
    parmDict['int'] = {i:v for i,v in enumerate((0.653817, 0.346183))}
    parmDict['lwidth'] = {i:v for i,v in enumerate((0.501844,0.626579))}
SetCu2Wave() # use these as default

def MakeTopasFPASizer(G2frame,FPdlg,mode,SetButtonStatus):
    '''Create a GUI with parameters for the NIST XRD Fundamental Parameters Code. 
    Parameter input is modeled after Topas input parameters.

    :param wx.Window FPdlg: Frame or Dialog where GUI will appear
    :param str mode: either 'BBpoint' or 'BBPSD' for Bragg-Brentano point detector or 
      (linear) position sensitive detector
    :param dict parmDict: dict to place parameters. If empty, default values from 
      globals BraggBrentanoParms, BBPointDetector & BBPSDDetector will be placed in 
      the array. 
    :returns: a sizer with the GUI controls
 
    '''
    def _onOK(event):
        XferFPAsettings(parmDict)
        SetButtonStatus(done=True) # done=True triggers the simulation
        FPdlg.Destroy()
    def _onClose(event):
        SetButtonStatus()
        FPdlg.Destroy()
    def _onAddWave(event):
        parmDict['numWave'] += 1 
        wx.CallAfter(MakeTopasFPASizer,G2frame,FPdlg,mode,SetButtonStatus)
    def _onRemWave(event):
        parmDict['numWave'] -= 1 
        wx.CallAfter(MakeTopasFPASizer,G2frame,FPdlg,mode,SetButtonStatus)
    def _onSetCu5Wave(event):
        parmDict['wave'] = {i:v for i,v in enumerate((1.534753,1.540596,1.541058,1.54441,1.544721))}
        parmDict['int'] = {i:v for i,v in enumerate((0.0159, 0.5791, 0.0762, 0.2417, 0.0871))}
        parmDict['lwidth'] = {i:v for i,v in enumerate((3.6854, 0.437, 0.6, 0.52, 0.62))}
        parmDict['numWave'] = 5
        wx.CallAfter(MakeTopasFPASizer,G2frame,FPdlg,mode,SetButtonStatus)
    def _onSetCu2Wave(event):
        SetCu2Wave()
        parmDict['numWave'] = 2
        wx.CallAfter(MakeTopasFPASizer,G2frame,FPdlg,mode,SetButtonStatus)
    def _onSetPoint(event):
        wx.CallAfter(MakeTopasFPASizer,G2frame,FPdlg,'BBpoint',SetButtonStatus)
    def _onSetPSD(event):
        wx.CallAfter(MakeTopasFPASizer,G2frame,FPdlg,'BBPSD',SetButtonStatus)
    def PlotTopasFPA(event):
        XferFPAsettings(parmDict)
        ttArr = np.arange(max(0.5,
                            simParms['plotpos']-simParms['calcwid']),
                            simParms['plotpos']+simParms['calcwid'],
                            simParms['step'])
        intArr = np.zeros_like(ttArr)
        NISTpk = setupFPAcalc()
        try:
            center_bin_idx,peakObj = doFPAcalc(
                NISTpk,ttArr,simParms['plotpos'],simParms['calcwid'],
                simParms['step'])
        except Exception as err:
            msg = "Error computing convolution, revise input"
            print(msg)
            print(err)
            return
        G2plt.PlotFPAconvolutors(G2frame,NISTpk)
        pkPts = len(peakObj.peak)
        pkMax = peakObj.peak.max()
        startInd = center_bin_idx-(pkPts//2) #this should be the aligned start of the new data
        # scale peak so max I=10,000 and add into intensity array
        if startInd < 0:
            intArr[:startInd+pkPts] += 10000 * peakObj.peak[-startInd:]/pkMax
        elif startInd > len(intArr):
            return
        elif startInd+pkPts >= len(intArr):
            offset = pkPts - len( intArr[startInd:] )
            intArr[startInd:startInd+pkPts-offset] += 10000 * peakObj.peak[:-offset]/pkMax
        else:
            intArr[startInd:startInd+pkPts] += 10000 * peakObj.peak/pkMax
        G2plt.PlotXY(G2frame, [(ttArr, intArr)],
                     labelX=r'$2\theta, deg$',
                     labelY=r'Intensity (arbitrary)',
                     Title='FPA peak', newPlot=True, lines=True)

    if FPdlg.GetSizer(): FPdlg.GetSizer().Clear(True)
    numWave = parmDict['numWave']
    if mode == 'BBpoint':
        itemList = BraggBrentanoParms+BBPointDetector
    elif mode == 'BBPSD':
        itemList = BraggBrentanoParms+BBPSDDetector
    else:
        raise Exception('Unknown mode in MakeTopasFPASizer: '+mode)
    
    MainSizer = wx.BoxSizer(wx.VERTICAL)
    MainSizer.Add((-1,5))
    waveSizer = wx.FlexGridSizer(cols=numWave+1,hgap=3,vgap=5)
    for lbl,prm,defVal in zip(
            (u'Wavelength (\u212b)','Rel. Intensity',u'Lorentz Width\n(\u212b/1000)'),
            ('wave','int','lwidth'),
            (0.0,   1.0,   0.1),
            ):
        text = wx.StaticText(FPdlg,wx.ID_ANY,lbl,style=wx.ALIGN_CENTER)
        text.SetBackgroundColour(wx.WHITE)
        waveSizer.Add(text,0,wx.EXPAND)
        if prm not in parmDict: parmDict[prm] = {}
        for i in range(numWave):
            if i not in parmDict[prm]: parmDict[prm][i] = defVal
            ctrl = G2G.ValidatedTxtCtrl(FPdlg,parmDict[prm],i,size=(90,-1))
            waveSizer.Add(ctrl,1,wx.ALIGN_CENTER_VERTICAL,1)
    MainSizer.Add(waveSizer)
    MainSizer.Add((-1,5))
    btnsizer = wx.BoxSizer(wx.HORIZONTAL)
    btn = wx.Button(FPdlg, wx.ID_ANY,'Add col')
    btnsizer.Add(btn)
    btn.Bind(wx.EVT_BUTTON,_onAddWave)
    btn = wx.Button(FPdlg, wx.ID_ANY,'Remove col')
    btnsizer.Add(btn)
    btn.Bind(wx.EVT_BUTTON,_onRemWave)
    btn = wx.Button(FPdlg, wx.ID_ANY,'CuKa1+2')
    btnsizer.Add(btn)
    btn.Bind(wx.EVT_BUTTON,_onSetCu2Wave)
    btn = wx.Button(FPdlg, wx.ID_ANY,'CuKa-5wave')
    btnsizer.Add(btn)
    btn.Bind(wx.EVT_BUTTON,_onSetCu5Wave)
    MainSizer.Add(btnsizer, 0, wx.ALIGN_CENTER, 0)
    MainSizer.Add((-1,5))
    btnsizer = wx.BoxSizer(wx.HORIZONTAL)
    btn = wx.Button(FPdlg, wx.ID_ANY,'Point Dect.')
    btn.Enable(not mode == 'BBpoint')
    btnsizer.Add(btn)
    btn.Bind(wx.EVT_BUTTON,_onSetPoint)
    btn = wx.Button(FPdlg, wx.ID_ANY,'PSD')
    btn.Enable(not mode == 'BBPSD')
    btnsizer.Add(btn)
    btn.Bind(wx.EVT_BUTTON,_onSetPSD)
    MainSizer.Add(btnsizer, 0, wx.ALIGN_CENTER, 0)
    MainSizer.Add((-1,5))
    
    prmSizer = wx.FlexGridSizer(cols=3,hgap=3,vgap=5)
    text = wx.StaticText(FPdlg,wx.ID_ANY,'label',style=wx.ALIGN_CENTER)
    text.SetBackgroundColour(wx.WHITE)
    prmSizer.Add(text,0,wx.EXPAND)
    text = wx.StaticText(FPdlg,wx.ID_ANY,'value',style=wx.ALIGN_CENTER)
    text.SetBackgroundColour(wx.WHITE)
    prmSizer.Add(text,0,wx.EXPAND)
    text = wx.StaticText(FPdlg,wx.ID_ANY,'explanation',style=wx.ALIGN_CENTER)
    text.SetBackgroundColour(wx.WHITE)
    prmSizer.Add(text,0,wx.EXPAND)
    for lbl,defVal,text in itemList:
        prmSizer.Add(wx.StaticText(FPdlg,wx.ID_ANY,lbl),1,wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL,1)
        if lbl not in parmDict: parmDict[lbl] = defVal
        ctrl = G2G.ValidatedTxtCtrl(FPdlg,parmDict,lbl,size=(70,-1))
        prmSizer.Add(ctrl,1,wx.ALL|wx.ALIGN_CENTER_VERTICAL,1)
        txt = wx.StaticText(FPdlg,wx.ID_ANY,text,size=(200,-1))
        txt.Wrap(180)
        prmSizer.Add(txt)
    MainSizer.Add(prmSizer)
    MainSizer.Add((-1,4),1,wx.EXPAND,1)
    btnsizer = wx.BoxSizer(wx.HORIZONTAL)
    btn = wx.Button(FPdlg, wx.ID_ANY, 'Plot peak')
    btnsizer.Add(btn)
    btn.Bind(wx.EVT_BUTTON,PlotTopasFPA)
    btnsizer.Add(wx.StaticText(FPdlg,wx.ID_ANY,' at '))
    if 'plotpos' not in simParms: simParms['plotpos'] =  simParms['minTT']
    ctrl = G2G.ValidatedTxtCtrl(FPdlg,simParms,'plotpos',size=(70,-1))
    btnsizer.Add(ctrl)
    btnsizer.Add(wx.StaticText(FPdlg,wx.ID_ANY,' deg.'))    
    MainSizer.Add(btnsizer, 0, wx.ALIGN_CENTER, 0)
    MainSizer.Add((-1,4),1,wx.EXPAND,1)
    btnsizer = wx.BoxSizer(wx.HORIZONTAL)
    OKbtn = wx.Button(FPdlg, wx.ID_OK)
    OKbtn.SetDefault()
    btnsizer.Add(OKbtn)
    Cbtn = wx.Button(FPdlg, wx.ID_CLOSE,"Cancel") 
    btnsizer.Add(Cbtn)
    MainSizer.Add(btnsizer, 0, wx.ALIGN_CENTER, 0)
    MainSizer.Add((-1,4),1,wx.EXPAND,1)
    # bindings for close of window
    OKbtn.Bind(wx.EVT_BUTTON,_onOK)
    Cbtn.Bind(wx.EVT_BUTTON,_onClose)
    FPdlg.SetSizer(MainSizer)
    MainSizer.Layout()
    MainSizer.Fit(FPdlg)
    FPdlg.SetMinSize(FPdlg.GetSize())
    FPdlg.SendSizeEvent()

def XferFPAsettings(InpParms):
    '''convert Topas-type parameters to SI units for NIST and place in a dict sorted
    according to use in each convoluter

    :param dict InpParms: a dict with Topas-like parameters, as set in 
      :func:`MakeTopasFPASizer`
    :returns: a nested dict with global parameters and those for each convolution
    '''
    wavenums = range(InpParms['numWave'])
    source_wavelengths_m = 1.e-10 * np.array([InpParms['wave'][i] for i in wavenums])
    la = [InpParms['int'][i] for i in wavenums]
    source_intensities = np.array(la)/max(la)
    source_lor_widths_m = 1.e-10 * 1.e-3 * np.array([InpParms['lwidth'][i] for i in wavenums])
    source_gauss_widths_m = 1.e-10 * 1.e-3 * np.array([0.001 for i in wavenums])
    
    NISTparms["emission"] = {'emiss_wavelengths' : source_wavelengths_m,
                'emiss_intensities' : source_intensities,
                'emiss_gauss_widths' : source_gauss_widths_m,
                'emiss_lor_widths' : source_lor_widths_m,
                'crystallite_size_gauss' : 1.e-9 * InpParms.get('Size_G',1e6),
                'crystallite_size_lor' : 1.e-9 * InpParms.get('Size_L',1e6)}
    
    if InpParms['filament_length'] == InpParms['receiving_slit_length']: # workaround: 
        InpParms['receiving_slit_length'] *= 1.00001 # avoid bug when slit lengths are identical
    NISTparms["axial"]  = {
            'axDiv':"full", 'slit_length_source' : 1e-3*InpParms['filament_length'],
            'slit_length_target' : 1e-3*InpParms['receiving_slit_length'],
            'length_sample' : 1e-3 * InpParms['sample_length'], 
            'n_integral_points' : 10,
            'angI_deg' : InpParms['soller_angle'],
            'angD_deg': InpParms['soller_angle']
            }
    if InpParms.get('LAC_cm',0) > 0:
        NISTparms["absorption"] = {
            'absorption_coefficient': InpParms['LAC_cm']*100, #like LaB6, in m^(-1)
            'sample_thickness': 1e-3 * InpParms['sample_thickness'],
            }
    elif "absorption" in NISTparms:
        del NISTparms["absorption"]

    if InpParms.get('lpsd_equitorial_divergence',0) > 0 and InpParms.get(
            'lpsd_th2_angular_range',0) > 0:
        PSDdetector_length_mm=np.arcsin(np.pi*InpParms['lpsd_th2_angular_range']/180.
                                            )*InpParms['Rs'] # mm
        NISTparms["si_psd"] = {
            'equatorial_divergence_deg': InpParms['lpsd_equitorial_divergence'],
            'si_psd_window_bounds': (0.,PSDdetector_length_mm/1000.)
            }
    elif "si_psd" in NISTparms:
        del NISTparms["si_psd"]
        
    if InpParms.get('Specimen_Displacement'):
        NISTparms["displacement"] = {'specimen_displacement': 1e-3 * InpParms['Specimen_Displacement']}
    elif "displacement" in NISTparms:
        del NISTparms["displacement"]

    if InpParms.get('receiving_slit_width'):
        NISTparms["receiver_slit"] = {'slit_width':1e-3*InpParms['receiving_slit_width']}
    elif "receiver_slit" in NISTparms:
        del NISTparms["receiver_slit"]

    #p.set_parameters(convolver="tube_tails",
    #        main_width=200e-6, tail_left=-1e-3,tail_right=1e-3, tail_intens=0.001
    #    )

    # set Global parameters
    max_wavelength = source_wavelengths_m[np.argmax(source_intensities)]
    NISTparms[""] = {
        'equatorial_divergence_deg' : InpParms['divergence'],
        'dominant_wavelength' : max_wavelength,
        'diffractometer_radius' : 1e-3* InpParms['Rs'],
        'oversampling' : InpParms['convolution_steps'],
        }
def setupFPAcalc():
    '''Create a peak profile object using the NIST XRD Fundamental 
    Parameters Code. 
    
    :returns: a profile object that can provide information on 
      each convolution or compute the composite peak shape. 
    '''
    p=FP.FP_profile(anglemode="twotheta",
                    output_gaussian_smoother_bins_sigma=1.0,
                    oversampling=NISTparms.get('oversampling',10))
    p.debug_cache=False
    #set parameters for each convolver
    for key in NISTparms:
        if key:
            p.set_parameters(convolver=key,**NISTparms[key])
        else:
            p.set_parameters(**NISTparms[key])
    return p
        
def doFPAcalc(NISTpk,ttArr,twotheta,calcwid,step):
    '''Compute a single peak using a NIST profile object

    :param object NISTpk: a peak profile computational object from the 
      NIST XRD Fundamental Parameters Code, typically established from
      a call to :func:`SetupFPAcalc`
    :param np.Array ttArr: an evenly-spaced grid of two-theta points (degrees)
    :param float twotheta: nominal center of peak (degrees)
    :param float calcwid: width to perform convolution (degrees)
    :param float step: step size
    '''
    # find closest point to twotheta (may be outside limits of the array)
    center_bin_idx=min(ttArr.searchsorted(twotheta),len(ttArr)-1)
    NISTpk.set_optimized_window(twotheta_exact_bin_spacing_deg=step,
                twotheta_window_center_deg=ttArr[center_bin_idx],
                twotheta_approx_window_fullwidth_deg=calcwid,
                )
    NISTpk.set_parameters(twotheta0_deg=twotheta)
    return center_bin_idx,NISTpk.compute_line_profile()

def MakeSimSizer(G2frame, dlg):
    '''Create a GUI to get simulation with parameters for Fundamental 
    Parameters fitting. 

    :param wx.Window dlg: Frame or Dialog where GUI will appear

    :returns: a sizer with the GUI controls 
 
    '''
    def _onOK(event):
        msg = ''
        if simParms['minTT']-simParms['calcwid']/1.5 < 0.1:
            msg += 'First peak minus half the calc width is too low'
        if simParms['maxTT']+simParms['calcwid']/1.5 > 175:
            if msg: msg += '\n'
            msg += 'Last peak plus half the calc width is too high'
        if simParms['npeaks'] < 8:
            if msg: msg += '\n'
            msg += 'At least 8 peaks are needed'
        if msg:
            G2G.G2MessageBox(dlg,msg,'Bad input, try again')
            return
        # compute "obs" pattern
        ttArr = np.arange(max(0.5,
                            simParms['minTT']-simParms['calcwid']/1.5),
                            simParms['maxTT']+simParms['calcwid']/1.5,
                            simParms['step'])
        intArr = np.zeros_like(ttArr)
        peaklist = np.linspace(simParms['minTT'],simParms['maxTT'],
                               simParms['npeaks'],endpoint=True)
        peakSpacing = (peaklist[-1]-peaklist[0])/(len(peaklist)-1)
        NISTpk = setupFPAcalc()
        minPtsHM = len(intArr)  # initialize points above half-max
        maxPtsHM = 0
        for num,twoth_peak in enumerate(peaklist):
            try:
                center_bin_idx,peakObj = doFPAcalc(
                    NISTpk,ttArr,twoth_peak,simParms['calcwid'],
                    simParms['step'])
            except:
                if msg: msg += '\n'
                msg = "Error computing convolution, revise input"
                continue
            if num == 0: G2plt.PlotFPAconvolutors(G2frame,NISTpk)
            pkMax = peakObj.peak.max()
            pkPts = len(peakObj.peak)
            minPtsHM = min(minPtsHM,sum(peakObj.peak >= 0.5*pkMax)) # points above half-max
            maxPtsHM = max(maxPtsHM,sum(peakObj.peak >= 0.5*pkMax)) # points above half-max
            startInd = center_bin_idx-(pkPts//2) #this should be the aligned start of the new data
            # scale peak so max I=10,000 and add into intensity array
            if startInd < 0:
                intArr[:startInd+pkPts] += 10000 * peakObj.peak[-startInd:]/pkMax
            elif startInd > len(intArr):
                break
            elif startInd+pkPts >= len(intArr):
                offset = pkPts - len( intArr[startInd:] )
                intArr[startInd:startInd+pkPts-offset] += 10000 * peakObj.peak[:-offset]/pkMax
            else:
                intArr[startInd:startInd+pkPts] += 10000 * peakObj.peak/pkMax
        # check if peaks are too closely spaced
        if maxPtsHM*simParms['step'] > peakSpacing/4:
            if msg: msg += '\n'
            msg += 'Maximum FWHM ({}) is too large compared to the peak spacing ({}). Decrease number of peaks or increase data range.'.format(
                maxPtsHM*simParms['step'], peakSpacing)
        # check if too few points across Hmax
        if minPtsHM < 10:
            if msg: msg += '\n'
            msg += 'There are only {} points above the half-max. 10 are needed. Dropping step size.'.format(minPtsHM)
            simParms['step'] *= 0.5
        if msg:
            G2G.G2MessageBox(dlg,msg,'Bad input, try again')
            wx.CallAfter(MakeSimSizer,G2frame, dlg)
            return
        # pattern has been computed successfully
        dlg.Destroy()
        wx.CallAfter(FitFPApeaks,ttArr, intArr, peaklist, maxPtsHM) # do peakfit outside event callback

    def FitFPApeaks(ttArr, intArr, peaklist, maxPtsHM):
        '''Perform a peak fit to the FP simulated pattern
        '''
        plswait = wx.Dialog(G2frame,style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add((1,1),1,wx.ALL|wx.EXPAND,1)
        txt = wx.StaticText(plswait,wx.ID_ANY,
                                'Fitting peaks...\nPlease wait...',
                                style=wx.ALIGN_CENTER)
        vbox.Add(txt,0,wx.ALL|wx.EXPAND)
        vbox.Add((1,1),1,wx.ALL|wx.EXPAND,1)
        plswait.SetSizer(vbox)
        plswait.Layout()
        plswait.CenterOnParent()
        plswait.Show() # post "please wait"
        wx.BeginBusyCursor()
        # pick out one or two most intense wavelengths
        ints = list(NISTparms['emission']['emiss_intensities'])
        Lam1 = NISTparms['emission']['emiss_wavelengths'][np.argmax(ints)]*1e10
        if len(ints) > 1: 
            ints[np.argmax(ints)] = -1
            Lam2 = NISTparms['emission']['emiss_wavelengths'][np.argmax(ints)]*1e10
        else:
            Lam2 = None
        histId = G2frame.AddSimulatedPowder(ttArr,intArr,
                                       'NIST Fundamental Parameters simulation',
                                       Lam1,Lam2)
        controls = G2frame.GPXtree.GetItemPyData(
            G2gd.GetGPXtreeItemId(G2frame,G2frame.root,'Controls'))
        controldat = controls.get('data',
                            {'deriv type':'analytic','min dM/M':0.001,})  #fil
        Parms,Parms2 = G2frame.GPXtree.GetItemPyData(
            G2gd.GetGPXtreeItemId(G2frame,histId,'Instrument Parameters'))
        peakData = G2frame.GPXtree.GetItemPyData(
            G2gd.GetGPXtreeItemId(G2frame,histId,'Peak List'))
        # set background to 0 with one term = 0; disable refinement
        bkg1,bkg2 = bkg = G2frame.GPXtree.GetItemPyData(
            G2gd.GetGPXtreeItemId(G2frame,histId,'Background'))
        bkg1[1]=False
        bkg1[2]=0
        bkg1[3]=0.0
        limits = G2frame.GPXtree.GetItemPyData(
            G2gd.GetGPXtreeItemId(G2frame,histId,'Limits'))
        # approximate asym correction
        try:
            Parms['SH/L'][1] = 0.25 * (
                NISTparms['axial']['length_sample']+
                NISTparms['axial']['slit_length_source']
                        ) / NISTparms['']['diffractometer_radius']
        except:
            pass
            
        for pos in peaklist:
            i = ttArr.searchsorted(pos)
            area = sum(intArr[max(0,i-maxPtsHM):min(len(intArr),i+maxPtsHM)])
            peakData['peaks'].append(G2mth.setPeakparms(Parms,Parms2,pos,area))
        histData = G2frame.GPXtree.GetItemPyData(histId)
        # refine peak positions only
        bxye = np.zeros(len(histData[1][1]))
        peakData['sigDict'] = G2pwd.DoPeakFit('LSQ',peakData['peaks'],
                                            bkg,limits[1],
                                            Parms,Parms2,histData[1],bxye,[],
                                           False,controldat,None)[0]
        # refine peak areas as well
        for pk in peakData['peaks']:
            pk[1] = True
        peakData['sigDict'] = G2pwd.DoPeakFit('LSQ',peakData['peaks'],
                                            bkg,limits[1],
                                            Parms,Parms2,histData[1],bxye,[],
                                           False,controldat)[0]
        # refine profile function
        for p in ('U', 'V', 'W', 'X', 'Y'):
            Parms[p][2] = True
        peakData['sigDict'] = G2pwd.DoPeakFit('LSQ',peakData['peaks'],
                                            bkg,limits[1],
                                            Parms,Parms2,histData[1],bxye,[],
                                           False,controldat)[0]
        # add in asymmetry
        Parms['SH/L'][2] = True
        peakData['sigDict'] = G2pwd.DoPeakFit('LSQ',peakData['peaks'],
                                            bkg,limits[1],
                                            Parms,Parms2,histData[1],bxye,[],
                                           False,controldat)[0]
        # reset "initial" profile
        for p in Parms:
            if len(Parms[p]) == 3:
                Parms[p][0] = Parms[p][1]
                Parms[p][2] = False
        wx.EndBusyCursor()
        plswait.Destroy() # remove "please wait"
        # save Iparms
        pth = G2G.GetExportPath(G2frame)
        fldlg = wx.FileDialog(G2frame, 'Set name to save GSAS-II instrument parameters file', pth, '', 
            'instrument parameter files (*.instprm)|*.instprm',wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
        try:
            if fldlg.ShowModal() == wx.ID_OK:
                filename = fldlg.GetPath()
                # make sure extension is .instprm
                filename = os.path.splitext(filename)[0]+'.instprm'
                File = open(filename,'w')
                File.write("#GSAS-II instrument parameter file; do not add/delete items!\n")
                for item in Parms:
                    File.write(item+':'+str(Parms[item][1])+'\n')
                File.close()
                print ('Instrument parameters saved to: '+filename)
        finally:
            fldlg.Destroy()
        #GSASIIpath.IPyBreak()
        
    def _onClose(event):
        dlg.Destroy()
    def SetButtonStatus(done=False):
        OKbtn.Enable(bool(NISTparms))
        saveBtn.Enable(bool(NISTparms))
        if done: _onOK(None)
    def _onSetFPA(event):
        # Create a non-modal dialog for Topas-style FP input.
        FPdlg = wx.Dialog(dlg,wx.ID_ANY,'FPA parameters',
                style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        MakeTopasFPASizer(G2frame,FPdlg,'BBpoint',SetButtonStatus)
        FPdlg.Raise()
        FPdlg.Show() 
    def _onSaveFPA(event):
        filename = G2G.askSaveFile(G2frame,'','.NISTfpa',
                                       'dict of NIST FPA values',dlg)
        if not filename: return
        fp = open(filename,'w')
        fp.write('# parameters to be used in the NIST XRD Fundamental Parameters program\n')
        fp.write('{\n')
        for key in sorted(NISTparms):
            fp.write("   '"+key+"' : "+str(NISTparms[key])+",")
            if not key: fp.write('  # global parameters')
            fp.write('\n')
        fp.write('}\n')
        fp.close()
    def _onReadFPA(event):
        filename = G2G.GetImportFile(G2frame,
                message='Read file with dict of values for NIST Fundamental Parameters',
                parent=dlg,
                wildcard='dict of NIST FPA values|*.NISTfpa')
        if not filename: return
        if not filename[0]: return
        try:
            txt = open(filename[0],'r').read()
            NISTparms.clear()
            array = np.array
            d = eval(txt)
            NISTparms.update(d)
        except Exception as err:
            G2G.G2MessageBox(dlg,
                    u'Error reading file {}:{}\n'.format(filename,err),
                    'Bad dict input')
        #GSASIIpath.IPyBreak()
        SetButtonStatus()

    if dlg.GetSizer(): dlg.GetSizer().Clear(True)
    MainSizer = wx.BoxSizer(wx.VERTICAL)
    MainSizer.Add(wx.StaticText(dlg,wx.ID_ANY,
            'Fit Profile Parameters to Peaks from Fundamental Parameters',
            style=wx.ALIGN_CENTER),0,wx.EXPAND)
    MainSizer.Add((-1,5))
    prmSizer = wx.FlexGridSizer(cols=2,hgap=3,vgap=5)
    text = wx.StaticText(dlg,wx.ID_ANY,'value',style=wx.ALIGN_CENTER)
    text.SetBackgroundColour(wx.WHITE)
    prmSizer.Add(text,0,wx.EXPAND)
    text = wx.StaticText(dlg,wx.ID_ANY,'explanation',style=wx.ALIGN_CENTER)
    text.SetBackgroundColour(wx.WHITE)
    prmSizer.Add(text,0,wx.EXPAND)
    for key,defVal,text in (
            ('minTT',3.,'Location of first peak in 2theta (deg)'),
            ('maxTT',123.,'Location of last peak in 2theta (deg)'),
            ('step',0.01,'Pattern step size (deg 2theta)'),
            ('npeaks',13.,'Number of peaks'),
            ('calcwid',2.,'Range to compute each peak (deg 2theta)'),
            ):
        if key not in simParms: simParms[key] = defVal
        ctrl = G2G.ValidatedTxtCtrl(dlg,simParms,key,size=(70,-1))
        prmSizer.Add(ctrl,1,wx.ALL|wx.ALIGN_CENTER_VERTICAL,1)
        txt = wx.StaticText(dlg,wx.ID_ANY,text,size=(300,-1))
        txt.Wrap(280)
        prmSizer.Add(txt)
    MainSizer.Add(prmSizer)

    btnsizer = wx.BoxSizer(wx.HORIZONTAL)
    btn = wx.Button(dlg, wx.ID_ANY,'Input FP vals')
    btnsizer.Add(btn)
    btn.Bind(wx.EVT_BUTTON,_onSetFPA)
    saveBtn = wx.Button(dlg, wx.ID_ANY,'Save FPA dict')
    btnsizer.Add(saveBtn)
    saveBtn.Bind(wx.EVT_BUTTON,_onSaveFPA)
    readBtn = wx.Button(dlg, wx.ID_ANY,'Read FPA dict')
    btnsizer.Add(readBtn)
    readBtn.Bind(wx.EVT_BUTTON,_onReadFPA)
    MainSizer.Add(btnsizer, 0, wx.ALIGN_CENTER, 0)
    MainSizer.Add((-1,4),1,wx.EXPAND,1)
    txt = wx.StaticText(dlg,wx.ID_ANY,
                            'If you use this, please cite: '+Citation,
                            size=(350,-1))
    txt.Wrap(340)
    MainSizer.Add(txt,0,wx.ALIGN_CENTER)
    btnsizer = wx.BoxSizer(wx.HORIZONTAL)
    OKbtn = wx.Button(dlg, wx.ID_OK)
    OKbtn.SetDefault()
    btnsizer.Add(OKbtn)
    Cbtn = wx.Button(dlg, wx.ID_CLOSE,"Cancel") 
    btnsizer.Add(Cbtn)
    MainSizer.Add(btnsizer, 0, wx.ALIGN_CENTER, 0)
    MainSizer.Add((-1,4),1,wx.EXPAND,1)
    # bindings for close of window
    OKbtn.Bind(wx.EVT_BUTTON,_onOK)
    Cbtn.Bind(wx.EVT_BUTTON,_onClose)
    SetButtonStatus()
    dlg.SetSizer(MainSizer)
    MainSizer.Layout()
    MainSizer.Fit(dlg)
    dlg.SetMinSize(dlg.GetSize())
    dlg.SendSizeEvent()
    dlg.Raise()
    
def GetFPAInput(G2frame):
    dlg = wx.Dialog(G2frame,wx.ID_ANY,'FPA input',
            style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
    MakeSimSizer(G2frame,dlg)
    dlg.Show()
    return
        