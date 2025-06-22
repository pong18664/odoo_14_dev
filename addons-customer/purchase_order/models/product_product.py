import logging
import re


from odoo import api, fields,tools, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError


class ProductProduct(models.Model):
    _inherit = 'product.product'


    length = fields.Float(string='Length', compute="compute_length_and_width", digits=(0, 3))
    width = fields.Float(string='Width', compute="compute_length_and_width", digits=(0, 3))
    area = fields.Float(string='Area', compute='_compute_area', digits=(0, 3))
    id_product = fields.Integer(string='Product Id' , compute='_display_product_id')
    check_type_category = fields.Char(string='Check Type Category', compute='_check_type_category')
    product_variant_seller_ids = fields.One2many('product.supplierinfo', 'product_id')


    # เช็ค categ_id.type_category == glass , aluminium sheet , aluminium
    def _check_type_category(self):
        for rec in self:
            check_type_category = False
            if rec.categ_id:
                if rec.categ_id.type_category == "glass":
                    check_type_category = "glass"
                elif rec.categ_id.type_category == "aluminium sheet":
                    check_type_category = "aluminium sheet"
                elif rec.categ_id.type_category == "aluminium":
                    check_type_category = "aluminium"
            else :
                check_type_category = False
            rec.check_type_category = check_type_category


    # Show ID ของ Product
    def _display_product_id(self):
        for rec in self:
            rec.id_product = rec.id


    # คำนวณ field area
    def _compute_area(self):
        for rec in self:
            rec.area = rec.length * rec.width


    # function ปุ่มเมื่อกดปุ่มจะทำการดึงค่า variant มาใส่ใน field length และ field width 
    def compute_length_and_width(self):
        for rec in self:
            rec.length = 0.0
            rec.width = 0.0
            if rec.categ_id.type_category:
                try:
                    for product_template_attribute_value in rec.product_template_attribute_value_ids:
                    # attribute_value_ids อาจจะมีมากกว่า 1 และมีชื่ออย่างอื่นที่ไม่ต้องการได้การ split ตรงๆ คือ ผิด และ product_template_attribute_value_ids อาจจะมีมากกว่า 1 อันได้
                        keywords_to_check = ["Length", "length", "Area", "area"]
                        if any(keyword in product_template_attribute_value.display_name for keyword in keywords_to_check):
                            type_product = product_template_attribute_value.display_name.split(":")
                            if rec.categ_id.type_category == "aluminium":
                                if type_product[0] in  ["Length", "length"]:
                                    length = product_template_attribute_value.name
                                    rec.length = int(length) / 1000
                            elif rec.categ_id.type_category == "aluminium sheet" or "glass":
                                if type_product[0] in ["Area", "area"]:
                                    variant = product_template_attribute_value.name.split("x")
                                    length = variant[0].replace('m','')
                                    width = variant[1].replace('m','')
                                    rec.length = float(length) / 1000
                                    rec.width = float(width) / 1000
                except Exception as e:
                    print(e)
                    # raise ValidationError(_(f"{tax_group_old_amount}"))


    # function create product ได้เพิ่มส่วยของ compute_length_and_width()
    @api.model
    def create(self, vals):
        product = super(ProductProduct, self).create(vals)
        product.compute_length_and_width()
        return product

    
    
