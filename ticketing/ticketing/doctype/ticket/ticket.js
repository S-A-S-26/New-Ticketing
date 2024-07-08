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
                    frappe.msgprint("No contract found for this ticket.");
                    frm.set_value("contract", null);
                    createButton(frm)
                }
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
            if(['Expired'].includes(val.message.status)){
                console.log("inside if createButton")
                frm.add_custom_button(__("Create Opportunity"), function() {
                    
                }, "Create");
            }else{
                frm.remove_custom_button("Create","Create Opportunity");
            }
        })
    }else{
        frm.add_custom_button(__("Create Opportunity"), function() {
                    
        }, "Create");
    }

   
    frm.add_custom_button(__("Create Service"), function() {
        
    }, "Create");
    frm.add_custom_button(__("Create Ticket Invoice"), function() {
        
    }, "Create");
    frm.add_custom_button(__("Create Service Ticket Invoice"), function() {
        
    }, "Create");
    
}