from odoo import _, api, models
from odoo.exceptions import UserError


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    _LOCKED_MESSAGE = _(
        "You cannot add or remove attachments on a confirmed purchase order."
    )

    @api.model
    def create(self, vals_list):
        records_vals = vals_list if isinstance(vals_list, list) else [vals_list]
        self._check_purchase_state_in_vals(records_vals)
        return super().create(vals_list)

    def write(self, vals):
        if 'res_model' in vals or 'res_id' in vals:
            self._check_purchase_state_on_write(vals)
        return super().write(vals)

    def unlink(self):
        self._ensure_not_linked_to_confirmed_po()
        return super().unlink()

    # Helpers
    def _check_purchase_state_in_vals(self, vals_list):
        purchase_vals = [
            vals
            for vals in vals_list
            if vals.get('res_model') == 'purchase.order' and vals.get('res_id')
        ]
        if not purchase_vals:
            return

        purchase_orders = self.env['purchase.order'].browse(
            [vals['res_id'] for vals in purchase_vals]
        )
        self._raise_if_any_locked_po(purchase_orders)

    def _check_purchase_state_on_write(self, vals):
        purchase_order_model = 'purchase.order'
        res_model = vals.get('res_model')
        res_id = vals.get('res_id')

        if res_model == purchase_order_model and res_id:
            purchase_order = self.env['purchase.order'].browse(res_id)
            self._raise_if_any_locked_po(purchase_order)
            return

        if res_model is None and res_id is None:
            return

        purchase_attachments = self.filtered(
            lambda rec: rec.res_model == purchase_order_model and rec.res_id
        )
        if purchase_attachments:
            purchase_orders = self.env['purchase.order'].browse(
                purchase_attachments.mapped('res_id')
            )
            self._raise_if_any_locked_po(purchase_orders)

    def _ensure_not_linked_to_confirmed_po(self):
        purchase_attachments = self.filtered(
            lambda rec: rec.res_model == 'purchase.order' and rec.res_id
        )
        if not purchase_attachments:
            return

        purchase_orders = self.env['purchase.order'].browse(
            purchase_attachments.mapped('res_id')
        )
        self._raise_if_any_locked_po(purchase_orders)

    def _raise_if_any_locked_po(self, purchase_orders):
        if any(po.state == 'purchase' for po in purchase_orders):
            raise UserError(self._LOCKED_MESSAGE)