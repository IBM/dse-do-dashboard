# Copyright IBM All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Server-side validation of scenario names.

Scenario names originate from client-controlled input (upload file names, rename/duplicate dialogs) and end up in
the UI (labels, grid column names). Only a conservative set of characters is allowed, so names can never carry
markup or code (e.g. quotes, brackets, parentheses, pipes, backslashes, angle brackets, control characters).
"""
import re
from typing import Optional

#: Max length. Consistent with the `String(256)` column `Scenario.scenario_name`.
MAX_SCENARIO_NAME_LENGTH = 256

# Allowlist: unicode letters, digits, underscore (`\w`), space, dot and hyphen.
_VALID_SCENARIO_NAME_PATTERN = re.compile(r'[\w .\-]+', re.UNICODE)


def get_scenario_name_error(scenario_name: Optional[str]) -> Optional[str]:
    """Returns a message describing why the scenario name is invalid, or None if the name is valid."""
    if not isinstance(scenario_name, str) or scenario_name.strip() == '':
        return "Scenario name cannot be empty."
    if len(scenario_name) > MAX_SCENARIO_NAME_LENGTH:
        return f"Scenario name cannot be longer than {MAX_SCENARIO_NAME_LENGTH} characters."
    if _VALID_SCENARIO_NAME_PATTERN.fullmatch(scenario_name) is None:
        return "Scenario name can only contain letters, digits, spaces, underscores (_), hyphens (-) and dots (.)."
    if scenario_name.startswith('.'):
        return "Scenario name cannot start with a dot (.)."
    return None


def is_valid_scenario_name(scenario_name: Optional[str]) -> bool:
    """True if the scenario name passes the allowlist and length checks."""
    return get_scenario_name_error(scenario_name) is None
