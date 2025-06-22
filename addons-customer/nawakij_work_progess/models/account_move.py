import logging
import re
import json

from datetime import datetime, timedelta
from odoo import api, fields, tools, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'
    

    ref_work_progess = fields.Char(string="Ref Work Progess", required=False, index=True, store=True)
    count_work_progess = fields.Integer(string="Count Work Progess", compute="_compute_count_work_progess", store=True, required=False ,default=0)
    count_sale_order = fields.Integer(string="Count Sale Order", compute="_compute_count_sale_order", default=0)


    @api.depends('ref_work_progess')
    def _compute_count_sale_order(self):
        for rec in self:
            if rec.ref_work_progess:
                sale_order = self.env['sale.order'].search([('source_document', 'ilike', rec.ref_work_progess.split(' / ')[0])])
                rec.count_sale_order = len(sale_order)
            else:
                rec.count_sale_order = 0           


    def action_view_sale_order(self):
        # ฟังชั่นสำหรับดู sale order
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_orders")
        action['domain'] = [('source_document', 'ilike', self.ref_work_progess.split(' / ')[0])]
        return action


    @api.depends('ref_work_progess')
    def _compute_count_work_progess(self):
        # ฟังชั่นนี้จะทําการค้นหา work.progess ที่มี name ตรงกับ ref_work_progess และนับจํานวน work.progess ที่ค้นหาได้
        for rec in self:
            if rec.ref_work_progess:
                work_progess = self.env['work.progess'].search([('name', 'ilike', rec.ref_work_progess)])
                rec.count_work_progess = len(work_progess)
            else:
                rec.count_work_progess = 0
           

    def action_view_work_progess(self):
        # ฟังชั่นนี้จะทําการค้นหา work.progess ที่มี name ตรงกับ ref_work_progess
        # แล้วก็จะทําการ action ไปที่ ir.actions.act_window ที่ได้จากค้นหา
        action = self.env["ir.actions.actions"]._for_xml_id("nawakij_work_progess.action_work_progess")
        action['domain'] = [('name', '=', self.ref_work_progess)]
        return action
