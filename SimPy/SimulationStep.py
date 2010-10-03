#!/usr / bin / env python
# coding=utf-8
# $Revision$ $Date$ kgm
"""SimulationStep 2.1 Supports stepping through SimPy simulation event - by - event.
Based on generators (Python 2.3 and later; not 3.0)

LICENSE:
Copyright (C) 2002, 2005, 2006, 2007, 2008, 2009, 2010  Klaus G. Muller, Tony Vignaux
mailto: kgmuller at xs4all.nl and Tony.Vignaux at vuw.ac.nz

    This library is free software; you can redistribute it and / or
    modify it under the terms of the GNU Lesser General Public
    License as published by the Free Software Foundation; either
    version 2.1 of the License, or (at your option) any later version.

    This library is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public
    License along with this library; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111 - 1307  USA
END OF LICENSE
"""
from SimPy.Simulation import *

__TESTING = False
version = __version__ = '2.1 $Revision$ $Date$'
if __TESTING: 
    print 'SimPy.SimulationStep %s' %__version__,
    if __debug__:
        print '__debug__ on'
    else:
        print

_step = False

class SimulationStep(Simulation):
    def __init__(self):
        Simulation.__init__(self)
        self._step = False

    def initialize(self):
        Simulation.initialize(self)
        self._step = False

    def startStepping(self):
        """Application function to start stepping through simulation."""
        self._step = True

    def stopStepping(self):
        """Application function to stop stepping through simulation."""
        self._step = False

    def step(self):
        Simulation.step(self)
        if self._step: self.callback()

    def simulate(self, callback=lambda: None, until=0):
        """
        Simulates until simulation time reaches ``until``. After processing each
        event, ``callback`` will be invoked if stepping has been enabled with
        :meth:`~SimPy.SimulationStep.startStepping`.
        """
        self.callback = callback
        return Simulation.simulate(self, until)

# For backward compatibility
Globals.sim = SimulationStep()

def startStepping():
    Globals.sim.startStepping()
    
def stopStepping():
    Globals.sim.stopStepping()
    
peek = Globals.sim.peek

step = Globals.sim.step

allMonitors = Globals.sim.allMonitors

allTallies = Globals.sim.allTallies
    
def simulate(callback = lambda :None, until = 0):
    return Globals.sim.simulate(callback = callback, until = until)

# End backward compatibility
    

################### end of Simulation module
    
if __name__ == '__main__':
    print 'SimPy.SimulationStep %s' %__version__
    ################### start of test / demo programs
    
    def askCancel():
        a = raw_input('[Time=%s] End run (e), Continue stepping (s), Run to end (r)'%now())
        if a == 'e':
            stopSimulation()
        elif a == 's':
            return
        else:
            stopStepping()
    
    def test_demo():
        class Aa(Process):
            sequIn = []
            sequOut = []
            def __init__(self, holdtime, name):
                Process.__init__(self, name)
                self.holdtime = holdtime
    
            def life(self, priority):
                for i in range(1):
                    Aa.sequIn.append(self.name)
                    print now(),rrr.name, 'waitQ:', len(rrr.waitQ),'activeQ:',\
                          len(rrr.activeQ)
                    print 'waitQ: ',[(k.name, k._priority[rrr]) for k in rrr.waitQ]
                    print 'activeQ: ',[(k.name, k._priority[rrr]) \
                               for k in rrr.activeQ]
                    assert rrr.n + len(rrr.activeQ) == rrr.capacity, \
                           'Inconsistent resource unit numbers'
                    print now(),self.name, 'requests 1 ', rrr.unitName
                    yield request, self, rrr, priority
                    print now(),self.name, 'has 1 ', rrr.unitName
                    print now(),rrr.name, 'waitQ:', len(rrr.waitQ),'activeQ:',\
                          len(rrr.activeQ)
                    print now(),rrr.name, 'waitQ:', len(rrr.waitQ),'activeQ:',\
                          len(rrr.activeQ)
                    assert rrr.n + len(rrr.activeQ) == rrr.capacity, \
                           'Inconsistent resource unit numbers'
                    yield hold, self, self.holdtime
                    print now(),self.name, 'gives up 1', rrr.unitName
                    yield release, self, rrr
                    Aa.sequOut.append(self.name)
                    print now(),self.name, 'has released 1 ', rrr.unitName
                    print 'waitQ: ',[(k.name, k._priority[rrr]) for k in rrr.waitQ]
                    print now(),rrr.name, 'waitQ:', len(rrr.waitQ),'activeQ:',\
                          len(rrr.activeQ)
                    assert rrr.n + len(rrr.activeQ) == rrr.capacity, \
                           'Inconsistent resource unit numbers'
    
        class Destroyer(Process):
            def __init__(self):
                Process.__init__(self)
    
            def destroy(self, whichProcesses):
                for i in whichProcesses:
                    Process().cancel(i)
                yield hold, self, 0
    
        class Observer(Process):
            def __init__(self):
                Process.__init__(self)
    
            def observe(self, step, processes, res):
                while now() < 11:
                    for i in processes:
                        print ' %s %s: act:%s, pass:%s, term: %s, interr:%s, qu:%s'\
                              %(now(),i.name, i.active(),i.passive(),i.terminated()\
                            ,i.interrupted(),i.queuing(res))
                    print
                    yield hold, self, step
    
        class UserControl(Process):
            def letUserInteract(self, when):
                yield hold, self, when
                startStepping()
                        
        print '****First case == priority queue, resource service not preemptable'
        initialize()
        rrr = Resource(5, name = 'Parking', unitName = 'space(s)', qType = PriorityQ,
                     preemptable = 0)
        procs = []
        for i in range(10):
            z = Aa(holdtime = i, name = 'Car ' + str(i))
            procs.append(z)
            activate(z, z.life(priority = i))
        o = Observer()
        activate(o, o.observe(1, procs, rrr))
        startStepping()
        a = simulate(until = 10000, callback = askCancel)
        print 'Input sequence: ', Aa.sequIn
        print 'Output sequence: ', Aa.sequOut
    
        print '\n****Second case == priority queue, resource service preemptable'
        initialize()
        rrr = Resource(5, name = 'Parking', unitName = 'space(s)', qType = PriorityQ,
                     preemptable = 1)
        procs = []
        for i in range(10):
            z = Aa(holdtime = i, name = 'Car ' + str(i))
            procs.append(z)
            activate(z, z.life(priority = i))
        o = Observer()
        activate(o, o.observe(1, procs, rrr))
        u = UserControl()
        activate(u, u.letUserInteract(4))
        Aa.sequIn = []
        Aa.sequOut = []
        a = simulate(askCancel, until = 10000)
        print a
        print 'Input sequence: ', Aa.sequIn
        print 'Output sequence: ', Aa.sequOut   
    
    def test_interrupt():
        class Bus(Process):
            def __init__(self, name):
                Process.__init__(self, name)
    
            def operate(self, repairduration = 0):
                print now(),'>> %s starts' % (self.name)
                tripleft = 1000
                while tripleft > 0:
                    yield hold, self, tripleft
                    if self.interrupted():
                        print 'interrupted by %s' %self.interruptCause.name
                        print '%s: %s breaks down ' %(now(),self.name)
                        tripleft = self.interruptLeft
                        self.interruptReset()
                        print 'tripleft ', tripleft
                        reactivate(br, delay = repairduration) # breakdowns only during operation
                        yield hold, self, repairduration
                        print now(),' repaired'
                    else:
                        break # no breakdown, ergo bus arrived
                print now(),'<< %s done' % (self.name)
    
        class Breakdown(Process):
            def __init__(self, myBus):
                Process.__init__(self, name = 'Breakdown ' + myBus.name)
                self.bus = myBus
    
            def breakBus(self, interval):
    
                while True:
                    yield hold, self, interval
                    if self.bus.terminated(): break
                    self.interrupt(self.bus)
                    
        print'\n\n+++test_interrupt'
        initialize()
        b = Bus('Bus 1')
        activate(b, b.operate(repairduration = 20))
        br = Breakdown(b)
        activate(br, br.breakBus(200))
        startStepping()
        simulate(until = 4000)
    
        
    def testSimEvents():
        class Waiter(Process):
            def waiting(self, theSignal):
                while True:
                    yield waitevent, self, theSignal
                    print '%s: process \'%s\' continued after waiting for %s' % (now(),self.name, theSignal.name)
                    yield queueevent, self, theSignal
                    print '%s: process \'%s\' continued after queueing for %s' % (now(),self.name, theSignal.name)
                    
        class ORWaiter(Process):
            def waiting(self, signals):
                while True:
                    yield waitevent, self, signals
                    print now(),'one of %s signals occurred' % [x.name for x in signals]
                    print '\t%s (fired / param)'%[(x.name, x.signalparam) for x in self.eventsFired]
                    yield hold, self, 1
                    
        class Caller(Process):
            def calling(self):
                while True:
                    signal1.signal('wake up!')
                    print '%s: signal 1 has occurred'%now()
                    yield hold, self, 10
                    signal2.signal('and again')
                    signal2.signal('sig 2 again')
                    print '%s: signal1, signal2 have occurred'%now()
                    yield hold, self, 10
        print'\n+++testSimEvents output'
        initialize()
        signal1 = SimEvent('signal 1')
        signal2 = SimEvent('signal 2')
        signal1.signal('startup1')
        signal2.signal('startup2')
        w1 = Waiter('waiting for signal 1')
        activate(w1, w1.waiting(signal1))
        w2 = Waiter('waiting for signal 2')
        activate(w2, w2.waiting(signal2))
        w3 = Waiter('also waiting for signal 2')
        activate(w3, w3.waiting(signal2))
        w4 = ORWaiter('waiting for either signal 1 or signal 2')
        activate(w4, w4.waiting([signal1, signal2]),prior = True)
        c = Caller('Caller')
        activate(c, c.calling())
        print simulate(until = 100)
        
    def testwaituntil():
        """
        Demo of waitUntil capability.
    
        Scenario:
        Three workers require sets of tools to do their jobs. Tools are shared, scarce
        resources for which they compete.
        """
    
    
        class Worker(Process):
            def __init__(self, name, heNeeds = []):
                Process.__init__(self, name)
                self.heNeeds = heNeeds
            def work(self):
            
                def workerNeeds():
                    for item in self.heNeeds:
                        if item.n == 0:
                            return False
                    return True
                         
                while now() < 8 * 60:
                    yield waituntil, self, workerNeeds
                    for item in self.heNeeds:
                        yield request, self, item
                    print '%s %s has %s and starts job' % (now(),self.name,
                        [x.name for x in self.heNeeds])
                    yield hold, self, random.uniform(10, 30)
                    for item in self.heNeeds:
                        yield release, self, item
                    yield hold, self, 2 #rest
      
        print '\n+++ nwaituntil demo output'
        initialize()
        brush = Resource(capacity = 1, name = 'brush')
        ladder = Resource(capacity = 2, name = 'ladder')
        hammer = Resource(capacity = 1, name = 'hammer')
        saw = Resource(capacity = 1, name = 'saw')
        painter = Worker('painter',[brush, ladder])
        activate(painter, painter.work())
        roofer = Worker('roofer',[hammer, ladder, ladder])
        activate(roofer, roofer.work())
        treeguy = Worker('treeguy',[saw, ladder])
        activate(treeguy, treeguy.work())
        for who in (painter, roofer, treeguy):
            print '%s needs %s for his job' % (who.name,[x.name for x in who.heNeeds])
        print
        print simulate(until = 9 * 60)    
        
        
        
        
    test_demo()
    test_interrupt()
    testSimEvents()
    testwaituntil()   
