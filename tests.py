import pandas as pd
import sys
import os
from os import path
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import requests
import ukbcohort
from ukbcohort import utils
from ukbcohort import query



gpc_path = "/Users/nathaliewillems/Box/Projects/Genomics/data/UKBB_Data/gp_clinical/gp_clinical_head100.txt"

main_filename="/Users/nathaliewillems/Box/Projects/Genomics/data/UKBB_Data/main_data/ukb41268_head100.csv"

cohort_criteria = {'all_of': [], 'any_of': [('41205', '3650'), ('read_3', 'F450.'), ('read_3', 'F4503'), ('read_2', 'F450.')], 'none_of': []}

queries=query.create_queries(cohort_criteria, main_filename, gpc_path)

queries
#%%
write_dir="test_new_func"
out_filename="test_new_out.txt"
eids = query.query_databases(cohort_criteria=cohort_criteria, queries=queries, main_filename=main_filename, gpc_path=gpc_path, write_dir=write_dir, out_filename=out_filename, write=True)

#%%

gpc = "/Users/nathaliewillems/Box/Projects/Genomics/data/UKBB_Data/gp_clinical/gp_clinical_head100.txt"

gtable = pd.read_csv(gpc, delimiter='\t')
gtable.head(10)

cohort_criteria = {'all_of': [], 'any_of': [('41205', '3650'), ('read_3', 'F450.'), ('read_3', 'F4503'), ('read_2', 'F450.')], 'none_of': []}


queries = {'gp_clinical': {
    'all_of': '', 'any_of': '', 'none_of': ''
},
    'main': {
        'all_of': '', 'any_of': '', 'none_of': ''
    }
}
data = {'gp_clinical': {
    'all_of': [], 'any_of': [], 'none_of': []
},
    'main': {
        'all_of': [], 'any_of': [], 'none_of': []
    }
}
main_fields = []


for logicKey in cohort_criteria.keys():
    for entry in cohort_criteria[logicKey]:
        if entry[0] in ['read_2', 'read_3']:
            data['gp_clinical'][logicKey].append(entry)
        else:
            data['main'][logicKey].append(entry)
            main_fields.append(entry[0])

print(data['gp_clinical'])



#%%

for database in data.keys():
    if len(data[database]) == 0:
        continue
    for logicKey in data[database]:
        if len(data[database][logicKey]) == 0:
            continue
        if database == 'gp_clinical':
            queries['gp_clinical'][logicKey] = query._create_mds_query(gpc, data[database][logicKey], logicKey)
        # elif database == 'main':
        #     queries['main'][logicKey] = _create_mds_query(main_filename, data[database][logicKey], logicKey)

#%%
queries

#%%

updated_entries = _create_main_query_updates(gpc, data['gp_clinical']['any_of'])
updated_entries


#%%
queries


#%%
from ukbcohort import utils


def _create_main_query_updates(main_filename: str, cohort_criteria_sublist: list):
    """Returns list of tuples for selected column_keys from cohort_criteria.

    Creates an updated list to query the main dataset, where the first entry is the field,
    and the second entry is a pandas query string for all keys corresponding to that field.

    Keyword arguments:
    ------------------
    main_filename: str
        path to main dataset
    cohort_criteria_sublist: list[tuples]
        list of tuples from searchCodeDict
    logic: str
        one of "all_of", "any_of", or "none_of"

    Returns:
    --------
    updates: list
        List of tuples matching the search criterion of the searchCodeDict with pandas query logic
    """
    updates = []
    scroll_replace = lambda x: 't' + x.replace('-', '_')
    period_replace = lambda x: x.replace('.', '_')
    for field, value in cohort_criteria_sublist:
        columns_list = utils.get_columns(main_filename=main_filename, keys=[field], nrows=2, delimiter='\t')
        print(columns_list)
        columns = [period_replace(scroll_replace(x)) for x in columns_list]
        query = _create_col_query(columns, value)
        updates.append((field, query))
    return updates


def _create_mds_query(main_filename: str, entries: list, logic: str) -> str:
    """Returns query for main dataset.

    Keyword arguments:
    ------------------
    entries: list[tuples]
        each tuple consists of field and code
    logic: str
        one of "all_of", "any_of", "none_of"

    Returns:
    --------
    query: str

    """

    updated_entries = _create_main_query_updates(main_filename, entries)
    query = ""
    updated2_entries = [str(f"({code})") for field, code in updated_entries if code]
    if logic == "all_of":
        query = " and ".join(updated2_entries)
    elif logic == "any_of" or logic == "none_of":
        query = " or ".join(updated2_entries)
    return query


#%%
for database in data.keys():
    if len(data[database]) == 0:
        continue
    for logicKey in data[database]:
        if len(data[database][logicKey]) == 0:
            continue
        if portal_access and database == 'gp_clinical':
            queries['gp_clinical'][logicKey] = _create_gpc_query(data[database][logicKey], logicKey)
        elif database == 'main':
            queries['main'][logicKey] = _create_mds_query(main_filename, data[database][logicKey], logicKey)
return queries




#%%

def _download_data(payload: str) -> requests.Response:
    """Returns response object.

    Sends POST request to UKBB to download SQL database data. Returns response object that then needs to be parsed.
    Keyword arguments:
    ------------------
    payload: str
        Base64 encoded payload containing search query and credentials

    Returns:
    --------
    response: dict
        POST query response object
    """

    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,"
                  "application/signed-exchange;v=b3;q=0.9",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        "cache-control": "max-age=0",
        "content-type": "application/x-www-form-urlencoded",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-site",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1"
    }
    data = payload
    url = "https://biota.ndph.ox.ac.uk/regserv.cgi"
    response = requests.post(url=url, data=data, headers=headers)
    return response

def _extract_eids(response: requests.Response) -> list:
    """extracts eid field from response object.

    Keyword arguments:
    ------------------
    response: dict
        POST query response object provided by _download_data

    Returns:
    --------
    eids: list
        list containing all eids matching the search criterion.
    """
    data = io.StringIO(response.text)
    df = pd.read_csv(data, sep=",")
    return list(df['eid'])



#%%

username="nathalie.willems@ibm.com"
password="!8cLmq8evuii_u4AXwUv"
application_id="51064"
driver_path="/Users/nathaliewillems/dev/drivers/chromedriver"

query = "SELECT distinct eid FROM gp_clinical WHERE read_3 = 'F4252' OR read_3 = 'F4251' OR read_3 = 'XE18j' OR read_3 = 'XE18j' OR read_3 = 'XE18j'"
driver_type="chrome"

if driver_type == "chrome":
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.options import Options
    driver = webdriver.Chrome(ChromeDriverManager().install())
    browser_options = Options()
    browser_options.add_argument("--headless")
    # browser_options.binary_location = '/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary'
    # driver = webdriver.Chrome(executable_path=os.path.abspath(driver_path), options=browser_options)
elif driver_type == "firefox":
    from selenium.webdriver.firefox.options import Options
    browser_options = Options()
    #browser_options.add_argument("--headless")
    driver = webdriver.Firefox(options=browser_options)
else:
    raise Exception("Unsupported driver type: {}".format(driver_type))

print("USING DRIVER: {} WITH PATH {}".format(driver_type, driver_path))

driver.get("https://bbams.ndph.ox.ac.uk/ams/resProjects/dataDownToShowcase?appn_id={}".format(application_id))

username_field = driver.find_element_by_id('id_username')
password_field = driver.find_element_by_id('id_password')


username_field.send_keys(username)
password_field.send_keys(password)

login_button = driver.find_element_by_id('id_login')
login_button.click()

data_portal_button = driver.find_element_by_link_text("1 Data Portal")
data_portal_button.click()


connect = driver.find_element_by_class_name("btn_glow")
connect.click()

table_download = driver.find_element_by_link_text("Table Download")
table_download.click()

gp_table="gp_clinical"
table_input = driver.find_element_by_name("dtab")
table_input.send_keys(gp_table)

fetch_table = driver.find_element_by_xpath("//input[@value='Fetch Table']")
fetch_table.click()

driver.find_element_by_xpath("//a[contains(@href,'https://biota.ndph.ox.ac.uk/tabserv.cgi')]").click()

# browser.find_element_by_xpath("//input[@value='1']")

#%%




#%%

sql_field = driver.find_element_by_id('sq0')
sql_field.send_keys(query)

fetch = driver.find_element_by_class_name("btn_glow")
fetch.click()

timeout=60

try:
    element_present = ec.presence_of_element_located((By.NAME, 'wtoken'))
    print(element_present)
    WebDriverWait(driver, timeout).until(element_present)
except TimeoutException as ex:
    raise TimeoutException('Timed out with exception: {}. Query could be malformed or be too complex. Try increasing `timeout`.'.format(ex))

hidden_element = driver.find_element_by_name('wtoken')
value = hidden_element.get_property('value')
driver.close()
payload = "tk=" + value

print(payload)

#%%
username_field.send_keys(username)
password_field.send_keys(password)

login_button = driver.find_element_by_id('id_login')
login_button.click()

data_portal_button = driver.find_element_by_link_text("1 Data Portal")
data_portal_button.click()

connect = driver.find_element_by_class_name("btn_glow")
connect.click()

sql_field = driver.find_element_by_id('sq0')
sql_field.send_keys(query)

fetch = driver.find_element_by_class_name("btn_glow")
fetch.click()



#%%

def get_payload(query: str, application_id: str, username: str, password: str, driver_path: str, driver_type: str,
                 timeout: int) -> str:
    """Returns payload necessary to query gp_clinical database.

    Opens headless session to the UKBB database, logs in and creates the payload needed to send request to their
    database.

    Keyword arguments:
    ------------------
    query: str
        SQL query string created manually through _createGpClinicalQueryString function
    application_id: str
        ID of the project with UKBB
    username: str
        UKBB user name
    password: str
        UKBB password
    driver_path: str
        path to driver
    driver_type: str
        type of driver (either firefox or chrome)
    timeout: int
        maximal waiting time for response


    Returns:
    --------
    payload: str
        String used in request body to access data in UKBB. To be used with correct headers or as input to
        _download_data()
    """

    if driver_type == "chrome":
        from selenium.webdriver.chrome.options import Options
        browser_options = Options()
        browser_options.add_argument("--headless")
        browser_options.binary_location = '/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary'
        driver = webdriver.Chrome(executable_path=os.path.abspath(driver_path), options=browser_options)
    elif driver_type == "firefox":
        from selenium.webdriver.firefox.options import Options
        browser_options = Options()
        browser_options.add_argument("--headless")
        driver = webdriver.Firefox(options=browser_options)
    else:
        raise Exception("Unsupported driver type: {}".format(driver_type))

    print("USING DRIVER: {} WITH PATH {}".format(driver_type, driver_path))

    driver.get("https://bbams.ndph.ox.ac.uk/ams/resProjects/dataDownToShowcase?appn_id={}".format(application_id))

    username_field = driver.find_element_by_id('id_username')
    password_field = driver.find_element_by_id('id_password')

    username_field.send_keys(username)
    password_field.send_keys(password)

    login_button = driver.find_element_by_id('id_login')
    login_button.click()

    data_portal_button = driver.find_element_by_link_text("1 Data Portal")
    data_portal_button.click()

    connect = driver.find_element_by_class_name("btn_glow")
    connect.click()

    sql_field = driver.find_element_by_id('sq0')
    sql_field.send_keys(query)

    fetch = driver.find_element_by_class_name("btn_glow")
    fetch.click()

    try:
        element_present = ec.presence_of_element_located((By.NAME, 'sr'))
        WebDriverWait(driver, timeout).until(element_present)
    except TimeoutException:
        raise TimeoutException('Timed out. Query could be malformed or be too complex. Try increasing `timeout`.')

    hidden_element = driver.find_element_by_name('sr')
    value = hidden_element.get_property('value')
    driver.close()
    payload = "sr=" + value
    return payload
