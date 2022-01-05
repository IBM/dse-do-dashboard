# Copyright IBM All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import List, Dict
from sqlalchemy import Table, Column, String, Integer, Float, ForeignKey, ForeignKeyConstraint
from collections import OrderedDict

from dse_do_utils.scenariodbmanager import ScenarioDbTable, ScenarioDbManager
from dse_do_utils.scenariodbmanager import ScenarioTable, ParameterTable, KpiTable, BusinessKpiTable
# from utils.scenariodbmanager import ScenarioDbTable, ScenarioDbManager
# from utils.scenariodbmanager import ScenarioTable, ParameterTable, KpiTable, BusinessKpiTable

import pandas as pd

from fruit_distribution.scenariodbmanager_update import ScenarioDbManagerUpdate


class ProductMarginTable(ScenarioDbTable):
    def __init__(self, db_table_name: str = 'product_margin', extended_columns_metadata: List[Column] = []):
        columns_metadata = [
            Column('product', String(256), primary_key=True),
            Column('margin', Float(), primary_key=False),
            Column('size', Float(), primary_key=False),
        ]
        columns_metadata.extend(extended_columns_metadata)
        super().__init__(db_table_name, columns_metadata)

class InventoryTable(ScenarioDbTable):
    def __init__(self, db_table_name: str = 'inventory', extended_columns_metadata: List[Column] = []):
        columns_metadata = [
            Column('product', String(256), primary_key=True),
            Column('inventory', Integer(), primary_key=False),
        ]
        constraints_metadata = [
            ForeignKeyConstraint(['product'], ['product_margin.product']),
        ]
        columns_metadata.extend(extended_columns_metadata)
        super().__init__(db_table_name, columns_metadata, constraints_metadata)

class DemandTable(ScenarioDbTable):
    def __init__(self, db_table_name: str = 'demand', extended_columns_metadata: List[Column] = []):
        columns_metadata = [
            Column('product', String(256), primary_key=True),
            Column('customer', String(256), primary_key=True),
            Column('demand', Integer(), primary_key=False),
        ]
        constraints_metadata = [
            ForeignKeyConstraint(['product'], ['product_margin.product']),
        ]
        columns_metadata.extend(extended_columns_metadata)
        super().__init__(db_table_name, columns_metadata, constraints_metadata)
        
class TruckTable(ScenarioDbTable):
    def __init__(self, db_table_name: str = 'truck', extended_columns_metadata: List[Column] = []):
        columns_metadata = [
            Column('truck_model', String(256), primary_key=True),
            Column('truck_capacity', Integer(), primary_key=False),
            Column('truck_cost', Float(), primary_key=False),
            Column('availability', Integer(), primary_key=False),
        ]
        columns_metadata.extend(extended_columns_metadata)
        super().__init__(db_table_name, columns_metadata)
        
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Output Tables
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class DemandOutputTable(ScenarioDbTable):
    def __init__(self, db_table_name: str = 'demand_output', extended_columns_metadata: List[Column] = []):
        columns_metadata = [
            Column('product', String(256), primary_key=True),
            Column('customer', String(256), primary_key=True),
            Column('demand', Integer(), primary_key=False),
            Column('margin', Float(), primary_key=False),
            Column('size', Float(), primary_key=False),
            Column('planned_delivery', Integer(), primary_key=False),
        ]
        constraints_metadata = [
            ForeignKeyConstraint(['product','customer'], ['demand.product', 'demand.customer']),
        ]
        columns_metadata.extend(extended_columns_metadata)
        super().__init__(db_table_name, columns_metadata, constraints_metadata)
        
class CustomerTruckOutputTable(ScenarioDbTable):
    def __init__(self, db_table_name: str = 'customer_truck_output', extended_columns_metadata: List[Column] = []):
        columns_metadata = [
            Column('customer', String(256), primary_key=True),
            Column('truck_model', String(256), primary_key=True),
            Column('truck_capacity', Integer(), primary_key=False),
            Column('truck_cost', Float(), primary_key=False),
            Column('num_trucks', Integer(), primary_key=False),
        ]
        constraints_metadata = [
            ForeignKeyConstraint(['truck_model'], ['truck.truck_model']),
        ]
        columns_metadata.extend(extended_columns_metadata)
        super().__init__(db_table_name, columns_metadata, constraints_metadata)


class FruitScenarioDbManager(ScenarioDbManagerUpdate):
    def __init__(self, input_db_tables: Dict[str, ScenarioDbTable]=None, output_db_tables: Dict[str, ScenarioDbTable]=None, 
                 credentials=None, schema: str = None, echo=False, multi_scenario: bool = True):
        if input_db_tables is None:
            input_db_tables = OrderedDict([
                ('Scenario', ScenarioTable()),
                ('ProductMargin', ProductMarginTable()),
                ('Inventory', InventoryTable()),
                ('Demand', DemandTable()),
                ('Truck', TruckTable()),
                ('Parameter', ParameterTable()),
            ])
        if output_db_tables is None:
            output_db_tables = OrderedDict([
                ('DemandOutput', DemandOutputTable()),
                ('TruckOutput', CustomerTruckOutputTable()),
                ('kpis', KpiTable()),
            ])
        super().__init__(input_db_tables=input_db_tables, output_db_tables=output_db_tables, credentials=credentials, schema=schema, echo=echo, multi_scenario=multi_scenario)