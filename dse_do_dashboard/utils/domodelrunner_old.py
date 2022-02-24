from abc import ABC, abstractmethod
from dse_do_utils.scenariodbmanager import Inputs, Outputs, ScenarioDbManager


class DoModelRunner(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def run(self, inputs: Inputs) -> Outputs:
        """Abstract method"""
        return {}


class DoNotebookRunner(DoModelRunner):
    def __init__(self, notebook_filepath: str):
        super().__init__()
        self.notebook_filepath = notebook_filepath

    def run(self, inputs: Inputs) -> Outputs:
        """TODO"""
        return {}


class DoDeployRunner(DoModelRunner):
    def __init__(self):
        super().__init__()

    def run(self, inputs: Inputs) -> Outputs:
        """TODO"""
        return {}


class DoDbJobRunner():
    """Runs a DO Model based on a scenario in the DB."""
    def __init__(self, dbm: ScenarioDbManager, scenario_name: str, model: DoModelRunner):
        self.dbm = dbm
        self.scenario_name = scenario_name
        self.model = model

    def run(self):
        inputs = self.dbm.read_scenario_input_tables_from_db(self.scenario_name)
        outputs = self.model.run(inputs)
        self.dbm.update_scenario_output_tables_in_db(scenario_name=self.scenario_name, outputs=outputs)