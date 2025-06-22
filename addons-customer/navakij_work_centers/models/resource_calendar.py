import logging
import re

from odoo import api, fields,tools, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    time_work_total = fields.Float(string="Time Work Total", compute="_compute_time_work_total")
 

    # function คำนวณหา ช.ม. ทำงาน
    def _compute_time_work_total(self):
        for rec in self:
            time_work_total = 0
            for line in rec.attendance_ids:
                if line.hour_to and line.hour_from:
                    time_work_total += line.hour_to - line.hour_from
            rec.time_work_total = time_work_total
