import xarray as xr 
import metpy.calc as mpcalc
from metpy.units import units
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import rioxarray as rxr
import geopandas as gpd
import glob
from shapely.geometry import mapping
import pandas as pd

ds = xr.open_dataset('global-analysis-forecast-phy-001-024-monthly_201810-201901_kepri.nc')

paths = glob.glob(r"D:\Suhendra\Riset BARATA\data oil & ship\kepri**oils.shp")[:4]

df_list = []
for i, path in enumerate(paths):
    gdf = gpd.read_file(path)
    gdf.geometry = gdf.geometry.buffer(0.083)
    gdf.crs = ('EPSG:4326')
    data = ds.isel(time=i).metpy.parse_cf()
    data_crs = data['uo'].metpy.cartopy_crs
    data = data.squeeze('depth')
    data.rio.write_crs(4326, inplace=True)
    clip = data.rio.clip(gdf.geometry.apply(mapping), gdf.crs)
    x, y = clip['uo'].metpy.coordinates('x', 'y')
    time = clip['uo'].metpy.time

    fig, ax = plt.subplots()
    Q = ax.quiver(x, y, clip['uo'], clip['vo'])
    gdf.plot(ax=ax, zorder=0)
    ax.set_xlim(103, 107)
    ax.set_ylim(-0.35, 2.5)

    ax.set_title('Current direction at '
                 + time.dt.strftime('%Y-%m').item())
    plt.show()


    df = clip.to_dataframe().reset_index()
    df_list.append(df)
    
dfs = pd.concat(df_list, ignore_index=True)
dfg = dfs.groupby('time').agg('mean')
dfg['angle'] = [mpcalc.wind_direction(u*units('m/s'), v*units('m/s'), convention='to').m for u, v in zip(dfg['uo'], dfg['vo'])]
# dfg['direction'] = [mpcalc.angle_to_direction(ang, full=True, level=1) for ang in dfg['angle']]
dfg.to_csv('kepri_current_mean.csv')

dfg = pd.read_csv('kepri_current_mean.csv')
dfg['direction'] = [mpcalc.angle_to_direction(ang, full=True, level=1) for ang in dfg['angle']]
dfg.to_csv('kepri_current_mean.csv')

