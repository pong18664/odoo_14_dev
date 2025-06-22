{
    "name": "nawakij account move",
    "summary": "Customization for account move",
    "version": "14.0",
    "author": "Ashva Consulting",
    "category": "Accounting",
    "license": "AGPL-3",
    "depends": [
        'base',
        'account',
        'nawakij_manufacturing'
    ],
    "data": [
        'security/ir.model.access.csv',
        "views/res_company_view.xml",
        "views/res_config_settings_view.xml",
        "views/account_move_view.xml",
        "views/account_move_retention_view.xml",
        'wizard/account_move_retention.xml',
   ],
    "installable": True,
    'application': True,
}