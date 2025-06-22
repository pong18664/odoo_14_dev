import logging
import re

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'


    def _custom_get_analytic_account(self):
        """
        function สำหรับกำหนดค่า field analytic_account_id
        """
        for move in self:
            if move.stock_move_id:
                move.analytic_account_id = move.stock_move_id.analytic_account_id


    def _custom_update_analytic_account_in_line_ids(self):
        """
        function สำหรับ update ค่า field analytic_account_id ให้กับ account.move.line
        """
        for move in self:
            for line in move.line_ids:
                if move.line_ids and move.analytic_account_id:
                    line.analytic_account_id = move.analytic_account_id


    @api.model_create_multi
    def create(self, vals_list):
        """
        เพิ่มการเรียกใช้ function
        """
        account_move_vals = super(AccountMove, self).create(vals_list)
        account_move_vals._custom_get_analytic_account() # เรียกใช้ finction
        account_move_vals._custom_update_analytic_account_in_line_ids() # เรียกใช้ finction
        return account_move_vals