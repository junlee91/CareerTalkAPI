from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import os, inspect, sys, re
# direct import the database_setup module.
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
from database_setup import Company


def match_company_url(raw_url, pattern):
    matches = pattern.finditer(raw_url)
    url = ''
    for m in matches:
        url = m.group(2) + m.group(3)
        if 'www.' in m.group(2):
            url = url[4:]
    return url


def get_company_info():
    SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
    SPREADSHEET_ID = '1fKG4iVnj9coxg2mwip4reD7Rt5eiBvlEDM-Hu84M3zE'
    RANGE_NAME = 'Sheet1!A4:E48'
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('../gsheet_credentials.json',
                                              SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('sheets', 'v4', http=creds.authorize(Http()))

    # Call the Sheets API
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID,
                                                 range=RANGE_NAME).execute()

    values = result.get('values', [])
    links = service.spreadsheets().get(
        spreadsheetId=SPREADSHEET_ID,
        ranges=RANGE_NAME,
        fields="sheets/data/rowData/values/hyperlink"
    ).execute()
    # print("============================================================")
    # pp = pprint.PrettyPrinter(indent=1)
    # pp.pprint(links)
    # print("============================================================")
    links_rows = links['sheets'][0]['data'][0]['rowData']
    pattern = re.compile('(//)(.+\.)(com|org|net|edu|gov|mil)')
    for val in links_rows:
        raw_url = val['values'][0]['hyperlink']
        url = match_company_url(raw_url, pattern)
        print(url)
    return values


def insert_rows():
    data = get_company_info()
    for row in data:
        name = row[0]
        if row[1].strip().lower() == 'int':
            type = 1
        elif row[1].strip().lower() == 'ft':
            type = 2
        else :
            type = 3
        if row[3].strip().lower() == 'bs':
            degree = 1
        elif row[3].strip().lower() == 'ms':
            degree = 2
        elif row[3].strip().lower() == 'phd':
            degree = 3
        elif row[3].strip().lower() == 'bs, ms':
            degree = 4
        elif row[3].strip().lower() == 'bs, phd':
            degree = 5
        elif row[3].strip().lower() == 'ms, phd':
            degree = 6
        else:
            degree = 8
        if row[4].strip().lower() == 'yes':
            visa = 1
        elif row[4].strip().lower() == 'no':
            visa = 2
        else:
            visa = 3

        print("name: {}, hiringtype: {}, degree: {}, visa: {}".format(name,
                                                                      type,
                                                                      degree,
                                                                      visa))
        print(row[2])
        print("fetching logo . . .")
        print("Adding a company . . .")

        company = Company(name=name, hiring_types=type, hiring_majors=row[2],
                          degree=degree, visa=visa, fair_id=1)
        #db_session.add(company)
        #db_session.commit()

get_company_info()