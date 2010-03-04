===================
INSTALLATION: SimPy
===================

:Authors: - Tony Vignaux <Vignaux@users.sourceforge.net>
          - Klaus Muller <Muller@users.sourceforge.net>

:SimPy release: 2.1.0
:SimPy Web-site: http://simpy.sourceforge.net/
:Python-Version: 2.3+ (but NOT 3.0)
:Revision: $Revision$
:Date: $Date$


This file describes the installation of SimPy 

In order to install SimPy on your system, you will need to perform the
following steps:

1. Check that you have Python 2.3 or a later version installed on your
   system. If necessary, download it from http://www.python.org and
   install it.

2. Download and unpack the SimPy archive into a folder (using option
   "Use folder names" in WinZip, "Re-create folders" in Linux Archive
   Manager, or similar option in your unpacker). This will create a
   "SimPy-2.1.0" folder with all source code and documentation.

3. Run "python setup.py install" in that folder. This 
   will install the SimPy programs in a folder on the Python 
   search path (typically /Lib/site-packages). 

4. Run one or more of the programs under "SimPy/SimPyModels" to see
   whether Python finds the SimPy module. If you get an error message
   like "ImportError: No module named SimPy", move the SimPy folder
   into a directory which you know to be on the Python module search
   path (like /Lib/site-packages).

5. The tutorial and manuals are in the "SimPy/SimPyDocs"
   folder. Start by accessing index.html with your browser.

6. Many users have commented that the Bank tutorials are valuable in
   getting users started on building their own simple models.  Even a
   few lines of Python and SimPy can model significant real systems.

7. For more help, contact the Simpy-Users mailing list,
   mailto:simpy-users at lists.sourceforge.net. SimPy users are pretty
   helpful.

Enjoy simulation programming in SimPy!

