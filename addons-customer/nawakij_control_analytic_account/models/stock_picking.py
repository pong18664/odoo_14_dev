import logging
import re
import json

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError

_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'


    def _custom_get_analytic_account(self):
        """
        function สำหรับกําหนด analytic account
        โดยการนำค่า analytic_account_id จาก document ก่อนหน้ามาใส่
        """
        for rec in self:
            if rec.backorder_id:
                stock_picking = self.env['stock.picking'].search([('id', '=', rec.backorder_id.id)])
                rec.analytic_account_id = stock_picking.analytic_account_id
            elif rec.origin:
                po = self.env['purchase.order'].search([('name', '=', rec.origin)])
                stock_picking = self.env['stock.picking'].search([('name', '=', rec.origin)])
                if po:
                    rec.analytic_account_id = po.analytic_account_id
                elif stock_picking:
                    rec.analytic_account_id = stock_picking.analytic_account_id


    @api.model
    def create(self, vals):
        """
        เพิ่มการเรียกใช้ function
        """
        picking_vals = super(StockPicking, self).create(vals)
        picking_vals._custom_get_analytic_account() # เรียกใช้ function
        return picking_vals


