#!/usr / bin / env python
from SimPy.SimulationRT import *
"""testRT_Behavior_OO.py
Tests SimulationRT for degree to which simulation time
and wallclock time can be synchronized.
"""
# $Revision: $ $Date:  $

print "Under test: SimulationRT.py %s"%simulationVersion
__version__ = '2.0 $Revision:  $ $Date: $ '
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

for obs in t.timing:
    print obs,obs[0]/obs[1]
      
s1=SimulationRT()
s1.initialize()
t=Ticker(sim=s1)
s1.activate(t,t.tick())
s1.simulate(until=10,real_time=True,rel_speed=5)

for obs in t.timing:
    print obs,obs[0]/obs[1]
