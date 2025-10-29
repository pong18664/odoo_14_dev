import re
import json
import logging
_logger = logging.getLogger(__name__)

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    po_type_subcontract = fields.Boolean(string="PO Type Subcontract", default=False)
    count_doc_delivery = fields.Integer(string="Count Doc Delivery", compute='_compute_count_doc_delivery', default=0, copy=False)


    def _compute_count_doc_delivery(self):
        """
        function นับจำนวนเอกสาร Delivery ที่สร้างขึ้นจาก PO นี้
        """
        for order in self:
            delivery_orders = self.env['stock.picking'].search([('origin', '=', order.name), ('picking_type_id.code', '=', 'outgoing')])
            order.count_doc_delivery = len(delivery_orders)


    def action_view_doc_delivery(self):
        """
        function เปิดหน้าต่างแสดงรายการ Delivery ที่สร้างขึ้นจาก PO นี้
        """
        self.ensure_one()
        delivery_orders = self.env['stock.picking'].search([('origin', '=', self.name), ('picking_type_id.code', '=', 'outgoing')])
        action = self.env.ref('stock.action_picking_tree_all').read()[0] #
        if len(delivery_orders) >= 1:
            action['domain'] = [('id', 'in', delivery_orders.ids)]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action


    def create_doc_delivery(self):
        """
        function สร้างเอกสาร Delivery เพื่อส่งวัตถุดิบไปยังผู้รับจ้างช่วง
        เงื่อนไข:
            - ตรวจสอบ order_line ว่ามีค่าไหม ถ้าไม่มีให้ return ออกไปเลย
            - ตรวจสอบ product ใน order line ว่า variant_bom_id มีค่าไหม
                - ถ้า condition นี้เป็น True ให้เก็บ bom_line ของ product เหล่านั้นไว้ใน list products_type_subcontract
        ขั้นตอนการสร้าง:
            - search operation type (Delivery) เก็บไว้ในตัวแปร operation_type
            - กําหนดต้นทาง/ปลายทาง
                - ต้นทาง = WH/Stock (operation_type.default_location_src_id)
                - ปลายทาง = 'Subcontracting Location' (search location ที่ name = 'Subcontracting Location' และ usage = 'internal')
            - เตรียมข้อมูลการสร้าง stock.picking เก็บไว้ใน picking_values
            - สร้าง stock.picking
            - เตรียมข้อมูลการสร้าง stock.move เก็บไว้ใน move_values
            - สร้าง stock.move
        """
        for order in self:
            if not order.order_line: # ไม่มี order line ใน PO ไม่ต้องทำอะไรให้ออกจาก function นี้
                return
            
            products_type_subcontract = [] # เก็บ product ที่มี BoM type = 'subcontract'
            for line in order.order_line:
                      
                if line.variant_bom_id: # ถ้า variant_bom_ids มีค่า
                    for product_component in line.variant_bom_id.bom_line_ids:
                        products_type_subcontract.append({
                            'product_id': product_component.product_id.id,
                            'display_name': product_component.product_id.display_name,
                            'qty': product_component.product_qty * line.product_qty,
                            'uom_id': product_component.product_uom_id.id,
                        })

            # ตรวจสอบ list products_type_subcontract ที่มี product_id ซ้ำกัน และรวม qty ของ product เหล่านั้น
            # temp_dict = {}
            # for item in products_type_subcontract:
            #     product_id = item['product_id']
            #     if product_id in temp_dict:
            #         temp_dict[product_id]['qty'] += item['qty']
            #     else:
            #         temp_dict[product_id] = item

            # search operation type (Delivery)
            operation_type = self.env['stock.picking.type'].search([
                ('name', '=', 'Delivery Orders'),
                ('sequence_code', '=', 'OUT'),
                ('warehouse_id', '=', order.picking_type_id.warehouse_id.id),
                ('code', '=', 'outgoing')
            ], limit=1)

            # กำหนดต้นทาง/ปลายทาง
            src_loc = operation_type.default_location_src_id # ต้นทาง = WH/Stock
            dest_loc = self.env['stock.location'].search([
                ('name', '=', 'Subcontracting Location'), 
                ('usage', '=', 'internal')], limit=1) # ปลายทาง = Subcontracting Location

            # เตรียมข้อมูลการสร้าง stock.picking
            picking_values = {
                'picking_type_id': operation_type.id or False,
                'location_id': src_loc.id if src_loc else False,
                'location_dest_id': dest_loc.id if dest_loc else False,
                'origin': order.name,
                'partner_id': order.partner_id.id,
                'move_type': 'direct',
                'company_id': order.company_id.id,
                'scheduled_date': fields.Datetime.now(),
                'analytic_account_id': order.analytic_account_id.id,
            }

            # สร้าง stock.picking
            picking = self.env['stock.picking'].create(picking_values)

            # เตรียมข้อมูลการสร้าง stock.move
            move_values = []
            for line in products_type_subcontract:
            # for line in temp_dict.values():
                move_values.append((0, 0, {
                    'product_id': line['product_id'],
                    'product_uom_qty': line['qty'],
                    'product_uom': line['uom_id'],
                    'picking_id': picking.id,
                    'reference': picking.name,
                    'location_id': src_loc.id,
                    'location_dest_id': dest_loc.id,
                    'name': line['display_name'],
                    'origin': order.name,
                }))

            # สร้าง stock.move
            picking.move_ids_without_package = move_values

            return picking


    def check_po_type_subcontract(self):
        """
        function สําหรับตรวจสอบ product ใน order_line ว่ามี BoM หรือไม่
        field variant_bom_id ไม่มีค่า = ไม่มี BoM
        และแจ้งเตือนรายการที่ไม่มี BoM
        """
        for order in self:
            if not order.po_type_subcontract:
                continue

            product_type_is_not_subcontract = [] # เก็บ product ที่ไม่มี BoM

            for line in order.order_line:
                if not line.variant_bom_id:
                    product_type_is_not_subcontract.append(line.product_id.display_name)

            if product_type_is_not_subcontract:
                unique_products = sorted(set(product_type_is_not_subcontract))
                product_list = "\n".join(f"- {name}" for name in unique_products)
                raise UserError(_("Check the BOM in the list.:\n%s") % product_list)

            order.create_doc_delivery()


    def button_confirm(self):
        """
        Override function button_confirm
        เพิ่มการเรียกใช้ function check_po_type_subcontract ก่อน confirm PO
        """
        self.check_po_type_subcontract()
        rec = super(PurchaseOrder, self).button_confirm()
        return rec
    
    
    @api.onchange('partner_id')
    def _get_variant_bom(self):
        """
        เรียกใช้ function _get_variant_bom() ใน purchase.order.line
        """
        for line in self.order_line:
            line._get_variant_bom()
            