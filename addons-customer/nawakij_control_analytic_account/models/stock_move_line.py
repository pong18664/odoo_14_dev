import logging
import re

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError

_logger = logging.getLogger(__name__)

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'


    def _custom_get_analytic_account(self):
        """
        function กำหนด Analytic Account ให้เป็น Analytic Account ของ Picking
        """
        for line in self:
            if line.picking_id.analytic_account_id:
                line.analytic_account_id = line.picking_id.analytic_account_id

                          
    @api.model
    def create(self, vals):
        """
        เพิ่มการเรียกใช้ function
        """
        stock_move_line_vals = super(StockMoveLine, self).create(vals)
        stock_move_line_vals._custom_get_analytic_account() # เรียกใช้ function
        return stock_move_line_vals