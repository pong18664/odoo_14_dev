import re
import logging

from odoo import api, fields,tools, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError

_logger = logging.getLogger(__name__)

class MrpProduction(models.Model):
    _inherit = 'mrp.production'


    def write(self, vals):
        """ตรวจสอบการเปลี่ยนแปลงใน move_raw_ids และบันทึกใน Chatter"""
        for rec in self:
            if 'move_raw_ids' in vals:
                messages = []
                for command in vals['move_raw_ids']:
                    if command[0] in [1, 4]:  # อัปเดตหรือเชื่อมโยงข้อมูล
                        move_id = command[1]  # ID ของ stock.move
                        new_vals = command[2]  # ค่าที่ถูกเปลี่ยนแปลง

                        changes = []
                        move = self.env['stock.move'].browse(move_id)

                        if new_vals:
                            if 'product_uom_qty' in new_vals:
                                old_product_uom_qty = move.product_uom_qty
                                new_product_uom_qty = new_vals['product_uom_qty']
                                if old_product_uom_qty != new_product_uom_qty:
                                    changes.append(f"   - to consume: {old_product_uom_qty:.2f} → {new_product_uom_qty:.2f}<br/>"
                                                   f"   - consume per unit: {old_product_uom_qty:.2f} → {new_product_uom_qty:.2f}<br/>")
                            # if 'consume_per_unit' in new_vals:
                            #     old_consume_per_unit = move.product_uom_qty
                            #     new_consume_per_unit = new_vals['product_uom_qty']
                            #     if old_consume_per_unit != new_consume_per_unit:
                            #         changes.append(f"   - consume per unit: {old_consume_per_unit:.2f} → {new_consume_per_unit:.2f}<br/>")

                        if changes:
                            message = f"product name: {move.product_id.display_name}<br/>" + "".join(changes)
                            messages.append(message)

                if messages:
                    final_message = "<br/>".join(messages)
                    rec.message_post(body=final_message)

        return super(MrpProduction, self).write(vals)   