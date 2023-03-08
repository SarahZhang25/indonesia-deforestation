# imports
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import geopandas as gpd
import pandas as pd
import descartes
from shapely.geometry import Point, Polygon

print("Reading in files...")
indonesia = gpd.read_file("data/indonesia_boundary.json")
concessions = gpd.read_file("data/Managed_Forest_Concessions_(WRI).geojson")
grid = pd.read_csv("data/land_features_cells.csv")

years = [i[-2:] for i in concessions['legal_term']]
concessions["year"] = ["19"+i  if int(i) > 30 else "20"+i for i in years]

# lat/long <-> distance conversions:
# conversions: https://stackoverflow.com/questions/1253499/simple-calculations-for-working-with-lat-lon-and-km-distance#:~:text=The%20approximate%20conversions%20are%3A,111.320*cos(latitude)%20km
# geo_x	longitude; higher is eastward
# geo_y	latitude; higher is northward
# 3 km longitutde = 3 / (111.320*cos(latitude)) deg
# 3 km latitude = 3 / 110.574 deg


print("Populating coord and cell_bounds...")

coords = [] # Point object of given geo_x, geo_y
cell_bounds = [] # Polygon of cell bounds using coord as center
for i in range(len(grid)):
    x, y = grid['geo_x'][i], grid['geo_y'][i]
    dx, dy = 3/(111.320*np.cos(np.deg2rad(y))), 3/110.574
    # dx, dy = 2, 2

    coords.append(Point(x, y))    
    cell_bounds.append(Polygon([(x-dx/2, y-dy/2), (x-dx/2, y+dy/2), (x+dx/2, y+dy/2), (x+dx/2, y-dy/2)]))

grid['coord'] = coords
grid['cell_bounds'] = cell_bounds


print("Populating concessions_with_grid and pts_inside_conc...")

# populate concessions_with_grid and pts_inside_conc
# brute force until coming up with smarter way....problem is the grid is so irregular....
# thought about using nearest neighbors + minimum bounding boxes and structures for that but the grid is just hard to work with in an organized way...
concession_cells = set()
cells_per_concession = [[] for i in range(len(concessions))] # each list contains the index of the cells which are contained in it
cells_proportions_per_concession = [[] for i in range(len(concessions))] # each list contains the proportion of the area covered by the contained cells in the concession
cells_areas_per_concession =  [[] for i in range(len(concessions))] # each list contains the area covered by the contained cells in the concession
for i in range(len(grid)):
    cell = grid['cell_bounds'][i] # Polygon
    j = 0
    for concession in concessions['geometry']:
        if concession.intersects(cell):
            # calculate intersection & proportion 
            intersection = cell.intersection(concession).area
            if intersection > 0:
                concession_cells.add(i)
                cells_per_concession[j].append(i)
                cells_areas_per_concession[j].append(intersection)
                cells_proportions_per_concession[j].append(intersection / cell.area)
        j += 1



total_area_per_concession_from_cell = np.array([sum(ls) for ls in cells_areas_per_concession])
total_area_per_concession_from_shape = np.array([shape.area for shape in concessions['geometry']])
cells_vs_shape_areas = total_area_per_concession_from_cell/total_area_per_concession_from_shape
insufficient_data_25 = [i for i in range(len(cells_vs_shape_areas)) if cells_vs_shape_areas[i] < .25]
insufficient_data_50 = [i for i in range(len(cells_vs_shape_areas)) if cells_vs_shape_areas[i] > .25 and cells_vs_shape_areas[i] < .5]

# populate all data per concession
print("Populating all land features per concession...")

fields = ['id', 'area', 'year', 'slope','elev', 'distroad', 'distcapital', 'peatdepth', 'biomasscarbonruesch', 'soilcarbon', 'biomasscarbonbaccini', 
    'defor2000', 'defor2001','defor2002','defor2003','defor2004','defor2005','defor2006', 'defor2007','defor2008','defor2009']#,
    # 'slope_std', 'elev_std', 'distroad_std', 'distcapital_std', 'biomasscarbonruesch_std', 'soilcarbon_std', 'peatdepth_std', 'biomasscarbonbaccini_std']
fields_dict = {key:[] for key in fields}
num_concessions = len(concessions)


# plain avg
def average_by_cell(key):
    """
    in-place modification/population of fields_dict
    for keys: slope, elev, distroad, distcapital, peatdepth
    """
    for i in range(num_concessions):
        if i in insufficient_data_25:
            fields_dict[key].append(float("NaN"))
        else:
            # print(i)
            cells_contained = cells_per_concession[i]
            # print([grid.iloc[cell, :][key] for cell in cells_contained])
            fields_dict[key].append(np.average([grid.iloc[cell, :][key] for cell in cells_contained]))
            # print(fields_dict[key][-1])

        # do std dev
        # fields_dict[key+"_std"].append(np.std([grid.iloc[cell][key] for cell in cells_contained]))

# area based avg
def average_by_cell_areas(key):
    """
    in-place modification/population of fields_dict
    for keys: biomasscarbonruesch, biomasscarbonbaccini, soilcarbon
    """
    for i in range(num_concessions):
        if i in insufficient_data_25:
            fields_dict[key].append(float("NaN"))
        else:
            cells_contained = cells_per_concession[i]
            areas = cells_areas_per_concession[i]
            proportions = cells_proportions_per_concession[i]
            # print("prop", proportions)
            # print("cell", list(grid.iloc[cells_contained, :][key]))

            proportional_qtys = []
            # total_area = concessions['area'][i] # given
            total_area = sum(areas) # calculuated - should be equiv to ^ 
            for i in range(len(cells_contained)):
                proportional_qtys.append(proportions[i] * grid.iloc[cells_contained[i], :][key])
            # print("qtys", proportional_qtys)
            # print(sum(proportional_qtys), total_area)

            fields_dict[key].append(sum(proportional_qtys)/total_area)

            
        # do std dev (just using attributes from all intersecting cells)
        # fields_dict[key+"_std"].append(np.std([grid.iloc[cell][key] for cell in cells_contained]))

# summing, also doing interpolation
def sum_by_cell_areas(key):
    """
    in-place modification/population of fields_dict
    for keys: all defor200X
    """
    for i in range(num_concessions):
        if i in insufficient_data_25:
            fields_dict[key].append(float("NaN"))
        else:
            cells_contained = cells_per_concession[i]
            areas = cells_areas_per_concession[i]
            proportions = cells_proportions_per_concession[i]
            # print("prop", proportions)
            # print("cell", list(grid.iloc[cells_contained, :][key]))

            proportional_qtys = []
            given_area = concessions['geometry'][i].area # given
            recon_area = sum(areas) # reconstructed/calculuated area - should be (close to) equiv to ^ 
            for i in range(len(cells_contained)):
                proportional_qtys.append(proportions[i] * grid.iloc[cells_contained[i], :][key])
            # print("qtys", proportional_qtys)
            # print(sum(proportional_qtys), total_area)

            # do area corrrection
            total = sum(proportional_qtys) / recon_area * given_area

            fields_dict[key].append(total)

# populate fields
fields_dict['id'] = [i for i in range(1, num_concessions+1)]
fields_dict['area'] = [concessions['area_ha'][i] for i in range(num_concessions)]
fields_dict['year'] = [concessions['year'][i] for i in range(num_concessions)]

for field in fields[3:8]:
    # 'slope','elev', 'distroad', 'distcapital', 'peatdepth'
    print("averaging FIELD:", field)
    average_by_cell(field)

for field in fields[8:11]:
    # 'biomasscarbonruesch', 'soilcarbon', 'biomasscarbonbaccini'
    print("averaging by area FIELD:", field)
    average_by_cell_areas(field)

for field in fields[11:21]:
    # 'defor2000', 'defor2001','defor2002','defor2003','defor2004','defor2005','defor2006', 'defor2007','defor2008','defor2009'
    print("summing FIELD:", field)
    sum_by_cell_areas(field)


# do proportions
print("Populating proportions for all land features per concession...")

for field in fields[11:21]:
    print("FIELD: prop", field)
    # print(fields_dict[field][i],fields_dict['area'][i])

    fields_dict[field+"prop"] = []
    for i in range(len(fields_dict[field])): # for every concession
        if float(fields_dict['area'][i]) == 0: # NaN if concession area is 0 
            fields_dict[field+"prop"].append( float("NaN") )
        else: # take proportion = value/area
            fields_dict[field+"prop"].append( fields_dict[field][i] / float(fields_dict['area'][i]) )
    print(len(fields_dict[field+"prop"])) # sanity check


fields_dict["num_cells"] = [len(ls) for ls in cells_per_concession]


print("Populating cumulative and avg cumul deforestation up to 2009...")
# cumulative and avg cumul deforestation up to 2009
# calculated by summing from the year the concession was introduced through 2009
# do proportions
fields_dict['defor_cumul'] = []
fields_dict['defor_cumul_avg'] = []
for i in range(len(fields_dict['defor2000'])):
    # print(i)
    conc_year = fields_dict['year'][i]
    # print(conc_year)

    defor_lists = [fields_dict[field][i] for field in fields[11:21] if int(field[-4:]) >= int(conc_year)]

    fields_dict['defor_cumul'].append(sum(defor_lists))
    fields_dict['defor_cumul_avg'].append(np.mean(defor_lists))

# cumulative proportion of deforestation - make this a proportion
fields_dict['defor_cumul_prop'] = [fields_dict['defor_cumul'][i]/float(fields_dict['area'][i]) if float(fields_dict['area'][i]) > 0 else np.NaN for i in range(len(fields_dict['defor_cumul']))]
fields_dict['defor_cumul_prop_avg'] = [fields_dict['defor_cumul_avg'][i]/float(fields_dict['area'][i]) if float(fields_dict['area'][i]) > 0 else np.NaN for i in range(len(fields_dict['defor_cumul_avg']))]

# [f(x) if condition else g(x) for x in sequence]


print("Populating years_in_effect and degree...")

# years the concession is in effect during 2001 and 2009
fields_dict["years_in_effect"] = 2010 - np.array([max(int(yr), 2000) for yr in concessions["year"]])

# import adjacency matrix
adj_mat = pd.read_csv("outputs/logging_concession_adjacencies_no_buffer.csv", header=None)
fields_dict["degree"] = [sum(adj_mat.iloc[i, :]) for i in range(len(adj_mat))]


# export
print("Exporting...")
features_df = pd.DataFrame.from_dict(fields_dict)
features_df.to_csv("outputs/features_by_logging_concession_new.csv", index=False)

    
#TODO: still need to copy over the following fields
# make this in the post-initial processing part in a function that can vary the threshold
#      over 50th percentile stuff (deforestation by year, count, ), over 50p normed?
# degree
# fix the stuff that references indices of the fields dict to referencing actual names bc this file will have changed the order of the keys

'''
Features processed:
Index(['id', 'area', 'year', 'slope', 'elev', 'distroad', 'distcapital',
       'peatdepth', 'biomasscarbonruesch', 'soilcarbon', 'biomasscarbonbaccini', 
       'defor2000', 'defor2001', 'defor2002', 'defor2003', 'defor2004', 
       'defor2005', 'defor2006', 'defor2007', 'defor2008', 'defor2009', 
       'defor2000prop', 'defor2001prop', 'defor2002prop', 'defor2003prop', 'defor2004prop', 
       'defor2005prop', 'defor2006prop', 'defor2007prop', 'defor2008prop', 'defor2009prop',
       'num_cells', 'defor_cumul', 'defor_cumul_avg', 'defor_cumul_prop', 'defor_cumul_prop_avg', 
       'years_in_effect', 'degree],
      dtype='object')
'''