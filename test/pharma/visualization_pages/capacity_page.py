from dash import dcc
import dash_bootstrap_components as dbc

from dse_do_dashboard.do_dash_app import DoDashApp
from dse_do_dashboard.visualization_pages.visualization_page import VisualizationPage
from dse_do_utils.plotlymanager import PlotlyManager


class CapacityPage(VisualizationPage):
    def __init__(self, dash_app: DoDashApp):
        super().__init__(dash_app=dash_app,
                         page_name='Capacity',
                         page_id='capacity_tab',
                         url='capacity',
                         input_table_names = ['RecipeProperties', 'Line', 'Product'],
                         output_table_names = [],
                         )

    def get_layout_children(self, pm: PlotlyManager):
        layout_children = [

            # dbc.Row(dbc.Col(html.Div("A single, half-width column"), width=6)),
            dbc.Row(
                dbc.Col(
                    dbc.Card([
                        ##       dbc.CardHeader(""),
                        dbc.CardBody(
                            dcc.Graph(
                                figure=pm.plotly_time_product_group_capacity_bars(),
                                style={'height': '55vh', 'width': '79vw'},
                            )
                        )
                    ])
                    # , width=12
                )
            ),

            dbc.Row([
                dbc.Col(
                    dbc.Card([
                        ##       dbc.CardHeader(""),
                        dbc.CardBody(
                            dcc.Graph(
                                figure=pm.plotly_line_product_capacity_heatmap(),
                                style={'height': '55vh', 'width': '36vw'},
                            ),

                        )
                    ])
                ),
                dbc.Col(
                    dbc.Card([
                        ##       dbc.CardHeader(""),
                        dbc.CardBody(
                            dcc.Graph(
                                figure=pm.plotly_time_product_group_capacity_heatmap(),
                                style={'height': '55vh', 'width': '36vw'},
                            ),
                        )
                    ])
                ),
            ]),

            dbc.Row(
                dbc.Col(
                    dbc.Card([
                        ##       dbc.CardHeader(""),
                        dbc.CardBody(
                            dcc.Graph(
                                figure=pm.plotly_line_package_capacity_heatmap(),
                                style={'height': '55vh', 'width': '79vw'},
                            )
                        )
                    ])
                    # , width=12
                )
            ),

            dbc.Row(
                dbc.Col(
                    dbc.Card([
                        ##       dbc.CardHeader(""),
                        dbc.CardBody(
                            dcc.Graph(
                                figure=pm.plotly_time_package_capacity_heatmap(),
                                style={'height': '55vh', 'width': '79vw'},
                            )
                        )
                    ])
                    # , width=12
                )
            ),

        ]

        return layout_children
