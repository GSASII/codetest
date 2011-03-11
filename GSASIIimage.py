#GSASII image calculations: ellipse fitting & image integration        
########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################
import math
import wx
import time
import numpy as np
import numpy.linalg as nl
import GSASIIpath
import GSASIIplot as G2plt
import GSASIIlattice as G2lat
import fellipse as fel

# trig functions in degrees
sind = lambda x: math.sin(x*math.pi/180.)
asind = lambda x: 180.*math.asin(x)/math.pi
tand = lambda x: math.tan(x*math.pi/180.)
atand = lambda x: 180.*math.atan(x)/math.pi
atan2d = lambda y,x: 180.*math.atan2(y,x)/math.pi
cosd = lambda x: math.cos(x*math.pi/180.)
acosd = lambda x: 180.*math.acos(x)/math.pi
rdsq2d = lambda x,p: round(1.0/math.sqrt(x),p)
#numpy versions
npsind = lambda x: np.sin(x*np.pi/180.)
npasind = lambda x: 180.*np.arcsin(x)/np.pi
npcosd = lambda x: np.cos(x*np.pi/180.)
nptand = lambda x: np.tan(x*np.pi/180.)
npatand = lambda x: 180.*np.arctan(x)/np.pi
npatan2d = lambda y,x: 180.*np.arctan2(y,x)/np.pi
    
def pointInPolygon(pXY,xy):
    #pXY - assumed closed 1st & last points are duplicates
    Inside = False
    N = len(pXY)
    p1x,p1y = pXY[0]
    for i in range(N+1):
        p2x,p2y = pXY[i%N]
        if (max(p1y,p2y) >= xy[1] > min(p1y,p2y)) and (xy[0] <= max(p1x,p2x)):
            if p1y != p2y:
                xinters = (xy[1]-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
            if p1x == p2x or xy[0] <= xinters:
                Inside = not Inside
        p1x,p1y = p2x,p2y
    return Inside
        
def makeMat(Angle,Axis):
    #Make rotation matrix from Angle in degrees,Axis =0 for rotation about x, =1 for about y, etc.
    cs = cosd(Angle)
    ss = sind(Angle)
    M = np.array(([1.,0.,0.],[0.,cs,-ss],[0.,ss,cs]),dtype=np.float32)
    return np.roll(np.roll(M,Axis,axis=0),Axis,axis=1)
                    
def FitRing(ring,delta):
    parms = []
    if delta:
        err,parms = FitEllipse(ring)
    errc,parmsc = FitCircle(ring)
    errc = errc[0]/(len(ring)*parmsc[2][0]**2)
#    print 'Ellipse?',err,parms,len(ring)
#    print 'Circle? ',errc,parmsc
    if not parms or errc < .1:
        parms = parmsc
    return parms
        
def FitCircle(ring):
    
    def makeParmsCircle(B):
        cent = [-B[0]/2,-B[1]/2]
        phi = 0.
        sr1 = sr2 = math.sqrt(cent[0]**2+cent[1]**2-B[2])
        return cent,phi,[sr1,sr2]
        
    ring = np.array(ring)
    x = np.asarray(ring.T[0])
    y = np.asarray(ring.T[1])
    
    M = np.array((x,y,np.ones_like(x)))
    B = np.array(-(x**2+y**2))
    result = nl.lstsq(M.T,B)
    return result[1],makeParmsCircle(result[0])
        
def FitEllipse(ring):
            
    def makeParmsEllipse(B):
        det = 4.*(1.-B[0]**2)-B[1]**2
        if det < 0.:
            print 'hyperbola!'
            return 0
        elif det == 0.:
            print 'parabola!'
            return 0
        cent = [(B[1]*B[3]-2.*(1.-B[0])*B[2])/det, \
            (B[1]*B[2]-2.*(1.+B[0])*B[3])/det]
        phi = 0.5*atand(0.5*B[1]/B[0])
        
        a = (1.+B[0])/cosd(2*phi)
        b = 2.-a
        f = (1.+B[0])*cent[0]**2+(1.-B[0])*cent[1]**2+B[1]*cent[0]*cent[1]-B[4]
        if f/a < 0 or f/b < 0:
            return 0
        sr1 = math.sqrt(f/a)
        sr2 = math.sqrt(f/b)
        if sr1 > sr2:
            sr1,sr2 = sr2,sr1
            phi -= 90.
            if phi < -90.:
                phi += 180.
        return cent,phi,[sr1,sr2]
                
    ring = np.array(ring)
    x = np.asarray(ring.T[0])
    y = np.asarray(ring.T[1])
    M = np.array((x**2-y**2,x*y,x,y,np.ones_like(x)))
    B = np.array(-(x**2+y**2))
    bb,err = fel.fellipse(len(x),x,y,1.E-7)
    return err,makeParmsEllipse(bb)
    
def FitDetector(rings,p0,wave):
    from scipy.optimize import leastsq
        
    def ellipseCalcD(B,xyd,wave):
        x = xyd[0]
        y = xyd[1]
        dsp = xyd[2]
        dist,x0,y0,phi,tilt = B
        tth = 2.0*npasind(wave/(2.*dsp))
        ttth = nptand(tth)
        radius = dist*ttth
        stth = npsind(tth)
        cosb = npcosd(tilt)
        R1 = dist*stth*npcosd(tth)*cosb/(cosb**2-stth**2)
        R0 = np.sqrt(R1*radius*cosb)
        zdis = R1*ttth*nptand(tilt)
        X = x-x0+zdis*npsind(phi)
        Y = y-y0-zdis*npcosd(phi)
        XR = X*npcosd(phi)-Y*npsind(phi)
        YR = X*npsind(phi)+Y*npcosd(phi)
        return (XR/R0)**2+(YR/R1)**2-1
    def ellipseCalcW(C,xyd):
        dist,x0,y0,phi,tilt,wave = C
        B = dist,x0,y0,phi,tilt
        return ellipseCalcD(B,xyd,wave)
    result = leastsq(ellipseCalcD,p0,args=(rings.T,wave))
    if len(rings) > 1:
        p0 = result[0]
        p0 = np.append(p0,wave)
        resultW = leastsq(ellipseCalcW,p0,args=(rings.T,))
        return result[0],resultW[0][-1]
    else:
        return result[0],wave
            
def ImageLocalMax(image,w,Xpix,Ypix):
    w2 = w*2
    sizey,sizex = image.shape
    xpix = int(Xpix)            #get reference corner of pixel chosen
    ypix = int(Ypix)
    if (w < xpix < sizex-w) and (w < ypix < sizey-w) and image[ypix,xpix]:
        Z = image[ypix-w:ypix+w,xpix-w:xpix+w]
        Zmax = np.argmax(Z)
        Zmin = np.argmin(Z)
        xpix += Zmax%w2-w
        ypix += Zmax/w2-w
        return xpix,ypix,np.ravel(Z)[Zmax],np.ravel(Z)[Zmin]
    else:
        return 0,0,0,0
    
def makeRing(dsp,ellipse,pix,reject,scalex,scaley,image):
    cent,phi,radii = ellipse
    cphi = cosd(phi)
    sphi = sind(phi)
    ring = []
    amin = 180
    amax = -180
    for a in range(-180,180,1):
        x = radii[0]*cosd(a)
        y = radii[1]*sind(a)
        X = (cphi*x-sphi*y+cent[0])*scalex      #convert mm to pixels
        Y = (sphi*x+cphi*y+cent[1])*scaley
        X,Y,I,J = ImageLocalMax(image,pix,X,Y)      
        if I and J and I/J > reject:
            X += .5                             #set to center of pixel
            Y += .5
            X /= scalex                         #convert to mm
            Y /= scaley
            amin = min(amin,a)
            amax = max(amax,a)
            ring.append([X,Y,dsp])
    if len(ring) < 20:             #want more than 20 deg
        return [],amax-amin
    return ring,amax-amin > 90
    
def makeIdealRing(ellipse,azm=None):
    cent,phi,radii = ellipse
    cphi = cosd(phi)
    sphi = sind(phi)
    ring = []
    if azm:
        aR = azm[0],azm[1],1
        if azm[1]-azm[0] > 180:
            aR[2] = 2
    else:
        aR = 0,362,2
    for a in range(aR[0],aR[1],aR[2]):
        x = radii[0]*cosd(a-phi)
        y = radii[1]*sind(a-phi)
        X = (cphi*x-sphi*y+cent[0])
        Y = (sphi*x+cphi*y+cent[1])
        ring.append([X,Y])
    return ring
    
def calcDist(radii,tth):
    stth = sind(tth)
    ctth = cosd(tth)
    ttth = tand(tth)
    return math.sqrt(radii[0]**4/(ttth**2*((radii[0]*ctth)**2+(radii[1]*stth)**2)))
    
def calcZdisCosB(radius,tth,radii):
    cosB = sinb = radii[0]**2/(radius*radii[1])
    if cosB > 1.:
        return 0.,1.
    else:
        cosb = math.sqrt(1.-sinb**2)
        ttth = tand(tth)
        zdis = radii[1]*ttth*cosb/sinb
        return zdis,cosB
    
def GetEllipse(dsp,data):
    dist = data['distance']
    cent = data['center']
    tilt = data['tilt']
    phi = data['rotation']
    radii = [0,0]
    tth = 2.0*asind(data['wavelength']/(2.*dsp))
    ttth = tand(tth)
    stth = sind(tth)
    ctth = cosd(tth)
    cosb = cosd(tilt)
    radius = dist*ttth
    radii[1] = dist*stth*ctth*cosb/(cosb**2-stth**2)
    if radii[1] > 0:
        radii[0] = math.sqrt(radii[1]*radius*cosb)
        zdis = radii[1]*ttth*tand(tilt)
        elcent = [cent[0]-zdis*sind(phi),cent[1]+zdis*cosd(phi)]
        return elcent,phi,radii
    else:
        return False
        
def GetDetectorXY(dsp,azm,data):
    from scipy.optimize import fsolve
    def func(xy,*args):
       azm,phi,R0,R1,A,B = args
       cp = cosd(phi)
       sp = sind(phi)
       x,y = xy
       out = []
       out.append(y-x*tand(azm))
       out.append(R0**2*((x+A)*sp-(y+B)*cp)**2+R1**2*((x+A)*cp+(y+B)*sp)**2-(R0*R1)**2)
       return out
    elcent,phi,radii = GetEllipse(dsp,data)
    cent = data['center']
    tilt = data['tilt']
    phi = data['rotation']
    wave = data['wavelength']
    dist = data['distance']
    tth = 2.0*asind(wave/(2.*dsp))
    ttth = tand(tth)
    radius = dist*ttth
    stth = sind(tth)
    cosb = cosd(tilt)
    R1 = dist*stth*cosd(tth)*cosb/(cosb**2-stth**2)
    R0 = math.sqrt(R1*radius*cosb)
    zdis = R1*ttth*tand(tilt)
    A = zdis*sind(phi)
    B = -zdis*cosd(phi)
    xy0 = [radius*cosd(azm),radius*sind(azm)]
    xy = fsolve(func,xy0,args=(azm,phi,R0,R1,A,B))+cent
    return xy
                    
def GetTthAzmDsp(x,y,data):
    wave = data['wavelength']
    dist = data['distance']
    cent = data['center']
    tilt = data['tilt']
    phi = data['rotation']
    azmthoff = data['azmthOff']
    dx = np.array(x-cent[0],dtype=np.float32)
    dy = np.array(y-cent[1],dtype=np.float32)
    X = np.array(([dx,dy,np.zeros_like(dx)]),dtype=np.float32).T
    X = np.dot(X,makeMat(phi,2))
    Z = np.dot(X,makeMat(tilt,0)).T[2]
    tth = npatand(np.sqrt(dx**2+dy**2-Z**2)/(dist-Z))
    dsp = wave/(2.*npsind(tth/2.))
    azm = npatan2d(dy,dx)+azmthoff
    return tth,azm,dsp
    
def GetTth(x,y,data):
    return GetTthAzmDsp(x,y,data)[0]
    
def GetTthAzm(x,y,data):
    return GetTthAzmDsp(x,y,data)[0:2]
    
def GetDsp(x,y,data):
    return GetTthAzmDsp(x,y,data)[2]
       
def GetAzm(x,y,data):
    return GetTthAzmDsp(x,y,data)[1]
       
def ImageCompress(image,scale):
    if scale == 1:
        return image
    else:
        return image[::scale,::scale]
        
def ImageCalibrate(self,data):
    import copy
    import ImageCalibrants as calFile
    print 'image calibrate'
    time0 = time.time()
    ring = data['ring']
    pixelSize = data['pixelSize']
    scalex = 1000./pixelSize[0]
    scaley = 1000./pixelSize[1]
    pixLimit = data['pixLimit']
    cutoff = data['cutoff']
    if len(ring) < 5:
        print 'not enough inner ring points for ellipse'
        return False
        
    #fit start points on inner ring
    data['ellipses'] = []
    outE = FitRing(ring,True)
    if outE:
        print 'start ellipse:',outE
        ellipse = outE
    else:
        return False
        
    #setup 360 points on that ring for "good" fit
    Ring,delt = makeRing(1.0,ellipse,pixLimit,cutoff,scalex,scaley,self.ImageZ)
    if Ring:
        ellipse = FitRing(Ring,delt)
        Ring,delt = makeRing(1.0,ellipse,pixLimit,cutoff,scalex,scaley,self.ImageZ)    #do again
        ellipse = FitRing(Ring,delt)
    else:
        print '1st ring not sufficiently complete to proceed'
        return False
    print 'inner ring:',ellipse
    data['center'] = copy.copy(ellipse[0])           #not right!! (but useful for now)
    data['ellipses'].append(ellipse[:]+('r',))
    G2plt.PlotImage(self,newImage=False)
    
    #setup for calibration
    data['rings'] = []
    data['ellipses'] = []
    if not data['calibrant']:
        print 'no calibration material selected'
        return True
    
    skip = data['calibskip']
    dmin = data['calibdmin']
    Bravais,cell = calFile.Calibrants[data['calibrant']][:2]
    A = G2lat.cell2A(cell)
    wave = data['wavelength']
    cent = data['center']
    elcent,phi,radii = ellipse
    HKL = G2lat.GenHBravais(dmin,Bravais,A)[skip:]
    dsp = HKL[0][3]
    tth = 2.0*asind(wave/(2.*dsp))
    ttth = tand(tth)
    data['distance'] = dist = calcDist(radii,tth)
    radius = dist*tand(tth)
    zdis,cosB = calcZdisCosB(radius,tth,radii)
    cent1 = []
    cent2 = []
    xSum = 0
    ySum = 0
    zxSum = 0
    zySum = 0
    phiSum = 0
    tiltSum = 0
    distSum = 0
    Zsum = 0
    for i,H in enumerate(HKL):
        dsp = H[3]
        tth = 2.0*asind(0.5*wave/dsp)
        stth = sind(tth)
        ctth = cosd(tth)
        ttth = tand(tth)
        radius = dist*ttth
        elcent,phi,radii = ellipse
        radii[1] = dist*stth*ctth*cosB/(cosB**2-stth**2)
        radii[0] = math.sqrt(radii[1]*radius*cosB)
        zdis,cosB = calcZdisCosB(radius,tth,radii)
        zsinp = zdis*sind(phi)
        zcosp = zdis*cosd(phi)
        cent = data['center']
        elcent = [cent[0]+zsinp,cent[1]-zcosp]
        ratio = radii[1]/radii[0]
        Ring,delt = makeRing(dsp,ellipse,pixLimit,cutoff,scalex,scaley,self.ImageZ)
        if Ring:
            numZ = len(Ring)
            data['rings'].append(np.array(Ring))
            newellipse = FitRing(Ring,delt)
            elcent,phi,radii = newellipse                
            if abs(phi) > 45. and phi < 0.:
                phi += 180.
            dist = calcDist(radii,tth)
            distR = 1.-dist/data['distance']
            if abs(distR) > 0.01:
                continue
            if distR > 0.001:
                print 'Wavelength too large?'
            elif distR < -0.001:
                print 'Wavelength too small?'
            else:
                ellipse = newellipse
                if abs((radii[1]/radii[0]-ratio)/ratio) > 0.1:
                    print 'Bad fit for ring # %i. Try reducing Pixel search range'%(i)
                    return False
            zdis,cosB = calcZdisCosB(radius,tth,radii)
            Tilt = acosd(cosB)          # 0 <= tilt <= 90
            zsinp = zdis*sind(ellipse[1])
            zcosp = zdis*cosd(ellipse[1])
            cent1.append(np.array([elcent[0]+zsinp,elcent[1]-zcosp]))
            cent2.append(np.array([elcent[0]-zsinp,elcent[1]+zcosp]))
            if i:
                d1 = cent1[-1]-cent1[-2]        #get shift of 2 possible center solutions
                d2 = cent2[-1]-cent2[-2]
                if np.dot(d2,d2) > np.dot(d1,d1):  #right solution is the larger shift
                    data['center'] = cent1[-1]
                else:
                    data['center'] = cent2[-1]
                Zsum += numZ
                phiSum += numZ*phi
                distSum += numZ*dist
                xSum += numZ*data['center'][0]
                ySum += numZ*data['center'][1]
                tiltSum += numZ*abs(Tilt)
            cent = data['center']
            print ('for ring # %2i dist %.3f rotate %6.2f tilt %6.2f Xcent %.3f Ycent %.3f Npts %d' 
                %(i,dist,phi,Tilt,cent[0],cent[1],numZ))
            data['ellipses'].append(copy.deepcopy(ellipse+('r',)))
        else:
            break
    G2plt.PlotImage(self,newImage=True)
    fullSize = len(self.ImageZ)/scalex
    if 2*radii[1] < .9*fullSize:
        print 'Are all usable rings (>25% visible) used? Try reducing Min ring I/Ib'
    if not Zsum:
        print 'Only one ring fitted. Check your wavelength.'
        return False
    cent = data['center'] = [xSum/Zsum,ySum/Zsum]
    wave = data['wavelength']
    dist = data['distance'] = distSum/Zsum
    
    #possible error if no. of rings < 3! Might need trap here
    d1 = cent1[-1]-cent1[1]             #compare last ring to 2nd ring
    d2 = cent2[-1]-cent2[1]
    Zsign = 1
    len1 = math.sqrt(np.dot(d1,d1))
    len2 = math.sqrt(np.dot(d2,d2))
    t1 = d1/len1
    t2 = d2/len2
    if len2 > len1:
        if -135. < atan2d(t2[1],t2[0]) < 45.:
            Zsign = -1
    else:
        if -135. < atan2d(t1[1],t1[0]) < 45.:
            Zsign = -1
    
    tilt = data['tilt'] = Zsign*tiltSum/Zsum
    phi = data['rotation'] = phiSum/Zsum
    rings = np.concatenate((data['rings']),axis=0)
    p0 = [dist,cent[0],cent[1],phi,tilt]
    result,newWave = FitDetector(rings,p0,wave)
    print 'Suggested new wavelength = ',('%.5f')%(newWave),' (not reliable if distance > 2m)'
    data['distance'] = result[0]
    data['center'] = result[1:3]
    data['rotation'] = np.mod(result[3],360.0)
    data['tilt'] = result[4]
    N = len(data['ellipses'])
    data['ellipses'] = []           #clear away individual ellipse fits
    for H in HKL[:N]:
        ellipse = GetEllipse(H[3],data)
        data['ellipses'].append(copy.deepcopy(ellipse+('b',)))
    print 'calibration time = ',time.time()-time0
    G2plt.PlotImage(self,newImage=True)        
    return True
    
def Make2ThetaAzimuthMap(data,masks,iLim,jLim):
    import numpy.ma as ma
    import polymask as pm
    #transforms 2D image from x,y space to 2-theta,azimuth space based on detector orientation
    pixelSize = data['pixelSize']
    scalex = pixelSize[0]/1000.
    scaley = pixelSize[1]/1000.
    
    tay,tax = np.mgrid[iLim[0]+0.5:iLim[1]+.5,jLim[0]+.5:jLim[1]+.5]         #bin centers not corners
    tax = np.asfarray(tax*scalex,dtype=np.float32)
    tay = np.asfarray(tay*scaley,dtype=np.float32)
    nI = iLim[1]-iLim[0]
    nJ = jLim[1]-jLim[0]
    #make position masks here
    spots = masks['Points']
    polygons = masks['Polygons']
    tam = ma.make_mask_none((iLim[1]-iLim[0],jLim[1]-jLim[0]))
    for polygon in polygons:
        if polygon:
            tamp = ma.make_mask_none((nI*nJ))
            tam = ma.mask_or(tam.flatten(),ma.make_mask(pm.polymask(nI*nJ,
                tax.flatten(),tay.flatten(),len(polygon),polygon,tamp)))
    if tam.shape: tam = np.reshape(tam,(nI,nJ))
    for X,Y,diam in spots:
        tam = ma.mask_or(tam,ma.getmask(ma.masked_less((tax-X)**2+(tay-Y)**2,(diam/2.)**2)))
    return np.array(GetTthAzm(tax,tay,data)),tam           #2-theta & azimuth arrays & position mask

def Fill2ThetaAzimuthMap(masks,TA,tam,image):
    import numpy.ma as ma
    Zlim = masks['Thresholds'][1]
    rings = masks['Rings']
    arcs = masks['Arcs']
    TA = np.dstack((ma.getdata(TA[1]),ma.getdata(TA[0])))    #azimuth, 2-theta
    tax,tay = np.dsplit(TA,2)    #azimuth, 2-theta
    for tth,thick in rings:
        tam = ma.mask_or(tam.flatten(),ma.getmask(ma.masked_inside(tay.flatten(),max(0.01,tth-thick/2.),tth+thick/2.)))
    for tth,azm,thick in arcs:
        tam = ma.mask_or(tam.flatten(),ma.getmask(ma.masked_inside(tay.flatten(),max(0.01,tth-thick/2.),tth+thick/2.))* \
            ma.getmask(ma.masked_inside(tax.flatten(),azm[0],azm[1])))
    taz = ma.masked_outside(image.flatten(),int(Zlim[0]),Zlim[1])
    tam = ma.mask_or(tam.flatten(),ma.getmask(taz))
    tax = ma.compressed(ma.array(tax.flatten(),mask=tam))
    tay = ma.compressed(ma.array(tay.flatten(),mask=tam))
    taz = ma.compressed(ma.array(taz.flatten(),mask=tam))
    del(tam)
    return tax,tay,taz
    
def ImageIntegrate(image,data,masks):
    import histogram2d as h2d
    print 'Begin image integration'
    LUtth = data['IOtth']
    if data['fullIntegrate']:
        LRazm = [-180,180]
    else:
        LRazm = data['LRazimuth']
    numAzms = data['outAzimuths']
    numChans = data['outChannels']
    Dtth = (LUtth[1]-LUtth[0])/numChans
    Dazm = (LRazm[1]-LRazm[0])/numAzms
    NST = np.zeros(shape=(numAzms,numChans),order='F',dtype=np.float32)
    H0 = np.zeros(shape=(numAzms,numChans),order='F',dtype=np.float32)
    imageN = len(image)
    Nx,Ny = data['size']
    nXBlks = (Nx-1)/1024+1
    nYBlks = (Ny-1)/1024+1
    Nup = nXBlks*nYBlks*3+3
    dlg = wx.ProgressDialog("Elapsed time","2D image integration",Nup,
        style = wx.PD_ELAPSED_TIME|wx.PD_AUTO_HIDE)
    try:
        t0 = time.time()
        Nup = 0
        dlg.Update(Nup)
        for iBlk in range(nYBlks):
            iBeg = iBlk*1024
            iFin = min(iBeg+1024,Ny)
            for jBlk in range(nXBlks):
                jBeg = jBlk*1024
                jFin = min(jBeg+1024,Nx)                
                print 'Process map block:',iBlk,jBlk,' limits:',iBeg,iFin,jBeg,jFin
                TA,tam = Make2ThetaAzimuthMap(data,masks,(iBeg,iFin),(jBeg,jFin))           #2-theta & azimuth arrays & create position mask
                Nup += 1
                dlg.Update(Nup)
                Block = image[iBeg:iFin,jBeg:jFin]
                tax,tay,taz = Fill2ThetaAzimuthMap(masks,TA,tam,Block)    #and apply masks
                del TA,tam
                Nup += 1
                dlg.Update(Nup)
                NST,H0 = h2d.histogram2d(len(tax),tax,tay,taz,numAzms,numChans,LRazm,LUtth,Dazm,Dtth,NST,H0)
                del tax,tay,taz
                Nup += 1
                dlg.Update(Nup)
        NST = np.array(NST)
        H0 = np.divide(H0,NST)
        H0 = np.nan_to_num(H0)
        del NST
        if Dtth:
            H2 = [tth for tth in np.linspace(LUtth[0],LUtth[1],numChans+1)]
        else:
            H2 = LUtth
        if Dazm:        
            H1 = [azm for azm in np.linspace(LRazm[0],LRazm[1],numAzms+1)]
        else:
            H1 = LRazm
        Nup += 1
        dlg.Update(Nup)
        t1 = time.time()
    finally:
        dlg.Destroy()
    print 'Integration complete'
    print "Elapsed time:","%8.3f"%(t1-t0), "s"
    return H0,H1,H2
