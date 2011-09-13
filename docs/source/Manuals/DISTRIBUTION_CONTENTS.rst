===================================
Contents of This SimPy Distribution
===================================

SimPy |release| contains the following files:

* SimPy            - Python code directory for the SimPy |release| package

        - Lister.py, a prettyprinter for class instances
        - Simulation.py, code for SimPy simulation
        - SimulationTrace.py, code for simulation with tracing
        - SimulationStep.py, code for executing simulations event-by-event
        - SimulationRT.py, code for synchronizing simulation time with wallclock time
        - SimulationGUIDebug.py, code for debugging/event stepping of models with a GUI
        - SimGUI.py, code for generating a Tk-based GUI for SimPy simulations
        - SimPlot.py, code for generating Tk-based plots (screen and Postscript)
        - __init__.py, initialisation of SimPy package
        - testSimPy.py, a unit test script for Simulation.py
        - testSimPyTrace, a unit test script for SimulationTrace.py
        - testSimPyRT.py, a unit test script for SimulationRT.py
        - testSimPyStep.py, a unit test script for SimulationStep.py
        - testSimPyOO.py, a unit test script for the Object Oriented (OO)
          API of Simulation.py
        - testSimPyTraceOO.py, a unit test script for the OO API of SimulationTrace.py
        - testSimPyRTOO.py, a unit test script for the OO API of SimulationRT.py
        - testSimPyStep.py, a unit test script for the OO API of SimulationStep.py
        - testRT_Behavior.py, a test program measuring the degree of RT synchronization for
          SimulationRT, and
        - testRT_Behavior_OO.py, an OO API version of that test program

* docs          - a directory containing the complete, browseable (HTML) documentation of SimPy.
   It includes tutorials and descriptions of accessing external packages from SimPy.
   **Click on index.html!**

* docs/examples - some SimPy models (in traditional and Object Oriented API)

    * Bankmodels - a sub-directory with the models of the Bank tutorials (in traditional and Object Oriented API)

 *  LICENSE.txt - GNU Lesser General Public Licence text
