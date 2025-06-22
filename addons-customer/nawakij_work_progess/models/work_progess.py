import logging
import re

from datetime import datetime, timedelta
from odoo import api, fields, tools, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
# raise ValidationError(_(""))
_logger = logging.getLogger(__name__)


class WorkProgess(models.Model):
    _name = 'work.progess'
    _description = 'Work Progess'


    name = fields.Char(string='Name', compute="_compute_name", readonly=True, required=False, index=True, store=True, copy=False, default='New')
    project_ids = fields.Many2one("configuration.work.progess.project", string="Project Name", required=False)
    date = fields.Date(string='Date', required=True, index=True, default=fields.Date.context_today, copy=False)
    line_ids = fields.One2many("work.progess.line", "work_progess_id", string="Work Progess Line")
    type_count = fields.Integer(string="Type", compute="_compute_type_count", store=True, default=0)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.company.currency_id)
    note = fields.Text(string="Note")
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_compute_amount_total')
    active = fields.Boolean(default=True)
    work_progess_project_id = fields.Many2one("work.progess.project", string="Work Progess Project", required=False)
    invoice_id = fields.Many2one('account.move', string='Invoice', required=False)
    count_invoice = fields.Integer(string="Count Invoice", compute="_compute_count_invoice", store=True, default=0)
    source_document = fields.Char(string='Source Document')
    cumulative_total = fields.Float(string='Cumulative Total', compute='_compute_cumulative_total', store=True, readonly=True, default=0)
    group_type_line_ids = fields.One2many("work.progess.group.type.line", "work_progess_id", string="Group Type Line")
    count_work_progess = fields.Integer(string="Count Work Progess", compute="_compute_count_work_progess", store=True, default=0)


    def open_group_product_wizard(self):
    # ฟังชั่นสำหรับเปิด wizard
        return {
            'name': _('Group Product Wizard'),
            'type': 'ir.actions.act_window',
            'res_model': 'work.progess.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                # 'default_product_id': self.line_ids.mapped('product_id').ids,
            }
        }


    @api.depends('line_ids.cumulative_amount')
    def _compute_cumulative_total(self):
        # ฟังชั่นสำหรับคำนวน cumulative_total
        for rec in self:
            rec.cumulative_total = sum(line.cumulative_amount for line in rec.line_ids)


    def create_next_work_progess(self):
    # ฟังก์ชั่นสำหรับสร้าง work progess ต่อไป

        count_work_progess = self.count_work_progess
        
        for rec in self:
            # สร้างส่วนหัว work progess
            work_progess = self.create({
                'project_ids': rec.project_ids.id,
                'date': rec.date,
                'type_count': rec.type_count,
                'source_document': rec.name,
                'note': rec.note
            })

            # สร้างส่วน work progess line
            for line in rec.line_ids:
                self.env['work.progess.line'].create({
                    'work_progess_id': work_progess.id,
                    'product_id': line.product_id.id,
                    'grouping_product_id': line.grouping_product_id.id if line.grouping_product_id else False,
                    'qty': line.qty,
                    'unit_price': line.unit_price,
                    'total': line.total,
                    'name_type_1': line.name_type_1 if line.name_type_1 else 0,
                    'percent_1': line.percent_1 if line.percent_1 else 0,
                    'previous_1': line.qty_1 + line.previous_1 if line.qty_1 else line.previous_1,
                    'cumulative_price_1': (
                        line.price_1 if line.price_1 and not line.cumulative_price_1 else 
                        line.cumulative_price_1 if line.cumulative_price_1 and not line.price_1 else 
                        line.cumulative_price_1 if line.cumulative_price_1 and line.price_1 else 
                        0
                    ),
                    'name_type_2': line.name_type_2 if line.name_type_2 else 0,
                    'percent_2': line.percent_2 if line.percent_2 else 0,
                    'previous_2': line.qty_2 + line.previous_2 if line.qty_2 else line.previous_2,
                    'cumulative_price_2': (
                        line.price_2 if line.price_2 and not line.cumulative_price_2 else 
                        line.cumulative_price_2 if line.cumulative_price_2 and not line.price_2 else 
                        line.cumulative_price_2 if line.cumulative_price_2 and line.price_2 else 
                        0
                    ),
                    'name_type_3': line.name_type_3 if line.name_type_3 else 0,
                    'percent_3': line.percent_3 if line.percent_3 else 0,
                    'previous_3': line.qty_3 + line.previous_3 if line.qty_3 else line.previous_3,
                    'cumulative_price_3': (
                        line.price_3 if line.price_3 and not line.cumulative_price_3 else 
                        line.cumulative_price_3 if line.cumulative_price_3 and not line.price_3 else 
                        line.cumulative_price_3 if line.cumulative_price_3 and line.price_3 else 
                        0
                    ),
                    'name_type_4': line.name_type_4 if line.name_type_4 else 0,
                    'percent_4': line.percent_4 if line.percent_4 else 0,
                    'previous_4': line.qty_4 + line.previous_4 if line.qty_4 else line.previous_4,
                    'cumulative_price_4': (
                        line.price_4 if line.price_4 and not line.cumulative_price_4 else 
                        line.cumulative_price_4 if line.cumulative_price_4 and not line.price_4 else 
                        line.cumulative_price_4 if line.cumulative_price_4 and line.price_4 else 
                        0
                    ),
                    'name_type_5': line.name_type_5 if line.name_type_5 else 0,
                    'percent_5': line.percent_5 if line.percent_5 else 0,
                    'previous_5': line.qty_5 + line.previous_5 if line.qty_5 else line.previous_5,
                    'cumulative_price_5': (
                        line.price_5 if line.price_5 and not line.cumulative_price_5 else 
                        line.cumulative_price_5 if line.cumulative_price_5 and not line.price_5 else 
                        line.cumulative_price_5 if line.cumulative_price_5 and line.price_5 else 
                        0
                    ),
                    'name_type_6': line.name_type_6 if line.name_type_6 else 0,
                    'percent_6': line.percent_6 if line.percent_6 else 0,
                    'previous_6': line.qty_6 + line.previous_6 if line.qty_6 else line.previous_6,
                    'cumulative_price_6': (
                        line.price_6 if line.price_6 and not line.cumulative_price_6 else 
                        line.cumulative_price_6 if line.cumulative_price_6 and not line.price_6 else 
                        line.cumulative_price_6 if line.cumulative_price_6 and line.price_6 else 
                        0
                    ),
                })

            for group_type in rec.group_type_line_ids:
                self.env['work.progess.group.type.line'].create({
                    'work_progess_id': work_progess.id,
                    'group_type_1': group_type.group_type_1 if group_type.group_type_1 else '',
                    'group_type_2': group_type.group_type_2 if group_type.group_type_2 else '',
                    'group_type_3': group_type.group_type_3 if group_type.group_type_3 else '',
                    'group_type_4': group_type.group_type_4 if group_type.group_type_4 else '',
                    'group_type_5': group_type.group_type_5 if group_type.group_type_5 else '',
                    'group_type_6': group_type.group_type_6 if group_type.group_type_6 else '',
                })            

            # บันทึกข้อมูลลงฐานข้อมูล
            work_progess.flush()


    def name_get(self):
        # ฟังก์ชั่นสำหรับสร้าง name

        # สร้าง result ว่าง
        result = []
        for record in self:
            # name = name_project จาก project_ids
            name = record.name
            # นำ name ไปใส่ใน result
            result.append((record.id, name))
            # นำ name ไปใส่ใน field name
            record.name = name
        return result


    @api.depends('project_ids')
    def _compute_count_work_progess(self):
        # ฟั่งก์ชั่นสำหรับนับจํานวน work progess ที่มี project_ids เดียวกัน
        for rec in self:
            if rec.project_ids:
                count = self.env['work.progess'].search_count([('project_ids', 'in', rec.project_ids.ids)])
                rec.count_work_progess = count


    @api.depends('project_ids','count_work_progess')
    def _compute_name(self):
        # ฟังก์ชั่นสำหรับกำหนดค่า field name เช่น project 1 / 0001
        for rec in self:
            if rec.project_ids and rec.count_work_progess:
                project_name = rec.project_ids.name_project
                rec.name = f"{project_name} / {str(rec.count_work_progess).zfill(4)}"
            else:
                rec.name = 'New'


    @api.depends('invoice_id.ref_work_progess')
    def _compute_count_invoice(self):
        # ฟังก์ชันสำหรับนับจำนวน invoice ที่มี ref_work_progess ตรงกับ name
        for rec in self:
            invoices = self.env['account.move'].search([('ref_work_progess', 'ilike', rec.name)])  # หา invoice ที่มี ref_work_progess ตรงกับ name
            rec.count_invoice = len(invoices) if invoices else 0  # ตรวจสอบจำนวน invoices


    def action_view_account_move(self):
        # ฟังชั่นนี้จะทําการค้นหา account.move ที่มี ref_work_progess ตรงกับ name
        # แล้วก็จะทําการ action ไปที่ ir.actions.act_window ที่ได้จากค้นหา
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
        action['domain'] = [('ref_work_progess', 'ilike', self.name)]
        return action


    def create_invoice(self):
        # ฟังชั่นสำหรับสร้าง invoice

        for record in self:
            # สร้าง form invoice
            invoice = self.env['account.move'].create({
                'partner_id': record.project_ids.partner_ids.id,
                'ref_work_progess': record.name,
                'move_type': 'out_invoice',
                'narration': self.note if self.note else '',
            })

            # สร้าง invoice_lines ว่าง
            invoice_lines = []
            # สร้างข้อมูล
            for line in self.line_ids:
                # นำข้อมูลไปใส่ใน invoice_lines
                if line.invoice_quantity:
                    invoice_lines.append((0, 0, {
                            'product_id': line.product_id, 
                            'quantity': line.invoice_quantity,
                            'price_unit': line.unit_price,
                            'move_id': invoice.id,
                        }))
            
            # นำข้อมูลจาก invoice_lines ไปใส่ใน invoice_line_ids ที่เดียว
            invoice.write({'invoice_line_ids': invoice_lines})
            # บันทึกข้อมูลการสร้าง invoice
            record.write({'invoice_id': invoice.id})
            # เรียกฟังชั่นสำหรับนับจํานวน invoice ที่มี ref_work_progess ตรงกับ name
            self._compute_count_invoice()

        return invoice


    # def create_invoice(self):
    #     # ฟังชั่นสำหรับสร้าง invoice

    #     for record in self:
    #         # สร้าง form invoice
    #         invoice = self.env['account.move'].create({
    #             'partner_id': record.project_ids.partner_ids.id,
    #             'ref_work_progess': record.name,
    #             'move_type': 'out_invoice',
    #             'narration': self.note,
    #         })

    #         # สร้าง dict สำหรับเก็บข้อมูลที่รวมกัน
    #         grouped_lines = {}

    #         for line in record.line_ids:
    #             # ใช้ grouping_product_id เป็น key
    #             group_name = line.grouping_product_id.id if line.grouping_product_id else line.product_id.id

    #             if group_name not in grouped_lines:
    #                 # ถ้ายังไม่มี ให้เพิ่มข้อมูลเริ่มต้น
    #                 if line.invoice_quantity > 0:
    #                     grouped_lines[group_name] = {
    #                         'group_product_id': line.grouping_product_id.id if line.grouping_product_id else False,
    #                         'product_id': line.product_id.id if not line.grouping_product_id else False,
    #                         'quantity': line.invoice_quantity,
    #                         'price_unit': line.unit_price if not line.grouping_product_id else False,  # เก็บราคาต่อหน่วยรวม
    #                         'total_amount': line.amount if line.grouping_product_id else False,  # เก็บราคารวม
    #                     }
    #             else:
    #                 # ถ้ามีอยู่แล้ว ให้รวมค่า
    #                 grouped_lines[group_name]['quantity'] += line.invoice_quantity
    #                 grouped_lines[group_name]['total_amount'] += line.amount

    #         # หลังจากวนลูปครบแล้ว คำนวณราคาต่อหน่วยเฉลี่ย
    #         for group_name, data in grouped_lines.items():
    #             if data['quantity'] > 0:
    #                 # คำนวณ price_unit จาก total_amount เฉพาะกรณีที่มี grouping_product_id
    #                 data['price_unit_form_amount'] = data['total_amount'] / data['quantity'] if data['total_amount'] else 0
    #             else:
    #                 data['price_unit_form_amount'] = 0  # ในกรณีที่ quantity เป็น 0 ป้องกันการหารด้วย 0

    #         # raise ValidationError(_(grouped_lines))

    #         # สร้าง invoice_lines ว่าง
    #         invoice_lines = []
    #         for group_name, data in grouped_lines.items():
    #             if data['quantity'] > 0:
    #                 invoice_lines.append((0, 0, {
    #                     'product_id': data['group_product_id'] if data['group_product_id'] else data['product_id'], 
    #                     'quantity': data['quantity'],
    #                     'price_unit': data['price_unit_form_amount'] if data['group_product_id'] else data['price_unit'],
    #                     'move_id': invoice.id,
    #                 }))

    #         # นำข้อมูลจาก invoice_lines ไปใส่ใน invoice_line_ids ที่เดียว
    #         invoice.write({'invoice_line_ids': invoice_lines})
    #         # บันทึกข้อมูลการสร้าง invoice
    #         record.write({'invoice_id': invoice.id})
    #     # เรียกฟังชั่นสำหรับนับจํานวน invoice ที่มี ref_work_progess ตรงกับ name
    #     self._compute_count_invoice()

    #     return invoice


    @api.model
    def create(self, vals):
        record = super(WorkProgess, self).create(vals)

        # เรียกใช้ฟังก์ชั่น create_work_progess_project_line เพื่อสร้าง work.progess.project.line 
        related_projects = self.env['work.progess.project'].search([
            ('project_name_id', '=', record.project_ids.id)
        ])
        # for project in related_projects:
        if related_projects:
            related_projects.create_work_progess_project_line()

        return record      
    

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

    
    @api.depends('line_ids')
    def _compute_amount_total(self):
        # ฟังก์ชั่นสำหรับคำนวนค่าใน field amount_total
        for record in self:
            # field amount_total = รวมจาก field amount ของ line_ids
            record.amount_total = sum(line.amount for line in record.line_ids)


    @api.depends('project_ids')
    def _compute_type_count(self):
        # ฟังก์ชั่นสำหรับคำนวนค่าใน field type_count
        for record in self:
            # field type_count = จำนวนของ project_ids.project_line
            record.type_count = len(record.project_ids.project_line)


    @api.onchange('project_ids')
    def create_work_progess_line(self):
        # ฟังก์ชั่นสำหรับสร้าง work progess line

        self.line_ids = [(5, 0, 0)]  # ลบรายการ work.progess.line ที่มีอยู่เดิม
        for line in self.project_ids.product_line_ids:
            self.env['work.progess.line'].create({
                'work_progess_id': self.id, 
                'product_id': line.product_id.id,
                'qty': line.qty,
                'unit_price': line.unit_price,
                'total': line.qty * line.unit_price,
            })
            

    @api.onchange('project_ids')
    def create_group_type_line_ids(self):
        # ฟังก์ชั่นสำหรับสร้างข้อมูลใน group_type_line_ids

        self.group_type_line_ids = [(5, 0, 0)]  # ลบรายการ work.progess.line ที่มีอยู่เดิม
        name_type = []
        percent_type = []
        for project_line in self.project_ids.project_line:
            name_type.append(project_line.name_ids.name_type)
            percent_type.append(project_line.percent)
        percent_strings = [f'{int(p)}%' for p in percent_type]

        group_type_line_vals = []
        if len(name_type) > 0 and len(percent_type) > 0:
            group_type_line_vals.append((0, 0, {
                'work_progess_id': self.id,
                'group_type_1': f"{name_type[0]}({percent_strings[0]})" if len(name_type) > 0 else '',
                'group_type_2': f"{name_type[1]}({percent_strings[1]})" if len(name_type) > 1 else '',
                'group_type_3': f"{name_type[2]}({percent_strings[2]})" if len(name_type) > 2 else '',
                'group_type_4': f"{name_type[3]}({percent_strings[3]})" if len(name_type) > 3 else '',
                'group_type_5': f"{name_type[4]}({percent_strings[4]})" if len(name_type) > 4 else '',
                'group_type_6': f"{name_type[5]}({percent_strings[5]})" if len(name_type) > 5 else '',
            }))

        self.group_type_line_ids = group_type_line_vals


class WorkProgessLine(models.Model):
    _name = 'work.progess.line'
    _description = 'Work Progess Line'


    product_id = fields.Many2one("product.product", string="Product Name", required=False)
    qty = fields.Float(string="Quantity", required=False, default=1)
    unit_price = fields.Float(string="Unit Price", required=False)
    total = fields.Float(string="Total", required=False, readonly=True, compute="_compute_total")
    work_progess_id = fields.Many2one("work.progess", string="Work Progess", required=False)
    type_count = fields.Integer(string="Type Count", related="work_progess_id.type_count", store=True, default=0)
    name_type_1 = fields.Char(string="Type1", compute="_compute_name_types", store=True)
    name_type_2 = fields.Char(string="Type2", compute="_compute_name_types", store=True)
    name_type_3 = fields.Char(string="Type3", compute="_compute_name_types", store=True)
    name_type_4 = fields.Char(string="Type4", compute="_compute_name_types", store=True)
    name_type_5 = fields.Char(string="Type5", compute="_compute_name_types", store=True)
    name_type_6 = fields.Char(string="Type6", compute="_compute_name_types", store=True)
    percent_1 = fields.Float(string="%", compute="_compute_percent", store=True)
    percent_2 = fields.Float(string="%", compute="_compute_percent", store=True)
    percent_3 = fields.Float(string="%", compute="_compute_percent", store=True)
    percent_4 = fields.Float(string="%", compute="_compute_percent", store=True)
    percent_5 = fields.Float(string="%", compute="_compute_percent", store=True)
    percent_6 = fields.Float(string="%", compute="_compute_percent", store=True)
    qty_1 = fields.Float(string="Qty1", store=True, default=0)
    qty_2 = fields.Float(string="Qty2", store=True, default=0)
    qty_3 = fields.Float(string="Qty3", store=True, default=0)
    qty_4 = fields.Float(string="Qty4", store=True, default=0)
    qty_5 = fields.Float(string="Qty5", store=True, default=0)
    qty_6 = fields.Float(string="Qty6", store=True, default=0)
    price_1 = fields.Float(string="Price1", compute="_compute_price", readonly=True, store=True)
    price_2 = fields.Float(string="Price2", compute="_compute_price", readonly=True, store=True)
    price_3 = fields.Float(string="Price3", compute="_compute_price", readonly=True, store=True)
    price_4 = fields.Float(string="Price4", compute="_compute_price", readonly=True, store=True)
    price_5 = fields.Float(string="Price5", compute="_compute_price", readonly=True, store=True)
    price_6 = fields.Float(string="Price6", compute="_compute_price", readonly=True, store=True)
    previous_1 = fields.Float(string='Previous 1', readonly=True, default=0)
    previous_2 = fields.Float(string='Previous 2', readonly=True, default=0)
    previous_3 = fields.Float(string='Previous 3', readonly=True, default=0)
    previous_4 = fields.Float(string='Previous 4', readonly=True, default=0)
    previous_5 = fields.Float(string='Previous 5', readonly=True, default=0)
    previous_6 = fields.Float(string='Previous 6', readonly=True, default=0)
    cumulative_qty_1 = fields.Float(string='Total Qty 1', compute="_compute_cumulative_qty", store=True, readonly=True, default=0)
    cumulative_qty_2 = fields.Float(string='Total Qty 2', compute="_compute_cumulative_qty", store=True, readonly=True, default=0)
    cumulative_qty_3 = fields.Float(string='Total Qty 3', compute="_compute_cumulative_qty", store=True, readonly=True, default=0)
    cumulative_qty_4 = fields.Float(string='Total Qty 4', compute="_compute_cumulative_qty", store=True, readonly=True, default=0)
    cumulative_qty_5 = fields.Float(string='Total Qty 5', compute="_compute_cumulative_qty", store=True, readonly=True, default=0)
    cumulative_qty_6 = fields.Float(string='Total Qty 6', compute="_compute_cumulative_qty", store=True, readonly=True, default=0)
    cumulative_price_1 = fields.Float(string='Total Price 1', compute="_compute_cumulative_price", store=True, readonly=True, default=0)
    cumulative_price_2 = fields.Float(string='Total Price 2', compute="_compute_cumulative_price", store=True, readonly=True, default=0)
    cumulative_price_3 = fields.Float(string='Total Price 3', compute="_compute_cumulative_price", store=True, readonly=True, default=0)
    cumulative_price_4 = fields.Float(string='Total Price 4', compute="_compute_cumulative_price", store=True, readonly=True, default=0)
    cumulative_price_5 = fields.Float(string='Total Price 5', compute="_compute_cumulative_price", store=True, readonly=True, default=0)
    cumulative_price_6 = fields.Float(string='Total Price 6', compute="_compute_cumulative_price", store=True, readonly=True, default=0)
    amount = fields.Float(string="Amount", compute="_compute_amount", store=True, readonly=True)
    payment_percent = fields.Float(string="%", compute="_compute_payment_percent", store=True , readonly=True)
    invoice_quantity = fields.Float(string="Invoice Quantity", compute="_compute_invoice_quantity", store=True , readonly=True)
    cumulative_amount = fields.Float(string='Total Amount', compute="_compute_cumulative_amount", readonly=True, store=True)
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


    @api.depends('unit_price')
    def _compute_total(self):
        for line in self:
            if line.unit_price:
                line.total = line.unit_price * line.qty


    @api.depends('cumulative_price_1', 'cumulative_price_2', 'cumulative_price_3', 'cumulative_price_4', 'cumulative_price_5', 'cumulative_price_6')
    def _compute_cumulative_amount(self):
        # ฟังชั่นนี้ใช้เพื่อคํานวณค่า Cumulative Amount
        for line in self:
            if any(getattr(line, f'cumulative_price_{i}') for i in range(1, 7)):
                line.cumulative_amount = sum(getattr(line, f'cumulative_price_{i}') for i in range(1, 7))


    @api.onchange('qty_1', 'qty_2', 'qty_3', 'qty_4', 'qty_5', 'qty_6', 'unit_price')
    def _compute_cumulative_price(self):
        # ฟังชั่นนี้ใช้เพื่อคํานวณค่า Cumulative Price
        for line in self:
            # เช็คกลุ่ม previous_1 ถึง previous_8 ว่ามีค่าหรือไม่
            # ถ้ากลุ่ม previous มีค่าแสดงว่า record นี้เป็น record ที่สร้างต่อมาจาก record ก่อนหน้า
            if any(getattr(line, f'previous_{i}') for i in range(1, 7)) and any(getattr(line, f'qty_{i}') for i in range(1, 7)):
                for i in range(1, 7):  
                    setattr(line, f'cumulative_price_{i}', 
                            ((getattr(line, f'percent_{i}') / 100) * getattr(line, f'previous_{i}') * line.unit_price) 
                            + getattr(line, f'price_{i}')) 
            # ถ้ากลุ่ม previous ไม่มีค่าแสดงว่า record นี้เป็น record แรก
            else:
                for i in range(1, 7):
                    setattr(line, f'cumulative_price_{i}', 
                            ((getattr(line, f'percent_{i}') / 100) * getattr(line, f'previous_{i}') * line.unit_price)) 
                        

    @api.depends('previous_1','previous_2','previous_3','previous_4','previous_5','previous_6',
                 'qty_1','qty_2','qty_3','qty_4','qty_5','qty_6')
    def _compute_cumulative_qty(self):
        # ฟังชั่นนี้ใช้เพื่อคํานวณค่า Cumulative Qty
        for line in self:
            if any(getattr(line, f'previous_{i}') for i in range(1, 7)) and any(getattr(line, f'qty_{i}') for i in range(1, 7)):
                for i in range(1, 7):
                    setattr(line, f'cumulative_qty_{i}', 
                            getattr(line, f'previous_{i}') + getattr(line, f'qty_{i}'))
            else:
                for i in range(1, 7):
                    setattr(line, f'cumulative_qty_{i}', 0)
                

    @api.depends('total', 'payment_percent')
    def _compute_invoice_quantity(self):
        # ฟังชั่นสําหรับคํานวณค่า invoice_quantity
        for line in self:
            if line.total > 0:
                line.invoice_quantity = (line.payment_percent / 100) * line.qty
            else:
                line.invoice_quantity = 0


    @api.depends('amount', 'total')
    def _compute_payment_percent(self):
        # ฟังชั่นสําหรับคํานวณค่า payment_percent
        for line in self:
            # ถ้า total มากกว่า 0 ให้คํานวณ payment_percent
            if line.total > 0:
                line.payment_percent = (line.amount / line.total) * 100
            # ถ้า total น้อยกว่าหรือเท่ากับ 0 ให้ payment_percent = 0
            else:
                line.payment_percent = 0


    @api.depends('price_1', 'price_2', 'price_3', 'price_4', 'price_5', 'price_6')
    def _compute_amount(self):
        # ฟังชั่นสําหรับคํานวณค่า amount
        for line in self:
            # field amount = field price_1 ถึง field price_8 บวกรวมกัน
            line.amount = line.price_1 + line.price_2 + line.price_3 + line.price_4 + line.price_5 + line.price_6


    @api.depends('unit_price','qty_1','qty_2','qty_3','qty_4','qty_5','qty_6')
    def _compute_price(self):
        # ฟังชั่นสําหรับคํานวณค่า price
        for line in self:
            for i in range(1, 7):
                setattr(line, f'price_{i}', (((getattr(line, f'percent_{i}') / 100) * getattr(line, f'qty_{i}')) * getattr(line, f'unit_price')))  


    @api.depends('work_progess_id.project_ids')
    def _compute_percent(self):
        # ฟังก์ชันสำหรับกำหนดค่าให้กับ field percent_1 ถึง field percent_6

        for line in self:
            # ดึง project ที่เกี่ยวข้องจาก work_progess_id
            project = line.work_progess_id.project_ids
            
            # ตรวจสอบว่ามี project หรือไม่
            if project:
                # ดึงค่าของ percent จาก name_ids ใน project_line
                percent = project.project_line.mapped('name_ids.percent')

                for i in range(1, 7):
                    setattr(line, f'percent_{i}', percent[i - 1] if len(percent) >= i else False)
                
                # กำหนดค่าให้ percent_1 ถึง percent_8 จากค่า percent ที่ดึงมา
                line.percent_1 = percent[0] if len(percent) > 0 else False
                line.percent_2 = percent[1] if len(percent) > 1 else False
                line.percent_3 = percent[2] if len(percent) > 2 else False
                line.percent_4 = percent[3] if len(percent) > 3 else False
                line.percent_5 = percent[4] if len(percent) > 4 else False
                line.percent_6 = percent[5] if len(percent) > 5 else False
            else:
                # หากไม่มี project, ให้ตั้งค่า percent_1 ถึง percent_8 เป็น False
                line.percent_1 = line.percent_2 = line.percent_3 = line.percent_4 = line.percent_5 = line.percent_6 = False


    @api.depends('work_progess_id.project_ids')
    def _compute_name_types(self):
        # ฟังก์ชันสำหรับกำหนดค่าให้กับ field name_type_1 ถึง field name_type_6

        for line in self:
            project = line.work_progess_id.project_ids
            
            if project:
                name_types = project.project_line.mapped('name_ids.name_type')
                
                # ใช้ลูปเพื่อกำหนดค่า name_type_1 ถึง name_type_6
                for i in range(6):
                    setattr(line, f'name_type_{i + 1}', name_types[i] if len(name_types) > i else False)
            else:
                # ใช้ลูปตั้งค่า name_type_1 ถึง name_type_6 เป็น False
                for i in range(6):
                    setattr(line, f'name_type_{i + 1}', False)


    @api.onchange('product_id')
    def _onchange_product_id(self):
        # ฟังก์ชันสำหรับเปลี่ยนค่า unit_price ตามการเปลี่ยนแปลงของ product_id
        if self.product_id:
            self.unit_price = self.product_id.list_price


    @api.onchange('qty', 'unit_price')
    def _onchange_qty(self):
        # ฟังก์ชันสำหรับเปลี่ยนค่า total ตามการเปลี่ยนแปลงของ qty หรือ unit_price
        if self.qty and self.unit_price:
            self.total = self.qty * self.unit_price


class WorkProgessGroupTypeLine(models.Model):
    _name = 'work.progess.group.type.line'
    _description = 'Work Progess Group Type Line'


    work_progess_id = fields.Many2one("work.progess", string="Work Progess")
    group_type_1 = fields.Char(string="Group Type 1", store=True, readonly=True)
    group_type_2 = fields.Char(string="Group Type 2", store=True, readonly=True)
    group_type_3 = fields.Char(string="Group Type 3", store=True, readonly=True)
    group_type_4 = fields.Char(string="Group Type 4", store=True, readonly=True)
    group_type_5 = fields.Char(string="Group Type 5", store=True, readonly=True)
    group_type_6 = fields.Char(string="Group Type 6", store=True, readonly=True)

    