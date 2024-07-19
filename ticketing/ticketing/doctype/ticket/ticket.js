// Copyright (c) 2024, Dexciss and contributors
// For license information, please see license.txt

frappe.ui.form.on("Ticket", {
	refresh(frm) {
        createButton(frm)
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