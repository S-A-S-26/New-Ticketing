// Copyright (c) 2024, Dexciss and contributors
// For license information, please see license.txt

frappe.ui.form.on('Service Request', {
	refresh: function(frm) {
		frappe.provide("erpnext.utils");
		if (!frm.doc.display_address){
			frm.trigger("customer_address")
		}
		if (frm.doc.service){
			validateServiceInvoiceBtn(frm)
		}
		frm.trigger('is_visit_required')
		if (frm.doc.billed_duration >= 0.001){
			add_create_invoice(frm)
		}
		addLogTime(frm)

	},

	is_visit_required:function(frm){
		if(frm.doc.is_visit_required){
            frm.add_custom_button("Visit Request",function(){
				frappe.call({
					method:"create_visit_request",
					doc:frm.doc,
					freeze:true,
					freeze_message:"Creating Visit Request",
					callback: function(r, rt){
						console.log("r.message=",r);
						
						if(r.message){
							frappe.msgprint("Visit Request Created Successfully")
						}else{
							frappe.msgprint("Visit Request Failed")
						}
					}
				})
			},"Create")
        }else{
            frm.remove_custom_button("Visit Request","Create"); 
        }
	},

	type:function(frm){
		addLogTime(frm)
	},

	ticket:function(frm){
		checkPayPerHour(frm)
		if (frm.doc.customer_address){
			frm.trigger("customer_address")
		}
	},

	status:function(frm){
		// frappe.call({
		// 	method:"ticketing.api.set_status",
		// 	args:{
		// 		status:frm.doc.status,
		// 		doctype:frm.doctype,
        //         name:frm.doc.name,
        //         target_doc:"Ticket",
		// 		target_doc_name:frm.doc.ticket
		// 	},
        //     freeze:true,
        //     freeze_message:"Updating status",
		// })
	},
	customer_address:function(frm){
		erpnext.utils.get_address_display(frm, "customer_address","display_address");
	}
});

function validateServiceInvoiceBtn(frm){
	frappe.call({
		method:"check_if_service_is_paid",
		doc:frm.doc,
		freeze:true,
		freeze_message:"Checking service info",
		callback: function(r, rt){
			console.log("r.message=",r);
			
			if(r.message ){
				
				if (frm.doc.type == "Hourly Service Request" && frm.doc.billed_duration < 0.01) {
					console.log("hourly service and duration less than zero");
					return
				}
				if (frm.doc.pay_by_hour == 0){
					console.log("is paid service validation add service")
					add_create_invoice(frm)
				}
			}else{
				console.log("is not paid service validation remove service")
				frm.remove_custom_button("Service Ticket Invoice","Create");
			}
		}
	})
}

function addLogTime(frm){
	let pph=checkPayPerHour(frm)
	console.log("checkPayPerHour",pph)
	if(frm.doc.type == "Hourly Service Request" || pph){
		frm.add_custom_button(__("Log Time"), function (){
			if (frm.doc.recent_log== undefined) {
				frm.doc.recent_log= frappe.datetime.now_datetime()
			}else{
				console.log(typeof frm.doc.recent_log,frm.doc.recent_log,)
				const datetimeString = frm.doc.recent_log;

				// Convert the static datetime string to a Date object
				const staticDatetime = new Date(datetimeString.replace(" ", "T"));

				// Get the current datetime
				// const now = new Date();
				const now = frappe.datetime.str_to_obj(frappe.datetime.now_datetime())

				// Calculate the difference in milliseconds
				const differenceInMillis = now - staticDatetime;
				console.log(differenceInMillis)
				let final_duration = Math.floor(differenceInMillis / 1000);
				if (frm.doc.duration){
					console.log("duration",frm.doc.duration)
					final_duration=frm.doc.duration+final_duration
				}
				frm.doc.duration=final_duration
				frm.doc.billed_duration=(final_duration/3600).toFixed(2)
				frm.doc.recent_log=frappe.datetime.now_datetime()
			}
			frm.refresh_field("recent_log")
			frm.refresh_field("duration")
			frm.refresh_field("billed_duration")
			if (frm.doc.billed_duration >= 0.001){
				add_create_invoice(frm)
			}
			frm.dirty()
			frm.save()
		},"Time")
		frm.add_custom_button(__("Reset Time"), function (){
			frm.doc.duration=undefined
			frm.doc.recent_log= undefined
			frm.doc.billed_duration=undefined
			frm.refresh_field("recent_log")
			frm.refresh_field("duration")
			frm.dirty()
			frm.save()
		},"Time")
	}else{
		frm.remove_custom_button("Log Time","Time")
		frm.remove_custom_button("Reset Time","Time")
	}
	
}

function checkPayPerHour(frm){
	let data=false
	frappe.call({
		method: "check_per_hour",
		doc: frm.doc,
        freeze: true,
        freeze_message: "Checking service info",
		async:false,
        callback: function(r, rt) {
            console.log("r.checkPayPerHour=", r);
            if (r.message) {
                data= true
				frm.doc.pay_by_hour=1
				frm.refresh_field("pay_by_hour")
				if ((frm.doc.billed_duration < 0.001)){
					console.log("remove form pay per hour check")
					frm.remove_custom_button("Service Ticket Invoice","Create");
				}
            } else {
				data= false
				frm.doc.pay_by_hour=0
				frm.refresh_field("pay_by_hour")
            }
        }
	})
	
	return data
}

function add_create_invoice(frm){
	console.log("add_create_invoice-0-0",frm.doc.billed_duration)
	frm.add_custom_button(__("Service Ticket Invoice"), function() {
		frappe.call({
			method:"create_sales_invoice_ticket",
			doc:frm.doc,
			freeze:true,
			freeze_message:"Create Service Ticket Invoice",
			callback: function(r, rt){
				console.log("r.message=",r);
				
				if(r.message ){
					frappe.msgprint("Service Ticket Invoice Created Successfully")
				}else{
					frappe.msgprint("Service Ticket Invoice Creation Failed")
				}
			}
		})
	}, "Create");
		
}