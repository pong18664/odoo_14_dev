import logging
import re

from datetime import datetime, timedelta
from odoo import api, fields, tools, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
# raise ValidationError(_(""))
_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"


    invoice_ok = fields.Boolean(string='Group Invoiced', default=False)
    