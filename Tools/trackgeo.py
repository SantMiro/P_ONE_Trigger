#!/usr/bin/env python

import numpy as np
import sys
from icecube import icetray,dataio,dataclasses,simclasses,phys_services,filterscripts,gulliver,recclasses


'''
This module script calculates muon track length inside the
detector, i.e., calculates the entry point in the detector
and the exit point (if any) and returns various parameters
'''

class CylinderIntersection(icetray.I3ConditionalModule):
    '''
    This class computes the line segments inside a
    cylindrical detector volume, size of the cylinder
    can be provided as initialization of the class.
    '''
    def __init__(self,context):
        icetray.I3ConditionalModule.__init__(self,context)
        self.AddParameter('inputmap','Name of inputmap', 'I3MCTree')
        self.AddParameter('outputmap','Name of output', 'Distance_cut_off')
        self.AddParameter('rad','radius',120.0 + 50.0)
        self.AddParameter('h_up','height up',500. + 50.)
        self.AddParameter('h_dn','height down', -1. * 500. - 50.)
        self.AddParameter('track','Distance inside detector', 200.)
        self.AddOutBox('OutBox')
        #self.rad = r #Radius of the cylinder


        #self.h_up = h/2.+50.#length up from the center (middle)
        #self.h_dn = -1.*h/2.+50.
    def Configure(self):
        self.inputmap = self.GetParameter('inputmap')
        self.outputmap = self.GetParameter('outputmap')
        self.rad = self.GetParameter('rad')
        self.h_up = self.GetParameter('h_up')
        self.h_dn = self.GetParameter('h_dn')
        self.track = self.GetParameter('track')
            #get the coefficients for a solution (roots) of
    #quadratic eqution of line intersecting a circle
    def coefficient(self,p):

        '''
        Computes the coefficients for line intersecting a circle equation
        p: I3Particle to get line equation from
        retruns the coefficients of the quadratic equation
        '''


        x0,y0,z0=p.pos
        #print(x0,y0,z0)
        theta,phi = (p.dir.theta,p.dir.phi)

        #solve the parametric equation of a line for circle w/ radius R
        #to get the coefficients in terms of line position coordinates,
        # direction vectors and circle radius
        c1 = np.sin(theta)**2
        c2 = 2.*np.sin(theta)*(x0*np.cos(phi)+y0*np.sin(phi))
        c3 = x0**2+y0**2-self.rad**2
        #C = [c1,c2,c3]
        #print(C)

        return np.array([c1,c2,c3])

#function to return the parametric values for a 
#line particle where it enters/exits the detector
#returns the tuple pair of doubles
    def get_intersection(self,p):


        '''get the parametric values of the line where it enters/exits 
        the cyllindrical volume
        p: I3Particle to get the line equation for (i.e. muons)
        returns: the solution of the quadratic equation
        '''
        #solve the quadratic equation to get the line intersecting circle in X-Y plane
        sol = np.roots(self.coefficient(p))
        #print(sol)
        assert (len(sol)==2 or len(sol)==0)#making sure roots are working properly
        if len(sol)==2:
            #print(sol)
            if np.iscomplex(sol).any():#discard if imaginary solutions
                return None
            t1=min(sol)
            t2=max(sol)
            #print(t1,t2)
            assert (t1!=t2), f'Scenario where entry and exit point are the same: {p},{t1,t2}'
            if t1>0 and t2>0:#event vertex outside the detector radius in X-Y plane
                zmin=p.pos.z+t1*p.dir.z #height at entry point
                zmax=p.pos.z+t2*p.dir.z #height at exit point
                #Check if first solution on the curved surface
                if abs(zmin)<=self.h_up and abs(zmax)<=self.h_up:#both intersect on the curved surface
                    return (t1,t2)
                elif abs(zmin)>self.h_up and abs(zmax)<=self.h_up:#exits on the curved surface,
                    new_t1 = (np.sign(zmin)*self.h_up-p.pos.z)/p.dir.z #enters from top/bottom planes
                    assert(t1<new_t1<=t2), f'Check for Bug 1: {p},{t1,t2}'
                    return (new_t1,t2)
                elif abs(zmin)<=self.h_up and abs(zmax)>self.h_up:#enters on the curved surface
                    new_t2 = (np.sign(zmax)*self.h_up-p.pos.z)/p.dir.z
                    assert(t1<=new_t2<t2), f'Check for Bug 2: {p},{t1,t2}'
                    return (t1,new_t2)
                elif abs(zmin)>self.h_up and abs(zmax)>self.h_up:#neither enters nor exits on curved surface
                    new_t1 = (np.sign(zmin)*self.h_up-p.pos.z)/p.dir.z
                    new_t2 = (np.sign(zmax)*self.h_up-p.pos.z)/p.dir.z
                    if zmin*zmax>0: return None #track does not enter/exit the volume
                    assert (t1<new_t1<=new_t2<t2), f'Check for Bug 3: {p},{t1,t2}'
                    return (new_t1,new_t2)
                else:#Unphysical check for bugs if condition comes here
                    assert False, f'Check for Bug 4: {p},{t1,t2}'
            if t1<=0 and t2>0:#vertex within the radius of X-Y
                zmax=p.pos.z+t2*p.dir.z
                if abs(p.pos.z)<=self.h_up and abs(zmax)<=self.h_up:#vertex within the detector and exits on the curved surface
                    return (0,t2)
                elif abs(p.pos.z)<=self.h_up and abs(zmax)>self.h_up:#vertex within the detecto
                    new_t2 = (np.sign(zmax)*self.h_up-p.pos.z)/p.dir.z
                    assert (0.<=new_t2<t2), f'Check for Bug 5: {p},{t1,t2}'
                    return (0.,new_t2)
                elif abs(p.pos.z)>self.h_up and abs(zmax)<=self.h_up:#vertex outside the detector and exits on the curved surface
                    new_t1=(np.sign(p.pos.z)*self.h_up-p.pos.z)/p.dir.z
                    assert (0.<new_t1<=t2), f'Check for Bug 6: {p},{t1,t2}'
                    return (new_t1,t2)
                elif abs(p.pos.z)>self.h_up and abs(zmax)>self.h_up:#vertex outside the detector
                    new_t1=(np.sign(p.pos.z)*self.h_up-p.pos.z)/p.dir.z
                    new_t2=(np.sign(zmax)*self.h_up-p.pos.z)/p.dir.z
                    if p.pos.z*zmax>0: return None #track does not enter/exit the detector
                    assert (0.<new_t1<=new_t2<t2), f'Check for Bug 7: {p},{t1,t2}'
                    return (new_t1,new_t2)
                else:
                    assert False, f'Check for Bug 8: {p},{t1,t2}'


            if t2<0:#Does not enter the detector
                return None

        if len(sol)==0:#straight upgoing/downgoing track

            if np.sqrt(p.pos.x**2+p.pos.y**2)<=self.rad:

                new_t1 = (self.h_dn-p.pos.z)/p.dir.z

                new_t2 = (self.h_up-p.pos.z)/p.dir.z

                if 0.<new_t1<new_t2:

                    return (new_t1,new_t2)

                elif 0.<new_t2<new_t1:

                    return (new_t2,new_t1)
                elif new_t1<0.<new_t2:

                    return (0.,new_t2)

                elif new_t2<0.<new_t1:

                    return (0.,new_t1)

                elif new_t1<0 and new_t2<0:

                    return None

                else:

                    assert False, f'Check for Bug 9: {p},{t1,t2}'

            else:

                return None

        return None

#the following function checks the solution with track length to return
#physical values for the track segment inside the detector
    def get_segment(self,p):

        sol = self.get_intersection(p)
        #print(sol)
        if sol==None:

            return (0.,0.)

        t1,t2=sol

        if t1==t2:

            return (0.,0.)

        assert (t1<=t2), f'Error in intersection calculation {t1,t2}'

        if p.length>t2:

            return (t1,t2)

        elif p.length>t1 and p.length<=t2:

            return (t1,p.length)

        elif p.length<=t1:

            return (0,0)
        else:

            assert False, f'Check for Bug 10: {p},{t1,t2}'


    def DAQ(self,frame):

        distance_within = dataclasses.I3Double()

        inmuon = frame[self.inputmap]

        ip,fp = self.get_segment(inmuon[1])

        #print(ip,fp)
        length = fp - ip


        #print(length)
        if length < self.track:
            return
        else:
            distance_within = dataclasses.I3Double(length)
        #dis = list()
        #dis.append(length)
        #print(dis)
        #distance_within = dis
        #l = dataclasses.I3MapKeyVectorDouble()
        #l = dis
        #print(l)
            frame['length'] = distance_within
        #print(frame['length'])
        #frame[self.outputmap] = inmuon
        #print(frame[self.outputmap])
        self.PushFrame(frame)
