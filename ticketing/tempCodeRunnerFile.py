def validate_resolution(self):
    print("\n\nValidating",self.resolution_details,self.resolution_details == '<div class="ql-editor read-mode"><p><br></p></div>')
    if (self.status=="Resolved" or self.status=="Closed" or self.status=="Completed") and (self.resolution_details == None or self.resolution_details == "" or self.resolution_details == '<div class="ql-editor read-mode"><p><br></p></div>'):
            frappe.throw("Please fill out resolution details for status Resolved and Closed or Completed")