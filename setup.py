# Copyright IBM All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import setuptools
import dse_do_dashboard

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dse_do_dashboard",
    version=dse_do_dashboard.__version__,
    author="Victor Terpstra",
    author_email="vterpstra@us.ibm.com",
    description="Decision Optimization Dashboard for IBM Cloud Pak for Data DO projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/IBM/dse-do-dashboard",
    packages=setuptools.find_packages(),
    install_requires=[
        'dse-do-utils>=0.5.4.0',
        'dash>=2.0.0',
        'flask_caching',
        'dash_bootstrap_components',
        'dash_pivottable',
        'dash_daq',
        'sqlalchemy>=1.3.23, <1.4',
        'pandas',
        'plotly',
        'openpyxl',
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