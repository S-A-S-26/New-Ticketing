import frappe 
from erpnext.support.doctype.service_level_agreement.service_level_agreement import ServiceLevelAgreement,get_customer_group,get_customer_territory,get_context,get_documents_with_active_service_level_agreement,remove_sla_if_applied,process_sla
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

class CustomServiceLevelAgreement(ServiceLevelAgreement):

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
        frappe.msgprint("get priority for service level agreement")
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
    frappe.msgprint("setting resolution time")
    start_date_time = get_datetime(doc.get("service_level_agreement_creation") or doc.creation)
    if doc.meta.has_field("resolution_time"):
        doc.resolution_time = time_diff_in_seconds(doc.resolution_date, start_date_time)
    if doc.meta.has_field("resolution_date"):
        print("inside if con for res date")
        doc.resolution_date = add_to_date(start_date_time, seconds=doc.resolution_time)

def get_active_service_level_agreement_for(doc):
    print("custom get_active_service_level_agreement")
    if not frappe.db.get_single_value("Support Settings", "track_service_level_agreement"):
        return

    filters = [
        ["Ticket Service Level Agreement", "document_type", "=", doc.get("doctype")],
        ["Ticket Service Level Agreement", "enabled", "=", 1],
    ]

    if doc.get("priority"):
        filters.append(["Service Level Priority", "priority", "=", doc.get("priority")])

    or_filters = []
    if doc.get("service_level_agreement"):
        or_filters = [
            ["Ticket Service Level Agreement", "name", "=", doc.get("service_level_agreement")],
        ]

    customer = doc.get("customer")
    if customer:
        or_filters.extend(
            [
                [
                    "Ticket Service Level Agreement",
                    "entity",
                    "in",
                    [customer, *get_customer_group(customer), *get_customer_territory(customer)],
                ],
                ["Ticket Service Level Agreement", "entity_type", "is", "not set"],
            ]
        )
    else:
        or_filters.append(["Ticket Service Level Agreement", "entity_type", "is", "not set"])

    default_sla_filter = [*filters, ["Ticket Service Level Agreement", "default_service_level_agreement", "=", 1]]
    default_sla = frappe.get_all(
        "Ticket Service Level Agreement",
        filters=default_sla_filter,
        fields=["name", "default_priority", "apply_sla_for_resolution", "condition"],
    )

    filters += [["Ticket Service Level Agreement", "default_service_level_agreement", "=", 0]]
    agreements = frappe.get_all(
        "Ticket Service Level Agreement",
        filters=filters,
        or_filters=or_filters,
        fields=["name", "default_priority", "apply_sla_for_resolution", "condition"],
    )

    # check if the current document on which SLA is to be applied fulfills all the conditions
    filtered_agreements = []
    for agreement in agreements:
        condition = agreement.get("condition")
        if not condition or (condition and frappe.safe_eval(condition, None, get_context(doc))):
            filtered_agreements.append(agreement)

    # if any default sla
    filtered_agreements += default_sla

    return filtered_agreements[0] if filtered_agreements else None
    
def apply(doc, method=None):
    import traceback
    for line in traceback.format_stack():
        print("Tback",line.strip())
    # Applies SLA to document on validate
    if (
        frappe.flags.in_patch
        or frappe.flags.in_migrate
        or frappe.flags.in_install
        or frappe.flags.in_setup_wizard
        or doc.doctype not in get_documents_with_active_service_level_agreement()
    ):
        return

    sla = get_active_service_level_agreement_for(doc)
    print("sla in apply",sla)
    if not sla:
        remove_sla_if_applied(doc)
        return

    process_sla(doc, sla)