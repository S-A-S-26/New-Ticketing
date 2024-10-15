
frappe.ui.form.on('Quotation', {
	refresh: function(frm) {
		console.log("custom quotation refresh")
		frm.add_custom_button("From Template", () => {
			const dia = new frappe.ui.form.MultiSelectDialog({
				doctype: "Quotation Template",
				target: this.cur_frm,
				setters: {
				},
				add_filters_group: 1,
				// date_field: "transaction_date",
				// get_query() {
				// 	return {
				// 		filters: { docstatus: ['!=', 2] }
				// 	}
				// },
				action(selections) {
					console.log(selections);
					frappe.call({
						method: "ticketing.api.get_quotation_items",
						args: {
							names: selections,
						},
						freeze: true,
						freeze_message: "Fetching Items For Quotation",
						callback: (res) => {
							console.log("res", res)
						}
					})
				}
			});
		}, "Get Items From")
	}
});
