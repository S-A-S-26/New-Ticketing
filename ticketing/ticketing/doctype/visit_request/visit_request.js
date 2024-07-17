// Copyright (c) 2024, Dexciss and contributors
// For license information, please see license.txt

frappe.ui.form.on("Visit Request", {
	refresh(frm) {
        let sch_d = new frappe.ui.Dialog({
            title: 'Schedule Visit',
            fields: [
                {
                    default: "Today",
                    fieldname: "schedule_date",
                    fieldtype: "Datetime",
                    in_standard_filter: 1,
                    label: "Requested Date",
                    reqd: 1
                },
  
            ],
            size: 'small', // small, large, extra-large 
            primary_action_label: 'Submit',
            primary_action(values) {
                console.log(values);
                frm.doc.scheduled_date=values.schedule_date
                frm.doc.status="Scheduled"
                frm.refresh_field("scheduled_date")
                frm.refresh_field("status")
                frm.dirty()
                sch_d.hide();
            }
        });
        
        
        frm.add_custom_button("Schedule Visit",function(){
            sch_d.show();
        },"Set")

        frm.add_custom_button("Re-Schedule Visit",function(){
            sch_d.show();
        },"Set")

        frm.add_custom_button("In-Progress",function(){
            frm.doc.status="In Progress"
            frm.refresh_field("status")
            frm.dirty()
        },"Set")

        frm.add_custom_button("Completed",function(){
            frm.doc.status="Completed"
            frm.refresh_field("status")
            frm.dirty()
        },"Set")
	},
});
