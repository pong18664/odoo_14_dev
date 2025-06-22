import logging
import re

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = "res.company"


    work_center_cost_account = fields.Many2one('account.account', string='Work Center Cost Account')
    work_center_cost_account_subcontract = fields.Many2one('account.account', string='Work Center Cost Account Subcontract')
    work_center_subcontract = fields.Many2one('account.account', string='Subcontract ช่างเหมา Work Center Cost Account')



