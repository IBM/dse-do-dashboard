# Copyright IBM All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import List, NamedTuple

from dash import dcc
import dash_bootstrap_components as dbc
import plotly.graph_objs as go

from dse_do_dashboard.do_dash_app import DoDashApp
from dse_do_dashboard.visualization_pages.visualization_page import VisualizationPage
from dse_do_utils.plotlymanager import PlotlyManager

# from fruit_distribution.fruit.fruitplotlymanager import FruitPlotlyManager


class KpiPageTemplate(VisualizationPage):
    """Abstract class. Creates a layout of KPI gauges with multiple rows of KPI gauges.
    Override the method `get_plotly_figures`.
    """
    def __init__(self, dash_app: DoDashApp, page_name: str = 'Default', page_id: str = 'default', url: str = 'default',
                 input_table_names: List[str] = [], output_table_names: List[str] = []):
        super().__init__(dash_app=dash_app,
                         page_name=page_name,
                         page_id=page_id,
                         url=url,
                         input_table_names=input_table_names,
                         output_table_names=output_table_names,
                         )

    def get_plotly_figures(self, pm: PlotlyManager) -> List[List[go.Figure]]:
        """Create gauges for KPI page as rows of columns.
        That is, each entry in the gauges represents a row. Each row contains a set of go.Figure.

        Abstract method. This is just a sample of a 2x2 matrix of KPIs. Override to """
        kpi_df = pm.dm.kpis
        gauges = [
            [
                KpiPageTemplate.make_traffic_light_gauge(
                    title="KPI 1 %",
                    value=round(.88 * 100, 3),
                    orange_threshold=75,
                    red_threshold=90,
                    max_val=100),
                KpiPageTemplate.make_traffic_light_gauge(
                    title="KPI 2",
                    value=55,
                    orange_threshold=75,
                    red_threshold=90,
                    max_val=100),
            ],
            [
                KpiPageTemplate.make_traffic_light_gauge(
                    title="KPI 3 %",
                    value=round(.33 * 100, 3),
                    orange_threshold=25,
                    red_threshold=50,
                    max_val=100),
                KpiPageTemplate.make_traffic_light_gauge(
                    title="KPI 4",
                    value=777,
                    orange_threshold=750,
                    red_threshold=900,
                    max_val=1000),
            ],
        ]
        return gauges

    def get_layout_children(self, pm: PlotlyManager):
        """Creates a layout for KPI gauges with multiple rows and columns.
        Each row can contain any number of columns."""
        figures = self.get_plotly_figures(pm=pm)

        figure_style = {'height': '20vh', 'width': '20vw', 'margin-left': 'auto', 'margin-right': 'auto',
                       'display': 'block'}
        layout_childen = []

        for figure_row in figures:
            row_layout = dbc.Row([
                dbc.Col(
                    dbc.Card([
                        dbc.CardBody(
                            dcc.Graph(
                                style=figure_style,
                                figure=figure
                            )
                        )
                    ])
                )
                for figure in figure_row
            ])
            layout_childen.append(row_layout)

        return layout_childen

    @staticmethod
    def make_traffic_light_gauge(value: float, title: str, orange_threshold: float, red_threshold: float, max_val: float):
        """
        """
        steps = [
            {'range': [0, orange_threshold], 'color': 'green'},
            {'range': [orange_threshold, red_threshold], 'color': 'orange'},
            {'range': [red_threshold, max_val], 'color': 'red'},
        ]

        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = value,
            domain = {'x': [0, 1], 'y': [0, .75]},
            title = {'text': title, 'font': {'color': 'black', 'size': 18}},
            gauge = {'axis': {'range': [None, max_val], 'tickfont': {'color': 'black'}},
                     'threshold' : {'line': {'color': "darkred", 'width': 4}, 'thickness': 0.75, 'value': red_threshold},
                     'steps': steps,
                     'bar': {'color': "darkblue"},},
        ))

        fig.update_layout(font = {'color': 'green' if value < orange_threshold else 'orange' if value > orange_threshold and value < red_threshold else 'red', 'family': "Arial"},
                          margin={'t':10,'b':30},
                          )

        return fig