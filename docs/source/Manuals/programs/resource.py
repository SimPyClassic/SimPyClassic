from SimPy.Simulation import *
class Client(Process):
    inClients=[]   # list the clients in order by their requests
    outClients=[]  # list the clients in order by completion of service

    def __init__(self,name):
       Process.__init__(self,name)

    def getserved(self,servtime,priority,myServer):
        Client.inClients.append(self.name)
        print self.name, 'requests 1 unit at t =',now()
         # request use of a resource unit
        yield request, self, myServer, priority
        yield hold, self, servtime
         # release the resource
        yield release, self, myServer
        print self.name,'done at t =',now()
        Client.outClients.append(self.name)

initialize()

    # the next line creates the ``server`` Resource object
server=Resource(capacity=2)     # server defaults to qType==FIFO

    # the next lines create some Client process objects
c1=Client(name='c1') ; c2=Client(name='c2')
c3=Client(name='c3') ; c4=Client(name='c4')
c5=Client(name='c5') ; c6=Client(name='c6')

    # in the next lines each client requests 
    # one of the ``server``'s Resource units
activate(c1,c1.getserved(servtime=100,priority=1,myServer=server))
activate(c2,c2.getserved(servtime=100,priority=2,myServer=server))
activate(c3,c3.getserved(servtime=100,priority=3,myServer=server))
activate(c4,c4.getserved(servtime=100,priority=4,myServer=server))
activate(c5,c5.getserved(servtime=100,priority=5,myServer=server))
activate(c6,c6.getserved(servtime=100,priority=6,myServer=server))

simulate(until=500)

print 'Request order: ',Client.inClients
print 'Service order: ',Client.outClients
