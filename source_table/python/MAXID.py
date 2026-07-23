# -*- coding: utf-8 -*-
"""
Created on Mon May 25 16:46:42 2026

@author: Joe
"""
import sqlite3

from config import MASTER_DB

def maxid():
    """
    Returns the largest SOURCE_ID currently in the updated database.
    """

    with sqlite3.connect(MASTER_DB) as conn:

        cursor = conn.execute(
            "SELECT MAX(SOURCE_ID) FROM Source_Table"
        )

        result = cursor.fetchone()[0]

    return int(result)