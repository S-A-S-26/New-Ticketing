// Copyright (c) 2024, Dexciss and contributors
// For license information, please see license.txt

frappe.ui.form.on('Repair Request', {
	refresh: function(frm) {
        frappe.provide("erpnext.utils");
		if (!frm.doc.display_address){
			frm.trigger("address")
		}
		show_notes(frm)
		if (!frm.doc.__islocal){
			frm.trigger('is_visit_required')
		}
	},
    address:function(frm){
        erpnext.utils.get_address_display(frm, "address","display_address");
    },
    is_visit_required:function(frm){
		if (frm.doc.__islocal){
			return
		}
		if(frm.doc.is_visit_required){
            frm.add_custom_button("Visit Request",function(){
				frappe.call({
					method:"create_visit_request",
					doc:frm.doc,
					freeze:true,
					freeze_message:"Creating Visit Request",
					callback: function(r, rt){
						console.log("r.message=",r);
						
						if(r.message){
							frappe.msgprint("Visit Request Created Successfully")
						}else{
							frappe.msgprint("Visit Request Failed")
						}
					}
				})
			},"Create")
        }else{
            frm.remove_custom_button("Visit Request","Create"); 
        }
	},
});

function show_notes(frm) {
    const crm_notes = new erpnext.utils.CRMNotes({
        frm: frm,
        notes_wrapper: $(frm.fields_dict.notes_html.wrapper),
    });
    crm_notes.refresh();

    frm.dirty();
}
