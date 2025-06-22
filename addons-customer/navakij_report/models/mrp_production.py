import logging
import re
import datetime
import pytz

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError

_logger = logging.getLogger(__name__)


class MrpProduction(models.Model):
    _inherit = "mrp.production"


    def date_now(self):
        time = datetime.datetime.now().strftime('%d/%m/%Y %I:%M%p')
        return time
    

    def get_data_product_length(self,product_id):
        """
        function ดึงค่า attribute length ของ product
        """
        for product in product_id:
            if product.product_template_attribute_value_ids:
                for attribute in product.product_template_attribute_value_ids:
                    if 'Area' in attribute.display_name:
                        length = attribute.name.split("x")
                        return length[0]
                    elif 'Length' in attribute.display_name:
                        length = attribute.name
                        return length
        return False


    def get_data_product_width(self,product_id):
        """
        function ดึงค่า attribute width ของ product
        """
        for product in product_id:
            if product.product_template_attribute_value_ids:
                for attribute in product.product_template_attribute_value_ids:
                    if 'Area' in attribute.display_name:
                        width = attribute.name.split("x")
                        return width[1]
        return False
                    

    def get_data_product_color(self,product_id):
        """
        function ดึงค่า attribute colour ของ product
        """
        for product in product_id:
            if product.product_template_attribute_value_ids:
                for attribute in product.product_template_attribute_value_ids:
                    if 'Colour' in attribute.display_name:
                        color = attribute.name
                        return color
        return False


    def get_transfers(self, picking_ids):
        """
        function หา PC in picking_ids.name
        ที่เชื่อมกับ mrp.production 
        """
        picking_name = []
        for picking in picking_ids:
            if 'PC' in picking.name:
                picking_name.append(picking.name)
        return picking_name
                # raise ValidationError(_(f"{picking.name}"))


    # function จัดรูปแบบ วัน/เดือน/ปี
    def get_formatted_date(self,date_data):
        if date_data:
            formatted_date = date_data.strftime('%d/%m/%Y')
            return formatted_date
        else:
            return False
        

    # function จัดรูปแบบ วัน/เดือน/ปี และ เวลา
    def get_formatted_date_and_time(self, date_data):
        if date_data:
            # Time zone ของ UTC และไทย
            utc_tz = pytz.timezone('UTC')
            thai_tz = pytz.timezone('Asia/Bangkok')

            # ใส่ time zone ของ UTC ให้กับ datetime object
            utc_time = utc_tz.localize(date_data)

            # แปลงเวลาเป็น time zone ของไทย
            local_time = utc_time.astimezone(thai_tz)

            # จัดรูปแบบวันที่และเวลาให้สวยงาม
            formatted_date = local_time.strftime('%d/%m/%Y %H:%M:%S')
            return formatted_date
        else:
            return False


    def print_manufacturing_TH(self):
        return self.env.ref('navakij_report.report_manufacturing_form_th_pdf').report_action(self)
    

    def print_manufacturing_ENG(self):
        return self.env.ref('navakij_report.report_manufacturing_form_eng_pdf').report_action(self)
    