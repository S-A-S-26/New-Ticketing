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

class RepairRequest(CRMNote):
	def validate(self):
		validate_resolution(self)
		set_status(self.status,self.doctype,self.name,"Ticket",self.ticket)
