# Copyright IBM All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import os

# from dashboard.my_secrets.db2wh import DB2Cloud_DO_Dashboards_credentials
from fruit_dash_app import FruitDashApp
from dse_do_dashboard.dash_app import HostEnvironment

if 'PROJECT_NAME' in os.environ:  # This works in CP4D v4.0.2
    host_env = HostEnvironment.CPD402  #'CP4D'
    from ibm_watson_studio_lib import access_project_or_space
    wslib = access_project_or_space()
    DB2_credentials = wslib.get_connection("DB2Cloud_DO_Dashboards")
else:
    host_env = HostEnvironment.Local  # 'local'
    from my_secrets.db2wh import DB2Cloud_DO_Dashboards_credentials
    DB2_credentials = DB2Cloud_DO_Dashboards_credentials

DA = FruitDashApp(db_credentials=DB2_credentials, schema='FRUIT_V2', dash_debug=True, host_env=host_env,
                  #                   port=8051,
                  # db_echo=True,
                  )



####################################
if __name__ == '__main__':
    DA.run_server()