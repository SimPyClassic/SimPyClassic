"""WidgetPacking_OO.py
Scenario:
In a factory, nProd widget-making machines produce widgets with a weight 
widgWeight (uniformly distributed [widgWeight-dWeight..widgWeight+dWeight])
on average every tMake minutes (uniform distribution 
[tmake-deltaT..tMake+deltaT]).A widget-packing machine packs widgets in tPack 
minutes into packages. Simulate for simTime minutes.

Model 1:
The widget-packer packs nWidgets into a package.

Model 2:
The widget-packer packs widgets into a package with package weight not
to exceed packMax. 
"""
from SimPy.Simulation import *
import random

## Experiment data -------------------------
nProd=2         #widget-making machines
widgWeight=20   #kilogrammes
dWeight=3       #kilogrammes
tMake=2         #minutes
deltaT=0.75     #minutes
tPack=0.25      #minutes per idget
initialSeed=1234567 #for random number stream
simTime=100     #minutes

print 'WidgetPacking'

## Model 1 components ----------------------

## Data
nWidgets=6      #widgets per package

class Widget:
    def __init__(self,weight):
        self.weight=weight
        
class WidgetMakerN(Process):
    def make(self,buffer):
        while True:
            yield hold,self,self.sim.r.uniform(tMake-deltaT,tMake+deltaT)
            yield put,self,buffer,1         # buffer 1 widget
        
class WidgetPackerN(Process):
    """Packs a number of widgets into a package"""
    def pack(self,buffer):
        while True:
            for i in range(nWidgets):
                yield get,self,buffer,1 #get widget
                yield hold,self,tPack   #pack it
            print "%s: package completed"%self.sim.now()

## Model 1 ---------------------------------
class WidgetPackingModel1(Simulation):
    def run(self):
        print "Model 1: pack %s widgets per package"%nWidgets
        self.initialize()
        self.r=random.Random()
        self.r.seed(initialSeed)
        wBuffer=Level(name="WidgetBuffer",capacity=500,sim=self)
        for i in range(nProd):
            wm=WidgetMakerN(name="WidgetMaker%s"%i,sim=self)
            self.activate(wm,wm.make(wBuffer))
        wp=WidgetPackerN(name="WidgetPacker",sim=self)
        self.activate(wp,wp.pack(wBuffer))
        self.simulate(until=simTime)

## Experiment ------------------------------
WidgetPackingModel1().run()

## Model 2 components ----------------------

## Data
packMax=120     #kilogrammes per package (max)

class WidgetMakerW(Process):
    """Produces widgets"""
    def make(self,buffer):
        while True:
            yield hold,self,self.sim.r.uniform(tMake-deltaT,tMake+deltaT)
            widgetWeight=self.sim.r.uniform(widgWeight-dWeight,widgWeight+dWeight)
            yield put,self,buffer,[Widget(weight=widgetWeight)] #buffer widget
        
class WidgetPackerW(Process):
    """Packs a number of widgets into a package"""
    def pack(self,buffer):
        weightLeft=0
        while True:
            packWeight=weightLeft   #pack a widget which did not fit 
                                    #into previous package
            weightLeft=0
            while True:
                yield get,self,buffer,1 #get widget
                weightReceived=self.got[0].weight
                if weightReceived+packWeight<=packMax:
                    yield hold,self,tPack   #pack it
                    packWeight+=weightReceived
                else:
                    weightLeft=weightReceived #for next package
                    break
                print "%s: package completed. Weight=%6.2f kg"%(self.sim.now(),packWeight)

## Model 2 ---------------------------------
class WidgetPackingModel2(Simulation):
    def run(self):
        print "\nModel 2: pack widgets up to max package weight of %s"%packMax
        self.initialize()
        self.r=random.Random()
        self.r.seed(initialSeed)
        wBuffer=Store(name="WidgetBuffer",capacity=500,sim=self)
        for i in range(nProd):
            wm=WidgetMakerW(name="WidgetMaker%s"%i,sim=self)
            self.activate(wm,wm.make(wBuffer))
        wp=WidgetPackerW(name="WidgetPacker",sim=self)
        self.activate(wp,wp.pack(wBuffer))
        self.simulate(until=simTime)
        
## Experiment ------------------------------
WidgetPackingModel2().run()
