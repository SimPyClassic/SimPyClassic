from SimPy.SimPlot import *
plt=SimPlot()
plt.plotLine([[0,0],[1,1],[2,4],[3,9]],title="This is prettier",
             color="red",smooth=True,width=2,windowsize=(200,200))
plt.mainloop()