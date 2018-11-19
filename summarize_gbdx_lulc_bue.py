#import arcpy
import rasterio, fiona
import os, sys
from rasterio.mask import mask
from matplotlib import pyplot as plt
import numpy as np
from shapely.geometry import mapping, shape


def writeProcessedShapefile(in_shp, out_shp, lulc_fnames, bue_fnames, lulc_dict, bue_dict, dates):

    with fiona.open(in_shp, 'r') as input:
        schema = input.schema.copy()
        input_crs = input.crs
    
        # add lulc field names
        for lulc_name in lulc_fnames:
            schema['properties'][lulc_name] = 'float'

        # add bue field names
        for bue_name in bue_fnames:
            schema['properties'][bue_name] = 'float'
        
        # get the lulc and bue keys for data extraction
        lulc_keys = ['lulcSummaries_' + d for d in dates]
        class_keys = lulc_dict[lulc_keys[0]][0].keys()
        bue_keys = ['bueSummaries_' + d for d in dates]
        
        # write the values
        with fiona.open(out_shp, 'w', 'ESRI Shapefile', schema, input_crs) as output:
             for i,elem in enumerate(input):
             
                  # add the lulc values
                  for lulc_name in lulc_fnames:
                      
                      # get the date and class name from field name
                      d = lulc_name.split('_')[1]
                      c = lulc_name.split('_')[0]
                      
                      # get the right data key for the fieldname 
                      ki = [ii for ii in lulc_keys if d in ii]
                      k = ki[0]
                      elem['properties'][lulc_name] = lulc_dict[k][i][c]
                      
                      
                  
                  for j,bue_name in enumerate(bue_fnames):
                      
                      # get the date for the bue name
                      d = bue_name.split('_')[1]
                      
                      # get the right data key for the fieldname 
                      ki = [ii for ii in bue_keys if d in ii]
                      k = ki[0]
                      elem['properties'][bue_name] = bue_dict[k][i]
                      
                      
                  output.write({'properties':elem['properties'],'geometry': mapping(shape(elem['geometry']))})
                  
                  
                  

def generateBUEfieldNames(bue_dict, date_list):

    bue_keys = bue_dict.keys()
    bue_fn = ['bue_{}'.format(d) for d in date_list]
    
    return bue_fn

def generateLULCfieldNames(lulc_dict, date_list):

    lulc_keys = lulc_dict.keys()
    class_keys = lulc_dict[lulc_keys[0]][0].keys()
    lulc_fn = []
    for d in date_list:
        for c in class_keys:
            f = '{}_{}'.format(c,d)
            lulc_fn.append(f)
            
    return lulc_fn



def getLULCdict(this_im, lulc):

    
    num_pix = this_im[this_im > 0].size
    
    ks = lulc.keys()
    
    a_dict = {}
    for k in ks:
        val = lulc[k]
        count = np.extract(this_im == val, this_im).size
        a_dict[k] = float(count)/num_pix
    
    return a_dict

def summarizeLULC(im, geoms_list, lulc):

    res = []
    for i,geom in enumerate(geoms_list):
    
        # open the cropped image
        this_im,fl = open_cropped_image(im, geom)
        
        # check to see if it is 0. if it is, the image doesn't intersect the geometry
        if not fl or this_im[this_im > 0].size == 0:
            null_dict = dict(zip(lulc.keys(), [0]*len(lulc.keys())))
            res.append(null_dict)
            continue
        
        # the image intersects and is valid
        else:
            res_dict = getLULCdict(this_im, lulc)
            res.append(res_dict)
    
    return res
    
def summarizeBUE(im, geom_list):

    res = []
    for i,geom in enumerate(geom_list):
    
        # open the cropped image
        this_im,fl = open_cropped_image_bue(im, geom)
        
        
        # check to see if it is 0. if it is, the image doesn't intersect the geometry
        if not fl or this_im[this_im > 0].size == 0:
            #print('something')
            res.append(0)
            continue
        
        # the image intersects and is valid
        else:
            #print ('else')
            num_pix = this_im[this_im != 2].size
            
            if num_pix == 0:
                res.append(0)
                continue
            else:
                
                val = this_im[this_im!=2].max()
                if val ==0:
                    res.append(0)
                    continue
                else:
                    count = np.extract(this_im == val, this_im).size
                    count = 0.0
                    res.append(float(count)/float(num_pix))
                
    return res



def open_cropped_image(imfile, poly):

    # open the image just on the geometry
    try:
        with rasterio.open(imfile, 'r') as src:
            out_image,_ = mask(src, [poly], crop=True)
        
        return out_image,1 #reduce the single dimension
    
    # the image doesn't overlap the geometry
    except:
    
        return 0,0
        
def open_cropped_image_bue(imfile, poly):

    # open the image just on the geometry
    try:
        with rasterio.open(imfile, 'r') as src:
            out_image,_ = mask(src, [poly], crop=True, nodata=2)
        
        return out_image,1 #reduce the single dimension
    
    # the image doesn't overlap the geometry
    except:
    
        return 0,0


def test_open_image(imfile, poly):
    with rasterio.open(imfile, 'r') as src:
        out_image = mask(src, [poly], crop=True, nodata=2)
    return out_image[0].squeeze()

shpfile = r"C:\Projects\smart_cities\Denver_Sample_Sites\DenSampleSites.shp"
#shpfile = r'C:\Users\jomc9287\Documents\ArcGIS\Default.gdb\DenSampleSites_ProjectAll'
out_shp = r"C:\Projects\smart_cities\Denver_Sample_Sites\proc_DenSampleSites.shp"

# some output info
outfolder = r'C:\Projects\smart_cities\summaries'
outgdb = os.path.join(outfolder, 'summaries.gdb')

# define the lulc images
lulc_1 = r'C:\Projects\smart_cities\exports\055530875010_01_lulc_summed.tif'
lulc_2 = r'C:\Projects\smart_cities\exports\056555743010_01_lulc_summed.tif'
lulc_3 = r'C:\Projects\smart_cities\exports\057197201010_01_lulc_summed.tif'
lulc_ims = [lulc_1, lulc_2, lulc_3]

# define the bue images
bue_1 = r"C:\Projects\smart_cities\gbdx_outputs\BUextent\055530875010_01_assembly_EXT_BEX_PANTEX10.tif"
bue_2 = r"C:\Projects\smart_cities\gbdx_outputs\BUextent\056555743010_01_assembly_EXT_BEX_PANTEX10.tif"
bue_3 = r"C:\Projects\smart_cities\gbdx_outputs\BUextent\057197201010_01_assembly_EXT_BEX_PANTEX10.tif"
bue_ims = [bue_1, bue_2, bue_3]

# define the associated dates
date_1 = '07242016'
date_2 = '06292015' 
date_3 = '10312014'
dates = [date_1, date_2, date_3]

# put them in lists
lulc_images = [lulc_1, lulc_2, lulc_3]
bue_images = [bue_1, bue_2, bue_3]
dates = [date_1, date_2, date_3]

# define the LULC values in a dictionary
codes = [128, 192, 255, 384, 402]
values = ['water', 'soil', 'veg', 'unclassified', 'shadow']
lulc_dict = dict(zip(values, codes))

# open shapefile and store geometries
with fiona.open(shpfile, "r") as shapefile:
    geoms = [feature["geometry"] for feature in shapefile]
    bounds = shapefile.bounds
    
# test an image with the first geometry    
#a = test_open_image(lulc_2, geoms[0])

# iterate through the dates, which correspond to the images
lulc_summaries = {}
bue_summaries = {}
for i, d in enumerate(dates):

    # extract geometry LULC for dates
    cur_lulc_im = lulc_ims[i]
    lulc_summaries['lulcSummaries_' + d] = summarizeLULC(cur_lulc_im, geoms, lulc_dict)
    
    # extract geometry BUE for dates
    cur_bue_im = bue_ims[i]
    bue_summaries['bueSummaries_' + d] = summarizeBUE(cur_bue_im, geoms)
    
    
    
    

# add fields and values to the shapefile! copy first.
lulc_field_names = generateLULCfieldNames(lulc_summaries, dates)
bue_field_names = generateBUEfieldNames(bue_summaries, dates)



writeProcessedShapefile(shpfile, out_shp, lulc_field_names, bue_field_names, lulc_summaries, bue_summaries, dates)