// Copyright (c) 2024, Dexciss and contributors
// For license information, please see license.txt

frappe.ui.form.on("Ticket", {
	// refresh(frm) {

	// },
    service_requested:function(frm){
        frappe.call({
            method:"get_contract",
            doc:frm.doc,
            freeze:true,
            freeze_message:"Fetching contract",
            callback: function(r, rt){
                if(r.message){
                    frm.set_value("contract", r.message);
                }
            }
        })
    }
});
