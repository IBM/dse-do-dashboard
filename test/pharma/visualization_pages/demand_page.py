from dash import dcc
import dash_bootstrap_components as dbc

from dse_do_dashboard.do_dash_app import DoDashApp
from dse_do_dashboard.visualization_pages.visualization_page import VisualizationPage
from dse_do_utils.plotlymanager import PlotlyManager


class DemandPage(VisualizationPage):
    def __init__(self, dash_app: DoDashApp):
        super().__init__(dash_app=dash_app,
                         page_name='Demand',
                         page_id='demand_tab',
                         url='demand',
                         input_table_names=['Demand', 'Product'],
                         output_table_names=[],
                         )

    def get_layout_children(self, pm: PlotlyManager):
        view = "All"
        layout_children = [
            # html.H1("My demand tab 4"),

            dbc.Row(
                dbc.Col(
                    dbc.Card([
                        ##       dbc.CardHeader(""),
                        dbc.CardBody(
                            dcc.Graph(
                                id='plotly_demand_bars',
                                # id={
                                #     'type': chart_type,
                                #     'index': 'plotly_demand_bars'  # Method on PlotlySupplyChainDataManager!
                                # },
                                figure=pm.plotly_demand_bars(view=view),
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
                                id='plotly_demand_bars_v2',
                                # id={
                                #     'type': chart_type,
                                #     'index': 'plotly_demand_pie'  # Method on PlotlySupplyChainDataManager!
                                # },
                                figure=pm.plotly_demand_bars(query="productGroup == 'Package'",
                                                               title="Total Package Demand"),
                                # style={'height': '800px'},
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
                                id='plotly_demand_bars_v3',
                                # id={
                                #     'type': chart_type,
                                #     'index': 'plotly_products_sunburst'  # Method on PlotlySupplyChainDataManager!
                                # },
                                figure=pm.plotly_demand_bars(query="productGroup != 'Package'",
                                                               title="Total Granulate Demand"),
                                # style={'height': '400px'},
                                style={'height': '55vh', 'width': '79vw'},
                            )
                        )
                    ])
                    # , width=12
                )
            ),

        ]
        return layout_children
