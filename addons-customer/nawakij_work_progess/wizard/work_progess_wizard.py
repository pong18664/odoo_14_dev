import logging
import re

from odoo import api, fields,tools, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError

class WorkProgessWizard(models.Model):
    _name = 'work.progess.wizard'
    _description = 'Work Progess Wizard'


    product_id = fields.Many2one("product.product", string="Product", domain="[('invoice_ok', '=', True)]")
    product_line_ids = fields.One2many("work.progess.line.wizard", "work_progess_wizard_id", string="Product Lines")
    active = fields.Boolean(default=True)


    def action_confirm(self):
    # ฟังก์ชั่นสำหรับบันทึกข้อมูลจาก wizard ไปยังโมเดลปกติ

        # ค้นหา record ของ work.progess ที่ถูกเปิด wizard มาจาก
        work_progess = self.env['work.progess'].browse(self._context.get('active_id'))
        
        # ตรวจสอบ product_line_ids ที่ถูก select โดยใช้ check_box
        selected_lines = self.product_line_ids.filtered(lambda l: l.check_box)

        # ถ้าไม่มี product ใน item line ที่ถูก select ให้ raise error
        if not selected_lines:
            raise UserError(_("Please select a Product in item line."))

        # ทำการ write เฉพาะ product_line_ids ที่ถูก select
        for line in selected_lines:
            work_progess.line_ids.filtered(lambda l: l.product_id == line.product_id).write({
                'grouping_product_id': self.product_id.id if self.product_id else False
            })
        

    @api.model
    def default_get(self, fields_list):
        res = super(WorkProgessWizard, self).default_get(fields_list)
        work_progess = self.env['work.progess'].browse(self._context.get('active_id'))
        
        # ตรวจสอบว่า work_progess มีการบันทึก line_ids หรือไม่
        if work_progess and work_progess.line_ids:
            product_lines = []
            for line in work_progess.line_ids:
                product_lines.append((0, 0, {
                    'check_box': False,
                    'product_id': line.product_id.id,
                    'grouping_product_id': line.grouping_product_id.id
                }))
            res['product_line_ids'] = product_lines
        return res
    

    @api.model
    def archive_record(self):
        # ฟังก์ชั่นสำหรับลบ record ทิ้ง

        # ดึง record ที่เลือกจาก context
        record_id = self._context.get('active_id')
        # ลบ record ทิ้ง
        records = self.env['work.progess'].search([('id', '=', record_id)])
        # ตั้งค่า active เป็น False เพื่อ archive record
        records.write({'active': False})
        return True


class WorkProgessLineWizard(models.Model):
    _name = 'work.progess.line.wizard'
    _description = 'Work Progess Line Wizard'


    work_progess_wizard_id = fields.Many2one("work.progess.wizard", string="Work Progess Wizard")
    check_box = fields.Boolean(string="Select", default=False)
    product_id = fields.Many2one("product.product", string="Product")
    grouping_product_id = fields.Many2one("product.product", string="Grouping Product Name")
    active = fields.Boolean(default=True)


    @api.model
    def archive_record(self):
        # ฟังก์ชั่นสำหรับลบ record ทิ้ง

        # ดึง record ที่เลือกจาก context
        record_id = self._context.get('active_id')
        # ลบ record ทิ้ง
        records = self.env['work.progess'].search([('id', '=', record_id)])
        # ตั้งค่า active เป็น False เพื่อ archive record
        records.write({'active': False})
        return True