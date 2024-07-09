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