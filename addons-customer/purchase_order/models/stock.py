from collections import defaultdict

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from collections import defaultdict
from datetime import datetime
from dateutil.relativedelta import relativedelta
from itertools import groupby


from odoo.addons.stock.models.stock_rule import ProcurementException

class StockRule(models.Model):
    _inherit = 'stock.rule'

    @api.model 
    def _run_buy(self, procurements):
        # จุดที่แก้ไข บรรทัดที่ 20 - 41
        # ทำให้ตอน confirm จาก manufacturing ไป purchase agreements สร้างเอกสารเป็น 1 ต่อ 1
        requisitions_values_by_company = defaultdict(list)
        other_procurements = []
        line_ids=[]
        for procurement, rule in procurements:
            if procurement.product_id.purchase_requisition == 'tenders':
                values = self.env['purchase.requisition']._prepare_tender_values(*procurement)
                line_ids.append(values['line_ids'][0])
                values['picking_type_id'] = rule.picking_type_id.id
                requisitions_values_by_company[procurement.company_id.id].append(values)
            else:
                other_procurements.append((procurement, rule))
        requisitions_values_by_company_one={}

        for company_id, requisitions_values in requisitions_values_by_company.items():
            # raise ValidationError(_(f"{requisitions_values}"))
            requisitions_values_by_company_one=requisitions_values
            break
        if requisitions_values_by_company_one:
            requisitions_values_by_company_one=requisitions_values_by_company_one[0]
            requisitions_values_by_company_one['line_ids']=line_ids
            # raise ValidationError(_(f"{requisitions_values_by_company_one}"))
            self.env['purchase.requisition'].sudo().with_company(company_id).create(requisitions_values_by_company_one)


        procurements_by_po_domain = defaultdict(list)
        errors = []
        for procurement, rule in procurements:

            # Get the schedule date in order to find a valid seller
            if procurement.product_id.purchase_requisition != 'tenders':
                procurement_date_planned = fields.Datetime.from_string(procurement.values['date_planned'])
                schedule_date = (procurement_date_planned - relativedelta(days=procurement.company_id.po_lead))

                supplier = False
                if procurement.values.get('supplierinfo_id'):
                    supplier = procurement.values['supplierinfo_id']
                else:
                    supplier = procurement.product_id.with_company(procurement.company_id.id)._select_seller(
                        partner_id=procurement.values.get("supplierinfo_name"),
                        quantity=procurement.product_qty,
                        date=schedule_date.date(),
                        uom_id=procurement.product_uom)

                # Fall back on a supplier for which no price may be defined. Not ideal, but better than
                # blocking the user.
                supplier = supplier or procurement.product_id._prepare_sellers(False).filtered(
                    lambda s: not s.company_id or s.company_id == procurement.company_id
                )[:1]

                if not supplier:
                    msg = _('There is no matching vendor price to generate the purchase order for product %s (no vendor defined, minimum quantity not reached, dates not valid, ...). Go on the product form and complete the list of vendors.') % (procurement.product_id.display_name)
                    errors.append((procurement, msg))

                partner = supplier.name
                # we put `supplier_info` in values for extensibility purposes
                procurement.values['supplier'] = supplier
                procurement.values['propagate_cancel'] = rule.propagate_cancel

                domain = rule._make_po_get_domain(procurement.company_id, procurement.values, partner)
                procurements_by_po_domain[domain].append((procurement, rule))
                
        if errors:
            raise ProcurementException(errors)

        for domain, procurements_rules in procurements_by_po_domain.items():
            # Get the procurements for the current domain.
            # Get the rules for the current domain. Their only use is to create
            # the PO if it does not exist.
            procurements, rules = zip(*procurements_rules)

            # Get the set of procurement origin for the current domain.
            origins = set([p.origin for p in procurements])
            # Check if a PO exists for the current domain.
            po = self.env['purchase.order'].sudo().search([dom for dom in domain], limit=1)
            company_id = procurements[0].company_id

            # การทำงานส่วนนี้เพื่อให้สร้าง 1 PO ต่อ 1 MO
            vals = rules[0]._prepare_purchase_order(company_id, origins, [p.values for p in procurements])
            po = self.env['purchase.order'].with_company(company_id).with_user(SUPERUSER_ID).create(vals)

            # เอา if else บรรทัดที่ 104-121 ออก ส่วนนี้เป็นส่วนที่เช็ค
            # ตอน confirm MO
            # ถ้าไม่มี PO ให้สร้าง PO ใหม่ 
            # ถ้ามี PO อยู่แล้วให้ update เพิ่มเข้าไปใน PO เดิม
            # if not po:
            #     # We need a rule to generate the PO. However the rule generated
            #     # the same domain for PO and the _prepare_purchase_order method
            #     # should only uses the common rules's fields.
            #     vals = rules[0]._prepare_purchase_order(company_id, origins, [p.values for p in procurements])
            #     # The company_id is the same for all procurements since
            #     # _make_po_get_domain add the company in the domain.
            #     # We use SUPERUSER_ID since we don't want the current user to be follower of the PO.
            #     # Indeed, the current user may be a user without access to Purchase, or even be a portal user.
            #     po = self.env['purchase.order'].with_company(company_id).with_user(SUPERUSER_ID).create(vals) 
            # else:
            #     # If a purchase order is found, adapt its `origin` field.
            #     if po.origin:
            #         missing_origins = origins - set(po.origin.split(', '))
            #         if missing_origins:
            #             po.write({'origin': po.origin + ', ' + ', '.join(missing_origins)})
            #     else:
            #         po.write({'origin': ', '.join(origins)})

            procurements_to_merge = self._get_procurements_to_merge(procurements)
            procurements = self._merge_procurements(procurements_to_merge)

            po_lines_by_product = {}
            grouped_po_lines = groupby(po.order_line.filtered(lambda l: not l.display_type and l.product_uom == l.product_id.uom_po_id).sorted(lambda l: l.product_id.id), key=lambda l: l.product_id.id)
            for product, po_lines in grouped_po_lines:
                po_lines_by_product[product] = self.env['purchase.order.line'].concat(*list(po_lines))
            po_line_values = []
            for procurement in procurements:
                po_lines = po_lines_by_product.get(procurement.product_id.id, self.env['purchase.order.line'])
                po_line = po_lines._find_candidate(*procurement)

                if po_line:
                    # If the procurement can be merge in an existing line. Directly
                    # write the new values on it.
                    vals = self._update_purchase_order_line(procurement.product_id,
                        procurement.product_qty, procurement.product_uom, company_id,
                        procurement.values, po_line)
                    po_line.write(vals)
                else:
                    # If it does not exist a PO line for current procurement.
                    # Generate the create values for it and add it to a list in
                    # order to create it in batch.
                    partner = procurement.values['supplier'].name
                    po_line_values.append(self.env['purchase.order.line']._prepare_purchase_order_line_from_procurement(
                        procurement.product_id, procurement.product_qty,
                        procurement.product_uom, procurement.company_id,
                        procurement.values, po))
            self.env['purchase.order.line'].sudo().create(po_line_values)

    
   