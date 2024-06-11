# Sentiment Project Frontend
This repository holds the code used for the frontend/data visualization part of the Sentiment Project at UConn. The project includes this frontend written in python using flask and a backend running an algorithm to calculate sentiment of financial conference calls (also written in python and NLTK, available at https://github.com/ckury/uconn-sentiment-backend). A main component of the project was to use Google Cloud (thenceforth abbreviated as `GCP`) resources including Compute Engine, App Engine, Datastore and Storage. 

*NOTE: This README and repository act as the main hub of the project. The backend repository mentioned above is a part of this project but acts as a sort of "sub-repository".*

## Project Showcase

This project's goal was to be able to run a custom sentiment analysis model on quarterly conference calls released by publicly traded companies and to visualize such data. This data would in production be used as one of many datapoints considered when making an investment decision.

The model would take in transcripts, separate them into individual paragraphs and tokenize them based on a predefined list of keywords. Then, the model will generate a score based on how positive or negative the sentiment is of the paragraph. Afterwards, the data is both uploaded to a cloud database and run through a summary program which summarizes the overall sentiment of the call. This summary is either unweighted (each keyword is considered equally important) or weighted (each keyword is assigned a predetermined value equal to the importance of the keyword).

### Pages:

#### /view_data
The view_data page is where the main data visualization occurs. This page allows you to select data by the ticker, sector or both. This page also allows you to select either weighted or unweighted sentiment scores, and if the data is based on a scoring category or if all of the data is summarized into a single data point.

![view data](/docs/images/view_data.png)

#### /info_drill
The info_drill page allows deeper and more detailed sentiment analysis with direct access to paragraphs for each conference call along with which category it was assigned and the score assigned.

![info drill](/docs/images/info_drill.png)

#### /keyword_lists
This page allows you to edit the keyword lists by which the conference calls are scored against. This page also allows you to modify the weighting of each keyword.

![keyword lists](/docs/images/keyword_lists.png)

#### /company_info
This page allows you to edit the list of companies and their info included in the system. This page also allows you to control which tickers are searched for when looking for data based on sector.

![company info](/docs/images/company_info.png)

#### /control
The control page allows you to upload conference call transcripts and run the sentiment analysis model on these transcripts with the selected keyword list.

![control](/docs/images/control.png)

### Data Pipeline

The dataflow is as follows:

#### Transcript Preparation
1. User creates a company entry in the /company_info page if not already present. This updates the company_info kind in datastore which is referenced during the data upload and processing stages.
2. User uploads transcripts through the `Upload Conference Calls` button on /control page. These files are named following input fields provided when uploading the file and are storred in a cloud bucket.

#### Processing settings
3. User selects company ticker for processing in /control
4. User selects keyword lists to be used. These can be set up in /keyword_lists if not already setup. These are expected to be consistent across multiple companies. There is an option for the generic keyword list. This list contains keywords that would be useful for all companies and can be selected separately

#### Sentiment scoring and processing
5. User clicks `Submit for Processing` button
6. Website performs the following:
    - An entry is added to task_list kind to track inprogress tasks and to store basic data like keyword lists to use and company ticker selected.
    - A VM is created to automatically handle processing.
7. VM automatically downloads keyword lists, ticker conference call transcripts and dependancies using the task_list entries and current files from the backend github repository
8. VM automatically performs conversion from the conference call input to a standard CSV format
9. VM automatically performs tokenization, scoring and summarization and outputs to local CSVs
10. VM automatically uploads data to Sentiment_Data namespace and on completion, self destructs. Throughout processing, VM updates tasklist with progress and status. VM program is designed to be run on preemptable VMs so as to save cost. This means that it will automatically recover from a preempt event.

#### Data Viewing
11. Once processing is finished, the user can view the data output either in /view_data or /info_drill


## Note about GCP
While the front-end can be run anywhere with access to the internet and the ability to enter GCP credentials, the front-end was designed specifically to interact with a GCP project and resources. Migrating to AWS, Azure or any other cloud provider or locally hosting would require copying the existing GCP code under `/utils/`, modifying the code to work with your setup and finally modifying import statements throughout the project to point to your new functions. All GCP code has been centralized to the `/utils/gcp/` directory, all other code just calls these functions. Writing support for other implementations was beyond the scope of the original project.

## Google App Engine
Google App Engine is what currently is used on the project. Migration to Google Cloud Run is placed on hold while other requirements are fullfilled. Because of this, no `app.yaml` exists in the project and must be added before `gcloud app deploy` is run. Add the following to app.yaml in the root directory:
```
runtime: python311
entrypoint: gunicorn -b :$PORT main:app
```

## How to run the project
NOTE: This project was intendend for GCP and so the following instructions are written for use with GCP. Using these instructions with other infrastructure setups would require modification and is not recomended without understanding the code. I'd recommend taking a look at the local code setup instructions below and the above note on GCP.

ADDITIONAL NOTE: GCP Resources are NOT free and thusly require either free credits or a billing method on file. These instructions assume that you have access to GCP and have a billing account set up. 
- For Free Trial information: https://cloud.google.com/docs/get-started
- For all billing information: https://cloud.google.com/billing/docs

### Setup GCP Project 
1. In the Cloud Console, Click the project selector and press `New Project`. Fill out a memerable name, ignore the organization field and press create. (Detailed Instructions: https://cloud.google.com/resource-manager/docs/creating-managing-projects) NOTE: Projects usually are created with an association to your billing account automatically, if you encounter billing problems in future steps, verify that the project has a valid billing account by following https://cloud.google.com/billing/docs/how-to/verify-billing-enabled 
2. Navigate to the left nav panel and click on APIs & Services (If the page isn't pinned to the nav panel, click `All Products` and under Management)
3. Enable the following services/APIs by clicking `ENABLE APIS AND SERVICES` and searching for the following: (Note this list has not been completely tested yet)
    - App Engine
    - App Engine Admin API
    - Cloud Datastore API
    - Cloud Firestore API
    - Cloud Storage
    - Cloud Storage API
    - Google Cloud APIs

#### Setup Compute Engine 
4. Navigate to the left nav panel and click on Compute Engine (If the page isn't pinned to the nav panel, click `All Products` and under Compute)
5. Under "Virtual Machines" in the left panel, click Instance Templates
6. Click `CREATE INSTANCE TEMPLATE` at the top and enter the following
    - Name: `production-model-vm-template` (Modifying from this requires changing `computeINSTANCETEMPLATEURL` in `settings.py`)
    - Location: `Global` (Modifying from this requires changing `computeINSTANCETEMPLATEURL` in `settings.py`)
    - Machine type: Any machine type works, recommeded type is: `e2-standard-2`
    - VM provisioning model: Either works, recommended is: `Spot` (More info: https://cloud.google.com/compute/docs/instances/spot)
    - VM provisioning model advanced settings:
        - Set time limit: `True`
        - Time limit: Anything works, recommended: `6 hours` (This prevents the machine from getting stuck and running forever. For longer processing, change this number but be mindful of errors costing more)
        - On VM termination: `Delete` (This automatically deletes the VM and removes the static resources used as this is not needed and would increase costs)
    - Change boot disk size to `32 GBs` (The dependancies are large and need more than the 10 GB default)
    - Access scopes: `Set access for each API` Modify the following: (These are required for the VM to access the correct GCP resources)
        - Cloud Datastore: `Enabled`
        - Compute Engine: `Read Write`
7. Click `CREATE` at the bottom. NOTE: Double check each option as once the template is created, it cannot be modified. You must delete and remake the template to change anything.

#### Setup App Engine
8. TODO: App Engine Setup

#### Setup Datastore
9. TODO: Datastore Setup

#### Setup Cloud Storage
10. TODO: Cloud Storage Setup

## Local code setup
To develop and test the code locally, a few things must be set up prior. Follow the below steps to set up the environment. Note that this assumes the Google Cloud CLI is already installed. I'd recommend using VSCode to manage git but any git manager works.
1. Clone the repo
2. Download nessesary packages and versions by running `pip install -r requirements.txt` (Note: Minimum Python version is 3.11)
4. Authenticate Google Cloud CLI and select project
5. (Optional) Add Google Cloud CLI to system path
6. Run `main.py` in Google Cloud CLI OR in terminal (requires Google Cloud CLI in system path)
