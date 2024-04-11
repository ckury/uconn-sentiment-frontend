kindCOMPANYINFO = 'Company_Info'
bucketUPLOAD = 'production_upload_data_sentiment-analysis-379200'

# Compute Engine properties

computeZONE = "us-central1-a"
computeINSTANCETEMPLATEURL = "global/instanceTemplates/production-model-vm-template"
computePROJECTID = "sentiment-analysis-379200"
computeSTARTUPSCRIPT = """#! /bin/bash
cd /
apt -y install git
git clone https://github.com/ckury/uconn-sentiment-automation
apt update
"""