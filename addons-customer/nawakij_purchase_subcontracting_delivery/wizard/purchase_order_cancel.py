import logging
import re

from odoo import api, fields,tools, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError

class PurchaseOrderCancel(models.TransientModel):
    _inherit = 'purchase.order.cancel'


    def action_cancel(self):
        """
        Override function action_cancel
        เพิ่มการตรวจสอบว่า PO นี้มีการสร้างเอกสาร Delivery ไว้หรือไม่
        ถ้ามีให้ยกเลิกเอกสาร Delivery ที่ state ไม่ใช่ 'done' และ 'cancel' เหล่านั้นก่อนที่จะยกเลิก PO
        """
        res = super(PurchaseOrderCancel, self).action_cancel()
        for wizard in self:
            purchase_order = wizard.purchase_id
            delivery_orders = self.env['stock.picking'].search([
                ('origin', '=', purchase_order.name), 
                ('picking_type_id.code', '=', 'outgoing')
                ])
            if delivery_orders:
                for delivery in delivery_orders:
                    if delivery.state not in ['done', 'cancel']:
                        delivery.action_cancel()
        return res