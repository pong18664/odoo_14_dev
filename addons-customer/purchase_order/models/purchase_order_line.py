import logging
import re
_logger = logging.getLogger(__name__)
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang, format_amount
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    product_name = fields.Text(string='Vendor Product Name', compute="_get_product_name" , store=True)
    product_code = fields.Text(string='Vendor Product Code', compute="_get_product_name" , store=True)
    product_variant = fields.Many2many('product.template.attribute.value', string='Product Variant', related='product_id.product_template_attribute_value_ids')
    secondary_product_uom = fields.Many2one('uom.uom', string='P UoM')
    p_quantity = fields.Float(string='P Quantity', digits=(0, 3))
    p_unit_price = fields.Float(string="P Unit Price")
    density = fields.Float(string="Density")
    type_product = fields.Text(string="Type product", compute="_get_type_product")
    price_unit_before_discount = fields.Float(string="Price Unit Before Discount", digits=(0, 3))
    discount = fields.Float(string="Discount%")


    @api.onchange('product_id')
    def get_analytic_account(self):
        """
        function นี้ทำงานเมื่อมีการเลือกหรือเปลี่ยนแปลง product_id
        โดยมี condition ที่เช็คว่า order_id.analytic_account_id มีค่าหรือไม่
        ถ้ามีค่าให้นำค่า order_id.analytic_account ไป update ที่ค่า line.account_analytic_id
        """        
        for line in self:
            if line.order_id.analytic_account_id:
                line.update({
                    'account_analytic_id': line.order_id.analytic_account_id.id
                })


    def _get_type_product(self):
        for rec in self:
            rec.type_product = rec.product_id.categ_id.type_category

    @api.onchange('order_id.requisition_id')
    def get_data_product(self):
        """
        ในกรณีที่ requisition_id ใน purchase order มีค่า
        ทำการดึงค่าจาก purchase agreement มาที่ purchase order
        """
        for line in self:
            if line.order_id.requisition_id:
                for agreement_line in line.order_id.requisition_id.line_ids:
                    if line.product_id == agreement_line.product_id:
                        line.update({
                            'p_quantity':agreement_line.p_quantity,
                            'p_unit_price':agreement_line.p_unit_price,
                            'density':agreement_line.density,
                            'price_unit':agreement_line.price_unit,
                        })


    @api.onchange('product_qty','p_unit_price','density','discount')
    def compute_price_unit_and_p_quantity(self):
        """
        Function คำนวณหาค่า p_quantity และ price_unit
        """
        for rec in self:
            if rec.product_id.categ_id.type_category == "aluminium":
                p_quantity_sum = rec.density * rec.product_id.length
                p_quantity = (rec.density * rec.product_id.length) * rec.product_qty
                unit_price = float(rec.p_unit_price) * float(p_quantity_sum)
                price_unit_before_discount = float(rec.p_unit_price) * float(p_quantity_sum)
                if rec.discount:
                    price_unit_after_discount = price_unit_before_discount - (price_unit_before_discount * (rec.discount / 100))
                    rec.update({
                        'p_quantity': p_quantity,
                        'price_unit': price_unit_after_discount if price_unit_after_discount > 0 else rec.price_unit - (rec.price_unit * (rec.discount / 100)),
                        'price_unit_before_discount': price_unit_before_discount,
                    })
                else :
                    rec.update({
                        'p_quantity': p_quantity,
                        'price_unit': unit_price,
                        'price_unit_before_discount': price_unit_before_discount,
                    })  

            elif rec.product_id.categ_id.type_category in ["glass", "aluminium sheet"]:
                p_quantity = rec.product_id.area * rec.product_qty
                unit_price = float(rec.p_unit_price) * float(rec.product_id.area)
                price_unit_before_discount = float(rec.p_unit_price) * float(rec.product_id.area)
                if rec.discount:
                    price_unit_after_discount = price_unit_before_discount - (price_unit_before_discount * (rec.discount / 100))
                    rec.update({
                        'p_quantity': p_quantity,
                        'price_unit': price_unit_after_discount if price_unit_after_discount > 0 else rec.price_unit - (rec.price_unit * (rec.discount / 100)),
                        'price_unit_before_discount': price_unit_before_discount,
                    })
                else :
                    rec.update({
                        'p_quantity': p_quantity,
                        'price_unit': unit_price,
                        'price_unit_before_discount': price_unit_before_discount,
                    })

            else :
                if rec.discount:
                    price_unit_after_discount = rec.price_unit - (rec.price_unit * (rec.discount / 100))
                    rec.update({
                        'price_unit': price_unit_after_discount,
                        'price_unit_before_discount': rec.price_unit,
                    })
                else :
                    rec.update({
                        'price_unit_before_discount': rec.price_unit,
                    })


    @api.onchange('product_id','order_id.partner_id')
    def _get_product_name(self):
        """
        ฟังก์ชันนี้จะทำงานเมื่อ product_id และ order_id.partner_id มีการเปลียนแปลง
        ฟังก์ชันนี้ทำการ หาค่าของ field product_name , product_code , p_unit_price จาก model product.supplierinfo
        เพื่อมาแสดงที่ field product_name , product_code , p_unit_price ของ model purchase.order.line
        โดยมี condition product_id ของ model product.supplierinfo เท่ากับ product_id ของ model purchase.order.line
        และ name ของ model product.supplierinfo เท่ากับ partner_id ของ model purchase.order
        """
        for rec in self:
            if rec.product_id and rec.order_id.partner_id:
                product_name = False
                product_code = False
                p_unit_price = False
                density = False
                
                seller = rec.env['product.supplierinfo'].search([
                    ('product_id' , '=' , rec.product_id.id),
                    ('name', '=' , rec.order_id.partner_id.id)
                    ])
                if(not seller):           
                    seller = rec.env['product.supplierinfo'].search([
                        ('product_tmpl_id' , '=' , rec.product_id.product_tmpl_id.id),
                        ('name', '=' , rec.order_id.partner_id.id)
                        ])
                    if seller:
                        product_name = seller.product_name
                        product_code = seller.product_code                       
                        p_unit_price = seller.p_unit_price
                        density = seller.density

                else:
                    product_name = seller.product_name
                    product_code = seller.product_code                    
                    p_unit_price = seller.p_unit_price
                    density = seller.density
                                
                rec.product_name = product_name
                rec.product_code = product_code
                rec.p_unit_price = p_unit_price
                rec.density = density
               
            else:
                rec.product_name = False
                rec.product_code = False
                rec.p_unit_price = False
                rec.density = False      
                

    @api.onchange('product_id')
    def _secondary_product_uom(self):
        """
        เป็นฟังก์ชันที่นำค่า field secondary_uom_id in product มาใส่ให้กับ 
        field secondary_product_uom in purchase.order.line เพื่อให้รู้ว่า มีหน่วยเป็นอะไร
        เช่น มีหน่วยเป็น Unit , Kg. and Orther
        """
        secondary_product_uom = False
        for line in self:
            if line.product_id:
                secondary_product_uom = line.product_id.secondary_uom_id
                line.secondary_product_uom = secondary_product_uom
            else:
                line.secondary_product_uom = False
        # raise ValidationError(_(f"{line.secondary_product_uom}"))
                

    @api.onchange('product_qty', 'product_uom',)
    def _onchange_quantity(self):
        if not self.product_id or self.invoice_lines:
            return
        params = {'order_id': self.order_id}
        seller = self.product_id._select_seller(
            partner_id=self.partner_id,
            quantity=self.product_qty,
            date=self.order_id.date_order and self.order_id.date_order.date(),
            uom_id=self.product_uom,
            params=params)

        if seller or not self.date_planned:
            self.date_planned = self._get_date_planned(seller).strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        # If not seller, use the standard price. It needs a proper currency conversion.
        if not seller: 
            po_line_uom = self.product_uom or self.product_id.uom_po_id
            price_unit = self.env['account.tax']._fix_tax_included_price_company(
                self.product_id.uom_id._compute_price(self.product_id.standard_price, po_line_uom),
                self.product_id.supplier_taxes_id,
                self.taxes_id,
                self.company_id,
            )
            if price_unit and self.order_id.currency_id and self.order_id.company_id.currency_id != self.order_id.currency_id:
                price_unit = self.order_id.company_id.currency_id._convert(
                    price_unit,
                    self.order_id.currency_id,
                    self.order_id.company_id,
                    self.date_order or fields.Date.today(),
                )
            # self.p_unit_price = self.p_unit_price
            # self.price_unit = price_unit   
            return

        price_unit = self.env['account.tax']._fix_tax_included_price_company(seller.price, self.product_id.supplier_taxes_id, self.taxes_id, self.company_id) if seller else 0.0
        if price_unit and seller and self.order_id.currency_id and seller.currency_id != self.order_id.currency_id:
            price_unit = seller.currency_id._convert(
                price_unit, self.order_id.currency_id, self.order_id.company_id, self.date_order or fields.Date.today())

        if seller and self.product_uom and seller.product_uom != self.product_uom:
            price_unit = seller.product_uom._compute_price(price_unit, self.product_uom)
        
        self.price_unit = price_unit
        
        default_names = []
        vendors = self.product_id._prepare_sellers({})
        for vendor in vendors:
            product_ctx = {'seller_id': vendor.id, 'lang': get_lang(self.env, self.partner_id.lang).code}
            default_names.append(self._get_product_purchase_description(self.product_id.with_context(product_ctx)))

        if (self.name in default_names or not self.name):
            product_ctx = {'seller_id': seller.id, 'lang': get_lang(self.env, self.partner_id.lang).code}
            self.name = self._get_product_purchase_description(self.product_id.with_context(product_ctx))

        # เป็นส่วนที่คำนวณหาค่า price_unit and p_quantity
        for rec in self:
            rec.compute_price_unit_and_p_quantity()
            
        # เป็นส่วนที่คำนวณหาค่า price_unit and p_quantity
        # for line in self:
        #     density = 1
        #     p_unit_price = 1
        #     seller = line.env['product.supplierinfo'].search([
        #             ('product_id' , '=' , line.product_id.id),
        #             ('name', '=' , line.order_id.partner_id.id)
        #             ])
        #     if(not seller):           
        #         seller = line.env['product.supplierinfo'].search([
        #             ('product_tmpl_id' , '=' , line.product_id.product_tmpl_id.id),
        #             ('name', '=' , line.order_id.partner_id.id)
        #             ])
        #         if seller:
        #             density = seller.density
        #             p_unit_price = seller.p_unit_price
        #     else:
        #         density = seller.density
        #         p_unit_price = seller.p_unit_price
                
                
        #     # ถ้า product_id.categ_id.type_category == "glass" or "aluminium sheet" จะคำนวณตามนี้
        #     if line.product_id.categ_id.type_category in ["glass", "aluminium sheet"]:
        #         p_quantity = line.product_id.area * line.product_qty
        #         unit_price = float(p_unit_price) * float(line.product_id.area)
        #         # raise ValidationError(_(f"{unit_price}"))
        #         line.update({
        #             'p_quantity': p_quantity,
        #             'price_unit': unit_price,
        #         })

        #     # ถ้า product_id.categ_id.type_category == "aluminium" จะคำนวณตามนี้
        #     if line.product_id.categ_id.type_category == "aluminium":                
        #         p_quantity_sum = density * line.product_id.length
        #         p_quantity = (density * line.product_id.length) * line.product_qty
        #         unit_price = float(p_unit_price) * float(p_quantity_sum)
        #         line.update({
        #             'p_quantity': p_quantity,
        #             'price_unit': unit_price,
        #         })


    @api.model
    def create(self, vals):
        product = super(PurchaseOrderLine, self).create(vals)
        product._get_product_name()
        product._onchange_quantity()
        product._secondary_product_uom()
        product.get_data_product()
        # raise ValidationError(_(f"{vals}"))
        return product
    
    
    def write(self, values):
        if 'display_type' in values and self.filtered(lambda line: line.display_type != values.get('display_type')):
            raise UserError(_("You cannot change the type of a purchase order line. Instead you should delete the current line and create a new line of the proper type."))

        if 'product_qty' in values:
            for line in self:
                if line.order_id.state == 'purchase':
                    line.order_id.message_post_with_view('purchase.track_po_line_template',
                                                         values={'line': line, 'product_qty': values['product_qty']},
                                                         subtype_id=self.env.ref('mail.mt_note').id)
        if 'qty_received' in values:
            for line in self:
                line._track_qty_received(values['qty_received'])

        # เพิ่มเติมส่วนของ if 'price_unit' in values:
        # if 'price_unit' in values:
        #     for line in self:
        #         density = 1
        #         p_unit_price = 1
        #         seller = line.env['product.supplierinfo'].search([
        #                 ('product_id' , '=' , line.product_id.id),
        #                 ('name', '=' , line.order_id.partner_id.id)
        #                 ])
        #         if(not seller):           
        #             seller = line.env['product.supplierinfo'].search([
        #                 ('product_tmpl_id' , '=' , line.product_id.product_tmpl_id.id),
        #                 ('name', '=' , line.order_id.partner_id.id)
        #                 ])
        #             if seller:
        #                 density = seller.density
        #                 p_unit_price = seller.p_unit_price     
        #         else:
        #             density = seller.density
        #             p_unit_price = seller.p_unit_price

        #         if line.product_id.categ_id.type_category in ["glass", "aluminium sheet"]:
        #             unit_price = float(p_unit_price) * float(line.product_id.area)
        #             values['price_unit'] = unit_price 

        #         if line.product_id.categ_id.type_category == "aluminium":                
        #             p_quantity_sum = density * line.product_id.length
        #             unit_price = float(p_unit_price) * float(p_quantity_sum)
        #             values['price_unit'] = unit_price 

        
        # raise ValidationError(_(f"{values}"))
        return super(PurchaseOrderLine, self).write(values)
    

