// Copyright (c) 2024, Dexciss and contributors
// For license information, please see license.txt

frappe.ui.form.on('Service Request', {
	refresh: function(frm) {

	},

	is_visit_required:function(frm){
		if(frm.doc.is_visit_required){
            frm.add_custom_button("Create Visit Request",function(){
				frappe.call({
					method:"create_visit_request",
					doc:frm.doc,
					freeze:true,
					freeze_message:"Creating Visit Request",
					callback: function(r, rt){
						console.log("r.message=",r);
						
						if(r.message){
		
						}else{
		
						}
					}
				})
			},"Create")
        }else{
            frm.remove_custom_button("Create Visit Request","Create"); 
        }
	}
});
