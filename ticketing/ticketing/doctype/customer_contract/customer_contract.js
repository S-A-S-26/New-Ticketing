// Copyright (c) 2024, Dexciss and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Customer Contract", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on("Contract Covered Services", {
        max_free_services:function(frm) {
            frm.selected_doc.remaining_free_service=frm.selected_doc.max_free_services
            frm.refresh_field("contract_covered_services")
    	},
    });