# Copyright IBM All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from abc import ABC
from typing import Dict, Optional, List

import dash
from dash import dcc, html, Output, Input, State
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import os
from flask_caching import Cache
import enum
import diskcache
from dash.long_callback import DiskcacheLongCallbackManager

from dse_do_dashboard.utils.dash_common_utils import ScenarioTableSchema


class HostEnvironment(enum.Enum):
    Local = 1  # Regular Dash
    CPD402 = 2  # Special handling of port


class DashApp(ABC):
    def __init__(self, logo_file_name: str = 'IBM.png',
                 navbar_brand_name: Optional[str] = 'Dashboard',
                 cache_config: Dict = {},
                 port: int = 8050,
                 dash_debug: bool = False,
                 host_env: Optional[HostEnvironment] = None,
                 bootstrap_theme = dbc.themes.BOOTSTRAP,
                 bootstrap_figure_template: str = "bootstrap",
                 enable_long_running_callbacks: bool = False,
                 ):
        self.port = port
        self.host_env = host_env
        self.dash_debug = dash_debug
        self.bootstrap_theme = bootstrap_theme
        self.set_bootstrap_figure_template(bootstrap_figure_template)

        # Long running callbacks:
        self.enable_long_running_callbacks = enable_long_running_callbacks
        if self.enable_long_running_callbacks:
            cache = diskcache.Cache("./cache")
            self.long_callback_manager = DiskcacheLongCallbackManager(cache)
        else:
            self.long_callback_manager = None

        self.app = self.create_dash_app()

        # Margins to layout the header, sidebar and content area:
        self.header_height = "3rem" # "6rem"
        self.footer_height = "10rem"
        self.sidebar_width = "16rem"
        self.adbar_width = "4rem"

        self.logo_file_name = logo_file_name  # set before call to get_app_layout()
        self.navbar_brand_name = navbar_brand_name
        self.cache_config = cache_config

        self.config_cache()
        self.app.layout = self.get_app_layout()

        self.set_cache_callbacks()
        self.set_dash_callbacks()




    def set_bootstrap_figure_template(self, bootstrap_figure_template: str):
        """See https://hellodash.pythonanywhere.com/theme_explorer"""
        load_figure_template(bootstrap_figure_template)
        self.bootstrap_figure_template = bootstrap_figure_template

    def create_dash_app(self):
        """Creates the Dash app. Called from the DashApp constructor.
        Implements special process around running in CPDv4.0.2 (i.e. `ws_applications.make_link()`)
        Can be overridden if necessary.

        Note:
            Changing Bootstrap stylesheets requires a Reload on the browser!
        """
        # print(os.getcwd())
        assets_path = os.getcwd() +'/assets'  # Not sure why it is not picking it up automatically, but this works
        if self.host_env == HostEnvironment.CPD402:
            print(f"Host is CPD, so run with make_link({self.port})")
            from ws_applications import make_link
            requests_prefix = make_link(self.port)
            app = dash.Dash(__name__,
                            serve_locally=False,
                            requests_pathname_prefix=requests_prefix,
                            # suppress_callback_exceptions = True,
                            assets_folder=assets_path,
                            long_callback_manager=self.long_callback_manager,
                            )
        else:
            app = dash.Dash(__name__,
                            # suppress_callback_exceptions = True,
                            assets_folder=assets_path,
                            long_callback_manager=self.long_callback_manager,
                            )
        dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.css"
        app.config.external_stylesheets = [self.bootstrap_theme, dbc_css]
        # app.config.external_stylesheets = [dbc.themes.SOLAR]
        app.config.suppress_callback_exceptions = True
        return app

    def run_server(self):
        """Runs the Dash server.
        To be called from index.py::

            if __name__ == '__main__':
                DA.run_server()

        """
        self.app.run_server(debug=self.dash_debug, port=self.port)

    def config_cache(self):
        self.cache = Cache()
        self.cache.init_app(self.app.server, config=self.cache_config)

    def get_app_layout(self):
        """Layout of whole app"""
        layout = html.Div([
            dcc.Location(id='url'),
            self.get_app_stores_div(),
            self.get_navbar(),
            self.get_sidebar(),
            self.get_content_template()],
            className="dbc"  # Bootstrap CSS, see https://hellodash.pythonanywhere.com/about_dbc_css
        )
        return layout

    def display_content_callback(self, pathname):
        """Callback for main content area. Will update the content area.
        Will need to be called through callback in index.py, where `DA` is the instance of the DashApp.

        Usage::

            @app.callback(Output('content', 'children'), [Input('url', 'pathname')])
            def display_content(pathname):
                return DA.display_content_callback()

        """
        layout = html.Div([
            html.H1(f"Error 404 - Page '{pathname}' not found"),
            dcc.Textarea(
                id='not_found',
                value='Page not found',
                style={'width': '100%', 'height': 300},
            ),
        ])
        return layout

    def get_content_template(self):
        """The template structure for the main content page.
        The callback `display_content` will update the actual contents
        """
        content = html.Div(id = 'content',
                           style = self.get_content_style()
                           )
        return content

    def get_content_style(self):
        """Style for the main contents section.
        Very important is the `margin-left`, otherwise it will overlap with the left-side navbar.
        Except for the margins, the other properties don't seem to differ from the default.

        :return:
        """
        # header_height, footer_height = "6rem", "10rem"
        # sidebar_width, adbar_width = "16rem", "4rem"
        content_style = {
            "margin-top": "1rem" , #self.header_height,
            "margin-left": self.sidebar_width,
            "margin-right": "1rem" , #self.adbar_width,
            "margin-bottom": self.footer_height,
            # "padding": "2rem 1rem",
            # "card_border": {
            #     "width": "1px",
            #     "style": "solid",
            #     "color": "#8EA9C1",
            #     "radius": "0px"
            # },
            # "card_background_color": "#edf3f4",
            # "card_box_shadow": "0px 0px 0px rgba(0,0,0,0)",
            # "card_margin": "15px",
            # "card_padding": "5px",
            # "card_outline": {
            #     "width": "0px",
            #     "style": "solid",
            #     "color": "#8EA9C1"
            # },
            # "card_header_border": {
            #     "width": "0px 0px 2px 0px",
            #     "style": "dashed",
            #     "color": "#8EA9C1",
            #     "radius": "0px"
            # },
            # "card_header_background_color": "#edf3f4",
            # "card_header_box_shadow": "0px 0px 0px rgba(0,0,0,0)",
            # "card_header_margin": "0px",
            # "card_header_padding": "10px",
            # "colorway": [
            #     "#004172",
            #     "#08539d",
            #     "#2e64c7",
            #     "#be35a0",
            #     "#e32433",
            #     "#eb6007",
            #     "#fb8b00",
            #     "#c19f00",
            #     "#5c9c00",
            #     "#897500",
            #     "#cb0049",
            #     "#7746ba",
            #     "#0080d1",
            #     "#3192d2",
            #     "#ac6ac0",
            #     "#e34862",
            #     "#c57e00",
            #     "#71a500",
            #     "#ad6e00",
            #     "#b82e2e",
            # ],
            # "colorscale": [
            #     "#00224e",
            #     "#123570",
            #     "#3b496c",
            #     "#575d6d",
            #     "#707173",
            #     "#8a8678",
            #     "#a59c74",
            #     "#c3b369",
            #     "#e1cc55",
            #     "#fee838"
            # ],
            # "font_family": "Quicksand",
            # "font_size": "15px",
            # "font_size_smaller_screen": "13px",
            # "font_family_header": "PT Sans",
            # "font_size_header": "24px",
            # "font_family_headings": "PT Sans",
            # "font_headings_size": None,
            # "header_border": {
            #     "width": "0px",
            #     "style": "solid",
            #     "color": "#8EA9C1",
            #     "radius": "0px"
            # },
        }
        return content_style

    def get_logo_src(self):
        src = self.app.get_asset_url(self.logo_file_name)
        return src

    def get_navbar_brand_children(self) -> str:
        """The children of the dbc.NavbarBrand component, typically a plain string.
        To be overridden."""
        brand = self.navbar_brand_name  #'Dashboard'
        return brand

    def get_navbar(self):
        # The scenario-bar is the section on the right with the scenario-dropdown and the refresh button
        scenario_bar = dbc.Row(
            [
                dcc.Store(id='reference_scenario_name_store'),
                dcc.Store(id='multi_scenario_names_store'),
                dbc.Col(
                    dcc.Dropdown(
                        id='top_menu_scenarios_drpdwn',
                        style={'width': '30vw'},
                    ),
                ),
                dbc.Col(
                    dbc.Button(
                        "Refresh", id='scenario_refresh_button', color="primary", className="ms-2", n_clicks=0
                    ),
                    width="auto",
                ),
            ],
            className="g-0 ms-auto flex-nowrap mt-3 mt-md-0",
            align="center",
        )

        navbar = dbc.Navbar(
            dbc.Container(
                [
                    html.A(
                        # Use row and col to control vertical alignment of logo / brand
                        dbc.Row(
                            [
                                dbc.Col(html.Img(src=self.get_logo_src(), height="50vh")),
                                # dbc.Col(dbc.NavbarBrand("Dashboard", className="ms-2")),
                                dbc.Col(dbc.NavbarBrand(self.get_navbar_brand_children(), className="ms-2")),
                            ],
                            align="center",
                            className="g-0",
                        ),
                        # href="/",
                        style={"textDecoration": "none"},
                    ),
                    # scenario_bar
                    dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),  # The NavbarToggler is a hamburger menu that will only appear of the screen is very small
                    dbc.Collapse(
                        scenario_bar,
                        id="navbar-collapse",
                        is_open=False,
                        navbar=True,
                    ),
                ]
            ),
            color="dark",
            dark=True,
        )
        return navbar
    # def get_navbar(self):
    #     navbar = dbc.Navbar(
    #         dbc.Container(
    #             [
    #                 html.A(
    #                     # Use row and col to control vertical alignment of logo / brand
    #                     dbc.Row(
    #                         [
    #                             dbc.Col(html.Img(src=self.get_logo_src(), height="50vh")),
    #                             dbc.Col(dbc.NavbarBrand("Dashboard", className="ms-2")),
    #                         ],
    #                         # align="left",
    #                         className="g-0",
    #                     ),
    #                     style={"textDecoration": "none"},
    #                 ),
    #                 dcc.Dropdown(
    #                     id='top_menu_scenarios_drpdwn',
    #                     style={'width': '20vw'},
    #
    #                 ),
    #
    #                 html.Button('Refresh', id='scenario_refresh_button', n_clicks=0,
    #                             style={'width': '300px'}
    #                             ),
    #             ]
    #         ),
    #         color="dark",
    #         dark=True,
    #         fixed='top'
    #     )
    #     return navbar

    def get_sidebar(self):
        sidebar_style = {
            "position": "fixed",
            "top": self.header_height,
            "left": 0,
            "bottom": self.footer_height,
            "width": self.sidebar_width,
            "padding": "1rem 1rem",
        }
        sidebar = html.Div([
            html.Hr(),
            dbc.Nav([

                dbc.NavLink(
                    href=self.app.get_relative_path('/'),
                    children='Home'
                ),
                # dbc.NavLink(
                #     href=self.app.get_relative_path('/prepare-data'),
                #     children='Prepare Data'
                # ),
                # dbc.NavLink(
                #     href=self.app.get_relative_path('/run-model'),
                #     children='Run Model'
                # ),
                # dbc.NavLink(
                #     href=self.app.get_relative_path('/explore-solution'),
                #     children='Explore Solution'
                # ),
                # dbc.NavLink(
                #     href=app.get_relative_path('/visualization'),
                #     children='Visualization'
                # ),

                # dbc.Button(
                #     "Visualization",
                #     outline=True,
                #     id = 'collapse-button',
                #     className='mb-3',
                #     n_clicks=0,
                #     href=self.app.get_relative_path('/visualization'),
                #     # active=True,
                #     color='primary',
                #
                # ),

                # dbc.Collapse(
                #     children = visualization_menu_children,
                #     id = "collapse",
                #     is_open=True,
                #     navbar=True,
                # ),

            ], vertical=True, pills=True,)], style = sidebar_style
        )
        return sidebar

    def get_app_stores_div(self) -> html.Div:
        """A Div container with all globally (and thus permanently available) dcc.Stores in the app."""
        stores = html.Div(
            id = 'global_stores',  # Not necessary
            children = self.get_app_stores()
        )
        return stores

    def get_app_stores(self) -> List[dcc.Store]:
        """To be overridden"""
        stores = []
        return stores

    def set_cache_callbacks(self):
        pass

    def set_dash_callbacks(self):
        app = self.app

        @app.callback(
            Output('content', 'children'),
            [Input('url', 'pathname'), Input('top_menu_scenarios_drpdwn', 'value')],
            [State('reference_scenario_name_store', 'data'),
             State('multi_scenario_names_store', 'data')
             ]
        )
        def display_content(pathname, scenario_name, reference_scenario_name, multi_scenario_names):
            """High level call back to update the content section of the app.
            Triggers when either the URL or the scenario-dropdown changes."""
            # reference_scenario_name = None,  #TODO
            # multi_scenario_names = None  #TODO

            # print(f"Reference scenario = {reference_scenario_name}")
            # print(f"Multi scenario names = {multi_scenario_names}")
            print(f"Showing URL = {pathname}")
            return self.display_content_callback(pathname, scenario_name, reference_scenario_name, multi_scenario_names)

        @app.callback(
            [Output('top_menu_scenarios_drpdwn', 'options'), Output('top_menu_scenarios_drpdwn', 'value')],
            [Input('scenario_refresh_button', 'n_clicks')],
            [State('top_menu_scenarios_drpdwn', 'value')],
            # Read the state of scenarios dropdown. Do NOT define this as an Input, otherwise the refresh will be triggered when you change the scenario.
            # prevent_initial_call = True  # If True, would prevent clearing the cache. However, it will also prevent the initialization of the scenario drpdwn menu!
        )
        def refresh_scenarios(n_clicks, current_scenario_name:str):
            """Reads the currently selected scenario-name. Reloads the scenario names from DB.
            If the currently selected scenario is valid, this will be maintained as the selected value.
            Main callback from scenario dropdown (?)
            """
            options, initial_scenario_name = self.refresh_scenarios_dash_callback(current_scenario_name)
            return [options, initial_scenario_name]

        @app.callback(
            Output("navbar-collapse", "is_open"),
            [Input("navbar-toggler", "n_clicks")],
            [State("navbar-collapse", "is_open")],
        )
        def toggle_navbar_collapse(n, is_open):
            """Callback for NavbarToggler in top-menubar.
            The NavbarToggler is a hamburger menu that will only appear of the screen is very small.
            So in normal desktop use, this toggler and callback are irrelevant."""
            if n:
                return not is_open
            return is_open

    def shutdown(self):
        """Shuts-down the Flash web-server, releasing the port.
        Relevant in CPD, so the port gets released immediately.
        """
        from flask import request
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()

    def get_table_schema(self, table_name) -> Optional[ScenarioTableSchema]:
        pass
