import logging
from contextlib import contextmanager

import pymssql
import pyodbc

from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

# this is need otherwise pyodbc will not work correctly
pyodbc.setDecimalSeparator(".")


class BaseExternalMssql(models.Model):
    _name = "base.external.mssql"
    _description = "Base External Mssql"

    name = fields.Char("Name of Datasource", required=True)
    server = fields.Char("Datenbase Server", required=True)
    database = fields.Char("Database Name", required=True)
    username = fields.Char("Database User", required=True)
    password = fields.Char("Database Password", required=True)
    connection_string = fields.Text(readonly=True, compute="_compute_connection_string")
    priority = fields.Boolean(string="Use this DB")
    driver = fields.Selection(
        [("pyodbc", "pyodbc"), ("pymssql", "pymssql")], default="pymssql"
    )

    @api.depends("server", "database", "username", "password")
    def _compute_connection_string(self):
        for record in self:
            if record.driver == "pyodbc":
                conn_string = f"DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={record.server};DATABASE={record.database};UID={record.username};PWD={record.password};TrustServerCertificate=yes;"
            elif record.driver == "pymssql":
                conn_string = f'server="{record.server}", user="{record.username}", password="{record.password}", database="{record.database}", tds_version="7.0"'

            record.connection_string = conn_string

    @contextmanager
    def connection_open(self):
        """It provides a context manager for the data source."""
        try:
            if self.driver == "pyodbc":
                connection = pyodbc.connect(self.connection_string, autocommit=True)
            elif self.driver == "pymssql":
                connection = pymssql.connect(
                    server=self.server,
                    user=self.username,
                    password=self.password,
                    database=self.database,
                    tds_version="7.0",
                    autocommit=True,
                )
            yield connection
        finally:
            try:
                self.connection_close(connection)
            except Exception:
                _logger.exception("Connection close failure.")

    def connection_close(self, connection):
        return connection.close()

    def execute(self, query_type, query, *params, as_dict=True):
        # import pdb; pdb.set_trace()
        with self.connection_open() as connection:
            if not as_dict:
                cur = connection.cursor()
            else:
                cur = connection.cursor(as_dict=True)
            cur.execute(query)
            if query_type == "insert":
                # connection.commit() not needed for pymssql
                # res = cur.execute('SELECT SCOPE_IDENTITY() AS [SCOPE_IDENTITY];') # this works for pyodbc
                # last_id = res.fetchval() # this works for pyodbc
                last_id = cur.lastrowid
                return last_id
            elif query_type == "select":
                rows = cur.fetchall()
                return rows

            elif query_type == "select_one":
                # result = cur.fetchval()
                # result = cur.fetchone()[0]
                result = cur.fetchone()
                _logger.info("RESULT FROM SELECT ONE: %s" % (result,))
                connection.commit()
                return result

    def connection_test(self):
        """It tests the connection

        Raises:
            Validation message with the result of the connection (fail or success)
        """
        try:
            with self.connection_open():
                pass
        except Exception as e:
            raise ValidationError(
                "Connection test failed:\n"
                "Here is what we got instead:\n%s" % tools.ustr(e)
            )
        else:
            rows = self.execute("select", "SELECT @@VERSION", as_dict=False)
            message = "Datenbbank-Version:\n"
            for row in rows:
                message += f"{row[0]} \n"

            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Datenbanktest erfolgreich",
                    "message": message,
                    "sticky": False,
                },
            }

    def set_priority(self):
        # Ensure only one record is selected
        if len(self) != 1:
            raise ValidationError("Bitte nur eine Datenbank verwenden.")

        # Set all records' priority to False
        self.search([]).write({"priority": False})

        # Set the selected record's priority to True
        self.write({"priority": True})

        return True
