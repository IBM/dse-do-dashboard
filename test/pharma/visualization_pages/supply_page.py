from dash import dcc, html
import dash_bootstrap_components as dbc

from dse_do_dashboard.do_dash_app import DoDashApp
from dse_do_dashboard.visualization_pages.visualization_page import VisualizationPage
from dse_do_utils.plotlymanager import PlotlyManager


class SupplyPage(VisualizationPage):
    def __init__(self, dash_app: DoDashApp):
        super().__init__(dash_app=dash_app,
                         page_name='Supply Flow',
                         page_id='supply_tab',
                         url='supply',
                         input_table_names = ['RecipeProperties', 'Line', 'Product', 'Location', 'Plant', 'BomItem', 'WIP'],
                         output_table_names = ['PlantInventory', 'WarehouseInventory',  'DemandInventory', 'ProductionActivity', 'TransportationActivity'],
                         )

    def get_layout_children(self, pm: PlotlyManager):
        layout_children = [

            dbc.Row(
                dbc.Col(
                    dbc.Card([
                        # dbc.CardHeader(title='Production'),
                        dbc.CardBody(
                            [dbc.CardHeader(html.Div("Production", style={'width': '80vw'})),
                             dcc.Graph(
                                 figure=pm.plotly_inventory_flow_sankey(),
                                 # style={'height': '85vh', 'width': '79vw'},
                             )
                             ])
                    ])
                    # , width=12
                )
            ),

            dbc.Row(
                dbc.Col(
                    dbc.Card([
                        # dbc.CardHeader(title='Production'),
                        dbc.CardBody(
                            [dbc.CardHeader(html.Div("Transportation", style={'width': '80vw'})),
                             dcc.Graph(
                                 figure=pm.plotly_production_activities_sankey(),
                                 # style={'height': '45vh', 'width': '79vw'},
                             )
                             ])
                    ])
                    # , width=12
                )
            ),

            dbc.Row(
                dbc.Col(
                    dbc.Card([
                        # dbc.CardHeader(title='Production'),
                        dbc.CardBody(
                            [dbc.CardHeader(html.Div('Inventory Flow', style={'width': '80vw'})),
                             dcc.Graph(
                                 figure=pm.plotly_transportation_activities_sankey(),
                                 # style={'height': '45vh', 'width': '79vw'},
                             )
                             ])
                    ])
                    # , width=12
                )
            ),
        ]

        return layout_children
