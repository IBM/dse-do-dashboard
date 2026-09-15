# Copyright IBM All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import List

from dash import html, dcc, Input, Output

from dse_do_dashboard import VisualizationPage
from dse_do_dashboard.dash_plotly_manager import DashPlotlyManager
from dse_do_dashboard.do_dash_app import DoDashApp

class OptimizationProgressPage(VisualizationPage):

    def __init__(self, dash_app: DoDashApp) -> None:
        super().__init__(
            dash_app=dash_app,
            page_name='OptimizationProgress',
            page_id='optimization_progress_tab',
            url='optimization_progress',
            input_table_names=['LexOptiLevel'],
            output_table_names=['OptimizationProgress'],
        )



    def get_layout_children(self, pm: DashPlotlyManager) -> List:
        """A drop-down button with the list of lexicographical optimization levels (sorted by priority) to select which level's progress to show, and then show the optimization progress line chart for that level, along with KPIs."""


        lex_opti_level_ids = self.get_lex_opti_level_ids(pm)
        dropdown = html.Div([
            html.Label("Select Lexicographical Optimization Level:"),
            dcc.Dropdown(
                id='lex_opti_level_dropdown',
                # options=[{'label': lex_opti_level_id, 'value': lex_opti_level_id} for lex_opti_level_id in lex_opti_level_ids],
                options=[{'label': f"{i} - {lex_opti_level_id}", 'value': lex_opti_level_id} for i, lex_opti_level_id in
                         enumerate(lex_opti_level_ids, start=1)],
                value=lex_opti_level_ids[0] if lex_opti_level_ids else None,  # Default to the first level if it exists

                clearable=False,
            )
        ])
        progress_line_chart = dcc.Graph(id='lex_opti_progress_line_chart')
        kpis_chart = dcc.Graph(id='lex_opti_progress_kpis_chart')

        layouts= [dropdown, progress_line_chart, kpis_chart]
        return layouts

    def get_lex_opti_level_ids(self, pm: DashPlotlyManager) -> List[str]:
        """Get a sorted list of active lexicographical optimization level IDs from the LexOptiLevel output table.
        Sort by priority (ascending).
        If there is only one unique lex_opti_level_id in the LexOptiMetrics output table, then return that one (even if the LexOptiLevel table has multiple levels), since in that case the metrics are only available at the overall optimization level, not at each individual lexicographical level.
        """
        df = pm.dm.optimization_progress_output.groupby(['lex_opti_level_id']).count()[[]]
        if hasattr(pm.dm, 'lex_opti_levels'):
            df = df.join(pm.dm.lex_opti_levels[['priority']], how='left')
            df = df.fillna(0) # If there are lex_opti_level_ids in the progress output that are not in the lex_opti_levels table, fill their priority with 0 to put them at the top of the list.
            df = df.sort_values(by='priority')
        lex_opti_level_ids = df.index.tolist()
        return lex_opti_level_ids

    def set_dash_callbacks(self):
        """Define Dash callbacks for this page

        Will be called to register any callbacks
        :return:
        """
        app = self.dash_app.app

        @app.callback(
            [
                Output("lex_opti_progress_line_chart", "figure"),
                Output("lex_opti_progress_kpis_chart", "figure")
            ],
            Input('lex_opti_level_dropdown', 'value'))
        def update_gap_and_kpi_table(lex_opti_level_id):
            fig1 = self.pm.plotly_optimization_progress(lex_opti_level_id=lex_opti_level_id)
            fig2 = self.pm.plotly_optimization_progress_kpis(lex_opti_level_id=lex_opti_level_id)
            return [fig1, fig2]
