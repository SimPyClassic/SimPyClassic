""" bank07_OO: One Counter,random arrivals """
from SimPy.Simulation import *
from random import expovariate, seed

## Model components ------------------------

class Source(Process):
    """ Source generates customers randomly """

    def generate(self,number,meanTBA,resource):     
        for i in range(number):
            c = Customer(name = "Customer%02d"%(i,),sim=self.sim)
            self.sim.activate(c,c.visit(timeInBank=12.0,
                               res=resource))          
            t = expovariate(1.0/meanTBA)
            yield hold,self,t

class Customer(Process):
    """ Customer arrives, is served and  leaves """
        
    def visit(self,timeInBank=0,res=None):       
        arrive = self.sim.now()       # arrival time        
        print "%8.3f %s: Here I am     "%(now(),self.name)

        yield request,self,res                       
        wait = now()-arrive  # waiting time        
        print "%8.3f %s: Waited %6.3f"%(self.sim.now(),self.name,wait)
        yield hold,self,timeInBank               
        yield release,self,res                     
        
        print "%8.3f %s: Finished      "%(self.sim.now(),self.name)

## Experiment data -------------------------

maxNumber = 5                                      
maxTime = 400.0  # minutes                                
ARRint = 10.0    # mean, minutes

## Model -----------------------------------
class BankModel(Simulation):
   def run(self):
       self.initialize()
       k = Resource(name="Counter",unitName="Clerk",sim=self)     
       s = Source('Source',sim=self)
       self.activate(s,s.generate(number=maxNumber,            
                      meanTBA=ARRint, resource=k),at=0.0)        
       self.simulate(until=maxTime)
## Experiment ------------------------------
seed(99999)
BankModel().run()