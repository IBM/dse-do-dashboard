from dash import dcc
import dash_bootstrap_components as dbc

from dse_do_dashboard.do_dash_app import DoDashApp
from dse_do_dashboard.visualization_pages.visualization_page import VisualizationPage
from dse_do_utils.plotlymanager import PlotlyManager


class InventoryPage(VisualizationPage):
    def __init__(self, dash_app: DoDashApp):
        super().__init__(dash_app=dash_app,
                         page_name='Inventory',
                         page_id='inventory_tab',
                         url='inventory',
                         input_table_names = ['RecipeProperties', 'Line', 'Product', 'Location', 'Plant', 'Demand'],
                         output_table_names = ['PlantInventory', 'WarehouseInventory', 'DemandInventory'],
                         )

    def get_layout_children(self, pm: PlotlyManager):
        layout_children = [

            dbc.Row([
                dbc.Col(
                    dbc.Card([
                        ##       dbc.CardHeader(""),
                        dbc.CardBody(
                            dcc.Graph(
                                figure=pm.plotly_wh_inventory(mode='area'),
                                # style={'height': '75vh', 'width': '36vw'},
                            ),
                        )
                    ])
                ),
                dbc.Col(
                    dbc.Card([
                        ##       dbc.CardHeader(""),
                        dbc.CardBody(
                            dcc.Graph(
                                figure=pm.plotly_plant_inventory(mode='area'),
                                # style={'height': '75vh', 'width': '36vw'},
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
                                figure=pm.plotly_plant_inventory(mode='bar'),
                                # style={'height': '85vh', 'width': '79vw'},
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
                                figure=pm.plotly_wh_inventory(mode='bar'),
                                # style={'height': '85vh', 'width': '79vw'},
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
                                figure=pm.plotly_demand_inventory(mode = 'bar'),
                                # style={'height': '85vh', 'width': '79vw'},
                            )
                        )
                    ])
                    # , width=12
                )
            ),
        ]
        return layout_children
