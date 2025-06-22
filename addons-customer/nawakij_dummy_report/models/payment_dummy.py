import logging
import re

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)

class PaymentDummy(models.Model):
    _name = "payment.dummy"
    _description = 'Dummy Payment'


    check_box = fields.Boolean(string="Select", copy=False, help="ใช้สำหรับเลือกเอกสารการชำระเงิน dummy")
    name = fields.Char(string="Name", copy=False, default="New", help="เก็บชื่อเอกสารการชำระเงิน")
    payment_date = fields.Date(string="Date", copy=False, default=fields.Date.context_today, help="วันที่ชำระเงิน")
    tax_invoice_number = fields.Char(string="Tax INV Number", copy=False, help="เก็บเลขเอกสารภาษี")
    tax_invoice_date = fields.Date(string="Tax INV Date", copy=False, help="วันที่เอกสารภาษี")

    # field monetary
    amount = fields.Monetary(string="Amount", copy=False, currency_field='currency_id', help="จำนวนเงินที่ชำระ")
    amount_due = fields.Monetary(string="Amount Due", copy=False, currency_field='currency_id', help="จำนวนเงินที่ค้างชำระ")

    # field many2one
    account_move_id = fields.Many2one("account.move", string="Account Move",copy=False)
    currency_id = fields.Many2one('res.currency', string="Currency")

    # field related
    account_move_name = fields.Char(string="INV Number", related="account_move_id.name")
    account_move_date = fields.Date(string="INV Date", related="account_move_id.invoice_date")
    account_move_partner = fields.Many2one('res.partner', string="Customer", related="account_move_id.partner_id")

