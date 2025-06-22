from odoo import api, fields, models, _

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    journal_default_id = fields.Many2one(
        'account.journal',
        string='Default Journal',
        help="กำหนด Account Journal เริ่มต้มให้กับเอกสาร Retention"
    )
    debit_default_id = fields.Many2one(
        'account.account',
        string='Default Debit Account',
        help="กำหนด Account Debit เริ่มต้มให้กับเอกสาร Retention"
    )
    credit_default_id = fields.Many2one(
        'account.account',
        string='Default Credit Account',
        help="กำหนด Account Credit เริ่มต้มให้กับเอกสาร Retention"
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            journal_default_id=self.env.company.journal_default_id.id,
            debit_default_id=self.env.company.debit_default_id.id,
            credit_default_id=self.env.company.credit_default_id.id
        )
        return res

    def set_values(self):
        # การตั้งค่าใน ResConfigSettings จะอัปเดตค่าบริษัทโดยตรง
        super(ResConfigSettings, self).set_values()
        self.env.company.journal_default_id = self.journal_default_id
        self.env.company.debit_default_id = self.debit_default_id
        self.env.company.credit_default_id = self.credit_default_id
