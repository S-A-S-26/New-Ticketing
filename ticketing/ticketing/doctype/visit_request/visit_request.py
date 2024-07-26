# Copyright (c) 2024, Dexciss and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from ticketing.api import set_status,validate_resolution
from erpnext.crm.utils import (
	CRMNote,
	copy_comments,
	link_communications,
	link_open_events,
	link_open_tasks,
)


class VisitRequest(CRMNote):
	def validate(self):
		validate_resolution(self)
		if self.reference_type == "Repair Request":
			print("repair req")
			set_status(self.status,self.doctype,self.name,"Repair Request",self.repair_request)
		else:
			set_status(self.status,self.doctype,self.name,"Service Request",self.service_request)
