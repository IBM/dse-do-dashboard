# Copyright IBM All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import List

from plotly.graph_objs import Figure

from dse_do_dashboard.dash_plotly_manager import DashPlotlyManager
from dse_do_dashboard.do_dash_app import DoDashApp
from dse_do_dashboard.visualization_pages.plotly_1_column_visualization_page import Plotly1ColumnVisualizationPage


class OptimizationProgressPage(Plotly1ColumnVisualizationPage):

    def __init__(self, dash_app: DoDashApp) -> None:
        super().__init__(
            dash_app=dash_app,
            page_name='OptimizationProgress',
            page_id='optimization_progress_tab',
            url='optimization_progress',
            input_table_names=[],
            output_table_names=['OptimizationProgress'],
        )

    def get_plotly_figures(self, pm: DashPlotlyManager) -> List[Figure]:
        return [
            pm.plotly_optimization_progress(),
            pm.plotly_optimization_progress_kpis()
        ]
