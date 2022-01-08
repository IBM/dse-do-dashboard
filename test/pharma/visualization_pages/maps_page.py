from dash import dcc
import dash_bootstrap_components as dbc

from dse_do_dashboard.do_dash_app import DoDashApp
from dse_do_dashboard.visualization_pages.visualization_page import VisualizationPage
from dse_do_utils.plotlymanager import PlotlyManager


class MapsPage(VisualizationPage):
    def __init__(self, dash_app: DoDashApp):
        super().__init__(dash_app=dash_app,
                         page_name='Maps',
                         page_id='maps_tab',
                         url='maps',
                         input_table_names = ['Line', 'Product', 'Location', 'Plant', 'Demand', 'BomItem'],
                         output_table_names = ['DemandInventory','TransportationActivity', 'ProductionActivity', 'PlantInventory', 'WarehouseInventory'],
                         )

    def get_layout_children(self, pm: PlotlyManager):
        layout_children = [
            # ddk.Block(),

            dbc.Card(
                dcc.Graph(
                    figure=pm.line_map(),
                    # style={'height': '65vh', 'width': '79vw'},
                    # style={'height': '800px', 'width': '1000px'},
                )
            ),

            dbc.Row(
                dbc.Col(
                    dbc.Card([
                        ##       dbc.CardHeader(""),
                        dbc.CardBody(
                            dcc.Graph(
                                figure=pm.demand_choropleth_map(),
                                # style={'height': '65vh', 'width': '79vw'},
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
                                figure=pm.unfulfilled_demand_choropleth_map(),
                                # style={'height': '65vh', 'width': '79vw'},
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
                                figure=pm.unfulfilled_demand_choropleth_map(animation_col = "timePeriodSeq"),
                                # style={'height': '65vh', 'width': '79vw'},
                            )
                        )
                    ])
                    # , width=12
                )
            ),
        ]
        return layout_children
