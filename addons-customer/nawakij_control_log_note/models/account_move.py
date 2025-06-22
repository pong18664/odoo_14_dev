import re
import logging

from odoo import api, fields,tools, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'


    def write(self, vals):
        """ตรวจสอบการเปลี่ยนแปลงใน invoice_line_ids และบันทึกใน Chatter"""
        for rec in self:
            if 'invoice_line_ids' in vals:
                messages = []
                for command in vals['invoice_line_ids']:
                    if command[0] in [1, 4]:  # อัปเดตหรือเชื่อมโยงข้อมูล
                        line_id = command[1]  # ID ของ invoice_line_ids
                        new_vals = command[2]  # ค่าที่ถูกเปลี่ยนแปลง

                        changes = []
                        line = self.env['account.move.line'].browse(line_id)

                        if new_vals:
                            if 'quantity' in new_vals:
                                old_quantity = line.quantity
                                new_quantity = new_vals['quantity']
                                if old_quantity != new_quantity:
                                    changes.append(f"   - quantity: {old_quantity:.2f} → {new_quantity:.2f}<br/>")
                            if 'price_unit' in new_vals:
                                old_price = line.price_unit
                                new_price = new_vals['price_unit']
                                if old_price != new_price:
                                    changes.append(f"   - price unit: {old_price:.2f} → {new_price:.2f}<br/>")
                        if changes:
                            message = f"product name: {line.product_id.display_name}<br/>" + "".join(changes)
                            messages.append(message)

                if messages:
                    final_message = "<br/>".join(messages)
                    rec.message_post(body=final_message)

        return super(AccountMove, self).write(vals)