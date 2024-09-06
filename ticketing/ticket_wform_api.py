import frappe

@frappe.whitelist()
def check_warranty(equipment,customer,customer_address):
    print("check warranty")
    print(f"""select we.status ,w.name from `tabWarranty` as w join `tabWarranty Address` as wa on w.name=wa.parent join `tabWarranty Equipments` as we on w.name=we.parent where we.equipment="{equipment}" and w.customer="{customer}" and wa.warranty_address="{customer_address}" order by w.creation desc;""")
    data=frappe.db.sql(f"""select we.status ,w.name from `tabWarranty` as w join `tabWarranty Address` as wa on w.name=wa.parent join `tabWarranty Equipments` as we on w.name=we.parent where we.equipment="{equipment}" and w.customer="{customer}" and wa.warranty_address="{customer_address}" order by w.creation desc;""",as_dict=True)
    print("data",data)
    return_data={}
    if data:
        data=data[0]
        if data.get('status') == 'Active' or data.get('status') == 'Expiring':
            return_data['warranty_status'] = "Under Warranty"
        elif data.get('status') == 'Expired':
            return_data['warranty_status'] = "Expired"
        else:
            return_data['warranty_status'] = "No Warranty"
        return_data['warranty']=data.get('name')
    else:
        return_data['warranty_status'] = "No Warranty"
        return_data['warranty'] = None
    print("return data",return_data)
    return return_data


@frappe.whitelist()
def get_contract(service_requested,customer,customer_address):
    print("get_contract---"+f"""select cc.name,cc.status from `tabCustomer Contract` as cc join `tabContract Address Items` as addr on cc.name = addr.parent join `tabContract Covered Services` as sc on cc.name= sc.parent where addr.customer_address ='{customer_address}' and sc.service='{service_requested}' ORDER BY cc.creation DESC LIMIT 1;""")
    data=frappe.db.sql(f"""select cc.name,cc.status from `tabCustomer Contract` as cc join `tabContract Address Items` as addr on cc.name = addr.parent join `tabContract Covered Services` as sc on cc.name= sc.parent where addr.customer_address ='{customer_address}' and sc.service='{service_requested}' and cc.customer='{customer}' ORDER BY cc.creation DESC LIMIT 1;""",as_dict=True)
    print("data sql",data)
    if data:
        return data[0]
    else:
        return False
    
@frappe.whitelist()
def get_customer_address(customer):
    
    data=frappe.db.get_all("Address",[["link_name","=",customer]],pluck='name')
    print("data sql",data)
    if data:
        return data
    else:
        return []
    
@frappe.whitelist()
def get_customer(user):
    
    data=frappe.db.get_all("Customer",[["user","=",user]],pluck='name')
    print("data sql",data)
    if data:
        return data
    else:
        return []

@frappe.whitelist()
def get_items_filtered(mstock=0):
    
    data=frappe.db.get_all("Item",[["is_stock_item","=",mstock]],pluck='name')
    print("data sql",data)
    if data:
        return data
    else:
        return []
    
@frappe.whitelist()
def get_feedback_options(rating):
    data=frappe.db.get_all("Ticket Feedback Options",[["rating","=",rating]],pluck='name')
    print("data sql",data)
    if data:
        return data
    else:
        return []
    
@frappe.whitelist(allow_guest=True)
def update_ticket_feedback(ticket,rating,option,resolution=None,text=None,extra=None):
    print("update ticket_feedback",ticket)

    doc=frappe.get_doc("Ticket",ticket)
    doc.status="Closed"
    doc.rating_motn=rating
    doc.feedback_text=text
    doc.feedback_option=option
    doc.feedback_extra=extra
    doc.resolution_details=resolution

    doc.save()
    return "Ticket Closed Successfully"
