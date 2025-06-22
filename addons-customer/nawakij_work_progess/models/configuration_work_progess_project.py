import logging
import re


from odoo import api, fields,tools, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError


class ConfigurationWorkProgessProject(models.Model):
    _name = 'configuration.work.progess.project'
    _description = 'Configuration Work Progess Project'


    name_project = fields.Char(string='Project Name', required=True)
    project_line = fields.One2many("configuration.work.progess.project.line", "project_ids", string="Project Line")
    sum_percent = fields.Float(string="Sum Percent", compute="compute_sum_percent")
    product_line_ids = fields.One2many("configuration.work.progess.project.line", "product_ids", string="Product Line")
    sale_order_id = fields.Many2one("sale.order", string="Sale Order", required=False)
    partner_ids = fields.Many2one("res.partner", string="Customer", required=True)
    count_sale_order = fields.Integer(string="Count Sale Order", compute="_compute_count_sale_order", store=True, default=0)
    sale_order_id = fields.Many2one("sale.order", string="Sale Order", required=False)


    @api.depends('sale_order_id.source_document')
    def _compute_count_sale_order(self):
        # ฟังชั่นสำหรับคำนวณจำนวน sale order
        for rec in self:
            sale_order = self.env['sale.order'].search([('source_document', 'ilike', rec.name_project)]) 
            rec.count_sale_order = len(sale_order) if sale_order else 0


    def action_view_sale_order(self):
        # ฟังชั่นสำหรับดู sale order
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_orders")
        action['domain'] = [('source_document', 'ilike', self.name_project)]
        return action


    def copy(self, default=None):
        default = dict(default or {})
        # เปลี่ยนชื่อโปรเจคใหม่เป็นชื่อเดิมพร้อมคำว่า " (copy)"
        default['name_project'] = self.name_project
        
        # คัดลอก project_line
        copied_project = super(ConfigurationWorkProgessProject, self).copy(default)

        # คัดลอก project_line และ product_line_ids มาในเรคคอร์ดใหม่
        for line in self.project_line:
            line.copy({
                'project_ids': copied_project.id,
            })

        for line in self.product_line_ids:
            line.copy({
                'product_ids': copied_project.id,
            })

        return copied_project


    def create_sale_order(self):
        # ฟังชั่นสร้าง sale order

        for rec in self:
            # สร้าง sale order
            sale_order = self.env['sale.order'].create({
                'partner_id': rec.partner_ids.id,
                'date_order': fields.Date.today(),
                'source_document': rec.name_project,
            })

            for line in rec.product_line_ids:
                # สร้าง sale order line
                self.env['sale.order.line'].create({
                    'order_id': sale_order.id,
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.qty,
                    'price_unit': line.unit_price,
                })

            # ตั้งค่าฟิลด์ sale_order_id ให้ถูกต้อง
            rec.write({'sale_order_id': sale_order.id})

        
    @api.depends('project_line')
    def compute_sum_percent(self):
        for rec in self:
            # field sum_percent = ผลรวมของค่า percent ของ project_line
            rec.sum_percent = sum(rec.project_line.mapped('percent'))
            # ถ้าผลรวมมากกว่า 100 ให้ raise error
            if rec.sum_percent > 100:
                raise UserError('The total percentage exceeds 100%.')


    def name_get(self):
        # สร้าง result ว่าง
        result = []
        for record in self:
            # ใช้ name_project เพื่อค้นหาจาก ID แทนการใช้ name_project
            name = record.name_project
            # นำ name ไปใส่ใน result
            result.append((record.id, name))
        return result


class ConfigurationWorkProgessProjectLine(models.Model):
    _name = 'configuration.work.progess.project.line'
    _description = 'Configuration Work Progess Project Line'

    
    name_ids = fields.Many2one("configuration.work.progess.type", string="Name")
    project_ids = fields.Many2one("configuration.work.progess.project", string="Project")
    product_ids = fields.Many2one("configuration.work.progess.project", string="Project")
    percent = fields.Float(string="Percent %", related="name_ids.percent", store=True, readonly=False)
    product_id = fields.Many2one("product.product", string="Product Name", required=False)
    qty = fields.Float(string="Quantity", required=False, default=1)
    unit_price = fields.Float(string="Unit Price", required=False)
    total = fields.Float(string="Total", compute="_compute_total", store=True , readonly=True)


    @api.onchange('product_id')
    def onchange_product_id(self):
        for rec in self:
            # ถ้า product_id มีค่า
            if rec.product_id:
                # field unit_price = product_id.lst_price
                rec.unit_price = rec.product_id.lst_price
            else:
                # ถ้าไม่มี product_id ให้ตั้ง unit_price เป็น 0
                rec.unit_price = 0.0


    @api.depends('qty', 'unit_price')
    def _compute_total(self):
        # ฟังก์ชันสำหรับคำนวนค่า total
        for rec in self:
            rec.total = rec.qty * rec.unit_price



