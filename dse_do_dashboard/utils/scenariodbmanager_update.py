# Copyright IBM All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
from multiprocessing.pool import ThreadPool
from typing import Dict, List, NamedTuple, Any, Optional

import pandas as pd
import sqlalchemy
from dse_do_utils.scenariodbmanager import ScenarioDbManager, ScenarioDbTable, DbCellUpdate

#  Typing aliases
Inputs = Dict[str, pd.DataFrame]
Outputs = Dict[str, pd.DataFrame]

#########################################
# Added to dse-do-utils v 0.5.3.2b
#########################################
# class DbCellUpdate(NamedTuple):
#     scenario_name: str
#     table_name: str
#     row_index: List[Dict[str, Any]]  # e.g. [{'column': 'col1', 'value': 1}, {'column': 'col2', 'value': 'pear'}]
#     column_name: str
#     current_value: Any
#     previous_value: Any  # Not used for DB operation
#     row_idx: int  # Not used for DB operation


class ScenarioDbManagerUpdate(ScenarioDbManager):
    """
    DEPRECATED - was used to develop DB features that are now migrated to dse-do-utils
    To test editable tables. Supports DB updates of edits.
    Supports CRUD operations on scenarios.
    Changes are added to dse-do-utils v 0.5.4.0b
    """

    def __init__(self, input_db_tables: Dict[str, ScenarioDbTable], output_db_tables: Dict[str, ScenarioDbTable],
                 credentials=None, schema: str = None, echo: bool = False, multi_scenario: bool = True,
                 enable_transactions: bool = True, enable_sqlite_fk: bool = True):
        super().__init__(input_db_tables, output_db_tables, credentials, schema, echo, multi_scenario, enable_transactions, enable_sqlite_fk)


    ############################################################################################
    # Update scenario
    # Added to dse-do-utils v 0.5.3.2b
    ############################################################################################
    # def update_cell_changes_in_db(self, db_cell_updates: List[DbCellUpdate]):
    #     """Update a set of cells in the DB.
    #
    #     :param db_cell_updates:
    #     :return:
    #     """
    #     if self.enable_transactions:
    #         print("Update cells with transaction")
    #         with self.engine.begin() as connection:
    #             self._update_cell_changes_in_db(db_cell_updates, connection=connection)
    #     else:
    #         self._update_cell_changes_in_db(db_cell_updates, connection=self.engine)

    # def _update_cell_changes_in_db(self, db_cell_updates: List[DbCellUpdate], connection):
    #     """Update an ordered list of single value changes (cell) in the DB."""
    #     for db_cell_change in db_cell_updates:
    #         self._update_cell_change_in_db(db_cell_change, connection)

    # def _update_cell_change_in_db(self, db_cell_update: DbCellUpdate, connection):
    #     """Update a single value (cell) change in the DB."""
    #     # db_table_name = self.db_tables[db_cell_update.table_name].db_table_name
    #     # column_change = f"{db_cell_update.column_name} = '{db_cell_update.current_value}'"
    #     # scenario_condition = f"scenario_name = '{db_cell_update.scenario_name}'"
    #     # pk_conditions = ' AND '.join([f"{pk['column']} = '{pk['value']}'" for pk in db_cell_update.row_index])
    #     # old_sql = f"UPDATE {db_table_name} SET {column_change} WHERE {pk_conditions} AND {scenario_condition};"
    #
    #     db_table: ScenarioDbTable = self.db_tables[db_cell_update.table_name]
    #     t: sqlalchemy.Table = db_table.get_sa_table()
    #     pk_conditions = [(db_table.get_sa_column(pk['column']) == pk['value']) for pk in db_cell_update.row_index]
    #     target_col: sqlalchemy.Column = db_table.get_sa_column(db_cell_update.column_name)
    #     sql = t.update().where(sqlalchemy.and_((t.c.scenario_name == db_cell_update.scenario_name), *pk_conditions)).values({target_col:db_cell_update.current_value})
    #     # print(f"_update_cell_change_in_db = {sql}")
    #
    #     connection.execute(sql)

    ############################################################################################
    # Missing CRUD operations on scenarios in DB:
    # - Delete scenario
    # - Duplicate scenario
    # - Rename scenario
    ############################################################################################
    # Migrated 2022-01-10
    # def delete_scenario_from_db(self, scenario_name: str):
    #     """Delete a scenario. Uses a transaction (when enabled)."""
    #     if self.enable_transactions:
    #         print("Delete scenario within a transaction")
    #         with self.engine.begin() as connection:
    #             self._delete_scenario_from_db(scenario_name=scenario_name, connection=connection)
    #     else:
    #         self._delete_scenario_from_db(scenario_name=scenario_name, connection=self.engine)

    # def duplicate_scenario_in_db(self, source_scenario_name: str, target_scenario_name: str):
    #     """Duplicate a scenario. Uses a transaction (when enabled)."""
    #     if self.enable_transactions:
    #         print("Duplicate scenario within a transaction")
    #         with self.engine.begin() as connection:
    #             self._duplicate_scenario_in_db(connection, source_scenario_name, target_scenario_name)
    #     else:
    #         self._duplicate_scenario_in_db(self.engine, source_scenario_name, target_scenario_name)
    #
    # def _duplicate_scenario_in_db(self, connection, source_scenario_name: str, target_scenario_name: str = None):
    #     """Is fully done in DB using SQL in one SQL execute statement
    #     :param source_scenario_name:
    #     :param target_scenario_name:
    #     :param connection:
    #     :return:
    #     """
    #     if target_scenario_name is None:
    #         new_scenario_name = self._find_free_duplicate_scenario_name(source_scenario_name)
    #     elif self._check_free_scenario_name(target_scenario_name):
    #         new_scenario_name = target_scenario_name
    #     else:
    #         raise ValueError(f"Target name for duplicate scenario '{target_scenario_name}' already exists.")
    #
    #     # inputs, outputs = self.read_scenario_from_db(source_scenario_name)
    #     # self._replace_scenario_in_db_transaction(scenario_name=new_scenario_name, inputs=inputs, outputs=outputs,
    #     #                                          bulk=True, connection=connection)
    #     self._duplicate_scenario_in_db_sql(connection, source_scenario_name, new_scenario_name)
    #
    # def _duplicate_scenario_in_db_sql(self, connection, source_scenario_name: str, target_scenario_name: str = None):
    #     """
    #     :param source_scenario_name:
    #     :param target_scenario_name:
    #     :param connection:
    #     :return:
    #
    #     See https://stackoverflow.com/questions/9879830/select-modify-and-insert-into-the-same-table
    #
    #     Problem: the table Parameter/parameters has a column 'value' (lower-case).
    #     Almost all of the column names in the DFs are lower-case, as are the column names in the ScenarioDbTable.
    #     Typically, the DB schema converts that the upper-case column names in the DB.
    #     But probably because 'VALUE' is a reserved word, it does NOT do this for 'value'. But that means in order to refer to this column in SQL,
    #     one needs to put "value" between double quotes.
    #     Problem is that you CANNOT do that for other columns, since these are in upper-case in the DB.
    #     Note that the kpis table uses upper case 'VALUE' and that seems to work fine
    #
    #     Resolution: use SQLAlchemy to construct the SQL. Do NOT create SQL expressions by text manipulation.
    #     SQLAlchemy has the smarts to properly deal with these complex names.
    #     """
    #     if target_scenario_name is None:
    #         new_scenario_name = self._find_free_duplicate_scenario_name(source_scenario_name)
    #     elif self._check_free_scenario_name(target_scenario_name):
    #         new_scenario_name = target_scenario_name
    #     else:
    #         raise ValueError(f"Target name for duplicate scenario '{target_scenario_name}' already exists.")
    #
    #     batch_sql=False  # BEWARE: batch = True does NOT work!
    #     sql_statements = []
    #
    #     # 1. Insert scenario in scenario table
    #     # sql_insert = f"INSERT INTO SCENARIO (scenario_name) VALUES ('{new_scenario_name}')"  # Old
    #     # sa_scenario_table = list(self.input_db_tables.values())[0].table_metadata  # Scenario table must be the first
    #     sa_scenario_table = list(self.input_db_tables.values())[0].get_sa_table()  # Scenario table must be the first
    #     sql_insert = sa_scenario_table.insert().values(scenario_name = new_scenario_name)
    #     # print(f"_duplicate_scenario_in_db_sql - Insert SQL = {sql_insert}")
    #     if batch_sql:
    #         sql_statements.append(sql_insert)
    #     else:
    #         connection.execute(sql_insert)
    #
    #     # 2. Do 'insert into select' to duplicate rows in each table
    #     for scenario_table_name, db_table in self.db_tables.items():
    #         if scenario_table_name == 'Scenario':
    #             continue
    #         # else:
    #         #     table_column_names = db_table.get_df_column_names()
    #
    #         # print(f"#####TABLE METADATA: {type(db_table.table_metadata)}")
    #         # print(t1.insert().from_select(['a', 'b'], t2.select().where(t2.c.y == 5)))
    #
    #         # print(f"Columns for {scenario_table_name}: {table_column_names}")
    #         # target_column_names = table_column_names.copy()
    #         # # target_column_names = [f"{db_table.db_table_name}.{n}" for n in target_column_names]
    #         # target_columns_txt = ','.join(target_column_names)
    #         # # target_columns_txt = ','.join([f'"{n}"' for n in target_column_names])
    #         # source_column_names = table_column_names.copy()
    #         # source_column_names[0] = f"'{target_scenario_name}'"
    #         # # source_columns_txt = ','.join(source_column_names)
    #         #
    #         # # other_source_column_names =  table_column_names.copy()[1:]  # Drop the scenario_name column
    #         # # other_source_column_names = [f"{db_table.db_table_name}.{n}" for n in other_source_column_names]
    #         # other_source_columns_txt = ','.join(other_source_column_names)
    #         # # source_columns = ','.join(f'"{n}"' for n in source_column_names[1:])
    #         # # source_columns_txt = f"'{target_scenario_name}', {source_columns}"
    #
    #         t: sqlalchemy.table = db_table.table_metadata  # The table at hand
    #         s: sqlalchemy.table = sa_scenario_table  # The scenario table
    #         # print("+++++++++++SQLAlchemy insert-select")
    #         select_columns = [s.c.scenario_name if c.name == 'scenario_name' else c for c in t.columns]  # Replace the t.c.scenario_name with s.c.scenario_name, so we get the new value
    #         # print(f"select columns = {select_columns}")
    #         select_sql = (sqlalchemy.select(select_columns)
    #                       .where(sqlalchemy.and_(t.c.scenario_name == source_scenario_name, s.c.scenario_name == target_scenario_name)))
    #         target_columns = [c for c in t.columns]
    #         sql_insert = t.insert().from_select(target_columns, select_sql)
    #         # print(f"sql_insert = {sql_insert}")
    #
    #         # sql_insert = f"INSERT INTO {db_table.db_table_name} ({target_columns_txt}) SELECT '{target_scenario_name}',{other_source_columns_txt} FROM {db_table.db_table_name} WHERE scenario_name = '{source_scenario_name}'"
    #         if batch_sql:
    #             sql_statements.append(sql_insert)
    #         else:
    #             connection.execute(sql_insert)
    #     if batch_sql:
    #         batch_sql = ";\n".join(sql_statements)
    #         print(batch_sql)
    #         connection.execute(batch_sql)
    #
    #
    # def _find_free_duplicate_scenario_name(self, scenario_name: str, scenarios_df=None) -> Optional[str]:
    #     """Finds next free scenario name based on pattern '{scenario_name}_copy_n'.
    #     Will try at maximum 20 attempts.
    #     """
    #     max_num_attempts = 20
    #     for i in range(1, max_num_attempts + 1):
    #         new_name = f"{scenario_name}({i})"
    #         free = self._check_free_scenario_name(new_name, scenarios_df)
    #         if free:
    #             return new_name
    #     raise ValueError(f"Cannot find free name for duplicate scenario. Tried {max_num_attempts}. Last attempt = {new_name}. Rename scenarios.")
    #     return None
    #
    # def _check_free_scenario_name(self, scenario_name, scenarios_df=None) -> bool:
    #     if scenarios_df is None:
    #         scenarios_df = self.get_scenarios_df()
    #     free = (False if scenario_name in scenarios_df.index else True)
    #     return free
    #
    # ##############################################
    # def rename_scenario_in_db(self, source_scenario_name: str, target_scenario_name: str):
    #     """Rename a scenario. Uses a transaction (when enabled).
    #     TODO: get rename in SQL to work. Currently causing Integrity errors due to not being able to defer constraint checking."""
    #     if self.enable_transactions:
    #         print("Rename scenario within a transaction")
    #         with self.engine.begin() as connection:
    #             # self._rename_scenario_in_db(source_scenario_name, target_scenario_name, connection=connection)
    #             self._rename_scenario_in_db_sql(connection, source_scenario_name, target_scenario_name)
    #     else:
    #         # self._rename_scenario_in_db(source_scenario_name, target_scenario_name)
    #         self._rename_scenario_in_db_sql(self.engine, source_scenario_name, target_scenario_name)
    #
    # # def _rename_scenario_in_db(self, source_scenario_name: str, target_scenario_name: str = None, connection=None):
    # #     """DEPRECATED: use _rename_scenario_in_db_sql: more efficient. Avoids moving data back and forth
    # #     TODO: do this with SQL. Avoids moving data from and too the DB. More efficient.
    # #     :param source_scenario_name:
    # #     :param target_scenario_name:
    # #     :param connection:
    # #     :return:
    # #     """
    # #     if self._check_free_scenario_name(target_scenario_name):
    # #         new_scenario_name = target_scenario_name
    # #     else:
    # #         raise ValueError(f"Target name for rename scenario '{target_scenario_name}' already exists.")
    # #
    # #     # Note that when using a transaction, the order of delete vs insert is irrelevant
    # #     inputs, outputs = self.read_scenario_from_db(source_scenario_name)
    # #     # print(f"KPI columns {outputs['kpis'].columns}")
    # #     outputs['kpis'].columns = outputs['kpis'].columns.str.upper()  # HACK!!! TODO: fix in read_scenario
    # #     self._replace_scenario_in_db_transaction(scenario_name=new_scenario_name, inputs=inputs, outputs=outputs,
    # #                                              bulk=True, connection=connection)
    # #     self._delete_scenario_from_db(scenario_name=source_scenario_name, connection=connection)
    #
    # def _rename_scenario_in_db_sql(self, connection, source_scenario_name: str, target_scenario_name: str = None):
    #     """Rename scenario.
    #     Uses 2 steps:
    #     1. Duplicate scenario
    #     2. Delete source scenario.
    #
    #     Problem is that we use scenario_name as a primary key. You should not change the value of primary keys in a DB.
    #     Instead, first copy the data using a new scenario_name, i.e. duplicate a scenario. Next, delete the original scenario.
    #
    #     Long-term solution: use a scenario_seq sequence key as the PK. With scenario_name as a ordinary column in the scenario table.
    #
    #     Old:
    #     Do a rename using an SQL UPDATE
    #     `UPDATE table SET scenario_name = 'target_scenario_name' WHERE scenario_name = 'source_scenario_name'`
    #     Bottleneck: causes Integrity errors while updating. Need to defer constraint checking!
    #
    #     Work-around 1:
    #     Group all sql UPDATE statements in one sql statement.
    #     -> No exception, but doesn't seem to do anything!
    #     This is anyway NOT a good way
    #     See https://stackoverflow.com/questions/2499246/how-to-update-primary-key
    #     Apparently, we still need to first insert new rows (cascading!), then delete the old rows
    #
    #     Use of 'insert into select': https://stackoverflow.com/questions/9879830/select-modify-and-insert-into-the-same-table
    #     """
    #     # sql_statements = []
    #     # for scenario_table_name, db_table in self.db_tables.items():
    #     #     sql_update = f"UPDATE {db_table.db_table_name} SET SCENARIO_NAME = '{target_scenario_name}' WHERE SCENARIO_NAME = '{source_scenario_name}';"
    #     #     sql_statements.append(sql_update)
    #     # sql = "\n".join(sql_statements)
    #     # print(sql)
    #     # if connection is None:
    #     #     self.engine.execute(sql)
    #     # else:
    #     #     connection.execute(sql)
    #
    #     # 1. Duplicate scenario
    #     self._duplicate_scenario_in_db_sql(connection, source_scenario_name, target_scenario_name)
    #     # 2. Delete scenario
    #     self._delete_scenario_from_db(source_scenario_name, connection=connection)


    # def _delete_scenario_from_db(self, scenario_name: str, connection):
    #     """Deletes all rows associated with a given scenario.
    #     Note that it only deletes rows from tables defined in the self.db_tables, i.e. will NOT delete rows in 'auto-inserted' tables!
    #     Must do a 'cascading' delete to ensure not violating FK constraints. In reverse order of how they are inserted.
    #     Also deletes entry in scenario table
    #     Uses SQLAlchemy syntax to generate SQL
    #     TODO: batch all sql statements in single execute. Faster? And will that do the defer integrity checks?
    #     """
    #     batch_sql=False
    #     insp = sqlalchemy.inspect(connection)
    #     tables_in_db = insp.get_table_names(schema=self.schema)
    #     sql_statements = []
    #     for scenario_table_name, db_table in reversed(self.db_tables.items()):  # Note this INCLUDES the SCENARIO table!
    #         if db_table.db_table_name in tables_in_db:
    #             # sql = f"DELETE FROM {db_table.db_table_name} WHERE scenario_name = '{scenario_name}'"  # Old
    #             t = db_table.table_metadata  # A Table()
    #             sql = t.delete().where(t.c.scenario_name == scenario_name)
    #             if batch_sql:
    #                 sql_statements.append(sql)
    #             else:
    #                 connection.execute(sql)
    #
    #     # Because the scenario table has already been included in above loop, no need to do separately
    #     # Delete scenario entry in scenario table:
    #     # sql = f"DELETE FROM SCENARIO WHERE scenario_name = '{scenario_name}'"
    #     # sql_statements.append(sql)
    #     if batch_sql:
    #         batch_sql = ";\n".join(sql_statements)
    #         print(batch_sql)
    #         connection.execute(batch_sql)

        #############################################################################
        # for scenario_table_name, db_table in reversed(self.db_tables.items()):
        #     # if insp.has_table(db_table.db_table_name, schema=self.schema):  # .has_table() only supported in SQLAlchemy 1.4+
        #     if db_table.db_table_name in tables_in_db:
        #         sql = f"DELETE FROM {db_table.db_table_name} WHERE scenario_name = '{scenario_name}'"
        #         if connection is None:
        #             self.engine.execute(sql)
        #         else:
        #             connection.execute(sql)
        #
        # # Delete scenario entry in scenario table:
        # sql = f"DELETE FROM SCENARIO WHERE scenario_name = '{scenario_name}'"
        # if connection is None:
        #     self.engine.execute(sql)
        # else:
        #     connection.execute(sql)
        #############################################################################
        # if connection is None:
        #     insp = sqlalchemy.inspect(self.engine)
        #     print(f"inspector no transaction = {type(insp)}")
        #     tables_in_db = insp.get_table_names(schema=self.schema)
        #     print(tables_in_db)
        #     for scenario_table_name, db_table in reversed(self.db_tables.items()):
        #         if insp.has_table(db_table.db_table_name, schema=self.schema):
        #         if insp.has_table(db_table.db_table_name, schema=self.schema):
        #             sql = f"DELETE FROM {db_table.db_table_name} WHERE scenario_name = '{scenario_name}'"
        #             self.engine.execute(sql)
        #
        #     # Delete scenario entry in scenario table:
        #     sql = f"DELETE FROM SCENARIO WHERE scenario_name = '{scenario_name}'"
        #     self.engine.execute(sql)
        # else:
        #     insp = sqlalchemy.inspect(connection)
        #     print(f"inspector with transaction= {type(insp)}")
        #     print(insp.get_table_names(schema=self.schema))
        #     for scenario_table_name, db_table in reversed(self.db_tables.items()):
        #         if insp.has_table(db_table.db_table_name, schema=self.schema):
        #             sql = f"DELETE FROM {db_table.db_table_name} WHERE scenario_name = '{scenario_name}'"
        #             connection.execute(sql)
        #
        #     # Delete scenario entry in scenario table:
        #     sql = f"DELETE FROM SCENARIO WHERE scenario_name = '{scenario_name}'"
        #     connection.execute(sql)
    #############################################
    # Migrated VT 2022-01-09:
    # def read_scenario_from_db(self, scenario_name: str, multi_threaded: bool = False) -> (Inputs, Outputs):
    #     """Single scenario load.
    #     Main API to read a complete scenario.
    #     Reads all tables for a single scenario.
    #     Returns all tables in one dict
    #
    #     Fixed: omit reading scenario table as an input.
    #     """
    #     print(f"read_scenario_from_db.multi_threaded = {multi_threaded}")
    #     if multi_threaded:
    #         inputs, outputs = self._read_scenario_from_db_multi_threaded(scenario_name)
    #     else:
    #         if self.enable_transactions:
    #             with self.engine.begin() as connection:
    #                 inputs, outputs = self._read_scenario_from_db(scenario_name, connection)
    #         else:
    #             inputs, outputs = self._read_scenario_from_db(scenario_name, self.engine)
    #     return inputs, outputs

    # Migrated VT 2022-01-09:
    # def _read_scenario_from_db_multi_threaded(self, scenario_name) -> (Inputs, Outputs):
    #     """Reads all tables from a scenario using multi-threading"""
    #     class ReadTableFunction(object):
    #         def __init__(self, dbm):
    #             self.dbm = dbm
    #         def __call__(self, scenario_table_name, db_table):
    #             return self._read_scenario_db_table_from_db_thread(scenario_table_name, db_table)
    #         def _read_scenario_db_table_from_db_thread(self, scenario_table_name, db_table):
    #             with self.dbm.engine.begin() as connection:
    #                 df = self.dbm._read_scenario_db_table_from_db(scenario_name, db_table, connection)
    #                 dict = {scenario_table_name: df}
    #             return dict
    #
    #     thread_number = 8
    #     pool = ThreadPool(thread_number)
    #     thread_worker = ReadTableFunction(self)
    #     print("ThreadPool created")
    #     # input_tables = [(scenario_table_name, db_table) for scenario_table_name, db_table in self.input_db_tables.items()]
    #     # input_results = pool.starmap(thread_worker, input_tables)  # Returns a list of Dict: [{scenario_table_name: df}]
    #     # inputs = {k:v for element in input_results for k,v in element.items()}  # Convert list of Dict to one Dict.
    #     # # print(inputs)
    #     # output_tables = [(scenario_table_name, db_table) for scenario_table_name, db_table in self.output_db_tables.items()]
    #     # output_results = pool.starmap(thread_worker, output_tables)
    #     # outputs = {k:v for element in output_results for k,v in element.items()}
    #
    #     all_tables = [(scenario_table_name, db_table) for scenario_table_name, db_table in self.db_tables.items() if scenario_table_name != 'Scenario']
    #     # print(all_tables)
    #     all_results = pool.starmap(thread_worker, all_tables)
    #     inputs = {k:v for element in all_results for k,v in element.items() if k in self.input_db_tables.keys()}
    #     outputs = {k:v for element in all_results for k,v in element.items() if k in self.output_db_tables.keys()}
    #
    #     print("All tables loaded")
    #
    #     return inputs, outputs


    # Migrated VT 2022-01-09:
    # def _read_scenario_from_db(self, scenario_name: str, connection) -> (Inputs, Outputs):
    #     """Single scenario load.
    #     Main API to read a complete scenario.
    #     Reads all tables for a single scenario.
    #     Returns all tables in one dict
    #     """
    #     inputs = {}
    #     for scenario_table_name, db_table in self.input_db_tables.items():
    #         # print(f"scenario_table_name = {scenario_table_name}")
    #         if scenario_table_name != 'Scenario':  # Skip the Scenario table as an input
    #             inputs[scenario_table_name] = self._read_scenario_db_table_from_db(scenario_name, db_table, connection=connection)
    #
    #     outputs = {}
    #     for scenario_table_name, db_table in self.output_db_tables.items():
    #         outputs[scenario_table_name] = self._read_scenario_db_table_from_db(scenario_name, db_table, connection=connection)
    #         # if scenario_table_name == 'kpis':
    #         #     # print(f"kpis table columns = {outputs[scenario_table_name].columns}")
    #         #     outputs[scenario_table_name] = outputs[scenario_table_name].rename(columns={'name': 'NAME'})  #HACK!!!!!
    #     return inputs, outputs

    # Migrated VT 2022-01-09:
    # def _read_scenario_db_table_from_db(self, scenario_name: str, db_table: ScenarioDbTable, connection) -> pd.DataFrame:
    #     """Read one table from the DB.
    #     Removes the `scenario_name` column.
    #
    #     Modification: based on SQLAlchemy syntax. If doing the plain text SQL, then some column names not properly extracted
    #     """
    #     db_table_name = db_table.db_table_name
    #     # sql = f"SELECT * FROM {db_table_name} WHERE scenario_name = '{scenario_name}'"  # Old
    #     # db_table.table_metadata is a Table()
    #     t = db_table.table_metadata
    #     sql = t.select().where(t.c.scenario_name == scenario_name)  # This is NOT a simple string!
    #     # print(f"_read_scenario_db_table_from_db SQL = {sql}")
    #     # df = pd.read_sql(sql, con=self.engine)
    #     df = pd.read_sql(sql, con=connection)
    #     if db_table_name != 'scenario':
    #         df = df.drop(columns=['scenario_name'])
    #
    #     return df
