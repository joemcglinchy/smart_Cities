from gbdxtools import Interface

# create the GBDX interface
gbdx = Interface()

# use the denver AOI from GDBX Postman examples. This is the body of the POST request which returned 66 items
# {
    	# "searchAreaWkt": "POLYGON ((-105.35202026367188 39.48113956424843, -105.35202026367188 40.044848254075546, -104.65988159179688 40.044848254075546, -104.65988159179688 39.48113956424843, -105.35202026367188 39.48113956424843))",
    	# "filters": ["(bands == Multi) AND (cloudCover = '0') AND (offNadirAngle <= '15.0') AND ((sensorPlatformName == WORLDVIEW03_VNIR) OR (sensorPlatformName == WORLDVIEW02))"],
    	# "types": ["1BProduct"],
    	# "startDate": "2014-01-01T00:00:00.000Z",
  		# "endDate": "2017-11-01T23:59:59.999Z"
    # }

# set some parameters for the search
searchAOI_str = "POLYGON ((-105.35202026367188 39.48113956424843, -105.35202026367188 40.044848254075546, -104.65988159179688 40.044848254075546, -104.65988159179688 39.48113956424843, -105.35202026367188 39.48113956424843))"
filters = "(bands == Multi) AND (cloudCover = '0') AND (offNadirAngle <= '15.0') AND ((sensorPlatformName == WORLDVIEW03_VNIR) OR (sensorPlatformName == WORLDVIEW02))"
types = "1BProduct"
startDate = "2014-01-01T00:00:00.000Z"
endDate = "2017-11-01T23:59:59.999Z"

results = gbdx.catalog.search(searchAreaWkt=searchAOI_str,
                                filters=[filters],
                                types=[types],
                                startDate=startDate,
                                endDate=endDate)
                                
print(len(results))   


# investigated result, these 3 scenes look good for coverage
id1 = '1030010057062200' # big strip, Date: 07-24-2016, covers 88% of geometries
id2 = '1030010045AC3E00' # smaller scene, Date: 06-29-2015, covers other 12%
id3 = '1030010036314500' # smaller scene, covers some of big strip. Date: 10-31-2014, useful for repeatability

workflows = []       # list to hold workflow objects
base_folders = []   # list to hold base folders
aop_locs = []       # list to hold output locations for AOP tasks
ids = [id1, id2, id3]
for id in ids:

    # order the scene
    order_id = gbdx.ordering.order(id)
    print (order_id)
    
    # The order_id is unique to your image order and can be used to track the progress of your order. The ordered image sits in a directory on S3. The output of the following describes where:
    status = gbdx.ordering.status(order_id)
    print('scene ' + id + ' has been ordered, waiting for delivery...')
    
    # Make sure DRA is disabled if you are processing both the PAN+MS files
    #Edit the following line(s) to reflect specific folder(s) for the output file (example location provided)
    # data = str(status[0]['location'])
    
    while 's3' not in str(gbdx.ordering.status(order_id)[0]['location']):
        pass
    
    print('scene ' + id + ' delivered. pushing on...')
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
    
    base_folder = 'denver_smartCities_lulc_catalogId_{}_mcglinchy'.format(id)
    workflow.savedata(aoptask.outputs.data,location='{}/Protogen_LULC/aoptask/'.format(base_folder))
    workflow.savedata(pp_task.outputs.data,location='{}/ProtoPrep/'.format(base_folder))
    workflow.savedata(prot_lulc.outputs.data,location='{}/Protogen_LULC/LULC/'.format(base_folder))
    workflow.execute()
    
    workflows.append(workflow)
    base_folders.append(base_folder)
    aop_locs.append('{}/Protogen_LULC/aoptask/'.format(base_folder))
    

# all workflows have been submitted. Resubmit for the Built Up Extent task    
flag = False
while not flag:

    # check for any workflow failure
    failed_list = [w.failed for w in workflows]
    if True in failed_list:
        sys.exit('sorry, something failed!')
        
    # check if all LULC workflows have succeeded
    suc_list = [w.succeeded for w in workflows]
    if False in suc_list:
        pass
    else: # all workflows have succeeded
        flag = True

print('all LULC workflows completed. moving on to built up extent')

# compile list of the aop-task rasters... need to get these from the task outputs 
bu_workflows = []
aop_raster1 = r's3://gbd-customer-data/d7dcf387-b4a7-4c83-90ad-f7e26883a331/denver_smartCities_lulc_catalogId_1030010057062200_mcglinchy/Protogen_LULC/aoptask/055530875010_01/055530875010_01_assembly.tif'
aop_raster2 = r's3://gbd-customer-data/d7dcf387-b4a7-4c83-90ad-f7e26883a331/denver_smartCities_lulc_catalogId_1030010045AC3E00_mcglinchy/Protogen_LULC/aoptask/056555743010_01/056555743010_01_assembly.tif'
aop_raster3 = r's3://gbd-customer-data/d7dcf387-b4a7-4c83-90ad-f7e26883a331/denver_smartCities_lulc_catalogId_1030010036314500_mcglinchy/Protogen_LULC/aoptask/057197201010_01/057197201010_01_assembly.tif'
inputs = [aop_raster1, aop_raster2, aop_raster3]
for i,id in enumerate(ids):
    # when LULC is done, run the built up extent task
    prototask1 = gbdx.Task("protogenV2PANTEX10", raster=inputs[i])
    workflow1 = gbdx.Workflow([ prototask1 ])  
    #Edit the following line(s) to reflect specific folder(s) for the output file (example location provided)
    workflow1.savedata(prototask1.outputs.data, location="{}/BuiltUpExtent/".format(base_folders[i]))
    workflow1.execute()
    print workflow1.id
    print workflow1.status
    bu_workflows.append(workflow1)

[w.status for w in bu_workflows] 
# compile list of all outputs in s3 for use as S3Image type.
