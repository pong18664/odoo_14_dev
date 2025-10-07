import re
import logging
_logger = logging.getLogger(__name__)

from odoo import api, fields,tools, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'


    debit = fields.Monetary(string='Debit', default=0.0000, currency_field='company_currency_id', digits=(16, 4))
    credit = fields.Monetary(string='Credit', default=0.0000, currency_field='company_currency_id', digits=(16, 4))