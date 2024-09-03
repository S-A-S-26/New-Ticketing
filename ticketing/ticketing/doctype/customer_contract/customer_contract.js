// Copyright (c) 2024, Dexciss and contributors
// For license information, please see license.txt

frappe.ui.form.on("Customer Contract", {
	refresh(frm) {

	},
        free_visit:function(frm){
                console.log("free_visit")
                frm.doc.remaining_free_visits =frm.doc.free_visit
                frm.refresh_field('remaining_free_visits')
        }
});

frappe.ui.form.on("Contract Covered Services", {
        max_free_services:function(frm) {
            frm.selected_doc.remaining_free_service=frm.selected_doc.max_free_services
            frm.refresh_field("contract_covered_services")
    	},
        
    });