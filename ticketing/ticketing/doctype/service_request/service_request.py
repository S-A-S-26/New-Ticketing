# Copyright (c) 2024, Dexciss and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ServiceRequest(Document):
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
		data=frappe.db.sql(f"""select cs.name,ccs.item_name,ccs.service_type,ccs.remaining_free_service  from `tabService Request` as sr join `tabTicket` as tk on sr.ticket = tk.name join `tabCustomer Contract` as cs on tk.contract=cs.name join `tabContract Covered Services` as ccs on cs.name=ccs.parent where tk.name="{self.ticket}" and ccs.service="{self.service}";""",as_dict=True)
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
		