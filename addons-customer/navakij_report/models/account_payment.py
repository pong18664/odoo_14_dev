import logging
import re

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)

class AccountPayment(models.Model):
    _inherit = "account.payment"

    amount_due = fields.Float(string='Amount Due', store=True)

    def create(self, vals):
        """
        เมื่อ function create ทำงานให้เรียกใช้ function _compute_amount_due
        """
        res = super(AccountPayment, self).create(vals)
        res._compute_amount_due()
        return res

    def _compute_amount_due(self):
        """
        search amount due in invoice ที่ name เดียวกันกับ ref ของ payment
        และ นำ amount due มาเก็บใน field amount_due
        """
        for rec in self:
            if rec.ref:
                inv_origin = self.env['account.move'].search([('name', '=', rec.ref)], limit=1)
                if inv_origin:
                    rec.amount_due = inv_origin.amount_residual if inv_origin.amount_residual else 0.0
  
    def get_formatted_date(self,date_data):
        """
        function จัดรูปแบบ วัน/เดือน/ปี
        """
        if date_data:
            formatted_date = date_data.strftime('%d/%m/%Y')
            return formatted_date
        else:
            return False

    def get_data_invoice_origin(self):
        """
        ฟังชั้นดึงข้อมูล invoice origin
        """
        result = []
        for rec in self:
            if rec.ref:
                inv_origin = self.env['account.move'].search([('name', '=', rec.ref)], limit=1)
                if inv_origin:
                    for line_tax in inv_origin.tax_invoice_ids:
                        tax_inv_number = line_tax.tax_invoice_number
                        tax_inv_date = line_tax.tax_invoice_date
                    data_invorigin = {
                        # 'name': inv_origin.name,
                        # 'invoice_date': self.get_formatted_date(inv_origin.invoice_date) if inv_origin.invoice_date else '',
                        'tax_inv_number': tax_inv_number,
                        'tax_inv_date': self.get_formatted_date(tax_inv_date) if tax_inv_date else '',
                        'amount_total': inv_origin.amount_total or 0.0,
                    }
                    result.append(data_invorigin)
        return result
    




