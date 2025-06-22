from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    
    work_center_cost_account = fields.Many2one('account.account', string='Work Center Cost Account',store=True)
    work_center_cost_account_subcontract = fields.Many2one('account.account', string='Work Center Cost Account Subcontract',store=True)
    work_center_subcontract = fields.Many2one('account.account', string='Subcontract ช่างเหมา Work Center Cost Account')


    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            work_center_cost_account=self.env.company.work_center_cost_account.id,
            work_center_cost_account_subcontract=self.env.company.work_center_cost_account_subcontract.id,
            work_center_subcontract=self.env.company.work_center_subcontract.id,
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env.company.work_center_cost_account = self.work_center_cost_account
        self.env.company.work_center_cost_account_subcontract = self.work_center_cost_account_subcontract
        self.env.company.work_center_subcontract = self.work_center_subcontract