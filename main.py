from olsera_fetch import get_data_barang
from olsera_fetch import get_data_pelanggan
from olsera_fetch import get_data_penjualan
from olsera_fetch import get_data_penjualan_detail
from olsera_fetch import get_data_pembelian
from olsera_fetch import get_data_pembelian_detail
from olsera_fetch import get_data_pelanggan2
from olsera_fetch import login
from olsera_fetch import ensure_schema
from tax_xml_exporter import generateXMLTax, generateXMLTaxDay, perbandinganNama
import argparse
# import sys
# from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QComboBox


# class OlseraFetcherApp(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.initUI()

#     def initUI(self):
#         layout = QVBoxLayout()

#         self.label = QLabel('Select Data Type:', self)
#         layout.addWidget(self.label)

#         self.comboBox = QComboBox(self)
#         self.comboBox.addItems(["barang", "order", "orderdetail", "pelanggan", "login", "tax"])
#         layout.addWidget(self.comboBox)

#         self.button = QPushButton('Fetch Data', self)
#         self.button.clicked.connect(self.on_click)
#         layout.addWidget(self.button)

#         self.setLayout(layout)
#         self.setWindowTitle('Olsera Fetcher')
#         self.show()

#     def on_click(self):
#         jenisdata = self.comboBox.currentText()
#         if jenisdata == "barang":
#             get_data_barang()
#         elif jenisdata == "order":
#             get_data_penjualan()
#         elif jenisdata == "orderdetail":
#             get_data_penjualan_detail()
#         elif jenisdata == "pelanggan":
#             get_data_pelanggan()
#         elif jenisdata == "login":
#             login()
#         elif jenisdata == "tax":
#             generateXMLTax()
#         else:
#             self.label.setText("Invalid Argument")

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     ex = OlseraFetcherApp()
#     sys.exit(app.exec_())


def main():

    parser = argparse.ArgumentParser(description='Olsera Fetcher')
    parser.add_argument('--jenisdata', help='Username')
    parser.add_argument('--orderNo', help='Order Number')
    parser.add_argument('--date', help='tanggal penjualan')
    parser.add_argument('--nama', help='Nama Pelanggan')
    args = parser.parse_args()

    ensure_schema()

#    if args.jenisdata == "barang":
#        get_data_barang()
#    elif args.jenisdata == "order":
#        get_data_penjualan()
#    elif args.jenisdata == "purchase":
#        get_data_pembelian()
#    elif args.jenisdata == "purchasedetail":
#        get_data_pembelian_detail()
#    elif args.jenisdata == "orderdetail":
#        get_data_penjualan_detail()
#    elif args.jenisdata == "pelanggan":
#        get_data_pelanggan()
#    elif args.jenisdata == "login":
#        login()
#    elif args.jenisdata == "tax":
#        generateXMLTax(args.orderNo)
#    elif args.jenisdata == "tax-10":
#        generateXMLTaxDay(args.date)
#    elif args.jenisdata == "pelanggan2":
#        get_data_pelanggan2()
#    else:
#        print("Invalid Argument")
#        print("Please use --jenisdata with value 'barang', 'order', 'orderdetail', 'pelanggan', 'login', or 'tax'")

    if args.jenisdata == "all":
        # 1. Master Data
        get_data_barang()
        get_data_pelanggan()
        
        # 2. Transactions
        get_data_penjualan()
        get_data_penjualan_detail()
        get_data_pembelian()
        get_data_pembelian_detail()
    
    elif args.jenisdata == "barang":
        get_data_barang()
    elif args.jenisdata == "order":
        get_data_penjualan()
    elif args.jenisdata == "purchase":
        get_data_pembelian()
    elif args.jenisdata == "purchasedetail":
        get_data_pembelian_detail()
    elif args.jenisdata == "orderdetail":
        get_data_penjualan_detail()
    elif args.jenisdata == "pelanggan":
        get_data_pelanggan()
    elif args.jenisdata == "login":
        login()
    elif args.jenisdata == "tax":
        generateXMLTax(args.orderNo)
    elif args.jenisdata == "tax-10":
        generateXMLTaxDay(args.date)
    elif args.jenisdata == "pelanggan2":
        get_data_pelanggan2()
    else:
        print("Invalid Argument")
        # Updated help text to include 'all'
        print("Please use --jenisdata with value 'barang', 'order', 'orderdetail', 'pelanggan', 'login', 'tax', or 'all'")


if __name__ == "__main__":
    main()





