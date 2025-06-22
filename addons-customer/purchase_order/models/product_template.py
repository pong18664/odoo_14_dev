import logging
import re


from odoo import api, fields,tools, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'


    @tools.ormcache()
    def _get_default_category_id(self):
    # Deletion forbidden (at least through unlink)
        return self.env.ref('product.product_category_all')

    @tools.ormcache()
    def _get_default_uom_id(self):
    # Deletion forbidden (at least through unlink)
        return self.env.ref('uom.product_uom_unit')

    secondary_uom_id = fields.Many2one('uom.uom', 'Secondary Unit of Measure',default=_get_default_uom_id, required=True, help="Default unit of measure used for all stock operations.")
    secondary_uom_name = fields.Char(string='Secondary Unit of Measure Name', related='uom_id.name', readonly=True)
    id_product = fields.Integer(string='Product Id' , compute='_display_product_id')

    # Show ID ของ Product
    def _display_product_id(self):
        for rec in self:
            rec.id_product = rec.id

    # คำนวณ field area
    def _compute_area(self):
        for rec in self:
            rec.area = rec.length * rec.width    


          


    


    