# Sentiment Project Frontend
This repository holds the code used by Google Cloud Run to host the front-end for the Sentiment project at UConn. The web application is written in python using flask with html pages. Cloud build will automatically run when a commit is pushed to the main branch and automatically deploy it to the Cloud Run service. Other branch commits are ignored and not built.

## Google Cloud Run
Google Cloud Run is the successor to App Engine. The main benefits of Cloud Run over App Engine is the flexibility that Cloud Run affords when it comes to deploying and configuring the service. To view the webapp, open up the Google Cloud console and navigate to Cloud Run. Click `uconn-sentiment-frontend` service and click the URL under the title.

## Google Cloud Build
Whenever the github repo is updated, a trigger is activated and Cloud Build will automatically clone the repo and build the docker container. Once the container is created, it is automatically deployed to Cloud Run. To manually trigger a build of the repo, navigate to Cloud Build and click on `Triggers` in the nav panel on the left. Click run on the trigger.

## Local code setup
To develop and test the code locally, a few things must be set up prior. Follow the below steps to set up the environment. Note that this assumes the Google Cloud CLI is already installed. I'd recommend using VSCode to manage git but any git manager works.
1. Clone the repo
2. Download nessesary packages and versions by running `pip install -r requirements.txt`
4. Authenticate Google Cloud CLI
5. (Optional) Add Google Cloud CLI to system path
6. Run `main.py` in Google Cloud CLI OR in terminal (requires Google Cloud CLI in system path)
