""" bank20: One counter with a priority customer """
from SimPy.Simulation import *
from random import expovariate, seed

## Model components ------------------------

class Source(Process):
    """ Source generates customers randomly"""

    def generate(self,number,interval):       
        for i in range(number):
            c = Customer(name = "Customer%02d"%(i,))
            activate(c,c.visit(timeInBank=12.0,P=0))            
            t = expovariate(1.0/interval)
            yield hold,self,t

class Customer(Process):
    """ Customer arrives, is served and  leaves """
        
    def visit(self,timeInBank=0,P=0):                           
        arrive=now()       # arrival time                       
        Nwaiting=len(counter.waitQ)
        print "%8.3f %s: Queue is %d on arrival"%(now(),self.name,Nwaiting)

        yield request,self,counter,P                            
        wait=now()-arrive  # waiting time                       
        print "%8.3f %s: Waited %6.3f"%(now(),self.name,wait)
        yield hold,self,timeInBank
        yield release,self,counter                              

        print "%8.3f %s: Completed"%(now(),self.name)

## Experiment data -------------------------

maxTime = 400.0  # minutes                                   

## Model  ----------------------------------

def model():
    global counter                                              
    seed(98989)
    counter = Resource(name="Karen", qType=PriorityQ)           
    initialize()
    source=Source('Source')
    activate(source,
             source.generate(number=5, interval=10.0),at=0.0)    
    guido = Customer(name = "Guido     ")                       
    activate(guido,guido.visit(timeInBank=12.0,P=100),at=23.0)     
    simulate(until=maxTime)

## Experiment  ----------------------------------

model()
