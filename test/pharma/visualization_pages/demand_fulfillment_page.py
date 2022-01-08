from dash import dcc
import dash_bootstrap_components as dbc

from dse_do_dashboard.do_dash_app import DoDashApp
from dse_do_dashboard.visualization_pages.visualization_page import VisualizationPage
from dse_do_utils.plotlymanager import PlotlyManager


class DemandFulfillmentPage(VisualizationPage):
    def __init__(self, dash_app: DoDashApp):
        super().__init__(dash_app=dash_app,
                         page_name='Demand Fulfillment',
                         page_id='demand_fulfillment_tab',
                         url='demand_fulfillment',
                         input_table_names = ['Product'],
                         output_table_names = ['DemandInventory','TransportationActivity'],
                         )

    def get_layout_children(self, pm: PlotlyManager):
        layout_children = [

            dbc.Row(
                dbc.Col(
                    dbc.Card([
                        ##       dbc.CardHeader(""),
                        dbc.CardBody(
                            dcc.Graph(
                                figure=pm.plotly_demand_fullfilment_multi_plot(mode='columns',var_names=['Unfulfilled','Backlog','Backlog Resupply','Inventory']),
                                # style={'height': '55vh', 'width': '79vw'},
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
                                figure=pm.plotly_demand_fullfilment_multi_plot(),
                                # style={'height': '200vh', 'width': '79vw'},
                            )
                        )
                    ])
                    # , width=12
                )
            ),
        ]
        return layout_children
