SimPy
=====

SimPy is a process-based discrete-event simulation language based on standard
Python and released under the GNU LGPL.

It provides the modeller with components of a simulation model. These include
processes for active components like customers, messages and vehicles as well
as  resources for passive components that form limited capacity congestion
points (like servers, checkout counters and tunnels). It also provides monitor
variables to aid in gathering statistics. SimPy comes with extensive plotting
capabilities.

The distribution contains in-depth documentation, tutorials, and a large number
of simulation models.

Simulation model developers are encouraged to share their SimPy modeling
techniques with the SimPy community. Please post a message to the `simpy-Users
mailing list <mailto:simpy-users at lists.sourceforge.net>`_

Subscribe to simpy-users mailing list:
http://lists.sourceforge.net/lists/listinfo/simpy-users

Software developers are also encouraged to interface SimPy with other Python-
accessible packages, such as GUI, database or mapping and to share these new
capabilities with the community under the GNU LGPL.


Installation
------------

SimPy requires Python 2.3 or above. Python 3 is not yet supported, but we are
working on it.

You can install SimPy easily via `PIP <http://pypi.python.org/pypi/pip>`_
(or ``easy_install``)::

    $ pip install SimPy
    $ # or:
    $ easy_install SimPy

You can also download and install SimPy manually::

    $ cd where/you/put/simpy/
    $ python setup.py install


If you want to upgrade an existing installation of SimPy, just add the ``-U``
option to *pip* or *easy_install*, e.g.::

    $ pip install -U SimPy


Getting started
---------------

Run one or more of the programs under *docs/examples/* to see whether Python
finds the SimPy module. If you get an error message like *ImportError: No
module named SimPy*, check if the SimPy packages exists in your site-packages
folder (like /Lib/site-packages).

The tutorial and manuals are in the *docs/html* folder. Many users have
commented that the Bank tutorials are valuable in getting users started on
building their own simple models. Even a few lines of Python and SimPy can
model significant real systems.

For more help, contact the `SimPy-Users mailing list
<mailto:simpy-users@lists.sourceforge.net>`_. SimPy users are pretty helpful.

Enjoy simulation programming in SimPy!
