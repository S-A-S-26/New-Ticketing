# Copyright (c) 2024, Dexciss and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class Warranty(Document):
	
	def validate(self):
		self.set_warranty_status()
	
	def before_submit(self):
		self.warranty_status = "Active"
		for item in self.warranty_equipments:
			if True or item.status == "Draft":
				item.status = "Active"


	def set_warranty_status(self):
		for item in self.warranty_equipments:
			if item.status == 'Expiring':
				self.warranty_status = 'Expiring'
				return