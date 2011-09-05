from SimPy.Simulation import *
from math import sqrt

class Client(Process):
    inClients=[]
    outClients=[]

    def __init__(self,name):
       Process.__init__(self,name)

    def getserved(self,servtime,myServer):
        print self.name, 'requests 1 unit at t =',now()
        yield request, self, myServer
        yield hold, self, servtime
        yield release, self, myServer
        print self.name,'done at t =',now()

initialize()

server=Resource(capacity=1,monitored=True,monitorType=Monitor)

c1=Client(name='c1') ; c2=Client(name='c2')
c3=Client(name='c3') ; c4=Client(name='c4')

activate(c1,c1.getserved(servtime=100,myServer=server))
activate(c2,c2.getserved(servtime=100,myServer=server))
activate(c3,c3.getserved(servtime=100,myServer=server))
activate(c4,c4.getserved(servtime=100,myServer=server))

simulate(until=500)

print
print '(TimeAverage no. waiting:',server.waitMon.timeAverage()
print '(Number) Average no. waiting:',server.waitMon.mean()
print '(Number) Var of no. waiting:',server.waitMon.var()
print '(Number) SD of no. waiting:',sqrt(server.waitMon.var())
print '(TimeAverage no. in service:',server.actMon.timeAverage()
print '(Number) Average no. in service:',server.actMon.mean()
print '(Number) Var of no. in service:',server.actMon.var()
print '(Number) SD of no. in service:',sqrt(server.actMon.var())
print '='*40
print 'Time history for the "server" waitQ:'
print '[time, waitQ]'
for item in server.waitMon:
    print item
print '='*40
print 'Time history for the "server" activeQ:'
print '[time, activeQ]'
for item in server.actMon:
    print item
