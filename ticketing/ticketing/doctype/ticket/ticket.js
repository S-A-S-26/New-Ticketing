// Copyright (c) 2024, Dexciss and contributors
// For license information, please see license.txt

frappe.ui.form.on("Ticket", {
	refresh(frm) {
        createButton(frm)
        show_notes(frm)
	},
    after_save:function(frm){
        createButton(frm)
    },
    service_requested:function(frm){
        frappe.call({
            method:"get_contract",
            doc:frm.doc,
            freeze:true,
            freeze_message:"Fetching contract",
            callback: function(r, rt){
                console.log("r.message=",r);
                
                if(r.message){
                    frm.set_value("contract", r.message.name);
                    if (['In Progress', 'Expiring'].includes(r.message.status)){
                        frm.set_value("contract_status", "Active");
                    }else{
                        frm.set_value("contract_status", "Inactive");
                    }
                }else{
                    // frappe.msgprint("No contract found for this ticket.");
                    frm.set_value("contract", null);
                    frm.doc.contract_status="Not Found";
                    frm.refresh_field('contract_status')
                }
                createButton(frm)
            }
        })
    },


});


function createButton(frm, status=undefined) {
    if (frm.doc.__islocal) {
        return
    }
    console.log("createButton", status)
    if (frm.doc.contract){
        frappe.db.get_value('Customer Contract', frm.doc.contract,'status')
        .then(val => {
            console.log('doc',val)
            if(['Expired'].includes(val.message.status) || frm.doc.type=="Project" || frm.doc.contract_status=="Inactive"){
                console.log("inside if createButton")
                add_opportunity_btn(frm)
            }else{
                frm.remove_custom_button("Opportunity","Create");
            }
        })
    }else{
        
        add_opportunity_btn(frm)     
       
    }

   if(frm.doc.type=="Service Request" && frm.doc.contract){
        frm.add_custom_button(__("Service Request"), function() {
            frappe.call({
                method:"create_service_req",
                doc:frm.doc,
                freeze:true,
                freeze_message:"Creating service request",
                callback: function(r, rt){
                    console.log("r.message=",r);
                    
                    if(r.message){
                        frappe.msgprint(r.message+" created successfully.");
                        frm.refresh_fields("service_request")
                    }else{
                        frappe.msgprint("Service request creation failed.");
                    }
                }
            })
        }, "Create");
    }else{
        frm.remove_custom_button("Service Request","Create"); 
    }

    frappe.call({
        method:"validate_before_ticketInv",
        doc:frm.doc,
        freeze:true,
        freeze_message:"Validating before ticket invoice",
        callback: function(r, rt){
            console.log("validate before ticket",r);
            if (r.message){
                frm.add_custom_button(__("Pay Per Ticket Invoice"), function() {
                    frappe.call({
                        method:"create_ticket_invoice",
                        doc:frm.doc,
                        freeze:true,
                        freeze_message:"Creating Ticket Invoice",
                        callback: function(r, rt){
                            console.log("r.message=",r);
                            
                            if(r.message){
                                frappe.msgprint("Ticket Invoice created successfully.");
                            }else{
                                frappe.msgprint("Failed to Ticket Invoice.");
                            }
                        }
                    })
            
                }, "Create");
            }else{
                frm.remove_custom_button("Pay Per Ticket Invoice","Create");
            }
        }
    })
    

    // frm.add_custom_button(__("Service Ticket Invoice"), function() {
        
    // }, "Create");

    // frm.add_custom_button(__("Warranty Invoice"), function() {
        
    // }, "Create");

    // if(frm.doc.type=="Project" || frm.doc.contract_status=="Inactive"){
    //     frm.add_custom_button(__("Opportunity"), function() {
            
    //     }, "Create");
    // }else{
    //     frm.remove_custom_button("Opportunity","Create"); 
    // }

}


function add_opportunity_btn(frm){
    console.log("add_opportun")
    frm.add_custom_button(__("Opportunity"), function() {
        console.log("opportunity")
        frappe.call({
            method:"create_opp",
            doc:frm.doc,
            freeze:true,
            freeze_message:"Creating opportunity",
            callback: function(r, rt){
                console.log("r.message=",r);
                
                if(r.message){
                    frappe.msgprint("Opportunity created successfully.");
                    // frm.refresh_fields("service_request")
                }else{
                    frappe.msgprint("Opportunity creation failed.");
                }
            }
        })
    }, "Create");
}

function show_notes(frm) {
    const crm_notes = new erpnext.utils.CRMNotes({
        frm: frm,
        notes_wrapper: $(frm.fields_dict.notes_html.wrapper),
    });
    crm_notes.refresh();

    frm.dirty();
}

// erpnext.crm.Opportunity = class Ticket extends frappe.ui.form.Controller {
// 	onload() {
// 		if (!this.frm.doc.status) {
// 			this.frm.set_value("status", "Open");
// 		}
// 		if (!this.frm.doc.company && frappe.defaults.get_user_default("Company")) {
// 			this.frm.set_value("company", frappe.defaults.get_user_default("Company"));
// 		}
// 		if (!this.frm.doc.currency) {
// 			this.frm.set_value("currency", frappe.defaults.get_user_default("Currency"));
// 		}

// 		this.setup_queries();
// 		this.frm.trigger("currency");
// 	}

// 	refresh() {
// 		this.show_notes();
// 		this.show_activities();
// 	}

// 	setup_queries() {
// 		var me = this;

// 		me.frm.set_query("customer_address", erpnext.queries.address_query);

// 		this.frm.set_query("item_code", "items", function () {
// 			return {
// 				query: "erpnext.controllers.queries.item_query",
// 				filters: { is_sales_item: 1 },
// 			};
// 		});

// 		me.frm.set_query("contact_person", erpnext.queries["contact_query"]);

// 		if (me.frm.doc.opportunity_from == "Lead") {
// 			me.frm.set_query("party_name", erpnext.queries["lead"]);
// 		} else if (me.frm.doc.opportunity_from == "Customer") {
// 			me.frm.set_query("party_name", erpnext.queries["customer"]);
// 		} else if (me.frm.doc.opportunity_from == "Prospect") {
// 			me.frm.set_query("party_name", function () {
// 				return {
// 					filters: {
// 						company: me.frm.doc.company,
// 					},
// 				};
// 			});
// 		}
// 	}

// 	create_quotation() {
// 		frappe.model.open_mapped_doc({
// 			method: "erpnext.crm.doctype.opportunity.opportunity.make_quotation",
// 			frm: cur_frm,
// 		});
// 	}

// 	make_customer() {
// 		frappe.model.open_mapped_doc({
// 			method: "erpnext.crm.doctype.opportunity.opportunity.make_customer",
// 			frm: cur_frm,
// 		});
// 	}

// 	show_notes() {
// 		const crm_notes = new erpnext.utils.CRMNotes({
// 			frm: this.frm,
// 			notes_wrapper: $(this.frm.fields_dict.notes_html.wrapper),
// 		});
// 		crm_notes.refresh();
// 	}

// 	show_activities() {
// 		const crm_activities = new erpnext.utils.CRMActivities({
// 			frm: this.frm,
// 			open_activities_wrapper: $(this.frm.fields_dict.open_activities_html.wrapper),
// 			all_activities_wrapper: $(this.frm.fields_dict.all_activities_html.wrapper),
// 			form_wrapper: $(this.frm.wrapper),
// 		});
// 		crm_activities.refresh();
// 	}
// };

// extend_cscript(cur_frm.cscript, new erpnext.crm.Opportunity({ frm: cur_frm }));