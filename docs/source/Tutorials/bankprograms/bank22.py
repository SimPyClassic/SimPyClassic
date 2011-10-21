""" bank22: An interruption by a phone call """          
from SimPy.Simulation  import *                          

## Model components ------------------------


class Customer(Process):                                 
    """ Customer arrives, looks around and leaves """
        
    def visit(self,timeInBank,onphone):                  
        print "%7.4f %s: Here I am"%(now(),self.name)    
        yield hold,self,timeInBank                       
        if self.interrupted():                           
            timeleft = self.interruptLeft                
            self.interruptReset()                        
            print "%7.4f %s: Excuse me"%(now(),self.name)
            print "%7.4f %s: Hello! I'll call back"%(now(),self.name)
            yield hold,self,onphone                      
            print "%7.4f %s: Sorry, where were we?"%(now(),self.name)
            yield hold,self,timeleft                     
        print "%7.4f %s: I must leave"%(now(),self.name) 
   
class Call(Process):                                     
    """ Cellphone call arrives and interrupts """ 
        
    def ring(self,klaus,timeOfCall):                     
        yield hold,self,timeOfCall                       
        print "%7.4f Ringgg!"%(now())                    
        self.interrupt(klaus)                            

## Experiment data -------------------------

timeInBank = 20.0
timeOfCall = 9.0
onphone = 3.0
maxTime = 100.0


## Model/Experiment  ----------------------------------

initialize()                                             
klaus = Customer(name="Klaus")                           
activate(klaus,klaus.visit(timeInBank,onphone))          
call = Call()                                       
activate(call, call.ring(klaus,timeOfCall))              
simulate(until=maxTime)                                  
