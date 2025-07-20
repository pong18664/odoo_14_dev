import logging
import re

from odoo import api, fields, models, SUPERUSER_ID, _ 
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import timedelta
from odoo.fields import Date

class AccountMove(models.Model):
    _inherit = 'account.move'


    def _post(self, soft=True):
        """
        Override function _post เอาเฉพาะ record แรกของ tax_invoice_ids และ tax_invoice_date ต้องไม่มีค่า
        เพื่อกำหนด tax_invoice_date ให้เป็นวันที่ปัจจุบัน (วันที่โพสต์)
        """
        for rec in self:
            first_line = rec.tax_invoice_ids[:1]  # ดึง recordset แรก (0 หรือ 1 เรคคอร์ด)
            
            # เฉพาะกรณีเป็น invoice และ record แรกมีอยู่และยังไม่มี tax_invoice_date
            if rec.move_type == 'out_invoice' and first_line and not first_line.tax_invoice_date:
                # โพสต์ invoice
                res = super(AccountMove, rec)._post(soft=soft)
                # ตั้งวันที่ภาษีเท่ากับวันที่โพสต์ (วันนี้)
                tax_invoice_date = fields.Date.context_today(rec)
                first_line.write({'tax_invoice_date': tax_invoice_date})
            else:
                # ไม่เข้าเงื่อนไขก็โพสต์ตามปกติ
                res = super(AccountMove, rec)._post(soft=soft)
        
        return res




