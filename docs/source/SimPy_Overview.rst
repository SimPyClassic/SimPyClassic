==============
SimPy Overview
==============

.. toctree::
   :maxdepth: 1

SimPy_ is a process-based discrete-event simulation language based on standard
Python and released under the GNU LGPL. It provides the modeller with
components of a simulation model including *processes*, for active components
like customers, messages, and vehicles, and  *resources*, for passive
components that form limited capacity congestion points like servers, checkout
counters, and tunnels. It also provides *monitor variables* to aid in gathering
statistics. Random variates are provided by the standard Python *random*
module.

SimPy is based on ideas from Simula and Simscript but uses standard Python. It
provides efficient implementation of co-routines using Python's generators
capability. It requires Python 2.3 or later, **but does not work yet with
Python 3.0**.

SimPy has been under development since 2002.

More information is available on the `SimPy Homepage`_ and the `SimPy wiki`_.

.. _SimPy: http://simpy.sourceforge.net/index.html
.. _`SimPy Homepage`: http://simpy.sourceforge.net/index.html
.. _`SimPy wiki`: http://sourceforge.net/apps/mediawiki/simpy/index.php?title=SimPy
.. _`Simpy page on Sourceforge`: http://sourceforge.net/projects/simpy/
