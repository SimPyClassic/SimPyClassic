""" bank20_OO: One counter with a priority customer """
from SimPy.Simulation import *
from random import expovariate, seed

## Model components ------------------------

class Source(Process):
    """ Source generates customers randomly """

    def generate(self,number,interval,resource):       
        for i in range(number):
            c = Customer(name = "Customer%02d"%(i,),sim=self.sim)
            self.sim.activate(c,c.visit(timeInBank=12.0,
                               res=resource,P=0))           
            t = expovariate(1.0/interval)
            yield hold,self,t

class Customer(Process):
    """ Customer arrives, is served and  leaves """
        
    def visit(self,timeInBank=0,res=None,P=0):              
        arrive = self.sim.now()       # arrival time                 
        Nwaiting = len(res.waitQ)
        print "%8.3f %s: Queue is %d on arrival"%(self.sim.now(),self.name,Nwaiting)

        yield request,self,res,P                            
        wait = self.sim.now()-arrive  # waiting time                 
        print "%8.3f %s: Waited %6.3f"%(self.sim.now(),self.name,wait)
        yield hold,self,timeInBank
        yield release,self,res                              

        print "%8.3f %s: Completed"%(self.sim.now(),self.name)

## Experiment data -------------------------

maxTime = 400.0  # minutes                                
                           

## Model ------------------------------
class BankModel(Simulation):
    def run(self):
        self.initialize()
        k = Resource(name="Counter",unitName="Karen",               
             qType=PriorityQ,sim=self)    
        s = Source('Source',sim=self)
        self.activate(s,s.generate(number=5, interval=10.0,              
                              resource=k),at=0.0)                   
        guido = Customer(name="Guido     ",sim=self)                         
        self.activate(guido,guido.visit(timeInBank=12.0,res=k,
                                   P=100),at=23.0)                  
        self.simulate(until=maxTime)

## Experiment ---------------------------
seed(98989)
BankModel().run()