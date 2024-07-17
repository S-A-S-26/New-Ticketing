# Copyright (c) 2024, Dexciss and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from ticketing.api import set_status

class RepairRequest(Document):
	def validate(self):
		set_status(self.status,self.doctype,self.name,"Ticket",self.ticket)
