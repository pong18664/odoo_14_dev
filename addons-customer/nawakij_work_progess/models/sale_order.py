import logging
import re

from datetime import datetime, timedelta
from odoo import api, fields, tools, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    

    source_document = fields.Char(string="Source Document", required=False, store=True)
    count_work_progess = fields.Integer(string="Count Work Progess", compute="_compute_count_work_progess", required=False ,default=0)
    count_config_work_progess_project = fields.Integer(string="Count Config Work Progess Project", compute="_compute_count_config_work_progess_project", required=False, default=0)
    count_invoice = fields.Integer(string="Count Invoice", compute="_compute_count_invoice", required=False, default=0)


    @api.depends('source_document')
    def _compute_count_invoice(self):
        for rec in self:
            if rec.source_document:
                invoice = self.env['account.move'].search([('ref_work_progess', 'ilike', rec.source_document)])
                rec.count_invoice = len(invoice)
            else:
                rec.count_invoice = 0


    def action_view_account_move(self):
        # ฟังชั่นนี้จะทําการค้นหา account.move ที่มี ref_work_progess ตรงกับ name
        # แล้วก็จะทําการ action ไปที่ ir.actions.act_window ที่ได้จากค้นหา
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
        action['domain'] = [('ref_work_progess', 'ilike', self.source_document)]
        return action


    @api.depends('source_document')
    def _compute_count_work_progess(self):
        # ฟังชั่นสำหรับนับจำนวน work.progess ที่มี name ตรงกับ source_document
        for rec in self:
            if rec.source_document:
                work_progess = self.env['work.progess'].search([('name', 'ilike', rec.source_document)])
                rec.count_work_progess = len(work_progess)
            else :
                rec.count_work_progess = 0


    @api.depends('source_document')
    def _compute_count_config_work_progess_project(self):
        # ฟังชั่นสำหรับนับจำนวน configuration.work.progess.project ที่มี name ตรงกับ source_document
        for rec in self:
            if rec.source_document:
                config_work_progess_project = self.env['configuration.work.progess.project'].search([('name_project', 'ilike', rec.source_document)])
                rec.count_config_work_progess_project = len(config_work_progess_project)
            else:
                rec.count_config_work_progess_project = 0


    def action_view_work_progess(self):
        # ฟังชั่นนี้จะทําการค้นหา work.progess ที่มี name ตรงกับ source_document
        # แล้วก็จะทําการ action ไปที่ ir.actions.act_window ที่ได้จากค้นหา
        action = self.env["ir.actions.actions"]._for_xml_id("nawakij_work_progess.action_work_progess")
        action['domain'] = [('name', 'ilike', self.source_document)]
        return action
    

    def action_view_config_work_progess_project(self):
        # ฟังชั่นนี้จะทําการค้นหา configuration.work.progess.project ที่มี name ตรงกับ source_document
        # แล้วก็จะทําการ action ไปที่ ir.actions.act_window ที่ได้จากค้นหา
        action = self.env["ir.actions.actions"]._for_xml_id("nawakij_work_progess.action_configuration_work_progess_project")
        action['domain'] = [('name_project', 'ilike', self.source_document)]
        return action


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'


    work_progess_value = fields.Integer(string="Work Progess Value", required=False)