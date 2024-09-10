# Copyright (c) 2024, Dexciss and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from ticketing.api import set_status,validate_resolution,deduction_on_visit_req
from erpnext.crm.utils import (
	CRMNote,
	copy_comments,
	link_communications,
	link_open_events,
	link_open_tasks,
)


class VisitRequest(CRMNote):
	def validate(self):
		print("self visiwst",self.__dict__)
		# print(self.__islocal)
		if not self.is_new():
			check_service_repair(self)
		if not self.visit_duration:
			self.visit_duration = 0
		validate_resolution(self)
		if self.reference_type == "Repair Request":
			print("repair req")
			prev_value=set_status(self,self.status,self.doctype,self.name,"Repair Request",self.repair_request)
			value=frappe.db.get_value("Repair Request Status Mapping with Ticket",{"source":prev_value},['destination'])
			print("value visit Request",value)
			if value:
				set_status(self,self.status,'Repair Request',self.name,"Ticket",self.ticket)
		else:
			prev_value=set_status(self,self.status,self.doctype,self.name,"Service Request",self.service_request)
			value=frappe.db.get_value("Service Request Status Mapping with Ticket Status",{"source":prev_value},['destination'])
			print("value visit Request",value)
			if value:
				set_status(self,self.status,'Service Request',self.name,"Ticket",self.ticket)

	@frappe.whitelist()
	def create_visit_invoice(self):
		print("create visit invoice")
		item={'name':"",'price':""}
		sales_inv=frappe.get_doc({"doctype":"Sales Invoice"})
		if self.reference_type == "Repair Request":
			item['name'] = frappe.db.get_value("Repair Request",self.repair_request,'equipment')
			item['price'] = frappe.db.get_value("Repair Request",self.repair_request,'price_per_visit')
			sales_inv.custom_visit_request=self.name   
			print("item in repair ",item)
		else:
			item['name'] = frappe.db.get_value("Service Request",self.service_request,'service')
			# select cc.name,cc.price_per_visit  from `tabVisit Request` as vr join `tabService Request` as sr on vr.service_request=sr.name join `tabTicket` as tk on sr.ticket=tk.name join `tabCustomer Contract` as cc on tk.contract=cc.name where vr.service_request='SR0053';
			data_customer= frappe.db.sql(f"select cc.name,cc.price_per_visit  from `tabVisit Request` as vr join `tabService Request` as sr on vr.service_request=sr.name join `tabTicket` as tk on sr.ticket=tk.name join `tabCustomer Contract` as cc on tk.contract=cc.name where vr.service_request='{self.service_request}';",as_dict=True)
			item['price']= data_customer['price_per_request']
			print("item in service",item)
			
		if not item: 
			frappe.throw("No equipment or service found for the given reference.")

		sales_inv.customer=self.customer
		sales_inv.company=self.company
		sales_inv.due_date=frappe.utils.nowdate()
		sales_inv.append("items", {
			"item_code": item['name'],
			"qty": 1,
			"rate": item['price'],
		})
		sales_inv.insert()
		return sales_inv.name

		# deduction_on_visit_req(self)
def check_service_repair(self):
	if self.reference_type == "Service Request":
		tk= frappe.db.get_value("Service Request",{"name":self.service_request},'ticket')
		if not tk or self.ticket != tk:
			frappe.throw(f"The Service Request '{self.service_request}' is not associated with ticket '{self.ticket}'")
		pass
	else:
		tk= frappe.db.get_value("Repair Request",{"name":self.repair_request},'ticket')
		if not tk or self.ticket != tk:
			frappe.throw(f"The Service Request '{self.repair_request}' is not associated with ticket '{self.ticket}'")