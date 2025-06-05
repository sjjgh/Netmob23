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
import time
#include every interaction
#%%
#import data
day_str = '20190403'
city_str = 'Paris'
app_str = 'Uber'

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
#coarsen the geodata
factor=10
newid_list=[]
newid2oldid={}
coarse_dict={}
n2=int(n_rows/factor)
m2=int(n_cols/factor)
city_mask2 = np.zeros((n2, m2))
for i in range(n2):
    for j in range(m2):
        elesum=0
        elem=[]
        for ii in range(factor*i+1,factor*i+factor+1):
            for jj in range(factor*j,factor*j+factor):
                elesum+=city_mask[ii,jj]
                if (ii,jj) in matrix2tile_dict:
                    elem.append(matrix2tile_dict[(ii,jj)])
        if elesum>=9:
            coarse_dict[(i,j)]=elem
            nid=i*m2+j
            newid_list.append(nid)
            newid2oldid[nid]=elem
            if (i+j)%2==0:
                city_mask2[i,j]=1
            else:
                city_mask2[i,j]=0.5
        else:
            city_mask2[i,j]=0
#%%
#coarsen corresponding usage
nf4=np.zeros((len(newid_list),96))
for i in range(len(newid_list)):
    new_tileid=newid_list[i]
    asum=0
    arrsum=np.zeros(96)
    for ot in newid2oldid[new_tileid]:
        temp=df2.loc[df2['tile_id']==ot]
        arr=temp.iloc[:,1:].to_numpy(dtype=float)
        arr=arr.reshape(96)
        arrsum=arrsum+arr
    nf4[i]=arrsum
#%%
#state1 have the larger total usuage
time1=50
time2=51
state1=nf4[:,time1]
state2=nf4[:,time2]
if sum(nf4[:,time1])>sum(nf4[:,time2]):
    state1=nf4[:,time1]
    state2=nf4[:,time2]
else:
    state1=nf4[:,time2]
    state2=nf4[:,time1]
#%%
#compute distance between tiles
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
xnb_dict=defaultdict(list)
ii=0
row_dim=n2
col_dim=m2
xid2tt=[]
x_weight=[]
for nt1 in newid_list:
    for nt2 in newid_list:
        x_weight.append(distance(nt1,nt2))
        xid2tt.append([nt1,nt2])
        tt2xid[nt1,nt2]=ii
        ii+=1
numberofx=ii
#%%
nt2nid={}
for i in range(len(newid_list)):
    nt2nid[newid_list[i]]=i
#%%
#inequalities
number_of_tiles=len(newid_list)
Aub1=np.zeros((number_of_tiles,numberofx))
bub1=np.zeros(number_of_tiles)
for i in range(number_of_tiles):
    for nt in newid_list:
        xid=tt2xid[(newid_list[i],nt)] #flow out and evp
        Aub1[i,xid]=1
    bub1[i]=state1[i]
#%%
#equalities
Aeq=np.zeros((number_of_tiles,numberofx))
beq=np.zeros(number_of_tiles)
for i in range(number_of_tiles):
    for nt in newid_list:
        xid=tt2xid[(newid_list[i],nt)]
        Aeq[i,xid]=-1 #flow out and evp
        xid2=tt2xid[(nt,newid_list[i])]
        Aeq[i,xid2]=1 #flow in and evp
    xid3=tt2xid[(newid_list[i],newid_list[i])]
    Aeq[i,xid3]=-1 #evp
    beq[i]=state2[i]-state1[i]
#%%
#coefficients
c=np.array(x_weight)        
#%%
#bounds
lb=[0]*numberofx
ub=[0]*numberofx
for i in range(number_of_tiles):
    for nt in newid_list:
        xid=tt2xid[(newid_list[i],nt)]
        ub[xid]=state1[i]
bounds=list(zip(lb,ub))
#%%
#solver
from scipy.optimize import linprog
starto=time.time()
res = linprog(c,A_ub=Aub1, b_ub=bub1,A_eq=Aeq, b_eq=beq,bounds=bounds,method='highs')
endo=time.time()
print(" {0} seconds for linprog".format(endo - starto))
x_opt=res.x
#%%
#ready to plot
city_mask3= np.zeros((n2, m2))
for i in range(n2):
    for j in range(m2):
        if city_mask2[i,j]>0:
            nt=i*m2+j
            nid=nt2nid[nt]
            city_mask3[i,j]=nf4[nid,0]
        else:
            city_mask3[i,j]=float("NaN")
for i in range(len(x_opt)):
    nt1,nt2=xid2tt[i]
    if nt1==nt2:
        row_id1=int(nt1//m2)
        col_id1=int(nt1%m2)
        if sum(nf4[:,time1])>sum(nf4[:,time2]):
            city_mask3[row_id1,col_id1]=x_opt[i]
        else:
            city_mask3[row_id1,col_id1]=-x_opt[i]
#%%
#plot the flows
import matplotlib as mpl
import matplotlib.ticker as ticker
import matplotlib.colors as colors
from  matplotlib.cm import ScalarMappable

cmap_region = cm.get_cmap('PiYG').copy()
cmap_region.set_under('w', 0)
norm_region = colrs.Normalize(vmin=-100000, vmax=100000,clip=True)

fig = plt.figure(figsize=(30, 15))
plt.imshow(city_mask3, cmap=cmap_region, norm=norm_region)
#plt.imshow(city_mask3, cmap=cmap_region)
plt.title('Time='+str(times_str[time1])+' - '+str(times_str[time2]))
#plt.imshow(city_mask2, cmap=cmap_region, norm=norm_region)
ax = plt.gca()
# Minor ticks to plot grid

ax.set_xticks(np.arange(-0.5,33), minor=True)
ax.set_yticks(np.arange(-0.5,30), minor=True)
ax.grid(which='minor', color='w', linestyle='-', linewidth=1)
# Remove minor ticks
ax.tick_params(which='minor', bottom=False, left=False)



#cmap_region.set_array([])


minx, maxx = (0, 100000)
n_lines = 5
cc=np.arange(1,10)
norm = mpl.colors.Normalize(vmin=minx, vmax=maxx)

'''
colmap = plt.get_cmap('autumn_r') 
cmap = mpl.cm.ScalarMappable(norm=norm, cmap=colmap)
cmap.set_array([])
'''

cmap = mpl.cm.YlOrRd(np.linspace(0,1,20))
cmap = mpl.colors.ListedColormap(cmap[6:,:-1])
norm = mpl.colors.Normalize(vmin=10000, vmax=100000)
scalarMap = cm.ScalarMappable(norm=norm,cmap=cmap)

#cmap=cm.get_cmap('cool_r').copy()
for i in range(len(x_opt)):
    x=x_opt[i]
    if x>=10000:
        nt1,nt2=xid2tt[i]
        if nt1!=nt2:            
            row_id1=int(nt1//m2)
            col_id1=int(nt1%m2)
            row_id2=int(nt2//m2)
            col_id2=int(nt2%m2)
            colorVal = scalarMap.to_rgba(x)
            if sum(nf4[:,time1])>sum(nf4[:,time2]):
                plt.arrow(col_id1,row_id1,col_id2-col_id1,row_id2-row_id1,width = 0.05,color=colorVal,alpha=0.8)
            else:
                plt.arrow(col_id2,row_id2,col_id1-col_id2,row_id1-row_id2,width = 0.05,color=colorVal,alpha=0.8)
cax = fig.add_axes([0.765, 0.25, 0.02, .5])
cax1 = fig.add_axes([0.84, 0.25, 0.02, .5])
clb=plt.colorbar(scalarMap,cax=cax)
#clb.ax.set_title('Flow')
clb.ax.text(s='Flow',x=0.5,y=104000,ha='center')
cbtk=np.arange(-100000,100000,20000)
clb1=plt.colorbar(cax=cax1,ticks=cbtk)
#clb1.ax.set_title('Evaporation')
clb1.ax.text(s='Evaporation',x=0.5,y=110000,ha='center')
clb1.ax.text(s='increment',x=0.5,y=-110000,ha='center')
#clb1.ax.text(s='unchanged',x=0.5,y=0,ha='center')
ax.set_facecolor("gray")
#plt.arrow(5,10,1,-1,width = 0.05,color='red')
#plt.arrow(x[0],x[1],y[0]-x[0],y[1]-x[1],width = 0.001,color='red')
plt.savefig('foo.png')
plt.show()
#%%
def compute_center_coordinates(nt):
    oldtiles=newid2oldid[nt]
    x_list=[]
    y_list=[]
    for ot in oldtiles:
        cod_list=tile2geo_dict[ot][0]
        for cod in cod_list:
            x_list.append(cod[0])
            y_list.append(cod[1])
    x_c=(max(x_list)+min(x_list))/2
    y_c=(max(y_list)+min(y_list))/2
    return [x_c,y_c]
#%%
#save the flows to a txt file
count=0
arrow_cod_list=[]
with open("insta_we_arr_cod"+str(time1)+"0403"+"_Paris.txt","w") as file:
    if sum(nf4[:,time1])>sum(nf4[:,time2]):      # decide whether it is evporation or increasement
        file.write('1'+'\n') #evp
    else:
        file.write('-1'+'\n') # incre
    for i in range(len(x_opt)):
        x=x_opt[i]
        if x>0:
            count+=1
            nt1,nt2=xid2tt[i]
            cod1=compute_center_coordinates(nt1)
            cod2=compute_center_coordinates(nt2)
            if sum(nf4[:,time1])>sum(nf4[:,time2]):
                arrow_cod_list.append([cod1,cod2])
                file.write(str(cod1[0])+' '+str(cod1[1])
                           +' '+str(cod2[0])+' '+str(cod2[1])
                           +' '+str(x)+' '+str(nt1)
                           +'\n')
            else:
                arrow_cod_list.append([cod2,cod1])
                file.write(str(cod2[0])+' '+str(cod2[1])
                           +' '+str(cod1[0])+' '+str(cod1[1])
                           +' '+str(x)+' '+str(nt1)
                           +'\n') 

    
    

