# Copyright IBM All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from dse_do_dashboard.main_pages.main_page import MainPage
from dash import dcc, html


class NotFoundPage(MainPage):
    def __init__(self, dash_app):
        super().__init__(dash_app,
                         page_name='Not Found',
                         page_id='not-found',
                         url='not-found',
                         )

    def get_layout(self, error_message: str = ""):
        layout = html.Div([

            html.H1("Error 404 - Page not found"),
            dcc.Textarea(
                id='not_found',
                # value='Page not found',
                value=error_message,
                style={'width': '100%', 'height': 300},
            ),

        ])
        return layout