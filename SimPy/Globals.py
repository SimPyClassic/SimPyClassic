# coding=utf-8
"""
This file provides a global Simulation object and the global simulation methods
used by SimPy up to version 1.9.1.

"""
global sim
sim = None

def initialize():
    sim.initialize()

def now():
    return sim.now()

def stopSimulation():
    """Application function to stop simulation run"""
    sim.stopSimulation()

def allEventNotices():
    """Returns string with eventlist as;
            t1: processname, processname2
            t2: processname4, processname5, . . .
                . . .  .
        """
    return sim.allEventNotices()

def allEventTimes():
    """Returns list of all times for which events are scheduled.
    """
    return sim.allEventTimes()

def startCollection(when = 0.0, monitors = None, tallies = None):
    """Starts data collection of all designated Monitor and Tally objects
    (default = all) at time 'when'.
    """
    sim.startCollection( when = when, monitors = monitors, tallies = tallies)

def _startWUStepping():
    """Application function to start stepping through simulation for waituntil
    construct."""
    sim._startWUStepping()

def _stopWUStepping():
    """Application function to stop stepping through simulation."""
    sim._stopWUStepping()

def activate(obj, process, at = 'undefined', delay = 'undefined',
              prior = False):
    """Application function to activate passive process."""
    sim.activate(obj, process, at = at, delay = delay, prior = prior)

def reactivate(obj, at = 'undefined', delay = 'undefined', prior = False):
    """Application function to reactivate a process which is active,
    suspended or passive."""
    sim.reactivate(obj, at = at, delay = delay, prior = prior)

def simulate(until = 0):
    return sim.simulate(until = until)
