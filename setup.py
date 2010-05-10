#! /usr/bin/env python
from distutils.core import setup
setup(
      version = "2.1.0beta",
      author = "Klaus Muller, Tony Vignaux",
      author_email = "vignaux at user.sourceforge.net;kgmuller at users.sourceforge.net",
      description = "Release 2.1.0beta of SimPy simulation package",
      url = "http://SimPy.SourceForge.net",
      long_description=\
"""
SimPy 2.1.0 is a major re-release of SimPy 2.0. It repairs
a number of errors in SimPy 2.0.1 libraries, models and documentation.
There has been significant code refactoring in Simulation.py,
SimulationStep.py, SimulationTrace.py, SimulationRT.py, and Lib.py.
This resulted in a significant reduction of code to be maintained.

Documentation/tutorials on using the advanced OO API have been added.

SimPy is a process-based discrete-event simulation language
based on standard Python and released under the GNU LGPL. 

It provides the modeller with components of a simulation
model. These include processes, for active components like
customers, messages, and vehicles, and resources, for
passive components that form limited capacity congestion
points like servers, checkout counters, and tunnels. It
also provides monitor variables to aid in gathering
statistics. SimPy comes with extensive plotting capabilities.

The distribution contains in-depth documentation, tutorials,
and a large number of simulation models.

Simulation model developers are encouraged to share their
SimPy modeling techniques with the SimPy community. Please
post a message to the simpy-Users mailing list,

mailto:simpy-users at lists.sourceforge.net.

Subscribe to simpy-users mailing list:
http://lists.sourceforge.net/lists/listinfo/simpy-users

Software developers are also encouraged to interface SimPy with
other Python-accessible packages, such as GUI, data base or
mapping and to share these new capabilities with the
community under the GNU LGPL.
""",
      license = "GNU LGPL",
      name = "SimPy",
      packages = ["SimPy"],
      keywords = "simulation, discrete event simulation, process-oriented simulation",
      classifiers = [
          "Programming Language :: Python",
          "Operating System :: OS Independent",
          "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
          "Development Status :: 5 - Production/Stable",
          "Intended Audience :: Science/Research",
           "Topic :: Scientific/Engineering"
                      ]
      )
