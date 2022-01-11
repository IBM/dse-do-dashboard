from typing import Optional, Dict
import pandas as pd

# from supply_chain.water.supply_chain_schema import SCNFO_SCHEMA
# from supply_chain.abbott.abbottdatamanager import AbbottDataManager
from supply_chain.pharma.pharmadatamanager import PharmaDataManager
from utils.dash_common_utils import ScenarioTableSchema
# from supply_chain.water.waterdatamanager import WaterDataManager


class DEPharmaDataManager(PharmaDataManager):
    def __init__(self, inputs=None, outputs=None, table_schema:Dict[str, ScenarioTableSchema]=None):
        super().__init__(inputs, outputs)

        # self.demand_index_columns = ['customerName', 'locationName', 'productName', 'timePeriodSeq']
        # self.production_activities_index_columns = ['productName', 'timePeriodSeq', 'lineName',
        # 'recipeId']  # We'll be using these later on
        # self.table_schema = SCNFO_SCHEMA  # TODO: avoid hard-coding!?
        self.table_schema = table_schema

    ############################################
    # Hack: move to DataManager in dse-do-utils
    ############################################
    def get_raw_table_by_name(self, table_name: str) -> Optional[pd.DataFrame]:
        """Get the 'raw' (non-indexed) table from inputs or outputs."""
        if table_name in self.inputs:
            df = self.inputs[table_name]
        elif table_name in self.outputs:
            df = self.outputs[table_name]
        else:
            df = None
        return df

    def get_table_by_name(self, table_name:str, index:bool=False, expand:bool=False) -> Optional[pd.DataFrame]:
        """Return input or output table by name.

        :param table_name: can be the name of an input or an output table
        :param index: index the DataFrame
        :param expand: join tables from foreign-keys
        :return:
        """
        df = self.get_raw_table_by_name(table_name)
        if df is not None:
            if expand:
                if table_name in self.table_schema:
                    for fkt in self.table_schema[table_name].foreign_tables:
                        foreign_df = self.get_table_by_name(fkt.table_name, expand=True)
                        if foreign_df is not None:
                            df = pd.merge(df, foreign_df, on=fkt.foreign_keys, how='inner')
                        else:
                            print(f"Error: could not find foreign-key table {fkt.table_name}")
            if index:
                if table_name in self.table_schema:
                    df = df.set_index(self.table_schema[table_name].index_columns, verify_integrity=True)
        return df

    def get_table_schema(self, table_name: str) -> Optional[ScenarioTableSchema]:
        table_schema = None
        if self.table_schema is not None and table_name in self.table_schema:
            table_schema = self.table_schema[table_name]
        return table_schema

############################################
# Hack: move to DataManager in dse-do-utils
############################################
# def get_raw_table_by_name(self, table_name):
#     """Get the 'raw' (non-indexed) table from inputs or outputs."""
#     if table_name in self.inputs:
#         df = self.inputs[table_name]
#     elif table_name in self.outputs:
#         df = self.outputs[table_name]
#     else:
#         df = None
#     return df
# DataManager.get_raw_table_by_name = get_raw_table_by_name