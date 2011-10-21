""" bank07_OO: One Counter,random arrivals """
from SimPy.Simulation import Simulation,Process,hold,Resource,request,release
from random import expovariate, seed

## Model components ------------------------

class Source(Process):
    """ Source generates customers randomly """

    def generate(self,number,meanTBA):     
        for i in range(number):
            c = Customer(name = "Customer%02d"%(i,),sim=self.sim)
            self.sim.activate(c,c.visit(timeInBank=12.0,
                               res=self.sim.k))          
            t = expovariate(1.0/meanTBA)
            yield hold,self,t

class Customer(Process):
    """ Customer arrives, is served and  leaves """
        
    def visit(self,timeInBank=0,res=None):       
        arrive = self.sim.now()       # arrival time        
        print "%8.3f %s: Here I am     "%(self.sim.now(),self.name)

        yield request,self,res                       
        wait = self.sim.now()-arrive  # waiting time        
        print "%8.3f %s: Waited %6.3f"%(self.sim.now(),self.name,wait)
        yield hold,self,timeInBank               
        yield release,self,res                     
        
        print "%8.3f %s: Finished      "%(self.sim.now(),self.name)

## Experiment data -------------------------

maxNumber = 5                                      
maxTime = 400.0  # minutes                                
ARRint = 10.0    # mean, minutes

## Experiment ------------------------------
seed(0)

sim = Simulation()
sim.initialize()
sim.k = Resource(name="Counter",unitName="Clerk",sim=sim)     
s = Source('Source',sim=sim)
sim.activate(s,s.generate(number=maxNumber, meanTBA=ARRint),at=0.0)        
sim.simulate(until=maxTime)
