#! /usr/bin/env python
from distutils.core import setup
setup(
      version="1.9.1",
      author="Klaus Muller, Tony Vignaux",
      author_email="vignaux@user.sourceforge.net;kgmuller@users.sourceforge.net",
      description="Version 1.9.1 of SimPy simulation package",
      long_description=\
"""
Release 1.9.1 of SimPy is a bug-fix release of 1.9. It cures the following bugs:

- excessive circular garbage, leading to large memory requirements,
- runtime error when executing preempts of process holding hultiple resources.

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

mailto:simpy-users@lists.sourceforge.net.

Subscribe to simpy-users mailing list:
http://lists.sourceforge.net/lists/listinfo/simpy-users

Software developers are also encouraged to interface SimPy with
other Python-accessible packages, such as GUI, data base or
mapping and to share these new capabilities with the
community under the GNU LGPL.
""",
      license="GNU LGPL",
      name="SimPy",
      url="simpy.sourceforge.net",
      packages=["SimPy"]
      )
