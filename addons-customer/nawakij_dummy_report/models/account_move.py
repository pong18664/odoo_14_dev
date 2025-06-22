import logging
import re

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "account.move"


    # fields many2one
    vat_dummy_id = fields.Many2one("account.tax", string="VAT", copy=False)
    wht_dummy_id = fields.Many2one("account.withholding.tax", string="WHT", copy=False)
    payment_dummy_id = fields.Many2one(
        "payment.dummy", 
        string="Payment Receipt", 
        copy=False,
        domain="[('id', 'in', payment_dummy_ids)]",                               
        help="เอกสารการชำระเงิน dummy ที่เกี่ยวข้องกับเอกสารบัญชีนี้"
    )

    # fields one2many
    payment_dummy_ids = fields.One2many(
        "payment.dummy",
        "account_move_id",
        string="Payment Dummy",
        copy=False,
    )

    # fields monetary
    pay_this_round = fields.Monetary(string="Pay This Round", copy=False, default=0.00, help="เก็บจำนวนเงินที่ต้องชำระในรอบนี้")
    amount_due_payment_dummy = fields.Monetary(
        string="Amount Due",
        copy=False,
        default=0.00,
        # compute="_compute_amount_due_payment_dummy",
        currency_field="currency_id",
        help="จำนวนเงินที่ค้างชำระในเอกสารการชำระเงิน dummy"
    )
 

    def create_payment_dummy(self):
        """
        Function สำหรับสร้างเอกสาร payment dummy
        โดยจะสร้างเอกสารการชำระเงิน dummy สำหรับแต่ละเอกสารบัญชีที่เลือก
        และบันทึกเอกสารการชำระเงิน dummy ลงใน payment.dummy
        และปรับปรุงค่า amount_due_payment_dummy และ pay_this_round
        ในเอกสารบัญชีที่เลือก
        """
        for rec in self:

            if not rec.pay_this_round:
                raise UserError(_("กรุณากรอกจำนวนเงินที่ต้องชำระในรอบนี้"))
            
            if rec.pay_this_round > rec.amount_due_payment_dummy and rec.payment_dummy_ids:
                raise UserError(_("ยอดเงินที่ชำระมากกว่ายอดคงค้าง"))

            # เตรียมข้อมูลสำหรับสร้างเอกสารการชำระเงิน dummy
            payment_dummy_vals = {
                "name": self.env['ir.sequence'].next_by_code('payment.dummy'),
                "payment_date": fields.Date.context_today(rec),
                "amount": rec.pay_this_round,
                "amount_due": rec.amount_due_payment_dummy - rec.pay_this_round if rec.amount_due_payment_dummy else rec.net_total - rec.pay_this_round,
                "account_move_id": rec.id,
                "currency_id": rec.currency_id.id,
            }

            # สร้างเอกสารการชำระเงิน dummy
            payment_dummy = self.env["payment.dummy"].create(payment_dummy_vals)

            # บันทึกเอกสารการชำระเงิน dummy ลงใน payment.dummy
            rec.payment_dummy_ids = [(4, payment_dummy.id)]

            # กำหนดค่า amount_due_payment_dummy ตามเงื่อนไข
            if rec.amount_due_payment_dummy:
                rec.amount_due_payment_dummy = rec.amount_due_payment_dummy - rec.pay_this_round
            else:
                rec.amount_due_payment_dummy = rec.net_total - rec.pay_this_round

            # reset ค่า pay_this_round กลับเป็น 0.00
            rec.pay_this_round = 0.00


    def delete_payment_dummy(self):
        """
        Function สำหรับลบเอกสาร payment dummy
        โดยจะลบเอกสารการชำระเงิน dummy ที่เลือก
        และปรับปรุงค่า amount_due_payment_dummy และ amount ของ payment.dummy ที่เหลืออยู่
        และแสดงข้อความแจ้งเตือนหากไม่มีเอกสารการชำระเงิน dummy ที่เลือก
        """
        for rec in self:

            # กรองเอกสารการชำระเงิน dummy ที่เลือก
            payment_dummy_ids = rec.payment_dummy_ids.filtered(lambda x: x.check_box)

            if not payment_dummy_ids:
                raise UserError(_("กรุณาเลือกรายการที่ต้องการลบ"))
            
            # รวมยอด amount ใน payment_dummy_ids
            rec.amount_due_payment_dummy += sum(payment_dummy.amount for payment_dummy in payment_dummy_ids)

            # ลบ record ออกจากฐานข้อมูลจริง
            payment_dummy_ids.unlink()

            amount = 0.00
            # ทำการ update ค่า amount_due ของ payment.dummy ใน payment_dummy_ids ทียังเหลืออยู่
            for payment_dummy in rec.payment_dummy_ids:
                amount = amount + payment_dummy.amount
                payment_dummy.amount_due = rec.net_total - amount


    def print_payment_receipt_pdf(self):
        """
        Function สำหรับพิมพ์ใบเสร็จรับเงิน
        โดยจะสร้างเอกสาร PDF สำหรับใบเสร็จรับเงิน
        และส่งกลับไปยัง client เพื่อให้สามารถดาวน์โหลดได้
        """
        return self.env.ref("nawakij_dummy_report.payment_receipt_report_dummy_th_pdf").report_action(self)
                

        


