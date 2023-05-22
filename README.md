# indonesia-deforestation
studying deforestation in indonesia by analyzing logging concessions, oil palm concessions, protected areas, and more 

## File structure breakdown:

### Folders
`/data`
- contains raw datasets

`/outputs`
- contains outputs from analyses

`/exploratory-analysis-results`
- extensive collection of images from exploratory analysis

### Scripts
- `adjacencies.ipynb` creates the adjacency matrices of logging concessions and some exploratory analysis
- `exploratory_analysis.ipynb` performs extensive exploratory analysis on logging concessions dataset
- `features.ipynb` aggregates Busch grid data with logging concessions and populates `outputs/features_by_logging_concession.csv`
- `features_oilpalm.ipynb` aggregates Busch grid data with oil palm concessions and populates `outputs/features_by_oilpalm_concession.csv`
- `integrate_features_by_concession.py` runs all the processing needed to populate `features_by_logging_concession.csv` (does the same as the first 24 cells of features.py but is in script form)
- `interaction_measures.ipynb` investiages different interaction measures between logging concessions
- `logging_vs_oilpalm_concessions.ipynb` begins analyzing relationships between logging and oil palm concessions
- `neighboring_effects_analysis.ipynb` does statistical analysis on neighbor effects on logging concessions as well as multiple linear regression of features vs. deforestation 
- `cell_reference_coord_determination.ipynb` does regressions analysis to determine what part of the Busch cells the given coordinate position corresponds to (see file for detailed description)
- `plotting_cell_reference_coord_determination.py`- does some visualization for helping with `cell_reference_coord_determination.ipynb`

Files actively being used for data analysis:
- `interaction_measures.ipynb` 
- `neighboring_effects_analysis.ipynb`
- `logging_vs_oilpalm_concessions.ipynb`

### Misc
- `cells.pptx` - illustrates 
- `covariates_desriptions.xlsx` explains how grid data was consolidated with concessions 



### Explanation of files in `/data`
- original datasets for logging concessions from the Ministry of Forestry
    - source: https://globil-panda.opendata.arcgis.com/maps/c69f5c140667471681eb48d673653ac2/about

    Managed_Forest_Concessions_(WRI).csv

    Managed_Forest_Concessions_(WRI).geojson

    Managed_Forest_Concessions_(WRI).kml

    Managed_Forest_Concessions_(WRI).zip


- original datasets of shapefiles for oil palm concessions from Greenpeace:

    Greenpeace_Indonesia_Oil_Palm_Concessions_Map_Nov_2020.dbf

    Greenpeace_Indonesia_Oil_Palm_Concessions_Map_Nov_2020.prj

    Greenpeace_Indonesia_Oil_Palm_Concessions_Map_Nov_2020.shp

    Greenpeace_Indonesia_Oil_Palm_Concessions_Map_Nov_2020.shx

- greenpeace.csv is oil palm concession data in csv form, from greenpeace


- Protected areas shapefiles are split across three sets:

    protected_areas_0.shp,
    protected_areas_0.shx

    protected_areas_1.shp,
    protected_areas_1.shx

    protected_areas_2.shp,
    protected_areas_2.shx


- grid_coords.csv contains information about the Busch cells' coordinates and area

- indonesia_boundary.json is a high resolution polygon shapefile containing the boundary of Indonesia
    - source: https://geodata.mit.edu/catalog/stanford-py486tm4357
- indonesia-provinces.geojson is a lower-resolution dataset of the boundary of indonesia (more time-friendly for doing initial calculations with)
    - source: https://github.com/superpikar/indonesia-geojson/blob/master/indonesia.geojson

- loggingconcessions_companies.csv and oilpalmconcessions_companies.csv are lists of the companies of the respective concession type; data is directly from the original datasets 


### Sources
- Busch et al. 2015 for grid-level deforestation and land feature data: https://www.pnas.org/doi/full/10.1073/pnas.1412514112 
    - dataset: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/28615&studyListingIndex=0_9abdc6f0f22513af2201195407de
- Logging concessions from Ministry of Forestry via the WWF dataset: https://globil-panda.opendata.arcgis.com/maps/c69f5c140667471681eb48d673653ac2/about    
- Greenpeace for oil palm concessions dataset was directly emailed, see `data/Greenpeace Oil Palm Concessions.zip`
- Protected Areas dataset: https://www.protectedplanet.net/country/IDN
- Low-resolution Indonesia boundary shapefiles: https://github.com/superpikar/indonesia-geojson/blob/master/indonesia.geojson
- High-resolution Indonesia boundary shapefiles: https://geodata.mit.edu/catalog/stanford-py486tm4357

### Dependencies:
- Python 3.9.5 (3.8 should work)

`
matplotlib==3.5.1
numpy==1.21.5
pandas==1.4.1
geopandas==0.6.1
descartes==1.1.0
scipy==1.7.3
statsmodels==0.13.2
seaborn==0.11.2
`