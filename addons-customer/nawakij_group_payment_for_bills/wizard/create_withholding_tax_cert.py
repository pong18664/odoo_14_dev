import re
import logging
_logger = logging.getLogger(__name__)

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class CreateWithholdingTaxCert(models.TransientModel):
    _inherit = "create.withholding.tax.cert"


    # def create_wt_cert(self):
    #     res = super(CreateWithholdingTaxCert, self).create_wt_cert()
    #     raise UserError(_(f"data: {res}"))
    #     return res
    

    def create_wt_cert_multi(self):
        res = super(CreateWithholdingTaxCert, self).create_wt_cert_multi()
        raise UserError(_(f"data: {res}"))
        return res



