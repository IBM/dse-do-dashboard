from dash import dcc
import dash_bootstrap_components as dbc

from dse_do_dashboard.do_dash_app import DoDashApp
from dse_do_dashboard.visualization_pages.visualization_page import VisualizationPage
from dse_do_utils.plotlymanager import PlotlyManager


class ProductionPage(VisualizationPage):
    def __init__(self, dash_app: DoDashApp):
        super().__init__(dash_app=dash_app,
                         page_name='Production',
                         page_id='production_tab',
                         url='production',
                         input_table_names = ['Product', 'Location'],
                         output_table_names = ['ProductionActivity'],
                         )

    def get_layout_children(self, pm: PlotlyManager):
        layout_children = [

            dbc.Row(
                dbc.Col(
                    dbc.Card([
                        ##       dbc.CardHeader(""),
                        dbc.CardBody(
                            dcc.Graph(
                                figure=pm.plotly_production_activities_bars(title="Total Production"),
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
                                figure=pm.plotly_production_activities_bars(query="productGroup == 'Package'",title="Package Production"),
                                # style={'height': '100vh', 'width': '79vw'},
                            )
                        )
                    ])
                    # , width=12
                )
            ),

        ]

        return layout_children
