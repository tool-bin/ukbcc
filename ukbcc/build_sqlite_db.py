from . import db, colors
import argparse
import os

def main():
    """Build sqlite database.

    Keyword arguments:
    ------------------
    db_path: str
        path to write sqlite database to
    main_path: str
        path to main dataset csv file
    gp_clin_path: str
        path to gp_clinical tsv file
    showcase_path: str
        path to showcase csv file

    Returns:
    --------
    success: bool

    """
    parser = argparse.ArgumentParser(description='Create sqlite database.')
    parser.add_argument('--db_path',
                        help='Please specify the path to write the sqlite database file to e.g ./ukb_data.sqlite',
                        default=None)
    parser.add_argument('--main_path', help='Please specify the path to the main dataset file',
                        default=None)
    parser.add_argument('--gp_clin_path', help='Please specify the path to the GP clinical dataset file',
                        default=None)
    parser.add_argument('--showcase_path', help='Please specify the path to the showcase data file',
                        default=None)

    args = parser.parse_args()
    # db_file = args.db_path
    # main_file = args.main_path
    # gp_clin_file =  args.gp_clin_path
    # showcase_file = args.showcase_path
    cols = colors.terminal
    if not args.db_path:
        print(cols['orange'] + 'No db file path provided' + cols['default'])
        db_file = input('Please specify path to write the sqlite database file to e.g ./ukb_data.sqlite: ')
        overwrite = 'N'
        while os.path.exists(db_file) and overwrite not in ['y', 'Y']:
            overwrite = input('File exists. Overwrite? [Y/N]: ')
    else:
        db_file = args.db_path
    if not args.main_path:
        print(cols['orange'] + 'Main file path not provided' + cols['default'])
        main_file = input('Please specify path to main dataset csv file: ')
        while not os.path.exists(main_file):
            print(cols['orange'] + f"Main dataset file path not found in {main_file} please check the path was specified correctly" + cols['default'])
            main_file = input("Please specify correct path to main dataset file: ")
    else:
        main_file = args.main_path
    if not args.gp_clin_path:
        print(cols['orange'] + 'GP clinical file path not provided' + cols['default'])
        gp_clin_file = input('Please specify path to GP clinical dataset file: ')
        while not os.path.exists(gp_clin_file):
            print(cols['orange'] + "GP clinical file path not found, please check the path was specified correctly" + cols['default'])
            gp_clin_file = input('Please specify correct path to GP clinical file: ')
    else:
        gp_clin_file = args.gp_clin_path
    if not args.showcase_path:
        print(cols['orange'] + 'Showcase file path not provided' + cols['default'])
        showcase_file = input('Please specify path to showcase dataset file: ')
        while not os.path.exists(showcase_file):
            print("Showcase file path not found, please check the path was specified correctly")
            showcase_file = input("Please specify correct path to showcase file: ")
    else:
        showcase_file = args.showcase_path
    db.create_sqlite_db(db_file, main_file, gp_clin_file, showcase_file)


if __name__ == "__main__":
    main()
