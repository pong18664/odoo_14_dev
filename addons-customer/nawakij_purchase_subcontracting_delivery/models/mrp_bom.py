from odoo import api, fields, models


class MrpBom(models.Model):
    _inherit = 'mrp.bom'


    def name_get(self):
        """
        function สำหรับแสดงชื่อ BoM ในรูปแบบ code แทน name
        """
        result = []
        for bom in self:
            name = bom.code
            if name:
                result.append((bom.id, name))
            else:
                super_name = super(MrpBom, bom).name_get()
                result.extend(super_name)
        return result