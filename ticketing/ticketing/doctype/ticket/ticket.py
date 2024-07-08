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
		if self.contract:
			print(f"""select tk.name from `tabTicket` as tk join `tabCustomer Contract` as cc on tk.contract=cc.name where tk.creation BETWEEN cc.from_date AND cc.to_date and cc.customer='{self.customer}' AND cc.name='{self.contract}';
			""")
			already_ticket=frappe.db.sql(f"""select tk.name from `tabTicket` as tk join `tabCustomer Contract` as cc on tk.contract=cc.name where tk.creation BETWEEN cc.from_date AND cc.to_date and cc.customer='{self.customer}' AND cc.name='{self.contract}';
			""",pluck=True)
		# if already_ticket:
		# 	frappe.throw(f"A ticket already exists for the customer {self.customer} with contract {self.contract}")
	
	@frappe.whitelist()
	def get_contract(self):
		print("get_contract---"+f"""select cc.name,cc.status from `tabCustomer Contract` as cc join `tabContract Address Items` as addr on cc.name = addr.parent join `tabContract Covered Services` as sc on cc.name= sc.parent where addr.customer_address ='{self.customer_address}' and sc.service='{self.service_requested}' ORDER BY cc.creation DESC LIMIT 1;""")
		data=frappe.db.sql(f"""select cc.name,cc.status from `tabCustomer Contract` as cc join `tabContract Address Items` as addr on cc.name = addr.parent join `tabContract Covered Services` as sc on cc.name= sc.parent where addr.customer_address ='{self.customer_address}' and sc.service='{self.service_requested}' and cc.customer='{self.customer}' ORDER BY cc.creation DESC LIMIT 1;""",as_dict=True)
		print("data sql",data)
		if data:
			return data[0]
		else:
			return False
		return '4oefv9k1um'