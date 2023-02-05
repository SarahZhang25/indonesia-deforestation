# imports
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import geopandas as gpd
import pandas as pd
import descartes
from shapely.geometry import Polygon

# mpl.rcParams['figure.dpi'] = 300 # set dpi

# base layers
indonesia = gpd.read_file("data/indonesia-provinces.geojson") # source: https://github.com/superpikar/indonesia-geojson/blob/master/indonesia.geojson
# indonesia = gpd.read_file("data/indonesia_boundary.json") # source: https://geodata.mit.edu/catalog/stanford-py486tm4357
logging_concessions = gpd.read_file("data/Managed_Forest_Concessions_(WRI).geojson")
oil_palm_concessions = gpd.read_file("data/Greenpeace_Indonesia_Oil_Palm_Concessions_Map_Nov_2020.shp")
grid = pd.read_csv("data/land_features_cells.csv")

# taking subset
# in_contention = []
# for i in range(len(grid)):
#     if grid["area"][i] < 900:
#         in_contention.append(grid.index[i])
# filtered = grid.iloc[in_contention, :]
# print(filtered)

# plotting
fig = plt.figure()
ax = plt.subplot(111)

indonesia.plot(ax=ax) # plot indonesia
logging_concessions.plot(ax=ax, color="lime", alpha=.75) # plot concession regions
oil_palm_concessions.plot(ax=ax, color="red", alpha=.55) # plot concession regions

# grid.plot.scatter(x='geo_x', y='geo_y', s=5, ax=ax, color="yellow") # plot grid coordinates
# filtered.plot.scatter(x='geo_x', y='geo_y', s=0.08,ax=ax, color="red") # plot grid coordinates


plt.axis('scaled')
plt.show()



# label concessions
# logging_concessions['coords'] = logging_concessions['geometry'].apply(lambda x: x.representative_point().coords[:])
# logging_concessions['coords'] = [coords[0] for coords in logging_concessions['coords']]

# for idx, row in logging_concessions.iterrows():
#     plt.annotate(text=logging_concessions.index[idx], xy=row['coords'],
#                  horizontalalignment='center', fontsize=10)

# plotting cell square boundaries
# geo_x	longitude
# geo_y	latitude
# 3 km latitude = 3 / 110.574 deg
# 3 km longitutde = 3 / (111.320*cos(latitude)) deg
# grid_squares = []
# for i in range(len(grid)):
#     x, y = grid['geo_x'][i], grid['geo_y'][i]
#     grid_squares.append(Polygon([(x, y), (x, y+3/110.574), (x+3/(111.320*np.cos(y)), y+3/110.574), (x+3/(111.320*np.cos(y)), y)]))

# grid['geometry'] = grid_squares
# for square in grid_squares:
    # plt.plot(*square.exterior.xy, ax=ax)

# label grid points
# for i in range(len(grid)):
    # plt.annotate(text=grid["id"][i], xy=(grid['geo_x'][i], grid['geo_y'][i]), fontsize=8)

    
# label filtered grid points
# for i in range(len(filtered)):
    # plt.annotate(text=str(filtered['id'].iloc[i,]) + ":\n" + str(int(filtered['area'].iloc[i,])), xy=(filtered['geo_x'].iloc[i,], filtered['geo_y'].iloc[i,]), fontsize=6)


# plt.show()
