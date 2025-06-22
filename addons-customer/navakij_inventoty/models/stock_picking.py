import logging
import re
import json

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError

_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'


    check_operation_type = fields.Char(compute="_check_operation")
    srm_count = fields.Integer(string="SRM" ,compute="get_srm_count")
    check_state_srm = fields.Selection([
        ('state draft', 'Draft'),
        ('state waiting', 'Waiting'),
        ('state ready', 'Ready'),
    ], string='Check Status', defualt=False ,compute='_check_state_srm')
    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account")
    count_po = fields.Integer(string="PO", compute="_custom_get_po_count", default=0)


    def _custom_get_po_count(self):
        """
        function สำหรับนับจํานวน PO
        """
        for rec in self:
            rec.count_po = len(rec.purchase_id) if rec.purchase_id else 0


    def custom_action_to_tree_view_po(self):
        """
        ฟังก์ชันสําหรับพาไปหน้า tree view ของ PO
        """
        action = self.env["ir.actions.actions"]._for_xml_id("purchase.purchase_rfq")
        action['domain'] = [
            ('name', '=', self.origin)
            ]
        return action


    def _check_state_srm(self):
        """
        สำหรับกำหนดค่าให้กับ field check_state_srm
        """
        srm_data = self.env['stock.picking'].search([("origin", "=", self.name)])
        if any(rec.state == 'draft' for rec in srm_data):
            self.check_state_srm = 'state draft'
        elif any(rec.state == 'confirmed' for rec in srm_data):
            self.check_state_srm = 'state waiting'
        elif any(rec.state == 'assigned' for rec in srm_data):
            self.check_state_srm = 'state ready'
        else:
            self.check_state_srm = False


    def update_state(self):
        """
        สำหรับเรียกใช้ function action_confirm , action_assign , button_validate
        ตามแต่ละ state
        """
        srm_data = self.env['stock.picking'].search([("origin", "=", self.name)])
        # immediate_transfer_model = self.env['stock.immediate.transfer']
        if any(rec.state == 'draft' for rec in srm_data):
            srm_data.action_confirm()
        elif any(rec.state == 'confirmed' for rec in srm_data):
            srm_data.action_assign()
            for line in srm_data.move_line_ids_without_package:
                line.location_id = srm_data.location_id
        elif any(rec.state == 'assigned' for rec in srm_data):
            for line in srm_data.move_line_ids_without_package:
                if line.qty_done == 0:
                    line.qty_done = line.product_uom_qty
            for rec in srm_data:
                rec.button_validate() 
           

    def get_srm_count(self):
        """
        หาค่าของ field origin ของ stock.picking ที่ตรงกับ field name ของ stock.picking 
        """
        self.srm_count = len(self.env['stock.picking'].search([("origin", "=", self.name)]))

    
    def action_view_stock_picking(self):
        """
        เป็น function action พาเปลี่ยนหน้าไปตามที่ระบุ external id ไว้ และแสดงข้อมูลตามเงื่อนไขที่กำหนดไว้ที่ domain 
        ค่าของ field origin ของ stock.picking ที่ตรงกับ field name ของ stock.picking
        """
        action = self.env["ir.actions.actions"]._for_xml_id("stock.stock_picking_action_picking_type")
        action['domain'] = [("origin", "=", self.name)]
        return action


    def _check_operation(self):
        """
        เช็คว่า Document นี้ picking_type_id.code == "incoming" หรือไม่
        """
        for rec in self:
            check_operation_type = False
            if rec.picking_type_id:
                if rec.picking_type_id.code == "incoming":
                    check_operation_type = "incoming"
            else :
                check_operation_type = False
            rec.check_operation_type = check_operation_type


    @api.onchange('location_dest_id')
    def check_location(self):
        """
        สำหรับกำหนดค่าให้ field show_location เป็น True หรือ False ตามแต่ละ condition 
        """
        if self.location_dest_id:
            stock_location = self.env['stock.location'].search([])
            location_dest_name = self.location_dest_id.complete_name.split('/')

            for location in stock_location:
                location_name = location.complete_name.split('/')
                if len(location_dest_name) == 1:
                    if location_dest_name[0] in location_name[0]:
                        location.show_location = True
                    else:
                        location.show_location = False
                elif len(location_dest_name) == 2:
                    if location_dest_name[0] in location.complete_name and location_dest_name[1] in location.complete_name:
                        location.show_location = True
                    else:
                        location.show_location = False
                elif len(location_dest_name) >= 3:
                    if location_dest_name[2] in location.complete_name:
                        location.show_location = True
                    else:
                        location.show_location = False


    def new_create_stock_picking(self):
        """
        function สำหรับสร้างเอกสาร SRM2 จากเอกสาร SRM โดยมีเงื่อนไขแยกแต่ละ location
        """
        # condition สําหรับการสร้าง SRM 
        if self.picking_type_id.name == 'Store Raw Materials' and self.state == 'done':
            picking_type = self.env['stock.picking.type'].search([('name', '=', 'SRM 2')])
            source_location = self.location_dest_id.id
            processed_locations = set()  # เก็บเพื่อตรวจสอบ location_ids ที่ถูกประมวลผลแล้ว
            for stock_move in self.move_ids_without_package:
                # ตรวจสอบว่า location_ids ได้ถูกประมวลผลไปแล้วหรือยัง
                location_ids_hashable = frozenset(stock_move.location_ids.ids)
                if location_ids_hashable in processed_locations:
                    continue  # ถ้าถูกประมวลผลไปแล้วให้ข้ามรายการนี้
                new_srm = self.env['stock.picking'].create({
                    'location_id': source_location,
                    'location_dest_id': stock_move.location_ids[0].id if stock_move.location_ids else False,
                    # 'picking_type_id': self.picking_type_id.id,
                    'picking_type_id': picking_type.id,
                    'origin': self.name,
                })
                for move in self.move_ids_without_package.filtered(lambda x: frozenset(x.location_ids.ids) == location_ids_hashable):
                    new_line = self.env['stock.move'].create({
                        'product_id': move.product_id.id,
                        'name': move.name,
                        'product_uom': move.product_uom.id,
                        'product_uom_qty': move.product_uom_qty,
                        'picking_id': new_srm.id,
                        'location_id': self.location_dest_id.id,
                        'location_dest_id': move.location_ids.id,
                    })
                processed_locations.add(location_ids_hashable)
            return {
                'name': 'New Stock Picking',
                'view_mode': 'form',
                'res_model': 'stock.picking',
                'res_id': new_srm.id,
                'view_id': False,
                'type': 'ir.actions.act_window',
            }

         
    def button_validate(self):
        """
        เพิ่ม condition สำหรับการเรียกใช้ function new_create_stock_picking()
        """
        picking = super(StockPicking, self).button_validate()
        if self.picking_type_id.name == 'Store Raw Materials' and self.move_ids_without_package.location_ids:
            self.new_create_stock_picking()
        return picking 


    @api.model
    def create(self, vals):
        """
        เพิ่มการเรียกใช้ function
        """
        picking = super(StockPicking, self).create(vals)
        picking.check_location() # เรียกใช้ function
        return picking     


                              