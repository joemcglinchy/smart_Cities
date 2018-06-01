import shapely
from gbdxtools import Interface
import fiona
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.collections import PatchCollection
from descartes import PolygonPatch


#%matplotlib inline

def summarize_LULC_with_geometries(id, polys):


    return polys_with_summary

def get_bounds(poly):

    a=np.array(zip(poly['coordinates'][0])).squeeze()
    
    # minx, miny, maxx, maxy
    return (a[:,0].min(), a[:,1].min(), a[:,0].max(), a[:,1].max() )

def plot_geom(poly, cm=plt.get_cmap('RdBu'), num_colous=255):

    fig = plt.figure()
    ax = fig.add_subplot(111)
    
    
    minx, miny, maxx, maxy = get_bounds(poly)
    
    w, h = maxx - minx, maxy - miny
    ax.set_xlim(minx - 0.2 * w, maxx + 0.2 * w)
    ax.set_ylim(miny - 0.2 * h, maxy + 0.2 * h)
    ax.set_aspect(1)

    patches = []
    for idx, p in enumerate([poly]):
        colour = cm(1. * idx / num_colours)
        patches.append(PolygonPatch(p, fc=colour, ec='#555555', alpha=1., zorder=1))
    ax.add_collection(PatchCollection(patches, match_original=True))
    ax.set_xticks([])
    ax.set_yticks([])
    plt.title("Shapefile polygons rendered using Shapely")
    #plt.savefig('data/london_from_shp.png', alpha=True, dpi=300)
    plt.show()
    
    del fig
    del ax
    
    return


shp_fi = r"C:\Projects\smart_cities\Denver_Sample_Sites\DenSampleSites.shp"

with fiona.open(shp_fi, "r") as shapefile:
    geoms = [feature["geometry"] for feature in shapefile]
    bounds = shapefile.bounds
    
print (len(geoms))


cm = plt.get_cmap('RdBu')
num_colours = len(geoms)

# plot 1 geometry. plotting is 'off by one' from ArcMap, so feature 498 is OBJECTID 499
plot_geom(geoms[466])

# summarize the LULC result for each polygon. using the big strip first... id1
id1 = '1030010057062200' # big strip, Date: 07-24-2016, covers 88% of geometries
id2 = '1030010045AC3E00' # smaller scene, Date: 06-29-2015, covers other 12%
id3 = '1030010036314500' # smaller scene, covers some of big strip. Date: 10-31-2014, useful for repeatability

sum_geoms = summarize_LULC_with_geometries(id1, geoms)
 
