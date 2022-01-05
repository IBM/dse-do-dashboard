# DSE_DO_Dashboard
Plotly/Dash-based dashboard for Decision Optimization projects in IBM Cloud Pak for Data.

[Source (GitHub)](https://github.com/IBM/dse-do-dashboard)<br>
[Documentation (GitHubPages)](https://ibm.github.io/dse-do-dashboard/)

This repository contains the package `dse_do_dashboard`. This can be installed using pip.

## Introduction
This re-usable and extendable framework allows a data-scientist to quickly configure a Plotly/Dash-based dashboard 
for a project in IBM Cloud Pak for Data. This package is mainly focussed on Decision Optimization projects, 
but can be used for any CPD project.

Data exchange between the CPD project and the dashboard is through a (DB2/DB2WH/DB-on-cloud) database.
The database contains one or more 'scenarios'. 
A scenario is a set of named DataFrames, divided in 2 sets: inputs and outputs.

A user would typically define a set of custom VisualizationPages, each containing one or more Plotly plots.
In addition, Folium maps are supported.

![DO Dashboard Layout](docs/source/_static/MainDashboardLayout.jpg?raw=true "DO Dashboard Layout")
![DO Dashboard Layout](_static/MainDashboardLayout.jpg?raw=true "DO Dashboard Layout")

## Main classes
1. DoDashApp. Main class that contains the framework code for the dashboard. Subclass to define your dashboard.
2. VisualizationPage. Subclass for each visualization page in your dashboard.

## Usage
Main steps:
1. In your CPD project, define subclasses for `dse_do_utils.DataManager`, `dse_do_utils.ScenarioDbManager`, and `dse_do_utils.PlotlyManager`
2. Subclass `dse_do_dashboard.DoDashApp`.
3. For each custom visualization page, define a subclass of `dse_do_dashboard.VisualizationPage`.
4. Provision a database (DB2 or Db2-on-cloud), get the credentials.
5. Use the `dse_do_utils.ScenarioDbManager` in your CPD project to insert one or more scenarios in the DB.
6. Create an `index.py` file that creates and instance of the DoDashApp and runs the server.
7. Run `index.py` to start the dashboard. Open link with browser.

## DoDashApp UI structure
An instance of a DoDashApp will have the following UI layout:
1. A top-menu bar with the logo and a drop-down menu to select the scenario.
2. A left side-bar menu with 5 'main' pages:
   1. Home: Select reference scenarios. To be further developed.
   2. Prepare Data: Out-of-the-box UI to review the input tables.
   3. Run Model: run a deployed DO. To be further developed.
   4. Explore Solution: Out-of-the-box UI to review the output tables.
   5. Visualization: A tabbed-view of the custom VisualizationPages.
3. In the left side-bar a collapsable menu with the custom VisualizationPages

## DoDashApp Example
An example of a dashboard class that contains 2 custom VisualizationPages: KpiPage and DemandPage.
Most important:
1. Create instances of the VisualizationPages
2. Specify the class names of the DataManager, ScenarioDbManager and PlotlyManager

```
class FruitDashApp(DoDashApp):
    def __init__(self, db_credentials: Dict, schema: str = None, cache_config: Dict = None,
                 port: int = 8050, debug: bool = False, host_env: str = None):
        visualization_pages = [
            KpiPage(self), 
            DemandPage(self),
        ]
        logo_file_name = "logistics.jpg"

        database_manager_class = FruitScenarioDbManager
        data_manager_class = FruitDataManager
        plotly_manager_class = FruitPlotlyManager
        super().__init__(db_credentials, schema,
                         logo_file_name=logo_file_name,
                         cache_config=cache_config,
                         visualization_pages = visualization_pages,
                         database_manager_class=database_manager_class,
                         data_manager_class=data_manager_class,
                         plotly_manager_class=plotly_manager_class,
                         port=port, debug=debug, host_env=host_env)
```

## VisualizationPage example
Example of a custom VisualizationPage. 
It uses the Plotly1ColumnVisualizationPage that creates a one-column vertical layout of a set of Plotly figures.
Most important:
1. Create a subclass of VisualizationPage (in this case of a Plotly1ColumnVisualizationPage). Specify the name, url and id.
2. Specify the names of the input and output tables that need to be loaded for the visualizations on this page.
3. Define methods on the PlotlyManager that create Plotly Figures and add to method `get_plotly_figures`.

```
class DemandPage(Plotly1ColumnVisualizationPage):
    def __init__(self, dash_app: DoDashApp):
        super().__init__(dash_app=dash_app,
                         page_name='Demand',
                         page_id='demand_tab',
                         url='demand',
                         input_table_names=['Demand','Inventory'],  # Use ['*'] to include all tables
                         output_table_names=[],
                         )

    def get_plotly_figures(self, pm: PlotlyManager) -> List[Figure]:
        return [
            pm.plotly_demand_pie(),
            pm.plotly_demand_vs_inventory_bar(),
        ]
```