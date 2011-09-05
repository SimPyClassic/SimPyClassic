from SimPy.Simulation import *

class Customer(Process):
   def buy(self,budget=0):
      print 'Here I am at the shops ',self.name
      t = 5.0
      for i in range(4):
          yield hold,self,t   
            # executed 4 times at intervals of t time units
          print 'I just bought something ',self.name
          budget -= 10.00
      print   'All I have left is ', budget,\
              ' I am going home ',self.name,

initialize()

# create a customer named "Evelyn",
C = Customer(name='Evelyn')

# and activate her with a budget of 100
activate(C,C.buy(budget=100),at=10.0)  
    
simulate(until=100.0)
