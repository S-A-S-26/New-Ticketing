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


@frappe.whitelist()
def get_sla(self,sla):
    set_response_by(self,sla)
    set_resolution_by(self,sla)

def get_holidays(self):
    res = []
    if not self.holiday_list:
        return res
    holiday_list = frappe.get_doc("HD Service Holiday List", self.holiday_list)
    for row in holiday_list.holidays:
        res.append(row.holiday_date)
    return res

def get_priorities(self):
    """
    Return priorities related info as a dict. With `priority` as key
    """
    res = {}
    for row in self.priorities:
        res[row.priority] = row
    return res

def get_workdays(self) -> dict[str, dict]:
    """
    Return workdays related info as a dict. With `workday` as key
    """
    res = {}
    for row in self.support_and_resolution:
        res[row.workday] = row
    return res

def set_response_by(self, doc: Document):
    start = doc.service_level_agreement_creation#need to open the field
    doc.response_by = self.calc_time(start, doc.priority, "response_time")

def set_resolution_by(self, doc: Document):
    total_hold_time = doc.total_hold_time or 0
    start = add_to_date(
        doc.service_level_agreement_creation,
        seconds=total_hold_time,
        as_datetime=True,
    )
    doc.resolution_by = self.calc_time(start, doc.priority, "resolution_time")

def calc_time(
    self,
    start_at: str,
    priority: str,
    target,
):#this needs to be passed on with a sla account self
    res = get_datetime(start_at)
    priority = self.get_priorities()[priority]
    time_needed = priority.get(target, 0)
    holidays = self.get_holidays()
    weekdays = get_weekdays()
    workdays = self.get_workdays()
    while time_needed:
        today = res
        today_day = getdate(today)
        today_weekday = weekdays[today.weekday()]
        is_workday = today_weekday in workdays
        is_holiday = today_day in holidays
        if is_holiday or not is_workday:
            res = add_to_date(res, days=1, as_datetime=True)
            continue
        today_workday = workdays[today_weekday]
        now_in_seconds = time_diff_in_seconds(today, today_day)
        start_time = max(today_workday.start_time.total_seconds(), now_in_seconds)
        till_start_time = max(start_time - now_in_seconds, 0)
        end_time = max(today_workday.end_time.total_seconds(), now_in_seconds)
        time_left = max(end_time - start_time, 0)
        if not time_left:
            res = getdate(add_to_date(res, days=1, as_datetime=True))
            continue
        time_taken = min(time_needed, time_left)
        time_needed -= time_taken
        time_required = till_start_time + time_taken
        res = add_to_date(res, seconds=time_required, as_datetime=True)
    return res