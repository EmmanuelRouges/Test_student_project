import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import xarray as xr
import cartopy.crs as ccrs
import cartopy
import datetime
from datetime import date

##Data
##!!Update directory/file name to your directory/file name!!
param = 't2m' #Name of variable given by climate data store
param_name = '2mT' #Name of variable as written in your file title
Data_dir = '/storage/silver/acrcc/ERA5-data/'+param_name+'/' #Source directory of your data

Years = range(2002,2022)
Years = [str(year) for year in Years]



# **Compute a running mean**

##!!Update directory/file name to your directory/file name!!
File = Data_dir + 'ERA5_'+param_name+'_daily_1950-1978_NAtl_Eur_1deg.nc' #File name
Data = xr.open_dataset(File)


dates = Data[param].coords['time']

window_days = 2
nb_windows = int(len(dates) - 2*window_days)

runmean = []

for i_day in range(window_days, window_days+nb_windows):
    print(i_day)
    sub_dates = dates[i_day-window_days:i_day+window_days+1]
    
    window_mean = Data_Z500[param].loc[sub_dates,:,:].mean(dim='time')
    if i_day == window_days:
        
        runmean = window_mean.assign_coords(coords = {'time': dates[i_day]})
    else:
        window_mean = window_mean.assign_coords(coords = {'time': dates[i_day]})
        runmean = xr.concat([runmean, window_mean], dim = 'time')

##!!Update directory/file name to your directory/file name!!
runmean.to_netcdf(Data_dir + 'ERA5_'+param_name+'_5day_runmean_1979-2022_NAtl_Eur_1deg.nc') #Save runmean file 


# **Compute the climatology**

##!!Update directory/file name to your directory/file name!!
runmean = xr.open_dataset(Data_dir + 'ERA5_'+param_name+'_5day_runmean_1979-2022_NAtl_Eur_1deg.nc')
runmean_dates = runmean.coords['time']


#Extract the month/day combinations
mmdd = []
for date in dates:
    date = str(date.values)
    if date[:4] == '1979':
        mmdd.append(date[4:])

#Climatology computation
clim = []

for md in mmdd:
    print(md)
    
    dates_md = [day for day in runmean_dates if str(day.values)[4:] == md]
    dates_md_xr = xr.concat(dates_md, dim = 'time')

    runmean_md = runmean[param].loc[dates_md_xr]
    md_mean = runmean_md.mean(dim = 'time')
   
    if md == mmdd[0]:
        
        clim = md_mean.assign_coords(coords = {'time': dates_md[0]})
    else:
        md_mean = md_mean.assign_coords(coords = {'time': dates_md[0]})
        clim = xr.concat([clim, md_mean], dim = 'time')


clim_dates = pd.date_range(start = '20020101',end = '20021231')
clim_dates_str = [date.strftime("%Y%m%d") for date in clim_dates]



clim.coords['time'] = clim_dates_str

##!!Update directory/file name to your directory/file name!!
clim.to_netcdf(Data_dir + 'ERA5_'+param_name+'_clim_1979-2022_NAtl_Eur_1deg.nc')


# **Compute the anomaly**


def Anomaly_computation(daily_data, clim_data, dates, clim_dates, param):
    
    year_ref = str(clim_data.coords['time'][0].values)[:4]


    for date in dates:

        print('date',date[:10])
        date_clim_str = year_ref + date[4:]
        
    
        #Use 02/28 climate for 02/29
        if date_clim_str[4:] == '0229':
            date_clim = clim_dates[58]
        else:
            date_clim = date_clim_str
        i_date = list(dates).index(date)
        i_clim_date = list(clim_dates.values).index(date_clim)
        
        data_date = daily_data.loc[date]
        data_clim_date = clim_data[param].loc[date_clim]
        
        anomaly = data_date - data_clim_date
        
        if date == dates[0]:
            Anomaly = anomaly.assign_coords(coords = {'time': date})
        else:
            anomaly = anomaly.assign_coords(coords = {'time': date})
            Anomaly = xr.concat([Anomaly, anomaly], dim = 'time')
            
    
    return Anomaly

##!!Update directory/file name to your directory/file name!!
Clim = xr.open_dataset(Data_dir + 'ERA5_'+param_name+'_clim_1979-2022_NAtl_Eur_1deg.nc')
clim_dates = Clim[param].coords['time']


for year in Years:
    print(year)

    dates_year = [date for date in dates.values if date[:4] == year]
    Data = Data_Z500[param].loc[dates_year]
    
    Anomaly_year = Anomaly_computation(Data, Clim, dates_year, clim_dates, param)

    
    if year == Years[0]:
        Anomaly = Anomaly_year
    else:
        Anomaly = xr.concat([Anomaly, Anomaly_year], dim = 'time')



##!!Update directory/file name to your directory/file name!!
Anomaly.to_netcdf(Data_dir + 'ERA5_'+param_name+'_anomaly_1950-1979_NAtl_Eur_1deg.nc')


##Example for plotting

long = Clim[param].coords['longitude']
lat = Clim[param].coords['latitude']
area_carto = [long[0], long[-1], lat[0], lat[-1]]


# In[23]:


colors_cmap = ['(64,0,75)','(118,42,131)','(153,112,171)','(194,165,207)','(231,212,232)','(247,247,247)',
               '(217,240,211)','(166,219,160)','(90,174,97)','(27,120,55)','(0,68,27)']
colors_cmap = reversed(colors_cmap)
colors_cmap_test = []
for c in colors_cmap:
    new = c.replace(',',' '). replace('(',''). replace(')','')
    split_c = new.split()
    c_new = [int(split_c[0])/256, int(split_c[1])/256, int(split_c[2])/256, 1]
    colors_cmap_test.append(np.array(c_new))
    
cmap_U10 = ListedColormap(colors_cmap_test[::-1])

levels_neg = np.arange(-50, 10, 10)
levels_pos = np.arange(10, 50+1, 10)
# levels_0 = np.arange(-0.5,1,1)
# Levels = np.append(levels_neg, levels_0)
# Levels = np.append(Levels, levels_pos)
Levels = np.append(levels_neg, levels_pos)


# In[24]:


fig, axs =  plt.subplots(1, 1, figsize = (20,20), subplot_kw = {'projection':ccrs.PlateCarree()})
# ax = axs[1, 1]
axs.coastlines(resolution = "110m")
contours = axs.contourf(long, lat, Anomaly.loc['19800101'],
                               levels = Levels,
                               cmap = cmap_U10,
                               extend = 'both',
                               transform=ccrs.PlateCarree())


# In[26]:


fig, axs =  plt.subplots(1, 1, figsize = (20,20), subplot_kw = {'projection':ccrs.PlateCarree()})
# ax = axs[1, 1]
axs.coastlines(resolution = "110m")
contours = axs.contourf(long, lat, Anomaly.loc['19810401'],
                               levels = Levels,
                               cmap = cmap_U10,
                               extend = 'both',
                               transform=ccrs.PlateCarree())


# In[ ]:




