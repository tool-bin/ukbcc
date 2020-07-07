import pandas as pd
import os
from selenium import webdriver
import requests
from . import utils
import io
import time


def create_queries(cohort_criteria: dict, main_filename: str, gpc_path: str) -> dict:
    """Returns query strings for gp_clinical and main dataset.

    Keyword arguments:
    ------------------
    cohort_criteria: dict
        dictionary that was created using select_conditions or update_inclusion_logic function
    main_filename: str
        path to main file
    portal_access: bool
        set to False if portal_access access is not required

    Returns:
    --------
    queries: dict(str)
        dictionary containing one query string per database
    """

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

    for database in data.keys():
        if len(data[database]) == 0:
            continue
        for logicKey in data[database]:
            if len(data[database][logicKey]) == 0:
                continue
            if gpc_path and database == 'gp_clinical':
                queries['gp_clinical'][logicKey] = _create_mds_query(gpc_path, entries=data[database][logicKey], delimiter='\t', logic=logicKey)
            elif database == 'main':
                queries['main'][logicKey] = _create_mds_query(main_filename, data[database][logicKey], logicKey)
    return queries


def query_databases(cohort_criteria: dict, queries: dict, main_filename: str, write_dir: str,
                    gpc_path: str="gp_clinical.tsv", out_filename: str = "", write: bool = False) -> list:
    """Returns eids of candidates matching the cohort criteria.

    Queries UKBB database and Main dataset for the specified cohort_criteria.

    Keyword arguments:
    ------------------
    cohort_criteria: dict
        dictionary that was created using select_conditions or update_inclusion_logic function
    queries: dict
        dictionary containing query strings for each database and logic
    main_filename: str
        path to main file
    credentials_path: str
        path to a .py file containing the variables:
        application_id: str
            ID of the project with UKBB
        username: str
            UKBB user name
        password: str
            UKBB password
    driver_path: str
        path to the driver used by selenium
    driver_type: str [chrome]
        driver_type for selenium, chrome or firefox
    timeout: int [120]
        time in seconds to wait for response from UKBB. Useful for more involved queries.
    portal_access: bool
        set to False if portal access is not required.
    gpc_path: str
        path and name of file to write gp_clinical dataset to (default = gp_clinical.tsv)
    write_dir: str
        path and name of directory to write output files to
    out_filename: str
        path and out_filename to which to write results if write == True
    write: bool [False]
        set to True to store results in file `out_filename`.

    Returns:
    --------
    eids: list
        List of eids matching the search criterion of the searchCodeDict
    """

    separate_eids = {'gp_clinical': {
        'all_of': [], 'any_of': [], 'none_of': []
    },
        'main': {
            'all_of': [], 'any_of': [], 'none_of': []
        }
    }

    main_fields = []
    for logicKey in cohort_criteria.keys():
        if len(cohort_criteria[logicKey]) == 0:
            continue
        for entry in cohort_criteria[logicKey]:
            if entry[0] not in ['read_2', 'read_3']:
                main_fields.append(entry[0])

    for database in queries.keys():
        if len(queries[database]) == 0:
            break
        for logicKey in queries[database]:
            if len(queries[database][logicKey]) == 0:
                continue
            if database == 'gp_clinical' and gpc_path:
                query = queries['gp_clinical'][logicKey]
                print("Querying gp_clinical table with: " + query)
                pgc_eids = _query_main_data(main_filename=gpc_path, delimiter='\t', keys=['read_2', 'read_3'],
                                            query=query)
                separate_eids[database][logicKey] = pgc_eids
            elif database == 'main':
                query = queries['main'][logicKey]
                print("Querying main dataset with: " + query)
                main_eids = _query_main_data(main_filename, main_fields, query)
                separate_eids[database][logicKey] = main_eids

    try:
        ands = set.intersection(*(set(x) for x in [separate_eids['gp_clinical']['all_of'],
                                                   separate_eids['main']['all_of']] if x))
    except Exception as error:
        print("Raise exception: {}".format(error))
        ands = set()
    ors = set(set(separate_eids['gp_clinical']['any_of']) | set(separate_eids['main']['any_of']))
    nots = set(set(separate_eids['gp_clinical']['none_of']) | set(separate_eids['main']['none_of']))
    try:
        ands_ors = set.intersection(*(set(x) for x in [ands, ors] if x))
    except Exception as error:
        print("Raise exceptions: {}".format(error))
        ands_ors = set()
    eids = list(ands_ors - nots)

    if write:
        output_file = write_dir + '/' + out_filename
        utils.write_txt_file(output_file, eids)
    return eids


def _create_gpc_query(entries: list, logic: str) -> str:
    """Returns query string for gp_clinical database.

    Keyword arguments:
    ------------------
    entries: list[tuples]
        each tuple consists of field and code
    logic: str
        "all_of", "any_of", or "none_of"


    Returns:
    --------
    query: str

    """
    query_start = 'SELECT distinct eid FROM gp_clinical WHERE '
    query_end = ''
    conditions = [f"{code} IS NOT NULL" if code == 'not null' else f"{field} = '{code}'" for field, code in entries]
    if logic == 'all_of':
        query_end = ' AND '.join(conditions)
    elif logic == "any_of" or logic == "none_of":
        query_end = ' OR '.join(conditions)
    query = query_start+query_end
    return query


def _create_main_query_updates(main_filename: str, cohort_criteria_sublist: list, delimiter=','):
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
        columns_list = utils.get_columns(main_filename=main_filename, keys=[field], nrows=2, delimiter=delimiter).set_index(
            'eid').columns.tolist()
        columns = [period_replace(scroll_replace(x)) for x in columns_list]
        query = _create_col_query(columns, value)
        updates.append((field, query))
    return updates


def _query_main_data(main_filename: str, keys: list, query: str, delimiter: str=',', return_df: bool=False) -> list:
    """Returns eids for given query.

    Filters main data file, extracting only keys needed, then queries it to return matching eids.

    Keyword arguments:
    ------------------
    main_filename: str
        path to main dataset
    keys: list
        list of all column_keys in the cohort_criteria
    query: str
        string to query data. most likely created using _create_mds_query.


    Returns:
    --------
    eids: list
        List of eids
    """
    main_df = utils.get_columns(main_filename, keys, delimiter=delimiter).set_index('eid')
    main_df.columns = "t" + main_df.columns.str.replace('-', '_')
    main_df.columns = main_df.columns.str.replace('.', '_')
    filtered_eids = main_df.query(query)#.reset_index()['eid'].tolist()
    if return_df:
        return filtered_eids.reset_index()
    else:
        return filtered_eids.reset_index()['eid'].tolist()

#
# def _query_gpc_data(query: str, credentials_path: str, driver_path: str, driver_type: str,
#                     timeout: int = 120) -> list:
#     """Returns eids for given query.
#
#     Queries UKBB database and list of returns eids.
#
#     Keyword arguments:
#     ------------------
#     query: str
#         string to query database. most likely created with _create_gpc_query
#     credentials_path: str
#     path to a .py file containing the variables:
#     application_id: str
#         ID of the project with UKBB
#     username: str
#         UKBB user name
#     password: str
#         UKBB password
#     driver_path: str
#         path to the driver used by selenium
#     driver_type: str
#         driver_type for selenium e.g chrome or firefox
#     timeout: int [120]
#         time in seconds to wait for response from UKBB. Useful for more involved queries.
#
#     Returns:
#     --------
#     eids: list
#         List of eids
#     """
#     supported_drivers = ['chrome', 'firefox']
#     driver_type = driver_type.lower()
#
#     if not path.exists(credentials_path):
#         sys.exit("Credentials file not found")
#
#     if driver_type not in supported_drivers:
#         raise Exception("Program only supports {} drivers, you provided {}. Please install relevant driver and "
#                         "browser. Instructions in README.md".format(supported_drivers, driver_type))
#
#     application_id = ""
#     username = ""
#     password = ""
#
#     #exec(open(f'{credentials_path}/credentials.py').read())
#     config = configparser.ConfigParser()
#     config.read(credentials_path)# + "/credentials.py")
#
#     application_id = config['CREDS']['application_id'].strip('""')
#     username = config['CREDS']['username'].strip('""')
#     password = config['CREDS']['password'].strip('""')
#     print("app id {}, username {}, password {}".format(application_id, username, password))
#     payload = download_gpclinical(query, application_id, username, password, driver_path, driver_type,
#                                   timeout)
#     response = _download_data(payload)
#     eids = _extract_eids(response)
#     return eids


def get_inverse_cohort(main_filename: str, eids: list) -> list:
    """Returns list of remaining eids.

    Keyword arguments:
    ------------------
    main_filename: str
        path to main dataframe
    eids: list
        list of eids in cohort

    Returns:
    --------
    eids: list
    """

    main_df = pd.read_csv(main_filename)
    main_eids = main_df.eid
    return list(set(main_eids) - set(eids))


def download_gpclinical(application_id: str, username: str, password: str, driver_path: str, driver_type: str,
                        download_dir: str, timeout: int = 3600) -> str:
    """Downloads gp_clinical database.

    Opens headless session to the UKBB database, logs in and downloads gp_clinical.csv into download_dir.

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
    download_dir: str
        download directory for gp_clinical.csv
    timeout: int [3600]
        optional timeout time in seconds. defaults to an hour.
    """

    prefs = {
        'download.default_directory': f'{download_dir}'
    }
    if driver_type == "chrome":
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        browser_options = Options()
        browser_options.add_argument("--headless")
        browser_options.add_experimental_option('prefs', prefs)
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=browser_options)
    elif driver_type == "firefox":
        from selenium.webdriver.firefox.options import Options
        from webdriver_manager.firefox import GeckoDriverManager
        browser_options = Options()
        browser_options.add_argument("--headless")
        browser_options.add_experimental_option('prefs', prefs)
        driver = webdriver.Firefox(executable_path=GeckoDriverManager().install(), options=browser_options)

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
    seconds = 0
    dl_wait = True
    while dl_wait and seconds < timeout:
        time.sleep(1)
        dl_wait = False
        # for fname in os.listdir('./data/'):
        #     if fname.endswith('.crdownload'):
        for fname in os.listdir(download_dir):
            if fname.endswith('.crdownload'):
                dl_wait = True
        seconds += 1
    driver.close()


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


def _construct_renaming_dict(columns: list, delimiter: str) -> (dict, list):
    """Returns dictionary to rename columns.

    Creates dictionary for renaming. Used internally to reformat main dataframe.

    Keyword arguments:
    ------------------
    columns: list[str]
        columns to be renamed
    delimiter: str
        delimiter to split column names

    Returns:
    --------
    (out, numbers): (dict, list)
        out: dictionary to be used for renaming of the columns
        numbers: list[str] of appendices
    """
    out = dict()
    numbers = []
    for c in columns:
        if c == 'eid':
            out[c] = 'eid'
        else:
            out[c] = c.split(delimiter)[-1]
            numbers.append(c.split(delimiter)[-1])
    return out, numbers

def _create_mds_query(main_filename: str,  entries: list, logic: str, delimiter: str=',') -> str:
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

    updated_entries = _create_main_query_updates(main_filename, entries, delimiter=delimiter)
    query = ""
    updated2_entries = [str(f"({code})") for field, code in updated_entries if code]
    if logic == "all_of":
        query = " and ".join(updated2_entries)
    elif logic == "any_of" or logic == "none_of":
        query = " or ".join(updated2_entries)
    return query


def _create_col_query(columns: list, value: str) -> str:
    """Returns query string for all column variations corresponding to all column_keys in 'keys' using value 'value'.

    Keyword arguments:
    ------------------
    columns: list[str]
        list of keys from the main dataset
    value: str
        target value for each column
    logic: str
        on of "all_of", "any_of", "none_of"


    Returns:
    --------
    query: str

    """

    query = ""
    columnvals = [f"{col}.notnull()" if value == 'not null' else f"{col} == '{value}'" for col in columns]
    query = " or ".join(columnvals)
    return query
