kindCOMPANYINFO = 'Company_Info'
bucketUPLOAD = 'production_upload_data_sentiment-analysis-379200'

# Compute Engine properties

computeZONE = "us-central1-a"
computeINSTANCETEMPLATEURL = "global/instanceTemplates/production-model-vm-template"
computePROJECTID = "sentiment-analysis-379200"
computeSTARTUPSCRIPT = """#! /bin/bash
cd /
curl -H 'Cache-Control: no-cache, no-store' -o startup-script.sh https://raw.githubusercontent.com/ckury/uconn-sentiment-automation/main/startup-script.sh
bash startup-script.sh
"""

datastoreNAMESPACEKEYWORDS = 'Sentiment_Keywords'