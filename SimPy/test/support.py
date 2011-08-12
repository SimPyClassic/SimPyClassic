# coding=utf-8

from SimPy.Simulation import Simulation
from SimPy import Globals


def pytest_generate_tests(metafunc):
    if 'sim' in metafunc.funcargnames:
        # Execute tests using the global simulation object (SimPy 1.x style).
        metafunc.addcall(param='global')
        # Exeucte tests using a dedicated simulation instance (SimPy OO style).
        metafunc.addcall(param='oo')


def pytest_funcarg__sim(request):
    if request.param == 'global':
        # Clear global simulation so that it can be used in multiple tests.
        Globals.sim.initialize()
        return Globals.sim
    elif request.param == 'oo':
        return Simulation()
