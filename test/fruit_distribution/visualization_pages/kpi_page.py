# Copyright IBM All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import List

from dse_do_dashboard.do_dash_app import DoDashApp
from dse_do_utils.plotlymanager import PlotlyManager
import plotly.graph_objs as go

from fruit_distribution.fruit.fruitplotlymanager import FruitPlotlyManager
from dse_do_dashboard.visualization_pages.kpi_page_template import KpiPageTemplate


class KpiPage(KpiPageTemplate):
    def __init__(self, dash_app: DoDashApp):
        super().__init__(dash_app=dash_app,
                         page_name='KPIs',
                         page_id='kpi_tab',
                         url='kpi',
                         input_table_names=[],
                         output_table_names=['kpis'],
                         )

    def get_plotly_figures(self, pm: PlotlyManager) -> List[List[go.Figure]]:
        """Create gauges for KPI page as rows of columns.
        That is, each entry in the gauges represents a row. Each row contains a set of go.Figure"""
        kpi_df = pm.dm.kpis
        gauges = [[
            KpiPageTemplate.make_traffic_light_gauge(
                title="Margin",
                value=kpi_df.at[("Margin"), "VALUE"],
                orange_threshold=750,
                red_threshold=900,
                max_val=1000),
            KpiPageTemplate.make_traffic_light_gauge(
                title="Transportation",
                value=kpi_df.at[("Transportation"), "VALUE"],
                orange_threshold=750,
                red_threshold=900,
                max_val=1000),
        ],
        [
            KpiPageTemplate.make_traffic_light_gauge(
                title="KPI %",
                value=round(.88 * 100, 3),
                orange_threshold=75,
                red_threshold=90,
                max_val=100),
        ]
        ]
        return gauges

    # def get_layout_children(self, pm: PlotlyManager):
    #     kpis = pm.dm.kpis.reset_index()
    #     kpi1 = 0.88
    #     kpi2 = .5
    #     kpi3 = .22
    #     kpi4 = .56
    #     kpi5 = .42
    #     # b_kpis = self.dm.business_kpis.reset_index()
    #
    #     # gauge_style = {'height': '30vh', 'width': '41vw', 'margin-left':'auto','margin-right':'auto', 'display':'block'}
    #     gauge_style = {'height': '20vh', 'width': '20vw', 'margin-left':'auto','margin-right':'auto', 'display':'block'}
    #     # gauge_style = {'height': '20vh'}
    #     layout_childen = [
    #         # ddk.Header([ddk.Title('Business KPI Gauges')]),
    #
    #         dbc.Row([
    #             dbc.Col(
    #                 dbc.Card([
    #                     dbc.CardBody(
    #                         # dbc.Block(width=25),
    #                         dcc.Graph(
    #                             id="stat1",
    #                             # style={'height': '30vh', 'width': '41vw', 'margin-left':'auto','margin-right':'auto', 'display':'block'},
    #                             style=gauge_style,
    #                             # style={'height': '20vh'},
    #                             figure=pm.make_gauge(value=round(kpi1 * 100, 3),
    #                                                    title="Unfulfilled Demand %", max_val=100,
    #                                                    orange_threshold=2, red_threshold=5)
    #                         ),)])),
    #             dbc.Col(
    #                 dbc.Card([
    #                     dbc.CardBody(
    #                         # dbc.Block(width=25),
    #                         dcc.Graph(
    #                             id="stat2",
    #                             # style={'height': '30vh', 'width': '41vw', 'margin-left':'auto','margin-right':'auto', 'display':'block'},
    #                             style=gauge_style,
    #                             figure=pm.make_gauge(value=round(kpi2 * 100, 3),
    #                                                    title="Backlog %", max_val=100,
    #                                                    orange_threshold=5, red_threshold=10)
    #                         ), )]))
    #         ]),
    #
    #         dbc.Row([
    #             dbc.Col(
    #                 dbc.Card([
    #                     dbc.CardBody(
    #                         # dbc.Block(width=25),
    #                         dcc.Graph(
    #                             id="stat3",
    #                             # style={'height': '30vh', 'width': '26.5vw', 'margin-left':'auto','margin-right':'auto', 'display':'block'},
    #                             style=gauge_style,
    #                             figure=pm.make_gauge(value=round(kpi3, 3),
    #                                                    title="Inventory Days-of-Supply",
    #                                                    orange_threshold=85, red_threshold=95,
    #                                                    max_val=80)
    #                         ), )])),
    #             dbc.Col(
    #                 dbc.Card([
    #                     dbc.CardBody(
    #                         # dbc.Block(width=25),
    #                         dcc.Graph(
    #                             id="stat4",
    #                             # style={'height': '30vh', 'width': '26.5vw', 'margin-left':'auto','margin-right':'auto', 'display':'block'},
    #                             style=gauge_style,
    #                             figure=pm.make_gauge(value=kpi4,
    #                                                    title="Air Shipping %",
    #                                                    orange_threshold=10, red_threshold=30,
    #                                                    max_val=100)
    #                         ), )])),
    #             dbc.Col(
    #                 dbc.Card([
    #                     dbc.CardBody(
    #                         # dbc.Block(width=25),
    #                         dcc.Graph(
    #                             id="stat5",
    #                             # style={'height': '30vh', 'width': '26.5vw', 'margin-left':'auto','margin-right':'auto', 'display':'block'},
    #                             style=gauge_style,
    #                             figure=pm.make_gauge(value=round(kpi5, 3),
    #                                                    title="Utilization %",
    #                                                    orange_threshold=85, red_threshold=95,
    #                                                    max_val=100)
    #                         ), )]))
    #
    #         ]),
    #     ]
    #
    #     return layout_childen