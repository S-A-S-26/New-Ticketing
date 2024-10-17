// Copyright (c) 2024, Dexciss and contributors
// For license information, please see license.txt

frappe.ui.form.on("Certificate of Insurance", {
	refresh(frm) {
		frm.fields_dict['floor'].get_query = function(doc, cdt, cdn) {
			console.log("site address", frm.doc.site_address)
			const address = frm.doc.site_address.map((obj) => obj.address)
			console.log("filter address", address)
			return {
				filters: { "customer_address": ["in", address] }
			};
		};
	},
});
