import logging
import re
import json

from datetime import datetime
from odoo import api, fields,tools, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from collections import defaultdict
# raise ValidationError(_(f"{workorder.check_yes_or_no}"))
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'
    

    @api.model
    def _search_default_journal(self, journal_types):
        """
        Overrides the default behavior to use the company's default journal for
        out_retention type moves.
        """
        journal = super(AccountMove, self)._search_default_journal(journal_types)
        
        # ตรวจสอบ move_type ใน context
        move_type = self._context.get('default_move_type')
        if move_type == 'out_retention':
            retention_journal = self.env.company.journal_default_id
            if retention_journal:
                journal = retention_journal

        return journal


    retention = fields.Monetary(string="Retention")
    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account")
    po_no = fields.Char(string="PO No.")
    advance_no = fields.Char(string="ADV No.")
    internal_detail = fields.Char(string="Internal Detail")
    inv = fields.Boolean(string="Invoice", default=False, copy=False)
    tax_inv = fields.Boolean(string="Tax Invoice", default=False, copy=False)
    delivery_address = fields.Char(string="Delivery Address")
    count_retention = fields.Integer(string="Count Retention", store=True, copy=False, default=0)
    count_invoice = fields.Integer(string="Count Invoice", store=True, copy=False, default=0)
    state_invoice = fields.Selection([
        ('not_invoiced', 'Not Invoiced'),
        ('invoice_done', 'Invoice Done'),
    ], default='not_invoiced', copy=False, string="State Invoice")

    # compute field   
    wht = fields.Monetary(string="WHT", compute="_compute_wht",store=True)
    net_total = fields.Monetary(string="Net Total", compute="_compute_net_total", store=True)
    show_button_retention = fields.Boolean(compute="_show_button_retention", store=True, default=False)

    # edit from original field
    move_type = fields.Selection(selection=[
            ('entry', 'Journal Entry'),
            ('out_invoice', 'Customer Invoice'),
            ('out_refund', 'Customer Credit Note'),
            ('in_invoice', 'Vendor Bill'),
            ('in_refund', 'Vendor Credit Note'),
            ('out_receipt', 'Sales Receipt'),
            ('in_receipt', 'Purchase Receipt'),
            ('out_retention', 'Retention'), # เพิ่ม
        ], string='Type', required=True, store=True, index=True, readonly=True, tracking=True,
        default="entry", change_default=True)


    def custom_state_invoice(self):
        """
        ฟังก์ชั่นสําหรับเปลี่ยน state invoice
        """
        for rec in self:
            rec.state_invoice = 'invoice_done'


    def custom_count_invoice(self):
        """
         ค้นหาชื่อของเอกสาร retention ว่ามีอยู่ใน field ref ของเอกสาร invoice
         และ count จํานวนเอกสาร invoice
        """
        for rec in self:
            rec.count_invoice = len(self.env['account.move'].search([('ref', 'ilike', rec.name)]))


    def custom_action_to_invoice(self):
        """
        ฟังก์ชั่นสําหรับสร้าง action ไปที่เอกสาร invoice
        """
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")    
        action['domain'] = [
            ('move_type', '=', 'out_invoice'),
            ('ref', 'ilike', self.name)
            ]
        return action 


    def custom_create_invoice_group(self):
        """
        ฟังก์ชั่นสําหรับสร้าง invoice จากหลายเอกสารของ retention
        condition การ group
        แต่ละ retention ต้องมี partner_id เดียวกัน
        """
        if len(self) > 1: # เช็คว่าตอนนี้มี record มากกว่า 1 หรือไม่
            record_name = ", ".join(self.mapped("name"))

            if len(set(self.mapped("partner_id"))) == 1 : # เช็คว่า partner_id ของเอกสารนั้นเหมือนกันหรือไม่
                
                invoice_vals = {
                    'move_type': 'out_invoice',
                    'state': 'draft',
                    'partner_id': self.partner_id.id,
                    'ref': record_name,
                    'invoice_line_ids': [],
                }

                account = self.env.company.debit_default_id
                price_unit = sum(line.price_unit for line in self.invoice_line_ids)

                invoice_vals['invoice_line_ids'].append((0, 0, {
                    'name': 'Retention',
                    'quantity': 1,
                    'price_unit': price_unit or 0.0,
                    'account_id': account.id
                }))

                invoice = self.env['account.move'].create(invoice_vals)
                self.custom_count_invoice()
                self.custom_state_invoice()
                
                return invoice
                
            else:
                raise ValidationError(_("There is a mismatched customer name.")) # แจ้งเตือน "มีชื่อลูกค้าที่ไม่ตรงกัน"

        else:
            raise ValidationError(_("Please select more than one record")) # แจ้งเตือน "กรุณาเลือกเอกสารมากกว่า 1"


    def custom_button_create_invoice(self):
        """
        ฟังก์ชั่นสําหรับสร้าง invoice จากเอกสาร retention
        """
        AccountMove = self.env['account.move']
        account = self.env.company.debit_default_id
        for rec in self:
            if rec.move_type == 'out_retention':
                invoice_vals = {
                    'move_type': 'out_invoice',
                    'partner_id': rec.partner_id.id,
                    'ref': rec.name,
                    'invoice_line_ids': [],
                }
                for line in rec.invoice_line_ids:
                    invoice_vals['invoice_line_ids'].append((0, 0, {
                        'name': line.name,
                        'quantity': line.quantity or 1,
                        'price_unit': line.price_unit or 0.0,
                        'account_id': account.id
                    }))
                invoice = AccountMove.create(invoice_vals)

        self.custom_count_invoice()
        self.custom_state_invoice()
        return invoice


    @api.depends('move_type', 'count_retention')
    def _show_button_retention(self):
        """
        ฟังก์ชั่นสําหรับ กำหนดค่า field show_button_retention
        เพื่อกำหนดการแสดงปุ่ม retention
        True = แสดง  /  False = ไม่แสดง
        """
        for rec in self:
            if rec.move_type == "out_invoice" and rec.count_retention > 0:
                rec.show_button_retention = True
            else:
                rec.show_button_retention = False


    def _compute_count_retention(self): 
        """
        ฟังก์ชั่นสําหรับ กำหนดค่า field count_retention
        เพื่อนับจํานวนเอกสาร retention
        """
        retentions = self.env['account.move'].search([
            ('move_type', '=', 'out_retention'), 
            ('ref', 'ilike', self.name), 
            ])
        self.count_retention = len(retentions)


    def action_to_retention(self):
        """
        Action to go to the tree view of retention. 
        This function is used to generate action to go to the tree view of retention.
        The domain of action is set to filter retention that has move_type = 'out_retention' and ref like name of this record.
        """
        action = self.env["ir.actions.actions"]._for_xml_id("nawakij_account_move.action_move_out_retention_type")    
        action['domain'] = [
            ('move_type', '=', 'out_retention'),
            ('ref', 'ilike', self.name)
            ]
        return action 

        
    # แก้ไขจาก function เดิม
    @api.onchange('invoice_line_ids')
    def _onchange_invoice_line_ids(self):
        current_invoice_lines = self.line_ids.filtered(lambda line: not line.exclude_from_invoice_tab) # ใช้สําหรับเก็บ line_ids ที่อยู่ใน invoice_line_ids
        others_lines = self.line_ids - current_invoice_lines # ใช้สําหรับเก็บ line_ids ที่ไม่อยู่ใน invoice_line_ids

        default_account_credit = self.env.company.credit_default_id # ใช้สําหรับเก็บ credit_default_id ของ company
        if self.move_type == 'out_retention': # ถ้า move_type = out_retention
            for line in others_lines:
                line.account_id = default_account_credit # กําหนด account_id เป็น credit_default_id

        if others_lines and current_invoice_lines - self.invoice_line_ids:
            others_lines[0].recompute_tax_line = True
        self.line_ids = others_lines + self.invoice_line_ids
        self._onchange_recompute_dynamic_lines()


    # แก้ไขจาก function เดิม
    def _creation_message(self):
        # OVERRIDE
        if not self.is_invoice(include_receipts=True):
            return super()._creation_message()
        return {
            'out_invoice': _('Invoice Created'),
            'out_refund': _('Credit Note Created'),
            'in_invoice': _('Vendor Bill Created'),
            'in_refund': _('Refund Created'),
            'out_receipt': _('Sales Receipt Created'),
            'in_receipt': _('Purchase Receipt Created'),
            'out_retention':_('Retention Created') # เพิ่มเติม
        }[self.move_type]


    # แก้ไขจาก function เดิม
    @api.model
    def get_invoice_types(self, include_receipts=False):
        # เพิ่ม out_retention ใน list
        return ['out_invoice', 'out_refund', 'in_refund', 'in_invoice', 'out_retention'] + (include_receipts and ['out_receipt', 'in_receipt'] or [])


    # แก้ไขจาก function เดิม
    @api.model
    def get_outbound_types(self, include_receipts=True):
        # เพิ่ม out_retention ใน list
        return ['in_invoice', 'out_refund', 'out_retention'] + (include_receipts and ['in_receipt'] or [])


    # แก้ไขจาก function เดิม
    def _reverse_moves(self, default_values_list=None, cancel=False):
        ''' Reverse a recordset of account.move.
        If cancel parameter is true, the reconcilable or liquidity lines
        of each original move will be reconciled with its reverse's.

        :param default_values_list: A list of default values to consider per move.
                                    ('type' & 'reversed_entry_id' are computed in the method).
        :return:                    An account.move recordset, reverse of the current self.
        '''
        if not default_values_list:
            default_values_list = [{} for move in self]

        if cancel:
            lines = self.mapped('line_ids')
            # Avoid maximum recursion depth.
            if lines:
                lines.remove_move_reconcile()

        reverse_type_map = {
            'entry': 'entry',
            'out_invoice': 'out_refund',
            'out_refund': 'entry',
            'in_invoice': 'in_refund',
            'in_refund': 'entry',
            'out_receipt': 'entry',
            'in_receipt': 'entry',
            'out_retention': 'entry', # เพิ่มเติม
        }

        move_vals_list = []
        for move, default_values in zip(self, default_values_list):
            default_values.update({
                'move_type': reverse_type_map[move.move_type],
                'reversed_entry_id': move.id,
            })
            move_vals_list.append(move.with_context(move_reverse_cancel=cancel)._reverse_move_vals(default_values, cancel=cancel))

        reverse_moves = self.env['account.move'].create(move_vals_list)
        for move, reverse_move in zip(self, reverse_moves.with_context(check_move_validity=False, move_reverse_cancel=cancel)):
            # Update amount_currency if the date has changed.
            if move.date != reverse_move.date:
                for line in reverse_move.line_ids:
                    if line.currency_id:
                        line._onchange_currency()
            reverse_move._recompute_dynamic_lines(recompute_all_taxes=False)
        reverse_moves._check_balanced()

        # Reconcile moves together to cancel the previous one.
        if cancel:
            reverse_moves.with_context(move_reverse_cancel=cancel)._post(soft=False)
            for move, reverse_move in zip(self, reverse_moves):
                group = defaultdict(list)
                for line in (move.line_ids + reverse_move.line_ids).filtered(lambda l: not l.reconciled):
                    group[(line.account_id, line.currency_id)].append(line.id)
                for (account, dummy), line_ids in group.items():
                    if account.reconcile or account.internal_type == 'liquidity':
                        self.env['account.move.line'].browse(line_ids).with_context(move_reverse_cancel=cancel).reconcile()

        return reverse_moves


    # แก้ไขจาก function เดิม
    def _get_move_display_name(self, show_ref=False):
        ''' Helper to get the display name of an invoice depending of its type.
        :param show_ref:    A flag indicating of the display name must include or not the journal entry reference.
        :return:            A string representing the invoice.
        '''
        self.ensure_one()
        draft_name = ''
        if self.state == 'draft':
            draft_name += {
                'out_invoice': _('Draft Invoice'),
                'out_refund': _('Draft Credit Note'),
                'out_retention': _('Draft Retention'), # เพิ่มเติมส่วนของ out_retention
                'in_invoice': _('Draft Bill'),
                'in_refund': _('Draft Vendor Credit Note'),
                'out_receipt': _('Draft Sales Receipt'),
                'in_receipt': _('Draft Purchase Receipt'),
                'entry': _('Draft Entry'),
            }[self.move_type]
            if not self.name or self.name == '/':
                draft_name += ' (* %s)' % str(self.id)
            else:
                draft_name += ' ' + self.name
        return (draft_name or self.name) + (show_ref and self.ref and ' (%s%s)' % (self.ref[:50], '...' if len(self.ref) > 50 else '') or '')


    def action_add_retention(self):
        """
        ฟังชั่นสำหรับ action ไปยัง wizard view retention
        """
        if not self.retention:
            raise UserError(_("Retention is not set."))
        action = self.env["ir.actions.actions"]._for_xml_id("nawakij_account_move.action_view_account_move_retention")

        if self.is_invoice(): 
            action['name'] = _('Retention')
            action['context'] = {
                'default_move_id': self.id,  # ส่ง ID ของ account.move
                'default_company_id': self.company_id.id,  # ส่ง ID ของบริษัท 
            }

        return action


    @api.onchange('analytic_account_id')
    def _onchange_analytic_account_id(self):
        """
        ฟังก์ชั่นสําหรับเปลี่ยน analytic account ให้กับ invoice line
        """
        for rec in self:
            for line in rec.invoice_line_ids:
                if rec.analytic_account_id:
                    line.analytic_account_id = rec.analytic_account_id


    @api.depends('amount_total', 'retention', 'wht')
    def _compute_net_total(self):
        """
        ฟังก์ชั่นสําหรับคํานวณ net total
        ถ้าค่าของ amount_total , retention , wht มีการเปลี่ยนแปลง
        ทำการคำนวณ net_total = amount_total - retention - wht
        """
        for rec in self:
            rec.net_total = rec.amount_total - rec.retention - rec.wht


    @api.depends('line_ids.wt_tax_id', 'line_ids.price_subtotal')
    def _compute_wht(self):
        """
        คำนวณค่า WHT จาก move.line และรวมผลลัพธ์ใน move
        """
        for move in self:
            total_wht = 0
            for line in move.line_ids:
                if line.wt_tax_id:
                    total_wht += line.price_subtotal * (line.wt_tax_id.amount / 100)
            move.wht = total_wht


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'


    @api.model
    def default_get(self, default_fields):
        # OVERRIDE
        """
        Override the default_get method to set default values for account.move.line
        based on the context 'default_move_type'. If the move type is 'out_retention',
        the account_id is set to the company's debit default account.
        
        :param default_fields: List of fields for which default values are to be fetched.
        :return: Dictionary of field names and their corresponding default values.
        """

        values = super(AccountMoveLine, self).default_get(default_fields)
        move_type = self.env.context.get('default_move_type')  # ค่านี้ควรเป็น string เช่น 'out_retention'
        if move_type == 'out_retention':
            values.update({
                'account_id': self.env.company.debit_default_id.id,
            })
        return values
    

    def _auto_update_tax_invoice_custom(self):
        """
        function สำหรับ auto update value tax_base_amount และ balance ใน tax invoice
        """
        for line in self:
            if line.tax_invoice_ids:
                line.tax_invoice_ids.write({
                    'tax_base_amount': abs(line.tax_base_amount),
                    'balance': abs(line.balance),
                    })


    def write(self, vals):
        rec = super(AccountMoveLine, self).write(vals)

        if "tax_base_amount" in vals: # condition ที่เพิ่ม เพื่อไม่ให้เกิดการ update ซ้ํามากเกินไป
            self._auto_update_tax_invoice_custom() # ส่วนนี้เป็นส่วนเสริม

        return rec
    
