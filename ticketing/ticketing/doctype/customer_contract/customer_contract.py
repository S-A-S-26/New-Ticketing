# Copyright (c) 2024, Dexciss and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CustomerContract(Document):
	
	def validate(self):
		if self.from_date>self.to_date:
			frappe.throw("From Date should be less than To Date")
