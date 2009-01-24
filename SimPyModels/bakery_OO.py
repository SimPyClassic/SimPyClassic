"""bakery_OO.py
Scenario:
The Patisserie Francaise bakery has three ovens baking their renowned
baguettes for retail and restaurant customers. They start baking one
hour before the shop opens and stop at closing time. 
They bake batches of 40 breads at a time,
taking 25..30 minutes (uniformly distributed) per batch. Retail customers
arrive at a rate of 40 per hour (exponentially distributed). They buy
1, 2 or 3 baguettes with equal probability. Restaurant buyers arrive
at a rate of 4 per hour (exponentially dist.). They buy 20,40 or 60
baguettes with equal probability.
Simulate this operation for 100 days of 8 hours shop opening time.
a) What is the mean waiting time for retail and restaurant buyers?
b) What is their maximum waiting time?
b) What percentage of customer has to wait longer than 15 minutes??
c) Plot the number of baguettes over time for an arbitrary day.
   (use PLOTTING=True to do this)

"""
from SimPy.Simulation import *
from SimPy.SimPlot import *
import random
## Model components ------------------------
class Bakery:
    def __init__(self,nrOvens,toMonitor,sim):
        self.stock = Level(name="baguette stock",monitored=toMonitor,sim=sim)
        for i in range(nrOvens):
            ov=Oven(sim=sim)
            sim.activate(ov,ov.bake(capacity=batchsize,bakery=self))
class Oven(Process):
    def bake(self,capacity,bakery):
        while self.sim.now()+tBakeMax<tEndBake:
            yield hold,self,r.uniform(tBakeMin,tBakeMax)
            yield put,self,bakery.stock,capacity
class Customer(Process):
    def buyBaguette(self,cusType,bakery):
        tIn = self.sim.now()
        yield get,self,bakery.stock,r.choice(buy[cusType])
        waits[cusType].append(self.sim.now()-tIn)
class CustomerGenerator(Process):
    def generate(self,cusType,bakery):
        while True:
            yield hold,self,r.expovariate(1.0/tArrivals[cusType])
            if self.sim.now()<(tShopOpen+tBeforeOpen):
                c=Customer(cusType,sim=self.sim)
                self.sim.activate(c,c.buyBaguette(cusType,bakery=bakery))
## Model -----------------------------------
class BakeryModel(Simulation):
    def run(self):
        #toMonitor=False
        self.initialize()
        toMoni = day==(nrDays-1)
        b = Bakery(nrOvens=nrOvens,toMonitor=toMoni,sim=self)
        for cType in ["retail","restaurant"]:
            cg = CustomerGenerator(sim=self)
            self.activate(cg,cg.generate(cusType=cType,bakery=b),delay=tBeforeOpen)
        self.simulate(until=tBeforeOpen+tShopOpen)
        return b
## Experiment data -------------------------
nrOvens = 3
batchsize = 40                                                     #nr baguettes
tBakeMin = 25/60.; tBakeMax=30/60.                                #hours
tArrivals = {"retail":1.0/40,"restaurant":1.0/4}                  #hours
buy = {"retail":[1,2,3],"restaurant":[20,40,60]}                 #nr baguettes
tShopOpen = 8; tBeforeOpen = 1; tEndBake = tBeforeOpen+tShopOpen  #hours
nrDays=100
r=random.Random(12371)
PLOTTING=True
## Experiment ------------------------------
waits={}
waits["retail"]=[]; waits["restaurant"]=[]
bakMod = BakeryModel()
for day in range(nrDays):
    bakery = bakMod.run()
## Analysis/output -------------------------
print 'bakery'
for cType in ["retail","restaurant"]:
    print "Average wait for %s customers: %4.2f hours"\
    %(cType,(1.0*sum(waits[cType]))/len(waits[cType]))
    print "Longest wait for %s customers: %4.1f hours"%(cType,max(waits[cType]))
    nrLong = len([1 for x in waits[cType] if x>0.25])
    nrCust = len(waits[cType])
    print "Percentage of %s customers having to wait for more than 0.25 hours: %s"\
           %(cType,100*nrLong/nrCust)    


if PLOTTING:
    plt = SimPlot()
    plt.plotStep(bakery.stock.bufferMon,
             title="Number of baguettes in stock during arbitrary day",color="blue")
    plt.mainloop()
