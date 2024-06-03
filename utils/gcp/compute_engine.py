'''
compute_engine.py module for UCONN Sentiment Analysis

This module interfaces with GCP compute engine to do the following:

createVM -> Creates a VM with given parameters

Note: GCP credentials need to be set as environmental variable when running the python program

author: Charlie Kuryluk
date: 6/3/2024

'''

from google.cloud import compute_v1

computeClient = compute_v1.InstancesClient()

def createVM(projectid, zone, templateurl, startupscript, name):
    metadata = compute_v1.Metadata()
    items = compute_v1.Items()
    items.key = "startup-script"
    items.value = startupscript
    metadata.items = [items]
        
    instance = compute_v1.InsertInstanceRequest()

    instance.project = projectid
    instance.instance_resource.name = name
    instance.zone = zone
    instance.source_instance_template = templateurl
        
    instance.instance_resource.metadata = metadata

    requestCompute = computeClient.insert(instance)
    return requestCompute.result()