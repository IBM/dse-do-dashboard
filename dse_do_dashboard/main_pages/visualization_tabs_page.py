# Copyright IBM All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import Dict, List

from dse_do_dashboard.main_pages.main_page import MainPage
from dash import dcc, html, Output, Input, State
import dash_bootstrap_components as dbc

from dse_do_dashboard.visualization_pages.visualization_page import VisualizationPage


class VisualizationTabsPage(MainPage):
    """Visualization pages in tabbed layout

    TODO (minor): handle case when there are no visualization pages (i.e. len(self.dash_app.visualization_pages) == 0)
    """
    def __init__(self, dash_app):
        super().__init__(dash_app,
                         page_name='Visualization',
                         page_id='visualization',
                         url='visualization',
                         )

    def get_layout(self, scenario_name: str = None, reference_scenario_name: str = None, multi_scenario_names: List[str] = None):
        tab_style = {"fontWeight": "bold"}
        visualization_pages = self.dash_app.visualization_pages
        tab_children = [
            dcc.Tab(
                label=vp.page_name,
                value=vp.page_id,
                style=tab_style,
                selected_style=tab_style,
            ) for vp in visualization_pages
        ]
        tabs = dcc.Tabs(
            id="tabs",
            value=visualization_pages[0].page_id,
            children=tab_children,
        )
        layout = html.Div([
            dbc.Card(children=tabs),
            html.Div(id='page_content'),
        ]
        )
        return layout

    def get_visualization_tab_layout_callback(self, page_id, scenario_name: str, reference_scenario_name: str = None, multi_scenario_names: List[str] = None):
        """
        Callback to render the visualization tabs.
        Call from DoDashApp, which is in turn is called from index.py::

            @app.callback(Output("page_content", "children"),
              [Input("tabs", "value"),
               Input('top_menu_scenarios_drpdwn', 'value')])
            def get_visualization_tab_layout_callback(page_id, scenario_name):
                return DA.get_visualization_tab_layout_callback(page_id, scenario_name)

        """
        print(f"get_visualization_tab_layout_callback for {page_id}")
        visualization_pages_dict: Dict[str, VisualizationPage] = {vp.page_id: vp for vp in self.dash_app.visualization_pages}
        if page_id in visualization_pages_dict:
            vp = visualization_pages_dict[page_id]
            try:
                print(f"Getting layout for {page_id}")
                # tab_layout = getattr(sys.modules[f"visualization_pages.{vp.module_name}"], 'layout')
                tab_layout = vp.get_layout(scenario_name, reference_scenario_name, multi_scenario_names)
                return tab_layout

            except KeyError:
                print(f"ERROR in visualization render_tabs2: unknown module_name = {vp.module_name}")
                # return main_pages.not_found.layout
                return self.dash_app.get_not_found_page().get_layout(f"ERROR in visualization render_tabs2: unknown module_name = {vp.module_name}")

        else:
            print(f"ERROR in visualization render_tabs2: unknown page_id = {page_id}")
            # return main_pages.not_found.layout
            return self.dash_app.get_not_found_page().get_layout(f"ERROR in visualization render_tabs2: unknown page_id = {page_id}")

    def set_dash_callbacks(self):
        """Define Dash callbacks for this page

        Will be called to register any callbacks
        :return:
        """
        app = self.dash_app.app

        @app.callback(Output("page_content", "children"),
                      [Input("tabs", "value"),
                       Input('top_menu_scenarios_drpdwn', 'value')],
                      [State('reference_scenario_name_store', 'data'),
                       State('multi_scenario_names_store', 'data')])
        def get_visualization_tab_layout_callback(page_id, scenario_name, reference_scenario_name, multi_scenario_names):
            """To update the tabbed-visualization page."""
            print("xxxxxxxxxxxxxxxxxxxxxx")
            return self.get_visualization_tab_layout_callback(page_id, scenario_name,
                                                              reference_scenario_name=reference_scenario_name,
                                                              multi_scenario_names=multi_scenario_names)
