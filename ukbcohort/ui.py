import pandas as pd
from . import colors
from . import utils


def select_conditions(candidate_df: pd.DataFrame,  write_dir: str, inclusion_logic: str = "any_of") -> dict:
    """Returns cohort_criteria object.

    Interactively search dataframe candidate_df for conditions containing search_terms.

    Keyword arguments:
    ------------------
    candidate_df: pd.DataFrame
        searchable dataframe with the keys [Field, FieldID, Coding, Value, Meaning]
    write_dir: str
        path and name of directory to write cohort_criteria object to
    inclusion_logic: str: ["any_of"], "all_of", "none_of"

    Returns:
    --------
    cohort_criteria: dict
          dictionary containing three keys: all_of, any_of, and none_of.
          each entry holds a list of tuples (Column number, 'gp_clinical, read_2', or 'gp_clinical, read_3' and search
          code or 'not null') to be included in the search query.
          by default, "all_of" and "none_of" will be empty.
    """

    cols = colors.terminal

    print(cols["orange"] + 'The following column_keys have potentially relevant values. Please choose if you want to '
                           'include all patients who have any value in this field [a], none [hit enter], or if '
                           'you would like to choose specific values [c].' + cols["default"])
    choice = []
    field_tuples = [(candidate_df.Field.loc[a], candidate_df.FieldID.loc[a]) for a in candidate_df.index]
    for field in set(field_tuples):
        include = input("Include {}? [a/c/_] ".format(field[0]))
        field_code = field[1]
        if include in ["a", "A"]:
            choice.append((field_code, 'not null'))
        elif include in ["c", "C"]:
            print(cols["bold"] + "Please choose which codes to include [i] or skip entry [hit enter], skip rest of "
                                 "field [s]." + cols["default"])
            field_df = candidate_df[candidate_df.Field == field[0]]
            meaning_tuples = [(field_df.Meaning.loc[a], field_df.Value.loc[a]) for a in field_df.index]
            for meaning in set(meaning_tuples):
                include = input('    Include {}? [i/_/s] '.format(meaning[0]))
                if include in ['i', 'I']:
                    choice.append((field_code, meaning[1]))
                if include in ['s', 'S']:
                    break
    cohort_criteria = dict()
    cohort_criteria[inclusion_logic] = choice
    cohort_filename = write_dir + "/cohort_dictionary.txt"
    utils.write_dictionary(cohort_criteria, cohort_filename)
    return cohort_criteria


def update_inclusion_logic(cohort_criteria: dict, searchable_df: pd.DataFrame, write_dir: str) -> dict:
    """Returns updated cohort_criteria object

    Interactively update for logical search conditions.

    Keyword arguments:
    ------------------
    cohort_criteria: dict
          dictionary with three keys: and, or, and none.
          each entry holds a list of tuples (Column number, 'gp_clinical, read_2', or 'gp_clinical, read_3' and search
          code or 'not null') to be included in the search query.
    candidate_df: pd.DataFrame
        searchable dataframe with the keys [Field, FieldID, Coding, Value, Meaning]
    write_dir: str
        path and name of directory to write cohort_criteria object to


    Returns:
    --------
    cohort_criteria: dict
          dictionary with three keys: and, or, and none.
          each entry holds a list of tuples (Column number, 'gp_clinical, read_2', or 'gp_clinical, read_3' and search
          code or 'not null') to be included in the search query.
    """

    cols = colors.terminal
    print(cols['bold'] + 'Please choose if the following conditions are mandatory (every patient in your cohort '
                                'will have this condition) {}[m]{}{}, optional (every patients in your cohort will '
                                'have one or more of these conditions) {}[o]{}{}, or undesired (none of the patients '
                                'in your cohort will have this condition) {}[e]{}{}'.format(cols['green'],
                                                                                            cols['default'],
                                                                                            cols['bold'],
                                                                                            cols['blue'],
                                                                                            cols['default'],
                                                                                            cols['bold'],
                                                                                            cols['red'],
                                                                                            cols['default'],
                                                                                            cols['bold']))
    return_search_dict = {
        "all_of": [],
        "any_of": [],
        "none_of": []
    }

    for logicKey in cohort_criteria.keys():
        for entry in cohort_criteria[logicKey]:
            field = entry[0]
            value = entry[1]
            if value != 'not null':
                df_row = searchable_df.query('FieldID == "{}" and Value == "{}"'.format(field, value)).iloc[0]
                field_description = df_row['Field']
                value_description = df_row['Meaning']
            else:
                df_row = searchable_df.query('FieldID == "{}"'.format(field)).iloc[0]
                field_description = df_row['Field']
                value_description = 'not null'

            choice = input("{}, {}".format(field_description, value_description))

            if choice in ['m', 'M']:
                return_search_dict['all_of'].append(entry)
            elif choice in ['o', 'O']:
                return_search_dict['any_of'].append(entry)
            elif choice in ['e', 'E']:
                return_search_dict['none_of'].append(entry)
    cohort_filename = write_dir + "/cohort_criteria_updated.txt"
    utils.write_dictionary(return_search_dict, cohort_filename)
    return return_search_dict
