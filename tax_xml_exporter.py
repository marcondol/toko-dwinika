from sqlalchemy import create_engine, MetaData, Table, text
from sqlalchemy.orm import sessionmaker
import pandas as pd
import xml.etree.ElementTree as ET
from xml.dom import minidom
import zipfile
import os

import os
from dotenv import load_dotenv
load_dotenv()

db_url = os.environ.get('DB_URL_TAX') or os.environ['DB_URL']

# Database connection
engine = create_engine(db_url)

uom_dict = {
    'PAK': 'UM.0022',
    'ROL': 'UM.0033',
    'KIT': 'UM.0033',
    'GLN': 'UM.0033',
    'LITERAN': 'UM.0007',
    'SET.': 'UM.0033',
    'ROLL': 'UM.0033',
    'BOX': 'UM.0022',
    'Ltr': 'UM.0009',
    'LBR': 'UM.0020',
    'BH': 'UM.0021',
    'BTL': 'UM.0033',
    'PSG': 'UM.0033',
    'TUBE': 'UM.0033',
    'SET': 'UM.0019',
    'pcs': 'UM.0021',
    'KARTON': 'UM.0022',
    'LTR': 'UM.0007',
    'UNIT': 'UM.0018',
    'PCS': 'UM.0021',
    'PACK': 'UM.0022',
    'BH\'': 'UM.0021',
    'QTN': 'UM.0033',
    'KG': 'UM.0003',
    'LSN': 'UM.0033',
    '2.5 LTR': 'UM.0033'
}

# Get Data from Database
def getDataFaktur(orderNo):
    query = f"""SELECT a.id, order_date, forder_date, customer_name, order_amount, total_amount, b.address, a.order_no from orders a
LEFT JOIN customers b on a.customer_code = b.code
WHERE order_no = '{orderNo}'"""
    df = pd.read_sql_query(query, engine)
    return df

def getFakturDetail(orderId):
    query = f"SELECT a.product_id, a.product_name, a.qty, a.discount, a.amount, a.price, b.uom from orders_detail a LEFT JOIN barang b on a.product_id = b.id  WHERE sales_order_id = {orderId}"
    df = pd.read_sql_query(query, engine)
    return df


def getNPWP(customer_text):
    query = text("SELECT a.*, b.id, b.customer_text as customer_name, LPAD(a.npwp, 16, '0') as padded_npwp FROM customers_npwp a LEFT JOIN customers b ON a.customer_id = b.id WHERE trim(lower(b.customer_text)) = trim(lower('" + customer_text + "'))")
    with engine.connect() as connection:
        result = connection.execute(query)
        for row in result:
            if row.customer_text == None or row.nama_pt == None :
                continue
            if customer_text.lower() == row.customer_name.lower():
                return { 'padded_npwp': row.padded_npwp, 'customer_name': row.nama_pt }
    return None

def generateXMLTax(orderNo):
    faktur = getDataFaktur(orderNo)

    customerData = getNPWP(faktur['customer_name'][0].strip())
    if customerData is None:
        customerData = { 'padded_npwp': '0000000000000000', 'customer_name': None }
    # Create XML structure
    root = ET.Element('TaxInvoiceBulk', {
        'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        'xsi:noNamespaceSchemaLocation': 'TaxInvoice.xsd'
    })
    ET.SubElement(root, 'TIN').text = '0317859734412000'
    list_of_tax_invoice = ET.SubElement(root, 'ListOfTaxInvoice')

    for index, invoice in faktur.iterrows():
        tax_invoice = ET.SubElement(list_of_tax_invoice, 'TaxInvoice')
        ET.SubElement(tax_invoice, 'TaxInvoiceDate').text = invoice.order_date.split(' ')[0]
        ET.SubElement(tax_invoice, 'TaxInvoiceOpt').text = 'Normal'
        ET.SubElement(tax_invoice, 'TrxCode').text = '04'
        ET.SubElement(tax_invoice, 'AddInfo').text = ''
        ET.SubElement(tax_invoice, 'CustomDoc').text =  ''
        ET.SubElement(tax_invoice, 'CustomDocMonthYear').text = invoice.order_no
        ET.SubElement(tax_invoice, 'RefDesc').text = ''
        ET.SubElement(tax_invoice, 'FacilityStamp').text = ''
        ET.SubElement(tax_invoice, 'SellerIDTKU').text = '0317859734412000000000'
        ET.SubElement(tax_invoice, 'BuyerTin').text = customerData['padded_npwp']
        ET.SubElement(tax_invoice, 'BuyerDocument').text = 'TIN'
        ET.SubElement(tax_invoice, 'BuyerCountry').text = 'IDN'
        ET.SubElement(tax_invoice, 'BuyerDocumentNumber').text = customerData['padded_npwp']
        ET.SubElement(tax_invoice, 'BuyerName').text = customerData['customer_name'] if customerData['customer_name'] else invoice.customer_name
        ET.SubElement(tax_invoice, 'BuyerAdress').text = invoice.address
        ET.SubElement(tax_invoice, 'BuyerEmail').text = ''
        ET.SubElement(tax_invoice, 'BuyerIDTKU').text = customerData['padded_npwp'] + '000000'

        list_of_good_service = ET.SubElement(tax_invoice, 'ListOfGoodService')
        good_services = getFakturDetail(invoice.id)
        for index, service in good_services.iterrows():
            taxBase = float(service.price) * float(service.qty) - float(service.discount)
            otherTaxBase =  round(taxBase * 11/12)
            good_service = ET.SubElement(list_of_good_service, 'GoodService')
            ET.SubElement(good_service, 'Opt').text = "A"
            ET.SubElement(good_service, 'Code').text = ''
            ET.SubElement(good_service, 'Name').text = service.product_name
            ET.SubElement(good_service, 'Unit').text = uom_dict[service.uom] if service.uom in uom_dict else 'UM.0033'
            ET.SubElement(good_service, 'Price').text = str(service.price)
            ET.SubElement(good_service, 'Qty').text = str(service.qty)
            ET.SubElement(good_service, 'TotalDiscount').text = str(service.discount)
            ET.SubElement(good_service, 'TaxBase').text = str(round(taxBase))
            ET.SubElement(good_service, 'OtherTaxBase').text = str(otherTaxBase)
            ET.SubElement(good_service, 'VATRate').text = str(12)
            ET.SubElement(good_service, 'VAT').text = str(round((float(service.price) * float(service.qty)) * 0.11))
            ET.SubElement(good_service, 'STLGRate').text = str(0)
            ET.SubElement(good_service, 'STLG').text = str(0)
            otherTaxBase = 0

        # Write to XML file
        # tree = ET.ElementTree(root)
        # Pretty print the XML
        xml_str = ET.tostring(root, encoding='utf-8').decode('utf-8')
        xml_str = minidom.parseString(xml_str).toprettyxml(indent="   ")

        # Save to file
        with open(f"{orderNo}.xml", "w") as f:
            f.write(xml_str)

def generateXMLTaxDay(forderdate):
    query = text("SELECT order_no FROM orders WHERE id in(select sales_order_id from orders_detail) and order_date = '" + forderdate + " 00:00:00'")
#    query = text("SELECT order_no FROM orders WHERE id in(select sales_order_id from orders_detail) and order_date like '2025-01%'")

    def deleteZip():
        for file in os.listdir('.'):
            if file.endswith('.zip'):
                os.remove(file)

#    deleteZip()

    with engine.connect() as connection:
        result = connection.execute(query)
        for row in result:
            generateXMLTax(row[0])
    def zipXMLFiles():
        with zipfile.ZipFile('tax-'+ forderdate +'.zip', 'w') as tax_zip:
            for file in os.listdir('.'):
                if file.endswith('.xml'):
                    tax_zip.write(file)
                    os.remove(file)

    zipXMLFiles()

    def deleteXMLFiles():
        for file in os.listdir('.'):
            if file.endswith('.xml'):
                os.remove(file)

    deleteXMLFiles()

def perbandinganNama(nama_pelanggan):
    from difflib import get_close_matches

    query = text("SELECT * from customers_npwp")
    query2 = text("SELECT * from customers")
    result_df = pd.read_sql_query(query2, engine)
    with engine.connect() as connection:
        result = connection.execute(query)
        for row in result:
            if row.customer_text == None or row.customer_pt == None :
                continue
            closest_match = get_close_matches(row.customer_text.lower(), result_df['customer_text'].str.lower(), n=1, cutoff=0.6)
            if closest_match:
                if not any(row.customer_text.lower().startswith(prefix) for prefix in ['klinik', 'apt', 'rs', 'rumahsakit']):
                    matched_row = result_df[result_df['customer_text'].str.lower() == closest_match[0]].iloc[0]
                    print(f"{row.customer_text}, {matched_row['id']}, {matched_row['customer_text']}")



