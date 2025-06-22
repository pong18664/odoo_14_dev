{
    "name": "nawakij inventory",
    "summary": "Customization for inventory",
    "version": "14.0",
    "author": "Ashva Consulting",
    "category": "Stock",
    "license": "AGPL-3",
    "depends": [
        "account",
        "sale",
        "stock",
        "mrp",
    ],
    "data": [
        'views/stock_picking_view.xml',
        'views/mrp_production_view.xml',
        'views/stock_location_view.xml',
        'views/stock_move_view.xml',
        'views/stock_move_line_view.xml',
        # 'views/product_product_view.xml',
   ],
    "installable": True,
    'application': True,
}