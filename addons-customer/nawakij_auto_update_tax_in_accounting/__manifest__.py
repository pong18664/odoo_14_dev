{
    "name": "nawakij auto update tax in accounting",
    "summary": "Auto update tax in invoice line",
    "version": "14.0",
    "author": "Ashva Consulting",
    "category": "Accounting",
    "license": "AGPL-3",
    "depends": [
        "account",
    ],
    "data": [
        'security/ir.model.access.csv',
        'views/account_move_view.xml',
        'wizard/update_invoice_tax_wizard_view.xml',
    ],
    'images': ['static/description/icon.png'],
    "installable": True,
    'application': True,
}