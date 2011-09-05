Visualize model events and states using **SimulationGUIDebug**
===============================================================

Brian Jacobs, Kip Nicol and Logan Rockmore, a group of senior students of
Professor Matloff at U. of California at Davis  have  developed a great tool
for gaining insight into the event-by-event execution of a SimPy model. It is
equally useful for teaching and program debugging.

The **SimulationGUIDebug** tool is a SimPy module which shows a GUI with a
model's event list and the status of selected Process and Resource instances
over time. The user can interactively step from event to event and set
breakpoints at one or more points in (simulated) time.

**SimulationGUIDEbug** can be used as a standalone debuger or together with
Python debuggers such as PDB.

The tool was originally written for SimPy 1.9. It has been ported to SimPy 2.0.

The tool's documentation (user guide, design overview, etc.) is `here`_ .

.. _here: _static/SimGUIDebug2_0.pdf
