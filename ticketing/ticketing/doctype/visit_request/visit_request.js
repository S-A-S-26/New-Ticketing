// Copyright (c) 2024, Dexciss and contributors
// For license information, please see license.txt

frappe.ui.form.on("Visit Request", {
    after_save(frm){
        frm.refresh()
    },
	refresh(frm) {
        frappe.provide("erpnext.utils");
		if (frm.doc.address && !frm.doc.display_address){
			// frm.trigger("address")
            frappe.call({
                method: 'frappe.contacts.doctype.address.address.get_address_display',
                args: {
                    address_dict: frm.doc.address
                },
                callback: function(r) {
                    frm.doc.display_address=r.message
                    frm.refresh_field("display_address")
                }
            })
		}
        show_notes(frm)
        
        if(frm.doc.repair_request){
            frappe.db.get_value('Repair Request', frm.doc.repair_request, 'price_per_visit')
            .then(r => {
                console.log(r.message.price_per_visit) // Open
                if (r.message.price_per_visit>0){
                    frm.add_custom_button("Create Repair Visit Invoice", function(){
                        frappe.call({
                            method:"create_visit_invoice",
                            doc:frm.doc,
                            freeze:true,
                            freeze_message:"Creating Visit Invoice",
                            callback: function(r) {
                                if(r.message){
                                    frappe.msgprint("Visit Invoice Successfully.");
                                } else{
                                    frappe.msgprint("Failed to Create Visit Invoice.");
                                }
                            }
                        })
                    },"Create")
                }
            })
        }

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
                const req_date=frappe.datetime.str_to_obj(frm.doc.requested_date)
                const sch_date=frappe.datetime.str_to_obj(values.schedule_date)
                console.log(typeof(req_date),typeof(sch_date))
                if (sch_date<req_date){
                    frappe.throw("Schedule date must be greater than requested date")
                }
                frm.doc.scheduled_date=values.schedule_date
                frm.doc.status="Scheduled"
                frm.refresh_field("scheduled_date")
                frm.refresh_field("status")
                frm.dirty()
                sch_d.hide();
                frm.save()
            }
        });
        
        if (frm.doc.status == "To Schedule"){
            frm.add_custom_button("Schedule Visit",function(){
                sch_d.show();
            },"Set")
        }else{
            frm.remove_custom_button("Schedule Visit","Set"); 
        }

        if (frm.doc.status == "Overdue" || frm.doc.status == "Completed"){
            frm.add_custom_button("Re-Schedule Visit",function(){
                sch_d.show();
            },"Set")
        }else{
            frm.remove_custom_button("Re-Schedule Visit","Set"); 
        }

        if (frm.doc.status == "Scheduled"){
            frm.add_custom_button("In-Progress",function(){
                frm.doc.status="In Progress"
                frm.refresh_field("status")
                frm.dirty()
                frm.save()
            },"Set")
        }else{
            frm.remove_custom_button("In-Progress","Set"); 
        }

        show_completed_button(frm)

        if(frm.doc.reference_type=="Service Request"){
                // frm.add_custom_button("Create Service Visit Invoice",function(){
                //     frappe.call({
                //         method:"ticketing.api.deduction_on_visit_req",
                //         args:{
                //             reference_type:frm.doc.reference_type,
                //             service_request:frm.doc.service_request,
                //             repair_request:frm.doc.repair_request,
                //             name:frm.doc.name,
                //         },
                //         callback: function(r) {
                //             if(r.message){
                //                 frappe.msgprint("Visit Invoice created successfully.");
                //             } else{
                //                 frappe.msgprint("Failed to Create Visit Invoice.");
                //             }
                //         }
                //     })
                // },"Create")
                frm.add_custom_button("Create Service Visit Invoice",function(){
                    frappe.call({
                        method:"deduction_on_visit_req",
                        doc:frm.doc,
                        freeze:true,
                        freeze_message:"Creating Visit Invoice",
                        callback: function(r) {
                            if(r.message){
                                frappe.msgprint("Visit Invoice created successfully.");
                            } else{
                                frappe.msgprint("Failed to Create Visit Invoice.");
                            }
                        }
                    })
                },"Create")
        }

        frm.set_query('ticket', () => {
            if(frm.doc.reference_type == "Service Request"){
                return {
                    filters: {
                        type: ['in', ['Service Request']]
                    }
                }
            }else{
                return {
                    filters: {
                        type: ['in', ['Equipment Issue']]
                    }
                }
            }
        })
        
	},
    address:function(frm){
        erpnext.utils.get_address_display(frm, "address","display_address");
        console.log("frm.doc.__unsaved",frm.doc.__unsaved)
    },
    reference_type: function(frm){
        frm.doc.ticket= undefined
        frm.doc.repair_request=undefined
        frm.doc.service_request=undefined
        frm.refresh_fields(['ticket','repair_request','service_request'])
    },
    visit_completed_by:function(frm){
        show_completed_button(frm)
    },
    visit_duration:function(frm){
        show_completed_button(frm)
    }
});


function show_notes(frm) {
    const crm_notes = new erpnext.utils.CRMNotes({
        frm: frm,
        notes_wrapper: $(frm.fields_dict.notes_html.wrapper),
    });
    crm_notes.refresh();

    // frm.dirty();
}


function show_completed_button(frm){
    if (frm.doc.status == "In Progress" && frm.doc.visit_completed_by && frm.doc.visit_duration){
        frm.add_custom_button("Completed",function(){
            frm.doc.status="Completed"
            frm.refresh_field("status")
            frm.dirty()
            frm.save()
        },"Set")
    }else{
        frm.remove_custom_button("Completed","Set"); 
    }
}