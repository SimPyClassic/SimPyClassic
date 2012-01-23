""" bank01_OO: The single non-random Customer """
from SimPy.Simulation import Simulation, Process, hold


## Model components -----------------------------
class Customer(Process):
    """ Customer arrives, looks around and leaves """

    def visit(self, timeInBank):
        print("%2.1f %s  Here I am" % (self.sim.now(), self.name))
        yield hold, self, timeInBank
        print("%2.1f %s  I must leave" % (self.sim.now(), self.name))


## Model ----------------------------------------
class BankModel(Simulation):
    def run(self):
        """ PEM """
        c = Customer(name="Klaus", sim=self)
        self.activate(c, c.visit(timeInBank), at=tArrival)
        self.simulate(until=maxTime)

## Experiment data ------------------------------

maxTime = 100.0     # minutes
timeInBank = 10.0   # minutes
tArrival = 5.0      # minutes

## Experiment -----------------------------------

mymodel = BankModel()
mymodel.run()
