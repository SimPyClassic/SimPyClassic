#!/usr / bin / env python
# coding=utf-8
from SimPy.Simulation  import *
from SimPy.MonitorTest import *
import unittest
# $Revision$ $Date$
"""testSimPy_simident.py
SimPy version 2.1
Unit tests of checks of correct use of sim parameter. 
2.1 introduces checks that two entities involved in a yield (e.g.
a Process and a Resource) belong to the same Simulation instance.

NOTE: This unit test set only works if __debug__ == True. If
Python is called with the -O or -OO parameter, the checks are not
being executed.

#'$Revision$ $Date$ kgm'

"""

simulationVersion=version
print "Under test: Simulation.py %s"%simulationVersion
__version__ = '2.1 $Revision$ $Date$ '
print 'testSimpy_simident.py %s'%__version__
if not __debug__:
    print "Unit tests not executed -- run in __debug__ mode."
    sys.exit()
    
class Activatetest(Process):
    """Used in testActivate.
    """
    def run(self):
        yield hold,self,0
        
class Requesttest(Process):
    """Used in testRequest.
    """
    def run(self,res):
        yield request,self,res
        
class PutStoretest(Process):
    """Used in testPutStore.
    """
    def run(self,store):
        yield put,self,store,[1]
        
class GetStoretest(Process):
    """Used in testGetStore.
    """
    def run(self,store):
        yield get,self,store,1

class PutLeveltest(Process):
    """Used in testPutLevel.
    """
    def run(self,level):
        yield put,self,level,1
        
class GetLeveltest(Process):
    """Used in testGetLevel.
    """
    def run(self,level):
        yield get,self,level,1  

class Waiteventtest(Process):
    """Used in testWaitevent.
    """
    def run(self,event):
        yield waitevent,self,event
        
class Queueeventtest(Process):
    """Used in testQueueevent.
    """
    def run(self,event):
        yield queueevent,self,event

class makesimtestcase(unittest.TestCase):
    """Tests of checks for identical sim parameters.
    """
    ## -------------------------------------------------------------
    ## Test of "activate" call
    ## -------------------------------------------------------------
    def testActivate(self):
        s = Simulation()
        s.initialize() 
        r = Activatetest(sim=s)
        try:
            activate(r,r.run()) ## missing s.
        except FatalSimerror:
            pass
        else:
            self.fail("expected FatalSimerror")        
        s.simulate(until=1)
    
    ## -------------------------------------------------------------
    ## Test of "yield request,self,res"
    ## -------------------------------------------------------------
    def testRequest(self):
        s = Simulation()
        s.initialize()
        res = Resource( ) # wrong sim  
        r = Requesttest(sim=s)
        s.activate(r,r.run(res = res))
        try:
            s.simulate(until=1)
        except FatalSimerror:
            pass
        else:
            self.fail("expected FatalSimerror")

    ## -------------------------------------------------------------
    ## Test of "yield put,self,store"
    ## -------------------------------------------------------------
    def testPutStore (self):
        s = Simulation()
        s.initialize()
        store = Store( ) # wrong sim  
        r = PutStoretest(sim=s)
        s.activate(r,r.run(store = store))
        try:
            s.simulate(until=1)
        except FatalSimerror:
            pass
        else:
            self.fail("expected FatalSimerror")        
    ## -------------------------------------------------------------
    ## Test of "yield put,self,level"
    ## -------------------------------------------------------------
    def testPutLevel (self):
        s = Simulation()
        s.initialize()
        levl = Level( ) # wrong sim  
        r = PutLeveltest(sim=s)
        s.activate(r,r.run(level = levl))
        try:
            s.simulate(until=1)
        except FatalSimerror:
            pass
        else:
            self.fail("expected FatalSimerror") 

    ## -------------------------------------------------------------
    ## Test of "yield get,self,store"
    ## -------------------------------------------------------------
    def testGetStore(self):
        s = Simulation()
        s.initialize()
        store = Store( ) # wrong sim  
        r = GetStoretest(sim=s)
        s.activate(r,r.run(store = store))
        try:
            s.simulate(until=1)
        except FatalSimerror:
            pass
        else:
            self.fail("expected FatalSimerror") 
            
    ## -------------------------------------------------------------
    ## Test of "yield get,self,level"
    ## -------------------------------------------------------------
    def testGetLevel(self):
        s = Simulation()
        s.initialize()
        levl = Level( ) # wrong sim  
        r = GetLeveltest(sim=s)
        s.activate(r,r.run(level = levl))
        try:
            s.simulate(until=1)
        except FatalSimerror:
            pass
        else:
            self.fail("expected FatalSimerror")   
            
    ## -------------------------------------------------------------
    ## Test of "yield waitevent,self,evt"
    ## -------------------------------------------------------------
    def testWaitevent(self):
        s = Simulation()
        s.initialize()
        evt = SimEvent() ## wrong sim
        w = Waiteventtest(sim = s)
        s.activate(w,w.run(event = evt))
        try:
            s.simulate(until=1)
        except FatalSimerror:
            pass
        else:
            self.fail("expected FatalSimerror")           
        
    ## -------------------------------------------------------------
    ## Test of "yield queueevent,self,evt"
    ## -------------------------------------------------------------
    def testQueueevent(self):
        s = Simulation()
        s.initialize()
        evt = SimEvent() ## wrong sim
        w = Queueeventtest(sim = s)
        s.activate(w,w.run(event = evt))
        try:
            s.simulate(until=1)
        except FatalSimerror:
            pass
        else:
            self.fail("expected FatalSimerror")   

def makesimSuite():
    suite = unittest.TestSuite()
    testRequest =  makesimtestcase('testRequest')
    testActivate = makesimtestcase('testActivate')
    testPutStore = makesimtestcase('testPutStore')
    testPutLevel = makesimtestcase('testPutLevel')
    testGetStore = makesimtestcase('testGetStore')
    testGetLevel = makesimtestcase('testGetLevel')
    testWaitevent = makesimtestcase('testWaitevent')
    testQueueevent = makesimtestcase('testQueueevent')
    
    suite.addTests([testRequest, testActivate, testPutStore, testPutLevel,
                    testGetStore, testGetLevel, testWaitevent, testQueueevent])
    return suite
    
if __name__ == '__main__':
    alltests = unittest.TestSuite((makesimSuite()
                                ))
    runner = unittest.TextTestRunner()
    runner.run(alltests)