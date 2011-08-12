"""
A utility module for stepping through the events of a simulation
under user control.

REQUIRES SimPy 2.1
"""
from SimPy.SimulationTrace import *
           
def stepper(whichsim):
    evlist = whichsim._timestamps
    while True:
        if not evlist:
            print "No more events."
            break
        tEvt = evlist[0][0]
        who = evlist[0][2]
        while evlist[0][3]: #skip cancelled event notices
            whichsim.step()
        print "\nTime now: %s, next event at: %s for process: %s " %(whichsim.now(),tEvt,who.name)

        cmd = raw_input(
              "'s' next event,'r' run to end,'e' to end run, " 
              "<time> skip to event at <time>, 'l' show eventlist, 'p<name>' skip to event for <name>: ") 
        try:
            nexttime = float(cmd)
            while whichsim.peek() < nexttime:
                whichsim.step()
        except:
            if cmd == 's':
                whichsim.step()
            elif cmd == 'r':
                break
            elif cmd == 'e':
                stopSimulation()
                break
            elif cmd == 'l':
                print "Events scheduled: \n%s"%whichsim.allEventNotices() 
            elif cmd[0] == 'p':
                while evlist and evlist[0][2].name <> cmd[1:]:
                    whichsim.step()                    
            else:
                print "%s not a valid command" % cmd


if __name__ == "__main__":
    import random as r
    r.seed(1234567)

    class Test(Process):
        def run(self):
            while self.sim.now() < until:
                yield hold,self,r.uniform(1,10)
                
    class Waiter(Process):
        def run(self,evt):
            def gt30():
                return self.sim.now() > 30 
                
            yield waituntil,self,gt30
            print "now() is past 30"
            self.sim.stopSimulation()
            
    until = 100
    s = SimulationTrace()
    s.initialize()
    evt = SimEvent(sim=s)
    t=Test("Test1", sim=s)
    s.activate(t,t.run())
    t2=Test("Test2", sim=s)
    s.activate(t2,t2.run())
    w=Waiter("Waiter", sim=s)
    s.activate(w,w.run(evt=evt))
    stepper(whichsim=s)