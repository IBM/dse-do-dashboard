from abc import ABC, abstractmethod

# from dse_do_dashboard import DoDashApp
from dse_do_utils.deployeddomodel import DeployedDOModel
from dse_do_utils.scenariodbmanager import Inputs, Outputs, ScenarioDbManager
from dse_do_dashboard.utils.donotebookrunner import DoNotebookRunner
from typing import NamedTuple
from typing import Type


class DoModelRunner(ABC):
    """
    TODO: For all model classes, after completion grab run-time, log, solve_status
    """
    def __init__(self, scenario_name: str,
                 dash_app = None,  # DoDashApp, cannot declare due to circular import
                 database_manager_class = None,
                 db_credentials = None,
                 schema: str = None,
                 db_echo: bool = False,
                 ):
        # self.dash_app = dash_app
        self.dash_app = dash_app
        self.database_manager_class = database_manager_class
        self.db_credentials = db_credentials
        self.schema = schema
        self.db_echo = db_echo
        if self.dash_app is None:
            self.dbm = self.create_database_manager_instance()
        else:
            self.dbm = self.dash_app.dbm  # Re-use existing dbm if available:
            self.dash_app.job_queue.append(self)  # TODO: hack to do a job-queue. Be careful with global variables in Dash!
        self.scenario_name = scenario_name
        self.log = ""
        self.code = ""  # Only applies to DoNotebookRunner
        self.run_status: str = "Initializing"
        self.id = 'my id'  # TODO: generate unique ID

    def create_database_manager_instance(self) -> ScenarioDbManager:
        """Create an instance of a ScenarioDbManager.
        The default implementation uses the database_manager_class from the constructor.
        Optionally, override this method."""
        if self.database_manager_class is not None and self.db_credentials is not None:
            print(f"Connecting to DB2 at {self.db_credentials['host']}, schema = {self.schema}")
            dbm = self.database_manager_class(credentials=self.db_credentials, schema=self.schema, echo=self.db_echo)
        else:
            print("Error: either specifiy `database_manager_class`, `db_credentials` and `schema`, or override `create_database_manager_instance`.")
        return dbm

    def run(self):
        """
        1. Load inputs from DB
        2. Run model
        3. Write outputs back to DB
        """
        self.run_status = "Loading input data"
        inputs = self.load_inputs()
        self.run_status = "Running Model"
        outputs = self.run_model(inputs)
        self.run_status = "Saving output data"
        self.update_outputs(outputs)
        self.run_status = "Done"

    def load_inputs(self) -> Inputs:
        return self.dbm.read_scenario_input_tables_from_db(self.scenario_name)

    @abstractmethod
    def run_model(self, inputs: Inputs) -> Outputs:
        """Abstract method"""
        return {}

    def update_outputs(self, outputs: Outputs):
        # print("Update output tables in DB")
        self.dbm.update_scenario_output_tables_in_db(scenario_name=self.scenario_name, outputs=outputs)
        # print("Done update output tables in DB")


class DoNotebookModelRunner(DoModelRunner):
    def __init__(self, scenario_name: str, notebook_filepath: str,
                 my_globals, my_locals,
                 dash_app = None,  # DoDashApp, cannot declare due to circular import
                 database_manager_class = None,
                 db_credentials = None,
                 schema: str = None,
                 db_echo: bool = False,
                 ):
        super().__init__(scenario_name,
                         dash_app=dash_app,
                         database_manager_class=database_manager_class,
                         db_credentials=db_credentials,
                         schema=schema,
                         db_echo=db_echo
                         )
        self.notebook_filepath = notebook_filepath
        self.globals = my_globals
        self.locals = my_locals

    def run_model(self, inputs: Inputs) -> Outputs:
        """TODO"""
        runner = DoNotebookRunner(self.notebook_filepath, self.globals, self.locals)
        outputs = runner.run(inputs)
        self.log = runner.log
        self.code = runner.code
        return outputs

class DoClassModelRunner(DoModelRunner):
    """
    TODO: grab the self.log so we can use this in the UI
    """
    def __init__(self, scenario_name: str, data_manager_class,
                 optimization_engine_class,
                 dash_app = None,  # DoDashApp, cannot declare due to circular import
                 database_manager_class = None,
                 db_credentials = None,
                 schema: str = None,
                 db_echo: bool = False,
                 ):
        super().__init__(scenario_name,
                         dash_app=dash_app,
                         database_manager_class=database_manager_class,
                         db_credentials=db_credentials,
                         schema=schema,
                         db_echo=db_echo
                         )
        self.data_manager_class = data_manager_class
        self.optimization_engine_class = optimization_engine_class

    def run_model(self, inputs: Inputs) -> Outputs:
        """Run an OptimizationEngine class"""
        dm = self.data_manager_class(inputs=inputs)
        engine = self.optimization_engine_class(data_manager=dm)
        outputs = engine.run()
        return outputs


class DoDeployedModelRunner(DoModelRunner):
    def __init__(self, scenario_name: str,
                 wml_credentials,
                 space_name: str, deployment_id: str,
                 dash_app = None,  # DoDashApp, cannot declare due to circular import
                 database_manager_class = None,
                 db_credentials = None,
                 schema: str = None,
                 db_echo: bool = False,
                 ):
        super().__init__(scenario_name=scenario_name,
                         dash_app=dash_app,
                         database_manager_class=database_manager_class,
                         db_credentials=db_credentials,
                         schema=schema,
                         db_echo=db_echo
                         )
        self.wml_credentials = wml_credentials
        self.space_name = space_name
        self.deployment_id = deployment_id

    def run_model(self, inputs: Inputs) -> Outputs:
        """"""
        mdl = DeployedDOModel(self.wml_credentials, space_name=self.space_name, deployment_id=self.deployment_id)
        job_details = mdl.solve(inputs)
        return mdl.outputs


# class DoDbJobRunner():
#     """Runs a DO Model based on a scenario in the DB."""
#     def __init__(self, dbm: ScenarioDbManager, scenario_name: str, model: DoModelRunner):
#         self.dbm = dbm
#         self.scenario_name = scenario_name
#         self.model = model
#
#     def run(self):
#         inputs = self.dbm.read_scenario_input_tables_from_db(self.scenario_name)
#         outputs = self.model.run(inputs)
#         self.dbm.update_scenario_output_tables_in_db(scenario_name=self.scenario_name, outputs=outputs)


class DoModelRunnerConfig(NamedTuple):
    runner_name: str
    runner_id: str
    runner_class: Type[DoModelRunner]