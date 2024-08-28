frappe.ready(function() {
	// bind events here
	frappe.web_form.on('customer_address', async () =>{
		frappe.call({
			method: 'frappe.contacts.doctype.address.address.get_address_display',
            args: {
                address_dict: frappe.web_form.get_value('customer_address')
            },
            callback: function(r) {
                frappe.web_form.set_value('customer_address_display', r.message);
            }
		})
	});
})