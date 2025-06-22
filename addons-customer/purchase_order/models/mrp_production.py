import logging
import re


from odoo import api, fields,tools, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'


    purchase_agreements_count = fields.Integer(string="" ,compute="get_purchase_agreements_count")

    # หาค่าของ field origin ของ purchase.requisition ที่ตรงกับ field name ของ mrp.production 
    def get_purchase_agreements_count(self):
        self.purchase_agreements_count = len(
            self.env['purchase.requisition'].search([("origin", "=", self.name)]))


    # เป็น function action พาเปลี่ยนหน้าไปตามที่ระบุ external id ไว้ และแสดงข้อมูลตามเงื่อนไขที่กำหนดไว้ที่ domain 
    # ค่าของ field origin ของ purchase.requisition ที่ตรงกับ field name ของ mrp.production
    def action_view_purchase_agreements(self):
        action = self.env["ir.actions.actions"]._for_xml_id("purchase_requisition.action_purchase_requisition")
        action['domain'] = [("origin", "=", self.name)]
        return action

    


