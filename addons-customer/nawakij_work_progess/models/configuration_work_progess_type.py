import logging
import re


from odoo import api, fields,tools, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError


class ConfigurationWorkProgessType(models.Model):
    _name = 'configuration.work.progess.type'
    _description = 'Configuration Work Progess Type'

    name_type = fields.Char(string='Type Name', required=False)
    percent = fields.Float(string='Percent %', required=False)
    project_ids = fields.Many2one('configuration.work.progess.project', string='Project')


    def name_get(self):
        # สร้าง result ว่าง
        result = []
        for record in self:
            # name = record.name_type
            name = record.name_type
            # นำ name ไปใส่ใน result
            result.append((record.id, name))
        return result
    

    