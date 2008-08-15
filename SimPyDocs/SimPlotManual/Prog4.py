# Prog4.py
from SimPy.SimPlot import *
plt=SimPlot()
plt.plotBars([[0,0],[1,1],[2,4],[3,9]],
             color="blue",width=2,windowsize=(200,200))
plt.mainloop()