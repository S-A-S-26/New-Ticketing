import frappe 
from erpnext.support.doctype.service_level_agreement.service_level_agreement import ServiceLevelAgreement
from frappe.model.document import Document
from frappe.utils import (
	add_to_date,
	get_datetime,
	get_datetime_str,
	get_link_to_form,
	get_system_timezone,
	get_time,
	get_weekdays,
	getdate,
	nowdate,
	time_diff_in_seconds,
	to_timedelta,
)

class ServiceLevelAgreement(Document):

    def before_insert(self):
        print("custom method overridenn")
		# no need to set up SLA fields for Issue dt as they are standard fields in Issue
        if self.document_type in ["Issue","Ticket","Service Request"]:
            return
        print("self",self.__dict__)
        meta = frappe.get_meta(self.document_type, cached=False)
        # frappe.throw("sla Custom Field {'fieldname': 'service_level_section'} not found")
        print("meta",meta,meta.__dict__,meta.custom)

    def get_service_level_agreement_priority(self, priority):
        priority = frappe.get_doc("Service Level Priority", {"priority": priority, "parent": self.name})

        return frappe._dict(
            {
                "priority": priority.priority,
                "response_time": priority.response_time,
                "resolution_time": priority.resolution_time,
            }
        )    
    
    def set_resolution_time(doc):
        print("setting resolution date")
        start_date_time = get_datetime(doc.get("service_level_agreement_creation") or doc.creation)
        if doc.meta.has_field("resolution_time"):
            doc.resolution_time = time_diff_in_seconds(doc.resolution_date, start_date_time)
        if doc.meta.has_field("resolution_date"):
            print("inside if con for res date")
            doc.resolution_date = add_to_date(start_date_time, seconds=doc.resolution_time)