{
    "name": "Mail Server Filter",
    "summary": """
        Filter outgoing and incoming mail server by database name.
    """,
    "author": "Mint System GmbH",
    "website": "https://github.com/OCA/sale-workflow",
    "category": "Technical",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["mail"],
    "data": ["views/ir_mail_server.xml", "views/fetchmail_server.xml"],
    "installable": True,
    "application": False,
    "auto_install": False,
    "images": ["images/screen.png"],
}
