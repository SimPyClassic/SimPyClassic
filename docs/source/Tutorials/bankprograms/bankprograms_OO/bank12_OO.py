""" bank12_OO: Multiple runs of the bank with a Monitor""" 
from SimPy.Simulation import Simulation,Process,Resource,Monitor,hold,\
                               request,release 
from random import expovariate,seed

## Model components ------------------------

class Source(Process):
    """ Source generates customers randomly"""

    def generate(self,number,interval):       
        for i in range(number):
            c = Customer(name = "Customer%02d"%(i,),sim=self.sim)
            self.sim.activate(c,c.visit(b=self.sim.k))          
            t = expovariate(1.0/interval)
            yield hold,self,t

class Customer(Process):
    """ Customer arrives, is served and leaves """
        
    def visit(self,b):       
        arrive = self.sim.now()
        yield request,self,b
        wait = self.sim.now()-arrive
        self.sim.wM.observe(wait)                                
        tib = expovariate(1.0/timeInBank)
        yield hold,self,tib
        yield release,self,b

## Model  ----------------------------------

class BankModel(Simulation):
    def run(self,aseed):
        self.initialize()
        seed(aseed)        
        self.k = Resource(capacity=Nc,name="Clerk",sim=self)  
        self.wM = Monitor(sim=self)                                   
        s = Source('Source',sim=self)
        self.activate(s,s.generate(number=maxNumber,interval=ARRint),at=0.0)         
        self.simulate(until=maxTime)
        return (self.wM.count(),self.wM.mean())  
 
## Experiment data -------------------------

maxNumber = 50
maxTime = 2000.0  # minutes                                    
timeInBank = 12.0   # mean, minutes
ARRint = 10.0     # mean, minutes
Nc = 2            # number of counters
seedVals = [393939,31555999,777999555,319999771] 

## Experiment/Result  ----------------------------------

modl = BankModel()        
for Sd in seedVals:
    modl.run(aseed=Sd)
    moni = modl.wM
    print "Average wait for %3d completions was %6.2f minutes."% (moni.count(),moni.mean())
