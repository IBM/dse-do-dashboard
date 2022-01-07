# Copyright IBM All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import Dict, List, NamedTuple, Any, Optional

import sqlalchemy
from dse_do_utils.scenariodbmanager import ScenarioDbManager, ScenarioDbTable


#########################################
# Added to dse-do-utils v 0.5.3.2b
#########################################
class DbCellUpdate(NamedTuple):
    scenario_name: str
    table_name: str
    row_index: List[Dict[str, Any]]  # e.g. [{'column': 'col1', 'value': 1}, {'column': 'col2', 'value': 'pear'}]
    column_name: str
    current_value: Any
    previous_value: Any  # Not used for DB operation
    row_idx: int  # Not used for DB operation


class ScenarioDbManagerUpdate(ScenarioDbManager):
    """
    To test editable tables. Supports DB updates of edits.
    Changes are added to dse-do-utils v 0.5.3.2b
    """

    def __init__(self, input_db_tables: Dict[str, ScenarioDbTable], output_db_tables: Dict[str, ScenarioDbTable],
                 credentials=None, schema: str = None, echo: bool = False, multi_scenario: bool = True,
                 enable_transactions: bool = True, enable_sqlite_fk: bool = True):
        super().__init__(input_db_tables, output_db_tables, credentials, schema, echo, multi_scenario, enable_transactions, enable_sqlite_fk)


    ############################################################################################
    # Update scenario
    # Added to dse-do-utils v 0.5.3.2b
    ############################################################################################
    def update_cell_changes_in_db(self, db_cell_updates: List[DbCellUpdate]):
        """Update a set of cells in the DB.

        :param db_cell_updates:
        :return:
        """
        if self.enable_transactions:
            print("Update cells with transaction")
            with self.engine.begin() as connection:
                self._update_cell_changes_in_db(db_cell_updates, connection=connection)
        else:
            self._update_cell_changes_in_db(db_cell_updates)

    def _update_cell_changes_in_db(self, db_cell_updates: List[DbCellUpdate], connection=None):
        """Update an ordered list of single value changes (cell) in the DB."""
        for db_cell_change in db_cell_updates:
            self._update_cell_change_in_db(db_cell_change, connection)

    def _update_cell_change_in_db(self, db_cell_update: DbCellUpdate, connection=None):
        """Update a single value (cell) change in the DB."""
        db_table_name = self.db_tables[db_cell_update.table_name].db_table_name
        column_change = f"{db_cell_update.column_name} = '{db_cell_update.current_value}'"
        scenario_condition = f"scenario_name = '{db_cell_update.scenario_name}'"
        pk_conditions = ' AND '.join([f"{pk['column']} = '{pk['value']}'" for pk in db_cell_update.row_index])
        sql = f"UPDATE {db_table_name} SET {column_change} WHERE {pk_conditions} AND {scenario_condition};"
        # print(f"_update_cell_change_in_db = {sql}")
        if connection is None:
            self.engine.execute(sql)
        else:
            connection.execute(sql)

    ############################################################################################
    # Missing CRUD operations on scenarios in DB:
    # - Delete scenario
    # - Duplicate scenario
    # - Rename scenario
    ############################################################################################

    def delete_scenario_from_db(self, scenario_name: str):
        """Delete a scenario. Uses a transaction (when enabled)."""
        if self.enable_transactions:
            print("Delete scenario within a transaction")
            with self.engine.begin() as connection:
                self._delete_scenario_from_db(scenario_name=scenario_name, connection=connection)
        else:
            self._delete_scenario_from_db(scenario_name=scenario_name)

    def duplicate_scenario_in_db(self, source_scenario_name: str, target_scenario_name: str):
        """Duplicate a scenario. Uses a transaction (when enabled)."""
        if self.enable_transactions:
            print("Duplicate scenario within a transaction")
            with self.engine.begin() as connection:
                self._duplicate_scenario_in_db(source_scenario_name, target_scenario_name, connection=connection)
        else:
            self._duplicate_scenario_in_db(source_scenario_name, target_scenario_name)

    def _duplicate_scenario_in_db(self, source_scenario_name: str, target_scenario_name: str = None, connection=None):
        """
        TODO: break _replace_scenario_in_db_transaction into a delete and insert. Then use the insert here.
        :param source_scenario_name:
        :param target_scenario_name:
        :param connection:
        :return:
        """
        if target_scenario_name is None:
            new_scenario_name = self._find_free_duplicate_scenario_name(source_scenario_name)
        elif self._check_free_scenario_name(target_scenario_name):
            new_scenario_name = target_scenario_name
        else:
            raise ValueError(f"Target name for duplicate scenario '{target_scenario_name}' already exists.")

        inputs, outputs = self.read_scenario_from_db(source_scenario_name)
        self._replace_scenario_in_db_transaction(scenario_name=new_scenario_name, inputs=inputs, outputs=outputs,
                                                 bulk=True, connection=connection)

    def _find_free_duplicate_scenario_name(self, scenario_name: str) -> Optional[str]:
        """Finds next free scenario name based on pattern '{scenario_name}_copy_n'.
        Will try at maximum 20 attempts.
        """
        max_num_attempts = 20
        for i in range(1, max_num_attempts + 1):
            new_name = f"{scenario_name}_copy_{i}"
            free = self._check_free_scenario_name(new_name)
            if free:
                return new_name
        raise ValueError(f"Cannot find free name for duplicate scenario. Tried {max_num_attempts}. Last attempt = {new_name}. Rename scenarios.")
        return None

    def _check_free_scenario_name(self, scenario_name) -> bool:
        free = (False if scenario_name in self.get_scenarios_df().index else True)
        return free

    ##############################################
    def rename_scenario_in_db(self, source_scenario_name: str, target_scenario_name: str):
        """Rename a scenario. Uses a transaction (when enabled).
        TODO: get rename in SQL to work. Currently causing Integrity errors due to not being able to defer constraint checking."""
        if self.enable_transactions:
            print("Duplicate scenario within a transaction")
            with self.engine.begin() as connection:
                self._rename_scenario_in_db(source_scenario_name, target_scenario_name, connection=connection)
                # self._rename_scenario_in_db_sql(source_scenario_name, target_scenario_name, connection=connection)
        else:
            self._rename_scenario_in_db(source_scenario_name, target_scenario_name)
            # self._rename_scenario_in_db_sql(source_scenario_name, target_scenario_name)

    def _rename_scenario_in_db(self, source_scenario_name: str, target_scenario_name: str = None, connection=None):
        """
        TODO: do this with SQL. Avoids moving data from and too the DB. More efficient.
        :param source_scenario_name:
        :param target_scenario_name:
        :param connection:
        :return:
        """
        if self._check_free_scenario_name(target_scenario_name):
            new_scenario_name = target_scenario_name
        else:
            raise ValueError(f"Target name for rename scenario '{target_scenario_name}' already exists.")

        # Note that when using a transaction, the order of delete vs insert is irrelevant
        inputs, outputs = self.read_scenario_from_db(source_scenario_name)
        # print(f"KPI columns {outputs['kpis'].columns}")
        outputs['kpis'].columns = outputs['kpis'].columns.str.upper()  # HACK!!! TODO: fix in read_scenario
        self._replace_scenario_in_db_transaction(scenario_name=new_scenario_name, inputs=inputs, outputs=outputs,
                                                 bulk=True, connection=connection)
        self._delete_scenario_from_db(scenario_name=source_scenario_name, connection=connection)

    def _rename_scenario_in_db_sql(self, source_scenario_name: str, target_scenario_name: str = None, connection=None):
        """Do a rename using an SQL UPDATE

        UPDATE table SET scenario_name = 'target_scenario_name' WHERE scenario_name = 'source_scenario_name'

        Bottleneck: causes Integrity errors while updating. Need to defer constraint checking!
        """
        for scenario_table_name, db_table in self.db_tables.items():
            sql = f"UPDATE {db_table.db_table_name} SET scenario_name = '{target_scenario_name}' WHERE scenario_name = '{source_scenario_name}'"
            if connection is None:
                self.engine.execute(sql)
            else:
                connection.execute(sql)
        pass


    def _delete_scenario_from_db(self, scenario_name: str, connection=None):
        """Deletes all rows associated with a given scenario.
        Note that it only deletes rows from tables defined in the self.db_tables, i.e. will NOT delete rows in 'auto-inserted' tables!
        Must do a 'cascading' delete to ensure not violating FK constraints. In reverse order of how they are inserted.
        Also deletes entry in scenario table
        """
        if connection is None:
            insp = sqlalchemy.inspect(self.engine)
        else:
            insp = sqlalchemy.inspect(connection)
        tables_in_db = insp.get_table_names(schema=self.schema)
        for scenario_table_name, db_table in reversed(self.db_tables.items()):
            # if insp.has_table(db_table.db_table_name, schema=self.schema):  # .has_table() only supported in SQLAlchemy 1.4+
            if db_table.db_table_name in tables_in_db:
                sql = f"DELETE FROM {db_table.db_table_name} WHERE scenario_name = '{scenario_name}'"
                if connection is None:
                    self.engine.execute(sql)
                else:
                    connection.execute(sql)

        # Delete scenario entry in scenario table:
        sql = f"DELETE FROM SCENARIO WHERE scenario_name = '{scenario_name}'"
        if connection is None:
            self.engine.execute(sql)
        else:
            connection.execute(sql)

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