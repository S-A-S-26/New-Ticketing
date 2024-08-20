# Copyright (c) 2024, Dexciss and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime

class Warranty(Document):
	
	def validate(self):
		self.set_warranty_status()
		self.check_from_expiry()
		# self.warranty_period_val()
	
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

	def check_from_expiry(self):
		for i in self.warranty_equipments:
			if i.warranty_expiry_date < self.from_date:
				frappe.throw("Warranty Expiry date should be greater than from date")

	@frappe.whitelist()
	def warranty_period_val(self,selected):
		selected=frappe._dict(selected)
		print("selected",selected,type(selected))
		print("self from date",self.from_date)
		if not self.from_date:
			frappe.throw("Please add the From Date")
		self.from_date=self.from_date.split(".")[0]
		from_date= datetime.strptime(self.from_date, '%Y-%m-%d %H:%M:%S')
		days=round((datetime.strptime(selected.warranty_expiry_date, '%Y-%m-%d %H:%M:%S')-from_date).total_seconds()/86400,1)
		print("warranty period",selected.warranty_expiry_date,datetime.now(),datetime.strptime(selected.warranty_expiry_date, '%Y-%m-%d %H:%M:%S')-datetime.now(),type(selected.warranty_expiry_date),type(selected.warranty_period),days,selected.warranty_period)
		if selected.warranty_period and float(selected.warranty_period) > 0 and days > float(selected.warranty_period):
			frappe.throw(f"Warranty period should be less than or equal to the remaining days currently {days} days")
			
		# for i in self.warranty_equipments:
		# 	days=round((datetime.strptime(i.warranty_expiry_date, '%Y-%m-%d %H:%M:%S')-datetime.now()).total_seconds()/86400,1)
		# 	print("warranty period",i.warranty_expiry_date,datetime.now(),datetime.strptime(i.warranty_expiry_date, '%Y-%m-%d %H:%M:%S')-datetime.now(),type(i.warranty_expiry_date),type(i.warranty_period),days,i.warranty_period)
		# 	if i.warranty_period and int(i.warranty_period) > 0 and days > int(i.warranty_period):
		# 		frappe.throw(f"Warranty period should be less than or equal to the remaining days currently {days} days")
