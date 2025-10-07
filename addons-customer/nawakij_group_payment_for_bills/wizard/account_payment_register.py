import re
import logging
_logger = logging.getLogger(__name__)

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'


    payment_difference = fields.Monetary(compute='_compute_payment_difference', digits=4)