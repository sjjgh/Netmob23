# -*- coding: utf-8 -*-
"""
Created on Thu May 25 21:54:12 2023

@author: JIajie Shi
"""
import pandas as pd
import numpy as np
import datetime
import json

from matplotlib import pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colrs
import math
#include every interaction
#%%
#import data
day_str = '20190403'
city_str = 'Paris'
app_str = 'Instagram'

# downlink traffic file
traffic_file_dn = f'./{city_str}_{app_str}_{day_str}_DL.txt'

# let's make a list of 15 min time intervals to use as column names
day = datetime.datetime.strptime(day_str, '%Y%m%d')
times = [day + datetime.timedelta(minutes=15*i) for i in range(96)]
times_str = [t.strftime('%H:%M') for t in times]

# column names
columns = ['tile_id'] + times_str

# let's load the data of the downlink traffic
df_traffic_dn = pd.read_csv(traffic_file_dn, sep=' ', names=columns)
df_traffic_dn.head(20)
#%%
df2=df_traffic_dn.copy()
#%%
#import more libriaries
import json
from matplotlib import pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colrs

from shapely.geometry import shape as Shape
import numpy as np

from descartes.patch import PolygonPatch

plt.rcParams['font.size'] = 18
#%%
city_str = 'Paris'
n_rows, n_cols = (409, 346)
city_geojson_file = f'./{city_str}.geojson'
fd = open(city_geojson_file)
city_geojson = json.load(fd)
fd.close()
#%%
matrix2tile_dict={}
city_mask = np.zeros((n_rows, n_cols))
tile_id_list=[]
tile2geo_dict={}
for feature in city_geojson['features']:
    tile_id = feature['properties']['tile_id']
    tile_id_list.append(tile_id)
    tile2geo_dict[tile_id]=feature['geometry']['coordinates']
    row_index = int(tile_id // n_cols)
    col_index = int(tile_id % n_cols)
    matrix2tile_dict[(row_index,col_index)]=tile_id
    if (row_index+col_index)%2==0:
        city_mask[row_index, col_index] = 1
    else:
        city_mask[row_index, col_index] = 1
#%%
time1=80
time2=81
stime1=str(times_str[time1])
stime2=str(times_str[time2])
state1=[]
state2=[]
tile_list=[]
for  row in  range(218-10,218+10):
    for col in range(79-10,79+10):
        ind=row*n_cols+col
        tile_list.append(ind)
        state1.append(int(df2.loc[df2['tile_id']==ind,stime1]))
        state2.append(int(df2.loc[df2['tile_id']==ind,stime2]))
#%%
'''
time1=83
time2=84
stime1=str(times_str[time1])
stime2=str(times_str[time2])
state11=[]
state22=[]
tile_list=[]
for  row in  range(218-10,218+10):
    for col in range(79-10,79+10):
        ind=row*n_cols+col
        tile_list.append(ind)
        state11.append(int(df2.loc[df2['tile_id']==ind,stime1]))
        state22.append(int(df2.loc[df2['tile_id']==ind,stime2]))
'''
#%%
flag=1
if sum(state2)>sum(state1):
    state1,state2=state2,state1
    print('reversed')
    flag=0
#%%
#compute distance between tiles
m2=n_cols
def distance(nt1,nt2):
    row_id1=int(nt1//m2)
    col_id1=int(nt1%m2)
    row_id2=int(nt2//m2)
    col_id2=int(nt2%m2)
    d1=abs(row_id1-row_id2)
    d2=abs(col_id1-col_id2)
    return math.sqrt(d1**2+d2**2)
#%%
#assign weights according to the distances
from collections import defaultdict
tt2xid={}
ii=0
xid2tt=[]
x_weight=[]
for nt1 in tile_list:
    for nt2 in tile_list:
        x_weight.append(distance(nt1,nt2))
        xid2tt.append([nt1,nt2])
        tt2xid[nt1,nt2]=ii
        ii+=1
numberofx=ii
#%%
#inequalities
number_of_tiles=len(tile_list)
Aub1=np.zeros((number_of_tiles,numberofx))
bub1=np.zeros(number_of_tiles)
for i in range(number_of_tiles):
    for nt in tile_list:
        xid=tt2xid[(tile_list[i],nt)] #flow out and evp
        Aub1[i,xid]=1
    bub1[i]=state1[i]
#%%
#equalities
Aeq=np.zeros((number_of_tiles,numberofx))
beq=np.zeros(number_of_tiles)
for i in range(number_of_tiles):
    for nt in tile_list:
        xid=tt2xid[(tile_list[i],nt)]
        Aeq[i,xid]=-1 #flow out
        xid2=tt2xid[(nt,tile_list[i])]
        Aeq[i,xid2]=1 #flow in
    xid3=tt2xid[(tile_list[i],tile_list[i])]
    Aeq[i,xid3]=-1 #evp
    beq[i]=state2[i]-state1[i]
#%%
#coefficients
c=np.array(x_weight)
#%%
#solver
from scipy.optimize import linprog
res = linprog(c, A_ub=Aub1, b_ub=bub1, A_eq=Aeq, b_eq=beq,method='highs')
#%%
x_opt=res.x
#%%
def compute_center_coordinates(nt):
    x_list=[]
    y_list=[]
    cod_list=tile2geo_dict[nt][0]
    for cod in cod_list:
        x_list.append(cod[0])
        y_list.append(cod[1])
    x_c=(max(x_list)+min(x_list))/2
    y_c=(max(y_list)+min(y_list))/2
    return [x_c,y_c]
#%%
arrow_cod_list=[]
with open("ins0403_DL_cod"+str(time1)+"_prince.txt","w") as file:
    for i in range(len(x_opt)):
        x=x_opt[i]
        if x>0:
            nt1,nt2=xid2tt[i]
            cod1=compute_center_coordinates(nt1)
            cod2=compute_center_coordinates(nt2)
            if flag:
                arrow_cod_list.append([cod1,cod2])
                file.write(str(cod1[0])+' '+str(cod1[1])
                           +' '+str(cod2[0])+' '+str(cod2[1])
                           +' '+str(x)+' '+str(nt1)
                           +'\n')
            else:
                arrow_cod_list.append([cod2,cod1])
                file.write(str(cod2[0])+' '+str(cod2[1])
                           +' '+str(cod1[0])+' '+str(cod1[1])
                           +' '+str(-x)+' '+str(nt1)
                           +'\n')
    
