#!/usr/bin/python

from cinemanaAPI import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import * 
from PyQt5.uic import loadUiType
from os import path, mkdir
from scripts import get_thumb_image, get_poster_image, Player
from json import dump, load
from time import sleep

BLANK = '---'
EXTERNEL_SUB = 'externel subtitle'
SEARCH_HISTORY_FILE = path.join(path.dirname(__file__), 'data' + path.sep + 'search_history_file.json')
ASSETS_FOLDER = ILE = path.join(path.dirname(__file__), 'assets')
DATA_PATH = path.join(path.dirname(__file__), 'data')


class GetItems(QThread):
    RESULT_DATA = pyqtSignal(list, int)

    def __init__(self, data_fetch_function, tab, **kwargs):
        QThread.__init__(self)
        self.kwargs = kwargs
        self.fn = data_fetch_function # search or getItems
        self.tab = tab

    def run(self):
        json_data, _ = self.fn(**self.kwargs)
        if json_data:
            self.RESULT_DATA.emit(json_data, self.tab)
        else:
            print(_)
            return

class RefreshData(QThread):
    SETSUBTITLES = pyqtSignal(list)
    SETVIDEOS = pyqtSignal(list)

    def __init__(self, nb):
        QThread.__init__(self)
        self.nb = nb

    def run(self):
        eps_info , _ = getInfos(self.nb)

        if eps_info:
            self.SETSUBTITLES.emit(eps_info['translations'])

        else:
            print(_)
            return

        # Add available video qualities
        # Get videos data
        videos_data, _ = getVideos(self.nb)
        if videos_data:
            self.SETVIDEOS.emit(videos_data)

        else:
            print(_)
            return


class SetInfo(QThread):
    LISTEPISODES = pyqtSignal(dict)
    SETMAININFO = pyqtSignal(dict)
    SETSUBTITLES = pyqtSignal(list)
    SETVIDEOS = pyqtSignal(list)
    SETPOSTER = pyqtSignal(bytes)
    ERRORDIALOG = pyqtSignal(object)
    finished = pyqtSignal()


    def __init__(self, nb, kind):
        QThread.__init__(self)
        self.nb = nb
        self.kind = kind
        # self.threadPools = []


    def run(self):
        # get info
        info, _ = getInfos(self.nb)
        if not info:
            self.ERRORDIALOG.emit(_)
            print(_)
            return
        
        # print(info)

        # if item is movie
        if self.kind != '1':            
            eps = {}
            seasons = []

            # Add episodes
            episodes_info, _ = getEpisodes(self.nb)
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
                self.LISTEPISODES.emit(eps)
                    
            else:
                self.ERRORDIALOG.emit(_)
                print(_)
                return 

        # Add available video qualities
        # Get videos data
        videos_data, _ = getVideos(self.nb)
        if videos_data:
            self.SETVIDEOS.emit(videos_data)
            
        else:
            print(_)
            return
        

        # Add available Subs
        try:
            item_info, _ = getInfos(self.nb)
        except:
            pass
        else:
            if 'translations' in item_info.keys():
                self.SETSUBTITLES.emit(item_info['translations'])

        # Set name, year, categories, etc .. 
        self.SETMAININFO.emit(info)

        # Set Poster image
        data = get_poster_image(info['imgObjUrl'])
        if data:
            # print(type(data))
            self.SETPOSTER.emit(data)

        else:
            get_poster_image.delete(info['imgObjUrl'])
            
        self.finished.emit()

class SetPoster(QThread):

    def __init__(self, item, url):
        QThread.__init__(self)
        self.item = item
        self.url = url
        self.tries = 0
        self._isRunning = True
    
    def run(self):
        self.tries += 1
        data = get_thumb_image(self.url)
        if data:
            # print(self.url)
            pixmap = QPixmap()
            pixmap.loadFromData(data)
            try:
                self.item.setIcon(QIcon(pixmap))
            except (RuntimeError, TypeError, NameError):
                return
        
        else:
            get_thumb_image.delete(self.url)
            if self.tries <= 3 and self._isRunning:
                print(f"Trying to set cover for {self.tries} times")
                sleep(5)
                self.run()

    # Ignore This 
    # def stop(self):
    #     # print("Closing cover Thread")
    #     self._isRunning = False
    
ERROR_FORM, _ = loadUiType(path.join(path.dirname(__file__), 'ui' + path.sep + 'error_dialog.ui'))
MAIN_CLASS, _ = loadUiType(path.join(path.dirname(__file__), 'ui' + path.sep + 'main.ui'))
class MainWidnow(QMainWindow, MAIN_CLASS):
    def __init__(self, parent=None):
        super(MainWidnow, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)

        # Set the Custom theme
        toggle_stylesheet('dark.qss')
        self.actionDark_Theme.triggered[bool].connect(self.setTheme)


        # Threads to prevent gui frozen
        # Threads List
        self.threadPools = []
        self.coverPools = []

        # Change Window Title
        self.setWindowTitle("QtCinemana")

        # window icon
        self.setWindowIcon(QIcon(ASSETS_FOLDER + path.sep + 'cinemana.png'))

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

        # Indicates the current search results page or home items page
        self.pageNumber = 1

        # Set completer 
        self.setSearchLineCompleter()

    ###################

        # BEGIN PROGRAM WITH HOME 
        self.homeItems()

    ###################

    def setTheme(self, checked=False):
        if checked:
            toggle_stylesheet('dark.qss')
        else:
            toggle_stylesheet('light.qss')

    def showErrorDialog(self, error):
        self.loading(False)
        print("Showing Error Dialog")
        dialog = QDialog()
        dialog.ui = ERROR_FORM()
        dialog.ui.setupUi(dialog)
        dialog.ui.error_info.setText(str(error))
        dialog.show()
        dialog.exec_()


    def loading(self, state=True):
        """ change cursor shape to loading """
        if state:
            self.setCursor(Qt.WaitCursor)
        else:
            self.unsetCursor()

    def handleButtons(self):
        """ Connect Button to the functions """ 
        self.btnsearch.clicked.connect(self.search)
        self.btnhome.clicked.connect(
            lambda: self.stackedWidget.setCurrentIndex(0))
        self.btnplay.clicked.connect(self.player)
        self.tbtnclear_search.clicked.connect(self.clearSearchResult)
        self.btncloseplayer.clicked.connect(self.closePlayer)
        self.btnaddsub.clicked.connect(self.addExternelSubtitle)
        
    def handleTabChanges(self):
        # If it's in search mode
        search_kword = self.elsearch.text()
        if search_kword:
            self.search()

        else:
            self.homeItems(clear=True)

    def homeItems(self, clear=None):
        self.loading(True)  # Change Cursor to loading

        current_tab = self.home_tabs.currentIndex()
        homeItemsThread = GetItems(getItems, current_tab, itemsPerPage=20, videoKind=current_tab + 1)
        self.threadPools.append(homeItemsThread)        # Add the thread to the list so It won't destroyed
        

        homeItemsThread.RESULT_DATA.connect(lambda data, current_tab: self.lstResult(data, current_tab, clear=clear))

        # Start the thread
        self.threadPools[-1].start()
        self.loading(False)

    def closePlayer(self):
        """ 
            This change a active vaiable value inside the worker to falce
            And when the player worker check it and it's false it will be
            terminated.
         """
        self.worker.active = False
        self.playerThread.quit()
        self.playerThread.wait()


    def player(self):
        """ Threat MPV Player """ 
        video, subtitle = None, None

        # Get current chosen quality and sub
        qua = self.coqual.currentText()
        if qua != BLANK:
            video = self.videos[qua]
        
        sub = self.cosubs.currentText()
        if sub != BLANK:
            subtitle = self.subs[sub]


        if video == None:
            # if no video is available, then end the function..
            return

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
        
        # Final resets
        self.btnplay.hide()
        self.btncloseplayer.show()
        
        # Connect Signal and slots
        self.playerThread.finished.connect(
            lambda: self.btnplay.show()
        )
        self.playerThread.finished.connect(
            lambda: self.btncloseplayer.hide()
        )

        #  Start the playerThread
        self.playerThread.start()

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
        
    def setSearchLineCompleter(self):
        completer = QCompleter(self.loadSearchHistory())
        self.elsearch.setCompleter(completer)


    def loadSearchHistory(self):
        # print('loading')
        if not path.exists(SEARCH_HISTORY_FILE):
            if not path.exists(DATA_PATH):
                mkdir('data')
            # print("Creating new file")
            with open(SEARCH_HISTORY_FILE, 'x') as fo:
                dump([], fo)

        with open(SEARCH_HISTORY_FILE, 'r') as fo:
            try:
                # print("Loading data")
                p_data = load(fo)
                # print(p_data)
            except:
                p_data = []
            finally:
                # print(p_data)
                return p_data


    def addToSearchHistory(self, search_kword):
        
        p_data = self.loadSearchHistory()
        # print(type(p_data))
        if search_kword not in p_data:
            p_data.append(search_kword)

            with open(SEARCH_HISTORY_FILE, 'w') as fo:
                dump(p_data, fo)

    def search(self, page=0):
        search_kword = self.elsearch.text()
        if search_kword:        # If the edit Line is not empty
            self.loading(True)

            # Add to search history
            self.addToSearchHistory(search_kword)

            self.setSearchLineCompleter()

            current_tab = self.home_tabs.currentIndex()
            types = ['movie', 'series']

            searchThread = GetItems(
                search, current_tab, videoTitle=search_kword, type=types[current_tab], page=page)
            self.threadPools.append(searchThread)
            
            searchThread.RESULT_DATA.connect(self.obtainDataAndSearch)
            
            self.threadPools[-1].start()

            self.loading(False)     # Set the Cursor to the normal shape
    
    def obtainDataAndSearch(self, data, current_tab):
        self.lstResult(data, current_tab, clear=True)

        # Show search result clear button
        self.tbtnclear_search.show()


    def lstResult(self, json_info, current_tab, clear=None):
        self.loading(True)

        if current_tab == 0:
            self.listWidget = self.movies_listwidget
        elif current_tab == 1:
            self.listWidget = self.series_listwidget
        else:
            return

        if clear != None:
            self.listWidget.clear()

        self.listWidget.setIconSize(250 * QSize(2, 2))

        for i in json_info:
        # print("Listing result")
            name = i['en_title']

            name += f"\n({i['year']})"

            # Name
            it = QListWidgetItem(name)

            # Set id number
            it.setData(Qt.UserRole, (i['nb'], i['kind']))

            # Set on hover
            it.setToolTip(i['stars'])


            """ Set it for basic image for now and then get the read image """
            it.setIcon(QIcon(ASSETS_FOLDER + path.sep + 'cover.jpg'))
            stRealCover = SetPoster(it, i['imgThumbObjUrl'])
            self.coverPools.append(stRealCover)
            self.coverPools[-1].start()

            # Set Item not selectable
            it.setFlags(it.flags() | ~Qt.ItemIsSelectable)

            self.listWidget.addItem(it)

        self.loading(False)
    
    def viewItem(self, item):
        self.loading(True)     # Change cursor to loading 
                                # Will back to normal in setVideos function
        
        # print(item.data(Qt.UserRole))
        nb, kind = item.data(Qt.UserRole)

        # if item is movie
        if kind == '1':
            # Hide episodes list
            self.tbepisodes.hide()
        
        # If it's series
        else:
            self.tbepisodes.show()
        
        # self.stackedWidget.setCurrentIndex(1)
        stInfo = SetInfo(nb, kind)
        
        # Connect Signal to slots
        stInfo.LISTEPISODES.connect(self.listEpisodes)
        stInfo.SETSUBTITLES.connect(self.setSubtitles)
        stInfo.SETVIDEOS.connect(self.setVideos)
        stInfo.ERRORDIALOG.connect(self.showErrorDialog)
        stInfo.SETPOSTER.connect(self.setPosterImage)
        stInfo.SETMAININFO.connect(self.setMainInfo)
        stInfo.finished.connect(lambda: self.stackedWidget.setCurrentIndex(1))
        
        self.threadPools.append(stInfo)
        self.threadPools[-1].start()

        # self.loading(False)

    def setMainInfo(self, info):
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
        self.linfo.setText(
            "<a href='{}'>info</a>" .format(info['imdbUrlRef']))

        # Set categories
        cate = info['categories']
        categories = []
        for i in cate:
            categories.append(i['en_title'])
        self.lcate.setText(' • '.join(categories))


    def setPosterImage(self, data):
        """ Basically get the data and set the label image """
        pixmap = QPixmap()
        pixmap.loadFromData(data)
        self.lposter.setPixmap(pixmap.scaled(300, 400, Qt.KeepAspectRatio))

    def listEpisodes(self, info):
        self.tbepisodes.clear()
        for s in sorted(info.keys()):
            
            tab = QListWidget(self)
            # tab = self.parent.episodesListWidget(self.parent)
            tab.setEditTriggers(QAbstractItemView.NoEditTriggers)
            tab.currentItemChanged.connect(self.refreshInfo)
            self.tbepisodes.addTab(tab, f'season {s}')

            for e in info[f"{s}"]:
                eps_number = e['episodeNummer']
                episode = QListWidgetItem(f"episode {eps_number}")
                episode.setData(Qt.UserRole, e['nb'])

                # Set Item not selectable
                episode.setFlags(episode.flags() | ~Qt.ItemIsSelectable)
                tab.addItem(episode)

            self.tbepisodes.addTab(tab, f'season {s}')


    def refreshInfo(self, item):
        self.loading(True)

        nb = item.data(Qt.UserRole)
        # print(nb)

        rfrshInfoThread = RefreshData(nb)
        self.threadPools.append(rfrshInfoThread)

        rfrshInfoThread.SETSUBTITLES.connect(self.setSubtitles)
        rfrshInfoThread.SETVIDEOS.connect(self.setVideos)

        self.threadPools[-1].start()

        self.loading(False)

    def addExternelSubtitle(self):
        # getting the file path
        fname, _ = QFileDialog.getOpenFileName(self, 'Choose subtitle file', '~', "Subtitle Files (*.srt *.ass *.ssa *.vtt)")
        if fname:
            self.subs[EXTERNEL_SUB] = fname

            # Get comboBox items
            AllItems = [self.cosubs.itemText(i)
                        for i in range(self.cosubs.count())]
            if EXTERNEL_SUB not in AllItems:
                self.cosubs.addItem(EXTERNEL_SUB)

        else:
            print(':: No subtitle file chosen')
            

    def setSubtitles(self, info):
        self.cosubs.clear()
        self.subs = {}
        self.cosubs.addItem(BLANK)
        try:
            for i in info:
                # print(i)
                if i['extention'] != 'vtt':
                    self.cosubs.addItem(i['name'])
                    self.subs[i['name']] = i['file']
        except:
            print(":: No Available subs")

        
    def setVideos(self, info):
        
        self.videos = {}
        # Remove all previous items
        self.coqual.clear()

        # Add blank '--'
        self.coqual.addItem(BLANK)
        for i in info:
            # print(i)
            self.coqual.addItem(i['resolution'])
            self.videos[i['resolution']] = i['videoUrl']

        self.loading(False)

# Change the theme
def toggle_stylesheet(path):
    '''
    Toggle the stylesheet to use the desired path in the Qt resource
    system (prefixed by `:/`) or generically (a path to a file on
    system).
    '''

    # get the QApplication instance,  or crash if not set
    app = QApplication.instance()
    if app is None:
        raise RuntimeError("No Qt Application found.")

    file = QFile(path)
    file.open(QFile.ReadOnly | QFile.Text)
    stream = QTextStream(file)
    app.setStyleSheet(stream.readAll())

if __name__ == '__main__':
    app = QApplication([])

    window = MainWidnow()
    window.show()
    app.exec_()
