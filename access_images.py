from gbdxtools import Interface
from gbdxtools import S3Image
from gbdxtools import CatalogImage
import os,sys
import numpy as np


# create the GBDX interface
gbdx = Interface()
sinfo = gbdx.s3.info
s3_bucket = str(sinfo['bucket'])
s3_prefix = str(sinfo['prefix'])
s3_head = r's3://'
# s3path = os.path.join(s3_head, s3_bucket, s3_prefix)

# investigated result, these 3 scenes look good for coverage
id1 = '1030010057062200' # big strip, Date: 07-24-2016, covers 88% of geometries
id2 = '1030010045AC3E00' # smaller scene, Date: 06-29-2015, covers other 12%
id3 = '1030010036314500' # smaller scene, covers some of big strip. Date: 10-31-2014, useful for repeatability
ids = [id1, id2, id3]

# folder base names
base_folder = 'denver_smartCities_lulc_catalogId_{}_mcglinchy'.format(id)
aop_task_base = r'Protogen_LULC/aoptask'
protoprep_task_base = 'ProtoPrep'
LULC_base = 'Protogen_LULC/LULC'
    
# compile list of the aop-task rasters... need to get these from the task outputs 
aop_raster1 = r's3://gbd-customer-data/d7dcf387-b4a7-4c83-90ad-f7e26883a331/denver_smartCities_lulc_catalogId_1030010057062200_mcglinchy/Protogen_LULC/aoptask/055530875010_01/055530875010_01_assembly.tif'
aop_raster2 = r's3://gbd-customer-data/d7dcf387-b4a7-4c83-90ad-f7e26883a331/denver_smartCities_lulc_catalogId_1030010045AC3E00_mcglinchy/Protogen_LULC/aoptask/056555743010_01/056555743010_01_assembly.tif'
aop_raster3 = r's3://gbd-customer-data/d7dcf387-b4a7-4c83-90ad-f7e26883a331/denver_smartCities_lulc_catalogId_1030010036314500_mcglinchy/Protogen_LULC/aoptask/057197201010_01/057197201010_01_assembly.tif'

# compile list of all outputs in s3 for use as S3Image type.
