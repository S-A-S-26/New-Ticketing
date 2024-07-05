# Copyright (c) 2024, Dexciss and contributors
# For license information, please see license.txt

import frappe
from datetime import timedelta 
from frappe.model.document import Document
from frappe.utils import (
	add_to_date,
	get_datetime,
	get_weekdays,
	getdate,
	now_datetime,
	time_diff_in_seconds,
	to_timedelta,
)
from ticketing.api import get_sla


class Ticket(Document):
	
	def validate(self):
		pass
		# if self.is_new():
		# 	self.service_level_agreement_creation=
		# if self.link_yrud:
		# 	sla=frappe.get_doc("Service Level Agreement",self.link_yrud)
		# 	get_sla(self,sla)
	
	@frappe.whitelist()
	def get_contract(self):
		print("get_contract")
		contract=frappe.db.sql(f"""select cc.name from `tabCustomer Contract` as cc join `tabContract Address Items` as addr on cc.name = addr.parent join `tabContract Covered Services` as sc on cc.name= sc.parent where addr.customer_address ='{self.customer_address}' and sc.service='{self.service_requested}' ORDER BY cc.creation DESC LIMIT 1;""",pluck=True)
		print("contract",contract)
		return contract