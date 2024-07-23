# Copyright (c) 2024, Dexciss and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
# from erpnext.support.doctype.service_level_agreement.service_level_agreement import ServiceLevelAgreement,apply,get_context
from ticketing.api import set_status
from ticketing.sla_methods import apply

class ServiceRequest(Document):
	def validate(self):
		set_status(self.status,self.doctype,self.name,"Ticket",self.ticket)
		apply(self)

	@frappe.whitelist()
	def create_visit_request(self):
		doc=frappe.get_doc({"doctype":"Visit Request"})
		doc.customer=self.customer
		doc.reference_type="Service Request"
		doc.address=self.customer_address
		doc.ticket=self.ticket
		doc.service_request=self.name
		doc.request_details=self.request_details
		doc.sla=self.sla
		doc.sla_status=self.sla_status
		doc.insert()

	@frappe.whitelist()
	def check_if_service_is_paid(self):
		print(f"""SELECT tk.name,ccs.name,cs.name,ccs.item_name,ccs.service_type,ccs.remaining_free_service FROM `tabTicket` AS tk JOIN `tabCustomer Contract` AS cs ON tk.contract = cs.name JOIN `tabContract Covered Services` AS ccs ON cs.name = ccs.parent WHERE tk.name = "{self.ticket}" AND ccs.service = "{self.service}";""")
		data=frappe.db.sql(f"""SELECT tk.name,ccs.name,cs.name,ccs.item_name,ccs.service_type,ccs.remaining_free_service FROM `tabTicket` AS tk JOIN `tabCustomer Contract` AS cs ON tk.contract = cs.name JOIN `tabContract Covered Services` AS ccs ON cs.name = ccs.parent WHERE tk.name = "{self.ticket}" AND ccs.service = "{self.service}";""",as_dict=True)
		print("data",data)
		if data:
			data=data[0]
		print("data",data)
		# if not data:
		# 	return True
		if data.service_type == "Free Service":
			return False
		elif data.service_type != "Free Service" and data.remaining_free_service == 0:
			return True
		else:
			return False
		
	@frappe.whitelist()
	def check_per_hour(self):
		if not self.service:
			return False
		data=frappe.db.sql(f"""SELECT ccs.service_type FROM `tabTicket` AS tk JOIN `tabCustomer Contract` AS cs ON tk.contract = cs.name JOIN `tabContract Covered Services` AS ccs ON cs.name = ccs.parent WHERE tk.name = "{self.ticket}" AND ccs.service = "{self.service}";""",pluck=True)
		print("checkPayPerHour",data)
		if not data:
			return False
		else:
			return True if data[0] == "Pay by Hour" else False;