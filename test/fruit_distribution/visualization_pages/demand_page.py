# Copyright IBM All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import List

from plotly.graph_objs import Figure

from dse_do_dashboard.do_dash_app import DoDashApp
from dse_do_dashboard.visualization_pages.plotly_1_column_visualization_page import Plotly1ColumnVisualizationPage
from dse_do_utils.plotlymanager import PlotlyManager


class DemandPage(Plotly1ColumnVisualizationPage):
    def __init__(self, dash_app: DoDashApp):
        super().__init__(dash_app=dash_app,
                         page_name='Demand',
                         page_id='demand_tab',
                         url='demand',
                         # input_table_names=['Demand','Inventory'],
                         input_table_names=['*'],
                         output_table_names=[],
                         )

    def get_plotly_figures(self, pm: PlotlyManager) -> List[Figure]:
        return [
            pm.plotly_demand_pie(),
            pm.plotly_demand_vs_inventory_bar(),
        ]

