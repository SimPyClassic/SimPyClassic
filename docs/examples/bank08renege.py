""" bank08

 A counter with a random service time
 and customers who renege. Based on the program bank08.py
 from TheBank tutorial. (KGM)
"""
from SimPy.Simulation  import *
from random import expovariate, seed, uniform

## Model components ------------------------

class Source(Process):
    """ Source generates customers randomly"""

    def generate(self,number,interval,counter):       
        for i in range(number):
            c = Customer(name = "Customer%02d"%(i,))
            activate(c,c.visit(counter,timeInBank=12.0))
            t = expovariate(1.0/interval)
            yield hold,self,t

class Customer(Process):
    """ Customer arrives, is served and leaves """
        
    def visit(self,counter,timeInBank=0):       
        arrive=now()
        print "%7.4f %s: Here I am     "%(now(),self.name)

        yield (request,self,counter),(hold,self,Customer.patience())

        if self.acquired(counter):
            wait=now()-arrive
            print "%7.4f %s: Waited %6.3f"%(now(),self.name,wait)
            tib = expovariate(1.0/timeInBank)            
            yield hold,self,tib                          
            yield release,self,counter
            print "%7.4f %s: Finished"%(now(),self.name)
        else:
            wait=now()-arrive
            print "%7.4f %s: RENEGED after %6.3f"%(now(),self.name,wait)            
        
    def fpatience(minpatience=0,maxpatience=10000000000):
        while True:
            yield uniform(minpatience,maxpatience)
    fpatience=staticmethod(fpatience)

## Model ---------------------------------------------

def model():                                   
    counter = Resource(name="Karen") 
    pat=Customer.fpatience(minpatience=1,maxpatience=3)
    Customer.patience=pat.next
    initialize()
    source = Source('Source')
    activate(source,source.generate(NumCustomers,
                                    interval=IntervalCustomers,
                                    counter=counter))
    simulate(until=maxTime)

## Experiment data -------------------------

maxTime = 400.0
theseed = 12345
NumCustomers = 5
IntervalCustomers = 10.0
## Experiment ------------------------------

seed(theseed)
print 'bank08renege'
model()                               

