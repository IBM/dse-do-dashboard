# Copyright IBM All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import List

from plotly.graph_objs import Figure

from dse_do_dashboard.do_dash_app import DoDashApp
from dse_do_dashboard.visualization_pages.plotly_rows_visualization_page import PlotlyRowsVisualizationPage
from dse_do_utils.plotlymanager import PlotlyManager

class KPIComparePage(PlotlyRowsVisualizationPage):
    def __init__(self, dash_app: DoDashApp):
        super().__init__(dash_app=dash_app,
                         page_name='KPI Compare',
                         page_id='kpi_compare_tab',
                         url='kpi_compare',
                         input_table_names=[],
                         output_table_names=['kpis'],
                         enable_reference_scenario=True,
                         enable_multi_scenario=True
                         )

    def get_plotly_figures(self, pm: PlotlyManager) -> List[Figure]:
        return pm.plotly_kpi_compare_bar_charts()

