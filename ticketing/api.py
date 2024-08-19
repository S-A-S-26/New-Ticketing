import frappe
from datetime import timedelta 
from frappe.model.document import Document
from frappe.utils import (
	add_to_date,
	get_datetime,
	get_weekdays,
	getdate,
	now_datetime,
	time_diff_in_seconds,
	to_timedelta,
)
# from frappe.contacts.doctype.address import get_address_display

@frappe.whitelist()
def get_sla(self,sla):
    set_response_by(self,sla)
    set_resolution_by(self,sla)

def get_holidays(self):
    res = []
    if not self.holiday_list:
        return res
    holiday_list = frappe.get_doc("HD Service Holiday List", self.holiday_list)
    for row in holiday_list.holidays:
        res.append(row.holiday_date)
    return res

def get_priorities(self):
    """
    Return priorities related info as a dict. With `priority` as key
    """
    res = {}
    for row in self.priorities:
        res[row.priority] = row
    return res

def get_workdays(self) -> dict[str, dict]:
    """
    Return workdays related info as a dict. With `workday` as key
    """
    res = {}
    for row in self.support_and_resolution:
        res[row.workday] = row
    return res

def set_response_by(self, doc: Document):
    start = doc.service_level_agreement_creation#need to open the field
    doc.response_by = self.calc_time(start, doc.priority, "response_time")

def set_resolution_by(self, doc: Document):
    total_hold_time = doc.total_hold_time or 0
    start = add_to_date(
        doc.service_level_agreement_creation,
        seconds=total_hold_time,
        as_datetime=True,
    )
    doc.resolution_by = self.calc_time(start, doc.priority, "resolution_time")

def calc_time(
    self,
    start_at: str,
    priority: str,
    target,
):#this needs to be passed on with a sla account self
    res = get_datetime(start_at)
    priority = self.get_priorities()[priority]
    time_needed = priority.get(target, 0)
    holidays = self.get_holidays()
    weekdays = get_weekdays()
    workdays = self.get_workdays()
    while time_needed:
        today = res
        today_day = getdate(today)
        today_weekday = weekdays[today.weekday()]
        is_workday = today_weekday in workdays
        is_holiday = today_day in holidays
        if is_holiday or not is_workday:
            res = add_to_date(res, days=1, as_datetime=True)
            continue
        today_workday = workdays[today_weekday]
        now_in_seconds = time_diff_in_seconds(today, today_day)
        start_time = max(today_workday.start_time.total_seconds(), now_in_seconds)
        till_start_time = max(start_time - now_in_seconds, 0)
        end_time = max(today_workday.end_time.total_seconds(), now_in_seconds)
        time_left = max(end_time - start_time, 0)
        if not time_left:
            res = getdate(add_to_date(res, days=1, as_datetime=True))
            continue
        time_taken = min(time_needed, time_left)
        time_needed -= time_taken
        time_required = till_start_time + time_taken
        res = add_to_date(res, seconds=time_required, as_datetime=True)
    return res

@frappe.whitelist()
def create_opportunity(self):
    print("opportunity creation",self.contract,self.contract_status)
    doc=frappe.get_doc({"doctype":"Opportunity"})
    doc.opportunity_from="Customer"
    doc.party_name=self.customer
    doc.status="Open"
    rate=[0]
    if self.contract:
        print("inside if for rate")
        print(f"""select ccs.price from `tabCustomer Contract` as cc join `tabContract Covered Services` as ccs on cc.name = ccs.parent where cc.name = '{self.contract}' and ccs.service = '{self.service_requested}';""")
        rate=frappe.db.sql(f"""select ccs.price from `tabCustomer Contract` as cc join `tabContract Covered Services` as ccs on cc.name = ccs.parent where cc.name = '{self.contract}' and ccs.service = '{self.service_requested}';""",pluck=True)
        doc.append("items",{
                "item_code":self.service_requested,
                "qty":1,
                "rate":rate[0],
                "amount":rate[0]
                })
    doc.custom_ticket=self.name
    doc.insert()
    return "Opportunity"

@frappe.whitelist()
def set_status(self,status,doctype,name,target_doc,target_doc_name):
    print("self",self.__dict__)
    if self.get('__islocal') == True:
        return
    mapping={
        ("Service Request","Ticket"):"Service Request Status Mapping with Ticket Status",
        ("Visit Request","Service Request"):"Visit Status Mapping to Service Request",
        ("Visit Request","Repair Request"):"Visit Request Status Mapping with Repair Request",
        ("Repair Request","Ticket"):"Repair Request Status Mapping with Ticket",
    }
    print("mapping",mapping[(doctype,target_doc)])
    value=frappe.db.get_value(mapping[(doctype,target_doc)],{"source":status},['destination'])
    if value:
        print("if value set status",target_doc,target_doc_name)
        doc=frappe.get_doc(target_doc,target_doc_name)
        doc.status=value
        doc.save()
        print("set value",(target_doc,target_doc_name,"status",value))
        return value
        # frappe.db.set_value(target_doc,target_doc_name,"status",value,update_modified=False)

from bs4 import BeautifulSoup
def validate_resolution(self):
    resolution_details = False
    if self.resolution_details:
        print("b4",BeautifulSoup(self.resolution_details, "html.parser").get_text(strip=True))
        if BeautifulSoup(self.resolution_details, "html.parser").get_text(strip=True):
            print("data exists b4")
            resolution_details=True
        else:
            print("data doesnt exists b4")
            resolution_details=False
    print("\n\nValidating",self.resolution_details,self.resolution_details == '<div class="ql-editor read-mode"><p><br></p></div>')
    if (self.status=="Resolved" or self.status=="Closed" or self.status=="Completed") and not (resolution_details):
            frappe.throw(f"Please fill out resolution details for {self.doctype} with statuses Resolved , Closed or Completed")

from datetime import datetime
def create_comment(self,method):
    if self.reference_type not in ["Ticket","Service Request","Visit Request","Repair Request"]:
        return
    comment_doc=frappe.new_doc("Comment")
    comment_doc.comment_type="Comment"
    comment_doc.content=f"{self.allocated_to} --> "+self.description
    comment_doc.reference_doctype=self.reference_type
    comment_doc.reference_name=self.reference_name
    comment_doc.comment_email=self.allocated_to
    comment_doc.insert()
    frappe.db.set_value(self.reference_type,self.reference_name,'modified',datetime.now())
    print("comment created",comment_doc.name)

def set_expiring():
    print("set_expiring")
    days_to_expire=frappe.db.get_single_value('Ticketing Settings', 'days_to_expire')
    if days_to_expire and days_to_expire <=0:
        return []
    expired_docs=[]
    items = frappe.db.get_all("Warranty Equipments",{"status":"Active"},pluck="name")
    for name in items:
        doc = frappe.get_doc("Warranty Equipments", name)
        if not doc.warranty_expiry_date:
            continue
        print("comp",doc.equipment,datetime.now() ,doc.warranty_expiry_date)
        days_remaining = (doc.warranty_expiry_date -datetime.now()).days
        if days_remaining <= days_to_expire and days_remaining > 0:
            print(f"days remaining {days_remaining} days_to_expire {days_to_expire}")
            # doc.warranty_status = "Expiring"
            # doc.save()
            if doc.parent not in expired_docs:
                expired_docs.append(doc.parent)
            frappe.db.set_value("Warranty Equipments",name,'status',"Expiring",update_modified=False)
    return expired_docs

def set_expired():
    print("set_expired")
    expired_docs=[]
    items = frappe.db.get_all("Warranty Equipments",{"status":['in',["Active","Expiring"]]},pluck="name")
    for name in items:
        doc = frappe.get_doc("Warranty Equipments", name)
        if not doc.warranty_expiry_date:
            continue
        print("comp",doc.equipment,datetime.now() ,doc.warranty_expiry_date)
        days_remaining = (doc.warranty_expiry_date -datetime.now()).days
        if datetime.now() > doc.warranty_expiry_date:
            print("expired",doc.equipment)
            # doc.warranty_status = "Expiring"
            # doc.save()
            if doc.parent not in expired_docs:
                expired_docs.append(doc.parent)
            frappe.db.set_value("Warranty Equipments",name,'status',"Expired",update_modified=False)
    return expired_docs

def set_warranty_status():
    docs=set_expiring()
    set_expired()
    print("docs",docs)
    for name in docs:
        frappe.db.set_value("Warranty",name,'warranty_status',"Expired",update_modified=False)
        # doc=frappe.get_doc("Warranty",name)
        # doc.set_warranty_status()
        # doc.save()

def create_sales_invoice_ticket(item_code,qty,rate,cust,doc_name):
    sales_inv=frappe.get_doc({"doctype":"Sales Invoice"})
    sales_inv.customer=cust
    sales_inv.due_date=frappe.utils.nowdate()
    sales_inv.append("items", {
        "item_code": item_code,
        "qty": qty,
        "rate":rate,
    })
    sales_inv.custom_ticket=doc_name   
    sales_inv.insert()
    return sales_inv.name
       
# def get_address_custom():
#     get_address_display()