import logging
import re


from odoo import api, fields,tools, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'


    analytic_account_id = fields.Many2one('account.analytic.account',string='Analytic Account')
    mrp_production_count = fields.Integer(
        string='Count Mrp Production', compute="get_mrp_production_count")
    internal_detail = fields.Char(string="Internal Detail", index=True)
  

    # หาค่าของ field name ของ mrp.production ที่ตรงกับ field origin ของ purchase.requisition 
    def get_mrp_production_count(self):
        self.mrp_production_count = len(
            self.env['mrp.production'].search([("name", "=", self.origin)]))
        
    # เป็น function action พาเปลี่ยนหน้าไปตามที่ระบุ external id ไว้ และแสดงข้อมูลตามเงื่อนไขที่กำหนดไว้ที่ domain 
    # ค่าของ field name ของ mrp.production ที่ตรงกับ field origin ของ purchase.requisition
    def action_view_mrp_production(self):
        action = self.env["ir.actions.actions"]._for_xml_id("mrp.mrp_production_action")
        action['domain'] = [("name", "=", self.origin)]
        return action
    

    @api.onchange('analytic_account_id')
    def onchange_analytic_account(self):
        """
        เป็น Function กำหนดค่าให้กับ field account_analytic_id ใน purchase.requisition.line
        """
        for order in self:
            for line in order.line_ids:
                line.account_analytic_id = order.analytic_account_id



class PurchaseRequisitionLine(models.Model):
    _inherit = 'purchase.requisition.line'


    p_quantity = fields.Float(string='P Quantity', digits=(0, 3))
    p_unit_price = fields.Float(string="P Unit Price")
    density = fields.Float(string="Density")
    secondary_product_uom = fields.Text(string='P UoM')
    type_product = fields.Text(string="Type product", compute="_get_type_product")


    def _get_type_product(self):
        for rec in self:
            rec.type_product = rec.product_id.categ_id.type_category

    
    @api.onchange('product_id')
    def _get_data_product(self):
        """
        Function สำหรับดึงค่า p_unit_price , density , price , secondary_product_uom
        จาก seller
        """
        secondary_product_uom = False
        for line in self:
            # ส่วนของดึงค่า p_unit_price , density , price
            if line.product_id and line.requisition_id.vendor_id:
                seller = line.env['product.supplierinfo'].search([
                        ('product_id' , '=' , line.product_id.id),
                        ('name', '=' , line.requisition_id.vendor_id.id)
                        ])
                if seller:
                    if line.product_id.categ_id.type_category in ["aluminium","glass", "aluminium sheet"]:
                        line.p_unit_price = seller.p_unit_price
                        line.density = seller.density
                    else:
                        line.price_unit = seller.price
                else:
                    seller_all = line.env['product.supplierinfo'].search([
                            ('product_id' , '=' , line.product_id.id)])
                    if seller_all:
                        if line.product_id.categ_id.type_category in ["aluminium","glass", "aluminium sheet"]:
                            line.p_unit_price = seller_all[0].p_unit_price
                            line.density = seller_all[0].density
                        else:
                            line.price_unit = seller_all[0].price    
                    else:
                        line.p_unit_price = False
                        line.density = False    
            else:
                seller_all = line.env['product.supplierinfo'].search([
                        ('product_id' , '=' , line.product_id.id)])
                if seller_all:
                    if line.product_id.categ_id.type_category in ["aluminium","glass", "aluminium sheet"]:
                        line.p_unit_price = seller_all[0].p_unit_price
                        line.density = seller_all[0].density
                    else:
                        line.price_unit = seller_all[0].price 
                else:
                    line.p_unit_price = False
                    line.density = False 

            # ส่วนของดึงค่า secondary_product_uom
            if line.product_id:
                secondary_product_uom = line.product_id.secondary_uom_id.name
                line.secondary_product_uom = secondary_product_uom
            else:
                line.secondary_product_uom = False
                
    @api.onchange('product_id','product_qty','p_unit_price','density')               
    def _compute_price_unit(self):
        """
        Function คำนวณหาค่า p_quantity กับ unit_price 
        สำหรับ product type ที่เท่ากับ aluminium , glass , aluminium sheet
        """
        for line in self:
            if line.product_id.categ_id.type_category == "aluminium":                
                p_quantity_sun = line.density * line.product_id.length
                p_quantity = (line.density * line.product_id.length) * line.product_qty
                unit_price = float(line.p_unit_price) * float(p_quantity_sun)
                line.update({
                    'p_quantity': p_quantity,
                    'price_unit': unit_price,
                })

            if line.product_id.categ_id.type_category in ["glass", "aluminium sheet"]:
                p_quantity = line.product_id.area * line.product_qty
                unit_price = float(line.p_unit_price) * float(line.product_id.area)
                line.update({
                    'p_quantity': p_quantity,
                    'price_unit': unit_price,
                })
