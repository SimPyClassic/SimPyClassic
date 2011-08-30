from SimPy.Simulation import *
from random import normalvariate,seed

class Deliver(Process):
   def deliver(self):          # an "offeror" PEM
       while True:
           lead = 10.0         # time between refills
           delivery = 10.0     # amount in each refill
           yield put, self, stock, delivery
           print 'at %7.4f, add %7.4f units, now amount = %6.4f'\
               %(now(),delivery,stock.amount)
           yield hold, self, lead

class Demand(Process):
   stockout = 0.0              # initialize initial stockout amount
   def demand(self):           # a "requester" PEM
       day = 1.0               # set time-step to one day
       while True:
           yield hold, self, day
           dd = normalvariate(1.20, 0.20)  # today's random demand
           ds = dd - stock.amount
               # excess of demand over current stock amount
           if dd > stock.amount:   # can't supply requested amount
               yield get, self, stock, stock.amount  
                   # supply all available amount
               self.stockout += ds         
                   # add unsupplied demand to self.stockout
               print 'day %7.4f, demand = %7.4f, \
                   shortfall = %7.4f' %(now(), dd, -ds)
           else:                   # can supply requested amount
               yield get, self, stock, dd
               print 'day %7.4f, supplied %7.4f, now amount = %6.4f'\
                   %(now(), dd, stock.amount)

stock = Level(monitored=True)  # 'unbounded' capacity and other defaults

seed(99999)
initialize()

offeror = Deliver()
activate (offeror, offeror.deliver())
requester = Demand()
activate (requester, requester.demand())

simulate (until=49.9)

result=(stock.bufferMon.mean(), requester.stockout)
print
print 'Summary of results through end of day %7.4f:' %(int(now()))
print 'average stock = %7.4f, cumulative stockout = %7.4f' %result
