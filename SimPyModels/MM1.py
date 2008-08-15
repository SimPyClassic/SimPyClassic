""" MM1.py Single-server queue with GUI input using Tkinter.
"""
from Tkinter import *
import tkMessageBox
from SimPy.Simulation import *
from random import uniform, expovariate
import string
 
# This is the mm_SiPy Code
def theTime(time):

     hrs=time//60
     min=time-hrs
     return "%s:%s" %(string.zfill(str(hrs),2),string.zfill(str(min),2))
     
class worker(Process):
     def __init__(self,id):
         Process.__init__(self)
         self.id=id
         self.output=0
         self.idle=0
         self.total_idle=0
         self.startService=None # change
 
     def working_day(self,foobar="None"):
         while now()<17*60: #work till 5 pm
             yield hold,self,uniform(3,10)
             self.output += 1
             if foobar != "None":
                foobar.queue.append(self)
                if foobar.idle:
                    reactivate(foobar)
                else:
                    self.idle=1 #worker has to wait for foobar service
                    start_idle=now()
                yield passivate,self #waiting and foobar service
             if self.idle:
                self.total_idle+=now()-start_idle
                mreport.append(self.total_idle)
             self.idle=0
 
     def mQueue(self,foobar="None",mreport="mreport"):
        if foobar != "None":
                foobar.queue.append(self)
                mreport.append(theTime(now())) # Collects time starting work
                if foobar.idle:
                        reactivate(foobar)
                else:
                        self.idle=1 #worker has to wait for foobar service
                        start_idle=now()
                yield passivate,self #waiting and foobar service
 #              mreport.append(self.startService)
                mreport.append(theTime(self.startService))
                if self.idle:
                        self.total_idle+=now()-start_idle
                        self.idle=0
                mreport.append(theTime(now())) #Collects time completed building widget
        yield hold,self,5 #Clean up to go home
        self.output += 1
        mreport.append(theTime(now())) # Collects time work complete
        mreport.append(self.total_idle) # Collects time waiting for machine
        mreport.append(self.output) # Collects number of widgets produced
 
 
class foobar_machine(Process):
     def __init__(self):
         Process.__init__(self)
         self.queue=[]
         self.idle=1
 
     def foobar_process(self):
         yield passivate,self
         while 1:
             while len(self.queue) > 0:
                 self.idle=0
                 served=self.queue.pop(0)
                 #  being_served=self.queue[0] ## change
                 served.startService=now() ## change
                 yield hold,self,expovariate(1/float(Ent3.get()))
 #                      served=self.queue.pop(0)
                 reactivate(served)
             self.idle=1
             yield passivate,self
 
 # This is model code
 
def Run():
     if Ent1.get() == "" or Ent2.get() == "" or Ent4.get() == ""\
        or Ent5.get() == "" or Ent3.get() == "":
        tkMessageBox.showerror("SimPy", "Try again!")
     else: 
        model()
 
# M/M/1 queue model
def model():
        report = []
        mStart = (float(Ent4.get())*60) # Start work at 8:30
        mdelay = 0
        initialize()
        foo=foobar_machine()
        activate(foo,foo.foobar_process(),delay=0)
        for i in range(int(Ent1.get())):
                mdelay += expovariate(1/float(Ent2.get()))
                mworker = i
                mreport = [i]
                mreport.append(mdelay) # Collects time between arrivals
                report.append(mreport)
                mworker = worker(mworker)
                activate(mworker,mworker.mQueue(foo,mreport),at=(mStart+mdelay))
        scheduler(till=(float(Ent5.get())*60)) #run simulation from midnight till 6 pm
        print "ID, Delay, Start Time, Start Work, Finish Widget, Finish Work, Waiting Time, Widgets Produced"
        for record in report:
                print record
        print "Model Run Complete."
 
        
def die():
        sys.exit()
        
root=Tk()
F=Frame(root)
Lbl1 = Label(F,text="Number of Entities").grid(row = 0, column = 0)
Ent1 = Entry(F)
Ent1.grid(row = 0, column = 1)
Lbl2 = Label(F,text="Mean Time Between Arrivals").grid(row = 1, column = 0)
Ent2 = Entry(F)
Ent2.grid(row = 1, column = 1)
Lbl3 = Label(F,text="Mean Processing Time").grid(row = 2, column = 0)
Ent3 = Entry(F)
Ent3.grid(row = 2, column = 1)
Lbl4 = Label(F,text="Start Time in Hours").grid(row = 3, column = 0)
Ent4 = Entry(F)
Ent4.grid(row = 3, column = 1)
Lbl5 = Label(F,text="End Time in Hours").grid(row = 4, column = 0)
Ent5 = Entry(F)

Ent5.grid(row = 4, column = 1)
Btn1 = Button(F,text="Press to Begin",command=Run).grid(row = 5, column = 0)
BExit = Button(F,text="Quit",command=die).grid(row = 5, column = 1)

F.pack()
root.title("SiPy Model")
root.mainloop()
