# Creates a schema in the DB
# WARNING: will delete all existing tables
import os

from pharma.pharma_dash_app import PharmaDashApp
from dse_do_dashboard.dash_app import HostEnvironment
from supply_chain.pharma.pharmascenariodbtables import PharmaScenarioDbManager

if 'PROJECT_NAME' in os.environ:  # This works in CP4D v4.0.2
    host_env = HostEnvironment.CPD402  #'CP4D'
    from ibm_watson_studio_lib import access_project_or_space
    wslib = access_project_or_space()
    DB2_credentials = wslib.get_connection("DB2Cloud_DO_Dashboards")
else:
    host_env = HostEnvironment.Local  # 'local'
    from my_secrets.db2wh import DB2Cloud_DO_Dashboards_credentials
    DB2_credentials = DB2Cloud_DO_Dashboards_credentials

scdb = PharmaScenarioDbManager(credentials = DB2_credentials, schema='PHARMA_V1', echo=True)
scdb.create_schema()