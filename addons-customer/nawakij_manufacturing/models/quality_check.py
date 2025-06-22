import logging
import re

from odoo import api, fields,tools, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
# raise ValidationError(_(f"{workorder.check_yes_or_no}"))


class QualityCheck(models.Model):
    _inherit = 'quality.check'


    @api.model
    def create(self, vals):
        res = super(QualityCheck, self).create(vals)
        res._update_production_state_qc()
        return res


    def write(self, vals):
        res = super(QualityCheck, self).write(vals)
        self._update_production_state_qc()
        return res


    def _update_production_state_qc(self):
        for rec in self:
            if rec.production_id:
                production = rec.production_id
                qc_passed = self.search([
                    ('production_id', '=', production.id),
                    ('quality_state', '=', 'pass')
                ], limit=1)
                if qc_passed:
                    production.state_qc = True
                else:
                    production.state_qc = False