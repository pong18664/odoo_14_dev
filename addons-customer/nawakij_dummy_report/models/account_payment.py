import logging
import re

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)

class AccountPayment(models.Model):
    _inherit = "account.payment"


    ref_payment_dummy = fields.Char(string="Ref Payment")


    def _get_ref_payment_dummy(self):
        pass

