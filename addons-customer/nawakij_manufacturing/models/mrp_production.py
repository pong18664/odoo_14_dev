import logging
import re

from odoo import api, fields,tools, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
# raise ValidationError(_(f"{workorder.check_yes_or_no}"))

class MrpProduction(models.Model):
    _inherit = 'mrp.production'


    vendor_bill_count = fields.Integer(string='Vendor Bill Count', compute='_compute_vendor_bill_count')
    show_button_create_bill = fields.Boolean(string='Show Button Create Bill', compute='_compute_show_button_create_bill', store=True)
    state_qc = fields.Boolean(string='State QC',defualt=False, store=True )


    @api.depends('state','state_qc')
    def _compute_show_button_create_bill(self):
        for rec in self:
            qc = self.env['quality.check'].search([
                ('production_id', '=', rec.id),
                ('quality_state', '=', 'pass')
            ], limit=1) 
            if (rec.state == "progress" and qc) or (rec.state == "to_close" and qc) or (rec.state == "done"):
                rec.show_button_create_bill = True
            else:
                rec.show_button_create_bill = False


    @api.depends('name')
    def _compute_vendor_bill_count(self):
        for production in self:
            vendor_bills = self.env['account.move'].search([
                ('ref', 'ilike', production.name),
                ('move_type', '=', 'in_invoice')
            ])
            production.vendor_bill_count = len(vendor_bills)


    def action_view_vendor_bill(self):
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_in_invoice_type")
        action['domain'] = [('ref', 'ilike', self.name),('move_type', '=', 'in_invoice')]
        return action
    

    def new_create_vendor_bill(self):
        """
        เป็น function สร้าง vendor bill in account.move
        """
        account_subcontract = self.company_id.work_center_subcontract
        for mrp in self:
            for workorder in mrp.workorder_ids:
                workcenter_name = workorder.workcenter_id.name
                if workorder.workcenter_id.yes_or_no in 'yes':
                    vendor_bill_vals = {
                        'move_type': 'in_invoice',
                        'ref': f"{self.name} - {'SUB'} - {workcenter_name}",
                        'invoice_line_ids': [],
                        }
                    
                    line_vals = {
                        'name': f"{self.name} - {'SUB'} - {workcenter_name}",
                        'account_id': account_subcontract.id,
                        'quantity': self.product_qty,
                        'price_unit': workorder.subcontract_cost,
                    }
                    
                    vendor_bill_vals['invoice_line_ids'].append((0, 0, line_vals))
                    self.env['account.move'].create(vendor_bill_vals)
                    

    def new_create_journal(self):
        """
        เป็น function สำหรับสร้าง journal entries ใหม่
        โดยเช็คจาก แท็ป work orders ใน mrp.production
        work center ที่มี Subcontract Cost ค่าเป็น no 
        เราจะนำค่าแรงของ work center ที่ได้มานั้น
        นำไปสร้าง journal entries เพิ่ม
        อาจมี work center มากกว่า 1 จะต้องนำไปสร้าง journal entries แยกกัน
        """
        account_center_cost = self.company_id.work_center_cost_account
        account_subcontract = self.company_id.work_center_cost_account_subcontract
        account_wip = self.env['account.account'].search([('code','=','100530')])
        journal_name = self.env['account.journal'].search([('name','=','Inventory Valuation')])

        for mrp in self:
            for workorder in mrp.workorder_ids:
                duration = workorder.duration
                work_center_cost = (duration / 60.0) * workorder.workcenter_id.costs_hour
                workcenter_name = workorder.workcenter_id.name

                # สร้าง journal entry สำหรับ workcenter ที่ไม่ใช่รับเหมา
                if workorder.workcenter_id.yes_or_no in 'no':
                    # Create the journal entry
                    new_journal = self.env['account.move'].create({
                        'ref': f"{self.name} - {'WC'} - {workcenter_name}",
                        'journal_id': journal_name.id,
                    })
                    # Create the journal entry lines (debit and credit)
                    lines_to_create = [
                        {
                            'move_id': new_journal.id,
                            'account_id': account_center_cost.id,
                            'name': f"{self.name} - {'WC'} - {workcenter_name}",
                            'credit': work_center_cost,
                            'debit': 0,
                        },
                        {
                            'move_id': new_journal.id,
                            'account_id': account_wip.id,
                            'name': f"{self.name} - {'WC'} - {workcenter_name}",
                            'credit': 0,
                            'debit': work_center_cost,
                        },
                    ]
                    # Create all lines in one go with a loop
                    self.env['account.move.line'].create(lines_to_create)
                    # Call the action_post() function
                    new_journal.action_post()
                
                # สร้าง journal entry สำหรับ workcenter ที่เป็นรับเหมา    
                elif workorder.workcenter_id.yes_or_no in 'yes':
                    # Create the journal entry
                    new_journal = self.env['account.move'].create({
                        'ref': f"{self.name} - {'SUB'} - {workcenter_name}",
                        'journal_id': journal_name.id,
                    })
                    # Create the journal entry lines (debit and credit)
                    lines_to_create = [
                        {
                            'move_id': new_journal.id,
                            'account_id': account_subcontract.id,
                            'name': f"{self.name} - {'SUB'} - {workcenter_name}",
                            'credit': workorder.subcontract_cost,
                            'debit': 0,
                        },
                        {
                            'move_id': new_journal.id,
                            'account_id': account_wip.id,
                            'name': f"{self.name} - {'SUB'} - {workcenter_name}",
                            'credit': 0,
                            'debit': workorder.subcontract_cost,
                        },
                    ]
                    # Create all lines in one go with a loop
                    self.env['account.move.line'].create(lines_to_create)
                    # Call the action_post() function
                    new_journal.action_post()

    
    def button_mark_done(self):
        mrp = super(MrpProduction, self).button_mark_done()
        if self.state == 'done':
            self.new_create_journal()
        return mrp

