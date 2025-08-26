# Copyright IBM All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import List

import pandas as pd

from dse_do_dashboard.do_dash_app import DoDashApp
from dse_do_utils.plotlymanager import PlotlyManager
import plotly.graph_objs as go
from dash import html
import dash_ag_grid as dag

from dse_do_dashboard.visualization_pages.kpi_page_template import KpiPageTemplate


class DefaultKpiPage(KpiPageTemplate):
    def __init__(self, dash_app: DoDashApp):
        super().__init__(dash_app=dash_app,
                         page_name='KPIs',
                         page_id='kpi_tab',
                         url='kpi',
                         input_table_names=[],
                         output_table_names=['kpis', 'BusinessKpi',],
                         include_kpi_grid=True,
                         enable_reference_scenario=True,
                         enable_multi_scenario=True,
                         )

    def get_plotly_figures(self, pm: PlotlyManager) -> List[List[go.Figure]]:
        """Create gauges for KPI page as rows of columns.
        That is, each entry in the gauges represents a row. Each row contains a set of go.Figure"""
        return [[]]