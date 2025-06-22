import logging
import re

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError

class MrpProduction(models.Model):
    _inherit = 'mrp.production'


    stock_move_line_ids = fields.One2many('stock.move.line', 'raw_material_production_id', 'Operations2')
    check_operation_type = fields.Char(compute="_check_operation")


    def _check_operation(self):
        """
        เช็คว่า document MO มี picking_type == mrp_operation หรือไม่
        """
        for rec in self:
            check_operation_type = False
            if rec.picking_type_id:
                if rec.picking_type_id.code == "mrp_operation":
                    check_operation_type = "mrp_operation"
            else :
                check_operation_type = False
            rec.check_operation_type = check_operation_type


