ukbcohort
===============================

version number: 0.1.9
author: Isabell Kiral, Nathalie Willems

Overview
--------

Tool for curation of UK Biobank data to generate cohorts. The tool can filter the main and associated datasets (e.g GP Clinical data) based on search terms provided by the user. It can be used interactively through a command line interface, or imported as a module and integrated into a broader pipeline. Additional functionality, such as automatically downloading large data files (bulk data) is also supported.

Installation / Usage
--------------------

Installing using pip (or pip3):

    $ pip3 install  git+ssh://git@github.ibm.com/isabeki/ukbcohort.git

Installing using pip (pip3) from particular branch

    $ pip3 install git+ssh://git@github.ibm.com/isabeki/ukbcohort.git@branchname


Or clone the repo:

    $ git clone https://github.com/isa_kiko/ukbcohort.git
    $ python setup.py install


In order to make full use of this module, you will need to download the following files:
* `main_dataset.csv`: The main dataset as downloaded from UK Biobank.
* `showcase.csv` and `codings.csv`: Files that can be found [in this repo](https://github.ibm.com/aur-genomics/modellingScripts/blob/master/isabell/ukbcohort/dataFiles) in their current version. A function is provided to download potentially updated files from the UKBB server. These files contain descriptions of columns in the main dataset as well as associated codes.
* `readcodes.csv`: A file linking readcodes to descriptions for the 'gp_clinical' table in the UKBB data portal. This file can be found [here](https://github.ibm.com/aur-genomics/modellingScripts/blob/master/isabell/ukbcohort/dataFiles).
<!-- * [`lookupCodeDescriptions.csv`](https://github.ibm.com/aur-genomics/modellingScripts/blob/master/isabell/cohortPipeline/lookupCodeDescriptions.csv): A file that maps descriptions to codes for the following formats: ICD9, ICD10, read_2, read_3.
* [`coding19.tsv`](https://github.ibm.com/aur-genomics/modellingScripts/blob/master/isabell/cohortPipeline/coding19.tsv): A file that maps the `node_id`s from the main dataset to ICD10 codes.    -->

### Enabling UKBB direct access to Primay Care databases using Chrome (Mac/Linux) or Firefox (Linux)
For Chrome:
<!--1. download [canary](https://www.google.com/chrome/canary/) -->
1. download [driver](https://chromedriver.storage.googleapis.com/index.html?path=83.0.4103.14/)
2. unzip downloaded file
3. add the directory to the path (`export PATH=$PATH:<pathToInstallation>`)
4. execute driver once to make sure your computer trust the distributor (on mac: right click, open, trust developer. double click won't work)
5. during installation, a credentials.py file will be created if it doens't exist already. Enter correct credentials (application ID, user name, and password) to access UKBB or use file as a template to create your own in the location of choice.
For Firefox:
1. download [driver](https://github.com/mozilla/geckodriver/releases)
2. unzip downloaded file
3. add the directory to the path (`export PATH=$PATH:<pathToInstallation>`)
4. during installation, a credentials.py file will be created if it doens't exist already. Enter correct credentials (application ID, user name, and password) to access UKBB or use file as a template to create your own in the location of choice.


Contributing
------------

As a collaborator, please make a branch and create a pull request when ready.
To contribute otherwise, please fork directory and create pull requests.

Example
-------

Example code can be found in this [demo notebook](https://github.ibm.com/isabeki/ukbcohort/blob/master/examples/example.ipynb).
