#!/usr/bin/python

from cinemanaAPI import *

# Import PyQt5
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import * 
from PyQt5.uic import loadUiType


from os import path

from scripts import get_thumb_image, get_poster_image, Player

MAIN_CLASS, _ = loadUiType(path.join(path.dirname(__file__), 'ui/main.ui'))

class MainWidnow(QMainWindow, MAIN_CLASS):
    def __init__(self, parent=None):
        super(MainWidnow, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)

        # Initialize handlers
        self.handleButtons()

        # Hide search-result-clear button
        self.tbtnclear_search.hide()
        self.btncloseplayer.hide()

        # Items List 
        self.listWidget = QListWidget()
        self.movies_listwidget.itemClicked.connect(self.viewItem)
        self.series_listwidget.itemClicked.connect(self.viewItem)


        # Videos and subs for player
        self.videos = {}
        self.subs = {}

        # Search on tab change
        self.home_tabs.currentChanged.connect(self.handleTabChanges) #changed!
        # self.connect(self.home_tabs, SIGNAL('currentChanged(int)'), self.search)
        # self.home_tabs.blockSignals(False)

        # Indicates the current search results page or home items page
        self.pageNumber = 1

    ###################

        # BEGIN PROGRAM WITH HOME 
        # self.homeItems()

    ###################
    def loading(self, state=True):
        """ change cursor shape to loading """
        if state:
            self.setCursor(Qt.WaitCursor)
        else:
            self.unsetCursor()

    def handleButtons(self):
        self.btnsearch.clicked.connect(self.search)
        self.btnhome.clicked.connect(
            lambda: self.stackedWidget.setCurrentIndex(0))
        self.btnplay.clicked.connect(self.player)
        self.tbtnclear_search.clicked.connect(self.clearSearchResult)
        self.btncloseplayer.clicked.connect(self.closePlayer)
        
    def handleTabChanges(self):
        search_kword = self.elsearch.text()
        if search_kword:
            self.search()

        else:
            self.homeItems(clear=True)

    def homeItems(self, clear=None):
        self.loading(True)

        current_tab = self.home_tabs.currentIndex()
        items_info, _ = getItems(itemsPerPage=50, videoKind=current_tab + 1)

        if items_info:
            self.lstResult(items_info, clear=clear)
        
        else:
            print(_)
            return
        self.loading(False)

    def closePlayer(self):
        self.worker.active = False
        self.playerThread.quit()
        self.playerThread.wait()


    def player(self):
        # self.loading(True)
        # print(self.videos, self.subs)
        video, subtitle = None, None

        # Get current chosen quality and sub
        
        qua = self.coqual.currentText()
        if qua:
            video = self.videos[qua]
        
        sub = self.cosubs.currentText()
        if sub:
            subtitle = self.subs[sub]

        self.playerThread = QThread()
        
        # Create a worker object
        self.worker = Player(video, subtitle)
        
        #  Move worker to the playerThread
        self.worker.moveToThread(self.playerThread)
        
        #  Connect signals and slots
        self.playerThread.started.connect(self.worker.play)
        self.worker.finished.connect(self.playerThread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.playerThread.finished.connect(self.playerThread.deleteLater)
        
        #  Start the playerThread
        self.playerThread.start()

        # Final resets
        self.btnplay.hide()
        self.btncloseplayer.show()
        
        self.playerThread.finished.connect(
            lambda: self.btnplay.show()
        )
        self.playerThread.finished.connect(
            lambda: self.btncloseplayer.hide()
        )

    def clearSearchResult(self):
        self.loading(True)
        # Hide clear button
        self.tbtnclear_search.hide()

        # Clear Search Reuslt
        self.movies_listwidget.clear()
        self.series_listwidget.clear()

        # Clear search line
        self.elsearch.clear()

        # List Home Items
        self.homeItems()
        self.loading(False)
        

    def search(self):
        search_kword = self.elsearch.text()
        if search_kword:
            self.loading(True)
            print("Searching ...")

            current_tab = self.home_tabs.currentIndex()

            types = ['movie', 'series']

            search_resuslt, _ = search(videoTitle=search_kword, type=types[current_tab])

            if search_resuslt:
                self.lstResult(search_resuslt, clear=True)
                
                # Show search result clear button
                self.tbtnclear_search.show()
            else:
                print(_)
            self.loading(False)

    def lstResult(self, json_info, clear=None):
        self.loading(True)
        current_tab = self.home_tabs.currentIndex()

        if current_tab == 0:
            self.listWidget = self.movies_listwidget
        elif current_tab == 1:
            self.listWidget = self.series_listwidget
        else:
            return

        if clear != None:
            self.listWidget.clear()

        self.listWidget.setIconSize(250 * QSize(2, 2))

        # print(json_info[0])

        for i in json_info:
            name = i['en_title']

            name += f"\n({i['year']})"

            # Name
            it = QListWidgetItem(name)

            # Set id number
            it.setData(Qt.UserRole, (i['nb'], i['kind']))

            # Set on hover
            it.setToolTip(i['stars'])

            # Poster
            data = get_thumb_image(i['imgThumbObjUrl'])
            pixmap = QPixmap()
            pixmap.loadFromData(data)

            it.setIcon(QIcon(pixmap))

            # Set Item not selectable
            it.setFlags(it.flags() | ~Qt.ItemIsSelectable)

            self.listWidget.addItem(it)

        self.loading(False)
    
    def viewItem(self, item):
        self.loading(True)
        # print(item.data(Qt.UserRole))
        nb, kind = item.data(Qt.UserRole)
        
        # get info
        info, _ = getInfos(nb)
        if info:
            # print(info)

            # if item is movie
            if kind == '1':
                # Hide episodes list
                self.tbepisodes.hide()

            else:
                self.tbepisodes.show()

                eps = {}
                seasons = []

                # Add episodes
                episodes_info, _ = getEpisodes(nb)
                if episodes_info:
                    # print(episodes_info)
                    for i in episodes_info:
                        if i['season'] not in seasons:
                            # print(i['season'])
                            seasons.append(i['season'])
                            eps[f"{i['season']}"] = []
                    for i in episodes_info:
                        eps[f"{i['season']}"].append(i)

                    # print(seasons)
                    self.tbepisodes.clear()
                    for s in sorted(seasons):
                      
                        tab = QListWidget()
                        tab.setEditTriggers(QAbstractItemView.NoEditTriggers)
                        tab.itemClicked.connect(self.refreshInfo)

                        for e in eps[f"{s}"]:
                            eps_number = e['episodeNummer']
                            episode = QListWidgetItem(f"episode {eps_number}")
                            episode.setData(Qt.UserRole, e['nb'])

                            # Set Item not selectable
                            episode.setFlags(episode.flags() |
                                             ~Qt.ItemIsSelectable)
                            tab.addItem(episode)

                        self.tbepisodes.addTab(tab, f'season {s}')
                        
                else:
                    print(_)
                    return


            # Add available Subs
            self.cosubs.clear()
            self.subs = {}
            item_info, _ = getInfos(nb)
            if item_info:
                # print(item_info)
                try:
                    for i in item_info['translations']:
                    # print(i)
                        if i['extention'] != 'vtt':
                            self.cosubs.addItem(i['name'])
                            self.subs[i['name']] = i['file'] 
                except:
                    print("No Available subs")

            else:
                print(_)
                return 

            # Add available video qualities
            # Get videos data
            videos_data, _ = getVideos(nb)
            if videos_data:
                self.videos = {}
                self.coqual.clear()
                for i in videos_data:
                    # print(i)
                    self.coqual.addItem(i['resolution'])
                    self.videos[i['resolution']] = i['videoUrl']

            else:
                print(_)
                return

            # print(self.videos, self.subs)
            # Set Poster image
            data = get_poster_image(info['imgObjUrl'])
            if data:
                pixmap = QPixmap()
                pixmap.loadFromData(data)
                self.lposter.setPixmap(pixmap.scaled(300, 400, Qt.KeepAspectRatio))

            # Set en Name
            self.lenname.setText(info['en_title'])

            # Set ar name
            if info['ar_title'] != info['en_title']:
                self.larname.show()
                self.larname.setText(info['ar_title'])
            else:
                self.larname.hide()

            # Set year
            self.lyear.setText(f"({info['year']})")

            # Set stars
            self.lstars.setText(info['stars'])

            # Set story
            self.lstory.setText(info['en_content'])

            # set online info link
            self.linfo.setText("<a href='{}'>info</a>" .format(info['imdbUrlRef']))

            # Set categories
            cate = info['categories']
            categories = []
            for i in cate:
                categories.append(i['en_title'])
            self.lcate.setText(' • '.join(categories))
                
            self.stackedWidget.setCurrentIndex(1)

        else:
            print(_)
            return
        
        self.loading(False)

    def refreshInfo(self, item):
        self.loading(True)
        nb = item.data(Qt.UserRole)
        print(nb)

        # Add available Subs
        self.cosubs.clear()
        eps_info , _ = getInfos(nb)

        if eps_info:
            # If translation is available 
            try:
                for i in eps_info['translations']:
                    if i['extention'] != 'vtt':
                        self.cosubs.addItem(i['name'])
                        self.subs[i['name']] = i['file']
            except:
                print("No Available subs")

        else:
            print(_)
            return

        # Add available video qualities
        # Get videos data
        videos_data, _ = getVideos(nb)
        if videos_data:
            self.videos = {}
            self.coqual.clear()
            for i in videos_data:
                self.coqual.addItem(i['resolution'])
                self.videos[i['resolution']] = i['videoUrl']
        else:
            print(_)
            return

        self.loading(False)

if __name__ == '__main__':
    app = QApplication([])
    window = MainWidnow()
    window.show()
    app.exec_()
