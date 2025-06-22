import re
import logging

from odoo import api, fields,tools, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError

_logger = logging.getLogger(__name__)

class MrpProduction(models.Model):
    _inherit = 'mrp.production'


    def copy(self, default=None):
        """
        เพิ่มเติมการ duplicate attachments
        """
        default = default or {}

        new_mo = super(MrpProduction, self).copy(default=default) # คัดลอกข้อมูล MO

        # ดึง Attachments ที่เกี่ยวข้องกับ MO นี้
        attachments = self.env['ir.attachment'].search([
            ('res_model', '=', 'mrp.production'),
            ('res_id', '=', self.id)
        ])

        # คัดลอก Attachments ไปยัง MO ใหม่
        for attachment in attachments:
            attachment.copy({
                'res_id': new_mo.id,  # เปลี่ยนให้เป็น MO ใหม่
            })

        return new_mo

