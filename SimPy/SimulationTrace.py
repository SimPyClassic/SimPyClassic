#!/usr / bin / env python
# coding=utf-8
# $Revision$ $Date$ kgm
"""SimulationTrace 2.1 Traces execution of SimPy models.
Implements SimPy Processes, Resources, Buffers, and the backbone simulation 
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
"""

from SimPy.Lister import *
from SimPy.Simulation import *


__TESTING = False
version = __version__ = '2.1 $Revision$ $Date$'
if __TESTING: 
    print 'SimPy.SimulationTrace %s' %__version__,
    if __debug__:
        print '__debug__ on'
    else:
        print

def trace_dispatch(trace, command, func):
    """
    Returns a wrapper for ``func`` which will record the dispatch in the trace
    log.
    """
    def dispatch(event):
        func(event)
        trace.recordEvent(command, event)

    return dispatch

class SimulationTrace(Simulation):
    def __init__(self):
        Simulation.__init__(self)
        self.trace = Trace(sim=self)
        # Trace method to be called on _post calls.
        self._post_tracing = None

        # We use our own instance of the command dictionary.
        self._dispatch = dict(Simulation._dispatch)

        # Now wrap all commands in a tracing call.
        for command, func in self._dispatch.items():
            self._dispatch[command] = trace_dispatch(self.trace, command, func)

    def initialize(self):
        Simulation.initialize(self)


    def _post(self, what, at, prior=False):
        if self._post_tracing is not None: self._post_tracing(what, at, prior)
        Simulation._post(self, what, at, prior)

    def activate(
            self, obj, process, at='undefined', delay='undefined', prior=False):
        # Activate _post tracing.
        self._post_tracing = self.trace.recordActivate
        Simulation.activate(self, obj, process, at, delay, prior)
        self._post_tracing = None

    def reactivate(
            self, obj, at='undefined', delay='undefined', prior=False):
        # Activate _post tracing.
        self._post_tracing = self.trace.recordReactivate
        Simulation.reactivate(self, obj, at, delay, prior)
        self._post_tracing = None

    def _terminate(self, process):
        self.trace.tterminated(process)
        Simulation._terminate(self, process)

    def simulate(self, until=0):
        try:
            return Simulation.simulate(self, until)
        finally:
            if not(self.trace.outfile is sys.stdout):
                self.trace.outfile.close()

class Trace(Lister):
    commands={hold:'hold', passivate:'passivate', request:'request', release:'release',
              waitevent:'waitevent', queueevent:'queueevent', waituntil:'waituntil',
            get:'get', put:'put'}

    def __init__(self, start = 0, end = 10000000000L, toTrace=\
                 ['hold', 'activate', 'cancel', 'reactivate', 'passivate', 'request',
                  'release', 'interrupt', 'terminated', 'waitevent', 'queueevent',
                  'signal', 'waituntil', 'put', 'get' 
                 ],outfile = sys.stdout,sim=None):
                        
        Trace.commandsproc={hold:Trace.thold, passivate:Trace.tpassivate,
                            request:Trace.trequest, release:Trace.trelease,
                            waitevent:Trace.twaitevent,
                            queueevent:Trace.tqueueevent,
                            waituntil:Trace.twaituntil,
                            get:Trace.tget, put:Trace.tput}
        if sim is None: sim=Globals.sim
        self.sim=sim
        self.start = start
        self.end = end
        self.toTrace = toTrace
        self.tracego = True
        self.outfile = outfile
        self._comment = None

    def treset(self):
        Trace.commandsproc={hold:Trace.thold, passivate:Trace.tpassivate,
                            request:Trace.trequest, release:Trace.trelease,
                            waitevent:Trace.twaitevent,
                            queueevent:Trace.tqueueevent,
                            waituntil:Trace.twaituntil,
                            get:Trace.tget, put:Trace.tput}
        self.start = 0
        self.end = 10000000000L
        self.toTrace = ['hold', 'activate', 'cancel', 'reactivate', 'passivate', 'request',
                        'release', 'interrupt', 'terminated', 'waitevent', 'queueevent',
                        'signal', 'waituntil', 'put', 'get']
        self.tracego = True
        self.outfile = sys.stdout
        self._comment = None

    def tchange(self,**kmvar):
        for v in kmvar.keys():
            if v == 'start':
                self.start = kmvar[v]
            elif v == 'end':
                self.end = kmvar[v]
            elif v == 'toTrace':
                self.toTrace = kmvar[v]
            elif v == 'outfile':
                self.outfile = kmvar[v]                
                
    def tstart(self):
        self.tracego = True

    def tstop(self):
        self.tracego = False

    def ifTrace(self, cond):
        if self.tracego and (self.start <= self.sim.now() <= self.end)\
           and cond:
            return True

    def thold(self, par):
        try:
            return 'delay: %s'%par[0][2]
        except:
            return 'delay: 0'
    thold = classmethod(thold)
    
    def trequest(self, par):
        res = par[0][2]
        if len(par[0]) == 4:
            priority = ' priority: ' + str(par[0][3])
        else:
            priority = ' priority: default'
        wQ = [x.name for x in res.waitQ]
        aQ = [x.name for x in res.activeQ]
        return '<%s> %s \n. . .waitQ: %s \n. . .activeQ: %s' % (res.name, priority, wQ, aQ)
    trequest = classmethod(trequest)
    
    def trelease(self, par):
        res = par[0][2]
        wQ = [x.name for x in res.waitQ]
        aQ = [x.name for x in res.activeQ]
        return '<%s> \n. . .waitQ: %s \n. . .activeQ: %s' % (res.name, wQ, aQ)
    trelease = classmethod(trelease)
    
    def tpassivate(self, par):
        return ""
    tpassivate = classmethod(tpassivate)

    def tactivate(self, par):
        pass
    tactivate = classmethod(tactivate)
    
    def twaitevent(self, par):
        evt = par[0][2]
        if type(evt) == list or type(evt) == tuple:
            enames = [x.name for x in evt]
            return 'waits for events <%s > '%enames
        else:
            return 'waits for event <%s > '%evt.name
    twaitevent = classmethod(twaitevent)
    
    def tqueueevent(self, par):
        evt = par[0][2]
        if type(evt) == list or type(evt) == tuple:
            enames = [x.name for x in evt]
            return 'queues for events <%s > '%enames          
        else:
            return 'queues for event <%s > '%evt.name
    tqueueevent = classmethod(tqueueevent)
    
    def tsignal(self, evt):
        wQ = [x.name for x in evt.waits]
        qQ = [x.name for x in evt.queues]
        return '<%s> \n. . .  occurred: %s\n. . .  waiting: %s\n. . .  queueing: %s'\
                %(evt.name, evt.occurred, wQ, qQ)
        pass
    tsignal = classmethod(tsignal)
    
    def twaituntil(self, par):
        condition = par[0][2]
        return 'for condition <%s > '%condition.func_name
    twaituntil = classmethod(twaituntil)
    
    def tget(self, par):
        buff = par[0][2]
        if len(par[0]) == 5:
            priority = ' priority: ' + str(par[0][4])
        else:
            priority = ' priority: default'
        if len(par[0]) == 3:
            nrToGet = 1
        else:
            nrToGet = par[0][3]
        toGet = 'to get: %s %s from' % (nrToGet, buff.unitName)
        getQ = [x.name for x in buff.getQ]
        putQ = [x.name for x in buff.putQ]
        try:
            inBuffer = buff.amount
        except:
            inBuffer = buff.nrBuffered
        return '%s <%s> %s \n. . .getQ: %s \n. . .putQ: %s \n. . .in buffer: %s'\
            %(toGet, buff.name, priority, getQ, putQ, inBuffer)
    tget = classmethod(tget)
    
    def tput(self, par):
        buff = par[0][2]
        if len(par[0]) == 5:
            priority = ' priority: ' + str(par[0][4])
        else:
            priority = ' priority: default'
        if len(par[0]) == 3:
            nrToPut = 1
        else:
            if type(par[0][3]) == type([]):
                nrToPut = len(par[0][3])
            else:
                nrToPut = par[0][3]
        getQ = [x.name for x in buff.getQ]
        putQ = [x.name for x in buff.putQ]
        toPut = 'to put: %s %s into' % (nrToPut, buff.unitName)
        try:
            inBuffer = buff.amount
        except:
            inBuffer = buff.nrBuffered
        return '%s <%s> %s \n. . .getQ: %s \n. . .putQ: %s \n. . .in buffer: %s'\
            %(toPut, buff.name, priority, getQ, putQ, inBuffer)
    tput = classmethod(tput)
    
    def recordEvent(self, command, whole):
        if self.ifTrace(Trace.commands[command] in self.toTrace):
            if not type(whole[0][0]) == tuple:
                print >> self.outfile, whole[0][1].sim.now(),\
                    Trace.commands[command],\
                    ' < ' + whole[0][1].name + ' > ',\
                    Trace.commandsproc[command](whole)
                if self._comment:
                    print >> self.outfile, '----', self._comment
            else:
                print >> self.outfile, whole[0][0][1].sim.now(),\
                         Trace.commands[command],\
                         ' < ' + whole[0][0][1].name + ' > '+\
                         Trace.commandsproc[command](whole[0])
                print >> self.outfile, '|| RENEGE COMMAND:'
                command1 = whole[0][1][0]
                print >> self.outfile, '||\t', Trace.commands[command1],\
                    ' < ' + whole[0][1][1].name + ' > ',\
                      Trace.commandsproc[command1]((whole[0][1],))
                if self._comment:
                    print >> self.outfile, '----', self._comment
                
        self._comment = None

    def recordInterrupt(self, who, victim):
        if self.ifTrace('interrupt' in self.toTrace):
            print >> self.outfile, '%s interrupt by: <%s > of: <%s >'\
                                   %(who.sim.now(),who.name, victim.name)
            if self._comment:
                print >> self.outfile, '----', self._comment
        self._comment = None
                
    def recordCancel(self, who, victim):
        if self.ifTrace('cancel' in self.toTrace):
            print >> self.outfile, '%s cancel by: <%s > of: <%s > '\
            %(who.sim.now(),who.name, victim.name)
            if self._comment:
                print >> self.outfile, '----', self._comment
        self._comment = None
        
    def recordActivate(self, who, when, prior):
        if self.ifTrace('activate' in self.toTrace):
            print >> self.outfile, '%s activate <%s > at time: %s prior: %s'\
                     %(who.sim.now(),who.name,when, prior)
            if self._comment:
                print >> self.outfile, '----', self._comment
        self._comment = None                                                                       

    def recordReactivate(self, who, when, prior):
        if self.ifTrace('reactivate' in self.toTrace):
            print >> self.outfile, '%s reactivate <%s > time: %s prior: %s'\
                     %(who.sim.now(),who.name,when, prior)
            if self._comment:
                print >> self.outfile, '----', self._comment
        self._comment = None
        
    def recordSignal(self, evt):
        if self.ifTrace('signal' in self.toTrace):
            print >> self.outfile, '%s event <%s > is signalled' \
                                   %(evt.sim.now(),evt.name)
            if self._comment:
                print >> self.outfile, '----', self._comment
        self._comment = None

    def tterminated(self, who):
        if self.ifTrace('terminated' in self.toTrace):
            print >> self.outfile, '%s <%s > terminated'\
                     %(who.sim.now(),who.name)
            if self._comment:
                print >> self.outfile, '----', self._comment
        self._comment = None        

    def ttext(self, par):
        self._comment = par
  
# For backward compatibility
Globals.sim = SimulationTrace()
trace = Globals.sim.trace
step = Globals.sim.step
peek = Globals.sim.peek
allMonitors = Globals.sim.allMonitors
allTallies = Globals.sim.allTallies
# End backward compatibility

if __name__ == '__main__':
    print 'SimPy.SimulationTrace %s' %__version__
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
        s=SimulationTrace()
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
        s=SimulationTrace()
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
        s=SimulationTrace()
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
        s=SimulationTrace()
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
        s=SimulationTrace()
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
        s=SimulationTrace()
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
        s=SimulationTrace()
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
        s=SimulationTrace()
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
        s=SimulationTrace()
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
        s=SimulationTrace()
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
        s=SimulationTrace()
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
