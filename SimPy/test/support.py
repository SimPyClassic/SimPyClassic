# coding=utf-8

from SimPy import Globals, Simulation, SimulationStep, SimulationTrace
from SimPy import Globals


def pytest_generate_tests(metafunc):
    if 'sim' in metafunc.funcargnames:
        # Execute tests using the global simulation object (SimPy 1.x style).
        metafunc.addcall(param='global')
        # Execute tests using a dedicated simulation instance (SimPy OO style).
        metafunc.addcall(param='oo')
        # Execute tests using a SimulationStep instance.
        metafunc.addcall(param='step')
        # Execute tests using a SimulationTrace instance.
        metafunc.addcall(param='trace')


def pytest_funcarg__sim(request):
    if request.param == 'global':
        # Clear global simulation so that it can be used in multiple tests.
        Globals.sim.initialize()
        return Globals.sim
    elif request.param == 'oo':
        return Simulation.Simulation()
    elif request.param == 'step':
        return SimulationStep.SimulationStep()
    elif request.param == 'trace':
        return SimulationTrace.SimulationTrace()
