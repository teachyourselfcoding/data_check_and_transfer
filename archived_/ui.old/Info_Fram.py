# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Info_Fram.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Info_Form(object):
    def setupUi(self, Info_Form):
        Info_Form.setObjectName("Info_Form")
        Info_Form.resize(1300, 914)
        self.SSD_label = QtWidgets.QLabel(Info_Form)
        self.SSD_label.setGeometry(QtCore.QRect(430, 100, 100, 20))
        self.SSD_label.setObjectName("SSD_label")
        self.SSD_browser = QtWidgets.QTextBrowser(Info_Form)
        self.SSD_browser.setGeometry(QtCore.QRect(540, 100, 391, 31))
        self.SSD_browser.setObjectName("SSD_browser")
        self.Detail_label = QtWidgets.QLabel(Info_Form)
        self.Detail_label.setGeometry(QtCore.QRect(30, 250, 81, 17))
        self.Detail_label.setObjectName("Detail_label")
        self.Start_btn = QtWidgets.QPushButton(Info_Form)
        self.Start_btn.setGeometry(QtCore.QRect(640, 150, 81, 31))
        self.Start_btn.setObjectName("Start_btn")
        self.Detail_table = QtWidgets.QTableWidget(Info_Form)
        self.Detail_table.setGeometry(QtCore.QRect(10, 279, 1280, 291))
        self.Detail_table.setMinimumSize(QtCore.QSize(480, 200))
        self.Detail_table.setMaximumSize(QtCore.QSize(1280, 300))
        self.Detail_table.setObjectName("Detail_table")
        self.Detail_table.setColumnCount(0)
        self.Detail_table.setRowCount(0)
        self.SSD_loaded_label = QtWidgets.QLabel(Info_Form)
        self.SSD_loaded_label.setGeometry(QtCore.QRect(30, 30, 91, 17))
        self.SSD_loaded_label.setObjectName("SSD_loaded_label")
        self.SSD_loaded_browser = QtWidgets.QTextBrowser(Info_Form)
        self.SSD_loaded_browser.setGeometry(QtCore.QRect(120, 30, 230, 191))
        self.SSD_loaded_browser.setObjectName("SSD_loaded_browser")
        self.Log_table = QtWidgets.QTableWidget(Info_Form)
        self.Log_table.setGeometry(QtCore.QRect(10, 650, 1280, 240))
        self.Log_table.setObjectName("Log_table")
        self.Log_table.setColumnCount(0)
        self.Log_table.setRowCount(0)
        self.Log_label = QtWidgets.QLabel(Info_Form)
        self.Log_label.setGeometry(QtCore.QRect(30, 610, 51, 31))
        self.Log_label.setTextFormat(QtCore.Qt.AutoText)
        self.Log_label.setObjectName("Log_label")

        self.retranslateUi(Info_Form)
        QtCore.QMetaObject.connectSlotsByName(Info_Form)

    def retranslateUi(self, Info_Form):
        _translate = QtCore.QCoreApplication.translate
        Info_Form.setWindowTitle(_translate("Info_Form", "进度显示"))
        self.SSD_label.setText(_translate("Info_Form", "当前操作路径："))
        self.Detail_label.setText(_translate("Info_Form", "任务详情："))
        self.Start_btn.setText(_translate("Info_Form", "开始"))
        self.SSD_loaded_label.setText(_translate("Info_Form", "已加载硬盘："))
        self.Log_label.setText(_translate("Info_Form", "日志："))
