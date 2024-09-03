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

		# deduction_on_visit_req(self)