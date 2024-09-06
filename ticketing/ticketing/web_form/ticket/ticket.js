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
        onPageLoad()
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
        onPageLoad()
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
        fetchItems()
        clearAll()
	});

    frappe.web_form.on('customer', () =>{
        frappe.web_form.set_value('customer_address',undefined)
        fetchCustomerAddress()
	});

    // frappe.web_form.on('rating_motn', async () =>{
	// 	frappe.call({
    //         method: 'ticketing.ticket_wform_api.get_feedback_options',
    //         args: {
    //             rating: frappe.web_form.get_value('rating_motn')
    //         },
    //         callback: function(r) {
    //             console.log("res rating opt",r)
    //             if (r.message){
    //                 frappe.web_form.fields_dict.feedback_option.set_data(r.message)
    //             }else{
    //                 frappe.web_form.fields_dict.feedback_option.set_data([])
    //             }
    //         }
    //     })
	// });

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
                if (r.message){
                    frappe.web_form.fields_dict.customer_address.set_data(r.message)
                }else{
                    frappe.web_form.fields_dict.customer_address.set_data([])
                }
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
                
                if(r.message){
                    frappe.web_form.fields_dict.customer.set_data(r.message)
                }
            }
        })
    }
    fetchCustomer()

    function onPageLoad(){
        frappe.web_form.fields_dict.customer_address.set_data([])
        const service_requested =frappe.web_form.get_value('service_requested')
        const equipment =frappe.web_form.get_value('equipment')
        if (!service_requested){
            frappe.web_form.set_df_property('contract_status', 'hidden',true);
            frappe.web_form.set_df_property('contract', 'hidden',true);
            frappe.web_form.set_df_property('item_name', 'hidden',true);
        }else{
            frappe.web_form.set_df_property('contract_status', 'hidden',false);
            frappe.web_form.set_df_property('contract', 'hidden',false);
            frappe.web_form.set_df_property('item_name', 'hidden',false);
        }

        if (!equipment){
            frappe.web_form.set_df_property('warranty', 'hidden',true);
            frappe.web_form.set_df_property('warranty_status', 'hidden',true);
            frappe.web_form.set_df_property('equipment_name', 'hidden',true);
        }else{
            frappe.web_form.set_df_property('warranty', 'hidden',false);
            frappe.web_form.set_df_property('warranty_status', 'hidden',false);
            frappe.web_form.set_df_property('equipment_name', 'hidden',false);
        }
    }
    onPageLoad()

    function fetchItems(){
        let tType = frappe.web_form.get_value('ticket_type')
        let stock = 0
        let target= ['service_requested']
        if (tType == "Service Request"){
            stock = 0
            target = 'service_requested'
        }else{
            stock = 1
            target = 'equipment'
        }

        frappe.call({
            method: 'ticketing.ticket_wform_api.get_items_filtered',
            args: {
                mstock: stock
            },
            callback: function(r) {
                console.log("res f items",r)
                frappe.web_form.fields_dict[target].set_data(r.message)
            }
        })
    }

    function addButtonFeedback() {
        let button = $('<button class="btn btn-primary btn-xs">Close</button>');
        button.css({
            float: 'right',
            marginLeft: 'auto'
        });
        $('div.breadcrumb-container').css({
            display: 'flex',
            alignItems: 'center', // vertically center the items
            justifyContent:'space-between',
        });
        button.click(function() {
            // add your button code here
            console.log("hello there")
            let d = new frappe.ui.Dialog({
                title: 'Enter details',
                fields: [
                    {
                        
                        label: "Rating",
                        fieldname: "dia_rating",
                        fieldtype: "Rating",
                        reqd: 1,
                        change() { // Add a change listener to the rating field
                            frappe.call({
                                method: 'ticketing.ticket_wform_api.get_feedback_options',
                                args: {
                                    rating: d.get_value('dia_rating')
                                },
                                async: false,
                                callback: function(r) {
                                    console.log("res rating opt",r)
                                    if (r.message){
                                        d.set_df_property('dia_feedback_option', 'options', []);
                                        d.set_df_property('dia_feedback_option', 'options', r.message);
                                        // frappe.web_form.fields_dict.feedback_option.set_data(r.message)
                                    }else{
                                        d.set_df_property('dia_feedback_option', 'options', []);
                                    }
                                }
                            })
                             // Dynamically update the options
                        }
                    },
                    {
                        allow_read_on_all_link_options: 0,
                        fieldname: "feedback_text",
                        fieldtype: "Data",
                        hidden: 0,
                        label: "Feedback (Text)",
                        max_length: 0,
                        max_value: 0,
                        precision: "",
                        read_only: 0,
                        reqd: 0,
                        show_in_filter: 0
                    },
                    {
                        fieldname: "dia_feedback_option",
                        fieldtype: "Select",
                        label: "Feedback (Option)",
                        options:[],
                        reqd: 1,
                    },
                    {
                        "allow_read_on_all_link_options": 0,
                        "fieldname": "feedback_extra",
                        "fieldtype": "Small Text",
                        "hidden": 0,
                        "label": "Feedback (Extra)",
                        "max_length": 0,
                        "max_value": 0,
                        "precision": "",
                        "read_only": 0,
                        "reqd": 0,
                        "show_in_filter": 0
                    },
                    {
                        "fieldname": "resolution_details",
                        "fieldtype": "Text Editor",
                        "label": "Resolution Details",
                        "reqd": 1,
                    },
                    // {
                    //     label: 'First Name',
                    //     fieldname: 'first_name',
                    //     fieldtype: 'Data'
                    // },
                    // {
                    //     label: 'Last Name',
                    //     fieldname: 'last_name',
                    //     fieldtype: 'Data'
                    // },
                    // {
                    //     label: 'Age',
                    //     fieldname: 'age',
                    //     fieldtype: 'Int'
                    // }
                ],
                size: 'large', // small, large, extra-large 
                primary_action_label: 'Submit',
                primary_action(values) {
                    console.log(values);
                    console.log("values.",values.dia_rating)
                    frappe.call({
                        method: 'ticketing.ticket_wform_api.update_ticket_feedback',
                        args: {
                            ticket: frappe.web_form.doc.name,
                            rating: values.dia_rating,
                            option:values.dia_feedback_option,
                            resolution:values.resolution_details,
                            text:values.feedback_text,
                            extra:values.feedback_extra,
                        },
                        callback: function(r) {
                            console.log("res on closing",r)
                            if (r.message){
                                frappe.msgprint(r.message)
                                d.hide();
                                // frappe.web_form.fields_dict.feedback_option.set_data(r.message)
                            }else{
                                frappe.msgprint("Error: Failed to submit feedback.")
                            }
                        },
                        // error: (r) => {
                        //     // on error
                        //     frappe.throw("Error: " + r.message)
                        // }
                    })
                    
                    
                }
            });
            // d.$body.ready(()=>{
            //     console.log("warpper ready")
            //     let content=$('.form-layout')
            //     // let content=$('div.modal-body').find('span.tooltip-content');
            //     console.log("content",content)
            // })
            console.log("d.wrapper",d.$body)
            d.show();
        });
        console.log("status",frappe.web_form.get_value('status'))
        if (frappe.web_form_doc.in_view_mode && !(['Closed', 'Resolved'].includes(frappe.web_form.get_value('status')))) {
            $('div.breadcrumb-container').append(button);
        }
    }
    addButtonFeedback()

})

