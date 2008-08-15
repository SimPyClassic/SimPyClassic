## Stepping1.py
from __future__ import generators
from SimPy.SimulationStep import *

def callbackTimeTrace():
    """Prints event times
    """
    print "at time=%s"%now()
        
class Man(Process):
    def walk(self):
        print "got up"
        yield hold,self,1
        print "got to door"
        yield hold,self,10
        print "got to mail box"
        yield hold,self,10
        print "got home again"
        
#trace event times
initialize()
otto=Man()
activate(otto,otto.walk())
startStepping()
simulate(callback=callbackTimeTrace,until=100)
