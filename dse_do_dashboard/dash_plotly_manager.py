from typing import Optional, TypeVar, Dict

import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from dse_do_utils import DataManager
from dse_do_utils.plotlymanager import PlotlyManager

DM = TypeVar('DM', bound='DataManager')


class DashPlotlyManager(PlotlyManager[DM]):

    def __init__(self, dm: DM):
        super().__init__(dm)

        self.ref_dm: Optional[DataManager]
        self.ms_inputs: Optional[Dict[str, pd.DataFrame]]
        self.ms_outputs: Optional[Dict[str, pd.DataFrame]]

    def plotly_kpi_compare_bar_charts(self, figs_per_row: int = 3, orientation: str = 'v') -> [[go.Figure]]:
        """
        Generalized compare of KPIs between scenarios. Creates a list-of-list of go.Figure, i.e. rows of figures,
        for the PlotlyRowsVisualizationPage.
        Each KPI gets its own bar-chart, comparing the scenarios.

        Supports 3 cases:
            1. Multi-scenario compare based on the Reference Scenarios multi-checkbox select on the Home page.
            2. Compare the current select scenario with the Reference Scenario selected on the Home page.
            3. Single scenario view based on the currently selected scenario

        Args:
            figs_per_row: int - Maximum number of figures per row
            orientation: str - `h' (horizontal) or `v` (vertical)

        Returns:
            figures in rows ([[go.Figure]]) - bar-charts in rows
        """
        # df = self.dm.kpis.reset_index()

        figs = []
        if self.get_multi_scenario_compare_selected():
            df = self.get_multi_scenario_table('kpis')
        elif self.get_reference_scenario_compare_selected():
            ref_df = self.ref_dm.kpis.reset_index()
            ref_df['scenario_name'] = 'Reference'
            selected_df = self.dm.kpis.reset_index()
            selected_df['scenario_name'] = 'Current'
            df = pd.concat([selected_df, ref_df])
        else:
            df = self.dm.kpis.reset_index()
            df['scenario_name'] = 'Current'

        for kpi_name, group in df.groupby('NAME'):
            labels = {'scenario_name': 'Scenario', 'VALUE': kpi_name}
            title = f'{kpi_name}'
            if orientation == 'v':
                fig = px.bar(group, x='scenario_name', y='VALUE', orientation='v', color='scenario_name', labels=labels,
                             title=title)
            else:
                fig = px.bar(group, y='scenario_name', x='VALUE', orientation='h', color='scenario_name',
                             labels=labels)
            fig.update_layout(xaxis_title=None)
            fig.update_layout(yaxis_title=None)
            fig.update_layout(showlegend=False)
            figs.append(fig)

        # Split list of figures in list-of-lists with maximum size of n:
        n = figs_per_row
        figs = [figs[i:i + n] for i in range(0, len(figs), n)]
        return figs

    def get_multi_scenario_compare_selected(self) -> bool:
        """Returns True if the user has selected multi-scenario compare
        TODO: migrate to dse-do-dashboard (or to some new class in the dse-do-dashboard?)
        """
        ms_enabled = (isinstance(self.ms_outputs, dict)
                      and isinstance(self.ms_inputs, dict)
                      and 'Scenario' in self.ms_inputs.keys()
                      and self.ms_inputs['Scenario'].shape[0] > 0
                      )
        return ms_enabled

    def get_multi_scenario_table(self, table_name: str) -> Optional[pd.DataFrame]:
        """Gets the df from the table named `table_name` in either inputs or outputs.
        Merges the Scenario table, so it has the scenario_name as column.
        DataFrame is NOT indexed!
        TODO: migrate to dse-do-dashboard (or to some new class in the dse-do-dashboard?)
        """
        if table_name in self.ms_inputs.keys():
            df = self.ms_inputs[table_name]
        elif table_name in self.ms_outputs.keys():
            df = self.ms_outputs[table_name]
        else:
            df = None

        if df is not None:
            df = df.merge(self.ms_inputs['Scenario'], on='scenario_seq')

        return df

    def get_reference_scenario_compare_selected(self) -> bool:
        """Returns True if the user has selected (single) reference-scenario compare
        TODO: migrate to dse-do-dashboard (or to some new class in the dse-do-dashboard?)
        """
        ms_selected = self.get_multi_scenario_compare_selected()
        ref_selected = isinstance(self.ref_dm, DataManager)
        return not ms_selected and ref_selected