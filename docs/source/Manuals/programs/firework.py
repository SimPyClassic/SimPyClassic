from SimPy.Simulation import *

class Firework(Process):

  def execute(self):
      print now(), ' firework launched'
      yield hold,self, 10.0    # wait 10.0 time units
      for i in range(10):
          yield hold,self,1.0
          print now(),  ' tick'
      yield hold,self,10.0     # wait another 10.0 time units
      print now(), ' Boom!!'

initialize()
f = Firework()                  # create a Firework object, and
   # activate it (with some default parameters)
activate(f,f.execute(),at=0.0)  
simulate(until=100)
