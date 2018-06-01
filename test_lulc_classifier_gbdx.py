from gbdxtools import Interface
import os,sys

# Initialize the gbdxtools Interface
gbdx = Interface()

scene_id = '104001000F443900' # august 2015 (commerce city)
scene_id = '10300100612DE400' # big strip! cloudy
scene_id = '103001002B3BEF00' # january, 2014 (lakewood)
scene_id1 = '103001001AAB3D00' #8-5-2012 big strip
order_id1 = gbdx.ordering.order(scene_id1)
print (order_id)

# The order_id is unique to your image order and can be used to track the progress of your order. The ordered image sits in a directory on S3. The output of the following describes where:
status = gbdx.ordering.status(order_id)

# Make sure DRA is disabled if you are processing both the PAN+MS files
#Edit the following line(s) to reflect specific folder(s) for the output file (example location provided)
# data = str(status[0]['location'])
data = str(gbdx.ordering.status(order_id)[0]['location'])
aoptask = gbdx.Task("AOP_Strip_Processor", data=data, enable_acomp=True, bands="MS", enable_pansharpen=False, enable_dra=False)

# Capture AOP task outputs
log = aoptask.get_output('log')
orthoed_output = aoptask.get_output('data')

# Stage AOP output for the Protogen Task using the Protogen Prep Task
pp_task = gbdx.Task("ProtogenPrep",raster=aoptask.outputs.data.value)    

# Setup ProtogenV2LULC Task
prot_lulc = gbdx.Task("protogenV2LULC",raster=pp_task.outputs.data.value)
    
# Run Combined Workflow
workflow = gbdx.Workflow([ aoptask, pp_task, prot_lulc ])

# Send output to  s3 Bucket. 
# Once you are familiar with the process it is not necessary to save the output from the intermediate steps.
#Edit the following line(s) to reflect specific folder(s) for the output file (example location provided)  
# workflow.savedata(aoptask.outputs.data,location='s3://gbd-customer-data/CustomerAccount#/Protogen_LULC/')
# workflow.savedata(pp_task.outputs.data,location='s3://gbd-customer-data/CustomerAccount#/ProtoPrep/')
# workflow.savedata(prot_lulc.outputs.data,location='s3://gbd-customer-data/CustomerAccount#/Protogen_LULC/LULC/')

base_folder = 'denver_lulc_example_sw_{}_mcglinchy'.format(scene_id)
workflow.savedata(aoptask.outputs.data,location='{}/Protogen_LULC/'.format(base_folder))
workflow.savedata(pp_task.outputs.data,location='{}/ProtoPrep/'.format(base_folder))
workflow.savedata(prot_lulc.outputs.data,location='{}/Protogen_LULC/LULC/'.format(base_folder))
workflow.execute()

print(workflow.id)
print(workflow.status)


#Edit the following path to reflect a specific path to an image
raster = 's3://gbd-customer-data/CustomerAccount#/PathToImage/'
raster = 's3://gbd-customer-data/d7dcf387-b4a7-4c83-90ad-f7e26883a331/denver_lulc_example_mcglinchy/Protogen_LULC/057133793010_01/'# 057133793010_01_assembly.tif'
raster = 's3://gbd-customer-data/d7dcf387-b4a7-4c83-90ad-f7e26883a331/denver_lulc_example_mcglinchy/Protogen_LULC/057133793010_01/057133793010_01_assembly.tif'

prototask1 = gbdx.Task("protogenV2PANTEX10", raster=raster)

workflow1 = gbdx.Workflow([ prototask1 ])  
#Edit the following line(s) to reflect specific folder(s) for the output file (example location provided)
workflow1.savedata(prototask1.outputs.data, location="denver1_lulc_example_mcglinchy/protogen/BuiltUpExtent")
workflow1.execute()

print workflow.id
print workflow.status