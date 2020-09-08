import argparse
from . import colors, ui, filter, query, stats
import os
import sys
from os import path
import configparser
from datetime import datetime


def main():
    """Main function
    """

    def str2bool(v):
        if isinstance(v, bool):
            return v
        if v.lower() in ('yes', 'true', 't', 'y', '1'):
            return True
        elif v.lower() in ('no', 'false', 'f', 'n', '0'):
            return False
        else:
            raise argparse.ArgumentTypeError('Boolean value expected.')

    parser = argparse.ArgumentParser(description='Create UKBB cohort.')
    parser.add_argument('--config', action='store', dest='config_file',
                        help='Location of config file if provided, optional',
                        default=None)
    # parser.add_argument('--gp_clinical_file', action='store', dest='gpc_path',
    #                     help='Path and name of gp_clinical table (txt). If providing path to an existing gp_clinical file, set portal_access parameter to False.',
    #                     default=None)

    args = parser.parse_args()
    cols = colors.terminal

    # defaults:
    aux_dir = './data_files'

    # constants:
    coding_filename = os.path.join(aux_dir, "codings.csv")
    showcase_filename = os.path.join(aux_dir, "showcase.csv")
    readcode_filename = os.path.join(aux_dir, "readcodes.csv")

    # Create or read config file.
    if not args.config_file:
        print(cols['orange'] + 'No config file provided. Creating config file.' + cols['default'])
        config_directory = input('Please specify directory for config file [`.` for current directory]: ')
        overwrite = 'N'
        while path.exists(config_directory+'config.conf') and overwrite not in ['y, Y']:
            overwrite = input('File exists. Overwrite? [Y/N]: ')
            config_directory = input('Please specify directory for config file: ')
        main_filename = input('Please specify the full path and name of main dataset: ')
        gp_clinical_file = input('Please specify the path and name of the GP clinical file (see README for how to download this). If you do not want to query this dataset, please type NO')
        out_path = input('Please specify the output directory for generated files: ')
        out_filename = input('Please specify the name of the file to store the list of ids for the cohort: ')

        with open(os.path.join(config_directory, "config.conf"), "w+") as file:
            file.write('[PATHS]\n'
                       f'main_filename = "{main_filename}"\n'
                       f'gp_clinical_file = "{gp_clinical_file}"\n'
                       f'out_path = "{out_path}"\n'
                       f'out_filename = "{out_filename}"\n')

        config = configparser.ConfigParser()
        config.read(f'{config_directory}'+'/config.conf')
        main_filename = config['PATHS']['main_filename'].strip('""')
        gp_clinical_file = config['PATHS']['gp_clinical_file'].strip('""')
        out_path = config['PATHS']['out_path'].strip('""')
        out_filename = config['PATHS']['out_filename'].strip('""')
        if gp_clinical_file in ['NO', 'No', 'no']:
            gp_clinical_file = None
    else:
        config_filepath = args.config_file
        if len(config_filepath.split('/')) > 1:
            config_filename = config_filepath.split('/')[-1]
            config_directory = config_filepath.split('/')[0]
        else:
            config_directory = '.'
            config_filename = config_filepath

        config = configparser.ConfigParser()
        config.read(config_filepath)
        main_filename = config['PATHS']['main_filename'].strip('""')
        out_filename = config['PATHS']['out_filename'].strip('""')
        out_path = config['PATHS']['out_path'].strip('""')
        gp_clinical_file = config['PATHS']['gp_clinical_file'].strip('""')
        if gp_clinical_file in ['NO', 'No', 'no']:
            gp_clinical_file = None

    if not os.path.exists(out_path):
        os.mkdir(out_path)
        print(f'"Directory {out_path} created."')
    else:
        print(f'"Directory {out_path} already exists. Appending timestamp."')
        now = datetime.now()
        dt_string = now.strftime("_%d%m_%H%M%S")
        out_path = out_path + dt_string
        os.mkdir(out_path)

    search_terms_input = input(cols['orange'] + 'Please enter comma-separated search terms: ' + cols['default'])
    search_terms = search_terms_input.split(',')

    search_df = filter.construct_search_df(showcase_filename=showcase_filename,
                                           coding_filename=coding_filename,
                                           readcode_filename=readcode_filename)
    candidate_df = filter.construct_candidate_df(searchable_df=search_df, search_terms=search_terms)
    cohort_criteria = ui.select_conditions(candidate_df=candidate_df, write_dir=out_path)
    cohort_criteria_updated = ui.update_inclusion_logic(cohort_criteria=cohort_criteria, searchable_df=search_df,
                                                        write_dir=out_path)
    queries = query.create_queries(cohort_criteria=cohort_criteria_updated, main_filename=main_filename,
                                   gpc_path=gp_clinical_file)
    eids = query.query_databases(cohort_criteria=cohort_criteria_updated, queries=queries, main_filename=main_filename,
                                 write_dir=out_path, gpc_path=gp_clinical_file, out_filename=out_filename, write=True)

    _, translation_df =stats.compute_stats(main_filename=main_filename, eids=eids, showcase_filename=showcase_filename,
                        coding_filename=coding_filename, column_keys=['34-0.0', '52-0.0', '22001-0.0', '21000-0.0',
                                                                      '22021-0.0'], out_path=out_path)

    stats.create_report(translation_df, out_path)


if __name__ == '__main__':
    main()
