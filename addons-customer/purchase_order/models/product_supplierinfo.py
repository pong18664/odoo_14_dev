import logging
import re

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError

_logger = logging.getLogger(__name__)

class SupplierInfo(models.Model):
    _inherit = 'product.supplierinfo'

    p_unit_price = fields.Float(string="P Unit Price")
    density = fields.Float(string='Density', digits=(0, 4))
    invisible_density = fields.Boolean(string="Invisible Density",compute='_compute_invisible_density')
    variant = fields.Many2many('product.template.attribute.value', string='Variant', related='product_id.product_template_attribute_value_ids') 


    @api.onchange('product_name','product_code')
    def update_data_supplier_purchase(self):
        """
        ถ้า product_name หรือ product_code ใน model'product.supplierinfo'
        มีการเปลี่ยนแปลงให้ update ข้อมูลไปที่ purchase
        conditions search purchase:
            - state ต้องเท่ากับ draft
            - partner_id ของ PO ต้องเท่ากับ partner_id ของ Supplier 
            - order_line.product_id ต้องเท่ากับ product_id ของ Supplier
        """
        for rec in self:
            product_id = rec.product_id.id_product
            purchase = rec.env['purchase.order'].search([
                # ('state', '=', 'draft'),
                ('partner_id', '=', rec.name.id),
                ('order_line.product_id', '=', product_id)
            ])

            if purchase:
                order_lines = purchase.mapped('order_line').filtered(lambda line: line.product_id.id == product_id)
                for order_line in order_lines:
                    order_line.write({
                        'product_name': rec.product_name,
                        'product_code': rec.product_code
                    })


    @api.onchange('product_id.categ_id', 'product_tmpl_id.categ_id')
    def _compute_invisible_density(self):
        # กำหนดค่าให้ field invisible_density 
        # ถ้า product_id.categ_id.type_category == "glass" 
        # หรือ product_tmpl_id.categ_id.type_category == "glass"
        # field invisible_density จะเท่ากับ True
        for seller in self:
            if seller.product_id.categ_id.type_category == "glass":
                invisible_density = True
            elif seller.product_tmpl_id.categ_id.type_category == "glass":
                invisible_density = True
            else:
                invisible_density = False
            seller.invisible_density = invisible_density


    # def create(self, vals_list):
    #     """
    #     Override to set product_tmpl_id when creating a supplierinfo.
    #     product_tmpl_id is set based on the product_id given in vals_list.
    #     This is necessary because the product_tmpl_id is not given in the vals_list
    #     when creating a supplierinfo from the product form.
    #     """
    #     for vals in vals_list:
    #         # ตรวจสอบว่า product_id มีค่าและไม่ใช่ None
    #         if 'product_id' in vals and vals['product_id']:
    #             product = self.env['product.product'].browse(vals['product_id'])
    #             # ตรวจสอบว่า product มีค่า product_tmpl_id
    #             if product.exists():
    #                 vals['product_tmpl_id'] = product.product_tmpl_id.id
    #             else:
    #                 _logger.warning(f"Product with ID {vals['product_id']} does not exist.")
    #         else:
    #             _logger.warning("Missing 'product_id' in vals_list.")
    #     # เรียกใช้งาน super เพื่อสร้าง supplierinfo
    #     supplierinfo = super(SupplierInfo, self).create(vals_list)
    #     return supplierinfo
                
            