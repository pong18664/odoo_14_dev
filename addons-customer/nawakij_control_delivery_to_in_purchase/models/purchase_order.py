from odoo import api, fields, models, SUPERUSER_ID, _ 
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.addons.purchase.models.purchase import PurchaseOrder as Purchase


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'


    picking_type_id = fields.Many2one(
        'stock.picking.type',
        string='Deliver To',
        required=True,
        domain="[('warehouse_id', '=', warehouse_id), ('warehouse_id.company_id', '=', company_id)]",
        help="This will determine operation type used for incoming shipment",
    )
    support_picking_type_id = fields.Many2one(
        'stock.picking.type', 'Deliver To',
        compute='_get_default_support_picking_type_id',
        help="field นี้สร้างเพื่อกำหนดค่า defult ตอนสร้างเอกสารให้กับ picking_type_id")


    def _get_default_support_picking_type_id(self):
        """
        Function สำหรับกำหนดค่าให้กับ support_picking_type_id
        โดยจะกำหนดค่าเป็น picking_type_id ถ้า state ไม่ใช่ 'draft'
        ถ้า state เป็น 'draft' จะกำหนดค่า support_picking_type_id เป็น False
        และถ้า picking_type_id มีค่า จะกำหนด support_picking_type_id เป็น picking_type_id
        """
        for rec in self:
            rec.support_picking_type_id = rec.picking_type_id if rec.state != 'draft' else False

            # ถ้า picking_type_id มีค่า ให้กำหนด support_picking_type_id เป็น picking_type_id
            if rec.picking_type_id:
                rec.support_picking_type_id = rec.picking_type_id


    @api.onchange('support_picking_type_id')
    def onchange_support_picking_type_id(self):
        """
        Function สำหรับถ้า support_picking_type_id มีการเปลี่ยนแปลง
        ให้กำหนดค่า picking_type_id = support_picking_type_id
        """
        for rec in self:
            rec.picking_type_id = rec.support_picking_type_id


