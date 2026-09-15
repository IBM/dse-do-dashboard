# Copyright IBM All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import List

import pandas as pd
from dash import html
from plotly.graph_objs import Figure

from dse_do_dashboard import VisualizationPage
from dse_do_dashboard.dash_plotly_manager import DashPlotlyManager
from dse_do_dashboard.do_dash_app import DoDashApp
from dse_do_dashboard.visualization_pages.plotly_1_column_visualization_page import Plotly1ColumnVisualizationPage
from dse_do_dashboard.visualization_pages.plotly_rows_visualization_page import PlotlyRowsVisualizationPage
from dse_do_utils.plotlymanager import PlotlyManager
# from nurse_assignment.dashboard.nurse_assignment_dash_app import NurseAssignmentDashApp
import dash_ag_grid as dag


class OptimizationProgressGridPage(VisualizationPage):
    def __init__(self, dash_app: DoDashApp):
        super().__init__(dash_app=dash_app,
                         page_name='Optimization Progress Grid',
                         page_id='optimization_progress_grid_tab',
                         url='optimization_progress_grid',
                         input_table_names=[],
                         output_table_names=['OptimizationProgress'],
                         )

    def get_layout_children(self, pm: DashPlotlyManager) -> List:
        # grid = self.dash_app.get_ag_grid_from_df(pm.dm.shift_skill_requirements_output.reset_index())
        grid_1 = self.get_optimization_progress_grid(pm)
        layout = html.Div([grid_1])
        layouts = [layout]
        return layouts

    def get_optimization_progress_grid(self, pm: DashPlotlyManager) -> dag.AgGrid:
        df, kpis = pm.dm.get_optimization_progress_as_wide_df()
        df = df.reset_index()

        column_def_override = {
            # 'nurse_name': {'field': 'nurse_name', 'headerName': 'Staff Name', },
        }

        columns_in_grid = df.columns
        columns_in_data = columns_in_grid
        columnDefs = [column_def_override[c] if c in column_def_override.keys() else {'field': c} for c in
                      columns_in_grid]

        defaultColDef = {
            'editable': True,
            # make every column use 'text' filter by default
            "filter": "agTextColumnFilter",
            "columnSize": "autoSize",
            "columnSizeOptions": {"skipHeader": True}}

        grid = dag.AgGrid(
            id="basic-df-grid",
            rowData=df[columns_in_data].to_dict("records"),
            columnDefs=columnDefs,
            dashGridOptions={'pagination': True, "rowHeight": 30, 'alwaysMultiSort': True},
            defaultColDef=defaultColDef,
            style={"height": 600, "width": '100%'},
            columnSize="autoSize",
            columnSizeOptions={"skipHeader": False},
        )
        return grid

