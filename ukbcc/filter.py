import pandas as pd


def construct_search_df(showcase_filename: str, coding_filename: str, readcode_filename: str) -> pd.DataFrame:
    """Returns searchable dataframe.

    Constructs one dataframe from showcase.csv, codings.csv (downloaded through utils.download_latest_files),
    and readcodes.csv (provided).

    Keyword arguments:
    ------------------
    showcase_filename: str
        location of showcase.csv
    coding_filename: str
        location of codings.csv
    readcode_filename: str
        location of readcodes.csv

    Returns:
    --------
    candidate_df: pd.DataFrame
        searchable dataframe with the keys [Field, FieldID, Coding, Value, Meaning,]
    """

    showcase = pd.read_csv(showcase_filename, dtype=str)
    codings = pd.read_csv(coding_filename, dtype=str)
    readcodes = pd.read_csv(readcode_filename, dtype=str)

    print("construct_search_df(): finished reading files")
    
    showcase_excerpt = showcase[['Field', 'FieldID', 'Coding']]

    #print(1)
    readcodes = readcodes.query("type == 'read_2' or type == 'read_3'").rename(
        columns={"type": "Coding", "code": "Value", "description": "Meaning"})
    #print(1.5)
    readcodes['Field'] = 'gp_clinical, ' + readcodes.Coding
    readcodes['FieldID'] = readcodes.Coding
    readcodes = readcodes.drop(["Unnamed: 0"], axis=1)
    #print(2)

    searchable_df = showcase_excerpt.merge(codings, how='outer', on="Coding")
    #print(3)
    searchable_df = pd.concat([searchable_df, readcodes])
    #print(4)

    searchable_df.Coding = searchable_df.Coding.astype('str')
    #print(5)
    searchable_df.FieldID = searchable_df.FieldID.astype('str')
    #print(6)

    #print("construct_search_df(): returning")

    return searchable_df


def construct_candidate_df(searchable_df: pd.DataFrame, search_terms: list) -> pd.DataFrame:
    """Returns dataframe containing conditions specified in search_terms.

    Keyword arguments:
    ------------------
    candidate_df: pd.DataFrame
        searchable dataframe with the keys [Field, FieldId, Coding, Value, Meaning]
    search_terms: list(str)
        conditions to include in the search

    Returns:
    --------
    candidate_df: pd.DataFrame
        filtered dataframe containing relevant candidate columns only with the keys
        [Field, FieldID, Coding, Value, Meaning]

    """

    search_terms = [x.strip(' ').lower() for x in search_terms]

    fields = searchable_df.Field.str.lower().str.contains('|'.join(search_terms), na=False)
    meanings = searchable_df.Meaning.str.lower().str.contains('|'.join(search_terms), na=False)
    candidate_df = searchable_df[fields].merge(searchable_df[meanings], how='outer')
    return candidate_df


def construct_cohort_criteria(all_of: list, any_of: list, none_of: list) -> dict:
    """Returns formatted cohort_criteria dictionary.

    Expects lists of tuples with each tuple being (key, value), where key is the base column id in the main dataset
    or 'gp_clinical, read_2' 'gp_clinical, read_3' for gp_clinical dataset. To find relevant keys and values, run construct_candidate_df with
    desired search terms.
    Every entry in your cohort will have the key-value pairs in 'all_of'.
    Every entry in your cohort will have one or more of the key-value-pairs in 'any_of'
    No entry will have the key-value pairs in 'none_of'

    To include a column entirely, set value to 'not null'.
    To exclude anyone who has a value recorded in a column, add tuple (<column_key>, 'not null') to 'none_of' list.


    Keyword arguments:
    ------------------
    all_of: list[tuple]
    any_of: list[tuple]
    none_of: list[tuple]

    Returns:
    --------
    cohort_criteria: dict
          dictionary containing three keys: all_of, any_of, and none_of.
          each entry holds a list of tuples (Column number, 'gp_clinical, read_2', or 'gp_clinical, read_3' and search
          code or 'not null') to be included in the search query.
          by default, "all_of" and "none_of" will be empty.
    """

    cohort_criteria = {
        "all_of": all_of,
        "any_of": any_of,
        "none_of": none_of
    }

    return cohort_criteria
