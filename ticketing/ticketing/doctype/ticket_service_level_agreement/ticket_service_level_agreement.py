# Copyright (c) 2024, Dexciss and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class TicketServiceLevelAgreement(Document):
	def get_service_level_agreement_priority(self, priority):
		priority = frappe.get_doc("Service Level Priority", {"priority": priority, "parent": self.name})

		return frappe._dict(
			{
				"priority": priority.priority,
				"response_time": priority.response_time,
				"resolution_time": priority.resolution_time,
			}
		)
