from dash import dcc
import dash_bootstrap_components as dbc

from dse_do_dashboard.do_dash_app import DoDashApp
from dse_do_dashboard.visualization_pages.visualization_page import VisualizationPage
from dse_do_utils.plotlymanager import PlotlyManager


class TransportationPage(VisualizationPage):
    def __init__(self, dash_app: DoDashApp):
        super().__init__(dash_app=dash_app,
                         page_name='Transportation',
                         page_id='transportation_tab',
                         url='transportation',
                         input_table_names = ['Line', 'Product', 'Location', 'Plant', 'Demand', 'BomItem'],
                         output_table_names = ['DemandInventory','TransportationActivity', 'ProductionActivity', 'PlantInventory', 'WarehouseInventory'],
                         )

    def get_layout_children(self, pm: PlotlyManager):
        layout_children = [

            dbc.Row(
                dbc.Col(
                    dbc.Card([
                        ##       dbc.CardHeader(""),
                        dbc.CardBody(
                            dcc.Graph(
                                id='plotly_transportation_bar',
                                # id={
                                #     'type': chart_type,
                                #     'index': 'plotly_demand_bars'  # Method on PlotlySupplyChainDataManager!
                                # },
                                figure=pm.plotly_transportation_bar(
                                    query="originLocationName in ['Central_Warehouse', 'Abbott_WH_NL']",
                                    title='Departing from Central Warehouse'),  # Central_Warehouse
                                style={'height': '75vh', 'width': '79vw'},
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
                                id='plotly_transportation_bar',
                                # id={
                                #     'type': chart_type,
                                #     'index': 'plotly_demand_bars'  # Method on PlotlySupplyChainDataManager!
                                # },
                                figure=pm.plotly_transportation_bar(),
                                style={'height': '75vh', 'width': '79vw'},
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
                                id='plotly_transportation_bar',
                                # id={
                                #     'type': chart_type,
                                #     'index': 'plotly_demand_bars'  # Method on PlotlySupplyChainDataManager!
                                # },
                                figure=pm.plotly_transportation_bar(
                                    query="originLocationName in ['API_Plant', 'Abbott_Weesp_Plant']",
                                    title='Departing from API Plant'),
                                style={'height': '75vh', 'width': '79vw'},
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
                                id='plotly_transportation_bar',
                                # id={
                                #     'type': chart_type,
                                #     'index': 'plotly_demand_bars'  # Method on PlotlySupplyChainDataManager!
                                # },
                                figure=pm.plotly_transportation_bar(
                                    query="originLocationName in ['Abbott_Olst_Plant','Packaging_Plant']",
                                    title='Departing from Packaging Plant'),
                                style={'height': '75vh', 'width': '79vw'},
                            )
                        )
                    ])
                    # , width=12
                )
            ),
        ]
        return layout_children
