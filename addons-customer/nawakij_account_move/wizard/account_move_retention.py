# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError


class AccountMoveRetention(models.TransientModel): 
 
    _name = 'account.move.retention'
    _description = 'Account Move Reversal Of Retention' 
    _check_company_auto = True

    move_id = fields.Many2one('account.move', string='Move', check_company=True, required=True)
    date_mode = fields.Selection(selection=[
            ('custom', 'Specific'),
            ('entry', 'Journal Entry Date')
    ], required=True, default='custom')
    date = fields.Date(string='Reversal date', default=fields.Date.context_today)
    reason = fields.Char(string='Reason')
    company_id = fields.Many2one('res.company', required=True, readonly=True)

    # computed fields
    move_type = fields.Selection(selection=[
            ('out_retention', 'Retention')
        ], string='Type', required=True, store=True, index=True, readonly=True, tracking=True,
        default="out_retention", change_default=True)
    journal_id = fields.Many2one(
        'account.journal', 
        string='Use Specific Journal', 
        help='If empty, uses the journal of the journal entry to be reversed.', 
        compute="_compute_journal_id", 
        store=True,
    )    


    @api.depends('move_id')
    def _compute_journal_id(self):
        for rec in self:
            rec.journal_id = self.env['account.journal'].search([('name', '=', 'Retention')], limit=1)


    def reverse_moves_of_retention(self):
        """
        Confirm button: Reverse moves and create new account.move records.
        """
        self.ensure_one()
        if not self.move_id:
            raise UserError(_('Please select a move to reverse.'))
        if not self.journal_id:
            raise UserError(_('Please specify a journal for the reversal.'))
        
        move = self.move_id
        reverse_date = self.date if self.date_mode == 'custom' else move.date
        default_account_debit = self.env.company.debit_default_id
        balance = move.retention

        # สร้าง invoice ใหม่
        invoice = self.env['account.move'].create({
            'partner_id': move.partner_id.id,
            'analytic_account_id': move.analytic_account_id.id,
            'ref': _('Reversal of: %(move_name)s, %(reason)s', move_name=move.name, reason=self.reason)
                if self.reason
                else _('Reversal of: %s', move.name),
            'date': reverse_date,
            'invoice_date': move.is_invoice(include_receipts=True) and (self.date or move.date) or False,
            'journal_id': self.journal_id.id if self.journal_id else move.journal_id.id,
            'invoice_payment_term_id': None,
            'invoice_user_id': move.invoice_user_id.id,
            'auto_post': reverse_date > fields.Date.context_today(self),
            'move_type': self.move_type,
        })

        # เพิ่ม invoice_lines
        invoice_lines = [{
            'name': "Retention",
            'account_id': default_account_debit.id,
            'quantity': 1,
            'price_unit': balance,
        }]
        
        # อัปเดต line_ids
        invoice.write({'invoice_line_ids': [(0, 0, line) for line in invoice_lines]})
        invoice._onchange_invoice_line_ids()
        move._compute_count_retention()
 
        # คืนค่าหน้าจอแสดง Invoice ที่สร้างขึ้น
        return {
            'type': 'ir.actions.act_window',
            'name': _('Reversed Move'),
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': invoice.id,
            'target': 'current',
        }


    
