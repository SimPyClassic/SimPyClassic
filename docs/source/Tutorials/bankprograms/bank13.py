""" bank13: Wait for the doorman to give a signal: *waitevent*"""
from SimPy.Simulation import *
from random import *

## Model components ------------------------

dooropen=SimEvent("Door Open")                                
class Doorman(Process):                                       
    """ Doorman opens the door"""
    def openthedoor(self):
        """ He will opens the door at fixed intervals"""
        for i in range(5):
            yield hold,self, 30.0                              
            dooropen.signal()                                     
            print "%7.4f You may enter"%(now(),)

class Source(Process):                                        
    """ Source generates customers randomly"""
    def generate(self,number,rate):       
        for i in range(number):
            c = Customer(name = "Customer%02d"%(i,))
            activate(c,c.visit(timeInBank=12.0))
            yield hold,self,expovariate(rate)

class Customer(Process):                                      
    """ Customer arrives, is served and leaves """
    def visit(self,timeInBank=10):       
        arrive = now()

        if dooropen.occurred:
            msg = '.'                                         
        else:
            msg = ' but the door is shut.'
        print "%7.4f %s: Here I am%s"%(now(),self.name,msg)
        yield waitevent,self,dooropen                         

        print "%7.4f %s: The door is open!"%(now(),self.name)

        wait = now()-arrive
        print "%7.4f %s: Waited %6.3f"%(now(),self.name,wait)

        yield request,self,counter
        tib = expovariate(1.0/timeInBank)
        yield hold,self,tib
        yield release,self,counter

        print "%7.4f %s: Finished    "%(now(),self.name)

## Experiment data -------------------------

maxTime = 400.0  # minutes                                    

counter = Resource(1,name="Clerk")

## Model  ----------------------------------

def model(SEED=393939):
    seed(SEED)

    initialize()
    doorman = Doorman()                                          
    activate(doorman,doorman.openthedoor())                    
    source = Source()                                                        
    activate(source,
             source.generate(number=5,rate=0.1),at=0.0)
    simulate(until=maxTime)


## Experiment  ----------------------------------

model()
