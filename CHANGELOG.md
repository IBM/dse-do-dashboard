# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]## [0.1.2.3b0]

## [0.1.2.2] - 2022-12-09
### Changed
- setup.py avoids import of dse_do_utils to get __version__
- Removed unused import in dash_common_utils causing failure in PyCharm debug mode

## [0.1.2.2b2] - 2022-11-15
### Changed
- DoDashApp.read_scenario_tables_from_db_cached only reads tables in the schema, skips others without warning.
- Enabled virtualization in DashTables (Prepare data and Explore Solution)
- Remove restriction on SQLAlchemy version < 1.4

## [0.1.2.2b1] - 2022-10-17
### Changed
- DashApp.run_server(self, **kwargs) with arguments for dash app.run_server()
- Enabled write output to DB after run model.
### Removed
- DashApp.set_run_server_kwargs()

## [0.1.2.2b0] - 2022-09-22
### Changed
- Stop Server button now uses os.kill() instead of deprecated Werkzeug callback

## [0.1.2.1] - 2022-04-28
### Changed
### Added
- Customize the 'brand' name of the dashboard by overriding DashApp.get_navbar_brand_children
- Customize the 'brand' name text of the dashboard from DashApp constructor argument `navbar_brand_name`
- FoliumColumnVisualizationPage for Folium maps
- DashApp.set_run_server_kwargs to add arguments to app.run_server() call, e.g. to set `host='localhost'` for Macs.

## [0.1.2.0.post1] - 2022-02-25
### Changed
- Removed most version fixes in setup.py to avoid installation error in CP4D

## [0.1.2.0] - 2022-02-24
### Changed
- Version bump-up from 0.1.1.1b to 0.1.2.0 due to new features
- Fixed bug in KpiPageTemplate.__init__
- Changed documentation build folder to `docs/doc_build`
- Install requirement of SQLAlchemy >=1.3.23, <1.4 (setup.py)
- Fixed versions of all required packages to match CPD 4.0.5
- Upgraded to dse-do-utils v0.5.4.2
- Fixed bug in PrepareDataPageEdit.get_data_table when zero index-columns
- Fixed bug in dash_common_utils.get_data_table when zero index-columns
- Fix in VisualizationTabsPage (hard-coded 'demand_tab' initial value)
### Added
- Reference scenario - PlotlyManager gets a pm.ref_dm based on the selected reference_scenario
- Multi scenario compare - PlotlyManager gets a pm.ms_inputs and pm.ms_outputs dict of DataFrames for scenario compare
- Improved support for interactive visualization pages: VisualizationPage stores PlotlyManager in `self.pm` in `VisualizationPage.get_layout`
- DashApp.get_app_layout: added `className="dbc"` to support Bootstrap CSS, see https://hellodash.pythonanywhere.com/about_dbc_css
- DashApp and DoDashApp constructors: added bootstrap_theme and bootstrap_figure_template to support Bootstrap CSS
- PlotlyRowsVisualizationPage template to easily add a visualization page of rows of Plotly Figures
- utils.domodelrunner and utils.donotebookrunner modules
- RunModel page with IO for running in-line and long-running model callbacks

## [0.1.1.0] - 2022-01-11
### Changed
- Version bump-up to 0.1.1.0 due to many new features
- DashApp, DoDashApp `debug` property renamed to `dash_debug`
- HomePageEdit and PrepareDataEdit are default main pages
### Added
- HomePage: Scenario duplicate, rename, delete
- DoDashApp.db_echo flag for DB connection debugging
- HomePage: Download scenario as Excel file
- HomePage: Download all scenarios as zip archive
- HomePage: Upload scenarios (from individual .xlsx or multiple in .zip)
- Read and Delete scenario using SQLAlchemy
- Duplicate scenario using SQLAlchemy insert-select

## [0.1.0.0b5] - 2022-01-05
### Changed
- First release to PyPI

## [0.1.0.0b4] - 2022-01-05
### Changed
- Last release on github.ibm.com
### Added
- License text to all files

## [0.1.0.0b3] - 2022-01-04
### Added
- KpiPageTemplate to create KPIs visualization page with traffic-light gauges
- Edit input tables: change cell values
- DashApp.shutdown method (for 'Stop Server' button)

## [0.1.0.0b2] - 2022-01-02
### Added
- HostEnvironment enum
- 'Stop Server' button on Home page
### Removed
- Remove href on logo. Doesn't work well in CPD
- Removed utils.dash_common_utils.VisualizationPage(NamedTuple)

## [Unreleased]## [0.1.0.0b1]
### Added
- Initial version



