import logging
import re

from collections import defaultdict
from odoo import api, fields,tools, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    
    def action_cancel(self,show_wizard=True):
        """ Cancels production order, unfinished stock moves and set procurement
        orders in exception """
        self.workorder_ids.filtered(lambda x: x.state not in ['done', 'cancel']).action_cancel()
        if show_wizard: 
            return {
                'name': _('Cancel Manufacturing'),
                'view_mode': 'form',
                'res_model': 'manufacturing.order.cancel',
                'view_id': self.env.ref('nawakij_notification_of_cancellation_confirmation.manufacturing_order_cancel_view_form').id,
                'type': 'ir.actions.act_window',
                'context': {'default_mrp_production_id': self.id},
                'target': 'new'
                }
        if not self.move_raw_ids:
            self.state = 'cancel'
            return True
        self._action_cancel()
        return True
    