from dash import dcc
import dash_bootstrap_components as dbc

from dse_do_dashboard.do_dash_app import DoDashApp
from dse_do_dashboard.visualization_pages.visualization_page import VisualizationPage
from dse_do_utils.plotlymanager import PlotlyManager


class UtilizationPage(VisualizationPage):
    def __init__(self, dash_app: DoDashApp):
        super().__init__(dash_app=dash_app,
                         page_name='Utilization',
                         page_id='utilization_tab',
                         url='utilization',
                         input_table_names = ['Product'],
                         output_table_names = ['LineUtilization', 'ProductionActivity'],
                         )

    def get_layout_children(self, pm: PlotlyManager):
        layout_children = [

            dbc.Row(
                dbc.Col(
                    dbc.Card([
                        ##       dbc.CardHeader(""),
                        dbc.CardBody(
                            dcc.Graph(
                                figure=pm.plotly_excess_utilization_line_time_bars(),
                                # style={'height': '100vh', 'width': '79vw'},
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
                                figure=pm.plotly_utilization_line_time_bars(),
                                # style={'height': '100vh', 'width': '79vw'},
                            )
                        )
                    ])
                    # , width=12
                )
            ),
        ]
        return layout_children
