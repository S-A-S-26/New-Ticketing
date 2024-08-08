// Copyright (c) 2024, Dexciss and contributors
// For license information, please see license.txt

frappe.ui.form.on('Warranty', {
	// refresh: function(frm) {

	// },
});


frappe.ui.form.on('Warranty Equipments', {
	// refresh: function(frm) {

	// },
	warranty_expiry_date:function(frm){
		console.log("cur frm.sel",frm.selected_doc)
		frappe.call({
			method:'warranty_period_val',
			doc:frm.doc,
			args:{
				'selected':frm.selected_doc,
			},
			error: function(r) {
				console.log("error")
				frm.selected_doc.warranty_expiry_date=undefined
				frm.refresh_field('warranty_equipments')
			},
		})
	}
});