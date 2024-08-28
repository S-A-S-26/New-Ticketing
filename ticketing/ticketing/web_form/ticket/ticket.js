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
        clearAll()
	});

    frappe.web_form.on('equipment', async () =>{
        console.log("equipment",frappe.web_form.get_value('equipment'))
        if (!frappe.web_form.get_value('equipment')){
            console.log("no equipment request data")
            return 
        }
		frappe.call({
			method: 'ticketing.ticket_wform_api.check_warranty',
            args: {
                equipment: frappe.web_form.get_value('equipment'),
                customer: frappe.web_form.get_value('customer'),
                customer_address: frappe.web_form.get_value('customer_address')
            },
            callback: function(r) {
                console.log("res equipent",r)
                frappe.web_form.set_value('warranty', r.message.warranty);
                frappe.web_form.set_value('warranty_status', r.message.warranty_status);
                frappe.web_form.set_df_property('warranty', 'read_only',true);
                if (r.message.warranty_status == 'No Warranty'){
                    frappe.web_form.set_df_property('warranty', 'hidden',true);
                }else{
                    frappe.web_form.set_df_property('warranty', 'hidden',false);
                }
            }
		})
	});

    frappe.web_form.on('service_requested', async () =>{
        console.log("service requested",frappe.web_form.get_value('service_requested'))
        if (!frappe.web_form.get_value('service_requested')){
            console.log("no service request data")
            return 
        }
		frappe.call({
			method: 'ticketing.ticket_wform_api.get_contract',
            args: {
                service_requested: frappe.web_form.get_value('service_requested'),
                customer: frappe.web_form.get_value('customer'),
                customer_address: frappe.web_form.get_value('customer_address')
            },
            callback: function(r) {
                console.log("res equipent",r)
                if (!r.message){
                    frappe.web_form.set_value('contract_status', 'Not Found');
                    frappe.web_form.set_value('contract', undefined);
                    frappe.web_form.set_df_property('contract', 'hidden',true);
                    
                }
                else if (['In Progress', 'Expiring'].includes(r.message.status)){
                    frappe.web_form.set_value('contract', r.message.name);
                    frappe.web_form.set_value('contract_status', 'Active');
                    frappe.web_form.set_df_property('contract', 'hidden',false);
                    frappe.web_form.set_df_property('contract', 'read_only',true);
                }else{
                    frappe.web_form.set_value('contract_status', 'Not Found');
                    frappe.web_form.set_value('contract', undefined);
                }
                // if (!r.message){
                //     frappe.web_form.set_value('warranty_status', 'Not Found');
                //     frappe.web_form.set_value('contract', undefined);
                // }else{
                    
                //     frappe.web_form.set_value('contract', r.message.name);
                //     frappe.web_form.set_value('contract_status', r.message.status);
                // }
            }
		})
	});

    frappe.web_form.on('ticket_type', async () =>{
        clearAll()
	});

    frappe.web_form.on('customer', () =>{
        fetchCustomerAddress()
	});

    function clearAll(){
        frappe.web_form.set_value('warranty', undefined);
        frappe.web_form.set_value('warranty_status', undefined);
        frappe.web_form.set_value('service_requested', undefined);
        frappe.web_form.set_value('contract_status',undefined);
        frappe.web_form.set_value('contract', undefined);
        frappe.web_form.set_value('equipment', undefined);   
    }

    console.log("onload script")
    function fetchCustomerAddress(){
        frappe.call({
            method: 'ticketing.ticket_wform_api.get_customer_address',
            args: {
                customer: frappe.web_form.get_value('customer')
            },
            callback: function(r) {
                console.log("res address",r)
                frappe.web_form.fields_dict.customer_address.set_data(r.message)
            }
        })
    }

    function fetchCustomer(){
        frappe.call({
            method: 'ticketing.ticket_wform_api.get_customer',
            args: {
                user: frappe.session.user
            },
            callback: function(r) {
                console.log("res address",r)
                frappe.web_form.fields_dict.customer.set_data(r.message)
            }
        })
    }
    fetchCustomer()
})

