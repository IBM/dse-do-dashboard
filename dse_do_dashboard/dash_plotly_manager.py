from typing import Optional, TypeVar, Dict

import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots

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

    #################################################
    # Optimization Progress
    #################################################
    # def plotly_optimization_progress(self) -> Optional[go.Figure]:
    #         df, kpis = self.dm.get_optimization_progress_as_wide_df()
    #         df = df.reset_index()
    #
    #         if df.shape[0] == 0:
    #             return go.Figure()
    #
    #         # If lex_opti_level_id is not present, fall back to single subplot (legacy behaviour)
    #         if 'lex_opti_level_id' not in df.columns:
    #             fig = make_subplots(specs=[[{"secondary_y": True}]])
    #             fig.add_trace(
    #                 go.Scatter(x=df.solve_time, y=df.objective_value, name="Objective",
    #                            hovertemplate="Objective = %{y}<br>Solve time = %{x:.2f} sec",
    #                            line_shape='hv'),
    #                 secondary_y=False,
    #             )
    #             fig.add_trace(
    #                 go.Scatter(x=df.solve_time, y=df.objective_bound, name="Bound",
    #                            hovertemplate="Bound = %{y}<br>Solve time = %{x:.2f} sec", line_shape='hv'),
    #                 secondary_y=False,
    #             )
    #             fig.add_trace(
    #                 go.Scatter(x=df.solve_time, y=df.objective_gap, name="Gap",
    #                            hovertemplate="Gap = %{y:%}<br>Solve time = %{x:.2f} sec", line_shape='hv'),
    #                 secondary_y=True,
    #             )
    #             fig.update_layout(title_text="Objective, Bound and Gap progress")
    #             fig.update_xaxes(title_text="Solve Time (s)")
    #             fig.update_yaxes(title_text="Objective and bound", secondary_y=False)
    #             fig.update_yaxes(title_text="Gap", secondary_y=True)
    #             return fig
    #
    #         # Create one vertical facet (row) per lex_opti_level_id
    #         levels = sorted(df['lex_opti_level_id'].unique())
    #         n_rows = len(levels)
    #         specs = [[{"secondary_y": True}] for _ in range(n_rows)]
    #         fig = make_subplots(rows=n_rows, cols=1, specs=specs, shared_xaxes=True, vertical_spacing=0.06)
    #
    #         for row, level in enumerate(levels, start=1):
    #             level_df = df[df['lex_opti_level_id'] == level]
    #             if level_df.shape[0] == 0:
    #                 continue
    #
    #             fig.add_trace(
    #                 go.Scatter(x=level_df.solve_time, y=level_df.objective_value, name="Objective",
    #                            hovertemplate="Objective = %{y}<br>Solve time = %{x:.2f} sec", line_shape='hv'),
    #                 row=row, col=1, secondary_y=False,
    #             )
    #             fig.add_trace(
    #                 go.Scatter(x=level_df.solve_time, y=level_df.objective_bound, name="Bound",
    #                            hovertemplate="Bound = %{y}<br>Solve time = %{x:.2f} sec", line_shape='hv'),
    #                 row=row, col=1, secondary_y=False,
    #             )
    #             fig.add_trace(
    #                 go.Scatter(x=level_df.solve_time, y=level_df.objective_gap, name="Gap",
    #                            hovertemplate="Gap = %{y:%}<br>Solve time = %{x:.2f} sec", line_shape='hv'),
    #                 row=row, col=1, secondary_y=True,
    #             )
    #
    #             # Y-axis titles per facet
    #             fig.update_yaxes(title_text=f"Objective and bound (level {level})", row=row, col=1, secondary_y=False)
    #             fig.update_yaxes(title_text="Gap", row=row, col=1, secondary_y=True)
    #
    #         fig.update_layout(title_text="Objective, Bound and Gap progress by lex_opti_level_id", showlegend=True)
    #         fig.update_xaxes(title_text="Solve Time (s)")
    #         return fig


    def plotly_optimization_progress(self, lex_opti_level_id: str = None) -> Optional[go.Figure]:
        df, kpis = self.dm.get_optimization_progress_as_wide_df()
        if lex_opti_level_id is not None:
            df = df.query("lex_opti_level_id == @lex_opti_level_id")

        if df.shape[0] == 0:
            return go.Figure()

        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Add traces
        fig.add_trace(
            go.Scatter(x=df.solve_time, y=df.objective_value, name="Objective", hovertemplate="Objective = %{y}<br>Solve time = %{x:.2f} sec",
                       line_shape='hv',
                       # line_shape={'shape': 'hv'},  # Doesn't work!
                       ),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(x=df.solve_time, y=df.objective_bound, name="Bound", hovertemplate="Bound = %{y}<br>Solve time = %{x:.2f} sec", line_shape='hv'),
            secondary_y=False,
        )

        fig.add_trace(
            go.Scatter(x=df.solve_time, y=df.objective_gap, name="Gap", hovertemplate="Gap = %{y:%}<br>Solve time = %{x:.2f} sec", line_shape='hv'),
            secondary_y=True,
        )

        # Add figure title
        fig.update_layout(
            title_text="Objective, Bound and Gap progress"
        )

        # Set x-axis title
        fig.update_xaxes(title_text="Solve Time (s)")

        # Set y-axes titles
        fig.update_yaxes(title_text="Objective and bound", secondary_y=False)
        fig.update_yaxes(title_text="Gap", secondary_y=True)
        return fig

    def plotly_optimization_progress_kpis(self, lex_opti_level_id: str = None) -> Optional[go.Figure]:
        """Plots the KPI values as a function of the solve time.
        Returns None if no KPIs
        """
        # kpis = ['Allocated Volume', 'Utilization']

        df, kpis = self.dm.get_optimization_progress_as_wide_df()
        if lex_opti_level_id is not None:
            df = df.query("lex_opti_level_id == @lex_opti_level_id")

        # Handle when no KPIs, i.e. empty list
        if len(kpis) == 0:
            return go.Figure()

        # Create figure with secondary y-axis
        fig = make_subplots(rows=len(kpis), cols=1)

        for row, kpi in enumerate(kpis, start=1):
            fig.add_trace(
                go.Scatter(x=df.solve_time, y=df[kpi], name=kpi, hovertemplate=f"{kpi} = %{{y}}<br>Solve time = %{{x:.2f}} sec", line_shape='hv'),
                row=row, col=1,
            )
            fig.update_yaxes(title_text=kpi, row=row, col=1)

        # Add figure title
        fig.update_layout(
            title_text="KPIs progress"
        )

        # Set x-axis title
        fig.update_xaxes(title_text="Solve Time (s)")
        return fig