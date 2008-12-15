#!/usr / bin / env python
# $Revision$ $Date$ kgm
"""SimulationRT 2.0 Provides synchronization of real time and SimPy simulation time.
Implements SimPy Processes, resources, and the backbone simulation scheduling
by coroutine calls. 
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
    4 / 8/2003: - Experimental introduction of synchronization of simulation
                time and real time (idea of Geoff Jarrad of CSIRO -- thanks,
                Geoff!).
                * Changes made to class EvlistRT, _nextev(), simulate()

    Dec 11, 2003:
            - Updated to Simulation 1.4alpha API

    13 Dec 2003: Merged in Monitor and Histogram

    27 Feb 2004: Repaired bug in activeQ monitor of class Resource. Now actMon
                 correctly records departures from activeQ.

    19 May 2004: Added erroneously omitted Histogram class.

    5 Sep 2004: Added SimEvents synchronization constructs
    
    17 Sep 2004: Added waituntil synchronization construct
    
    28 Sep 2004: Changed handling of real time -- now uses time.clock for Win32, and
                 time.time for all other OS (works better on Linux, Unix).

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
                  
    2 Apr 2008: - Repair of wallclock synchronisation algorithm
    
    10 Aug 2008: - Renamed __Evlist to EvlistRT and let it inherit from
                   Evlist (from Simulation.py) (Stefan Scherfke)
                 - New class SimulationRT contains the old method simulate
                 - Removed everything else and import it from Simulation.py
    
"""
import time

from SimPy.Simulation import *


__TESTING = False
version = __version__ = '2.0 $Revision$ $Date$'
if __TESTING: 
    print 'SimPy.SimulationRT %s' %__version__,
    if __debug__:
        print '__debug__ on'
    else:
        print

        
class EvlistRT(Evlist):
    """Defines event list and operations on it"""
    def __init__(self, sim):
        # always sorted list of events (sorted by time, priority)
        # make heapq
        self.sim = sim
        self.timestamps = []
        self.sortpr = 0  
        self.real_time = False
        self.rel_speed = 1 
        self.rtlast = self.sim.wallclock()
        self.stlast = 0
            
    def _nextev(self):
        """Retrieve next event from event list"""
        noActiveNotice = True
        ## Find next event notice which is not marked cancelled
        while noActiveNotice:
            if self.timestamps:
                 ## ignore priority value         
                (_tnotice, p,nextEvent, cancelled) = hq.heappop(self.timestamps)
                noActiveNotice = cancelled
            else:
                raise Simerror('No more events at time %s' % self.sim._t)
        nextEvent._rec = None
        self.sim._t = _tnotice
        ## Calculate any wait time
        ## event clock time = rtlast + (sim_time - stlast) / rel_speed
        ## delay = (1.0 * earliest / self.rel_speed) - self.sim.rtnow()
        if self.real_time:                                 
##          delay = next_time - self.sim.wallclock()
            delay = (1.0 * self.sim._t / self.rel_speed) - self.sim.rtnow()
            if delay > 0:
                time.sleep(delay)                  
            self.rtlast = self.sim.wallclock()
            self.stlast = self.sim._t
        if self.sim._t > self.sim._endtime:
            self.sim._t = self.sim._endtime
            self.sim._stop = True
            return (None,)
        try:
            resultTuple = nextEvent._nextpoint.next()
        except StopIteration:
            nextEvent._nextpoint = None
            nextEvent._terminated = True
            nextEvent._nextTime = None
            resultTuple = None
        return (resultTuple, nextEvent)


class SimulationRT(Simulation):
    
    def __init__(self):
        if sys.platform == 'win32':  #take care of differences in clock accuracy
            self.wallclock = time.clock
        else:
            self.wallclock = time.time
        self.rtstart = self.wallclock()
        Simulation.__init__(self)
        self.initialize()
        
    def initialize(self):
        Simulation.initialize(self)
        self._e = EvlistRT(self)

    def rtnow(self):
        return self.wallclock() - self.rtstart
        
    def rtset(self, rel_speed = 1):
        """resets the the ratio simulation time over clock time(seconds).
        """
        if _e is None:
            raise FatalSimerror('Fatal SimPy error: Simulation not initialized')
        _e.rel_speed = rel_speed
    
    def simulate(self, until = 0, real_time = False, rel_speed = 1):
        """Schedules Processes / semi - coroutines until time 'until'"""
        
        """Gets called once. Afterwards, co - routines (generators) return by 
        'yield' with a cargo:
        yield hold, self, <delay>: schedules the 'self' process for activation 
                                   after < delay > time units.If <,delay > missing,
                                   same as 'yield hold, self, 0'
                                   
        yield passivate, self    :  makes the 'self' process wait to be re - activated
    
        yield request, self,<Resource > [,<priority>]: request 1 unit from < Resource>
            with < priority > pos integer (default = 0)
    
        yield release, self,<Resource> : release 1 unit to < Resource>
    
        yield waitevent, self,<SimEvent>|[<Evt1>,<Evt2>,<Evt3), . . . ]:
            wait for one or more of several events
            
    
        yield queueevent, self,<SimEvent>|[<Evt1>,<Evt2>,<Evt3), . . . ]:
            queue for one or more of several events
    
        yield waituntil, self, cond : wait for arbitrary condition
    
        yield get, self,<buffer > [,<WhatToGet > [,<priority>]]
            get < WhatToGet > items from buffer (default = 1); 
            <WhatToGet > can be a pos integer or a filter function
            (Store only)
            
        yield put, self,<buffer > [,<WhatToPut > [,priority]]
            put < WhatToPut > items into buffer (default = 1);
            <WhatToPut > can be a pos integer (Level) or a list of objects
            (Store)
    
        EXTENSIONS:
        Request with timeout reneging:
        yield (request, self,<Resource>),(hold, self,<patience>) :
            requests 1 unit from < Resource>. If unit not acquired in time period
            <patience>, self leaves waitQ (reneges).
    
        Request with event - based reneging:
        yield (request, self,<Resource>),(waitevent, self,<eventlist>):
            requests 1 unit from < Resource>. If one of the events in < eventlist > occurs before unit
            acquired, self leaves waitQ (reneges).
            
        Get with timeout reneging (for Store and Level):
        yield (get, self,<buffer>,nrToGet etc.),(hold, self,<patience>)
            requests < nrToGet > items / units from < buffer>. If not acquired < nrToGet > in time period
            <patience>, self leaves < buffer>.getQ (reneges).
            
        Get with event - based reneging (for Store and Level):
        yield (get, self,<buffer>,nrToGet etc.),(waitevent, self,<eventlist>)
            requests < nrToGet > items / units from < buffer>. If not acquired < nrToGet > before one of
            the events in < eventlist > occurs, self leaves < buffer>.getQ (reneges).
    
            
    
        Event notices get posted in event - list by scheduler after 'yield' or by 
        'activate' / 'reactivate' functions.
        
        if real_time == True, the simulation time and real (clock) time get
        synchronized as much as possible. rel_speed is the ratio simulation time
        over clock time(seconds). Example: rel_speed == 100: 100 simulation time units take
        1 second clock time.
        
        """
        global _endtime, _e, _stop, _t, _wustep    
        self._stop = False
    
        if self._e is None:
            raise FatalSimerror('Simulation not initialized')
        self._e.real_time = real_time
        self._e.rel_speed = rel_speed
        self._e.rtlast = self.wallclock()
        self._e.stlast = 0
        if self._e._isEmpty():
            message = 'SimPy: No activities scheduled'
            return message
            
        self._endtime = until
        message = 'SimPy: Normal exit'
        dispatch={hold:holdfunc, request:requestfunc, release:releasefunc,
                  passivate:passivatefunc, waitevent:waitevfunc, queueevent:queueevfunc,
                  waituntil:waituntilfunc, get:getfunc, put:putfunc}
        commandcodes = dispatch.keys()
        commandwords={hold:'hold', request:'request', release:'release', passivate:'passivate',
            waitevent:'waitevent', queueevent:'queueevent', waituntil:'waituntil',
            get:'get', put:'put'}
        nextev = self._e._nextev ## just a timesaver
        while not self._stop and self._t <= self._endtime:
            try:
                a = nextev()
                if not a[0] is None:
                    ## 'a' is tuple '(<yield command>, <action>)'  
                    if type(a[0][0]) == tuple:
                        ##allowing for yield (request, self, res),(waituntil, self, cond)
                        command = a[0][0][0]
                    else: 
                        command = a[0][0]
                    if __debug__:
                        if not command in commandcodes:
                            raise FatalSimerror('Illegal command: yield %s'%command)
                    dispatch[command](a)     
            except FatalSimerror, error:
                print 'SimPy: ' + error.value
                sys.exit(1)
            except Simerror, error:
                message = 'SimPy: ' + error.value
                self._stop = True
            if self._wustep:
                self._test()
        self._stopWUStepping()
        self._e = None
        return message

# For backward compatibility
Globals.sim = SimulationRT()
def rtnow():
    return Globals.sim.rtnow()
    
def rtset(rel_speed = 1):
    Globals.sim.rtset()
    
def simulate(until = 0, real_time = False, rel_speed = 1):
    return Globals.sim.simulate(until = until, real_time = real_time, rel_speed = rel_speed)
# End backward compatibility

if __name__ == '__main__':
    print 'SimPy.SimulationRT %s' %__version__
    ############# Test / demo functions #############
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
                
        print'\n+++test_demo output'
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
        a = simulate(until = 10000, real_time = True, rel_speed = 1)
        print a
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
        Aa.sequIn = []
        Aa.sequOut = []
        a = simulate(until = 10000)
        print a
        print 'Input sequence: ', Aa.sequIn
        print 'Output sequence: ', Aa.sequOut   
    
    def test_interrupt():
        class Bus(Process):
            def __init__(self, name):
                Process.__init__(self, name)
    
            def operate(self, repairduration = 0):
                print now(),rtnow(),'>> %s starts' % (self.name)
                tripleft = 1000
                while tripleft > 0:
                    yield hold, self, tripleft
                    if self.interrupted():
                        print 'interrupted by %s' %self.interruptCause.name
                        print '%s(%s): %s breaks down ' %(now(),rtnow(),self.name)
                        tripleft = self.interruptLeft
                        self.interruptReset()
                        print 'tripleft ', tripleft
                        reactivate(br, delay = repairduration) # breakdowns only during operation
                        yield hold, self, repairduration
                        print now(),rtnow(),' repaired'
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
        print simulate(until = 4000, real_time = True, rel_speed = 200)
    
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
        print'\n\n+++testSimEvents output'
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
        
        print '\n+++\nwaituntil demo output'
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
    # Run tests
    test_interrupt()
    testSimEvents()
    testwaituntil()
