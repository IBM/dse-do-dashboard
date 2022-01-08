import os

from pharma.pharma_dash_app import PharmaDashApp
from dse_do_dashboard.dash_app import HostEnvironment
from my_secrets.db2wh import DB2_Pharma_CPD_credentials

if 'PROJECT_NAME' in os.environ:  # This works in CP4D v4.0.2
    host_env = HostEnvironment.CPD402  #'CP4D'
    from ibm_watson_studio_lib import access_project_or_space
    wslib = access_project_or_space()
    DB2_credentials = wslib.get_connection("DB2Cloud_DO_Dashboards")
else:
    host_env = HostEnvironment.Local  # 'local'
    from my_secrets.db2wh import DB2Cloud_DO_Dashboards_credentials
    DB2_credentials = DB2Cloud_DO_Dashboards_credentials

DA = PharmaDashApp(db_credentials = DB2_credentials, schema='PHARMA_V1', dash_debug=True, host_env=host_env,
                   db_echo=True,
                   )



####################################
if __name__ == '__main__':
    DA.run_server()
