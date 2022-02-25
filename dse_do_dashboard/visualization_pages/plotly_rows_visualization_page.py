# Copyright IBM All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
from abc import abstractmethod
from typing import List, NamedTuple

from dash import dcc
import dash_bootstrap_components as dbc
import plotly.graph_objs as go

from dse_do_dashboard.do_dash_app import DoDashApp
from dse_do_dashboard.visualization_pages.visualization_page import VisualizationPage
from dse_do_utils.plotlymanager import PlotlyManager


class PlotlyRowsVisualizationPage(VisualizationPage):
    """Abstract class. Creates a layout of Plotly Figures in a row format.
    Each row can contain a variable set of figures.
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

    @abstractmethod
    def get_plotly_figures(self, pm: PlotlyManager) -> List[List[go.Figure]]:
        """
        :returns List of Lists of Plotly Figures. One for each row.
        """
        rows=[]
        return rows

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
