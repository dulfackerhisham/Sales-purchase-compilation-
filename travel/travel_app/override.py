import frappe

def purchase_invoice(doc, method='None'):
    if doc.docstatus == 1:  # Create Purchase Invoice only if Sales Invoice is submitted
        # Create a new Purchase Invoice
        purchase_invoice = frappe.new_doc('Purchase Invoice')
        
        # Set the supplier based on the Sales Invoice custom field
        purchase_invoice.supplier = doc.custom_supplier
        
        # Loop through Sales Invoice items
        for item in doc.items:
            # Get the item rate from 'Item Price' for buying
            item_rate = frappe.db.get_list('Item Price', 
                filters={
                    'item_code': item.item_code,  # Use item code from Sales Invoice item
                    'price_list': 'Buying'        # Filter for 'Buying' price list
                },
                fields=['price_list_rate'],      # Get the 'price_list_rate' field
                limit=1                          # Get the first matching rate
            )
            
            # Check if a rate was found, default to 0 if not
            rate = item_rate[0].get('price_list_rate') if item_rate else 0
            
            # Append the item to Purchase Invoice
            purchase_invoice.append("items", {
                "item_code": item.item_code,
                "qty": item.qty,
                "rate": rate,                   # Use the fetched rate
                "amount": rate * item.qty        # Calculate amount based on rate and qty
            })
        
        # Insert the Purchase Invoice into the database
        purchase_invoice.insert()
        
        # Store the Purchase Invoice reference in the Sales Invoice
        doc.db_set('custom_purchase_invoice_', purchase_invoice.name)
        
        # Optional: Submit the Purchase Invoice if required
        purchase_invoice.submit()
    
    
        # Check if a linked Purchase Invoice exists
        


def after_cancel(doc,method="None"):
    if doc.custom_purchase_invoice_:
           
            try:
                purchase_invoice_doc = frappe.get_doc("Purchase Invoice", doc.custom_purchase_invoice_)
                if purchase_invoice_doc.docstatus == 1:
                    
                    purchase_invoice_doc.cancel()
                    frappe.msgprint(f"Linked Purchase Invoice {purchase_invoice_doc.name} has been canceled.")
            except frappe.DoesNotExistError:
                frappe.msgprint("Purchase Invoice not found.")
