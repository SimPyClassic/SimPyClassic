""" bank24_OO. BCC system with several counters """
from SimPy.Simulation import *
from random import expovariate, seed

## Model components ------------------------           

class Source(Process):
    """ Source generates customers randomly """

    def generate(self,number,meanTBA,resource):          
        for i in range(number):
            c = Customer(name = "Customer%02d"%(i,),sim=self.sim)
            self.sim.activate(c,c.visit(b=resource))              
            t = expovariate(1.0/meanTBA)                 
            yield hold,self,t

class Customer(Process):
    """ Customer arrives, is served and leaves """

    def visit(self,b):                                   
        arrive = now()
        print "%8.4f %s: Here I am "%(self.sim.now(),self.name)
        if len(b.waitQ) < maxInQueue:     # the test     
            yield request,self,b                         
            wait = self.sim.now()-arrive
            print "%8.4f %s: Wait %6.3f"%(self.sim.now(),self.name,wait)
            tib = expovariate(1.0/timeInBank)            
            yield hold,self,tib                          
            yield release,self,b
            print "%8.4f %s: Finished  "%(self.sim.now(),self.name)
        else:
            Customer.numBalking += 1                      
            print "%8.4f %s: BALKING   "%(self.sim.now(),self.name) 

## Experiment data -------------------------------       

timeInBank = 12.0 # mean, minutes                        
ARRint = 10.0     # mean interarrival time, minutes
numServers = 1    # servers
maxInSystem = 2   # customers
maxInQueue = maxInSystem - numServers                    

maxNumber = 8
maxTime = 4000.0 # minutes                                      
theseed = 12345                                          

## Model
class BankModel(Simulation):
    def run(self):
        self.initialize()
        k = Resource(capacity=numServers,
             name="Counter",unitName="Clerk",sim=self) 
        s = Source('Source',sim=self)
        self.activate(s, s.generate(number=maxNumber,meanTBA=ARRint, 
                         resource=k),at=0.0)             
        self.simulate(until=maxTime)
        
## Experiment --------------------------------------
seed(theseed)
Customer.numBalking = 0
modl=BankModel()
modl.run()
## Results -----------------------------------------

nb = float(Customer.numBalking)
print "balking rate is %8.4f per minute"%(nb/modl.now())
