"""
This file provides a global Simulation object and the global simulation methods
used by SimPy up to version 1.9.1.
"""
# $Revision: 136 $ $Date: 2008-11-01 11:18:13 +0100 (Sa, 01 Nov 2008) $
# SimPy version: 2.0

global sim
sim = None

def initialize():
    sim.initialize()

def now():
    return sim.now()

def stopSimulation():
    """Application function to stop simulation run"""
    sim.stopSimulation()

def _startWUStepping():
    """Application function to start stepping through simulation for waituntil construct."""
    sim._startWUStepping()

def _stopWUStepping():
    """Application function to stop stepping through simulation."""
    sim._stopWUStepping()

def activate(obj, process, at = 'undefined', delay = 'undefined', prior = False):
    """Application function to activate passive process."""
    sim.activate(obj, process, at, delay, prior)
    
def reactivate(obj, at = 'undefined', delay = 'undefined', prior = False):
    """Application function to reactivate a process which is active,
    suspended or passive."""
    sim.reactivate(obj, at, delay, prior)

def simulate(until = 0):
    return sim.simulate(until = until)
