""" bank12_OO: Multiple runs of the bank with a Monitor""" 
from SimPy.Simulation import * 
from random import expovariate,seed

## Model components ------------------------

class Source(Process):
    """ Source generates customers randomly"""

    def generate(self,number,interval,resource,mon):       
        for i in range(number):
            c = Customer(name = "Customer%02d"%(i,),sim=self.sim)
            self.sim.activate(c,c.visit(b=resource,M=mon))          
            t = expovariate(1.0/interval)
            yield hold,self,t

class Customer(Process):
    """ Customer arrives, is served and leaves """
        
    def visit(self,b,M):       
        arrive = self.sim.now()
        yield request,self,b
        wait = self.sim.now()-arrive
        M.observe(wait)                                
        tib = expovariate(1.0/timeInBank)
        yield hold,self,tib
        yield release,self,b
 
## Experiment data -------------------------

maxNumber = 50
maxTime = 2000.0  # minutes                                    
timeInBank = 12.0   # mean, minutes
ARRint = 10.0     # mean, minutes
Nc = 2            # number of counters
theSeed = 393939

## Model  ----------------------------------
class BankModel(Simulation):
    def run(self):
        self.initialize()                          
        k = Resource(capacity=Nc,name="Clerk",sim=self)  
        wM = Monitor(sim=self)                                   
        s = Source('Source',sim=self)
        self.activate(s,s.generate(number=maxNumber,interval=ARRint, 
                          resource=k,mon=wM),at=0.0)         
        self.simulate(until=maxTime)
        return (wM.count(),wM.mean())                     

## Experiment/Result  ----------------------------------
modl=BankModel()
theseeds = [393939,31555999,777999555,319999771]         
for Sd in theseeds:
    seed(Sd)
    result = modl.run()
    print "Average wait for %3d completions was %6.2f minutes."% result  
