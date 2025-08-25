import re
import logging
_logger = logging.getLogger(__name__)

from odoo import api, fields, models, SUPERUSER_ID, _ 
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import timedelta
from odoo.fields import Date

class AccountMove(models.Model):
    _inherit = 'account.move'


    count_confirm_inv = fields.Integer(
        string='Confirm Invoice Count', 
        default=0,
        help="สำหรับนับจำนวนครั้งที่มีการยืนยันการออกใบแจ้งหนี้ (confirm invoice)ที่มี ค่า tax_invoice_ids")


    def _set_partner_id_in_tax_invoice(self):
        """
        Function สำหรับกำหนด partner_id ใน tax_invoice_ids
        โดยจะกำหนด partner_id ให้ตรงกับ partner_id ของ move
        เมื่อ tax_invoice_ids มีค่าอยู่และเป็นประเภท 'out_invoice'
        """
        for move in self:
            if move.move_type == 'out_invoice' and move.tax_invoice_ids:
                for tax_invoice in move.tax_invoice_ids:
                    tax_invoice.partner_id = move.partner_id


    def _set_date_in_tax_invoice(self):
        """
        Function สำหรับกำหนดวันที่ใน tax_invoice_ids
        โดยจะกำหนดวันที่เป็นวันที่ปัจจุบัน (วันที่โพสต์) เมื่อ
        tax_invoice_ids มีค่าอยู่และเป็นประเภท 'out_invoice'
        และจะเพิ่มตัวนับ count_confirm_inv ขึ้น 1 ทุกครั้งที่มีการ
        ยืนยันการออกใบแจ้งหนี้ (confirm invoice)
        """
        for move in self:
            if move.move_type == 'out_invoice' and move.tax_invoice_ids:
                move.count_confirm_inv = move.count_confirm_inv + 1
                if move.count_confirm_inv == 1:
                    for tax in move.tax_invoice_ids:
                        tax.tax_invoice_date = fields.Date.context_today(move)


    def _post(self, soft=True):
        """
        Override function _post เพื่อเรียกใช้ฟังก์ชัน 
        _set_partner_id_in_tax_invoice และ _set_date_in_tax_invoice
        หลังจากที่มีการโพสต์ (post) ใบแจ้งหนี้
        """
        res = super(AccountMove, self)._post(soft=soft)
        self._set_partner_id_in_tax_invoice()
        self._set_date_in_tax_invoice()

        return res




