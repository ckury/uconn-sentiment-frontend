# Sentiment Project Frontend
This repository holds the code used for the frontend/data visualization part of the Sentiment Project at UConn. The project includes this frontend written in python using flask and a backend running an algorithm to calculate sentiment of financial conference calls (also written in python and NLTK, available at https://github.com/ckury/uconn-sentiment-backend). A main component of the project was to use Google Cloud (thenceforth abbreviated as `GCP`) resources including Compute Engine, App Engine, Datastore and Storage. 

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
3. Enable the following services/APIs by clicking `ENABLE APIS AND SERVICES` and searching for the following: (Note this list has not been completly tested yet)
    - App Engine
    - App Engine Admin API
    - Cloud Datastore API
    - Cloud Firestore API
    - Cloud Storage
    - Cloud Storage API
    - Google Cloud APIs
4. TODO: App Engine Setup
5. TODO: Compute Engine Setup
6. TODO: Datastore Setup
7. TODO: Cloud Storage Setup

## Local code setup
To develop and test the code locally, a few things must be set up prior. Follow the below steps to set up the environment. Note that this assumes the Google Cloud CLI is already installed. I'd recommend using VSCode to manage git but any git manager works.
1. Clone the repo
2. Download nessesary packages and versions by running `pip install -r requirements.txt` (Note: Minimum Python version is 3.11)
4. Authenticate Google Cloud CLI and select project
5. (Optional) Add Google Cloud CLI to system path
6. Run `main.py` in Google Cloud CLI OR in terminal (requires Google Cloud CLI in system path)
