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

2. Download and unpack the SimPy archive into a folder (using option "Use folder
   names" in WinZip, "Re-create folders" in Linux Archive Manager, or
   similar option in your unpacker). This will create a SimPy-2.1.0 folder 
   with all source code and documentation.	
   
3. Now you must install SimPy.
   You should always run the Python setup command from the distribution root directory,
   i.e. the top-level subdirectory that the module source distribution unpacks
   into. This subdirectory contains a file `setup.py`. 
   
   3.1 Normal installation on MS Windows:
       Open a command prompt window ("DOS box"), and run (assuming your SimPy top-level 
       directory is `c:\SimPy-2.1.0`):

         cd c:\SimPy-2.1.0
         python setup.py install

       This will install the SimPy programs in a folder on the Python search path 
       (typically `\Lib\site-packages`). 
     
   3.2 Normal installation on Linux or Unix: 
       If you've just downloaded the SimPy 2.1.0 source distribution
       `SimPy-2.1.0.tar.gz` onto a Linux/Unix system, the normal thing to do is:
   
         gunzip -c SimPy2.1.0.tar.gz | tar xf -    # unpacks into directory SimPy-2.1.0
         cd SimPy-2.1.0
         python setup.py install

       This will install the SimPy programs in a folder on the Python search path 
       (typically `/Lib/site-packages`). 
       
       Note: On Linux, installing into `/Lib/site-packages` normally 
       requires root privileges.
   
   3.3 Alternative installation on Windows, Linux/Unix:
       On a Linux/Unix system you might not have permission to write to the standard 
       directory `/Lib/site-packages`.  Or you might wish to try out SimPy 2.1.0 
       before making it a standard part of your local Python installation.  
       This is especially true when upgrading a SimPy distribution already present: 
       you want to make sure your existing base of scripts still works with the 
       new version before actually upgrading.
       
       Installing a new SimPy distribution to a non-standard folderis as simple as:

          python setup.py install --home=<dir>

       where you can supply any directory you like for the :option:`--home` option.  On
       Linux/Unix, lazy typists can just type a tilde (``~``); the `install` command
       will expand this to your home directory::

         python setup.py install --home=~

       The `--home` option defines the installation base directory.  Files are
       installed to `{home}/lib/python`.


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

