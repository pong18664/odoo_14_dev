import logging
import re

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError

class StockMove(models.Model):
    _inherit = 'stock.move'


    consume_per_unit = fields.Float(string="Consume Per Unit", compute="_compute_quantity_done_and_consume_per_unit")
    location_ids = fields.Many2one('stock.location', string="Location", domain=[('show_location', '=', True)])
    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account", readonly=False)

 
    @api.depends("raw_material_production_id.product_qty")
    @api.onchange("raw_material_production_id.product_qty")
    def _compute_quantity_done_and_consume_per_unit(self):
        """
        ส่วนของ Page Components 
        คำนวณ Consume Per Unit = To Consume / Quantity To Produce
        """
        for move in self:
            for mrp in move.raw_material_production_id:
                if move.raw_material_production_id:
                    move.consume_per_unit = float(move.product_uom_qty) / float(mrp.product_qty) 