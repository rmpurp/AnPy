#!/usr/bin/env python

import datetime as dt
from typing import Optional


def new_category(name: str):
    """Create a new category with the given name and get the associated id."""
    pass


def set_category_activation(cat_id: int, status: bool):
    """Set the active status of the given category to the given state."""
    pass


def get_categories(active_only: bool = True):
    """Get the categories as a dict from id to name.

    If keyword argument active_only is true (default behavior), then only the
    categories that are marked active are returned. Otherwise all of them,
    including inactive ones, are returned.
    """
    pass


def start(cat_id: int, datetime: Optional[dt.datetime] = None):
    """Record the beginning of a working session.

    If there is no datetime object passed in, the datetime associated with the
    current instant will be used instead.
    """
    pass


def cancel():
    """Cancel the current working session that is running"""
    pass


def stop(datetime: dt.datetime = None):
    """Record the end of a current working session.

    If there is no datetime object passed in, the datetime associated with the
    current instant will be used instead.
    """
    pass


def rename_category(cat_id: int, name: str):
    """Change the name of the category associated with the given id"""
    pass
