import logging
import re

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "account.move"


    select_tax_invoice_id = fields.Many2one(
        "account.move.tax.invoice", 
        string="Document to be printed", 
        copy=False,
        domain="[('id', 'in', tax_invoice_ids)]",                               
        help=""
    )


    def old_invoice_data(self):
        """
        ฟังก์ชั่นนี้ใช้เพื่อดึงข้อมูลใบแจ้งหนี้เก่าจาก ref ของการเคลื่อนไหว
        """
        for move in self:
            invoice_name = move.ref.split('Reversal of: ')[1].split(',')[0]
            invoice_data = self.env['account.move'].search([('name', '=', invoice_name)], limit=1)
            return invoice_data
        

    def old_get_invoice_date(self):
        """
        ฟังก์ชั่นนี้ใช้เพื่อดึงวันที่ของใบแจ้งหนี้เก่าจากข้อมูลที่เก็บไว้ใน ref
        """
        for move in self:
            invoice_data = move.old_invoice_data()
            if invoice_data:
                return invoice_data.invoice_date
            else:
                return 
            

    def old_get_invoice_amount_untaxes(self):
        """
        ฟังก์ชั่นนี้ใช้เพื่อดึงจำนวนเงินที่ไม่รวมภาษีของใบแจ้งหนี้เก่าจากข้อมูลที่เก็บไว้ใน ref
        """
        for move in self:
            invoice_data = move.old_invoice_data()
            if invoice_data:
                return invoice_data.amount_untaxed
            else:
                return 0.0

    
    def sort_item_lines_by_sequence(self):
        """
        ฟังก์ชั่นสําหรับเรียงลำดับบรรทัดตาม sequence
        และกรองบรรทัดที่มี quantity == 0 ออก
        """
        invoice_line = self.invoice_line_ids.sorted(key=lambda line: line.sequence)  # เรียงลำดับบรรทัดตาม sequence
        invoice_line = invoice_line.filtered(lambda line: line.quantity != 0)   # กรองออกบรรทัดที่มี quantity == 0 ออก
        return invoice_line


    def get_lines_without_product_id(self):
        """
        จัดกลุ่มบรรทัดตาม 'name' ที่ไม่มี 'product_id' และรวมข้อมูลบรรทัดที่เกี่ยวข้องที่มี 'product_id'
        คืนค่ารายการของข้อมูลที่จัดกลุ่มในรูปแบบของ list ที่มี dictionary
        """
        grouped_lines = []  # รายการสำหรับเก็บข้อมูลที่จัดกลุ่ม
        current_group = None  # กลุ่มปัจจุบัน
        uom = None  # หน่วยสินค้า
        group_quantity = 0  # จำนวนรวมในกลุ่ม
        group_price_unit = 0  # ราคาต่อหน่วยรวมในกลุ่ม
        group_price_subtotal = 0  # ราคารวมในกลุ่ม
        invoice_line = self.invoice_line_ids.sorted(key=lambda line: line.sequence)  # เรียงลำดับบรรทัดตาม sequence

        for line in invoice_line:
            if line.quantity == 0:  # เริ่มกลุ่มใหม่เมื่อพบบรรทัดที่ quantity = 0
                if current_group:  # ถ้ามีกลุ่มปัจจุบันอยู่ ให้เพิ่มกลุ่มก่อนหน้าไปยังผลลัพธ์
                    grouped_lines.append({
                        "name": current_group,
                        "uom": uom,
                        "quantity": group_quantity,
                        "price_unit": group_price_unit,
                        "price_subtotal": group_price_subtotal,
                    })

                # ตั้งค่าใหม่สำหรับกลุ่มใหม่
                first_name = line.name.split('**')[0] if '**' in line.name else line.name
                second_name = line.name.split('**')[1] if '**' in line.name else ''
                current_group = first_name
                uom = second_name
                group_quantity = 0
                group_price_unit = 0
                group_price_subtotal = 0
            else:  # รวมข้อมูลของบรรทัดที่มี product_id ในกลุ่มปัจจุบัน
                group_quantity += line.quantity
                group_price_unit += line.price_unit
                group_price_subtotal += line.price_subtotal

        # เพิ่มกลุ่มสุดท้ายไปยังผลลัพธ์
        if current_group:
            grouped_lines.append({
                "name": current_group,
                "uom": uom,
                "quantity": group_quantity,
                "price_unit": group_price_unit,
                "price_subtotal": group_price_subtotal,
            })

        return grouped_lines


    def get_formatted_date(self,date_data):
        """
        function จัดรูปแบบ วัน/เดือน/ปี
        """
        if date_data:
            formatted_date = date_data.strftime('%d/%m/%Y')
            return formatted_date
        else:
            return False


    def print_report_invoice_TH(self):
        """
        เป็น function action ไปที่ external id ใน data/report_data.xml
        """
        return self.env.ref('navakij_report.report_invoice_form_th_pdf').report_action(self)
    

    def print_report_invoice_ENG(self):
        """
        เป็น function action ไปที่ external id ใน data/report_data.xml
        """
        return self.env.ref('navakij_report.report_invoice_form_eng_pdf').report_action(self)
    

    def print_report_tax_invoice_TH(self):
        """
        เป็น function action ไปที่ external id ใน data/report_data.xml
        """        
        return self.env.ref('navakij_report.report_tax_invoice_form_th_pdf').report_action(self)
    

    def print_report_tax_invoice_ENG(self):
        """
        เป็น function action ไปที่ external id ใน data/report_data.xml
        """
        return self.env.ref('navakij_report.report_tax_invoice_form_eng_pdf').report_action(self)
    

    def print_report_billing_note_TH(self):
        """
        เป็น function action ไปที่ external id ใน data/report_data.xml
        """
        return self.env.ref('navakij_report.report_billing_note_form_th_pdf').report_action(self)



