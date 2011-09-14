============
Installation
============

This file describes the installation of SimPy |release|.

1. Check that you have Python 2.3 or above. Python 3 is not yet supported, but we are
   working on it. If necessary, download Python from http://www.python.org and
   install it.

2. Download and unpack the SimPy archive into a folder (using option "Use
   folder names" in WinZip, "Re-create folders" in Linux Archive Manager, or
   similar option in your unpacker). This will create a SimPy-|release| folder with
   all source code and documentation.	

3. You can install SimPy easily via `PIP <http://pypi.python.org/pypi/pip>`_
(or ``easy_install``)::

    $ pip install SimPy-|release|
    $ # or:
    $ easy_install SimPy-|release|

   Remember on Linux/MacOS/Unix you may need *root* privileges to be install
   SimPy. This also applies to the installing SimPy manually as described
   below.
  
   You can also download and install SimPy manually::

    $ cd where/you/put/simpy/SimPy-|release|
    $ python setup.py install

   You can install a new SimPy distribution to a non-standard folder::

    $ cd where/you/put/simpy/SimPy-|release|
    $ python setup.py install --home<dir>

    This is useful if you do not have permission perform the installation as
    described above.


4. Run one or more of the programs under *docs/examples to see
   whether Python finds the SimPy module. If you get an error message
   like *ImportError: No module named SimPy*, move the SimPy folder
   into a directory which you know to be on the Python module search
   path (like /Lib/site-packages).

5. The tutorial and manuals are in the *docs/html* folder. Many users have
   commented that the Bank tutorials are valuable in getting users started on
   building their own simple models. Even a few lines of Python and SimPy can
   model significant real systems.

For more help, contact the `SimPy-Users mailing list
<mailto:simpy-users@lists.sourceforge.net>`_. SimPy users are pretty helpful.


Enjoy simulation programming in SimPy!
