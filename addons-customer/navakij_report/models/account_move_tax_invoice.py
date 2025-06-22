import logging
import re

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)

class AccountMoveTaxInvoice(models.Model):
    _inherit = "account.move.tax.invoice"


    name = fields.Char(string="Tax Invoice Number", copy=False , related="tax_invoice_number")


