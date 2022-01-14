# How to setup the tests.

## Environment
The assumption is that this project has been cloned to your workstation.

If using PyCharm:
1. Open the project
2. Create a new virtual environment based on Python 3.8 (to be compatible with the current version of Python in CPD 4.0.4)
3. Install the requirements
4. Add the `test` folder as a source folder (see https://www.jetbrains.com/help/pycharm/configuring-project-structure.html)
5. Add folders `dse-do-dashboard/test/pharma/my_secrets` and `dse-do-dashboard/test/truit_distribution/my_secrets`. 
These folders are NOT (and should NOT! be) synched with git.
6. In the `my_secrets` add a Python file `db2wh.py` that contains the credentials to a DB2 database.
