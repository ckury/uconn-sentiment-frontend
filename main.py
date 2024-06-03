import os

from flask import Flask, render_template, request, redirect
from google.cloud import datastore
from dataplots.graphing_category import data_plot_category
from dataplots.graphing_summary import data_plot_summary


from settings import bucketUPLOAD, computeZONE, computeINSTANCETEMPLATEURL, computePROJECTID, computeSTARTUPSCRIPT, datastoreNAMESPACEKEYWORDS, kindCOMPANYINFO
from utils.utilities import get_tickers, getDateTime

from utils.gcp.compute_engine import createVM
from utils.gcp.datastore import createEntity, queryEntities, queryKinds
from utils.gcp.storage import uploadFile

app = Flask(__name__)

# Initialize the Datastore client
datastoreClient = datastore.Client()

@app.route('/')
def mainpage():
    return redirect("/view_data")

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/control')
def control():
    kinds = queryKinds(namespace=datastoreNAMESPACEKEYWORDS)
    try:
        kinds.remove('Generic')
    except ValueError:
        True

    tickers = get_tickers()

    return render_template('control.html', kinds=kinds, tickers=tickers)

@app.route('/view_data')
def view_data():
    kinds = queryKinds(namespace=datastoreNAMESPACEKEYWORDS)
    try:
        kinds.remove('Generic')
    except ValueError:
        True

    return render_template('view_data.html', kinds=kinds)

@app.route('/info_drill', methods=['GET', 'POST'])
def info_drill():
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
    tickers = get_tickers(datastoreClient)

    return render_template('upload_prompt.html', tickers=tickers)

@app.route('/company_info')
def company_info():
    return render_template('company_info.html')

@app.route('/keyword_lists')
def topics():
    kinds = queryKinds(namespace=datastoreNAMESPACEKEYWORDS)
    return render_template('keyword_lists.html', kinds=kinds)

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
        output.append((entity["Keyword"], entity["Category"], entity["Weight"]))

    return output

@app.route('/save_list', methods=['POST'])
def save_list():
    if request.method == "POST":
        json = request.get_json()

        keyword_list = json.get('list')
        data = json.get('data')

        for row in data:

            #TODO: Change logic to allow for row deletion
            
            query = datastoreClient.query(kind=keyword_list, namespace=datastoreNAMESPACEKEYWORDS)
            query.add_filter('Keyword', '=', row[0])
            results = list(query.fetch(limit=1))

            if results:
                entity = results[0] 

            else:
                entity = datastoreClient.entity(datastoreClient.key(keyword_list, namespace=datastoreNAMESPACEKEYWORDS))

            data = {"Keyword": row[0], "Category": row[1], "Weight": row[2]}
            
            entity.update(data)

            try:
                datastoreClient.put(entity=entity)
        
            except:
                return 
            
        return "Success", 201
    
@app.route('/get_companies', methods=['GET'])
def get_companies():

    results = queryEntities(kind='Company_Info', order='Yahoo_Ticker')

    output = []

    for entity in results:
        output.append((entity["Yahoo_Ticker"], entity["Full_Name"], entity["Sector"]))

    return output

@app.route('/save_company_list', methods=['POST'])
def save_company_list():
    if request.method == "POST":
        json = request.get_json()

        data = json.get('data')

        for row in data:

            #TODO: Change logic to allow for row deletion
            
            query = datastoreClient.query(kind=kindCOMPANYINFO)
            query.add_filter('Yahoo_Ticker', '=', row[0])
            results = list(query.fetch(limit=1))

            if results:
                entity = results[0] 

            else:
                entity = datastore.Entity(key=datastoreClient.key(kindCOMPANYINFO))

            data = {"Yahoo_Ticker": row[0], "Full_Name": row[1], "Sector": row[2]}
            
            entity.update(data)

            try:
                datastoreClient.put(entity=entity)
        
            except:
                return 
            
        return "Success", 201

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))