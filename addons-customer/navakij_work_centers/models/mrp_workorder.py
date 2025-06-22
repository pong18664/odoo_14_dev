import logging
import re

from odoo import api, fields,tools, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'
 
    subcontract_cost = fields.Integer(string="Subcontract Cost")
    check_yes_or_no = fields.Boolean(string='Check Yes or No', compute='_compute_check_yes_or_no')
    

    # function เช็คค่าของ field yes_or_no ถ้า field yes_or_no == 'yes' ค่า field check_yes_or_no = True
    @api.depends('workcenter_id.yes_or_no')
    def _compute_check_yes_or_no(self):
        for rec in self:
            rec.check_yes_or_no = any(workcenter.yes_or_no == 'yes' for workcenter in rec.workcenter_id)
        # raise ValidationError(_(f"{workorder.check_yes_or_no}"))


    # เพิ่ม condition ถ้า field reservation_state == 'assigned' function นี้ถึงจะทำงาน
    # def button_start(self):
    #     if self.production_id.reservation_state == 'assigned':
    #         super(MrpWorkorder, self).button_start()
    


