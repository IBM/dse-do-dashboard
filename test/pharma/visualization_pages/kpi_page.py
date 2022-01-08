from dash import dcc, dash_table
import dash_bootstrap_components as dbc

from dse_do_dashboard.do_dash_app import DoDashApp
from dse_do_dashboard.visualization_pages.visualization_page import VisualizationPage
from dse_do_utils.plotlymanager import PlotlyManager


class KpiPage(VisualizationPage):
    def __init__(self, dash_app: DoDashApp):
        super().__init__(dash_app=dash_app,
                         page_name='KPIs',
                         page_id='kpi_tab',
                         url='kpi',
                         input_table_names=['Line', 'Product', 'Location', 'Plant', 'Demand', 'BomItem'],
                         output_table_names=['DemandInventory','TransportationActivity', 'ProductionActivity', 'PlantInventory', 'WarehouseInventory', 'kpis', 'BusinessKPIs'],
                         )

    def get_layout_children(self, pm: PlotlyManager):
        kpis = pm.dm.kpis.reset_index()
        b_kpis = pm.dm.business_kpis.reset_index()

        print(f"Utilization KPI = {pm.utilization_kpi()}")


        # gauge_style = {'height': '30vh', 'width': '41vw', 'margin-left':'auto','margin-right':'auto', 'display':'block'}
        gauge_style = {'height': '20vh', 'width': '20vw', 'margin-left':'auto','margin-right':'auto', 'display':'block'}
        # gauge_style = {'height': '20vh'}
        layout_childen = [
            # ddk.Header([ddk.Title('Business KPI Gauges')]),

            dbc.Row([
                dbc.Col(
                    dbc.Card([
                        dbc.CardBody(
                            # dbc.Block(width=25),
                            dcc.Graph(
                                id="stat1",
                                # style={'height': '30vh', 'width': '41vw', 'margin-left':'auto','margin-right':'auto', 'display':'block'},
                                style=gauge_style,
                                # style={'height': '20vh'},
                                figure=pm.make_gauge(value=round(b_kpis['value'].iloc[0] * 100, 3),
                                                       title="Unfulfilled Demand %", max_val=100,
                                                       orange_threshold=2, red_threshold=5)
                            ),)
                    ],
                        # style={"border": "none", "outline": "solid green"},
                    )
                ),
                dbc.Col(
                    dbc.Card([
                        dbc.CardBody(
                            # dbc.Block(width=25),
                            dcc.Graph(
                                id="stat2",
                                # style={'height': '30vh', 'width': '41vw', 'margin-left':'auto','margin-right':'auto', 'display':'block'},
                                style=gauge_style,
                                figure=pm.make_gauge(value=round(b_kpis['value'].iloc[1] * 100, 3),
                                                       title="Backlog %", max_val=100,
                                                       orange_threshold=5, red_threshold=10)
                            ), )
                    ],
                    ))
            ],
                # style={'padding':'15px'}
            ),

            dbc.Row([
                dbc.Col(
                    dbc.Card([
                        dbc.CardBody(
                            # dbc.Block(width=25),
                            dcc.Graph(
                                id="stat3",
                                # style={'height': '30vh', 'width': '26.5vw', 'margin-left':'auto','margin-right':'auto', 'display':'block'},
                                style=gauge_style,
                                figure=pm.make_gauge_dos(value=round(pm.dos_kpi(), 3),
                                                           title="Inventory Days-of-Supply",
                                                           max_val=80)
                            ), )])),
                dbc.Col(
                    dbc.Card([
                        dbc.CardBody(
                            # dbc.Block(width=25),
                            dcc.Graph(
                                id="stat4",
                                # style={'height': '30vh', 'width': '26.5vw', 'margin-left':'auto','margin-right':'auto', 'display':'block'},
                                style=gauge_style,
                                figure=pm.make_gauge(value=float(pm.calc_air_pct()),
                                                       title="Air Shipping %",
                                                       orange_threshold=10, red_threshold=30,
                                                       max_val=100)
                            ), )])),
                dbc.Col(
                    dbc.Card([
                        dbc.CardBody(
                            # dbc.Block(width=25),
                            dcc.Graph(
                                id="stat5",
                                # style={'height': '30vh', 'width': '26.5vw', 'margin-left':'auto','margin-right':'auto', 'display':'block'},
                                style=gauge_style,
                                figure=pm.make_gauge(value=round(pm.utilization_kpi(), 3),
                                                       title="Utilization %",
                                                       orange_threshold=85, red_threshold=95,
                                                       max_val=100)
                            ), )]))

            ]),

            dbc.Row(
                dbc.Col(
                    dbc.Card([
                        ##       dbc.CardHeader(""),
                        dbc.CardBody(
                            dcc.Graph(
                                # id='plotly_transportation_bar',
                                # id={
                                #     'type': chart_type,
                                #     'index': 'plotly_demand_bars'  # Method on PlotlySupplyChainDataManager!
                                # },
                                figure=pm.kpi_heatmap(),
                                style={'height': '55vh', 'width': '79vw'},
                                # style={'height': '35vh', 'width': '39vw'},
                            )
                        )
                    ])
                    # , width=12
                )
            ),


            # ddk.Header([ddk.Title('KPI Table')]),

            dbc.Row(style = {'height': '5px'}),
            dbc.Row(
                dbc.Col(
                    dbc.Card([
                        dbc.CardBody(
                            dash_table.DataTable(
                                # style = {'width': 50},
                                columns=[{"name": i, "id": i} for i in b_kpis.columns],
                                data=b_kpis.to_dict("rows"),
                                editable=True,
                                style_cell={
                                    'font_family': 'sans-serif',
                                    'font_size': '12px',
                                    'textAlign': 'left'},
                                style_table={
                                    'maxHeight': '300px',
                                    'width': '79vw',
                                    # 'width': '500px',
                                    'overflowY': 'scroll'
                                },
                                # style={'height': '35vh', 'width': '85vw'},
                            ))], style = {'width':'80.5vw'}))),

            dbc.Row(style={'height': '50px'}),

        ]

        return layout_childen
