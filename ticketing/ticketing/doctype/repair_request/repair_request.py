# Copyright (c) 2024, Dexciss and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from ticketing.api import set_status,validate_resolution
from erpnext.crm.utils import (
	CRMNote,
	copy_comments,
	link_communications,
	link_open_events,
	link_open_tasks,
)

class RepairRequest(CRMNote):
	def validate(self):
		validate_resolution(self)
		set_status(self,self.status,self.doctype,self.name,"Ticket",self.ticket)

	@frappe.whitelist()
	def create_visit_request(self):
		doc=frappe.get_doc({"doctype":"Visit Request"})
		doc.customer=self.customer
		doc.reference_type="Repair Request"
		doc.address=self.address
		doc.ticket=self.ticket
		doc.repair_request=self.name
		doc.request_details=self.request_details
		doc.company = self.company
		# doc.
		# doc.sla=self.sla
		# doc.sla_status=self.sla_status
		doc.insert(ignore_mandatory=True)
		return True

	@frappe.whitelist()
	def create_repair_invoice(self):
		sales_inv=frappe.get_doc({"doctype":"Sales Invoice"})
		sales_inv.customer=self.customer
		sales_inv.company=self.company
		sales_inv.due_date=frappe.utils.nowdate()
		sales_inv.append("items", {
			"item_code": self.equipment,
			"qty": 1,
			"rate":self.price_per_repair,
		})
		sales_inv.custom_repair_request=self.name   
		sales_inv.insert()
		return sales_inv.name