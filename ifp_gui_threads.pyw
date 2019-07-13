# -*- coding:cp936 -*-
## TODO: 烧写线程与界面线程的文本传递只能通过signal-slot机制, 不能在烧写线程中直接控制界面控件
##       这可能需要将烧写线程和ifp基本函数重新封装成一个类,以后有时间再做好了

imort sys
import ifp
import pickle
import thread
import traceback
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from serial.tools.list_ports import *
from myserial import *

def QString2unicode(q_string):
    return unicode(q_string.toUtf8(), 'utf8')

class my_TextBrowser(QTextBrowser):
    def __init__(self, parent = None):
        super(my_TextBrowser, self).__init__(parent)
        self.clear_action = QAction('Clear All', self)
        self.clear_action.triggered.connect(self.clear_all)
        
    def contextMenuEvent (self, context_menu_event):
        popMenu = self.createStandardContextMenu()
        popMenu.addSeparator()
        popMenu.addAction(self.clear_action)
        popMenu.exec_(QCursor.pos())
        
        
    def clear_all(self):
        self.clear()

__intro_text__ = '''
<font color=red><B># input pipe description here(below are some examples), <br>
# or click "Open Batch File" button to select a pipe description file</B><br></font>
<blockquote>
    # '#' means comment<br>
    # for example, node [5e1d0a048822] is the target<br>
    # 5e1d0a048822 2020 # inline comment<br><br>

    # or normal 2-stage pipe, node [5e1d0a048611] is the target, node [5e1d0a048822] is the routing node<br>
    # 5e1d0a048822 2020 5e1d0a048611 2020<br><br>

    # just uid, a default '5e1d0a056699 2020' pipe will setup<br>
    # 5e1d0a056699<br>
    
</blockquote><br>
<B># Input the pipe description below<br></B>
<br>
5e1d0a087176
'''

__ver_text__ = '''
<B> IFP GUI Uploader, version 2.1<br>
    Author: Lv Haifeng<br>
    Last Modification: 2016-01-27<br>
</B>'''

class ifp_ui(QWidget):
    def __init__(self, parent=None):
        
        super(ifp_ui, self).__init__(parent)

        #初始化存储内容
        try:
            f = open('ifp_gui.cfg','rb')
            config = pickle.load(f)
            f.close()
            last_port = config['last_port']
            last_hexfile = config['last_hexfile']
            last_size = config['last_window_size']
            
            pos = last_hexfile.rfind('/')
            search_dir = last_hexfile[0:pos+1]             # hex文件目录
            print search_dir
            
            print 'cfg file exists'
            for item in config:
                print '%s:%s' % (item, config[item])
            
        except:
            last_port = 'COM1'
            last_hexfile = ''
            search_dir = '.'
            last_size = QSize(800, 600)

        #图标
        icon = QIcon(r'e:\Documents\My Sync Folder\Python\test\belling2.png')

        #字体
        font = QFont('Courier New', 10)

        self.statusbar = QStatusBar()                           # 状态栏
        self.statusbar.showMessage("Ver 3.1, Dev by Lv Haifeng")


        ## 面板控件
        
        # 烧录文件选择按钮
        self.open_hex_file_button = QPushButton('Open Hex File...')  # 打开hex文件的按钮
        self.open_hex_file_button.setStatusTip('Open and select the hex image file to upload')
        QObject.connect(self.open_hex_file_button, SIGNAL('clicked()'), self.on_open_hex_file)
        
        # 串口选择下拉框
        self.com_option = QComboBox()

        for i, port in enumerate(comports()):
            item_text = port[1].decode('gbk')
            if(len(item_text)>22):
                item_text = '...'+item_text[-22:]
            self.com_option.addItem(item_text)
            
            port_name = item_text[item_text.rfind('(')+1:-1]
            
            if 'config' in locals().keys():
                if port_name.upper() == last_port.upper():
                    self.com_option.setCurrentIndex(i)

        QObject.connect(self.com_option, SIGNAL('currentIndexChanged(int)'), self.on_com_port_changed)
        
        # Pipe描述文本框
        self.pipe_edit = QTextEdit()                            # 可手动输入Pipe的文本框
        self.setFont(font)
        self.pipe_edit.setHtml(__intro_text__)
        
        self.open_batch_file_button = QPushButton('Open Batch File...') # 打开批处理文件的按钮
        QObject.connect(self.open_batch_file_button, SIGNAL('clicked()'), self.on_open_batch_file)
        
        self.burn_button = QPushButton('Burn!')                 # 打开批处理文件的按钮
        #self.burn_button.setEnabled(False)
        QObject.connect(self.burn_button, SIGNAL('clicked()'), self.on_burn)
        
        # 输出文本框 
        self.browser = my_TextBrowser()                           # 文本
        

        #控件布局
        layout = QGridLayout()
        layout.addWidget(self.open_hex_file_button, 1, 1, 1, 1)
        
        layout.addWidget(self.com_option, 1, 2, 1, 1)
        #layout.addWidget(self.label, 2, 1, 1, 2)
        layout.addWidget(self.pipe_edit, 3, 1, 1, 2)
        layout.addWidget(self.open_batch_file_button, 4, 1, 1, 1)
        layout.addWidget(self.burn_button, 4, 2, 1, 1)
        layout.addWidget(self.browser, 1, 3, 4, 2)
        layout.addWidget(self.statusbar, 5, 1, 1, 4)
        
        #变量设置
        self.port = last_port
        self.hexfile = last_hexfile
        self.search_dir = search_dir

        
        #其余
        self.setLayout(layout)
        self.setWindowTitle('IFP')
        self.setWindowIcon(icon)
        self.resize(last_size)

        self.pipe_edit.setFocus()
        self.pipe_edit.selectAll()

        if len(self.hexfile) >0 :
            self.setWindowTitle('IFP - %s' % self.hexfile)
            self.browser.append('<font color = blue><B>Load Hex File : %s</B></font>' % self.hexfile)

        
    ## 重载closeEvent函数,该函数在窗体关闭时被调用
    def closeEvent(self, close_event):                  
        import pickle
        
        f = None
        try:
            f = open('ifp_gui.cfg','wb')
            config = {'last_port':self.port
                        ,'last_hexfile':self.hexfile
                        ,'last_window_size':self.size()}
            pickle.dump(config,f)
        finally:
            if f is not None:
                f.close()

    def on_open_hex_file(self):
        path = unicode(QFileDialog.getOpenFileName(self, 'Open Hex File', self.search_dir, '*.hex').toUtf8(), 'utf8')
        if len(path) > 0:
            self.hexfile = path
            self.setWindowTitle('IFP - %s' % self.hexfile)
            self.browser.append('<font color = blue><B>Load Hex File : %s</B></font>' % self.hexfile)
    
    def on_com_port_changed(self, i):
        port_text = QString2unicode(self.com_option.currentText())
        self.port = port_text[port_text.rfind('(')+1:-1]

    
    def on_open_batch_file(self):
        '''load the batch file and paste its contents to pipe textedit
        '''
        batchfile = QFileDialog.getOpenFileName(self, 'Open Batch File', self.search_dir)   #返回的是一个QString类型
        batchfile = unicode(batchfile.toUtf8(), 'utf8')                         #如果路径有中文,如不处理将出错;处理方法是将其转换成python内部处理的unicode
        f = open(batchfile)
        self.pipe_edit.clear()
        for line in f:
            self.pipe_edit.append(line.strip('\n').decode('gbk'))
            
    def on_burn(self):
        try:
            try:
                ser = init_uart(self.port)
                ifpp_uid = ifp.check_ifpp(ser)
                if(ifpp_uid != ''):
                    ser.close()
                else:
                    re_display("can't connect IFPP by %s\n>" % self.port)
                    return
            except SerialException:
                re_display("can't open %s\n>" % self.port)
                return
            
            data_buffer, data_chips = ifp.readhexfile(self.hexfile)
            
            pipe_text = QString2unicode(self.pipe_edit.toPlainText())
            pipe_set = ifp.process_pipe_info(pipe_text)
            
            # Way #1.
            #ifp.batch_burn_process(self.port, ifpp_uid, pipe_set, data_buffer, data_chips)
            
            
            # Way #2.
            self.burn_thread = BurnThread(self.port, ifpp_uid, pipe_set, data_buffer, data_chips)
            #self.connect(self.burn_thread, SIGNAL("finished()"), self.burn_thread, SLOT("deleteLater()"))
            self.connect(self.burn_thread, SIGNAL("output(str)"), self, SLOT("primary_display_slot"))
            self.burn_thread.start()
            
        except Exception as e:
            re_display("<font color=red>%s</font>" % traceback.format_exc())


       
    def primary_display_slot(self, s):
        if s.startswith("IfpException"):
            s = '<font color = red><B>' + s + '</font></B>'
       self.browser.append(s)
       self.browser.repaint()
        
    
    def secondary_output(s):
        if s.startswith("IfpException"):
            s = '<font color = red><B>' + s + '</font></B>'
        
        self.emit
    
def re_display(s, *other_s):
    for t in other_s:
        s += t
    
    if s.startswith("IfpException"):
        s = '<font color = red><B>' + s + '</font></B>'
   self.browser.append(s)
   self.browser.repaint()
   

    
def qtpy_gui_response():
    QApplication.processEvents()
    
class IfpThread(QThread, Ifp):
    def __init__(self, port, ifpp_uid, pipe_set, data_buffer, data_chips):
        super(BurnThread, self).__init__(None)
        self.port = port
        self.ifpp_uid = ifpp_uid
        self.pipe_set = pipe_set
        self.data_buffer = data_buffer
        self.data_chips = data_chips
    
    def run(self):
        ifp.batch_burn_process(self.port, self.ifpp_uid, self.pipe_set, self.data_buffer, self.data_chips)
    
    

app = QApplication(sys.argv)
gui = ifp_ui()
gui.show()
ifp.display_output = gui.secondary_output
#ifp.response_others = qtpy_gui_response

#gui.browser.contextMenuEvent = my_contextMenuEvent
sys.exit(app.exec_())
