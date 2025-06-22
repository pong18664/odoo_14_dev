import logging
import re

from odoo import api, fields,tools, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError


class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'
 
    salary_per_month = fields.Integer(string="Salary per month")
    yes_or_no = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')],
        string='Subcontract Cost',
        default='no',
    )

    # function คำนวณหาค่า field costs_hour(ค่าแรงต่อ ช.ม) จาก field salary_per_month
    @api.onchange('salary_per_month','resource_calendar_id')
    def compute_costs_hour(self):
        for workcenter in self:
            time_work_total = workcenter.resource_calendar_id.time_work_total
            if workcenter.salary_per_month:
                workcenter.costs_hour = (workcenter.salary_per_month / 4.0) / float(time_work_total)


