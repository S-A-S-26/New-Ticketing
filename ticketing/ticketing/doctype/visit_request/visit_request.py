# Copyright (c) 2024, Dexciss and contributors
# For license information, please see license.txt

import datetime
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
		print("self visiwst",self.__dict__)
		# print(self.__islocal)
		if not self.is_new():
			check_service_repair(self)
		if not self.visit_duration:
			self.visit_duration = 0
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

	@frappe.whitelist()
	def create_visit_log(self):
		if not self.visit_completed_by:
			frappe.throw("Please add VisitCompleted by")
		visit_log=frappe.get_doc({"doctype":"Visit Log"})
		visit_log.visit_completed_by=self.visit_completed_by
		visit_log.date = datetime.datetime.now()
		visit_log.visit_request=self.name
		visit_log.ticket=self.ticket
		visit_log.reference_type =  self.reference_type
		if self.reference_type == "Repair Request":
			visit_log.repair_request=self.repair_request
		else:
			visit_log.service_request=self.service_request
		visit_log.insert()

	@frappe.whitelist()
	def create_visit_invoice(self):
		print("create visit invoice")
		item={'name':"",'price':""}
		sales_inv=frappe.get_doc({"doctype":"Sales Invoice"})
		if self.reference_type == "Repair Request":
			item['name'] = frappe.db.get_value("Repair Request",self.repair_request,'equipment')
			item['price'] = frappe.db.get_value("Repair Request",self.repair_request,'price_per_visit')
			print("item in repair ",item)
		else:
			item['name'] = frappe.db.get_value("Service Request",self.service_request,'service')
			# select cc.name,cc.price_per_visit  from `tabVisit Request` as vr join `tabService Request` as sr on vr.service_request=sr.name join `tabTicket` as tk on sr.ticket=tk.name join `tabCustomer Contract` as cc on tk.contract=cc.name where vr.service_request='SR0053';
			data_customer= frappe.db.sql(f"select cc.name,cc.price_per_visit  from `tabVisit Request` as vr join `tabService Request` as sr on vr.service_request=sr.name join `tabTicket` as tk on sr.ticket=tk.name join `tabCustomer Contract` as cc on tk.contract=cc.name where vr.service_request='{self.service_request}';",as_dict=True)
			print("data_customer",data_customer)
			if data_customer:
				item['price']= data_customer[0]['price_per_visit']
			print("item in service",item)
			
		if not item: 
			frappe.throw("No equipment or service found for the given reference.")

		sales_inv.customer=self.customer
		sales_inv.company=self.company
		sales_inv.due_date=frappe.utils.nowdate()
		sales_inv.custom_visit_request=self.name   
		sales_inv.append("items", {
			"item_code": item['name'],
			"qty": 1,
			"rate": item['price'],
		})
		sales_inv.insert()
		self.create_visit_log()
		self.create_material_request(item['name'])
		return sales_inv.name

	@frappe.whitelist()
	def deduction_on_visit_req(self):
		print(f"""select cc.name,cc.free_visit,cc.price_per_visit,cc.remaining_free_visits,cc.visit_requested from `tabService Request` as sr join `tabCustomer Contract` as cc on cc.name=sr.customer_contract join `tabVisit Request` as vr on sr.name=vr.{self.reference_type.replace(' ',"_").lower()} where vr.{self.reference_type.replace(' ',"_").lower()}="{self.service_request if self.reference_type=='Service Request' else self.repair_request}";""")
		visitData=frappe.db.sql(f"""select cc.name,cc.free_visit,cc.price_per_visit,cc.remaining_free_visits,cc.visit_requested from `tabService Request` as sr join `tabCustomer Contract` as cc on cc.name=sr.customer_contract join `tabVisit Request` as vr on sr.name=vr.{self.reference_type.replace(' ',"_").lower()} where vr.{self.reference_type.replace(' ',"_").lower()}="{self.service_request if self.reference_type=='Service Request' else self.repair_request}";""",as_dict=True)
		print("visit Data",visitData)
		# visitData= frappe.db.get_value("Customer Contract", self.name,['free_visit',"price_per_visit"])
		if not visitData:
			return
		visitData=frappe._dict(visitData[0])
		availVisits=visitData.remaining_free_visits
		charge=visitData.price_per_visit
		cc_name= visitData.name
		visit_requested=visitData.visit_requested

		
		if not charge:
			frappe.throw("Visit Charge is zero in Customer Contract Doctype")

		if availVisits and availVisits>0:
			print("deduct from existing",cc_name)
			frappe.db.set_value("Customer Contract",cc_name,'remaining_free_visits',availVisits-1,update_modified=False)
			# return True
		else:
		#     sales_inv=frappe.get_doc({"doctype":"Sales Invoice"})
		#     sales_inv.customer=self.customer
		#     sales_inv.company=self.company
		#     sales_inv.due_date=frappe.utils.nowdate()
		#     sales_inv.append("items", {
		#         "item_code": item_code,
		#         "qty": qty,
		#         "rate":rate,
		#     })
		#     sales_inv.custom_ticket=doc_name   
		#     sales_inv.insert()
		#     return sales_inv.name
			self.create_visit_invoice()
		print("visit req",visit_requested)
		frappe.db.set_value("Customer Contract",cc_name,'visit_requested',visit_requested+1,update_modified=False)
		self.create_visit_log()
		return True

	@frappe.whitelist()
	def create_material_request(self,item):
		mr=frappe.get_doc({"doctype":"Material Request"})
		mr.material_request_type="Purchase"
		mr.transaction_date=datetime.datetime.now().date()
		mr.schedule_date=datetime.datetime.now().date()
		mr.custom_visit_request=self.name
		mr.company=self.company
		item_uom=frappe.db.get_value("Item",item,['stock_uom'])
		mr.append("items",{
			"item_code":item,
			"schedule_date":datetime.datetime.now().date(),
			"qty":1,
			"uom":item_uom,
			"warehouse":"All Warehouses - TMG",
		})
		mr.insert()

	@frappe.whitelist()
	def check_sales_exists(self,item):
		inv=frappe.db.exists("Sales Invoice",{"custom_visit_request":self.name})
		print("inv",inv)
		if inv:
			return True
		return False

		# deduction_on_visit_req(self)
def check_service_repair(self):
	if self.reference_type == "Service Request":
		tk= frappe.db.get_value("Service Request",{"name":self.service_request},'ticket')
		if not tk or self.ticket != tk:
			frappe.throw(f"The Service Request '{self.service_request}' is not associated with ticket '{self.ticket}'")
		pass
	else:
		tk= frappe.db.get_value("Repair Request",{"name":self.repair_request},'ticket')
		if not tk or self.ticket != tk:
			frappe.throw(f"The Service Request '{self.repair_request}' is not associated with ticket '{self.ticket}'")