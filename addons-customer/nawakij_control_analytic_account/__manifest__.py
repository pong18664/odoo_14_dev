{
    "name": "nawakij control analytic account",
    "summary": "Customization for control analytic account",
    "version": "14.0",
    "author": "Ashva Consulting",
    "category": "Control Analytic Account",
    "license": "AGPL-3",
    "depends": [
        "stock",
        "account",
        "mrp",
        "navakij_inventoty",
        "purchase_order",
    ],
    "data": [
        "views/stock_picking_view.xml",
        "views/account_move_view.xml",
        "views/purchase_order_view.xml",
        "views/sale_order_view.xml",
   ],
    "installable": True,
    'application': True,
}