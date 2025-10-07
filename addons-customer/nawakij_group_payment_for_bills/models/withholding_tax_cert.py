import logging
_logger = logging.getLogger(__name__)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare

INCOME_TAX_FORM = [
    ("pnd1", "PND1"),
    ("pnd3", "PND3"),
    ("pnd3a", "PND3a"),
    ("pnd53", "PND53"),
]


WHT_CERT_INCOME_TYPE = [
    ("1", "1. เงินเดือน ค่าจ้าง ฯลฯ 40(1)"),
    ("2", "2. ค่าธรรมเนียม ค่านายหน้า ฯลฯ 40(2)"),
    ("3", "3. ค่าแห่งลิขสิทธิ์ ฯลฯ 40(3)"),
    ("4A", "4. ดอกเบี้ย ฯลฯ 40(4)ก"),
    (
        "4B11",
        "4. เงินปันผล เงินส่วนแบ่งกำไร ฯลฯ 40(4)ข (1.1) "
        "กิจการที่ต้องเสียภาษีเงินได้นิติบุคคลร้อยละ 30 ของกำไรสุทธิ",
    ),
    (
        "4B12",
        "4. เงินปันผล เงินส่วนแบ่งกำไร ฯลฯ 40(4)ข (1.2) "
        "กิจการที่ต้องเสียภาษีเงินได้นิติบุคคลร้อยละ 25 ของกำไรสุทธิ",
    ),
    (
        "4B13",
        "4. เงินปันผล เงินส่วนแบ่งกำไร ฯลฯ 40(4)ข (1.3) "
        "กิจการที่ต้องเสียภาษีเงินได้นิติบุคคลร้อยละ 20 ของกำไรสุทธิ",
    ),
    (
        "4B14",
        "4. เงินปันผล เงินส่วนแบ่งกำไร ฯลฯ 40(4)ข (1.4) "
        "กิจการที่ต้องเสียภาษีเงินได้นิติบุคคลร้อยละ อื่นๆ (ระบุ) ของกำไรสุทธิ",
    ),
    (
        "4B21",
        "4. เงินปันผล เงินส่วนแบ่งกำไร ฯลฯ 40(4)ข (2.1) "
        "กำไรสุทธิกิจการที่ได้รับยกเว้นภาษีเงินได้นิติบุคคล",
    ),
    (
        "4B22",
        "4. เงินปันผล เงินส่วนแบ่งกำไร ฯลฯ 40(4)ข (2.2) "
        "ได้รับยกเว้นไม่ต้องนำมารวมคำนวณเป็นรายได้",
    ),
    (
        "4B23",
        "4. เงินปันผล เงินส่วนแบ่งกำไร ฯลฯ 40(4)ข (2.3) "
        "กำไรสุทธิส่วนที่หักผลขาดทุนสุทธิยกมาไม่เกิน 5 ปี",
    ),
    (
        "4B24",
        "4. เงินปันผล เงินส่วนแบ่งกำไร ฯลฯ 40(4)ข (2.4) "
        "กำไรที่รับรู้ทางบัญชีโดยวิธีส่วนได้เสีย",
    ),
    ("4B25", "4. เงินปันผล เงินส่วนแบ่งกำไร ฯลฯ 40(4)ข (2.5) อื่นๆ (ระบุ)"),
    ("5", "5. ค่าจ้างทำของ ค่าบริการ ค่าเช่า ค่าขนส่ง ฯลฯ 3 เตรส"),
    ("6", "6. อื่นๆ (ระบุ)"),
]


TAX_PAYER = [("withholding", "Withholding"), ("paid_one_time", "Paid One Time")]


class WithholdingTaxCert(models.Model):
    _inherit = "withholding.tax.cert"


    @api.model
    def _prepare_wt_line(self, move_line):
        """ Hook point to prepare wt_line """
        wt_percent = move_line.wt_tax_id.amount
        wt_cert_income_type = self._context.get("wt_cert_income_type")
        select_dict = dict(WHT_CERT_INCOME_TYPE)
        wt_cert_income_desc = select_dict.get(wt_cert_income_type, False)
        vals = {
            "wt_cert_income_type": wt_cert_income_type,
            "wt_cert_income_desc": wt_cert_income_desc,
            "wt_percent": wt_percent,
            "base": (abs(move_line.balance) / wt_percent * 100)
            if wt_percent
            else False,
            "amount": abs(move_line.balance),
            "ref_move_line_id": move_line.id,
        }
        _logger.info()
        return vals

    
