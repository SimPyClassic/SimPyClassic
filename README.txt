=================================================
 README: SimPy A Python-based simulation package
=================================================

:Authors: - Tony Vignaux <Vignaux@users.sourceforge.net>
          - Klaus Muller <Muller@users.sourceforge.net>
:SimPy version: 1.9.1
:SimPy Web-site: http://simpy.sourceforge.net/
:SimPy wiki: http://www.mcs.vuw.ac.nz/cgi-bin/wiki/SimPy
:Python-Version: 2.3 and later
:Revision: $Revision: 1.1.1.19 $
:Date: $Date: 2008/03/15 12:25:50 $

SimPy is a process-based discrete-event simulation language based on
standard Python and released under the GNU LGPL. 

It provides the modeller with components of a simulation model. These
include processes, for active components like customers, messages, and
vehicles, and resources, for passive components that form limited
capacity congestion points like servers, checkout counters, and
tunnels. It also provides monitor variables to aid in gathering
statistics.

SimPy can be downloaded from the "SimPy web-site": http://simpy.sourceforge.net.

Simulation model developers are encouraged to share their SimPy
modeling techniques with the SimPy community. Please "post a message
to the simpy-Users mailing list",
mailto:simpy-users@lists.sourceforge.net.

"Subscribe to simpy-users mailing list.", http://lists.sourceforge.net/lists/listinfo/simpy-users

Software developers are encouraged to interface SimPy with other
Python-accessible packages, such as GUI, data base or mapping and to
share these new capabilities with the community under the GNU GPL.

Feature requests for future SimPy versions should be sent to "Klaus
G. Muller", mailto:kgmuller at users.sourceforge.net, or "Tony Vignaux",
mailto:vignaux at users.sourceforge.net.

SimPy-1.9.1 contains the following files:

 * README.txt         - This file
 * HISTORY.txt        - a history of releases
 * INSTALLATION.txt   - a simple installation guide
 * COMPATIBILITY.txt  - a statement on SimPy compatibility with other Python
   modules/packages
 * CHANGES_FROM_PREVIOUS_VERSION.txt - a high level description of 
   differences between versions 1.9.1 and 1.9
 * SimPy            - Python code directory for the SimPy-1.9.1 package

        - Lister.py, a prettyprinter for class instances
        - Simulation.py, code for SimPy simulation
        - SimulationTrace.py, code for SimPy tracing
        - SimulationStep.py, code for executing simulations event-by-event
        - SimulationRT.py, code for synchronizing simulation time with wallclock time
        - SimGUI.py, code for generating a Tk-based GUI for SimPy simulations
        - SimPlot.py, code for generating Tk-based plots (screen and Postscript)
        - __init__.py, initialisation of SimPy package
        - testSimPy.py, a unit test script for Simulation.py
        - testSimPy.Trace, a unit test script for SimulationTrace.py
        - testSimPyRT.py, a unit test script for SimulationRT.py 
        - testSimPyStep.py, a unit test script for SimulationStep.py     

 * SimPyDocs          - a directory containing copies of:
 
        - the Cheatsheet (PDF, MS Excel, reST), 
        - the Manual (html, PDF, reST)
        - a Short Manual, describing only the basic SimPy facilities (html, PDF, reST)
        - the SimulationTrace manual (html, reST)
        - the SimulationRT manual  (html, reST)
        - the SimulationStep manual (html, reST)
        - TheBank tutorial (html, PDF)
        - TheBank2 tutorial (html, PDF)
        - a sub-directory "bankprograms" with the Bank programs
        - a sub-directory "Interfacing"
        
          - a sub-directory ProductionQualityPlotting with a
            document on interfacing to matplotlib for generating
            publication-quality plots
            
        - a sub-directory "SimGUI" with the SimGUI manual and examples
        - a sub-directory "SimPlot" with the SimPlot manual and examples
        - a sub-directory "SimPy_Sourcecode_Documentation", browseable (HTML)
          documentation of all SimPy code.

 * SimPyModels      - some SimPy models
 * LGPLlicense.html - GNU Lesser General Public Licence text
 * setup.py	     	- setup script (distutils)

:Date: $Date: 2008/03/15 12:25:50 $
:Revision: $Revision: 1.1.1.19 $


