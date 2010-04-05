"""
A utility module for stepping through the events of a simulation
under user control.

REQUIRES SimPy 2.1
"""
from SimPy.SimulationTrace import *
           
def stepper():
    evlist = Globals.sim._timestamps
    while True:
        if not evlist:
            print "No more events."
            break
        tEvt = evlist[0][0]
        who = evlist[0][2]
        while evlist[0][3]: #skip cancelled event notices
            step()
        print "\nTime now: %s, next event at: %s for process: %s " %(now(),tEvt,who.name)#peekAll()[0],peekAll()[1].name)

        cmd = raw_input(
              "'s' next event,'r' run to end,'e' to end run, " 
              "<time> skip to event at <time>, 'l' show eventlist, 'p<name>' skip to event for <name>: ") 
        try:
            nexttime = float(cmd)
            while peek() < nexttime:
                step()
        except:
            if cmd == 's':
                step()
            elif cmd == 'r':
                break
            elif cmd == 'e':
                stopSimulation()
                break
            elif cmd == 'l':
                print "Events scheduled: \n%s"%allEventNotices() 
            elif cmd[0] == 'p':
                while evlist and evlist[0][2].name <> cmd[1:]:
                    step()                    
            else:
                print "%s not a valid command" % cmd


if __name__ == "__main__":
    import random as r
    r.seed(1234567)

    class Test(Process):
        def run(self):
            while now() < until:
                yield hold,self,r.uniform(1,10)
                
    class Waiter(Process):
        def run(self,evt):
            def gt30():
                return now()>30
              
            yield waituntil,self,gt30
            print "now() is past 30"
            stopSimulation()
            
    until = 100
    initialize()
    evt = SimEvent()
    t=Test("Test1")
    activate(t,t.run())
    t2=Test("Test2")
    activate(t2,t2.run())
    w=Waiter("Waiter")
    activate(w,w.run(evt=evt))
    stepper()