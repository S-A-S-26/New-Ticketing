import frappe
from datetime import datetime

def set_visit_status():
    visit_reqs=frappe.db.get_all("Visit Request",{"status":"Scheduled"},pluck="name")
    print("visit_reqs",visit_reqs)
    for visit_req in visit_reqs:
        req=frappe.get_doc("Visit Request",visit_req)
        
        if req.scheduled_date < datetime.now():
            print("od",visit_req)
            req.status="Overdue"
            req.save()
        else:
            print("intime",visit_req)