from abc import abstractmethod
from typing import List, Optional

from dash import dcc, html
import dash_bootstrap_components as dbc
from plotly.graph_objs import Figure

# from dse_do_dashboard.do_dash_app import DoDashApp
from dse_do_dashboard.visualization_pages.visualization_page import VisualizationPage
# Copyright IBM All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from dse_do_utils.plotlymanager import PlotlyManager


class Plotly1ColumnVisualizationPage(VisualizationPage):
    def __init__(self, dash_app, page_name:str='Default', page_id:str='default', url:str='default',
                 input_table_names: Optional[List[str]] = None, output_table_names: Optional[List[str]] = None,
                 enable_reference_scenario: bool = False,
                 enable_multi_scenario: bool = False,
                 show_page_name: bool = False):
        super().__init__(dash_app=dash_app,
                         page_name=page_name,
                         page_id=page_id,
                         url=url,
                         input_table_names = input_table_names,
                         output_table_names = output_table_names,
                         enable_reference_scenario=enable_reference_scenario,
                         enable_multi_scenario=enable_multi_scenario
                         )
        self.show_page_name = show_page_name

    @abstractmethod
    def get_plotly_figures(self, pm: PlotlyManager) -> List[Figure]:
        return []

    def get_layout_children(self, pm: PlotlyManager):
        """Automatic 1 Column layout of all Plotly Figures.
        Vertical height is driven from the height defined in the Plotly figure.

        :param pm:
        :return:
        """
        layout_children = [
            dbc.Row(
                dbc.Col(
                    dbc.Card([
                        ##       dbc.CardHeader(""),
                        dbc.CardBody(
                            dcc.Graph(
                                figure=fig,
                                # style={'height': '100vh', 'width': '79vw'},
                            )
                        )
                    ])
                    # , width=12
                )
            )
            for fig in self.get_plotly_figures(pm)
        ]

        # Add a title row with the page_name
        if self.show_page_name:
            title_card = dbc.Card(html.H2(self.page_name, className='text-center'))
            layout_children.insert(0, title_card)

        return layout_children
