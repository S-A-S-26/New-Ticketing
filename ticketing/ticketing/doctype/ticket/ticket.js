// Copyright (c) 2024, Dexciss and contributors
// For license information, please see license.txt

frappe.ui.form.on("Ticket", {
	refresh(frm) {
        frappe.provide("erpnext.utils");
        createButton(frm)
        show_notes(frm)
        console.log("refresh")
        createPurchaseWarranty(frm)
        // if (frm.doc.equipment && frm.doc.type == "Equipment Issue"){
        //     console.log("purchase equipment")
        //     frm.trigger("equipment")
        // }
        
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
    equipment:function(frm){
        frm.doc.purchase_warranty=0
        frm.refresh_field('purchase_warranty')
        frappe.call({
            method:"check_warranty",
            doc:frm.doc,
            freeze:true,
            freeze_message:"Checking Warranty",
            callback: function(r, rt){
                console.log("r.message=",r);
                frm.refresh_field("warranty")
                frm.refresh_field("warranty_status")
                createButton(frm)
                if(r.message){

                }else{

                }

            }
        })
    },
    ticket_type:function(frm){
        frm.doc.contract=undefined
        frm.doc.contract_status=undefined
        frm.doc.service_requested=undefined
        frm.doc.item_name=undefined
        frm.doc.equipment=undefined
        frm.doc.equipment_name=undefined
        frm.doc.warranty=undefined
        frm.doc.warranty_status=undefined

        frm.refresh_fields(['contract','status','service_requested','item_name','equipment','equipment_name','warranty','warranty_status'])
    },
    purchase_warranty:function(frm){
        createPurchaseWarranty(frm)
    },
    customer_address:function(frm){
        console.log("customer_address")
        erpnext.utils.get_address_display(frm, "customer_address","customer_address_display");
        frm.refresh_field("address_html")
        // frappe.call({
        //     method:"frappe.contacts.doctype.address.address.get_address_display",
        //     args: {address_dict:frm.doc.customer_address},
        //     freeze:true,
        //     freeze_message:"Fetching customer address",
        //     callback: function(r, rt){
        //         console.log("r.message=",r);
        //         frm.set_value("address_html", r.message);
        //         frm.refresh_field("address_html")
        //     }
        // })
    },
    customer:function(frm){
        frm.doc.customer_address=undefined;
        frm.refresh_field("customer_address")
    }


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
    }else if (!frm.doc.contract && frm.doc.service_requested){
        
        add_opportunity_btn(frm)     
       
    }

   if(frm.doc.type=="Service Request" && frm.doc.contract && frm.doc.contract_status=="Active"){
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
                        frm.remove_custom_button("Service Request","Create"); 
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
    
    if (frm.doc.type == "Equipment Issue" && (frm.doc.warranty_status == "No Warranty" || frm.doc.warranty_status == "Expired")) {
        // frm.add_custom_button(__("Create Sales Invoice"), function() {
            
        // }, "Create");
        frm.remove_custom_button("Create Repair Request","Create");
    }else if (frm.doc.type == "Equipment Issue" && frm.doc.warranty_status == "Under Warranty") {
        frm.add_custom_button(__("Create Repair Request"), function() {
            frappe.call({
                method:"create_repair_request",
                doc:frm.doc,
                freeze:true,
                freeze_message:"Creating Repair Request",
                callback: function(r, rt){
                    console.log("r.message=",r);
                    
                    if(r.message){
                        frappe.msgprint("Repair Request created successfully.");
                    }else{
                        frappe.msgprint("Failed to Repair Request.");
                    }
                }
            })
        }, "Create");
        frm.remove_custom_button("Create Sales Invoice","Create");
    }else{
        frm.remove_custom_button("Create Sales Invoice","Create");
        frm.remove_custom_button("Create Repair Request","Create");
    }


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

    // frm.dirty();
}

function createPurchaseWarranty(frm) {
    console.log("createPurchaseWarranty",frm.doc.purchase_warranty)
    if (frm.doc.purchase_warranty){
        frm.add_custom_button('Purchase Warranty',function(){
            frappe.call({
                method:"purchase_warranty_invoice",
                doc:frm.doc,
                freeze:true,
                freeze_message:"Purchasing Warranty",
                callback: function(r, rt){
                    console.log("r.message=",r);
                    if (r.message){
                        frappe.msgprint("Warranty Purchased successfully.");
                        // setTimeout(() => {
                        //     frm.refresh();
                        // }, 1000);
                    }else{
                        frappe.msgprint("Failed to purchase warranty.");
                    }

                }
            })
        },"Create")
    }else{
        frm.remove_custom_button('Purchase Warranty','Create');
    }
}

