import logging
import re

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"


    quantity_to_receive = fields.Float(
        string="Quantity to Receive",
        digits=(0, 2),
        help="The quantity of the product that should be received.",
    )
    

    def _compute_quantity_to_receive(self):
        """
        function สำหรับคำนวน quantity_to_receive
        """
        for line in self:
            if line.product_uom_qty > 0:
                line.quantity_to_receive = line.product_uom_qty


    @api.model_create_multi
    def create(self, vals_list):
        res = super(StockMoveLine, self).create(vals_list)
        res._compute_quantity_to_receive() # เรียกใช้ function
        return res
    
