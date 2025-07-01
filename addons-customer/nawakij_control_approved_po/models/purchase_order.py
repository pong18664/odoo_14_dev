import logging
import re

from odoo import api, fields, models, SUPERUSER_ID, _ 
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import timedelta
from odoo.fields import Date

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'


    date_approve_1 = fields.Datetime(string="Date Approve 1", copy=False, help="วันที่อนุมัติ 1")
    date_approve_2 = fields.Datetime(string="Date Approve 2", copy=False, help="วันที่อนุมัติ 2")
    date_approve_3 = fields.Datetime(string="Date Approve 2", copy=False, help="วันที่อนุมัติ 3")


    def send_message_to_user_check_by(self, message=None):
        """
        ฟังก์ชันสำหรับส่งข้อความไปยังผู้ใช้ที่ทำการตรวจสอบ PO
        โดยใช้ระบบ Activity
        """
        for po in self:
            message = "PO อนุมัติแล้ว กรุณานำส่งให้ Supplier"
            if po.check_by_id:
                po.activity_schedule(
                    'mail.mail_activity_data_todo',
                    user_id=po.check_by_id.id,
                    note= message,
                    date_deadline=Date.today()
                )


    def action_mark_done_and_clear_activity_lv1(self):
        """
        function สำหรับทำเครื่องหมายกิจกรรมที่เกี่ยวข้องกับการตรวจสอบ PO ว่าเสร็จสิ้น
        และลบกิจกรรมที่ไม่เกี่ยวข้องกับการตรวจสอบ PO
        """
        for po in self:

            activity_done = po.activity_ids.filtered(lambda a: a.user_id == po.check_by_id)
            activity_cancel = po.activity_ids.filtered(lambda a: a.user_id != po.check_by_id)

            # action done 
            if activity_done:
                activity_done.action_done()

            # action cancel
            if activity_cancel:
                activity_cancel.unlink()
            

    def action_mark_done_and_clear_activity_lv2(self):
        """
        function สำหรับทำเครื่องหมายกิจกรรมที่เกี่ยวข้องกับการตรวจสอบ PO ว่าเสร็จสิ้น
        และลบกิจกรรมที่ไม่เกี่ยวข้องกับการตรวจสอบ PO
        """
        for po in self:

            activity_done = po.activity_ids.filtered(lambda a: a.user_id == po.approve_1_by_id)
            activity_cancel = po.activity_ids.filtered(lambda a: a.user_id != po.approve_1_by_id)

            # action done 
            if activity_done:
                activity_done.action_done()

            # action cancel
            if activity_cancel:
                activity_cancel.unlink()


    def action_mark_done_and_clear_activity_lv3(self):
        """
        function สำหรับทำเครื่องหมายกิจกรรมที่เกี่ยวข้องกับการตรวจสอบ PO ว่าเสร็จสิ้น
        และลบกิจกรรมที่ไม่เกี่ยวข้องกับการตรวจสอบ PO
        """
        for po in self:

            activity_done = po.activity_ids.filtered(lambda a: a.user_id == po.approve_2_by_id)
            activity_cancel = po.activity_ids.filtered(lambda a: a.user_id != po.approve_2_by_id)

            # action done 
            if activity_done:
                activity_done.action_done()

            # action cancel
            if activity_cancel:
                activity_cancel.unlink()


    def notify_users_approve_po_lv1(self, message=None):
        """
        สร้างกิจกรรมแจ้งเตือนให้ user ที่อยู่ใน Group 'Authorized sign-off personnel lv1'
        ให้มา Approve PO นี้ ผ่านระบบ Activity (TODO)
        """
        # ค้นหา Group
        group_1 = self.env['res.groups'].search([('name', '=', 'Authorized sign-off personnel lv1')], limit=1)

        if not group_1:
            raise UserError("Group 'Authorized sign-off personnel lv1' not found.")

        users_group_1 = group_1.users

        if not users_group_1:
            raise UserError("No users found in group 'Authorized sign-off personnel lv1'.")

        for po in self:
            for user in users_group_1:
                po.activity_schedule(
                    'mail.mail_activity_data_todo',
                    user_id=user.id,
                    note=f"กรุณาลงชื่อตรวจสอบ PO ที่ Check By",
                    # summary="PO Confirmation Required",
                    date_deadline=Date.today()
                )


    def notify_users_approve_po_lv2(self, message=None):
        """
        สร้างกิจกรรมแจ้งเตือนให้ user ที่อยู่ใน Group 'Authorized sign-off personnel lv2'
        ให้มา Approve PO นี้ ผ่านระบบ Activity (TODO)
        """
        # ค้นหา Group
        group_1 = self.env['res.groups'].search([('name', '=', 'Authorized sign-off personnel lv2')], limit=1)

        if not group_1:
            raise UserError("Group 'Authorized sign-off personnel lv2' not found.")

        users_group_1 = group_1.users

        if not users_group_1:
            raise UserError("No users found in group 'Authorized sign-off personnel lv2'.")

        for po in self:
            for user in users_group_1:
                po.activity_schedule(
                    'mail.mail_activity_data_todo',
                    user_id=user.id,
                    note=f"กรุณาลงชื่อตรวจสอบ PO ที่ Approve By 1",
                    # summary="PO Confirmation Required",
                    date_deadline=Date.today()
                )


    def notify_users_approve_po_lv3(self, message=None):
        """
        สร้างกิจกรรมแจ้งเตือนให้ user ที่อยู่ใน Group 'Authorized sign-off personnel lv3'
        ให้มา Approve PO นี้ ผ่านระบบ Activity (TODO)
        """
        # ค้นหา Group
        group_1 = self.env['res.groups'].search([('name', '=', 'Authorized sign-off personnel lv3')], limit=1)

        if not group_1:
            raise UserError("Group 'Authorized sign-off personnel lv3' not found.")

        users_group_1 = group_1.users

        if not users_group_1:
            raise UserError("No users found in group 'Authorized sign-off personnel lv3'.")

        for po in self:
            for user in users_group_1:
                po.activity_schedule(
                    'mail.mail_activity_data_todo',
                    user_id=user.id,
                    note=f"กรุณาลงชื่อตรวจสอบ PO ที่ Approve By 2",
                    # summary="PO Confirmation Required",
                    date_deadline=Date.today()
                )
               

    def button_check_1(self):
        """
        super ฟังก์ชัน button_check_1
        เพิ่มส่วนกำหนดให้ date_approve_1 เป็นวันที่ปัจจุบัน
        """
        self.ensure_one()
        rec =super(PurchaseOrder, self).button_check_1() # super function ส่วนของการลงชื่อตรวจสอบ
        self.date_approve_1 = fields.Datetime.now() # กำหนดให้ date_approve_1 เป็นวันที่ปัจจุบัน
        self.action_mark_done_and_clear_activity_lv1()  # เรียกใช้ฟังก์ชัน action_mark_done_and_clear_activity_lv1 เพื่อจัดการกิจกรรมที่เกี่ยวข้อง   
        self.notify_users_approve_po_lv2()  # เรียกใช้ฟังก์ชัน notify_users_approve_po_lv2 เพื่อแจ้งเตือนผู้ใช้ที่เกี่ยวข้อง
        return rec


    def button_approve_1(self):
        """
        super ฟังก์ชัน button_approve_1
        เพิ่มส่วนกำหนดให้ date_approve_2 เป็นวันที่ปัจจุบัน
        """
        self.ensure_one()
        rec = super(PurchaseOrder, self).button_approve_1() # super function ส่วนของการลงชื่อตรวจสอบ
        self.date_approve_2 = fields.Datetime.now() # กำหนดให้ date_approve_2 เป็นวันที่ปัจจุบัน
        self.action_mark_done_and_clear_activity_lv2()  # เรียกใช้ฟังก์ชัน action_mark_done_and_clear_activity_lv2 เพื่อจัดการกิจกรรมที่เกี่ยวข้อง   
        if self.check_config_po == True:
            self.notify_users_approve_po_lv3() # เรียกใช้ฟังก์ชัน notify_users_approve_po_lv3 เพื่อแจ้งเตือนผู้ใช้ที่เกี่ยวข้อง
        else:
            self.send_message_to_user_check_by()
        return rec


    def button_approve_2(self):
        """
        super ฟังก์ชัน button_approve_2
        เพิ่มส่วนกำหนดให้ date_approve_3 เป็นวันที่ปัจจุบัน
        """
        self.ensure_one()
        rec = super(PurchaseOrder, self).button_approve_2() # super function ส่วนของการลงชื่อตรวจสอบ
        self.date_approve_3 = fields.Datetime.now() # กำหนดให้ date_approve_3 เป็นวันที่ปัจจุบัน
        self.action_mark_done_and_clear_activity_lv3()  # เรียกใช้ฟังก์ชัน action_mark_done_and_clear_activity_lv3 เพื่อจัดการกิจกรรมที่เกี่ยวข้อง   
        self.send_message_to_user_check_by() # เรียกใช้ฟังก์ชัน send_message_to_user_check_by เพื่อส่งข้อความไปยังผู้ใช้ที่ทำการตรวจสอบ PO
        return rec
    

    def button_draft(self):
        """
        ฟังก์ชันสําหรับกดปุ่ม reset to draft
        เพิ่มส่วนล้างค่า date_approve_1, date_approve_2, date_approve_3
        """
        rec = super(PurchaseOrder, self).button_draft()
        self.date_approve_1 = False
        self.date_approve_2 = False
        self.date_approve_3 = False
        return rec
    

    def button_cancel(self, show_wizard=True):
        """
        ฟังก์ชันสําหรับกดปุ่ม Cancel
        ตรวจสอบว่า user ที่กดปุ่ม Cancel เป็น user ที่อยู่ในกลุ่ม 
        'Authorized sign-off personnel lv2' หรือ 'Authorized sign-off personnel lv3' ไหม
        """
        group_2 = self.env['res.groups'].search([('name', '=', 'Authorized sign-off personnel lv2')], limit=1)
        group_3 = self.env['res.groups'].search([('name', '=', 'Authorized sign-off personnel lv3')], limit=1)

        # ตรวจสอบว่าผู้ใช้ปัจจุบันมีสิทธิ์อยู่ในกลุ่มหรือไม่
        if self.env.user not in group_2.users and self.env.user not in group_3.users:
            raise UserError("คุณไม่มีสิทธิ์ในการยกเลิก Purchase Order นี้")
        # rec = super(PurchaseOrder, self).button_cancel()
        return super(PurchaseOrder, self).button_cancel(show_wizard=show_wizard)