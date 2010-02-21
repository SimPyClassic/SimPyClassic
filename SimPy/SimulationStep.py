#!/usr / bin / env python
# $Revision$ $Date$ kgm
"""SimulationStep 2.1 Supports stepping through SimPy simulation event - by - event.
Based on generators (Python 2.3 and later; not 3.0)

LICENSE:
Copyright (C) 2002, 2005, 2006, 2007, 2008  Klaus G. Muller, Tony Vignaux
mailto: kgmuller@xs4all.nl and Tony.Vignaux@vuw.ac.nz

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

**Change history:**

    Started out as SiPy 0.9
    
    5 / 9/2002: SiPy 0.9.1
    
        - Addition of '_cancel' method in class Process and supporting '_unpost' method in 
          class __Evlist.
        
        - Removal of redundant 'Action' method in class Process.
        
    12 / 9/2002:
    
        - Addition of resource class
        
        - Addition of '_request' and '_release' coroutine calls
        
    15 / 9/2002: moved into SimPy package
    
    16 / 9/2002:
        - Resource attributes fully implemented (resources can now have more
          than 1 shareable resource units)
        
    17 / 9/2002:
    
        - corrected removal from waitQ (Vignaux)
        
    17 / 9/2002:
    
        - added test for queue discipline in 'test_demo()'. Must be FIFO
        
    26 / 9/02: Version 0.2.0
    
        - cleaned up code; more consistent naming
        
        - prefixed all Simulation - private variable names with '_'.
        
        - prefixed all class - private variable names with '__'.
        
        - made normal exit quiet (but return message from scheduler()
        
    28 / 9/02:
    
        - included stopSimulation()
        
    15 / 10 / 02: Simulation version 0.3
    
        - Version printout now only if __TESTING
        
        - '_stop' initialized to True by module load, and set to False in 
      initialize()
        
        - Introduced 'simulate(until = 0)' instead of 'scheduler(till = 0)'. 
      Left 'scheduler()' in for backward compatibility, but marked
      as deprecated.
        
        - Added attribute 'name' to class Process; default == 'a_process'
        
        - Changed Resource constructor to 
      'def __init__(self, capacity = 1, name = 'a_resource', unitName = 'units''.
        
    13 / 11 / 02: Simulation version 0.6
    
        - Major changes to class Resource:
        
            - Added two queue types for resources, FIFO (default) and PriorityQ
            
            - Changed constructor to allow selection of queue type.
            
            - Introduced preemption of resources (to be used with PriorityQ
              queue type)
            
            - Changed constructor of class Resource to allow selection of preemption
            
            - Changes to class Process to support preemption of service
            
            - Cleaned up 'simulate' by replacing series of if - statements by dispatch table.

    19 / 11 / 02: Simulation version 0.6.1
        - Changed priority schemes so that higher values of Process 
          attribute 'priority' represent higher priority.

    20 / 11 / 02: Simulation version 0.7
        - Major change of priority approach:

            - Priority set by 'yield request, self, res, priority'

            - Priority of a Process instance associated with a specific 
              resource

    25 / 11 / 02: Simulation version 0.7.1

        - Code cleanup and optimization

        - Made process attributes remainService and preempted private 
         (_remainService and _preempted)

    11 / 12 / 2002: First process interrupt implementation

        - Addition of user methods 'interrupt' and 'resume'

        - Significant code cleanup to maintain process state

    20 / 12 / 2002: Changes to 'interrupt'; addition of boolean methods to show
                     process states

    16 / 3/2003: Changed hold (allowing posting events past _endtime)
    
    18 / 3/2003: Changed _nextev to prevent _t going past _endtime

    23 / 3/2003: Introduced new interrupt construct; deleted 'resume' method
    
    25 / 3/2003: Expanded interrupt construct:
    
        - Made 'interrupt' a method  of Process

        - Added 'interruptCause' as an attribute of an interrupted process

        - Changed definition of 'active' to 
         'self._nextTime <> None and not self._inInterrupt'

        - Cleaned up test_interrupt function

    30 / 3/2003: Modification of 'simulate':

        - error message if 'initialize' not called (fatal)

        - error message if no process scheduled (warning)

        - Ensured that upon exit from 'simulate', now() == _endtime is 
          always valid

    2 / 04 / 2003:

        - Modification of 'simulate': leave _endtime alone (undid change
          of 30 Mar 03)

        - faster '_unpost'

    3 / 04 / 2003: Made 'priority' private ('_priority')

    4 / 04 / 2003: Catch activation of non - generator error

    5 / 04 / 2003: Added 'interruptReset()' function to Process.

    7 / 04 / 2003: Changed '_unpost' to ensure that process has
                   _nextTime == None (is passive) afterwards.

    8 / 04 / 2003: Changed _hold to allow for 'yield hold, self' 
                   (equiv to 'yield hold, self, 0')

    10 / 04 / 2003: Changed 'cancel' syntax to 'Process().cancel(victim)'

    12 / 5/2003: Changed eventlist handling from dictionary to bisect
    
    9 / 6/2003: - Changed eventlist handling from pure dictionary to bisect-
                sorted 'timestamps' list of keys, resulting in greatly 
                improved performance for models with large
                numbers of event notices with differing event times.
                =========================================================
                This great change was suggested by Prof. Simon Frost. 
                Thank you, Simon! This version 1.3 is dedicated to you!
                =========================================================
              - Added import of Lister which supports well - structured 
                printing of all attributes of Process and Resource instances.

    Oct 2003: Added monitored Resource instances (Monitors for activeQ and waitQ)

    13 Dec 2003: Merged in Monitor and Histogram

    27 Feb 2004: Repaired bug in activeQ monitor of class Resource. Now actMon
                 correctly records departures from activeQ.
                 
    19 May 2004: Added erroneously omitted Histogram class.

    5 Sep 2004: Added SimEvents synchronization constructs
    
    17 Sep 2004: Added waituntil synchronization construct
    
    01 Dec 2004: SimPy version 1.5
                 Changes in this module: Repaired SimEvents bug re proc.eventsFired
                 
    12 Jan 2005: SimPy version 1.5.1
                 Changes in this module: Monitor objects now have a default name
                                         'a_Monitor'
                                         
    29 Mar 2005: Start SimPy 1.6: compound 'yield request' statements
    
    05 Jun 2005: Fixed bug in _request method -- waitMon did not work properly in
                 preemption case
                 
    09 Jun 2005: Added test in 'activate' to see whether 'initialize()' was called first.
    
    23 Aug 2005: - Added Tally data collection class
                 - Adjusted Resource to work with Tally
                 - Redid function allEventNotices() (returns prettyprinted string with event
                   times and names of process instances
                 - Added function allEventTimes (returns event times of all scheduled events)
                 
    16 Mar 2006: - Added Store and Level classes
                 - Added 'yield get' and 'yield put'
                 
    10 May 2006: - Repaired bug in Store._get method
                 - Repaired Level to allow initialBuffered have float value
                 - Added type test for Level get parameter 'nrToGet'
                 
    06 Jun 2006: - To improve pretty - printed output of 'Level' objects, changed attribute
                   _nrBuffered to nrBuffered (synonym for amount property)
                 - To improve pretty - printed output of 'Store' objects, added attribute
                   buffered (which refers to _theBuffer)
                   
    25 Aug 2006: - Start of version 1.8
                 - made 'version' public
                 - corrected condQ initialization bug
                 
    30 Sep 2006: - Introduced checks to ensure capacity of a Buffer > 0
                 - Removed from __future__ import (so Python 2.3 or later needed)
                
    15 Oct 2006: - Added code to register all Monitors and all Tallies in variables
                   'allMonitors' and 'allTallies'
                 - Added function 'startCollection' to activate Monitors and Tallies at a
                   specified time (e.g. after warmup period)
                 - Moved all test / demo programs to after 'if __name__ == '__main__':'.
                
    17 Oct 2006: - Added compound 'put' and 'get' statements for Level and Store.
    
    18 Oct 2006: - Repaired bug: self.eventsFired now gets set after an event fires
                   in a compound yield get / put with a waitevent clause (reneging case).
                   
    21 Oct 2006: - Introduced Store 'yield get' with a filter function.
                
    22 Oct 2006: - Repaired bug in prettyprinting of Store objects (the buffer 
                   content==._theBuffer was not shown) by changing ._theBuffer 
                   to .theBuffer.
                
    04 Dec 2006: - Added printHistogram method to Tally and Monitor (generates
                   table - form histogram)
                    
    07 Dec 2006: - Changed the __str__ method of Histogram to print a table 
                   (like printHistogram).
    
    18 Dec 2006: - Added trace printing of Buffers' 'unitName' for yield get and put.
    
    09 Jun 2007: - Cleaned out all uses of 'object' to prevent name clash.
    
    18 Nov 2007: - Start of 1.9 development
                 - Added 'start' method (alternative to activate) to Process
                 
    22 Nov 2007: - Major change to event list handling to speed up larger models:
                    * Drop dictionary
                    * Replace bisect by heapq
                    * Mark cancelled event notices in unpost and skip them in
                      nextev (great idea of Tony Vignaux))
                      
    4 Dec 2007: - Added twVariance calculation for both Monitor and Tally (gav)
    
    5 Dec 2007: - Changed name back to timeVariance (gav)
    
    1 Mar 2008: - Start of 1.9.1 bugfix release
                - Delete circular reference in Process instances when event 
                  notice has been processed (caused much circular garbage)
                - Added capability for multiple preempts of a process
                
    10 Aug 2008: - Removed most classes / methods and imported them from
                   Simulation.py instead (Stefan Scherfke)
                 - Moved remaining functions to SimulationStep and added some
                   methods for backward compatibility
                   
    10 Jan 2010: - Implemented refactoring proposed by Stefan Scherfke:
                   * removed duplication of code with Simulation.py
                 - Removed simulateStep function/method                   
    
"""
from SimPy.Simulation import *

__TESTING = False
version = __version__ = '2.0 $Revision$ $Date$'
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
