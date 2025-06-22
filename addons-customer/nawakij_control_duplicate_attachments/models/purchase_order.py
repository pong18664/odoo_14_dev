import logging
import re

from odoo import api, fields, models, SUPERUSER_ID, _ 
from odoo.exceptions import AccessError, UserError, ValidationError

_logger = logging.getLogger(__name__)

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'


    def copy(self, default=None):
        """
        เพิ่มเติมการ duplicate attachments
        """
        ctx = dict(self.env.context)
        ctx.pop('default_product_id', None)
        self = self.with_context(ctx)
        new_po = super(PurchaseOrder, self).copy(default=default)
        for line in new_po.order_line:
            if line.product_id:
                seller = line.product_id._select_seller(
                    partner_id=line.partner_id, quantity=line.product_qty,
                    date=line.order_id.date_order and line.order_id.date_order.date(), uom_id=line.product_uom)
                line.date_planned = line._get_date_planned(seller)

        # ดึง Attachments ที่เกี่ยวข้องกับ PO นี้
        attachments = self.env['ir.attachment'].search([
            ('res_model', '=', 'purchase.order'),
            ('res_id', '=', self.id)
        ])

        # คัดลอก Attachments ไปยัง PO ใหม่
        for attachment in attachments:
            attachment.copy({
                'res_id': new_po.id,  # เปลี่ยนให้เป็น PO ใหม่
            })

        return new_po

