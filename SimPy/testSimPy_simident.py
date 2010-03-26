#!/usr / bin / env python
# coding=utf-8
from SimPy.Simulation  import *
from SimPy.MonitorTest import *
import unittest
# $Revision$ $Date$
"""testSimPy_simident.py
SimPy version 2.1
Unit tests of checks of correct use of sim parameter. 
2.1 introduces checks that two entities involved in a yield (e.g.
a Process and a Resource) belong to the same Simulation instance.

NOTE: This unit test set only works if __debug__ == True. If
Python is called with the -O or -OO parameter, the checks are not
being executed.

#'$Revision$ $Date$ kgm'

"""

simulationVersion=version
print "Under test: Simulation.py %s"%simulationVersion
__version__ = '2.1 $Revision$ $Date$ '
print 'testSimpy.py %s'%__version__
if not __debug__:
    print "Unit tests not executed -- run in __debug__ mode."
    
    