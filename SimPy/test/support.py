# coding=utf-8

from SimPy import (Globals, Simulation, SimulationStep, SimulationTrace,
        SimulationRT)


def pytest_generate_tests(metafunc):
    if 'sim' in metafunc.funcargnames:
        # Execute tests using a dedicated simulation instance (SimPy OO style).
        metafunc.addcall(param='default')
        # Execute tests using a SimulationStep instance.
        metafunc.addcall(param='step')
        # Execute tests using a SimulationTrace instance.
        metafunc.addcall(param='trace')
        # Execute tests using a SimulationRT instance.
        metafunc.addcall(param='rt')

        # Execute tests using the global simulation object (SimPy 1.x style).
        metafunc.addcall(param='global-default')
        # Execute tests using the global SimulationStep object.
        metafunc.addcall(param='global-step')
        # Execute tests using the global SimulationTrace object.
        metafunc.addcall(param='global-trace')
        # Execute tests using the global SimulationRT object.
        metafunc.addcall(param='global-rt')


def pytest_funcarg__sim(request):
    if request.param == 'default':
        return Simulation.Simulation()
    elif request.param == 'step':
        return SimulationStep.SimulationStep()
    elif request.param == 'trace':
        return SimulationTrace.SimulationTrace()
    elif request.param == 'rt':
        return SimulationRT.SimulationRT()
    elif request.param.startswith('global'):
        if request.param.endswith('default'):
            Globals.sim = Simulation.Simulation()
        elif request.param.endswith('step'):
            Globals.sim = SimulationStep.SimulationStep()
        elif request.param.endswith('trace'):
            Globals.sim = SimulationTrace.SimulationTrace()
        elif request.param.endswith('rt'):
            Globals.sim = SimulationRT.SimulationRT()
        return Globals.sim
