import logging
import re

from itertools import groupby
from odoo import api, fields, models, SUPERUSER_ID, _ 
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.float_utils import float_is_zero

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    analytic_account_id = fields.Many2one('account.analytic.account',string='Analytic Account')
    internal_detail = fields.Char(string="Internal Detail", index=True)
    check_by_id = fields.Many2one('res.users', string='Check By', index=True, readonly=True, copy=False)
    approve_1_by_id = fields.Many2one('res.users', string='Approve 1 By', index=True, readonly=True, copy=False)
    approve_2_by_id = fields.Many2one('res.users', string='Approve 2 By', index=True, readonly=True, copy=False)
    hide_check_1 = fields.Boolean(string="Hide Check 1", compute='hide_button', default=False)
    hide_check_2 = fields.Boolean(string="Hide Check 2", compute='hide_button', default=True)
    hide_check_3 = fields.Boolean(string="Hide Check 3", compute='hide_button', default=True)
    check_config_po = fields.Boolean(string="Check Confic PO", compute='compute_check_config_po', default=False)
    delivery_address = fields.Char(string="Delivery Address")


    def button_draft(self):
        """
        ฟังก์ชันสําหรับกดปุ่ม reset to draft
        เสริมส่วนทำให้ check_by_id, approve_1_by_id, approve_2_by_id = False
        """
        rec = super(PurchaseOrder, self).button_draft()
        self.check_by_id = False
        self.approve_1_by_id = False
        self.approve_2_by_id = False
        return rec


    def button_confirm(self):
        """
        เสริมส่วนเช็คชื่อผู้ตรวจสอบ PO ก่อน confirm
        """
        rec = super(PurchaseOrder, self).button_confirm()
        if self.check_config_po:
            if not self.check_by_id:
                raise UserError("ยังไม่ได้กดปุ่ม Check 1")
            elif not self.approve_1_by_id:
                raise UserError("ยังไม่ได้กดปุ่ม Check 2")
            elif not self.approve_2_by_id:
                raise UserError("ยังไม่ได้กดปุ่ม Check 3")
        else:
            if not self.check_by_id:
                raise UserError("ยังไม่ได้กดปุ่ม Check 1")
            elif not self.approve_1_by_id:
                raise UserError("ยังไม่ได้กดปุ่ม Check 2")
        return rec
    
    
    @api.onchange('check_config_po','check_by_id','approve_1_by_id','approve_2_by_id')
    def hide_button(self):
        """
        ฟังชั่นสำหรับกำหนดค่า True หรือ False ให้กับ field hide_check_1, hide_check_2, hide_check_3
        เพื่อควบคุมการแสดง/ซ่อนปุ่ม Check 1, Check 2, Check 3
        """
        for rec in self:
            if rec.check_config_po: # ค่า amount_total มากกว่า ค่าที่กำหนด
                rec.hide_check_1 = True if rec.check_by_id else False   # True ซ่อน / False แสดง
                rec.hide_check_2 = False if rec.check_by_id and not rec.approve_1_by_id else True   # True ซ่อน / False แสดง
                rec.hide_check_3 = False if rec.check_by_id and rec.approve_1_by_id and not rec.approve_2_by_id else True   # True ซ่อน / False แสดง
            else:
                rec.hide_check_1 = True if rec.check_by_id else False   # True ซ่อน / False แสดง
                rec.hide_check_2 = False if rec.check_by_id and not rec.approve_1_by_id else True   # True ซ่อน / False แสดง
                rec.hide_check_3 = True # True ซ่อน / False แสดง 


    @api.onchange('amount_total')
    def compute_check_config_po(self):
        """
        ฟังชั่นสําหรับกำหนดค่า True หรือ False ให้กับ field check_config_po
        field check_config_po 
            - ถ้าเป็น True แสดงว่าค่า amount_total มากกว่า ค่า config.po_double_validation_amount
            - ถ้าเป็น False แสดงว่าค่า amount_total ไม่มากกว่า ค่า config.po_double_validation_amount
        """
        po_double_validation = self.env.company.po_double_validation 
        po_double_validation_amount = self.env.company.po_double_validation_amount
        for rec in self:
            if po_double_validation == 'two_step':
                if rec.amount_total > po_double_validation_amount:
                    rec.check_config_po = True
                else:
                    rec.check_config_po = False
            else:
                rec.check_config_po = False


    def button_check_1(self):
        """
        ฟังก์ชันสําหรับดึงชื่อ user ที่กำลังใช้งานใส่ใน field check_by_id
        """
        group = self.env['res.groups'].search([('name', '=', 'Authorized sign-off personnel lv1')])
        
        for rec in self:
            # ตรวจสอบว่าผู้ใช้ปัจจุบันมีสิทธิ์อยู่ในกลุ่มหรือไม่
            if self.env.user not in group.users:
                raise UserError("ไม่สามารถลงชื่อตรวจสอบได้")
            
            rec.check_by_id = self.env.user


    def button_approve_1(self):
        """
        ฟังก์ชันสําหรับดึงชื่อ user ที่กำลังใช้งานใส่ใน field approve_1_by_id
        """
        group = self.env['res.groups'].search([('name', '=', 'Authorized sign-off personnel lv2')])
        
        for rec in self:
            # ตรวจสอบว่าผู้ใช้ปัจจุบันมีสิทธิ์อยู่ในกลุ่มหรือไม่
            if self.env.user not in group.users:
                raise UserError("ไม่สามารถลงชื่อตรวจสอบได้")
            
            # ตรวจสอบว่าชื่อซ้ำกับผู้จัดทำหรือไม่
            if self.env.user == rec.check_by_id: 
                raise UserError("ชื่อซ้ำกับผู้จัดทำ")
            
            # หากผ่านการตรวจสอบทั้งหมด ให้อัปเดต field approve_1_by_id
            rec.approve_1_by_id = self.env.user


    def button_approve_2(self):
        """
        ฟังก์ชันสําหรับดึงชื่อ user ที่กำลังใช้งานใส่ใน field approve_2_by_id
        """
        group = self.env['res.groups'].search([('name', '=', 'Authorized sign-off personnel lv3')])

        for rec in self:
            # ตรวจสอบว่าผู้ใช้ปัจจุบันมีสิทธิ์อยู่ในกลุ่มหรือไม่
            if self.env.user not in group.users:
                raise UserError("ไม่สามารถลงชื่อตรวจสอบได้")
            
            # ตรวจสอบว่าชื่อซ้ำกับผู้จัดทำหรือไม่
            if self.env.user == rec.check_by_id: 
                raise UserError("ชื่อซ้ำกับผู้จัดทำ")
            
            # ตรวจสอบว่าชื่อซ้ำกับผู้ตรวจสอบหรือไม่
            if self.env.user == rec.approve_1_by_id:
                raise UserError("ชื่อซ้ำกับผู้ตรวจสอบ")
            
            rec.approve_2_by_id = self.env.user


    def button_update_tender(self): 
        for order in self:
            for line in order.order_line:
                line.get_data_product()


    @api.onchange('analytic_account_id')
    def onchange_analytic_account(self):
        """
        เป็น Function กำหนดค่าให้กับ field account_analytic_id ใน purchase.order.line
        """
        for order in self:
            for line in order.order_line:
                line.account_analytic_id = order.analytic_account_id
    
 
    def select_create_purchase(self):
        """
        เป็น Function สร้าง PO ใหม่จากการเลือกหลาย PO
        แล้วนำมารวมกันสร้างเป็น PO ใหม่
        """
        # ตรวจสอบว่ามี PO ที่ถูกเลือกอยู่หรือไม่
        if not self:
            return

        # ตรวจสอบว่ามี Vendor เดียวกันหรือไม่
        vendors = self.mapped('partner_id')
        if len(vendors) > 1:
            raise ValueError("Selected Purchase Orders must have the same vendor.")

        # สร้าง PO ใหม่
        new_po = self.env['purchase.order'].create({
            'partner_id': vendors.id,  # Vendor เดียวกันสำหรับทุก PO
            'date_order': fields.Date.today(),
            'origin': ', '.join(po_data.name for po_data in sorted(self, key=lambda po: po.name)),
        })

        # Dictionary เพื่อเก็บ Product ที่เคยเพิ่มเข้าไปและ Quantity ที่บวกรวม
        product_dict = {}

        # เพิ่มรายการจาก PO ที่ถูกเลือก
        for po_data in self:
            for line in po_data.order_line:
                if line.product_id in product_dict:
                    # หาก Product นี้มีอยู่ใน Dictionary แล้ว
                    # นำ Quantity มาบวกรวมกัน
                    product_dict[line.product_id] += line.product_qty
                else:
                    # หาก Product นี้ยังไม่มีอยู่ใน Dictionary
                    # เพิ่มเข้า Dictionary และกำหนดค่า Quantity
                    product_dict[line.product_id] = line.product_qty

        # เพิ่มรายการใน Purchase Order ใหม่
        for product, qty in product_dict.items():
            new_line = new_po.order_line.create({
                'product_id': product.id,
                'product_qty': qty,
                'name': product.name,
                'price_unit': product.list_price,
                'order_id': new_po.id,
            })

        return {
            'name': 'New Purchase Order',
            'view_mode': 'form',
            'res_model': 'purchase.order',
            'res_id': new_po.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
        }


    @api.onchange('partner_id')
    def _get_purchase_line(self):
        """
        เป็น Function เมื่อ field partner_id ใน purchase.order มีการเปลี่ยนแปลง
        ให้เรียกใช้ function _get_product_name() และ _onchange_quantity()
        """
        for rec in self:
            if rec.order_line:
                for line in rec.order_line:
                    line._get_product_name()
                    line._onchange_quantity()


    @api.model
    def create(self, vals):
        product = super(PurchaseOrder, self).create(vals)
        return product
