import logging
import re

from itertools import groupby
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.float_utils import float_is_zero

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'


    def button_cancel(self,show_wizard=True):
        for order in self:
            for inv in order.invoice_ids:
                if inv and inv.state not in ('cancel', 'draft'):
                    raise UserError(_("Unable to cancel this purchase order. You must first cancel the related vendor bills."))
        if show_wizard: 
            return {
                'name': _('Cancel Purchase Order'),
                'view_mode': 'form',
                'res_model': 'purchase.order.cancel',
                'view_id': self.env.ref('nawakij_notification_of_cancellation_confirmation.purchase_order_cancel_view_form').id,
                'type': 'ir.actions.act_window',
                'context': {'default_purchase_id': self.id},
                'target': 'new'
                }
        else:
            self.write({'state': 'cancel', 'mail_reminder_confirmed': False})

