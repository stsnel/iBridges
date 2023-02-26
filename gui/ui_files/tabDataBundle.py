"""Created by: PyQt6 UI code generator from the corresponding UI file

WARNING: Any manual changes made to this file will be lost when pyuic6 is
run again.  Do not edit this file unless you know what you are doing.
"""


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_tabDataBundle(object):
    def setupUi(self, tabDataBundle):
        tabDataBundle.setObjectName("tabDataBundle")
        tabDataBundle.resize(640, 532)
        tabDataBundle.setStyleSheet("QWidget\n"
"{\n"
"    color: rgb(86, 184, 139);\n"
"    background-color: rgb(54, 54, 54);\n"
"    selection-background-color: rgb(58, 152, 112);\n"
"}\n"
"\n"
"QTreeView\n"
"{\n"
"    background-color: rgb(85, 87, 83);\n"
"}\n"
"\n"
"QLabel#statusLabel\n"
"{\n"
"    color: rgb(217, 174, 23);\n"
"}\n"
"")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(tabDataBundle)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label_2 = QtWidgets.QLabel(tabDataBundle)
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_3.addWidget(self.label_2)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout_3.addItem(spacerItem)
        self.irodsZoneLabel = QtWidgets.QLabel(tabDataBundle)
        self.irodsZoneLabel.setText("")
        self.irodsZoneLabel.setObjectName("irodsZoneLabel")
        self.verticalLayout_3.addWidget(self.irodsZoneLabel)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.irodsFsTreeView = QtWidgets.QTreeView(tabDataBundle)
        self.irodsFsTreeView.setMinimumSize(QtCore.QSize(0, 600))
        self.irodsFsTreeView.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.irodsFsTreeView.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.irodsFsTreeView.setObjectName("irodsFsTreeView")
        self.horizontalLayout.addWidget(self.irodsFsTreeView)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QtWidgets.QLabel(tabDataBundle)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.resourceBox = QtWidgets.QComboBox(tabDataBundle)
        self.resourceBox.setObjectName("resourceBox")
        self.horizontalLayout_2.addWidget(self.resourceBox)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.forceCheckBox = QtWidgets.QCheckBox(tabDataBundle)
        self.forceCheckBox.setObjectName("forceCheckBox")
        self.verticalLayout.addWidget(self.forceCheckBox)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout.addItem(spacerItem2)
        self.createButton = QtWidgets.QPushButton(tabDataBundle)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.createButton.setFont(font)
        self.createButton.setObjectName("createButton")
        self.verticalLayout.addWidget(self.createButton)
        self.extractButton = QtWidgets.QPushButton(tabDataBundle)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.extractButton.setFont(font)
        self.extractButton.setObjectName("extractButton")
        self.verticalLayout.addWidget(self.extractButton)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout_3.addItem(spacerItem3)
        self.statusLabel = QtWidgets.QLabel(tabDataBundle)
        self.statusLabel.setStyleSheet("")
        self.statusLabel.setText("")
        self.statusLabel.setObjectName("statusLabel")
        self.verticalLayout_3.addWidget(self.statusLabel)

        self.retranslateUi(tabDataBundle)
        QtCore.QMetaObject.connectSlotsByName(tabDataBundle)

    def retranslateUi(self, tabDataBundle):
        _translate = QtCore.QCoreApplication.translate
        tabDataBundle.setWindowTitle(_translate("tabDataBundle", "Form"))
        self.label_2.setText(_translate("tabDataBundle", "(Un)Bundle Collections:"))
        self.label.setText(_translate("tabDataBundle", "Select: resource / free GB"))
        self.forceCheckBox.setText(_translate("tabDataBundle", "Force operations"))
        self.createButton.setText(_translate("tabDataBundle", "Create Bundle"))
        self.extractButton.setText(_translate("tabDataBundle", "Extract Bundle"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    tabDataBundle = QtWidgets.QWidget()
    ui = Ui_tabDataBundle()
    ui.setupUi(tabDataBundle)
    tabDataBundle.show()
    sys.exit(app.exec())
