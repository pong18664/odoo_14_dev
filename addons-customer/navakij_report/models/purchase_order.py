import logging
import re

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    
    def get_formatted_date(self,date_data):
        """
        function จัดรูปแบบ วัน/เดือน/ปี
        """
        if date_data:
            formatted_date = date_data.strftime('%d/%m/%Y')
            return formatted_date
        else:
            return False
        

    def print_report_po_TH(self):
        return self.env.ref('navakij_report.report_purchase_order_form_th_pdf').report_action(self)
    

    def print_report_po_ENG(self):
        return self.env.ref('navakij_report.report_purchase_order_form_eng_pdf').report_action(self)
    

    @api.model
    def amount_to_text_th(self, amount):
        """
        ฟังก์ชั่นแปลงจํานวนเงินเป็นภาษาไทย
        """
        units_name = [('บาท', 'สตางค์')]
        num_word = ['ศูนย์', 'หนึ่ง', 'สอง', 'สาม', 'สี่', 'ห้า', 'หก', 'เจ็ด', 'แปด', 'เก้า']
        position = ['', 'สิบ', 'ร้อย', 'พัน', 'หมื่น', 'แสน', 'ล้าน']

        if amount == 0:
            return 'ศูนย์บาทถ้วน'

        text = ''
        int_part, frac_part = str(amount).split('.')
        int_part = int(int_part)
        frac_part = int(frac_part)

        text += self.num_to_word(int_part, num_word, position, units_name[0][0])

        if frac_part > 0:
            text += self.num_to_word(frac_part, num_word, position, units_name[0][1])
        else:
            text += 'ถ้วน'
        
        return text

    def num_to_word(self, num, num_word, position, unit):
        """
        ฟังก์ชันสําหรับแปลงจํานวนเป็นตัวอักษร
        """
        if num == 0:
            return ''
        
        words = []
        digits = [int(d) for d in str(num)]
        digits.reverse()

        for i in range(len(digits)):
            if digits[i] != 0:
                words.append(num_word[digits[i]] + position[i])

        words.reverse()
        return ''.join(words) + unit