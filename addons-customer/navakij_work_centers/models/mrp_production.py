import logging
import re

from odoo import api, fields,tools, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
# raise ValidationError(_(f"{workorder.check_yes_or_no}"))

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    check_state = fields.Boolean(string="State Work Order", compute="show_button_mark_as_done")

    def _cal_price(self, consumed_moves):
        """Set a price unit on the finished move according to `consumed_moves`.
        """
        super(MrpProduction, self)._cal_price(consumed_moves)
        work_center_cost = 0
        work_center_cost_sub_contract = 0
        finished_move = self.move_finished_ids.filtered(lambda x: x.product_id == self.product_id and x.state not in ('done', 'cancel') and x.quantity_done > 0)
        if finished_move:
            finished_move.ensure_one()
            for work_order in self.workorder_ids:
                time_lines = work_order.time_ids.filtered(lambda x: x.date_end and not x.cost_already_recorded)
                duration = sum(time_lines.mapped('duration'))
                time_lines.write({'cost_already_recorded': True})
                # codeเดิม
                # work_center_cost += (duration / 60.0) * work_order.workcenter_id.costs_hour

                # ส่วนที่เพิ่มเติม ถ้า field yes_or_no มีค่า == yes คำนวณตามสูตรใหม่ เก็บค่าไว้ใน work_center_cost_sub_contract
                if work_order.workcenter_id.yes_or_no == 'yes':
                    work_center_cost_sub_contract += work_order.subcontract_cost
                # ส่วนที่เพิ่มเติม ถ้า field yes_or_no มีค่า == no คำนวณตามสูตรเดิม เก็บค่าไว้ใน work_center_cost
                if work_order.workcenter_id.yes_or_no == 'no':
                    work_center_cost += (work_order.duration / 60.0) * work_order.workcenter_id.costs_hour
            # ส่วนที่เพิ่มเติม 
            total_work_center_cost = work_center_cost_sub_contract + work_center_cost

            if finished_move.product_id.cost_method in ('fifo', 'average'):
                qty_done = finished_move.product_uom._compute_quantity(finished_move.quantity_done, finished_move.product_id.uom_id)
                extra_cost = self.extra_cost * qty_done
                finished_move.price_unit = (sum([-m.stock_valuation_layer_ids.value for m in consumed_moves.sudo()]) + total_work_center_cost + extra_cost) / qty_done
        # raise ValidationError(_(f"{finished_move.price_unit}"))
        return True

    # function สำหรับโชว์ปุ่ม mark as done ถ้า condition ถูกต้อง ค่าเป็น True = show button ถ้าค่าเป็น False = hide button
    @api.depends('state', 'reservation_state', 'workorder_ids', 'workorder_ids.state', 'qty_producing')
    def show_button_mark_as_done(self):
        for rec in self:
            state_mo = False
            if rec.workorder_ids:
                if rec.qty_producing > 0 and rec.state in ['progress', 'to_close'] and rec.reservation_state == 'assigned' and all(wo_line.state == 'done' for wo_line in rec.workorder_ids):
                    state_mo = True
            else:
                if rec.qty_producing > 0 and rec.state in ['progress', 'to_close'] and rec.reservation_state == 'assigned':
                    state_mo = True
            rec.check_state = state_mo    
        # raise ValidationError(_(f"{rec.check_state}"))

