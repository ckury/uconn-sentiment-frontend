'''
main.py main python file for UCONN Sentiment Analysis

This module uses flask to run a webserver as the frontend of the project.

Note: GCP credentials need to be set as environmental variable when running the python program.
These credentials are preset on GCP resources like App Engine and Compute Engine but need to be
set up on local systems.

Production Note: Running this file directly will use the flask development webserver. Per flask
documentation, this is not recommended for production use. Please use a production WSGI server
in a production setting. Gunicorn is installed with requirements.txt and is the recommended server.

author: Charlie Kuryluk
date: 6/3/2024

'''
# Libraries pre-installed
import os

# Libraries installed from requirements.txt
from flask import Flask, render_template, request, redirect

# Scripts included in repository
from dataplots.graphing_category import data_plot_category
from dataplots.graphing_summary import data_plot_summary

from utils.utilities import get_tickers, getDateTime

from utils.gcp.compute_engine import createVM
from utils.gcp.datastore import createEntity, queryEntities, queryKinds, queryIds, updateEntity, checkEntity, removeEntity
from utils.gcp.storage import uploadFile
# ===============================

# Settings
from settings import bucketUPLOAD, computeZONE, computeINSTANCETEMPLATEURL, computePROJECTID, computeSTARTUPSCRIPT, datastoreNAMESPACEKEYWORDS, kindCOMPANYINFO

# Flask app initialization
app = Flask(__name__)

# Flask app page setup
@app.route('/')
def mainpage():
    '''Main page does not exist, Temperary route redirects to the /view_data page'''

    return redirect("/view_data")

@app.route('/login')
def login():
    '''Login page for future auth feature'''

    return render_template('login.html')

@app.route('/control')
def control():
    '''Control page to control the model processing'''

    kinds = queryKinds(namespace=datastoreNAMESPACEKEYWORDS)
    try:
        kinds.remove('Generic')
    except ValueError:
        True

    tickers = get_tickers()

    return render_template('control.html', kinds=kinds, tickers=tickers)

@app.route('/view_data')
def view_data():
    '''Main data visualization page with graphs'''

    kinds = queryKinds(namespace=datastoreNAMESPACEKEYWORDS)
    try:
        kinds.remove('Generic')
    except ValueError:
        True

    return render_template('view_data.html', kinds=kinds)

@app.route('/info_drill', methods=['GET', 'POST'])
def info_drill():
    '''Individual conference call data viewer'''

    data = None
    if request.method == 'POST':
        yahoo_ticker = request.form.get('yahooTicker')
        period = request.form.get('period')
        category = request.form.get('category')

        results = queryEntities(kind='Banks_New', filters=[('YahooTicker', '=', yahoo_ticker), ('Period', '=', period), ('Category', '=', category)])

        data = []

        for result in results:
            format_result = dict(result)

            new_data = float(format_result['WeightedSentiment'])
            format_result['WeightedSentiment'] = f'{new_data:.3f}'

            new_data = float(format_result['Score'])
            format_result['Score'] = f'{new_data:.3f}'

            data.append(format_result)
            
    
    return render_template('info_drill.html', data=data)

@app.route('/upload_prompt')
def upload_prompt():
    tickers = get_tickers()

    return render_template('upload_prompt.html', tickers=tickers)

@app.route('/company_info')
def company_info():
    return render_template('company_info.html')

@app.route('/keyword_lists')
def topics():
    kinds = queryKinds(namespace=datastoreNAMESPACEKEYWORDS)
    return render_template('keyword_lists.html', kinds=kinds)

@app.route('/data_plot')
def data_plot():
    ticker = request.args.get('ticker')
    sector = request.args.get('sector')
    graphType = request.args.get('type')
    weighted = request.args.get('weighted')
    startmonth = request.args.get('startmonth')
    endmonth = request.args.get('endmonth')

    if graphType == "icat":
        output = data_plot_category(ticker=ticker, sector=sector, weighted=weighted, startmonth=startmonth, endmonth=endmonth)

    elif graphType == "sum":
        output = data_plot_summary(ticker=ticker, sector=sector, weighted=weighted, startmonth=startmonth, endmonth=endmonth)

    else:
        output = render_template('message_template.html', message='Use the above fields to select data, then press the "View Plot" button')

    if output == 429:
        output = render_template('message_template.html', message='Error 429: Google Cloud Firestore Data Quota Reached')

    return output

@app.route('/upload_file', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        filetype = request.form['filetype']
        ticker = request.form['ticker']
        date = request.form['date']
        f = request.files['file_upload']

        f.filename = ""

        if filetype == "CC":
            f.filename += "Raw_CC/"
        
        f.filename += ticker.replace(" ", "_") + "/"

        f.filename += date.replace("-", "_")

        f.filename += ".html"

        uploadFile(bucket_name=bucketUPLOAD, file=f)

    return render_template('upload_success.html')

@app.route('/create_task', methods=['POST'])
def create_task():
    if request.method == 'POST':
        json = request.get_json()

        datetime = getDateTime()

        entityid = createEntity("Task_List", 
                                {  "Yahoo_Ticker": json.get('yahooTicker'), 
                                   "Input_File": json.get('inputFile').replace(" ", "_"), 
                                   "Keyword_List": json.get('keywordList'), 
                                   "Status": "Waiting", 
                                   "Status_Message": "Waiting for VM to claim task and start processing", 
                                   "DateTime": datetime})
        
        createVM(computePROJECTID, computeZONE, computeINSTANCETEMPLATEURL, computeSTARTUPSCRIPT, f'production-automatic-{entityid}')
        

        # Create and Start VM
        return "Success: Task ID = " + str(entityid), "201"

@app.route('/get_keywords', methods=['GET'])
def get_keywords():
    keyword_list = request.args.get('list')

    results = queryEntities(kind=keyword_list, namespace=datastoreNAMESPACEKEYWORDS, order='Keyword')

    output = []

    for entity in results:
        output.append((entity["Keyword"], entity["Category"], entity["Weight"], entity.key.id))

    return output

@app.route('/save_list', methods=['POST'])
def save_list():
    if request.method == "POST":
        json = request.get_json()

        keyword_list = json.get('list')
        data = json.get('data')

        id_list = queryIds(kind=keyword_list, namespace=datastoreNAMESPACEKEYWORDS)

        for row in data:
            
            row_keyword = row[0]
            row_category = row[1]
            row_weight = row[2]
            row_id = int(row[4])

            if row_id not in id_list:
                createEntity(kind=keyword_list, 
                             namespace=datastoreNAMESPACEKEYWORDS, 
                             data={"Keyword": row_keyword, "Category": row_category, "Weight": row_weight})

            if row_id in id_list:
                updateEntity(checkEntity(id=row_id, kind=keyword_list, namespace=datastoreNAMESPACEKEYWORDS),
                             data={"Keyword": row_keyword, "Category": row_category, "Weight": row_weight})
                
                id_list.remove(row_id)

            
        for id in id_list:
            removeEntity(checkEntity(kind=keyword_list, 
                                     namespace=datastoreNAMESPACEKEYWORDS,
                                     id=id))
            
        return "Success", 201
    
@app.route('/get_companies', methods=['GET'])
def get_companies():

    results = queryEntities(kind='Company_Info', order='Yahoo_Ticker')

    output = []

    for entity in results:
        output.append((entity["Yahoo_Ticker"], entity["Full_Name"], entity["Sector"], entity.key.id))

    return output

@app.route('/save_company_list', methods=['POST'])
def save_company_list():
    if request.method == "POST":
        json = request.get_json()

        data = json.get('data')

        id_list = queryIds(kind=kindCOMPANYINFO)

        for row in data:
            
            row_yahoo_ticker = row[0]
            row_full_name = row[1]
            row_sector = row[2]
            row_id = int(row[4])

            if row_id not in id_list:
                createEntity(kind=kindCOMPANYINFO, 
                             data={"Yahoo_Ticker": row_yahoo_ticker, "Full_Name": row_full_name, "Sector": row_sector})

            if row_id in id_list:
                updateEntity(checkEntity(id=row_id, kind=kindCOMPANYINFO),
                             data={"Yahoo_Ticker": row_yahoo_ticker, "Full_Name": row_full_name, "Sector": row_sector})
                
                id_list.remove(row_id)

            
        for id in id_list:
            removeEntity(checkEntity(kind=kindCOMPANYINFO, id=id))
            
        return "Success", 201
# ===============================

# This runs the test server if this file is directly run
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))