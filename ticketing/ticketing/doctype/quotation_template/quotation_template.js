// Copyright (c) 2024, Dexciss and contributors
// For license information, please see license.txt

frappe.ui.form.on("Quotation Template", {
	refresh(frm) {
		frm.fields_dict['template_items'].grid.get_field('item').get_query = function(doc, cdt, cdn) {
			var child = locals[cdt][cdn];
			// console.log(child);
			return {
				filters: [
					['is_sales_item', '=', 1],
					['has_variants', '=', 0]
				]
			}
		}
	},
});
