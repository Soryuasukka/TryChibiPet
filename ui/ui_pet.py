# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_pet.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(873, 615)
        self.label_pet = QtWidgets.QLabel(Form)
        self.label_pet.setGeometry(QtCore.QRect(420, 320, 101, 101))
        self.label_pet.setAutoFillBackground(False)
        self.label_pet.setText("")
        self.label_pet.setAlignment(QtCore.Qt.AlignCenter)
        self.label_pet.setObjectName("label_pet")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))

