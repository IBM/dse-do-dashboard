# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]## [0.1.1.1b0]

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



