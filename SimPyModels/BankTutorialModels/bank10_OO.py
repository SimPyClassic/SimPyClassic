""" bank10_OO: Several Counters with individual queues"""
from SimPy.Simulation import *
from random import expovariate,seed

## Model components ------------------------

class Source(Process):
    """ Source generates customers randomly"""

    def generate(self,number,interval,counters):                   
        for i in range(number):
            c = Customer(name = "Customer%02d"%(i,),sim=self.sim)
            self.sim.activate(c,c.visit(counters))
            t = expovariate(1.0/interval)
            yield hold,self,t

def NoInSystem(R):                                                  
    """ Total number of customers in the resource R"""
    return (len(R.waitQ)+len(R.activeQ))                            

class Customer(Process):
    """ Customer arrives, chooses the shortest queue
        is served and leaves
    """
        
    def visit(self,counters):       
        arrive = self.sim.now()
        Qlength = [NoInSystem(counters[i]) for i in range(Nc)]      
        print "%7.4f %s: Here I am. %s"%(self.sim.now(),self.name,Qlength)   
        for i in range(Nc):                                         
            if Qlength[i] == 0 or Qlength[i] == min(Qlength):
                choice = i  # the chosen queue number                
                break
                
        yield request,self,counters[choice]
        wait = self.sim.now()-arrive
        print "%7.4f %s: Waited %6.3f"%(self.sim.now(),self.name,wait)
        tib = expovariate(1.0/timeInBank)
        yield hold,self,tib
        yield release,self,counters[choice]

        print "%7.4f %s: Finished"%(self.sim.now(),self.name)

## Experiment data -------------------------

maxNumber = 5
maxTime = 400.0 # minutes                                     
timeInBank = 12.0 # mean, minutes                          
ARRint = 10.0   # mean, minutes                          
Nc = 2          # number of counters
theseed = 12345                                           
                                    
## Model -----------------------------------
class BankModel(Simulation):
    def run(self):
        self.initialize()
        kk = [Resource(name="Clerk0",sim=self),
              Resource(name="Clerk1",sim=self)]      
        s = Source('Source',sim=self)
        self.activate(s,s.generate(number=maxNumber,interval=ARRint,
                      counters=kk),at=0.0)
        self.simulate(until=maxTime)
## Experiment ------------------------------
seed(theseed)
BankModel().run()