# coding=utf-8
"""
SimulationStep supports stepping through SimPy simulation event - by - event.
Based on generators.

"""
from SimPy.Simulation import *


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
