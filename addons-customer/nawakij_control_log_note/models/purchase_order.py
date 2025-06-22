import logging
import re

from odoo import api, fields, models, SUPERUSER_ID, _ 
from odoo.exceptions import AccessError, UserError, ValidationError

_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'


    def write(self, vals):
        """ตรวจสอบการเปลี่ยนแปลงใน order_line และบันทึกใน Chatter"""
        for order in self:
            if 'order_line' in vals:
                messages = []
                for command in vals['order_line']:
                    if command[0] in [1, 4]:  # อัปเดตหรือเชื่อมโยงข้อมูล
                        line_id = command[1]  # ID ของ order_line
                        new_vals = command[2]  # ค่าที่ถูกเปลี่ยนแปลง

                        changes = []
                        line = self.env['purchase.order.line'].browse(line_id)

                        if new_vals:
                            if 'product_qty' in new_vals:
                                old_quantity = line.product_qty
                                new_quantity = new_vals['product_qty']
                                if old_quantity != new_quantity:
                                    changes.append(f"   - quantity: {old_quantity:.2f} → {new_quantity:.2f}<br/>")
                            if 'price_unit' in new_vals:
                                old_price = line.price_unit
                                new_price = new_vals['price_unit']
                                if old_price != new_price:
                                    changes.append(f"   - price unit: {old_price:.2f} → {new_price:.2f}<br/>")
                            if 'p_quantity' in new_vals:
                                old_p_quantity = line.p_quantity
                                new_p_quantity = new_vals['p_quantity']
                                if old_p_quantity != new_p_quantity:
                                    changes.append(f"   - p quantity: {old_p_quantity:.2f} → {new_p_quantity:.2f}<br/>")
                            if 'density' in new_vals:
                                old_density = line.density
                                new_density = new_vals['density']
                                if old_density != new_density:
                                    changes.append(f"- density: {old_density:.2f} → {new_density:.2f}<br/>")

                        if changes:
                            message = f"product name: {line.product_id.display_name}<br/>" + "".join(changes)
                            messages.append(message)

                if messages:
                    final_message = "<br/>".join(messages)
                    order.message_post(body=final_message)

        return super(PurchaseOrder, self).write(vals)




