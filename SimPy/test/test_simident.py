# coding=utf-8

"""
Unit tests of checks of correct use of sim parameter.
2.1 introduces checks that two entities involved in a yield (e.g.
a Process and a Resource) belong to the same Simulation instance.
"""

from SimPy.Simulation  import *


class Activatetest(Process):
    """Used in testActivate.
    """
    def run(self):
        yield hold,self,0

class Requesttest(Process):
    """Used in testRequest.
    """
    def run(self,res):
        yield request,self,res

class PutStoretest(Process):
    """Used in testPutStore.
    """
    def run(self,store):
        yield put,self,store,[1]

class GetStoretest(Process):
    """Used in testGetStore.
    """
    def run(self,store):
        yield get,self,store,1

class PutLeveltest(Process):
    """Used in testPutLevel.
    """
    def run(self,level):
        yield put,self,level,1

class GetLeveltest(Process):
    """Used in testGetLevel.
    """
    def run(self,level):
        yield get,self,level,1

class Waiteventtest(Process):
    """Used in testWaitevent.
    """
    def run(self,event):
        yield waitevent,self,event

class Queueeventtest(Process):
    """Used in testQueueevent.
    """
    def run(self,event):
        yield queueevent,self,event

def test_activate():
    """Test of "activate" call"""
    s = Simulation()
    s.initialize()
    r = Activatetest(sim=s)
    try:
        activate(r,r.run()) ## missing s.
    except FatalSimerror:
        pass
    else:
        assert False, "expected FatalSimerror"
    s.simulate(until=1)

def test_request():
    """Test of "yield request,self,res" """
    s = Simulation()
    s.initialize()
    res = Resource( ) # wrong sim
    r = Requesttest(sim=s)
    s.activate(r,r.run(res = res))
    try:
        s.simulate(until=1)
    except FatalSimerror:
        pass
    else:
        assert False, "expected FatalSimerror"

def test_put_store():
    """Test of "yield put,self,store" """
    s = Simulation()
    s.initialize()
    store = Store( ) # wrong sim
    r = PutStoretest(sim=s)
    s.activate(r,r.run(store = store))
    try:
        s.simulate(until=1)
    except FatalSimerror:
        pass
    else:
        assert False, "expected FatalSimerror"

def test_put_level():
    """Test of "yield put,self,level" """
    s = Simulation()
    s.initialize()
    levl = Level( ) # wrong sim
    r = PutLeveltest(sim=s)
    s.activate(r,r.run(level = levl))
    try:
        s.simulate(until=1)
    except FatalSimerror:
        pass
    else:
        assert False, "expected FatalSimerror"

def test_get_store():
    """Test of "yield get,self,store" """
    s = Simulation()
    s.initialize()
    store = Store( ) # wrong sim
    r = GetStoretest(sim=s)
    s.activate(r,r.run(store = store))
    try:
        s.simulate(until=1)
    except FatalSimerror:
        pass
    else:
        assert False, "expected FatalSimerror"

def test_get_level():
    """Test of "yield get,self,level" """
    s = Simulation()
    s.initialize()
    levl = Level( ) # wrong sim
    r = GetLeveltest(sim=s)
    s.activate(r,r.run(level = levl))
    try:
        s.simulate(until=1)
    except FatalSimerror:
        pass
    else:
        assert False, "expected FatalSimerror"

def test_waitevent():
    """Test of "yield waitevent,self,evt" """
    s = Simulation()
    s.initialize()
    evt = SimEvent() ## wrong sim
    w = Waiteventtest(sim = s)
    s.activate(w,w.run(event = evt))
    try:
        s.simulate(until=1)
    except FatalSimerror:
        pass
    else:
        assert False, "expected FatalSimerror"

def test_queueevent():
    """Test of "yield queueevent,self,evt" """
    s = Simulation()
    s.initialize()
    evt = SimEvent() ## wrong sim
    w = Queueeventtest(sim = s)
    s.activate(w,w.run(event = evt))
    try:
        s.simulate(until=1)
    except FatalSimerror:
        pass
    else:
        assert False, "expected FatalSimerror"
