import logging
import re

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = "stock.picking"


    picking_type_name = fields.Char(related="picking_type_id.name" ,string="picking type name")

    
    # function จัดรูปแบบ วัน/เดือน/ปี
    def get_formatted_date(self,date_data):
        if date_data:
            formatted_date = date_data.strftime('%d/%m/%Y')
            return formatted_date
        else:
            return False

    
    def print_receipt_report_TH(self):
        return self.env.ref('navakij_report.report_receipt_form_th_pdf').report_action(self)
    

    def print_receipt_report_ENG(self):
        return self.env.ref('navakij_report.report_receipt_form_eng_pdf').report_action(self)
    

    def print_delivery_report_TH(self):
        return self.env.ref('navakij_report.report_delivery_form_th_pdf').report_action(self)
    

    def print_delivery_report_ENG(self):
        return self.env.ref('navakij_report.report_delivery_form_eng_pdf').report_action(self)
    

    def print_pick_components_report_TH(self):
        return self.env.ref('navakij_report.report_pick_components_form_th_pdf').report_action(self)
    

    def print_pick_components_report_ENG(self):
        return self.env.ref('navakij_report.report_pick_components_form_eng_pdf').report_action(self)
    

    def print_store_finished_product_report_TH(self):
        return self.env.ref('navakij_report.report_store_finished_product_form_th_pdf').report_action(self)
    

    def print_store_finished_product_report_ENG(self):
        return self.env.ref('navakij_report.report_store_finished_product_form_eng_pdf').report_action(self)


    def print_store_raw_materials_report_TH(self):
        return self.env.ref('navakij_report.report_store_raw_materials_form_th_pdf').report_action(self)
        

    def print_store_raw_materials_report_ENG(self):
        return self.env.ref('navakij_report.report_store_raw_materials_form_eng_pdf').report_action(self)
        