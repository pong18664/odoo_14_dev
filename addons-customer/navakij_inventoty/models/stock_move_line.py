import logging
import re

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'


    raw_material_production_id = fields.Many2one('mrp.production', related='move_id.raw_material_production_id')
    consume_per_unit = fields.Float(string="Consume Per Unit", related="move_id.consume_per_unit")
    custom_location_id = fields.Many2one('stock.location', string="Location")
    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account", readonly=False)


    @api.onchange('custom_location_id')
    def _onchange_custom_location_id(self):
        """
        ถ้า custom_location_id มีการเปลี่ยนแปลง 
        ให้ update location_ids ใน move_id ด้วย
        """
        for line in self:
            if line.custom_location_id:
                line.move_id.location_ids = line.custom_location_id.id
            else:
                line.move_id.location_ids = False    


    def compute_qty_done(self):
        """
        ส่วนของ Operation2
        Done = To Consume / Quantity To Produce
        """
        for move_line in self:
                move = move_line.move_id
                mrp = move_line.raw_material_production_id
                if mrp.product_qty:
                    move_line.qty_done = float(move.product_uom_qty) / float(mrp.product_qty)

                          
    @api.model
    def create(self, vals):
        """
        เพิ่มการเรียกใช้ function
        """
        product = super(StockMoveLine, self).create(vals)
        product.compute_qty_done() # เรียกใช้ function
        return product