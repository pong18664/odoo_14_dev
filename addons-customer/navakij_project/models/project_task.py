import logging
import re


from odoo import api, fields,tools, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError


class ProjectTask(models.Model):
    _inherit = 'project.task'


    navakij_sale_order_id = fields.Many2one('sale.order','Sale', tracking=True)
    navakij_purchase_order_id = fields.Many2one('purchase.order','Purchase', tracking=True)
    navakij_mrp_id = fields.Many2one('mrp.production','Manufacturing', tracking=True)
    navakij_invoice_id = fields.Many2one('account.move','Invoice', tracking=True)