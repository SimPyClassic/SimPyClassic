# coding=utf-8
"""
This is a small utility for interactively stepping through a simulation.

Usage:
    import stepping
    (simulation model)
    stepping.stepping(Globals) # instead of 'simulate(until = endtime)
"""
# $Revision: 464 $ $Date: 2010-04-05 05:59:53 +0200 (Mo, 05 Apr 2010) $ kgm
# SimPy version: 2.1
def stepping(glob):
    asim = glob.sim
    help = {'s':"next event",'r':"run to end",'e':"end run",
           '<time>':"skip to event at <time>",'l':"show eventlist",
           'p<name>':"skip to event for <name>",'h':"help"}
    evlist = asim._timestamps
    while True:
        if not evlist:
            print "No more events at t=%s"%asim.now()
            break
        tEvt = evlist[0][0]
        who = evlist[0][2]
        while evlist[0][3]: #skip cancelled event notices
            step()
        print "\nTime now: %s, next event at: t=%s for process: %s "\
              %(asim.now(),tEvt,who.name)

        while True:
            cmd = raw_input("Command ('h' for help): ")
            if cmd == "h":
                for i in help:
                    print i, ":", help[i]
            else:
                break
        try:
            nexttime = float(cmd)
            while asim.peek() < nexttime:
                asim.step()
        except:
            if cmd == 's':
                asim.step()
            elif cmd == 'r':
                while evlist:
                    asim.step()
                print "Run ended at t=%s"%asim.now()
                break   
            elif cmd == 'e':
                asim.stopSimulation()
                break
            elif cmd == 'l':
                print "Events scheduled: \n%s"%asim.allEventNotices() 
            elif cmd[0] == 'p':
                while evlist and evlist[0][2].name <> cmd[1:]:
                    asim.step()                    
            else:
                print "%s not a valid command" % cmd
                
if __name__ == "__main__":
    from SimPy.SimulationTrace import *
    
    class Car(Process):
        def drive(self, speed, howlong):
            going = speed
            yield hold,self,howlong
            going = 0
        
    initialize()
    b = Car(name = "Beemer")
    activate(b, b.drive(speed = 180, howlong = 45))
    c = Car(name = "Caddy")
    activate(c, c.drive(speed = 120, howlong = 120), at = 25)
    stepping(Globals)
    