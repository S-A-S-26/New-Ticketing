# Copyright (c) 2024, Dexciss and contributors
# For license information, please see license.txt

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
from ticketing.api import get_sla,create_opportunity,validate_resolution
from erpnext.crm.utils import (
	CRMNote,
	copy_comments,
	link_communications,
	link_open_events,
	link_open_tasks,
)


class Ticket(CRMNote):
	def validate(self):
		print("\n\nValidating",self.resolution_details,self.resolution_details == '<div class="ql-editor read-mode"><p><br></p></div>')
		validate_resolution(self)
		
		# already_ticket = False
		# if self.contract:
		# 	print(f"""select tk.name from `tabTicket` as tk join `tabCustomer Contract` as cc on tk.contract=cc.name where tk.creation BETWEEN cc.from_date AND cc.to_date and cc.customer='{self.customer}' AND cc.name='{self.contract}';
		# 	""")
		# 	already_ticket=frappe.db.sql(f"""select tk.name from `tabTicket` as tk join `tabCustomer Contract` as cc on tk.contract=cc.name where tk.creation BETWEEN cc.from_date AND cc.to_date and cc.customer='{self.customer}' AND cc.name='{self.contract}';
		# 	""",pluck=True)
		# if already_ticket:
		# 	frappe.throw(f"A ticket already exists for the customer {self.customer} with contract {self.contract}")
		

	@frappe.whitelist()
	def create_opp(self):
		if check_if_exists("Opportunity",self.name):
			frappe.throw(f"An opportunity already exists for this ticket to create new one delete the existing one")
		else:
			return create_opportunity(self)

	@frappe.whitelist()
	def validate_before_ticketInv(self):
		print("validate_before_ticket",self.__dict__)
		charge=frappe.db.get_value("Customer Contract",self.contract,'charge_per_ticket')
		print("charge,self.contractstat,self.type",charge,self.contract_status,self.type)
		if charge and charge>0 and self.contract_status == "Active" and self.type == "Service Request" and self.ticket_invoice == 0:
			return True
		else:
			return False

	@frappe.whitelist()
	def create_ticket_invoice(self):
		charge=frappe.db.get_value("Customer Contract",{"name":self.contract},'charge_per_ticket')
		if charge and charge>0 and self.contract_status == "Active" and self.type == "Service Request":
			sales_inv=frappe.get_doc({"doctype":"Sales Invoice"})
			sales_inv.customer=self.customer
			sales_inv.due_date=frappe.utils.nowdate()
			qty=1
			# if self.billing_based_on=="Timesheet":
			# 	qty=round(self.total_duration/3600,1)#convert to hours
			# contract_rate=frappe.db.get_value("Covered Services",{"item":self.service,"parent":self.contract},['rate'])
			# print('contract rate',contract_rate)
			sales_inv.append("items", {
				"item_code": self.service_requested,
				"qty": qty,
				"rate":charge,
			})
			sales_inv.custom_ticket=self.name
			sales_inv.insert()
			self.ticket_invoice=1
			self.save()
			return True
	
	@frappe.whitelist()
	def get_contract(self):
		print("get_contract---"+f"""select cc.name,cc.status from `tabCustomer Contract` as cc join `tabContract Address Items` as addr on cc.name = addr.parent join `tabContract Covered Services` as sc on cc.name= sc.parent where addr.customer_address ='{self.customer_address}' and sc.service='{self.service_requested}' ORDER BY cc.creation DESC LIMIT 1;""")
		data=frappe.db.sql(f"""select cc.name,cc.status from `tabCustomer Contract` as cc join `tabContract Address Items` as addr on cc.name = addr.parent join `tabContract Covered Services` as sc on cc.name= sc.parent where addr.customer_address ='{self.customer_address}' and sc.service='{self.service_requested}' and cc.customer='{self.customer}' ORDER BY cc.creation DESC LIMIT 1;""",as_dict=True)
		print("data sql",data)
		if data:
			return data[0]
		else:
			return False
		return '4oefv9k1um'
	

	@frappe.whitelist()
	def create_service_req(self):
		print("create_service_req---")
		if self.contract_status == "Active":
			doc=frappe.get_doc({"doctype":"Service Request"})
			doc.service=self.service_requested
			doc.customer=self.customer
			doc.type="Service Under Contract"
			doc.ticket=self.name
			doc.subject=self.subject
			doc.priority=self.priority
			doc.customer_address=self.customer_address
			contract_status=frappe.db.get_value("Customer Contract",self.contract,'status')
			if contract_status:
				doc.contract_status=contract_status
			doc.item_name=self.item_name
			doc.request_details=self.request_details
			doc.insert()
			self.service_request=1
			self.save()
			return "Service Request"
		else:
			print("opportunity creation",self.contract,self.contract_status)
			return create_opportunity(self)

	# @frappe.whitelist()
	# def add_note(self):


def check_if_exists(doc,ticket):
	print("check_if_opp_exists",ticket)
	opp=frappe.db.exists(doc,{"custom_ticket":ticket})
	if opp:
		return True
	else:
		return False