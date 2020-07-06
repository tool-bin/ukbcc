import argparse
from . import colors, ui, filter, query
import os
from os import path
import configparser
from datetime import datetime


def main():
    """Main function
    """
    parser = argparse.ArgumentParser(description='Create UKBB cohort.')
    parser.add_argument('--config', action='store', dest='config_file',
                        help='Location of config file if provided, optional',
                        default=None)
    parser.add_argument('--credentials', action='store', dest='cred_path',
                        help='Location of credentials file if provided, optional',
                        default=None)
    parser.add_argument('--portal_access-access,', action='store', dest='portal_access',
                        help='Set to False if interaction with the UKBB portal_access is not necessary. '
                             'Interaction will require valid application id, username, and password.'
                             'Defaults to True.',
                        default=True)
    parser.add_argument('--write_directory_path', action='store', dest='write_dir',
                        help='Path and name of directory for writing the output files',
                        default=None)

    args = parser.parse_args()
    cols = colors.terminal

    # defaults:
    driver_type = 'chrome'
    driver_path = '.'
    cred_path = '.'
    # constants:
    coding_filename = "dataFiles/codings.csv"
    showcase_filename = "dataFiles/showcase.csv"
    readcode_filename = "dataFiles/readcodes.csv"

    # Create or read config file.
    if not args.config_file:
        print(cols['orange'] + 'No config file provided. Creating config file.' + cols['default'])
        config_directory = input('Please specify directory for config file [`.` for current directory]: ')
        overwrite = 'N'
        while path.exists(config_directory+'config.py') and overwrite not in ['y, Y']:
            overwrite = input('File exists. Overwrite? [Y/N]: ')
            config_directory = input('Please specify directory for config file: ')
        main_filename = input('Please specify the full path and name of main dataset: ')
        out_filename = input('Please specify the name of the file to store the list of ids for the cohort: ')

        if args.portal_access:
            print(cols['orange'] + 'Configuration details for interaction with the portal_access. For instructions '
                                   'how to install headless drivers, please read Readme.md.' + cols['default'])
            driver_type = input('Specify driver type (chrome/firefox): ')
            driver_path = input('Specify path to driver: ')

        with open(config_directory + "/config.py", "w+") as file:
            file.write('[PATHS]\n'
                       f'main_filename = "{main_filename}"\n'
                       f'out_filename = "{out_filename}"\n'
                       f'driver_type = "{driver_type}"\n'
                       f'driver_path = "{driver_path}"\n')

        #exec(open(f'{config_directory}/config.py').read()
        config = configparser.ConfigParser()
        config.read(f'{config_directory}'+'/config.py')
        main_filename = config['PATHS']['main_filename'].strip('""')
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
        driver_type = config['PATHS']['driver_type'].strip('""')
        driver_path = config['PATHS']['driver_path'].strip('""')

    # Create or read credentials file.
    if args.portal_access:
        if not args.cred_path:
            print(cols['orange'] + 'No credentials provided. Creating credentials file.' + cols['default'])
            cred_directory = input('Please specify directory for credentials [`.` for current directory]: ')
            overwrite = 'N'
            while path.exists(cred_directory+'credentials.py') and overwrite not in ['y, Y']:
                overwrite = input('File exists. Overwrite? [Y/N]: ')
                cred_directory = input('Please specify directory for credentials [`.` for current directory]: ')
            application_id = input('Please enter the ID of your approved UKBB application: ')
            username = input('Please enter the username you use to log into the UKBB portal_access: ')
            password = input('Please enter the password you use to log into the UKBB portal_access: ')
            with open(cred_directory + "/credentials.py", "w+") as file:
                file.write("[CREDS]\n")
                file.write(f'application_id = "{application_id}"\n')
                file.write(f'username = "{username}"\n')
                file.write(f'password = "{password}"\n')
            cred_path = cred_directory
        else:
            cred_path = args.cred_path

    if args.write_dir:
        write_dir = args.write_dir
        if not os.path.exists(write_dir):
            os.mkdir(write_dir)
            print(f'"Directory {write_dir} created."')
        else:
            now = datetime.now()
            dt_string = now.strftime("_%d%m_%H%M%S")
            write_dir = write_dir + dt_string
            os.mkdir(write_dir)
            print(f'"Directory {args.write_dir} already exists. Appending timestamp."')
    else:
        now = datetime.now()
        dt_string = now.strftime("_%d%m_%H%M%S")
        write_dir = 'ukbcohort_output' + dt_string
        os.mkdir(write_dir)
        print(f'"No directory specified, default directory {write_dir} created. Storing output files here."')

    search_terms_input = input(cols['orange'] + 'Please enter search comma-separated search terms' + cols['default'])
    search_terms = search_terms_input.split(',')

    search_df = filter.construct_search_df(showcase_filename=showcase_filename,
                                           coding_filename=coding_filename,
                                           readcode_filename=readcode_filename)
    candidate_df = filter.construct_candidate_df(searchable_df=search_df, search_terms=search_terms)
    cohort_criteria = ui.select_conditions(candidate_df=candidate_df, write_dir=write_dir)
    cohort_criteria_updated = ui.update_inclusion_logic(cohort_criteria=cohort_criteria, searchable_df=search_df, write_dir=write_dir)
    queries = query.create_queries(cohort_criteria=cohort_criteria_updated, main_filename=main_filename,
                                   portal_access=args.portal_access)
    query.query_databases(cohort_criteria=cohort_criteria_updated, queries=queries, main_filename=main_filename, credentials_path=cred_path, write_dir=write_dir, driver_path=driver_path, driver_type=driver_type, timeout=120, portal_access=args.portal_access, out_filename=out_filename, write=True)


if __name__ == '__main__':
    main()
