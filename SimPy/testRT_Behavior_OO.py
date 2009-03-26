#!/usr / bin / env python
from SimPy.SimulationRT import *
"""testRT_Behavior_OO.py
Tests SimulationRT for degree to which simulation time
and wallclock time can be synchronized.

OO API.
"""
# $Revision$ $Date$

print "Under test: SimulationRT.py"
__version__ = '2.0 $Revision$ $Date$ '
print 'testRT_Behavior.py %s'%__version__

class Ticker(Process):
    def tick(self):
        self.timing = []
        while True:
            yield hold,self,1
            tSim = self.sim.now()
            tRT = self.sim.rtnow()
            self.timing.append((tSim,tRT))
            
s=SimulationRT()
s.initialize()
t=Ticker(sim=s)
s.activate(t,t.tick())
s.simulate(until=10,real_time=True,rel_speed=1)

print "Speed ratio set: 1"
print "------------------"
for tSim,tRT in t.timing:
    print "tSim:%s, tRT:%s, speed ratio:%s"%(tSim,tRT,tSim/tRT)
      
s1=SimulationRT()
s1.initialize()
t=Ticker(sim=s1)
s1.activate(t,t.tick())
s1.simulate(until=10,real_time=True,rel_speed=5)

print
print "Speed ratio set: 5"
print "------------------"
for tSim,tRT in t.timing:
    print "tSim:%s, tRT:%s, speed ratio:%s"%(tSim,tRT,tSim/tRT)
