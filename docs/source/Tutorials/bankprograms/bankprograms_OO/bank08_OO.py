""" bank08_OO: A counter with a random service time """
from SimPy.Simulation import Simulation,Process,Resource,hold,request,release
from random import expovariate, seed

## Model components ------------------------           

class Source(Process):
    """ Source generates customers randomly """

    def generate(self,number,meanTBA):         
        for i in range(number):
            c = Customer(name = "Customer%02d"%(i,),sim=self.sim)
            self.sim.activate(c,c.visit(b=self.sim.k))              
            t = expovariate(1.0/meanTBA)               
            yield hold,self,t

class Customer(Process):
    """ Customer arrives, is served and leaves """
        
    def visit(self,b):                                
        arrive = self.sim.now()
        print "%8.4f %s: Here I am     "%(self.sim.now(),self.name)
        yield request,self,b                          
        wait = self.sim.now()-arrive
        print "%8.4f %s: Waited %6.3f"%(self.sim.now(),self.name,wait)
        tib = expovariate(1.0/timeInBank)            
        yield hold,self,tib                          
        yield release,self,b                         
        print "%8.4f %s: Finished      "%(self.sim.now(),self.name)
        
## Experiment data -------------------------         

maxNumber = 5
maxTime = 400.0 # minutes                                     
timeInBank=12.0 # mean, minutes                      
ARRint = 10.0   # mean, minutes                      

## Experiment ------------------------------
seed(0)

sim = Simulation()
sim.initialize()
sim.k = Resource(name="Counter",unitName="Clerk",sim=sim)       
s = Source('Source',sim=sim)
sim.activate(s,s.generate(number=maxNumber,meanTBA=ARRint),at=0.0)           
sim.simulate(until=maxTime)
