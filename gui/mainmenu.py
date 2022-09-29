from PyQt6.QtWidgets import QMainWindow, QMessageBox
from PyQt6.uic import loadUi

from gui.irodsBrowser import irodsBrowser
from gui.irodsSearch import irodsSearch
from gui.irodsUpDownload import irodsUpDownload
from gui.irodsInfo import irodsInfo

import sys
import logging

class QPlainTextEditLogger(logging.Handler):
    def __init__(self, widget):
        super(QPlainTextEditLogger, self).__init__()

        self.widget = widget
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)

    def write(self, m):
        pass

class mainmenu(QMainWindow):
    def __init__(self, widget, ic, ienv):
        super(mainmenu, self).__init__()
        loadUi("gui/ui-files/MainMenu.ui", self)
        self.ic = ic
        self.widget = widget  # stackedWidget
        self.ienv = ienv

        # Menu actions
        self.actionExit.triggered.connect(self.programExit)
        self.actionCloseSession.triggered.connect(self.newSession)

        if not ienv or not ic:
            self.actionSearch.setEnabled(False)
            self.actionSaveConfig.setEnabled(False)
            ticketAccessWidget = loadUi("gui/ui-files/tabTicketAccess.ui")
            self.tabWidget.addTab(ticketAccessWidget, "Ticket Access")
            self.ticketAccessTab = irodsTicketLogin(ticketAccessWidget)

        else:
            self.actionSearch.triggered.connect(self.search)
            self.actionSaveConfig.triggered.connect(self.saveConfig)
            # self.actionExportMetadata.triggered.connect(self.exportMeta)

            # Data Transfers default for research Cloud, index 0
            updownloadWidget = loadUi("gui/ui-files/tabUpDownload.ui")
            self.tabWidget.addTab(updownloadWidget, "Data Transfers")
            self.updownload = irodsUpDownload(updownloadWidget, ic, self.ienv)
            log_handler = QPlainTextEditLogger(updownloadWidget.logs)
            logging.getLogger().addHandler(log_handler)

            # Browser, Dependency for search, index 1
            self.browserWidget = loadUi("gui/ui-files/tabBrowser.ui")
            self.tabWidget.addTab(self.browserWidget, "Browser")
            self.irodsBrowser = irodsBrowser(self.browserWidget, ic)

            # general info
            self.infoWidget = loadUi("gui/ui-files/tabInfo.ui")
            self.tabWidget.addTab(self.infoWidget, "Info")
            self.irodsInfo = irodsInfo(self.infoWidget, ic)
    
            self.tabWidget.setCurrentIndex(0)

    # connect functions
    def programExit(self):
        quit_msg = "Are you sure you want to exit the program?"
        reply = QMessageBox.question(self, 'Message', quit_msg, QMessageBox.StandardButton.Yes,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if self.ic:
                self.ic.session.cleanup()
            elif self.ticketAccessTab.ic:
                self.ticketAccessTab.ic.closeSession()
            sys.exit()
        else:
            pass

    def newSession(self):
        quit_msg = "Are you sure you want to disconnect?"
        reply = QMessageBox.question(self, 'Message', quit_msg, QMessageBox.StandardButton.Yes,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if self.ic:
                self.ic.session.cleanup()
            elif self.ticketAccessTab.ic:
                self.ticketAccessTab.ic.closeSession()
            currentWidget = self.widget.currentWidget()
            self.widget.setCurrentIndex(self.widget.currentIndex()-1)
            self.widget.removeWidget(currentWidget)
            currentWidget = self.widget.currentWidget()
            currentWidget.init_envbox()
        else:
            pass

    def search(self):
        search = irodsSearch(self.ic, self.browserWidget.collTable)
        search.exec()

    def saveConfig(self):
        path = saveIenv(self.ienv)
        self.globalErrorLabel.setText("Environment saved to: "+path)

    def exportMeta(self):
        print("TODO: Metadata export")
