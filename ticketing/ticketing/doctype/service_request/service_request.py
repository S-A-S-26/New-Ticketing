# Copyright (c) 2024, Dexciss and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
# from erpnext.support.doctype.service_level_agreement.service_level_agreement import ServiceLevelAgreement,apply,get_context
from ticketing.api import set_status,validate_resolution
from ticketing.sla_methods import apply

class ServiceRequest(Document):
	def validate(self):
		set_status(self,self.status,self.doctype,self.name,"Ticket",self.ticket)
		# apply(self)
		validate_resolution(self)

	@frappe.whitelist()
	def create_visit_request(self):
		doc=frappe.get_doc({"doctype":"Visit Request"})
		doc.customer=self.customer
		doc.company=self.company
		doc.reference_type="Service Request"
		doc.address=self.customer_address
		doc.ticket=self.ticket
		doc.service_request=self.name
		doc.request_details=self.request_details
		# doc.sla=self.sla
		# doc.sla_status=self.sla_status
		doc.insert()
		return True

	@frappe.whitelist()
	def check_if_service_is_paid(self):
		print(f"""SELECT tk.name,ccs.name,cs.name,ccs.item_name,ccs.service_type,ccs.remaining_free_service FROM `tabTicket` AS tk JOIN `tabCustomer Contract` AS cs ON tk.contract = cs.name JOIN `tabContract Covered Services` AS ccs ON cs.name = ccs.parent WHERE tk.name = "{self.ticket}" AND ccs.service = "{self.service}";""")
		data=frappe.db.sql(f"""SELECT tk.name,ccs.name,cs.name,ccs.item_name,ccs.service_type,ccs.remaining_free_service FROM `tabTicket` AS tk JOIN `tabCustomer Contract` AS cs ON tk.contract = cs.name JOIN `tabContract Covered Services` AS ccs ON cs.name = ccs.parent WHERE tk.name = "{self.ticket}" AND ccs.service = "{self.service}";""",as_dict=True)
		print("data",data)
		if data:
			data=data[0]
		else:
			return True
		print("data",data)
		# if not data:
		# 	return True
	
		if data.service_type == "Free Service":
			return False
		# elif data.service_type == "Pay by Hour":
		# 	return False
		elif data.service_type != "Free Service":
			return True
		else:
			return False
		
	@frappe.whitelist()
	def check_per_hour(self):
		if not self.service:
			return False
		data=frappe.db.sql(f"""SELECT ccs.service_type,ccs.remaining_free_service FROM `tabTicket` AS tk JOIN `tabCustomer Contract` AS cs ON tk.contract = cs.name JOIN `tabContract Covered Services` AS ccs ON cs.name = ccs.parent WHERE tk.name = "{self.ticket}" AND ccs.service = "{self.service}";""",as_dict=True)
		print("checkPayPerHour",data)
		if not data:
			return False
		else:
			return True if data[0].service_type == "Pay by Hour" else False;

	@frappe.whitelist()
	def create_sales_invoice_ticket(self):
		item_detail=self.check_remainig_free_services()
		self.create_service_log()
		print("item_detail",item_detail)
		if (item_detail.get('status')):
			return "Free Service"
		sales_inv=frappe.get_doc({"doctype":"Sales Invoice"})
		sales_inv.customer=self.customer
		sales_inv.due_date=frappe.utils.nowdate()
		sales_inv.append("items", {
			"item_code": self.service,
			"qty": self.billed_duration if self.billed_duration>=0.01 else 1,
			"rate":item_detail.get('price'),
		})
		sales_inv.custom_service_request=self.name   
		sales_inv.insert()
		return sales_inv.name

	def check_remainig_free_services(self):
		data=frappe.db.sql(f"""SELECT ccs.name,ccs.service_type,ccs.remaining_free_service,ccs.price FROM `tabTicket` AS tk JOIN `tabCustomer Contract` AS cs ON tk.contract = cs.name JOIN `tabContract Covered Services` AS ccs ON cs.name = ccs.parent WHERE tk.name = "{self.ticket}" AND ccs.service = "{self.service}";""",as_dict=True)
		print("check_remainig_free_services",data)
		if not data:
			return {"price":data[0].price,"status":False}
		elif data[0].remaining_free_service == 0:
			return {"price":data[0].price,"status":False}
		else:
			minus_val=1
			if self.billed_duration>0.001:
				minus_val=self.billed_duration
			if data[0].remaining_free_service > 0:
				frappe.db.set_value("Contract Covered Services",data[0].name,"remaining_free_service",data[0].remaining_free_service-minus_val)
				return {"price":data[0].price,"status":True}
	
	@frappe.whitelist()		
	def create_service_log(self):
		print("inside create_service_log")
		ser_log=frappe.get_doc({"doctype":"Service Log"})
		ser_log.service_request=self.name
		ser_log.ticket=self.ticket
		ser_log.type=self.type
		ser_log.insert()
		return True

	@frappe.whitelist()
	def check_if_free_service(self):
		print(f"""SELECT tk.name,ccs.name,cs.name,ccs.item_name,ccs.service_type,ccs.remaining_free_service FROM `tabTicket` AS tk JOIN `tabCustomer Contract` AS cs ON tk.contract = cs.name JOIN `tabContract Covered Services` AS ccs ON cs.name = ccs.parent WHERE tk.name = "{self.ticket}" AND ccs.service = "{self.service}";""")
		data=frappe.db.sql(f"""SELECT tk.name,ccs.name,cs.name,ccs.item_name,ccs.service_type,ccs.remaining_free_service FROM `tabTicket` AS tk JOIN `tabCustomer Contract` AS cs ON tk.contract = cs.name JOIN `tabContract Covered Services` AS ccs ON cs.name = ccs.parent WHERE tk.name = "{self.ticket}" AND ccs.service = "{self.service}";""",as_dict=True)
		print("data",data)
		if data:
			data=data[0]
		else:
			return True
		print("data",data)
		# if not data:
		# 	return True
	
		if data.service_type == "Free Service":
			return True