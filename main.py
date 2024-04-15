import os

from flask import Flask, render_template, request, redirect
from google.cloud import datastore, storage, compute_v1
from dataplots.graphing_category import data_plot_category
from dataplots.graphing_summary import data_plot_summary
from dataplots.table import data_table

from settings import bucketUPLOAD, computeZONE, computeINSTANCETEMPLATEURL, computePROJECTID, computeSTARTUPSCRIPT, datastoreNAMESPACEKEYWORDS, kindCOMPANYINFO
from utils.utilities import get_kinds


app = Flask(__name__)

# Initialize the Datastore client
datastoreClient = datastore.Client()
storageClient = storage.Client()
computeClient = compute_v1.InstancesClient()

@app.route('/')
def mainpage():
    return redirect("/view_data")

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/control')
def control():
    kinds = get_kinds(datastoreClient, datastoreNAMESPACEKEYWORDS)
    try:
        kinds.remove('Generic')
    except ValueError:
        True

    return render_template('control.html', kinds=kinds)

@app.route('/view_data')
def view_data():
    return render_template('view_data.html')

@app.route('/info_drill', methods=['GET', 'POST'])
def info_drill():
    data = None
    if request.method == 'POST':
        yahoo_ticker = request.form.get('yahooTicker')
        period = request.form.get('period')
        category = request.form.get('category')

        query = datastoreClient.query(kind='Banks_New')
        query.add_filter('YahooTicker', '=', yahoo_ticker)
        query.add_filter('Period', '=', period)
        query.add_filter('Category', '=', category)
        results = list(query.fetch())

        data = [dict(result) for result in results]
    
    return render_template('info_drill.html', data=data)

@app.route('/upload_prompt')
def upload_prompt():
    return render_template('upload_prompt.html')

@app.route('/company_info')
def company_info():
    return render_template('company_info.html')

@app.route('/keyword_lists')
def topics():
    kinds = get_kinds(datastoreClient, datastoreNAMESPACEKEYWORDS)
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

        data = {"Yahoo_Ticker": yahooTicker, "Input_File": inputFile, "Keyword_List": keywordList, "Status": "Waiting", "Status_Message": "Waiting for VM to claim task and start processing"}

        entity = datastoreClient.entity(datastoreClient.key("Task_List"))

        entity.update(data)

        try:
            datastoreClient.put(entity=entity)
            entityId = entity.key.id
        
        except:
            return
        
        metadata = compute_v1.Metadata()
        items = compute_v1.Items()
        items.key = "startup-script"
        items.value = computeSTARTUPSCRIPT
        metadata.items = [items]
        
        instance = compute_v1.InsertInstanceRequest()

        instance.project = computePROJECTID
        instance.instance_resource.name = f'production-automatic-{entityId}'
        instance.zone = computeZONE
        instance.source_instance_template = computeINSTANCETEMPLATEURL
        
        instance.instance_resource.metadata = metadata

        requestCompute = computeClient.insert(instance)
        operation = requestCompute.result()

        # Create and Start VM
        return "Success:" + str(entityId), "201"

@app.route('/get_keywords', methods=['GET'])
def get_keywords():
    keyword_list = request.args.get('list')

    query = datastoreClient.query(kind=keyword_list, namespace=datastoreNAMESPACEKEYWORDS)

    query.order = ['Keyword']

    output = []

    for e in query.fetch():
        output.append((e["Keyword"], e["Category"], e["Weight"]))

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

    query = datastoreClient.query(kind='Company_Info')

    query.order = ['Yahoo_Ticker']

    output = []

    for e in query.fetch():
        output.append((e["Yahoo_Ticker"], e["Full_Name"], e["Sector"]))

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
                entity = datastoreClient.entity(datastoreClient.key(kind=kindCOMPANYINFO))

            data = {"Yahoo_Ticker": row[0], "Full_Name": row[1], "Sector": row[2]}
            
            entity.update(data)

            try:
                datastoreClient.put(entity=entity)
        
            except:
                return 
            
        return "Success", 201

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))