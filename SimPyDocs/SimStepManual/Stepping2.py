from SimPy.SimulationStep import *

def callbackUserControl():
    """Allows user to control stepping
    """
    a=raw_input("[Time=%s] Select one: End run (e), Continue stepping (s), Run to end (r)= "%now())
    if a=="e":
        stopSimulation()
    elif a=="s":
        return
    else:
        stopStepping()
        
class Man(Process):
    def walk(self):
        print "got up"
        yield hold,self,1
        print "got to door"
        yield hold,self,10
        print "got to mail box"
        yield hold,self,10
        print "got home again"
#allow user control
initialize()
otto=Man()
activate(otto,otto.walk())
startStepping()
simulate(callback=callbackUserControl,until=100)


raw_input()


