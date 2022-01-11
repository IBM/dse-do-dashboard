#######################################################
# Table specific SQL
#######################################################
from typing import List, Dict

# from supply_chain.folium_supply_chain import SCMapManager, MappingSCDM
# from supply_chain.plotly_supply_chain import PlotlyManager, WaterPlotlyManager
from supply_chain.pharma.pharmaplotlymanager import PharmaPlotlyManager
from supply_chain.pharma.depharmadatamanager import DEPharmaDataManager
from supply_chain.scnfo.scnfoplotlymanager import PlotlyManager
from supply_chain.pharma.supply_chain_schema import SCNFO_SCHEMA, SCNFO_PIVOT_CONFIG

from supply_chain.water.watermapmanager import MappingSCDM, SCMapManager  # TODO!!!

# from supply_chain.water.waterplotlymanager import WaterPlotlyManager
# from dse_do_dashboard.visualization_pages.visualization_page import VisualizationPage
from dse_do_dashboard import VisualizationPage
from dse_do_utils.scenariodbmanager import ScenarioDbManager
# from supply_chain.water.dewaterdatamanager import DEWaterDataManager

import pandas as pd

#############################################################################
#  Dash Enterprise
# 
# Note: we're subclassing a specific use-case DbManager
# Issues to resolve:
# * Have to re-define the inputs and outputs tables
# * Redefine generic methods necessary for Dash Enterpise use
# * Probably need to make a container object instead of a sub/super class
#############################################################################
class PharmaDashEnterpriseDbManager():
    """Experimental container object that wraps around a custom ScenarioDbManager.
    Avoids having to subclass a CPD ScenarioDbManager
    Defines some generic methods.
    TODO: avoid hard-coding some class names
    """
    def __init__(self, dbm: ScenarioDbManager, visualization_pages_spec=[]):
        self.dbm = dbm
        self.plotly_manager_class = None
        self.folium_data_manager_class = None
        self.folium_map_manager_class = None
        self.visualization_pages_spec = visualization_pages_spec

    def set_table_read_callback(self, table_read_callback=None):
        # print(f"Set callback to {table_read_callback}")
        # self.table_read_callback = table_read_callback
        # self.dbm.table_read_callback = table_read_callback  # Quick Hack to fix error. TODO: 
        self.dbm.set_table_read_callback(table_read_callback)
    
        #  Convenience method to quickly get a DM from the ScenarioDbManager for
    def get_plotly_manager(self, scenario_name: str, input_table_names: List[str] = None, output_table_names: List[str] = None) -> PlotlyManager:
        """Loads data for selected input and output tables. 
        TODO: avoid hard-coding PlotlySupplyChainDataManager
        """
        inputs, outputs = self.dbm.read_scenario_tables_from_db_cached(scenario_name, input_table_names, output_table_names)
        # dm = DEWaterDataManager(inputs, outputs, table_schema=SCNFO_SCHEMA)
        dm = DEPharmaDataManager(inputs, outputs, table_schema=SCNFO_SCHEMA)
        pm = PharmaPlotlyManager(dm)
        dm.prepare_data_frames()
        return pm

    def get_folium_map_manager(self, scenario_name: str, input_table_names:List[str] = None, output_table_names: List[str] = None) -> SCMapManager:
        """
        TODO: avoid hard-coding MappingSCDM and SCMapManager
        VT: not sure this is actually used
        """
        inputs, outputs = self.dbm.read_scenario_tables_from_db_cached(scenario_name, input_table_names, output_table_names)
        dm = MappingSCDM(inputs=inputs,outputs=outputs)
        dm.prepare_data_frames()
        mm = SCMapManager(data_manager=dm, width='100%', height='100%')  # width/height=None ensures the iFrame drives the width/height and avoids scroll bars.
        return mm

    def get_input_table_names(self) -> List[str]:
        """Return list of valid table names based on self.input_db_tables"""
        names = list(self.dbm.input_db_tables.keys())
        if 'Scenario' in names: names.remove('Scenario')
        return names

    def get_output_table_names(self) -> List[str]:
        """Return list of valid table names based on self.input_db_tables"""
        names = list(self.dbm.output_db_tables.keys())
        return names

    def get_scenarios_df(self):
        return self.dbm.get_scenarios_df()

    def get_pivot_table_config(self, table_name):
        pivot_config = (SCNFO_PIVOT_CONFIG[table_name] if table_name in SCNFO_PIVOT_CONFIG else None)
        return pivot_config

    def get_visualization_pages_dict(self):
        visualization_pages_dict:Dict[str, VisualizationPage] = {vp.page_id:vp for vp in self.visualization_pages_spec}
        return visualization_pages_dict

    def get_visualization_pages_spec(self):
        return self.visualization_pages_spec
