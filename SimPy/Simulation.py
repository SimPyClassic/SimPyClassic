#!/usr / bin / env python
# $Revision$ $Date: 2008-09-10 17:25:13 +0200 (Mi, 10 Sep 2008) 
"""Simulation 2.0 Implements SimPy Processes, Resources, Buffers, and the backbone simulation
scheduling by coroutine calls. Provides data collection through classes 
Monitor and Tally.
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
          class _Evlist.
        
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
                
    10 Aug 2008: - Introduced a Simulation class that now contains all global
                   functions for the simulation.
                    * Globals.py contains dummies for them to obtain backward
                      compatibility (Ontje Luensdorf)
                 - Histogram, Monitor and Tally were moved to Recording.py
                   (Stefan Scherfke)
                 - Process, SimEvent, Queue, FIFO, PriorityQ, Resource, Buffer,
                   Level, Store moved to Resources.py
                 - Renamed __Evlist to Evlist
    
"""

import heapq as hq
import random
import sys
import types

from SimPy.Lister import Lister
from SimPy.Recording import Monitor, Tally
from SimPy.Lib import Process, SimEvent, PriorityQ, Resource, Level, Store

# Required for backward compatibility
import SimPy.Globals as Globals
from SimPy.Globals import initialize, simulate, now, stopSimulation, \
        allEventNotices, allEventTimes, startCollection,\
        _startWUStepping, _stopWUStepping, activate, reactivate


__TESTING = False
version = __version__ = '2.0 $Revision$ $Date$'
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


class Simerror(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return `self.value`

    
class FatalSimerror(Simerror):
    def __init__(self, value):
        Simerror.__init__(self, value)
        self.value = value

class Evlist(object):
    """Defines event list and operations on it"""
    def __init__(self, sim):
        # always sorted list of events (sorted by time, priority)
        # make heapq
        self.sim = sim
        self.timestamps = []
        self.sortpr = 0

    def _post(self, what, at, prior = False):
        """Post an event notice for process what for time at"""
        # event notices are Process instances
        if at < self.sim._t:
            raise Simerror('Attempt to schedule event in the past')
        what._nextTime = at
        self.sortpr -= 1
        if prior:
            # before all other event notices at this time
            # heappush with highest priority value so far (negative of 
            # monotonely decreasing number)
            # store event notice in process instance
            what._rec = [at, self.sortpr, what, False]
            # make event list refer to it
            hq.heappush(self.timestamps, what._rec)
        else:
            # heappush with lowest priority
            # store event notice in process instance
            what._rec = [at,-self.sortpr, what, False]
            # make event list refer to it
            hq.heappush(self.timestamps, what._rec)

    def _unpost(self, whom):
        """
        Mark event notice for whom as cancelled if whom is a suspended process
        """
        if whom._nextTime is not None:  # check if whom was actually active
            whom._rec[3] = True ## Mark as cancelled
            whom._nextTime = None  
            
    def _nextev(self):
        """Retrieve next event from event list"""
        noActiveNotice = True
        ## Find next event notice which is not marked cancelled
        while noActiveNotice:
            if self.timestamps:
                 ## ignore priority value         
                (_tnotice, p, nextEvent, cancelled) = hq.heappop(self.timestamps)
                noActiveNotice = cancelled
            else:
                raise Simerror('No more events at time %s' % self.sim._t)
        nextEvent._rec = None
        self.sim._t = _tnotice
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

    def _isEmpty(self):
        return not self.timestamps

    def _allEventNotices(self):
        """Returns string with eventlist as
                t1: [procname, procname2]
                t2: [procname4, procname5, . . . ]
                . . .  .
        """
        ret = ''
        for t in self.timestamps:
            ret += '%s:%s\n' % (t[1]._nextTime, t[1].name)
        return ret[:-1]

    def _allEventTimes(self):
        """Returns list of all times for which events are scheduled.
        """
        return self.timestamps


class Simulation(object):
    def __init__(self):
        self.initialize()
       
    def initialize(self):
        self._endtime = 0
        self._t = 0
        self._e = Evlist(self)
        self._stop = False
        self._wustep = False #controls per event stepping for waituntil construct; not user API
        self.condQ = []
        self.allMonitors = []
        self.allTallies = []
    
    def now(self):
        return self._t
    
    def stopSimulation(self):
        """Application function to stop simulation run"""
        self._stop = True
    
    def _startWUStepping(self):
        """Application function to start stepping through simulation for waituntil construct."""
        self._wustep = True
    
    def _stopWUStepping(self):
        """Application function to stop stepping through simulation."""
        self._wustep = False
    
    def allEventNotices(self):
        """Returns string with eventlist as;
                t1: processname, processname2
                t2: processname4, processname5, . . .
                . . .  .
        """
        ret = ''
        tempList = []
        tempList[:] = self._e.timestamps
        tempList.sort()
        # return only event notices which are not cancelled
        tempList = [[x[0],x[2].name] for x in tempList if not x[3]]
        tprev=-1
        for t in tempList:
            # if new time, new line
            if t[0] == tprev:
                # continue line
                ret += ',%s'%t[1]
            else:
                # new time
                if tprev==-1:
                    ret = '%s: %s' % (t[0],t[1])
                else:
                    ret += '\n%s: %s' % (t[0],t[1])
                tprev = t[0]
        return ret + '\n'
    
    def allEventTimes(self):
        """Returns list of all times for which events are scheduled.
        """
        r = []
        r[:] = self._e.timestamps
        r.sort()
        # return only event times of not cancelled event notices
        r1 = [x[0] for x in r if not x[3]]
        tprev=-1
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
        if self._e is None:
            raise FatalSimerror\
                    ('Fatal error: simulation is not initialized (call initialize() first)')
        if not (type(process) == types.GeneratorType):
            raise FatalSimerror('Activating function which'+
                ' is not a generator (contains no \'yield\')')
##        obj.sim=self
        if not obj._terminated and not obj._nextTime:
            #store generator reference in object; needed for reactivation
            obj._nextpoint = process
            if at == 'undefined':
                at = self._t
            if delay == 'undefined':
                zeit = max(self._t, at)
            else:
                zeit = max(self._t, self._t + delay)
            self._e._post(obj, at = zeit, prior = prior)
    
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
            self._e._post(obj, at = zeit, prior = prior)
    
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
        s = Starter()
        self.activate(s, s.collect(monitors = monitors, tallies = tallies),at = when)
    
    ## begin waituntil functionality
    def _test(self):
        """
        Gets called by simulate after every event, as long as there are processes
        waiting in self.condQ for a condition to be satisfied.
        Tests the conditions for all waiting processes. Where condition satisfied,
        reactivates that process immediately and removes it from queue.
        """
        rList = []
        for el in self.condQ:
            if el.cond():
                rList.append(el)
                self.reactivate(el)
        for i in rList:
            self.condQ.remove(i)
    
        if not self.condQ:
            self._stopWUStepping()
    
    def _waitUntilFunc(self, proc, cond):
        """
        Puts a process 'proc' waiting for a condition into a waiting queue.
        'cond' is a predicate function which returns True if the condition is
        satisfied.
        """    
        if not cond():
            self.condQ.append(proc)
            proc.cond = cond
            self._startWUStepping()         #signal 'simulate' that a process is waiting
            # passivate calling process
            proc._nextTime = None
        else:
            #schedule continuation of calling process
            self._e._post(proc, at = self._t, prior = 1)
    
    
    ##end waituntil functionality
    
    def simulate(self, until = 0):
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
        
        """
        self._stop = False
    
        if self._e is None:
            raise FatalSimerror('Simulation not initialized')
        if self._e._isEmpty():
            self._e = None
            message="SimPy: No activities scheduled"
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

def scheduler(till = 0):
    """Schedules Processes / semi - coroutines until time 'till'.
    Deprecated since version 0.5.
    """
    simulate(until = till)

def holdfunc(a):
    a[0][1]._hold(a)

def requestfunc(a):
    """Handles 'yield request, self, res' and 'yield (request, self, res),(<code>,self, par)'.
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
            raise FatalSimerror('Illegal code for reneging: waituntil')
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

# For backward compatibility
Globals.sim = Simulation()
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
