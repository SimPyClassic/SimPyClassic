"""callCenter_OO.py
Model shows use of get command with a filter function.

Scenario:
A call center runs around the clock. It has a number of agents online with
different skills/competences.
Calls by clients with different questions arrive at an expected rate of
callrate per minute (expo. distribution). An agent only deals with clients with
questions in his competence areas. The number of agents online and their skills
remain
constant --
when an agent goes offline, he is replaced by one withe thesame skills.
The expected service time tService[i] per question
follows an exponential distribution.
Clients are impatient and renege if they don't get service within time
tImpatience.

* Determine the waiting times of clients.
* Determine the percentage renegers
* Determine the percentage load on agents.
"""
from SimPy.Simulation import *
import random as r
# Model components -----------------------------------------------------------


class Client(Process):
    def __init__(self, need, sim):
        Process.__init__(self, sim=sim)
        self.need = need

    def getServed(self, callCenter):
        self.done = SimEvent(sim=self.sim)
        callsWaiting = callCenter.calls
        self.served = False
        self.tArrive = self.sim.now()
        yield put, self, callsWaiting, [self]
        yield hold, self, tImpatience
        # get here either after renege or after interrupt of
        # renege==successful call
        if self.interrupted():
            # success, got service
            callCenter.renegeMoni.observe(success)
            # wait for completion of service
            yield waitevent, self, self.done
        else:
            # renege
            callCenter.renegeMoni.observe(renege)
            callsWaiting.theBuffer.remove(self)
            callCenter.waitMoni.observe(self.sim.now() - self.tArrive)
            if callsWaiting.monitored:
                callsWaiting.bufferMon.observe(y=len(callsWaiting.theBuffer))


class CallGenerator(Process):
    def __init__(self, name, center, sim):
        Process.__init__(self, name=name, sim=sim)
        self.buffer = center.calls
        self.center = center

    def generate(self):
        while self.sim.now() <= endTime:
            yield hold, self, r.expovariate(callrate)
            ran = r.random()
            for aNeed in clientNeeds:
                if ran < probNeeds[aNeed]:
                    need = aNeed
                    break
            c = Client(need=need, sim=self.sim)
            self.sim.activate(c, c.getServed(callCenter=self.center))


class Agent(Process):
    def __init__(self, name, skills, sim):
        Process.__init__(self, name=name, sim=sim)
        self.skills = skills
        self.busyMon = Monitor(
            name="Load on {0}".format(self.name), sim=self.sim)

    def work(self, callCtr):
        incoming = callCtr.calls

        def mySkills(buffer):
            ret = []
            for client in buffer:
                if client.need in self.skills:
                    ret.append(client)
                    break
            return ret
        self.started = self.sim.now()
        while True:
            self.busyMon.observe(idle)
            yield get, self, incoming, mySkills
            self.busyMon.observe(busy)
            theClient = self.got[0]
            callCtr.waitMoni.observe(self.sim.now() - theClient.tArrive)
            self.interrupt(theClient)  # interrupt the timeout renege
            yield hold, self, tService[theClient.need]
            theClient.done.signal()


class Callcenter:
    def __init__(self, name, sim):
        self.calls = Store(name=name, unitName="call", monitored=True, sim=sim)
        self.waitMoni = Monitor("Caller waiting time", sim=sim)
        self.agents = []
        self.renegeMoni = Monitor("Renegers", sim=sim)


renege = 1
success = 0
busy = 1
idle = 0

# Experiment data ------------------------------------------------------------
centerName = "SimCityBank"
clientNeeds = ["loan", "insurance", "credit card", "other"]
aSkills = [["loan"], ["loan", "credit card"],
           ["insurance"], ["insurance", "other"]]
nrAgents = {0: 1, 1: 2, 2: 2, 3: 2}  # skill:nr agents of that skill
probNeeds = {"loan": 0.1, "insurance": 0.2, "credit card": 0.5, "other": 1.0}
tService = {"loan": 3., "insurance": 4.,
            "credit card": 2., "other": 3.}  # minutes
tImpatienceRange = (0.5, 1., 2.,)      # minutes
callrate = 7. / 10          # Callers per minute
endTime = 10 * 24 * 60    # minutes (10 days)
r.seed(12345)

# Model ----------------------------------------------------------------------


class CallCenterModel(Simulation):
    def run(self):
        self.initialize()
        callC = Callcenter(name=centerName, sim=self)
        for i in nrAgents.keys():  # loop over skills
            for j in range(nrAgents[i]):  # loop over nr agents of that skill
                a = Agent(name="Agent type {0}".format(
                    i), skills=aSkills[i], sim=self)
                callC.agents.append(a)
                self.activate(a, a.work(callCtr=callC))
        # buffer=callC.calls)
        cg = CallGenerator(name="Call generator", center=callC, sim=self)
        self.activate(cg, cg.generate())
        self.simulate(until=endTime)
        return callC


for tImpatience in tImpatienceRange:
    # Experiment --------------------------------------------------------------
    callCenter = CallCenterModel().run()
    # Analysis/output ---------------------------------------------------------
    print("\ntImpatience={0} minutes".format(tImpatience))
    print("==================")
    callCenter.waitMoni.setHistogram(low=0.0, high=float(tImpatience))
    try:
        print(callCenter.waitMoni.printHistogram(fmt="{0:6.1f}"))
    except:
        pass
    renegers = [1 for x in callCenter.renegeMoni.yseries() if x == renege]
    print("\nPercentage reneging callers: {0:4.1f}\n".format(
        100.0 * sum(renegers) / callCenter.renegeMoni.count()))
    for agent in callCenter.agents:
        print("Load on {0} (skills= {1}): {2:4.1f} percent".format(
            agent.name, agent.skills, agent.busyMon.timeAverage() * 100))
