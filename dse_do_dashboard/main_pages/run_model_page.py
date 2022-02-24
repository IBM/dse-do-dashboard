import time
from typing import List, Dict

import pandas as pd
import dash
from dash import dcc, html, Output, Input, State, dash_table
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate


from dse_do_dashboard.main_pages.main_page import MainPage
from dse_do_dashboard.utils.domodelrunner import DoModelRunnerConfig


class RunModelPage(MainPage):
    """
    Challenge with long_callback:
    If you navigate away from this page while the long_callback is running, Dash will generate errors
    stating that input/output components do not exist:
    All components ('ids') that are used for inputs, outputs, states and progress (output) must continue to exists
    while the callback is running.
    Work-around:
    Use dcc.Store(s) on a global level:
    * lrc_job_trigger_store: the result of pressing the run button, along with the scenario_name and model_class
    * lrc_job_log_store: the log, i.e. the output of the long_callback
    * lrc_job_queue_data_store: the progress output of the long_callback
    Next, we have:
    * A button and a regular callback that store the trigger data (i.e. the user pressing the run button)
    * A regular callback watching the log store and update the log text area
    * A regular callback watching the queue data store and update the lrc job queue datatable

    """
    def __init__(self, dash_app,
                 page_name: str = 'Run Model',
                 page_id : str = 'run-model',
                 url: str = 'run-model',

                 ):
        super().__init__(dash_app,
                         page_name=page_name,
                         page_id=page_id,
                         url=url,
                         )
        self.runner_config_dict: Dict[str, DoModelRunnerConfig] = {config.runner_id: config for config in dash_app.get_do_model_runner_configs()}

    def get_layout(self, scenario_name: str = None, reference_scenario_name: str = None, multi_scenario_names: List[str] = None):
        configs = list(self.runner_config_dict.values())

        layout = html.Div([
            # dcc.Store(id='job_queue_data_store'),
            dcc.Dropdown(
                id='do_model_class_drpdwn',
                options=[{'label': 'None', 'value': 'None'}]+[
                    {'label': config.runner_name, 'value': config.runner_id}
                    for config in configs
                ],
                # value=(configs[0].runner_id if len(configs) > 0 else None),
                value=('None'),
                style = {'width': '28vw',
                         # 'background-color': '#FF4136'
                         }),
            dbc.Button('Run Model inline', id='run_model_inline', n_clicks=0, color="primary", className="me-1"),
            dbc.Button('Run Model LRC', id='run_model_lrc', n_clicks=0, color="primary", className="me-1", disabled=(not self.dash_app.enable_long_running_callbacks)),
            dbc.Button('Update JobQueue', id='refresh_queue_inline', n_clicks=0, color="primary", className="me-1"),

            # html.H1("------------------------"),
            dbc.Card([
                dbc.CardHeader('Job Queue (in-line)'),
                dbc.CardBody(
                    children=[
                        self.get_job_queue_data_table(id = 'job_queue_table_inline'),
                    ]
                ),
            ]),
            dbc.Card([
                dbc.CardHeader('Job Queue (long-running)'),
                dbc.CardBody(
                    children=[
                        self.get_job_queue_data_table(id = 'job_queue_table_lrc'),
                    ]
                ),
            ]),
            dbc.Card([
                dbc.CardHeader('Job Log (in-line)'),
                dbc.CardBody(
                    children=[
                        dcc.Textarea(id='log_inline',
                                     readOnly =True,
                                     style={'width': '100%', 'height': 200},
                                     ),
                    ]
                ),
            ]),
            dbc.Card([
                dbc.CardHeader('Job Log (long-running)'),
                dbc.CardBody(
                    children=[
                        dcc.Textarea(id='log_lrc',
                                     readOnly =True,
                                     style={'width': '100%', 'height': 200},
                                     ),
                    ]
                ),
            ]),
        ],
        )
        return layout

    def set_dash_callbacks(self):
        """Define Dash callbacks for this page

        Will be called to register any callbacks
        :return:
        """
        app = self.dash_app.app

        # Need to get the runner_config_dict as a 'global' variable so that the long_callback can be pickled
        # runner_config_dict = self.runner_config_dict

        def make_default_progress_data():
            """We do not have to specify columns"""
            df = pd.DataFrame()
            return df.to_dict('records')

        @app.callback(
            Output('log_inline', 'value'),
                           [Input('run_model_inline', 'n_clicks')],
                           [State('top_menu_scenarios_drpdwn', 'value'),
                            State('do_model_class_drpdwn', 'value'),
                            ],
                           prevent_initial_call=True,
                           )
        def run_model_inline_callback(
                n_clicks,
                scenario_name: str,
                do_model_class_name: str,
                ):

            # print("RunModelPage2.run_model_callback_inline")

            if do_model_class_name == 'None':
                raise PreventUpdate

            # time.sleep(0.2)

            runner_class = self.runner_config_dict[do_model_class_name].runner_class
            print(f"Runner class = {runner_class}")
            runner = runner_class(scenario_name, dash_app=self.dash_app)
            # runner = FruitClassRunner(scenario_name)
            runner.run()
            # time.sleep(4)

            log = f"Run {do_model_class_name} with scenario {scenario_name}\n" \
                  "Log: \n" \
                  f"{runner.log}"
            return log


        @app.callback(Output('job_queue_table_lrc', 'data'),
                      [Input('lrc_job_queue_data_store', 'data')],
                      )
        def refresh_queue_callback(data):
            """The idea is to place the Store in the top-menu bar and this is always there.
            That may prevent issues with the long_callback.
            However, it seems to be also sensitive towards the input button.
            So this work-around may not apply anyway.
            Not in use currently. Here as a backup if we need it"""
            # print("refresh_queue_callback")
            if data is None or len(data) == 0:
                raise PreventUpdate
            # print(f"refresh_queue_callback with data {data}")
            return data

        @app.callback(Output('job_queue_table_inline', 'data'),
                      Input('refresh_queue_inline', 'n_clicks'),
                      )
        def refresh_job_queue_inline(n_clicks):
            return self.get_job_queue_data()


        @app.callback(Output('lrc_job_trigger_store', 'data'),
                      Input('run_model_lrc', 'n_clicks'),
                      [State('top_menu_scenarios_drpdwn', 'value'),
                      State('do_model_class_drpdwn', 'value'),],
                      prevent_initial_call=True,
                      )
        def lrc_job_trigger(n_clicks,
                            scenario_name: str,
                            do_model_class_name: str,):
            # TODO: as an extra precaution use the ctx to check it was the button that triggered the callback?
            # Note that switching scenarios will trigger this callback. Despite the prevent_initial_call
            # However, since switching scenarios will regenerate this page, the n_clicks will be 0
            trigger = {'n_clicks':n_clicks, 'scenario' : scenario_name, 'do_model_class_name': do_model_class_name}
            # print(f"Initial Trigger = {trigger}")
            if n_clicks == 0 or do_model_class_name == 'None':
                raise PreventUpdate
            trigger = {'n_clicks':n_clicks, 'scenario_name' : scenario_name, 'do_model_class_name': do_model_class_name}
            # print(f"Store Trigger = {trigger}")
            return trigger

        @app.callback(Output('log_lrc', 'value'),
                      Input('lrc_job_log_store', 'data'),
                      # prevent_initial_call=True,
                      )
        def lrc_job_log_update(data):
            # print(f"lrc_job_log_update = {data}")
            if data is None:
                raise PreventUpdate
            return data

    def get_job_queue_data(self) -> List[Dict]:
        """Return a List[Dict] with job DoModelRunner queue data.
        As in df.to_dict('records')
        """
        rows = []
        for job in self.dash_app.job_queue:
            row = {'id' : job.id,
                   'model': job.__class__.__name__,
                   'scenario' : job.scenario_name,
                   'run_status' : job.run_status}
            rows.append(row)
        # if len(rows) > 0:
        #     df = pd.DataFrame(rows)
        # else:
        #     df = pd.DataFrame(columns=['id', 'runner_class', 'scenario_name', 'run_status'])
        return rows

    def get_job_queue_data_table(self, id: str) -> dash_table.DataTable:
        return dash_table.DataTable(
            id=id,
            columns=[{'name': 'scenario', 'id': 'scenario'},
                     {'name': 'model', 'id': 'model'},
                     {'name': 'run_status', 'id': 'run_status'}
                     ],
            fixed_rows={'headers': True},
            editable=True,
            # fixed_columns={'headers': False, 'data': 0}, # Does NOT create a horizontal scroll bar
            filter_action="native",
            sort_action="native",
            sort_mode="multi",
            style_cell={
                'textOverflow': 'ellipsis',  # See https://dash.plotly.com/datatable/width to control column-name width
                'maxWidth': 0,               # Needs to be here for the 'ellipsis' option to work
                'overflow' : 'hidden',
                'font_family': 'sans-serif',
                'font_size': '12px',
                'textAlign': 'left'},
            style_table={
                'maxHeight': '400px',
                'overflowY': 'scroll'
            },
        )