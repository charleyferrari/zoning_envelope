import os
import csv
import Tkinter
import tkFileDialog
import copy
import re
import pandas as pd
import math
import numpy as np
import re


import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler

from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import mpl_toolkits.basemap.pyproj as pyproj

class simpleapp_tk(Tkinter.Tk):
	def __init__(self,parent):
		Tkinter.Tk.__init__(self,parent)
		self.parent = parent
		self.initialize()

	def initialize(self):
		self.grid()

		self.nycrez = self.datacreate()
		self.floorFilter = Tkinter.IntVar()
		self.entry = Tkinter.Entry(self,textvariable=self.floorFilter)
		self.entry.grid(column=0,row=0,sticky='EW')
		self.entry.bind("<Return>", self.OnPressEnter)
		self.floorFilter.set(4)

		button = Tkinter.Button(self,text=u"Click me !",
			command=self.OnButtonClick)
		button.grid(column=1,row=0)

		self.mapdraw(self.floorFilter.get(),self.nycrez)

	def OnButtonClick(self):
		self.mapdraw(self.floorFilter.get(),self.nycrez)

	def OnPressEnter(self):
		self.mapdraw(self.floorFilter.get(),self.nycrez)

	def mapdraw(self,floorFilter,nycrez):
		f = self.mapcode(floorFilter,nycrez)

		canvas = FigureCanvasTkAgg(f, master=self)
		canvas.show()
		canvas.get_tk_widget().grid(column=0,row=1,columnspan=2,sticky='EW')

	def datacreate(self):

		bx = pd.read_csv('bx.csv')
		bk = pd.read_csv('bk.csv')
		mn = pd.read_csv('mn.csv')
		qn = pd.read_csv('qn.csv')
		si = pd.read_csv('si.csv')
		nyc = pd.concat([bx,bk,mn,qn,si], ignore_index=True)

		for i in np.arange(0, len(nyc)):
		    nyc['ZoneDist1'][i] = str(nyc['ZoneDist1'][i])
		    nyc['ZoneDist2'][i] = str(nyc['ZoneDist2'][i])
		    nyc['ZoneDist3'][i] = str(nyc['ZoneDist3'][i])
		    nyc['ZoneDist4'][i] = str(nyc['ZoneDist4'][i])

		nycrez = nyc[((nyc['ZoneDist1'].str[:1] == 'R') | (nyc['ZoneDist2'].str[:1] == 'R') | 
		             (nyc['ZoneDist2'].str[:1] == 'R') |  (nyc['ZoneDist2'].str[:1] == 'R') | 
		             (nyc['ZoneDist1'].str.contains('/R')) | (nyc['ZoneDist2'].str.contains('/R')) |
		             (nyc['ZoneDist3'].str.contains('/R')) | (nyc['ZoneDist4'].str.contains('/R'))) &
		             (nyc['XCoord'].notnull())]

		nycrez = nycrez[['Borough', 'Block', 'Lot', 'CD', 'CT2010', 'CB2010',
		                 'Council', 'BldgArea', 'ResArea', 'ResidFAR', 'CommFAR', 
		                 'FacilFAR', 'BuiltFAR', 'LotArea', 'XCoord', 'YCoord', 'LandUse',
		                 'OwnerName', 'OwnerType', 'Address']]

		nycrez['LeftoverResidFAR'] = nycrez['ResidFAR'] - nycrez['BuiltFAR']
		nycrez['XCoordMeters'] = nycrez['XCoord'] * 0.3048
		nycrez['YCoordMeters'] = nycrez['YCoord'] * 0.3048         

		nycrez = nycrez[(nycrez['LeftoverResidFAR'] > 0)]

		nyli = pyproj.Proj("+proj=lcc +lat_1=40.66666666666666 +lat_2=41.03333333333333 +lat_0=40.16666666666666 +lon_0=-74 +x_0=300000 +y_0=0 +ellps=GRS80 +datum=NAD83 +to_meter=0.3048006096012192 +no_defs")
		wgs84 = pyproj.Proj("+proj=longlat +ellps=GRS80 +datum=NAD83 +no_defs")

		nycrez['Lon'], nycrez['Lat'] = pyproj.transform(nyli, wgs84, nycrez['XCoordMeters'].values, nycrez['YCoordMeters'].values)

		return nycrez



	def mapcode(self,FARfilter,nycrez):

		

		fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(12, 10))
		fig.subplots_adjust(hspace=0.05, wspace=0.05)

		ax= axes

		lllat=40.481
		urlat=40.899
		lllon=-74.323
		urlon=-73.716

		m = Basemap(projection='stere',
		                lon_0=(urlon + lllon) / 2,
		                lat_0=(urlat + lllat) / 2,
		                llcrnrlat=lllat, urcrnrlat=urlat,
		                llcrnrlon=lllon, urcrnrlon=urlon,
		                resolution='f')
		m.drawcoastlines()
		m.drawstates()
		m.drawcountries()

		x, y = m(nycrez['Lon'][nycrez['LeftoverResidFAR'] > FARfilter].values, nycrez['Lat'][nycrez['LeftoverResidFAR'] > FARfilter].values)
	    
		m.plot(x, y, 'k.', alpha=0.5)
		ax.set_title('Title')

		return fig
		


if __name__ == "__main__":
	app = simpleapp_tk(None)
	app.title('my application')
	app.mainloop()
