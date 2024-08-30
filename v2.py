import pandas as pd
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentField
import streamlit as st

# Configura el cliente de Form Recognizer
endpoint = "https://tableroadmi.cognitiveservices.azure.com/"
api_key = "0dbdead460874631bfef3f95699f96c7"
client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(api_key))

def analyze_invoices(files):
    data = []
    for file in files:
        file_bytes = file.read()
        poller = client.begin_analyze_document("prebuilt-invoice", document=file_bytes)
        result = poller.result()

        for document in result.documents:
            custom_name = document.fields.get("CustomName", None)
            vendor_name = document.fields.get("VendorName", None) 
            invoice_id = document.fields.get("InvoiceId", None)
            invoice_date = document.fields.get("InvoiceDate", None)
            invoice_amount = document.fields.get("InvoiceAmount", None)
            
            
            custom_name_value = custom_name.value if custom_name else ""
            vendor_name_value = vendor_name.value if vendor_name else ""
            invoice_id_value = invoice_id.value if invoice_id else ""
            invoice_date_value = invoice_date.value if invoice_date else ""
            invoice_amount_value = invoice_amount.value if invoice_amount else ""

            items_field = document.fields.get("Items", None)
            items = items_field.value if isinstance(items_field, DocumentField) else items_field
            if not isinstance(items, list):
                items = [items] if items else []

            for item in items:
                description = item.value.get("Description", None) if item.value else None
                quantity = item.value.get("Quantity", None) if item.value else None
                unit_price = item.value.get("UnitPrice", None) if item.value else None
                total_price = item.value.get("TotalPrice", None) if item.value else None

                item_data = {
                    "Custom_name": custom_name,
                    "Vendor Name": vendor_name_value,
                    "Invoice ID": invoice_id_value,
                    "Invoice Date": invoice_date_value,
                    "Invoice Amount": invoice_amount_value,
                    "Item Description": description.value if description else "",
                    "Quantity": quantity.value if quantity else "",
                    "Unit Price": unit_price.value if unit_price else "",
                    "Total Price": total_price.value if total_price else "",
                }
                data.append(item_data)

    # Crear un DataFrame y eliminar duplicados
    df = pd.DataFrame(data).drop_duplicates()

    return df

def main():
    st.title("Invoice Analyzer")
    
    uploaded_files = st.file_uploader("Upload invoices", type="pdf", accept_multiple_files=True)
    
    if uploaded_files:
        invoices_data = analyze_invoices(uploaded_files)
        st.write(invoices_data)

if __name__ == "__main__":
    main()
