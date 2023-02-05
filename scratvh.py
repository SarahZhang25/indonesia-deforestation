# imports
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import geopandas as gpd
import pandas as pd
import descartes
from shapely.geometry import Point, Polygon
import random

mpl.rcParams['figure.dpi'] = 600 # set dpi

indonesia = gpd.read_file("data/indonesia_boundary.json")
grid = pd.read_csv("data/grid_coords.csv")

# only consider coords with cell area < 900
in_contention = []
for i in range(len(grid)):
    if grid["area"][i] < 900:
        in_contention.append(grid.index[i])
filtered = grid.iloc[in_contention, :]

# pick a random small subset of them to run the cell intersection calculations on
random_subset_inds = random.sample(range(len(filtered)), k=25)
filtered_subset = filtered.iloc[random_subset_inds, :].reset_index(drop=True)

# conversions: https://stackoverflow.com/questions/1253499/simple-calculations-for-working-with-lat-lon-and-km-distance#:~:text=The%20approximate%20conversions%20are%3A,111.320*cos(latitude)%20km
# geo_x	longitude; higher is eastward
# geo_y	latitude; higher is northward
# 3 km latitude = 3 / 110.574 deg
# 3 km longitutde = 3 / (111.320*cos(latitude)) deg
coords, center_squares, bl_squares, br_squares, tl_squares, tr_squares = [], [], [], [], [], []
for i in range(len(filtered_subset)):
    x, y = filtered_subset['geo_x'][i], filtered_subset['geo_y'][i]
    dx, dy = 3/(111.320*np.cos(np.deg2rad(y))), 3/110.574
    coords.append(Point(x, y))
    bl_squares.append(Polygon([(x, y), (x, y+dy), (x+dx, y+dy), (x+dx, y)]))
    br_squares.append(Polygon([(x, y), (x, y+dy), (x-dx, y+dy), (x-dx, y)]))
    tl_squares.append(Polygon([(x, y), (x, y-dy), (x+dx, y-dy), (x+dx, y)]))
    tr_squares.append(Polygon([(x, y), (x, y-dy), (x-dx, y-dy), (x-dx, y)]))
    center_squares.append(Polygon([(x-dx/2, y-dy/2), (x-dx/2, y+dy/2), (x+dx/2, y+dy/2), (x+dx/2, y-dy/2)]))

filtered_subset['coord'] = coords
filtered_subset['bl_square'] = bl_squares
filtered_subset['br_square'] = br_squares
filtered_subset['tl_square'] = tl_squares
filtered_subset['tr_square'] = tr_squares
filtered_subset['center_square'] = center_squares
filtered_subset = gpd.GeoDataFrame(filtered_subset)

# create plot
fig = plt.figure()
ax = plt.subplot(111)

indonesia.plot(ax=ax)
for col in ("bl_square", "br_square", "tl_square", "tr_square", "center_square"):
    filtered_subset.set_geometry(col).plot(ax=ax, facecolor="none", edgecolor='orange', lw=0.7)
filtered_subset.set_geometry("coord").plot(ax=ax, color='red')

plt.axis('scaled')

# label points
for i in range(len(filtered_subset)):
    plt.annotate(text=str(filtered_subset['id'].iloc[i,]) + ":" + str(int(filtered_subset['area'].iloc[i,])), xy=(filtered_subset['geo_x'].iloc[i,], filtered_subset['geo_y'].iloc[i,]), fontsize=5)

plt.show()