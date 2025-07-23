import contextlib
import sqlite3
import threading
from sqlite3 import Connection
from typing import Dict, List, Optional, Iterator

import pandas as pd
import pandas.io.sql as sqlio
from pandas import DataFrame


class BaseDb(object):

    def __init__(self, db_name):
        self.db_name = db_name

    def connect(self) -> Connection:
        return sqlite3.connect(self.db_name, check_same_thread=True)

    def execute_sql(self, sql, parameters=None, many=False) -> None:
        if parameters is None:
            parameters = []
        conn = self.connect()
        cur = conn.cursor()
        try:
            if not many:
                cur.execute(sql, parameters)
            else:
                cur.executemany(sql, parameters)
            conn.commit()
        finally:
            cur.close()
            conn.close()

    def query_df(self, sql: str, parameters=None) -> DataFrame:
        """
        Execute SQL query and return results as DataFrame.
        Use chunk_size for large result sets to process data in chunks.
        """
        with self.connect() as conn:
            df = sqlio.read_sql_query(sql, conn, params=parameters)
        return df

    def query_json(self, sql, parameters=None) -> str:
        df = self.query_df(sql, parameters)
        return df.to_json(orient="records")

    def query(self, sql, parameters=None):
        if parameters is None:
            parameters = []
        conn = self.connect()
        cur = conn.cursor()
        result = None
        try:
            result = list(cur.execute(sql, parameters))
        finally:
            cur.close()
            conn.close()
        return result

    @contextlib.contextmanager
    def query_iterator(self, sql, parameters=None):
        if parameters is None:
            parameters = []
        conn = self.connect()
        cur = conn.cursor()
        try:
            yield cur.execute(sql, parameters)
        finally:
            cur.close()

    def query_scalar(self, sql, parameters=None):
        if parameters is None:
            parameters = []
        res = self.query(sql, parameters)
        return res[0][0] if res else None

    def table_has_column(self, table: str, column: str) -> str | None:
        sql = "PRAGMA table_info ('{}')".format(table)
        lst = self.query(sql)
        for col in lst:
            if col[1] == column:
                return col
        return None

    def table_exists(self, table_name: str) -> bool:
        sql = "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?"
        result = self.query(sql, [table_name])
        return len(result) > 0

    def ddl_script(self, filename: str) -> None:
        with open(filename, "r") as f:
            sql = f.read()
            self.execute_sql(sql)

    def insert_list(self, filename: str, values: List) -> None:
        conn = self.connect()
        cur = conn.cursor()
        try:
            with open(filename, "r") as f:
                sql = f.read()
                cur.executemany(sql, values)
            conn.commit()
        finally:
            cur.close()
            conn.close()
