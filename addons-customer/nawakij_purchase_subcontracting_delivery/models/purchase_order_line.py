from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    variant_bom_id = fields.Many2one(
        'mrp.bom',
        string='BoM',
        help='Variant BoM selected for this product.'
    )


    @api.onchange('product_id')
    def _get_variant_bom(self):
        """
        function สำหรับ set ค่า variant_bom_id อัตโนมัติเมื่อมีการเปลี่ยนแปลง product_id
        โดยจะเลือก BoM ที่มี type = 'subcontract' และ subcontractor_ids มี partner_id ของ PO line นี้
        """
        for rec in self:

            if rec.partner_id and rec.product_id:

                # variant_boms เก็บ BoM ที่ type = 'subcontract' และมี partner_id ของ PO ใน subcontractor_ids
                variant_boms = rec.product_id.variant_bom_ids.filtered(
                    lambda bom: rec.order_id.partner_id in bom.subcontractor_ids and bom.type == 'subcontract'
                )

                if variant_boms:
                    rec.variant_bom_id = variant_boms[0].id
                else:
                    # temp_boms เก็บ BoM ที่ type = 'subcontract' และมี partner_id ของ PO ใน subcontractor_ids
                    temp_boms = rec.product_id.bom_ids.filtered(
                    lambda bom: rec.order_id.partner_id in bom.subcontractor_ids and bom.type == 'subcontract'
                    )
                    
                    if temp_boms:
                        rec.variant_bom_id = temp_boms[0].id
                    else:
                        rec.variant_bom_id = False
            else:
                rec.variant_bom_id = False