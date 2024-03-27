import os
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from huobi.client.trade import TradeClient
import ccxt
import time
import threading

HUOBI_API_KEY="bf290a35-61efc7c4-9ce815a2-rfhfg2mkl3"
HUOBI_API_SECRET="1e905354-c8ec2b50-7b2adec0-54447"

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(606, 312)
        self.radioButton = QtWidgets.QRadioButton(Form)
        self.radioButton.setGeometry(QtCore.QRect(60, 90, 71, 21))
        self.radioButton.setObjectName("radioButton")
        self.radioButton_2 = QtWidgets.QRadioButton(Form)
        self.radioButton_2.setGeometry(QtCore.QRect(150, 90, 81, 21))
        self.radioButton_2.setObjectName("radioButton_2")
        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(240, 90, 51, 21))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setGeometry(QtCore.QRect(240, 120, 51, 21))
        self.label_2.setObjectName("label_2")
        self.lineEdit = QtWidgets.QLineEdit(Form)
        self.lineEdit.setGeometry(QtCore.QRect(290, 90, 113, 20))
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit_qty = QtWidgets.QLineEdit(Form)
        self.lineEdit_qty.setGeometry(QtCore.QRect(290, 120, 113, 20))
        self.lineEdit_qty.setObjectName("lineEdit_qty")
        self.pushButton = QtWidgets.QPushButton(Form)
        self.pushButton.setGeometry(QtCore.QRect(430, 90, 75, 51))
        self.pushButton.setObjectName("pushButton")
        self.label_time = QtWidgets.QLabel(Form)
        self.label_time.setGeometry(QtCore.QRect(20, 20, 600, 21))
        self.label_time.setObjectName("label_time")
        self.label_price = QtWidgets.QLabel(Form)
        self.label_price.setGeometry(QtCore.QRect(20, 50, 600, 21))
        self.label_price.setObjectName("label_price")
        self.plainTextEdit_details = QtWidgets.QPlainTextEdit(Form)
        self.plainTextEdit_details.setGeometry(QtCore.QRect(20, 150, 561, 141))
        self.plainTextEdit_details.setObjectName("plainTextEdit_details")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "huobi-BTCUSD"))
        self.radioButton.setText(_translate("Form", "BuyStop"))
        self.radioButton_2.setText(_translate("Form", "SellStop"))
        self.label.setText(_translate("Form", "Price : "))
        self.label_2.setText(_translate("Form", "Quantity : "))
        self.pushButton.setText(_translate("Form", "Set"))

class Window(QMainWindow, Ui_Form):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.client = TradeClient(api_key=HUOBI_API_KEY, secret_key=HUOBI_API_SECRET)
        self.exchange = ccxt.huobi()
        self.pushButton.clicked.connect(self.toggle_monitoring)  # This line connects the button click event to the set_order method
        self.update_price_label()
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_price_label)
        self.timer.start(5000)  # Update price every 5 seconds
        self.monitor_thread = None
        self.is_monitoring = False

    def update_price_label(self):
        try:
            ticker = self.exchange.fetch_ticker('BTC/USDT')
            current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            current_price = ticker['last']
            self.label_time.setText(f"Current Time: {current_time}")
            self.label_price.setText(f"Current BTC Price: {current_price}")
        except Exception as e:
            print("Error fetching price:", e)

    def toggle_monitoring(self):
        if not self.is_monitoring:
            self.start_monitoring()
        else:
            self.stop_monitoring()
 
    def start_monitoring(self):
        if self.radioButton.isChecked():
            stop_type = 'buy'
        else:
            stop_type = 'sell'
        stop_price = float(self.lineEdit.text())
        self.monitor_thread = threading.Thread(target=self.monitor_price, args=(stop_type, stop_price), daemon=True)
        self.monitor_thread.start()
        self.pushButton.setText("UnSet")
        self.is_monitoring = True
 
    def stop_monitoring(self):
        self.is_monitoring = False
        self.pushButton.setText("Set")
 
    def monitor_price(self, stop_type, stop_price):
        try:
            while self.is_monitoring:
                ticker = self.client.get_market_ticker(symbol='btcusdt')
                current_price = ticker['close']
                self.label_price.setText(f"Current BTC Price: {current_price}")
                if (stop_type == 'buy' and current_price > stop_price) or (stop_type == 'sell' and current_price < stop_price):
                    self.place_market_order(stop_type)
                    self.stop_monitoring()
                time.sleep(5)  # Adjust this value to change the interval between price checks
        except Exception as e:
            print("Error monitoring price:", e)
 
    def place_market_order(self, stop_type):
        try:
            qty = float(self.lineEdit_qty.text())
            if stop_type == 'buy':
                order_type = 'buy-market'
            else:
                order_type = 'sell-market'
            order_id = self.client.create_order(symbol='btcusdt', account_id='458069616', source='api', order_type=order_type, amount=qty, price=None)
            self.plainTextEdit_details.appendPlainText(f"Order ID: {order_id}")
            self.plainTextEdit_details.appendPlainText("Base Currency: USD")
            self.plainTextEdit_details.appendPlainText(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")
            QMessageBox.information(self, 'Order Placed', f'Order ID: {order_id}')
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))


def main_form():
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main_form()

