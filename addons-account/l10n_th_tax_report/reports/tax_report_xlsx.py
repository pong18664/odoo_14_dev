# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

import logging

from odoo import fields, models

from odoo.addons.report_xlsx_helper.report.report_xlsx_format import (
    FORMATS,
    XLS_HEADERS,
)

_logger = logging.getLogger(__name__)


class ReportTaxReportXlsx(models.TransientModel):
    _name = "report.l10n_th_tax_report.report_tax_report_xlsx"
    _inherit = "report.report_xlsx.abstract"
    _description = "Tax Report Excel"

    def _get_ws_params(self, wb, data, objects):
        tax_template = {
            "1_index": {
                "header": {"value": "#"},
                "data": {"value": self._render("row_pos")},
                "width": 3,
            },
            "2_tax_date": {
                "header": {"value": "Date"},
                "data": {"value": self._render("tax_date")},
                "width": 12,
            },
            "3_tax_invoice": {
                "header": {"value": "Number"},
                "data": {"value": self._render("tax_invoice_number")},
                "width": 18,
            },
            "4_partner_name": {
                "header": {"value": "Cust./Sup."},
                "data": {"value": self._render("partner_name")},
                "width": 30,
            },
            "5_partner_vat": {
                "header": {"value": "Tax ID"},
                "data": {"value": self._render("partner_vat")},
                "width": 15,
            },
            "6_partner_branch": {
                "header": {"value": "Branch ID"},
                "data": {"value": self._render("partner_branch")},
                "width": 12,
            },
            "7_tax_base_amount": {
                "header": {"value": "Base Amount"},
                "data": {
                    "value": self._render("tax_base_amount"),
                    "format": FORMATS["format_tcell_amount_right"],
                },
                "width": 21,
            },
            "8_tax_amount": {
                "header": {"value": "Tax Amount"},
                "data": {
                    "value": self._render("tax_amount"),
                    "format": FORMATS["format_tcell_amount_right"],
                },
                "width": 21,
            },
            "9_total_amount": {
                "header": {"value": "Total Amount"},
                "data": {
                    "value": self._render("total_amount"),
                    "format": FORMATS["format_tcell_amount_right"],
                },
                "width": 21,
            },
            "10_doc_ref": {
            # "9_doc_ref": {
                "header": {"value": "Doc Ref."},
                "data": {"value": self._render("doc_ref")},
                "width": 18,
            },
        }
        ws_params = {
            "ws_name": "TAX Report",
            "generate_ws_method": "_vat_report",
            "title": "TAX Report",
            "wanted_list": [k for k in sorted(tax_template.keys())],
            "col_specs": tax_template,
        }
        if objects.tax_id.type_tax_use == "sale":
            ws_params["ws_name"] = "Sale TAX Report"
            ws_params["title"] = "Sale TAX Report"
        elif objects.tax_id.type_tax_use == "purchase":
            ws_params["ws_name"] = "Purchase TAX Report"
            ws_params["title"] = "Purchase TAX Report"

        return [ws_params]

    def _vat_report(self, wb, ws, ws_params, data, objects):
        ws.set_portrait()
        ws.fit_to_pages(1, 0)
        ws.set_header(XLS_HEADERS["xls_headers"]["standard"])
        ws.set_footer(XLS_HEADERS["xls_footers"]["standard"])
        self._set_column_width(ws, ws_params)
        row_pos = 0
        # title
        row_pos = self._write_ws_title(ws, row_pos, ws_params, True)
        # company data
        # ws.write_column(
        #     row_pos, 1, ["Period :", "Partner :"], FORMATS["format_left_bold"]
        # )
        # ws.write_column(
        #     row_pos,
        #     2,
        #     [
        #         (objects.date_range_id.display_name) or "",
        #         (objects.company_id.display_name) or "",
        #     ],
        # )
        # ws.write_column(
        #     row_pos, 5, ["Tax ID :", "Branch ID :", "End Date :"], FORMATS["format_left_bold"]
        # )
        # ws.write_column(
        #     row_pos,
        #     6,
        #     [
        #         (objects.company_id.partner_id.vat) or "",
        #         (objects.company_id.partner_id.branch) or "",
        #     ],
        # )
        # row_pos += 3
        report = objects[:1]
        left_labels = ["Period :", "Partner :", "Start Date :"]
        left_values = [
            (report.date_range_id.display_name) if report else "",
            (report.company_id.display_name) if report else "",
            fields.Date.to_string(report.date_from) if report and report.date_from else "",
        ]
        right_labels = ["Tax ID :", "Branch ID :", "End Date :"]
        right_values = [
            (report.company_id.partner_id.vat) if report else "",
            (report.company_id.partner_id.branch) if report else "",
            fields.Date.to_string(report.date_to) if report and report.date_to else "",
        ]
        ws.write_column(row_pos, 1, left_labels, FORMATS["format_left_bold"])
        ws.write_column(row_pos, 2, left_values)
        ws.write_column(row_pos, 5, right_labels, FORMATS["format_left_bold"])
        ws.write_column(row_pos, 6, right_values)
        row_pos += max(len(left_labels), len(right_labels)) + 1
        # vat report table
        row_pos = self._write_line(
            ws,
            row_pos,
            ws_params,
            col_specs_section="header",
            default_format=FORMATS["format_theader_blue_left"],
        )
        ws.freeze_panes(row_pos, 0)
        grand_base = 0.00
        grand_tax = 0.00
        grand_total = 0.00
        for obj in objects:
            # total_base = 0.00
            # total_tax = 0.00
            for line in obj.results:
                # total_base += line.tax_base_amount
                # total_tax += line.tax_amount
                base_amount = line.tax_base_amount or 0.00
                tax_amount = line.tax_amount or 0.00
                line_total = base_amount + tax_amount
                grand_base += base_amount
                grand_tax += tax_amount
                grand_total += line_total
                row_pos = self._write_line(
                    ws,
                    row_pos,
                    ws_params,
                    col_specs_section="data",
                    render_space={
                        "row_pos": row_pos - 5,
                        "tax_date": line.tax_date or "",
                        "tax_invoice_number": line.tax_invoice_number or "",
                        "partner_name": line.partner_id.display_name or "",
                        "partner_vat": line.partner_id.vat or "",
                        # "partner_branch": line.partner_id.branch or "",
                        # "tax_base_amount": line.tax_base_amount or 0.00,
                        # "tax_amount": line.tax_amount or 0.00,
                        "partner_branch": self._prepare_partner_branch(line.partner_id),
                        "tax_base_amount": base_amount,
                        "tax_amount": tax_amount,
                        "total_amount": line_total,
                        "doc_ref": line.name or "",
                    },
                    default_format=FORMATS["format_tcell_left"],
                )
        ws.write_row(
            row_pos,
            6,
            # [total_base, total_tax],
            [grand_base, grand_tax, grand_total],
            FORMATS["format_theader_blue_amount_right"],
        )

    def _prepare_partner_branch(self, partner):
        if not partner:
            return ""
        display_name = partner.display_name or ""
        branch_keyword = "สาขาที่"
        if display_name and branch_keyword in display_name:
            parts = display_name.split(branch_keyword, 1)
            branch_value = parts[1].strip() if len(parts) > 1 else ""
            return branch_value or partner.branch or ""
        if display_name:
            return "สำนักงานใหญ่"
        return partner.branch or ""
