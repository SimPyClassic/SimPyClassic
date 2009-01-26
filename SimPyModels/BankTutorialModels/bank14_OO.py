"""bank14_OO: *waituntil* the Bank door opens"""
from SimPy.Simulation import *
from random import expovariate,seed

## Model components ------------------------

door = 'Shut'                                                 
def dooropen():                                               
    return door=='Open'

class Doorman(Process):                                       
    """ Doorman opens the door"""
    def openthedoor(self):
        """ He will open the door when he arrives"""
        global door
        yield hold,self,expovariate(1.0/10.0)                 
        door = 'Open'                                           
        print "%7.4f Doorman: Ladies and "\
              "Gentlemen! You may all enter."%(self.sim.now(),)

class Source(Process):                                        
    """ Source generates customers randomly"""
    def generate(self,number,rate):       
        for i in range(number):
            c = Customer(name = "Customer%02d"%(i,),sim=self.sim)
            self.sim.activate(c,c.visit(timeInBank=12.0))
            yield hold,self,expovariate(rate)

class Customer(Process):                                      
    """ Customer arrives, is served and leaves """
    def visit(self,timeInBank=10):       
        arrive = self.sim.now()

        if dooropen():
            msg = ' and the door is open.'         
        else:
            msg = ' but the door is shut.'
        print "%7.4f %s: Here I am%s"%(self.sim.now(),self.name,msg)

        yield waituntil,self,dooropen                         

        print "%7.4f %s: I can  go in!"%(self.sim.now(),self.name)     
        wait = self.sim.now()-arrive
        print "%7.4f %s: Waited %6.3f"%(self.sim.now(),self.name,wait)

        yield request,self,self.sim.counter
        tib = expovariate(1.0/timeInBank)
        yield hold,self,tib
        yield release,self,self.sim.counter

        print "%7.4f %s: Finished    "%(self.sim.now(),self.name)

## Experiment data -------------------------

maxTime = 2000.0   # minutes                                     

## Model  ----------------------------------
class BankModel(Simulation):
    def run(self):
        self.initialize()
        self.counter = Resource(1,name="Clerk",sim=self)
        door = 'Shut'
        doorman=Doorman(sim=self)                                          
        self.activate(doorman,doorman.openthedoor())                    
        source = Source(sim=self)                                                         
        self.activate(source,
             source.generate(number=5,rate=0.1),at=0.0)    
        self.simulate(until=400.0)

## Experiment  ----------------------------------
seed(393939)
BankModel().run()
