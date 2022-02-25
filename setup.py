# Copyright IBM All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import setuptools

###########################################################
# Problem:
# * `import dse_do_dashboard` is going to run the __init__.py,
# * which is going to do an import of `DoDashApp`,
# * which starts to load from required packages that have not been installed yet
# So we're back at the question of how to load the __version__ without triggering importing dependent packages
# * For now go back to manually defining the version here
###########################################################
# import dse_do_dashboard
# from dse_do_dashboard.version import __version__  # Prevents loading the whole package? No!

with open("README.md", "r") as fh:
    long_description = fh.read()

version = '0.1.2.1b'

setuptools.setup(
    name="dse_do_dashboard",
    # version=dse_do_dashboard.__version__,
    # version=__version__,
    version=version,
    author="Victor Terpstra",
    author_email="vterpstra@us.ibm.com",
    description="Decision Optimization Dashboard for IBM Cloud Pak for Data DO projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/IBM/dse-do-dashboard",
    packages=setuptools.find_packages(),
    install_requires=[
        'dse-do-utils>=0.5.4.2',
        'dash~=2.0.0',
        # 'flask_caching==1.10.1',
        # 'dash_bootstrap_components==1.0.2',
        # 'dash-bootstrap-templates==1.0.4',
        # 'dash_pivottable==0.0.2',
        # 'dash_daq==0.5.0',
        # 'sqlalchemy>=1.3.23, <1.4',
        # 'pandas<1.4',  # Pandas 1.4 requires sqlalchemy 1.4, see https://pandas.pydata.org/docs/dev/whatsnew/v1.4.0.html
        # 'plotly~=5.4.0',  # 5.5.0 is causing problems installing on CPD
        # 'openpyxl==3.0.9',
        # 'diskcache==5.4.0',  # For long-running callbacks
        # 'multiprocess==0.70.12.2',  # For long-running callbacks
        # 'psutil==5.9.0',  # For long-running callbacks
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        # "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Documentation :: Sphinx"
    ],
    project_urls={  # Optional
        'Source': 'https://github.com/IBM/dse-do-dashboard',
        'Documentation': 'https://ibm.github.io/dse-do-dashboard/',
        'IBM Decision Optimization': 'https://www.ibm.com/analytics/decision-optimization',
    },
)