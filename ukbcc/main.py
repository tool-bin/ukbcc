import argparse
from . import colors, ui, filter, query
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
    parser.add_argument('--credentials', action='store', dest='cred_file',
                        help='Location of credentials file if provided, optional',
                        default=None)
    parser.add_argument('--portal_access,', action='store', type=str2bool, dest='portal_access',
                        help='Set to False if interaction with the UKBB Data Portal is not necessary. '
                             'Interaction will require valid application id, username, and password.'
                             'Defaults to True.',
                        default=True)
    parser.add_argument('--gp_clinical_file', action='store', dest='gpc_path',
                        help='Path and name of gp_clinical table (txt). If providing path to an existing gp_clinical file, set portal_access parameter to false.',
                        default=None)
    # parser.add_argument('--write_directory_path', action='store', dest='write_dir',
    #                     help='Path and name of directory for writing the output files',
    #                     default=None)

    args = parser.parse_args()
    cols = colors.terminal

    # defaults:
    driver_type = 'chrome'
    driver_path = '.'
    cred_file = './credentials.conf'
    aux_dir = './data_files'

    # TODO (comments for nat)
    # 1. let user input download directory for auxiliary files
    # 2. download codings, showcase, readcodes into aux_dir
    # 3. use those paths where ever we need the files
    # 4. download genomics data
    # 5. rename package to ukbcc (might require some work)
    # 6. update all documentation to match the new name, including the command line tool

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
        out_path = input('Please specify the output directory for generated files: ')
        out_filename = input('Please specify the name of the file to store the list of ids for the cohort: ')

        if args.portal_access:
            print(cols['orange'] + 'Configuration details for interaction with the portal_access. For instructions '
                                   'how to install headless drivers, please read Readme.md.' + cols['default'])
            driver_type = input('Specify driver type (chrome/firefox): ')
            driver_path = input('Specify path to driver: ')

        with open(config_directory + "/config.conf", "w+") as file:
            file.write('[PATHS]\n'
                       f'main_filename = "{main_filename}"\n'
                       f'out_path = "{out_path}"\n'
                       f'out_filename = "{out_filename}"\n'
                       f'driver_type = "{driver_type}"\n'
                       f'driver_path = "{driver_path}"\n')

        #exec(open(f'{config_directory}/config.py').read()
        config = configparser.ConfigParser()
        config.read(f'{config_directory}'+'/config.conf')
        main_filename = config['PATHS']['main_filename'].strip('""')
        out_path = config['PATHS']['out_path'].strip('""')
        out_filename = config['PATHS']['out_filename'].strip('""')
        driver_type = config['PATHS']['driver_type'].strip('""')
        driver_path = config['PATHS']['driver_path'].strip('""')

    else:
        config_filepath = args.config_file
        if len(config_filepath.split('/')) > 1:
            config_filename = config_filepath.split('/')[-1]
            config_directory = config_filepath.split('/')[0]
        else:
            config_directory = '.'
            config_filename = config_filepath

        #exec(open(f'{config_directory}/config.py').read())
        config = configparser.ConfigParser()
        config.read(config_filepath)
        main_filename = config['PATHS']['main_filename'].strip('""')
        out_filename = config['PATHS']['out_filename'].strip('""')
        out_path = config['PATHS']['out_path'].strip('""')
        driver_type = config['PATHS']['driver_type'].strip('""')
        driver_path = config['PATHS']['driver_path'].strip('""')

    # Create or read credentials file.
    # if not args.portal_access, check gpc_path - if neither, ask if gp_clinical should be queried, if yes then ask for path to write data file to, else skip
    if args.portal_access:
        if not args.cred_file:
            print(cols['orange'] + 'No credentials provided. Creating credentials file.' + cols['default'])
            cred_directory = input('Please specify directory for credentials [`.` for current directory]: ')
            overwrite = 'N'
            while path.exists(cred_directory+'credentials.conf') and overwrite not in ['y, Y']:
                overwrite = input('File exists. Overwrite? [Y/N]: ')
                cred_directory = input('Please specify directory for credentials [`.` for current directory]: ')
            application_id = input('Please enter the ID of your approved UKBB application: ')
            username = input('Please enter the username you use to log into the UKBB Data Portal: ')
            password = input('Please enter the password you use to log into the UKBB Data Portal: ')
            with open(cred_directory + "/credentials.conf", "w+") as file:
                file.write("[CREDS]\n")
                file.write(f'application_id = "{application_id}"\n')
                file.write(f'username = "{username}"\n')
                file.write(f'password = "{password}"\n')
            cred_file = cred_directory + "/credentials.conf"
        else:
            cred_file = args.cred_file
        if not args.gpc_path:
            gp_directory = input('Please specify download directory for gp_clinical dataset: ')
        else:
            gp_directory = args.gpc_path
        print("Credentials for portal access provided, downloading GP Clinical data, and saving to gp_clinical.txt in {}. This process could take a while.".format(gp_directory))
        config = configparser.ConfigParser()
        config.read(cred_file)
        application_id = config['CREDS']['application_id'].strip('""')
        username = config['CREDS']['username'].strip('""')
        password = config['CREDS']['password'].strip('""')
        query.download_gpclinical(application_id, username, password, driver_path, driver_type,
                                      download_dir=gp_directory)
    else:
        if args.gpc_path:
            print(cols['orange'] + 'GP clinical file provided. Querying GP clinical data.')
        else:
            print(cols['orange'] + 'No portal access or gp_clinical.txt file path provided. Not querying GP clinical dataset.' + cols['default'])

    if not os.path.exists(out_path):
        os.mkdir(out_path)
        print(f'"Directory {out_path} created."')
    else:
        now = datetime.now()
        dt_string = now.strftime("_%d%m_%H%M%S")
        out_path = out_path + dt_string
        os.mkdir(out_path)
        print(f'"Directory {out_path} already exists. Appending timestamp."')

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
                                   gpc_path=gp_directory)
    query.query_databases(cohort_criteria=cohort_criteria_updated, queries=queries, main_filename=main_filename,
                          write_dir=out_path, gpc_path=gp_directory, out_filename=out_filename, write=True)


if __name__ == '__main__':
    main()
