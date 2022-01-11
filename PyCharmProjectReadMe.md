# DSE_DO_Dashboard - PyCharm Project setup

## Install environment and dependencies
1. File -> Settings -> Project -> Python Interpreter
Create a new virtual environment
2. Let `requirements.txt` install the dependencies

## Test the dse-do-dashboard package
In the `test` folder, add dashboard tests.
In order for the test to be able to do a regular import, add the `test` folder as a content root / source folder to the project

## Add dependency on dse-do-utils
Add the dse-do-utils root as a source folder to the project
1. File -> Settings -> Project -> Project Structure
2. Add Content Root
This allows us to develop the both packages in combination. Change the dse-do-utils and test in the dse-do-dashboard