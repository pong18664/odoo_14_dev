import logging
import re

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = "res.company"


    journal_default_id = fields.Many2one(
        'account.journal',
        string='Default Journal',
        help="กำหนด Account Journal เริ่มต้มให้กับเอกสาร Retention"
    )
    debit_default_id = fields.Many2one(
        'account.account',
        string='Default Debit Account',
        help="กำหนด Account Debit เริ่มต้มให้กับเอกสาร Retention"
    )
    credit_default_id = fields.Many2one(
        'account.account',
        string='Default Credit Account',
        help="กำหนด Account Credit เริ่มต้มให้กับเอกสาร Retention"
    ) 