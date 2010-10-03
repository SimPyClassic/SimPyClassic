#!/usr / bin / env python
# coding=utf-8
# $Revision$ $Date: 2008-09-10 17:25:13 +0200 (Mi, 10 Sep 2008) 
"""Simulation 2.1 Implements SimPy Processes, Resources, Buffers, and the backbone simulation
scheduling by coroutine calls. Provides data collection through classes 
Monitor and Tally.
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

import random
import sys
import types
from heapq import heappush, heappop

from SimPy.Lister import Lister
from SimPy.Recording import Monitor, Tally
from SimPy.Lib import Process, SimEvent, PriorityQ, Resource, Level, \
                      Store, Simerror, FatalSimerror

# Required for backward compatibility
import SimPy.Globals as Globals
from SimPy.Globals import initialize, simulate, now, stopSimulation, \
        allEventNotices, allEventTimes, startCollection,\
        _startWUStepping, _stopWUStepping, activate, reactivate


__TESTING = False
version = __version__ = '2.1 $Revision$ $Date$'
if __TESTING: 
    print 'SimPy.Simulation %s' %__version__,
    if __debug__:
        print '__debug__ on'
    else:
        print

# yield keywords
hold = 1
passivate = 2
request = 3
release = 4
waitevent = 5
queueevent = 6
waituntil = 7
get = 8
put = 9


class Infinity(object):
    def __cmp__(self, other):
        return 1

infinity = Infinity()

def holdfunc(a):
    a[0][1]._hold(a)

def requestfunc(a):
    """Handles 'yield request, self, res' and 
    'yield (request, self, res),(<code>,self, par)'.
    <code > can be 'hold' or 'waitevent'.
    """
    if type(a[0][0]) == tuple:
        ## Compound yield request statement
        ## first tuple in ((request, self, res),(xx, self, yy))
        b = a[0][0]
        ## b[2] == res (the resource requested)
        ##process the first part of the compound yield statement
        ##a[1] is the Process instance
        b[2]._request(arg = (b, a[1]))
        ##deal with add - on condition to command
        ##Trigger processes for reneging
        class _Holder(Process):
            """Provides timeout process"""
            def __init__(self,name,sim=None):
                Process.__init__(self,name=name,sim=sim)
            def trigger(self, delay):
                yield hold, self, delay
                if not proc in b[2].activeQ:
                    proc.sim.reactivate(proc)

        class _EventWait(Process):
            """Provides event waiting process"""
            def __init__(self,name,sim=None):
                Process.__init__(self,name=name,sim=sim)
            def trigger(self, event):
                yield waitevent, self, event
                if not proc in b[2].activeQ:
                    proc.eventsFired = self.eventsFired
                    proc.sim.reactivate(proc)
               
        #activate it
        proc = a[0][0][1] # the process to be woken up
        actCode = a[0][1][0]
        if actCode == hold:
            proc._holder = _Holder(name = 'RENEGE - hold for %s'%proc.name,
                                   sim=proc.sim)
            ##                                          the timeout delay
            proc.sim.activate(proc._holder, proc._holder.trigger(a[0][1][2]))
        elif actCode == waituntil:
            raise FatalSimerror('Illegal code for reneging: waituntil')
        elif actCode == waitevent:
            proc._holder = _EventWait(name = 'RENEGE - waitevent for %s'\
                                      %proc.name,sim=proc.sim)
            ##                                          the event
            proc.sim.activate(proc._holder, proc._holder.trigger(a[0][1][2]))
        elif actCode == queueevent:
            raise FatalSimerror('Illegal code for reneging: queueevent')
        else:
            raise FatalSimerror('Illegal code for reneging %s'%actCode)
    else:
        ## Simple yield request command
        a[0][2]._request(a)

def releasefunc(a):
    a[0][2]._release(a)

def passivatefunc(a):
    a[0][1]._passivate(a)

def waitevfunc(a):
    #if waiting for one event only (not a tuple or list)
    evtpar = a[0][2]
    if isinstance(evtpar, SimEvent):
        a[0][2]._wait(a)
    # else, if waiting for an OR of events (list / tuple):
    else: #it should be a list / tuple of events
        # call _waitOR for first event
        evtpar[0]._waitOR(a)
            
def queueevfunc(a):
    #if queueing for one event only (not a tuple or list)
    evtpar = a[0][2]
    if isinstance(evtpar, SimEvent):
        a[0][2]._queue(a)
    #else, if queueing for an OR of events (list / tuple):
    else: #it should be a list / tuple of events
        # call _queueOR for first event
        evtpar[0]._queueOR(a)
    
def waituntilfunc(par):
    par[0][1].sim._waitUntilFunc(par[0][1], par[0][2])
    
def getfunc(a):
    """Handles 'yield get, self, buffer, what, priority' and 
    'yield (get, self, buffer, what, priority),(<code>,self, par)'.
    <code > can be 'hold' or 'waitevent'.
    """
    if type(a[0][0]) == tuple:
        ## Compound yield request statement
        ## first tuple in ((request, self, res),(xx, self, yy))
        b = a[0][0]
        ## b[2] == res (the resource requested)
        ##process the first part of the compound yield statement
        ##a[1] is the Process instance 
        b[2]._get(arg = (b, a[1]))
        ##deal with add - on condition to command
        ##Trigger processes for reneging
        class _Holder(Process):
            """Provides timeout process"""
            def __init__(self,**par):
                Process.__init__(self,**par)
            def trigger(self, delay):
                yield hold, self, delay
                #if not proc in b[2].activeQ:
                if proc in b[2].getQ:
                    a[1].sim.reactivate(proc)

        class _EventWait(Process):
            """Provides event waiting process"""
            def __init__(self,**par):
                Process.__init__(self,**par)
            def trigger(self, event):
                yield waitevent, self, event
                if proc in b[2].getQ:
                    a[1].eventsFired = self.eventsFired
                    a[1].sim.reactivate(proc)
               
        #activate it
        proc = a[0][0][1] # the process to be woken up
        actCode = a[0][1][0]
        if actCode == hold:
            proc._holder = _Holder(name='RENEGE - hold for %s'%proc.name,
                                   sim=proc.sim)
            ##                                          the timeout delay
            a[1].sim.activate(proc._holder, proc._holder.trigger(a[0][1][2]))
        elif actCode == waituntil:
            raise FatalSimerror('waituntil: Illegal code for reneging: waituntil')
        elif actCode == waitevent:
            proc._holder = _EventWait(name="RENEGE - waitevent for%s"\
                                      %proc.name,sim=proc.sim)
            ##                                          the event
            a[1].sim.activate(proc._holder, proc._holder.trigger(a[0][1][2]))
        elif actCode == queueevent:
            raise FatalSimerror('Illegal code for reneging: queueevent')
        else:
            raise FatalSimerror('Illegal code for reneging %s'%actCode)
    else:
        ## Simple yield request command
        a[0][2]._get(a)


def putfunc(a):
    """Handles 'yield put' (simple and compound hold / waitevent)
    """
    if type(a[0][0]) == tuple:
        ## Compound yield request statement
        ## first tuple in ((request, self, res),(xx, self, yy))
        b = a[0][0]
        ## b[2] == res (the resource requested)
        ##process the first part of the compound yield statement
        ##a[1] is the Process instance 
        b[2]._put(arg = (b, a[1]))
        ##deal with add - on condition to command
        ##Trigger processes for reneging
        class _Holder(Process):
            """Provides timeout process"""
            def __init__(self,**par):
                Process.__init__(self,**par)
            def trigger(self, delay):
                yield hold, self, delay
                #if not proc in b[2].activeQ:
                if proc in b[2].putQ:
                    a[1].sim.reactivate(proc)

        class _EventWait(Process):
            """Provides event waiting process"""
            def __init__(self,**par):
                Process.__init__(self,**par)
            def trigger(self, event):
                yield waitevent, self, event
                if proc in b[2].putQ:
                    a[1].eventsFired = self.eventsFired
                    a[1].sim.reactivate(proc)
               
        #activate it
        proc = a[0][0][1] # the process to be woken up
        actCode = a[0][1][0]
        if actCode == hold:
            proc._holder = _Holder(name='RENEGE - hold for %s'%proc.name,
                                   sim=proc.sim)
            ##                                          the timeout delay
            a[1].sim.activate(proc._holder, proc._holder.trigger(a[0][1][2]))
        elif actCode == waituntil:
            raise FatalSimerror('Illegal code for reneging: waituntil')
        elif actCode == waitevent:
            proc._holder = _EventWait(name='RENEGE - waitevent for %s'\
                                      %proc.name,sim=proc.sim)
            ##                                          the event
            a[1].sim.activate(proc._holder, proc._holder.trigger(a[0][1][2]))
        elif actCode == queueevent:
            raise FatalSimerror('Illegal code for reneging: queueevent')
        else:
            raise FatalSimerror('Illegal code for reneging %s'%actCode)
    else:
        ## Simple yield request command
        a[0][2]._put(a)


class Simulation(object):
    _dispatch = {
            hold: holdfunc, request: requestfunc, release: releasefunc,
            passivate: passivatefunc, waitevent: waitevfunc,
            queueevent: queueevfunc, waituntil: waituntilfunc, get: getfunc,
            put: putfunc,
    }
    _commandcodes = _dispatch.keys()
    _commandwords = {
            hold: 'hold', request: 'request', release: 'release',
            passivate: 'passivate', waitevent: 'waitevent',
            queueevent: 'queueevent', waituntil: 'waituntil', get: 'get',
            put: 'put'
    }

    def __init__(self):
        self.initialize()

    def initialize(self):
        self._t = 0
        self.next_time = 0

        # Eventqueue stuff.
        self._timestamps = []
        self._sortpr = 0

        self._start = False
        self._stop = False
        self.condQ = []
        self.allMonitors = []
        self.allTallies = []

    def now(self):
        return self._t

    def stopSimulation(self):
        """Application function to stop simulation run"""
        self._stop = True

    def _post(self, what, at, prior = False):
        """Post an event notice for process what for time at"""
        # event notices are Process instances
        if at < self._t:
            raise FatalSimerror('Attempt to schedule event in the past')
        what._nextTime = at
        self._sortpr -= 1
        if prior:
            # before all other event notices at this time
            # heappush with highest priority value so far (negative of
            # monotonely decreasing number)
            # store event notice in process instance
            what._rec = [at, self._sortpr, what, False]
            # make event list refer to it
            heappush(self._timestamps, what._rec)
        else:
            # heappush with lowest priority
            # store event notice in process instance
            what._rec = [at,-self._sortpr, what, False]
            # make event list refer to it
            heappush(self._timestamps, what._rec)

    def _unpost(self, whom):
        """
        Mark event notice for whom as cancelled if whom is a suspended process
        """
        if whom._nextTime is not None:  # check if whom was actually active
            whom._rec[3] = True ## Mark as cancelled
            whom._nextTime = None

    def allEventNotices(self):
        """Returns string with eventlist as;
                t1: processname, processname2
                t2: processname4, processname5, . . .
                . . .  .
        """
        ret = ''
        tempList = []
        tempList[:] = self._timestamps
        tempList.sort()
        # return only event notices which are not cancelled
        tempList = [[x[0],x[2].name] for x in tempList if not x[3]]
        tprev = -1
        for t in tempList:
            # if new time, new line
            if t[0] == tprev:
                # continue line
                ret += ', %s'%t[1]
            else:
                # new time
                if tprev == -1:
                    ret = '%s: %s' % (t[0],t[1])
                else:
                    ret += '\n%s: %s' % (t[0],t[1])
                tprev = t[0]
        return ret + '\n'

    def allEventTimes(self):
        """Returns list of all times for which events are scheduled.
        """
        r = []
        r[:] = self._timestamps
        r.sort()
        # return only event times of not cancelled event notices
        r1 = [x[0] for x in r if not x[3]]
        tprev = -1
        ret = []
        for t in r1:
            if t == tprev:
                #skip time, already in list
                pass
            else:
                ret.append(t)
                tprev = t
        return ret

    def activate(self, obj, process, at = 'undefined', delay = 'undefined',
                 prior = False):
        """Application function to activate passive process."""
        if __debug__:
            if not (obj.sim == self):
                txt="activate: Process %s not in activating Simulation instance"\
                    %obj.name
                raise FatalSimerror(txt)
            if not (type(process) == types.GeneratorType):
                raise FatalSimerror('Activating function which'+
                    ' is not a generator (contains no \'yield\')')
        if not obj._terminated and not obj._nextTime:
            #store generator reference in object; needed for reactivation
            obj._nextpoint = process
            if at == 'undefined':
                at = self._t
            if delay == 'undefined':
                zeit = max(self._t, at)
            else:
                zeit = max(self._t, self._t + delay)
            self._post(obj, at = zeit, prior = prior)

    def reactivate(self, obj, at = 'undefined', delay = 'undefined',
                   prior = False):
        """Application function to reactivate a process which is active,
        suspended or passive."""
        # Object may be active, suspended or passive
        if not obj._terminated:
            a = Process('SimPysystem',sim=self)
            a.cancel(obj)
            # object now passive
            if at == 'undefined':
                at = self._t
            if delay == 'undefined':
                zeit = max(self._t, at)
            else:
                zeit = max(self._t, self._t + delay)
            self._post(obj, at = zeit, prior = prior)

    def startCollection(self, when = 0.0, monitors = None, tallies = None):
        """Starts data collection of all designated Monitor and Tally objects
        (default = all) at time 'when'.
        """
        class Starter(Process):
            def collect(self, monitors, tallies):
                for m in monitors:
                    m.reset()
                for t in tallies:
                    t.reset()
                yield hold, self
        if monitors is None:
            monitors = self.allMonitors
        if tallies is None:
            tallies = self.allTallies
        if when == 0.0:
            for m in monitors:
                try:
                    ylast = m[-1][1]
                    empty = False
                except IndexError:
                    empty = True
                m.reset()
                if not empty:
                    m.observe(t = now(), y = ylast)
            for t in tallies:
                t.reset()
        else:                
            s = Starter(sim = self)
            self.activate(s, s.collect(monitors = monitors, tallies = tallies),\
                      at = when, prior = True)
    

    def _waitUntilFunc(self, proc, cond):
        """
        Puts a process 'proc' waiting for a condition into a waiting queue.
        'cond' is a predicate function which returns True if the condition is
        satisfied.
        """
        if not cond():
            self.condQ.append(proc)
            proc.cond = cond
            # passivate calling process
            proc._nextTime = None
        else:
            #schedule continuation of calling process
            self._post(proc, at = self._t, prior = 1)

    def _terminate(self, process):
        """Marks a process as terminated."""
        process._nextpoint = None
        process._terminated = True
        process._nextTime = None

    def has_events(self):
        """
        Checks if there are events which can be processed. Returns ``True`` if
        there are events and the simulation has not been stopped.
        """
        return not self._stop and self._timestamps

    def peek(self):
        """
        Returns the time of the next event or infinity, if no
        more events are scheduled.
        """
        if not self._timestamps:
            return infinity
        else:
            return self._timestamps[0][0]

    def step(self):
        """
        Executes the next uncancelled event in the eventqueue. 
        """

        # Fetch next process and advance its process execution method.
        noActiveNotice = True
        # Get an uncancelled event
        while noActiveNotice:
            if self._timestamps:
                _tnotice, p, proc, cancelled = heappop(self._timestamps)
                noActiveNotice = cancelled
            else:
                return None

        # Advance simulation time.
        proc._rec = None
        self._t = _tnotice

        # Execute the event. This will advance the process execution method.
        try:
            resultTuple = proc._nextpoint.next()

            # Process the command function which has been yielded by the
            # process.
            if type(resultTuple[0]) == tuple:
                # allowing for reneges, e.g.:
                # >>> yield (request, self, res),(waituntil, self, cond)
                command = resultTuple[0][0]
            else:
                command = resultTuple[0]
            if __debug__:
                if not command in self._commandcodes:
                    raise FatalSimerror('Illegal command: yield %s'%command)
            self._dispatch[command]((resultTuple, proc))
        except StopIteration:
            # Process execution method has terminated.
            self._terminate(proc)

        # Test the conditions for all waiting processes if there are any at
        # all. Where condition are satisfied, reactivate that process
        # immediately and remove it from queue.
        # Always test the wait conditions. They might be triggered by on a
        # terminating process execution method (e.g. the above next() call
        # raises the StopIteration exception)
        if self.condQ:
            i = 0
            while i < len(self.condQ):
                proc = self.condQ[i]
                if proc.cond():
                    self.condQ.pop(i)
                    self.reactivate(proc)
                else:
                    i += 1

        # Return time of the next scheduled event.
        #return self._timestamps[0][0] if self._timestamps else None
        if self._timestamps:
            return self._timestamps[0][0]
        else:
            return None

    def simulate(self, until=0):
        """
        Start the simulation and run its loop until the timeout ``until`` is
        reached, stopSimulation is called, or no more events are scheduled.
        """
        try:
            if not self._timestamps:
                return 'SimPy: No activities scheduled'

            # Some speedups. Storing these values in local variables prevents
            # the self-lookup. Note that this can't be done for _stop because
            # this variable will get overwritten, bools are immutable.
            step = self.step
            timestamps = self._timestamps
            while not self._stop and timestamps and timestamps[0][0] <= until:
                step()

            if not self._stop and timestamps: 
                # Timestamps left, simulation not stopped
                self._t = until
                return 'SimPy: Normal exit at time %s' % self._t
            elif not timestamps: 
                # No more timestamps
                return 'SimPy: No more events at time %s' % self._t
            else: 
                # Stopped by call of stopSimulation
                return 'SimPy: Run stopped at time %s' % self._t
        except FatalSimerror, error:
                print 'SimPy: ' + error.value
                raise FatalSimerror, 'SimPy: ' + error.value
        except Simerror, error:
            return 'SimPy: ' + error.value
        finally:
            self._stop = True

# For backward compatibility
Globals.sim = Simulation()

peek = Globals.sim.peek

step = Globals.sim.step 

allMonitors = Globals.sim.allMonitors

allTallies = Globals.sim.allTallies
# End backward compatibility

if __name__ == '__main__':
    print 'SimPy.Simulation %s' %__version__
    ############# Test / demo functions #############
    def test_demo():
        class Aa(Process):
            sequIn = []
            sequOut = []
            def __init__(self, holdtime, name,sim=None):
                Process.__init__(self, name,sim=sim)
                self.holdtime = holdtime

            def life(self, priority):
                for i in range(1):
                    Aa.sequIn.append(self.name)
                    print self.sim.now(),rrr.name, 'waitQ:', len(rrr.waitQ),'activeQ:',\
                          len(rrr.activeQ)
                    print 'waitQ: ',[(k.name, k._priority[rrr]) for k in rrr.waitQ]
                    print 'activeQ: ',[(k.name, k._priority[rrr]) \
                               for k in rrr.activeQ]
                    assert rrr.n + len(rrr.activeQ) == rrr.capacity, \
                   'Inconsistent resource unit numbers'
                    print self.sim.now(),self.name, 'requests 1 ', rrr.unitName
                    yield request, self, rrr, priority
                    print self.sim.now(),self.name, 'has 1 ', rrr.unitName
                    print self.sim.now(),rrr.name, 'waitQ:', len(rrr.waitQ),'activeQ:',\
                          len(rrr.activeQ)
                    print self.sim.now(),rrr.name, 'waitQ:', len(rrr.waitQ),'activeQ:',\
                          len(rrr.activeQ)
                    assert rrr.n + len(rrr.activeQ) == rrr.capacity, \
                   'Inconsistent resource unit numbers'
                    yield hold, self, self.holdtime
                    print self.sim.now(),self.name, 'gives up 1', rrr.unitName
                    yield release, self, rrr
                    Aa.sequOut.append(self.name)
                    print self.sim.now(),self.name, 'has released 1 ', rrr.unitName
                    print 'waitQ: ',[(k.name, k._priority[rrr]) for k in rrr.waitQ]
                    print self.sim.now(),rrr.name, 'waitQ:', len(rrr.waitQ),'activeQ:',\
                          len(rrr.activeQ)
                    assert rrr.n + len(rrr.activeQ) == rrr.capacity, \
                           'Inconsistent resource unit numbers'

        class Observer(Process):
            def __init__(self,**vars):
                Process.__init__(self,**vars)

            def observe(self, step, processes, res):
                while self.sim.now() < 11:
                    for i in processes:
                        print '++ %s process: %s: active:%s, passive:%s, terminated: %s, interrupted:%s, queuing:%s'\
                              %(self.sim.now(),i.name, i.active(),i.passive(),\
                                i.terminated(),i.interrupted(),i.queuing(res))
                    print
                    yield hold, self, step

        print'\n+++test_demo output'
        print '****First case == priority queue, resource service not preemptable'
        s=Simulation()
        s.initialize()
        rrr = Resource(5, name = 'Parking', unitName = 'space(s)', qType = PriorityQ,
                     preemptable = 0,sim=s)
        procs = []
        for i in range(10):
            z = Aa(holdtime = i, name = 'Car ' + str(i),sim=s)
            procs.append(z)
            s.activate(z, z.life(priority = i))
        o = Observer(sim=s)
        s.activate(o, o.observe(1, procs, rrr))
        a = s.simulate(until = 10000)
        print a
        print 'Input sequence: ', Aa.sequIn
        print 'Output sequence: ', Aa.sequOut

        print '\n****Second case == priority queue, resource service preemptable'
        s=Simulation()
        s.initialize()
        rrr = Resource(5, name = 'Parking', unitName = 'space(s)', qType = PriorityQ,
                     preemptable = 1,sim=s)
        procs = []
        for i in range(10):
            z = Aa(holdtime = i, name = 'Car ' + str(i),sim=s)
            procs.append(z)
            s.activate(z, z.life(priority = i))
        o = Observer(sim=s)
        s.activate(o, o.observe(1, procs, rrr))
        Aa.sequIn = []
        Aa.sequOut = []
        a = s.simulate(until = 10000)
        print a
        print 'Input sequence: ', Aa.sequIn
        print 'Output sequence: ', Aa.sequOut

    def test_interrupt():
        class Bus(Process):
            def __init__(self, **vars):
                Process.__init__(self, **vars)

            def operate(self, repairduration = 0):
                print self.sim.now(),'>> %s starts' % (self.name)
                tripleft = 1000
                while tripleft > 0:
                    yield hold, self, tripleft
                    if self.interrupted():
                        print 'interrupted by %s' %self.interruptCause.name
                        print '%s: %s breaks down ' %(now(),self.name)
                        tripleft = self.interruptLeft
                        self.interruptReset()
                        print 'tripleft ', tripleft
                        s.reactivate(br, delay = repairduration) # breakdowns only during operation
                        yield hold, self, repairduration
                        print self.sim.now(),' repaired'
                    else:
                        break # no breakdown, ergo bus arrived
                print self.sim.now(),'<< %s done' % (self.name)

        class Breakdown(Process):
            def __init__(self, myBus,sim=None):
                Process.__init__(self, name = 'Breakdown ' + myBus.name,sim=sim)
                self.bus = myBus

            def breakBus(self, interval):

                while True:
                    yield hold, self, interval
                    if self.bus.terminated(): break
                    self.interrupt(self.bus)

        print'\n\n+++test_interrupt'
        s=Simulation()
        s.initialize()
        b = Bus(name='Bus 1',sim=s)
        s.activate(b, b.operate(repairduration = 20))
        br = Breakdown(b,sim=s)
        s.activate(br, br.breakBus(200))
        print s.simulate(until = 4000)

    def testSimEvents():
        class Waiter(Process):
            def __init__(self,**vars):
                Process.__init__(self,**vars)
            def waiting(self, theSignal):
                while True:
                    yield waitevent, self, theSignal
                    print '%s: process \'%s\' continued after waiting for %s' %\
                          (self.sim.now(),self.name, theSignal.name)
                    yield queueevent, self, theSignal
                    print '%s: process \'%s\' continued after queueing for %s' % (now(),self.name, theSignal.name)

        class ORWaiter(Process):
            def __init__(self,**vars):
                Process.__init__(self,**vars)
            def waiting(self, signals):
                while True:
                    yield waitevent, self, signals
                    print self.sim.now(),'one of %s signals occurred' %\
                          [x.name for x in signals]
                    print '\t%s (fired / param)'%\
                          [(x.name, x.signalparam) for x in self.eventsFired]
                    yield hold, self, 1

        class Caller(Process):
            def __init__(self,**vars):
                Process.__init__(self,**vars)
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
        s=Simulation()
        s.initialize()
        signal1 = SimEvent('signal 1',sim=s)
        signal2 = SimEvent('signal 2',sim=s)
        signal1.signal('startup1')
        signal2.signal('startup2')
        w1 = Waiter(name='waiting for signal 1',sim=s)
        s.activate(w1, w1.waiting(signal1))
        w2 = Waiter(name='waiting for signal 2',sim=s)
        s.activate(w2, w2.waiting(signal2))
        w3 = Waiter(name='also waiting for signal 2',sim=s)
        s.activate(w3, w3.waiting(signal2))
        w4 = ORWaiter(name='waiting for either signal 1 or signal 2',sim=s)
        s.activate(w4, w4.waiting([signal1, signal2]),prior = True)
        c = Caller(name='Caller',sim=s)
        s.activate(c, c.calling())
        print s.simulate(until = 100)

    def testwaituntil():
        """
        Demo of waitUntil capability.

        Scenario:
        Three workers require sets of tools to do their jobs. Tools are shared,
        scarce resources for which they compete.
        """
        class Worker(Process):
            def __init__(self, name, heNeeds = [],sim=None):
                Process.__init__(self, name,sim=sim)
                self.heNeeds = heNeeds
            def work(self):
                def workerNeeds():
                    for item in self.heNeeds:
                        if item.n == 0:
                            return False
                    return True

                while self.sim.now() < 8 * 60:
                    yield waituntil, self, workerNeeds
                    for item in self.heNeeds:
                        yield request, self, item
                    print '%s %s has %s and starts job' % (self.sim.now(),self.name,
                        [x.name for x in self.heNeeds])
                    yield hold, self, random.uniform(10, 30)
                    for item in self.heNeeds:
                        yield release, self, item
                    yield hold, self, 2 #rest

        print '\n+++ nwaituntil demo output'
        random.seed(12345)
        s=Simulation()
        s.initialize()
        brush = Resource(capacity = 1, name = 'brush',sim=s)
        ladder = Resource(capacity = 2, name = 'ladder',sim=s)
        hammer = Resource(capacity = 1, name = 'hammer',sim=s)
        saw = Resource(capacity = 1, name = 'saw',sim=s)
        painter = Worker('painter',[brush, ladder],sim=s)
        s.activate(painter, painter.work())
        roofer = Worker('roofer',[hammer, ladder, ladder],sim=s)
        s.activate(roofer, roofer.work())
        treeguy = Worker('treeguy',[saw, ladder],sim=s)
        s.activate(treeguy, treeguy.work())
        for who in (painter, roofer, treeguy):
            print '%s needs %s for his job' %\
                  (who.name,[x.name for x in who.heNeeds])
        print
        print s.simulate(until = 9 * 60)

    ## -------------------------------------------------------------
    ##                    TEST COMPOUND 'YIELD REQUEST' COMMANDS
    ## -------------------------------------------------------------

    ## -------------------------------------------------------------
    ##             TEST 'yield (request, self, res),(hold, self, delay)'
    ##                   == timeout renege
    ## -------------------------------------------------------------

    class JobTO(Process):
       """ Job class for testing timeout reneging
       """
       def __init__(self, server = None, name = '',sim=None):
            Process.__init__(self, name,sim=sim)
            self.res = server
            self.gotResource = None

       def execute(self, timeout, usetime):
            yield (request, self, self.res),(hold, self, timeout)
            if self.acquired(self.res):
                self.gotResource = True
                yield hold, self, usetime
                yield release, self, self.res
            else:
                self.gotResource = False


    def testNoTimeout():
        """Test that resource gets acquired without timeout
        """
        s=Simulation()
        s.initialize()
        res = Resource(name = 'Server', capacity = 1,sim=s)
        usetime = 5
        timeout = 1000000
        j1 = JobTO(server = res, name = 'Job_1',sim=s)
        s.activate(j1, j1.execute(timeout = timeout, usetime = usetime))
        j2 = JobTO(server = res, name = 'Job_2',sim=s)
        s.activate(j2, j2.execute(timeout = timeout, usetime = usetime))
        s.simulate(until = 2 * usetime)
        assert s.now() == 2 * usetime, 'time not == 2 * usetime'
        assert j1.gotResource and j2.gotResource,\
            'at least one job failed to get resource'
        assert not (res.waitQ or res.activeQ),\
            'job waiting or using resource'

    def testTimeout1():
        """Test that timeout occurs when resource busy
        """
        s=Simulation()
        s.initialize()
        res = Resource(name = 'Server', capacity = 1, monitored = True,sim=s)
        usetime = 5
        timeout = 3
        j1 = JobTO(server = res, name = 'Job_1',sim=s)
        s.activate(j1, j1.execute(timeout = timeout, usetime = usetime))
        j2 = JobTO(server = res, name = 'Job_2',sim=s)
        s.activate(j2, j2.execute(timeout = timeout, usetime = usetime))
        s.simulate(until = 2 * usetime)
        assert(s.now() == usetime),'time not == usetime'
        assert(j1.gotResource),'Job_1 did not get resource'
        assert(not j2.gotResource),'Job_2 did not renege'
        assert not (res.waitQ or res.activeQ),\
            'job waiting or using resource'

    def testTimeout2():
        """Test that timeout occurs when resource has no capacity free
        """
        s=Simulation()
        s.initialize()
        res = Resource(name = 'Server', capacity = 0,sim=s)
        usetime = 5
        timeout = 3
        j1 = JobTO(server = res, name = 'Job_1',sim=s)
        s.activate(j1, j1.execute(timeout = timeout, usetime = usetime))
        j2 = JobTO(server = res, name = 'Job_2',sim=s)
        s.activate(j2, j2.execute(timeout = timeout, usetime = usetime))
        s.simulate(until = 2 * usetime)
        assert s.now() == timeout, 'time %s not == timeout'%now()
        assert not j1.gotResource, 'Job_1 got resource'
        assert not j2.gotResource, 'Job_2 got resource'
        assert not (res.waitQ or res.activeQ),\
            'job waiting or using resource'

    ## ------------------------------------------------------------------
    ##             TEST 'yield (request, self, res),(waitevent, self, event)'
    ##                   == event renege
    ## ------------------------------------------------------------------
    class JobEvt(Process):
       """ Job class for testing event reneging
       """
       def __init__(self, server = None, name = '',sim=None):
            Process.__init__(self, name,sim=sim)
            self.res = server
            self.gotResource = None

       def execute(self, event, usetime):
            yield (request, self, self.res),(waitevent, self, event)
            if self.acquired(self.res):
                self.gotResource = True
                yield hold, self, usetime
                yield release, self, self.res
            else:
                self.gotResource = False

    class JobEvtMulti(Process):
       """ Job class for testing event reneging with multi - event lists
       """
       def __init__(self, server = None, name = '',sim=None):
            Process.__init__(self, name,sim=sim)
            self.res = server
            self.gotResource = None

       def execute(self, eventlist, usetime):
            yield (request, self, self.res),(waitevent, self, eventlist)
            if self.acquired(self.res):
                self.gotResource = True
                yield hold, self, usetime
                yield release, self, self.res
            else:
                self.gotResource = False

    class FireEvent(Process):
        """Fires reneging event
        """
        def __init__(self,**vars):
            Process.__init__(self,**vars)
        def fire(self, fireDelay, event):
            yield hold, self, fireDelay
            event.signal()

    def testNoEvent():
        """Test that processes acquire resource normally if no event fires
        """
        s=Simulation()
        s.initialize()
        res = Resource(name = 'Server', capacity = 1,sim=s)
        event = SimEvent(name='Renege_trigger',sim=s) #never gets fired
        usetime = 5
        j1 = JobEvt(server = res, name = 'Job_1',sim=s)
        s.activate(j1, j1.execute(event = event, usetime = usetime))
        j2 = JobEvt(server = res, name = 'Job_2',sim=s)
        s.activate(j2, j2.execute(event = event, usetime = usetime))
        s.simulate(until = 2 * usetime)
        # Both jobs should get server (in sequence)
        assert s.now() == 2 * usetime, 'time not == 2 * usetime'
        assert j1.gotResource and j2.gotResource,\
            'at least one job failed to get resource'
        assert not (res.waitQ or res.activeQ),\
            'job waiting or using resource'

    def testWaitEvent1():
        """Test that signalled event leads to renege when resource busy
        """
        s=Simulation()
        s.initialize()
        res = Resource(name = 'Server', capacity = 1,sim=s)
        event = SimEvent('Renege_trigger',sim=s)
        usetime = 5
        eventtime = 1
        j1 = JobEvt(server = res, name = 'Job_1',sim=s)
        s.activate(j1, j1.execute(event = event, usetime = usetime))
        j2 = JobEvt(server = res, name = 'Job_2',sim=s)
        s.activate(j2, j2.execute(event = event, usetime = usetime))
        f = FireEvent(name = 'FireEvent',sim=s)
        s.activate(f, f.fire(fireDelay = eventtime, event = event))
        s.simulate(until = 2 * usetime)
        # Job_1 should get server, Job_2 renege
        assert(s.now() == usetime),'time not == usetime'
        assert(j1.gotResource),'Job_1 did not get resource'
        assert(not j2.gotResource),'Job_2 did not renege'
        assert not (res.waitQ or res.activeQ),\
            'job waiting or using resource'

    def testWaitEvent2():
        """Test that renege - triggering event can be one of an event list
        """
        s=Simulation()
        s.initialize()
        res = Resource(name = 'Server', capacity = 1,sim=s)
        event1 = SimEvent('Renege_trigger_1',sim=s)
        event2 = SimEvent('Renege_trigger_2',sim=s)
        usetime = 5
        eventtime = 1 #for both events
        j1 = JobEvtMulti(server = res, name = 'Job_1',sim=s)
        s.activate(j1, j1.execute(eventlist = [event1, event2],usetime = usetime))
        j2 = JobEvtMulti(server = res, name = 'Job_2',sim=s)
        s.activate(j2, j2.execute(eventlist = [event1, event2],usetime = usetime))
        f1 = FireEvent(name = 'FireEvent_1',sim=s)
        s.activate(f1, f1.fire(fireDelay = eventtime, event = event1))
        f2 = FireEvent(name = 'FireEvent_2',sim=s)
        s.activate(f2, f2.fire(fireDelay = eventtime, event = event2))
        s.simulate(until = 2 * usetime)
        # Job_1 should get server, Job_2 should renege
        assert(s.now() == usetime),'time not == usetime'
        assert(j1.gotResource),'Job_1 did not get resource'
        assert(not j2.gotResource),'Job_2 did not renege'
        assert not (res.waitQ or res.activeQ),\
            'job waiting or using resource'

    testNoTimeout()
    testTimeout1()
    testTimeout2()
    testNoEvent()
    testWaitEvent1()
    testWaitEvent2()
    test_demo()
    test_interrupt()
    testSimEvents()
    testwaituntil()
