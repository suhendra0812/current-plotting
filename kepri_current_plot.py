import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from metpy.units import units
import metpy.calc as mpcalc

# Open the netCDF file as a xarray Dataset
data = xr.open_dataset('global-analysis-forecast-phy-001-024-monthly_201810-201901_kepri.nc')

# Resample and parse the dataset into monthly
data = data.resample(time="1M").mean().metpy.parse_cf()

# To rename variables, supply a dictionary between old and new names to the rename method
data = data.rename({
    'uo': 'u',
    'vo': 'v',
})

# Getting the cartopy coordinate reference system (CRS) of the projection of a DataArray
data_crs = data['u'].metpy.cartopy_crs

# Get multiple coordinates (for example, in just the x and y direction)
x, y = data['u'].metpy.coordinates('x', 'y')

# Or, we can just get a coordinate from the property
time = data['u'].metpy.time

# Select the data for this time
data_month = data.isel(time=0).squeeze('depth')
data_month['u'].attrs['units'] = 'm/s'
data_month['v'].attrs['units'] = 'm/s'

current_spd = mpcalc.wind_speed(data_month['u'], data_month['v'])
data_month = data_month.assign(cspd=(('latitude', 'longitude'), current_spd.m,
                           {'units': str(current_spd.units)}))

# Create the matplotlib figure and axis
fig, ax = plt.subplots(1, 1, figsize=(12, 8), subplot_kw={'projection': data_crs})

# Add geographic features
ax.add_feature(cfeature.LAND.with_scale('50m'), facecolor=cfeature.COLORS['land'])
ax.add_feature(cfeature.OCEAN.with_scale('50m'), facecolor=cfeature.COLORS['water'])
ax.add_feature(cfeature.STATES.with_scale('50m'), edgecolor='#c7c783', zorder=0)
ax.add_feature(cfeature.LAKES.with_scale('50m'), facecolor=cfeature.COLORS['water'],
               edgecolor='#c7c783', zorder=0)

# Plot wind speed as filled contours
levels = np.arange(0,11)
c = ax.contourf(x, y, data_month['cspd'], cmap='jet')
fig.colorbar(c)

# Plot wind quiver
q = ax.streamplot(x, y,
         data_month['u'], data_month['v'], transform=data_crs)

# Set extent
ax.set_extent([103, 107, -0.35, 2.5])

# Show gridlines
gl = ax.gridlines(draw_labels=True)
gl.xlabels_top = False
gl.ylabels_right = False

# Set a title and show the plot
ax.set_title('Current speed (m/s) and direction at '
             + time[0].dt.strftime('%Y-%m').item())
plt.show()

