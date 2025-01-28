{
    "name": "Base External Mssql",
    "summary": """
        Establish connection to external mssql database.
    """,
    "author": "Mint System GmbH",
    "website": "https://github.com/OCA/sale-workflow",
    "category": "Tools",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["base"],
    "data": ["security/ir.model.access.csv", "views/base_external_mssql.xml"],
    "application": False,
    "auto_install": False,
}
