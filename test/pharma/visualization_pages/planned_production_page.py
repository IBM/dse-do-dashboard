from dash import dcc
import dash_bootstrap_components as dbc

from dse_do_dashboard.do_dash_app import DoDashApp
from dse_do_dashboard.visualization_pages.visualization_page import VisualizationPage
from dse_do_utils.plotlymanager import PlotlyManager


class PlannedProductionPage(VisualizationPage):
    def __init__(self, dash_app: DoDashApp):
        super().__init__(dash_app=dash_app,
                         page_name='Planned Production',
                         page_id='planned_production_tab',
                         url='planned_production',
                         input_table_names = ['Product', 'PlannedProductionActivity'],
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
                                figure=pm.plotly_planned_production_activities_bars(title="Total Planned Production"),
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
                                figure=pm.plotly_planned_production_activities_bars(query="productGroup == 'Package'",title="Planned Package Production"),
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
                                figure=pm.plotly_production_slack_bars(title="Planned Production Slack"),
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
                                figure=pm.plotly_production_excess_bars(title="Planned Production Difference"),
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
                                figure=pm.plotly_production_excess_bars(
                                    title="Planned Production Difference - Percentage", mode='percentage'),
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
                                figure=pm.plotly_production_excess_bars(query="productGroup == 'Package'",
                                                                          title="Planned Package Production Difference"),
                                # style={'height': '100vh', 'width': '79vw'},
                            )
                        )
                    ])
                    # , width=12
                )
            ),

        ]

        return layout_children
