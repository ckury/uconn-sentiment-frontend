import os

from flask import Flask, render_template, request, redirect
from google.cloud import datastore, storage
from dataplots.graphing_category import data_plot_category
from dataplots.graphing_summary import data_plot_summary
from dataplots.table import data_table

"""DASH IMPORTS BEGINING"""
from dash import dash, html
from dataplots.company_data_table import company_data_table
from dataplots.topic_data_table import topic_data_table
"""DASH IMPORTS ENDING"""

from settings import bucketUPLOAD


app = Flask(__name__)

# Initialize the Datastore client
datastoreClient = datastore.Client()
storageClient = storage.Client()

@app.route('/')
def mainpage():
    return redirect("/view_data")

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/control')
def control():
    return render_template('control.html')

@app.route('/view_data')
def view_data():
    return render_template('view_data.html')

@app.route('/upload_prompt')
def upload_prompt():
    return render_template('upload_prompt.html')

@app.route('/company_info')
def company_info():
    return render_template('company_info.html')

@app.route('/topics')
def topics():
    return render_template('topics.html')

@app.route('/dataplot_placeholder')
def dataplot_placeholder():
    return render_template('dataplot_placeholder.html')

@app.route('/dataplots/data_plot')
def graph():
    ticker = request.args.get('ticker')
    sector = request.args.get('sector')
    graphType = request.args.get('type')
    weighted = request.args.get('weighted')
    startmonth = request.args.get('startmonth')
    endmonth = request.args.get('endmonth')

    if graphType == "icat":
        output = data_plot_category(ticker=ticker, sector=sector, weighted=weighted, startmonth=startmonth, endmonth=endmonth)

    if graphType == "sum":
        output = data_plot_summary(ticker=ticker, sector=sector, weighted=weighted, startmonth=startmonth, endmonth=endmonth)

    if output == 429:
        output = render_template("429.html")

    return output

@app.route('/dataplots/data_table')
def table():
    ticker = request.args.get('ticker')
    industry = request.args.get('industry')
    startmonth = request.args.get('startmonth')
    endmonth = request.args.get('endmonth')

    output = data_table(ticker=ticker, industry=industry, startmonth=startmonth, endmonth=endmonth)

    if output == 429:
        output = render_template("429.html")

    return output

@app.route('/submit_company_info', methods=['POST'])
def submit_company_info():
    if request.method == 'POST':
        yahoo_ticker = request.form['yahoo_ticker']
        industry = request.form['industry']
        long_name = request.form['long_name']

        # Check if the Yahoo ticker already exists in the database
        query = datastoreClient.query(kind='CompanyInfo')
        query.add_filter('YahooTicker', '=', yahoo_ticker)
        results = list(query.fetch(limit=1))

        # If the ticker exists, update the entity
        if results:
            company_entity = results[0]  # Get the existing entity
            company_entity.update({
                'YahooTicker': yahoo_ticker,
                'Industry': industry,
                'LongName': long_name,
            })
            datastoreClient.put(company_entity)
            return 'Yahoo ticker information updated successfully!'
        else:
            # If the ticker doesn't exist, create a new entity
            key = datastoreClient.key('CompanyInfo')
            company_entity = datastore.Entity(key=key)
            company_entity.update({
                'YahooTicker': yahoo_ticker,
                'Industry': industry,
                'LongName': long_name,
            })
            datastoreClient.put(company_entity)
            return 'Company information submitted successfully!'

    # If the request method is not POST, just return the form page
    return render_template('index.html')

@app.route('/upload_file', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file_upload']

        bucket = storageClient.get_bucket(bucketUPLOAD)
        blob = bucket.blob("Raw_CC/" + f.filename)

        blob.upload_from_file(f)
    return render_template('upload_success.html')

@app.route('/create_task', methods=['POST'])
def create_task():
    if request.method == 'POST':
        json = request.get_json()

        yahooTicker = json.get('yahooTicker')
        inputFile = json.get('inputFile')
        keywordList = json.get('keywordList')

        data = {"Yahoo_Ticker": yahooTicker, "Input_File": inputFile, "Keyword_List": keywordList}

        entity = datastoreClient.entity(datastoreClient.key("Task_List"))

        entity.update(data)

        try:
            datastoreClient.put(entity=entity)
            entityId = entity.key.id
        
        except:
            return

        # Create and Start VM
        return str(entityId)

"""DASH BEGINNING"""
dashapp_company = dash.Dash(server=False, routes_pathname_prefix="/dataplots/company_data_table/")

company_data_table(dashapp_company)

dashapp_company.init_app(app=app)

dashapp_topic = dash.Dash(server=False, routes_pathname_prefix="/dataplots/topic_data_table/")

topic_data_table(dashapp_topic)

dashapp_topic.init_app(app=app)
"""DASH ENDING"""

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))