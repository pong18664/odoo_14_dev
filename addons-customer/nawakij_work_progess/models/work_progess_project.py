import logging
import re

from datetime import datetime, timedelta
from odoo import api, fields, tools, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError


class WorkProgessProject(models.Model):
    _name = 'work.progess.project'
    _description = 'Work Progess Project'


    name = fields.Char(string='Name', required=False, index=True, copy=False)
    project_line_ids = fields.One2many("work.progess.project.line", "work_progess_project_id", string="Project Line")
    project_name_id = fields.Many2one("configuration.work.progess.project", string="Project Name", required=False, index=True, copy=False)
    work_progess_id = fields.Many2one('work.progess', string='Work Progess')


    def name_get(self):
        # ฟังก์ชั่นสําหรับสร้าง name
        
        # สร้าง result ว่าง
        result = []
        for rec in self:
            # name = name_project จาก project_name_id
            name = rec.project_name_id.name_project
            # นำ name ไปใส่ใน result
            result.append((rec.id, name))
        return result


    @api.onchange('project_name_id')
    def create_work_progess_project_line(self):
        # ฟังก์ชั่นสำหรับสร้าง work progess project line

        # ถ้า project_name_id มีค่า
        if self.project_name_id:
            # ลบรายการ project lines ที่มีอยู่เดิม
            self.project_line_ids = [(5, 0, 0)]

            # ค้นหา work.progess ที่ตรงกับ project_name_id
            work_progess = self.env['work.progess'].search([
                ('project_ids', '=', self.project_name_id.id)
            ])
            
            # ถ้า work_progess มีค่า
            if work_progess:
                for line in work_progess:
                    # สร้าง work progess project line ใหม่
                    self.env['work.progess.project.line'].create({
                        'work_progess_project_id': self.id,
                        'work_progess_id': line.id,
                        'date_work_progess': line.date,
                    })
    

    def create_work_progess(self):
        # ฟังก์ชั่นสำหรับสร้าง work progess 

        for rec in self:
            # สร้างส่วนหัว work progess ใหม่
            work_progess_obj = self.env['work.progess'].create({
                'project_ids': rec.project_name_id.id,  
            })

            # สร้าง work progess line 
            for work_progess_line in rec.project_name_id.product_line_ids:    
                self.env['work.progess.line'].create({
                    'work_progess_id': work_progess_obj.id,
                    'product_id': work_progess_line.product_id.id,
                    'qty': work_progess_line.qty,
                    'unit_price': work_progess_line.unit_price,
                    'total': work_progess_line.qty * work_progess_line.unit_price,
                })

            # สร้าง work progess group type line
            name_type = []
            percent_type = []
            for project_line in self.project_name_id.project_line:
                name_type.append(project_line.name_ids.name_type)
                percent_type.append(project_line.percent)
            percent_strings = [f'{int(p)}%' for p in percent_type]
            
            if len(name_type) > 0 and len(percent_type) > 0:
                self.env['work.progess.group.type.line'].create({
                    'work_progess_id': work_progess_obj.id,
                    'group_type_1': f"{name_type[0]}({percent_strings[0]})" if len(name_type) > 0 else '',
                    'group_type_2': f"{name_type[1]}({percent_strings[1]})" if len(name_type) > 1 else '',
                    'group_type_3': f"{name_type[2]}({percent_strings[2]})" if len(name_type) > 2 else '',
                    'group_type_4': f"{name_type[3]}({percent_strings[3]})" if len(name_type) > 3 else '',
                    'group_type_5': f"{name_type[4]}({percent_strings[4]})" if len(name_type) > 4 else '',
                    'group_type_6': f"{name_type[5]}({percent_strings[5]})" if len(name_type) > 5 else '',
                })

            # ตั้งค่าฟิลด์ work_progess_id ให้ถูกต้อง
            rec.write({'work_progess_id': work_progess_obj.id})
            # ถ้ามีการสร้าง work progess
            if rec.project_name_id:
                # ให้เรียกฟังก์ชัน create_work_progess_project_line เพื่อสร้าง work progess project line
                rec.create_work_progess_project_line()


class WorkProgessProjectLine(models.Model):
    _name = 'work.progess.project.line'
    _description = 'Work Progess Project Line'


    name = fields.Char(string='Name', required=False, index=True, copy=False)
    work_progess_project_id = fields.Many2one("work.progess.project", string="Work Progess", required=False)
    work_progess_id = fields.Many2one("work.progess", string="Work Progess", required=False)
    date_work_progess = fields.Date(string='Date',  store=True, readonly=True)
    
