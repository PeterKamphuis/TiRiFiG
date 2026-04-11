"""Shared selection state for the currently focused graph parameter."""

_current_parameter = None


def get_current_parameter():
    return _current_parameter


def set_current_parameter(parameter):
    global _current_parameter
    _current_parameter = parameter
