# Copyright IBM All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from abc import ABC, abstractmethod
from dash import html, dcc
from dse_do_dashboard.dash_app import DashApp

class MainPage(ABC):
    def __init__(self, dash_app: DashApp, page_name: str, page_id: str, url: str):
        self.dash_app = dash_app
        self.page_name = page_name  # As shown in UI
        self.page_id = page_id  # Used for Dash pattern-matching callback
        self.url = url  # URL, i.e. web address: `host:port/url`

    @abstractmethod
    def get_layout(self):
        layout = html.Div([
            html.H1("Error 404 - Page not found"),
            dcc.Textarea(
                id='not_found',
                # value='Page not found',
                value="Error: Need to override `get_layout` method.",
                style={'width': '100%', 'height': 300},
            ),
        ])
        return layout

    def set_dash_callbacks(self):
        """Define Dash callbacks for this page.
        Note that a reference to `self` (i.e. the instance of the MainPage) is possible!.
        So you can directly call the callback defined in this subclass.
        :return:
        """
        pass


