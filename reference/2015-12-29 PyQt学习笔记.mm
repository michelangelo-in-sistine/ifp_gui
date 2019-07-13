<map version="0.9.0">
<!-- To view this file, download free mind mapping software FreeMind from http://freemind.sourceforge.net -->
<node CREATED="1451378069293" ID="ID_1819677448" MODIFIED="1451378074708" TEXT="PyQt&#x5b66;&#x4e60;&#x7b14;&#x8bb0;">
<node CREATED="1451378075473" ID="ID_890344455" MODIFIED="1451378077908" POSITION="right" TEXT="&#x57fa;&#x672c;&#x6846;&#x67b6;">
<node CREATED="1451378084962" ID="ID_796682739" MODIFIED="1451378120513" TEXT="1. &#x5efa;&#x7acb;&#x4e00;&#x4e2a;app&#x8fdb;&#x7a0b;&#x5b9e;&#x4f8b;:&#xa;app = QtGui.QApplication(sys.argv)">
<node CREATED="1451378131095" ID="ID_173186587" MODIFIED="1451378149073" TEXT="* app&#x8fdb;&#x7a0b;&#x5b9e;&#x4f8b;&#x7684;&#x521b;&#x7acb;&#x5fc5;&#x987b;&#x5148;&#x4e8e;&#x4e3b;&#x7a97;&#x53e3;&#x5b9e;&#x4f8b;"/>
</node>
<node CREATED="1451378162276" HGAP="28" ID="ID_1733422349" MODIFIED="1451439319216" TEXT="2. &#x5efa;&#x7acb;&#x4e00;&#x4e2a;(&#x6216;&#x591a;&#x4e2a;)&#x7a97;&#x4f53;&#x5b9e;&#x4f8b;:&#xa;class MainWindow(QtGui.QMainWindow):&#xa;    def __init__(self, parent=None):&#xa;        QtGui.QMainWindow.__init__(self)&#xa;&#xa;win = MainWindow()&#xa;win.show()" VSHIFT="12">
<node CREATED="1451378561163" ID="ID_63738695" MODIFIED="1451378584752" TEXT="&#x7b80;&#x5355;&#x7a97;&#x53e3;&#x53ef;&#x4ee5;&#x7ee7;&#x627f;QtGui.QWidget&#x7c7b;"/>
<node CREATED="1451378791379" ID="ID_517523012" MODIFIED="1451378811338" TEXT="&#x7a97;&#x4f53;&#x521d;&#x59cb;&#x5316;&#x77e5;&#x8bc6;&#x70b9;">
<node CREATED="1451378710072" ID="ID_1220243819" MODIFIED="1451378728971" TEXT="&#x8bbe;&#x7f6e;&#x7a97;&#x53e3;&#x5927;&#x5c0f; self.resize()"/>
<node CREATED="1451378729813" ID="ID_1638064672" MODIFIED="1451378755126" TEXT="&#x8bbe;&#x7f6e;&#x7a97;&#x53e3;&#x4f4d;&#x7f6e;, &#x5927;&#x5c0f;: self.setGeometry()"/>
<node CREATED="1451378756000" ID="ID_1299147445" MODIFIED="1451378768500" TEXT="&#x8bbe;&#x7f6e;&#x6807;&#x9898;&#x680f;setWindowTitle()"/>
</node>
<node CREATED="1451378814257" HGAP="22" ID="ID_718027509" MODIFIED="1451439312617" TEXT="&#x7a97;&#x4f53;&#x589e;&#x52a0;&#x63a7;&#x4ef6;" VSHIFT="68">
<node CREATED="1451378608259" ID="ID_230347056" MODIFIED="1451378829847" TEXT="&#x589e;&#x52a0;&#x72b6;&#x6001;&#x680f;:&#xa;__init__()&#x4e2d;&#xa;self.statusBar().showMessage(u&apos;&#x72b6;&#x6001;&#x680f;&#x6587;&#x5b57;&apos;)"/>
<node CREATED="1451378847060" ID="ID_672419240" MODIFIED="1451378914634" TEXT="&#x7a97;&#x4f53;&#x589e;&#x52a0;&#x6309;&#x94ae;:&#xa;button = QtGui.QPushButton(&apos;&#x6309;&#x94ae;&#x6807;&#x9898;&apos;, self)     # &#x7a97;&#x4f53;&#x5185;&#x589e;&#x52a0;&#x4e00;&#x4e2a;&#x6309;&#x94ae;">
<node CREATED="1451378919799" ID="ID_1928055122" MODIFIED="1451378971471" TEXT="&#x589e;&#x52a0;&#x8fde;&#x63a5;&#x4fe1;&#x53f7;&#x4e0e;&#x69fd;:&#xa;self.connect(quit, QtCore.SIGNAL(&apos;clicked()&apos;), QtGui.qApp, QtCore.SLOT(&apos;quit()&apos;))"/>
</node>
<node CREATED="1451378669574" ID="ID_1012311065" MODIFIED="1451381269694" TEXT="&#x7a97;&#x4f53;&#x589e;&#x52a0;&#x83dc;&#x5355;&#x65b9;&#x6cd5;:&#xa;&#x7a97;&#x4f53;__init__&#x65b9;&#x6cd5;&#x91cc;:&#xa;        menubar = self.menuBar()&#xa;        file = menubar.addMenu(&apos;&amp;File&apos;)&#xa;        file.addAction(exit)">
<node CREATED="1451437249986" ID="ID_583165020" MODIFIED="1451441310257" TEXT="&#x5176;&#x4e2d;Action&#x662f;QT&#x7684;&#x62bd;&#x8c61;&#x7528;&#x6237;&#x754c;&#x9762;, &#x53ef;&#x4ee5;&#x653e;&#x7f6e;&#x5728;&#x7a97;&#x53e3;&#x90e8;&#x4ef6;&#x4e2d;. &#x53ef;&#x4ee5;&#x901a;&#x8fc7;&#x83dc;&#x5355;,&#x5de5;&#x5177;&#x680f;&#x6309;&#x94ae;,&#x952e;&#x76d8;&#x5feb;&#x6377;&#x952e;&#x6765;&#x8c03;&#x7528;"/>
</node>
<node CREATED="1451441352464" ID="ID_1377637606" MODIFIED="1451441429070" TEXT="&#x6784;&#x5efa;Action&#x65b9;&#x6cd5;:&#xa;exit = QtGui.QAction(QtGui.QIcon(r&apos;C:\Python27\Lib\site-packages\eric6\icons\default\close.png&apos;), &apos;Exit&apos;, self)&#xa;        &#xa;        exit.setShortcut(&apos;Ctrl+Q&apos;)&#xa;        exit.setStatusTip(&apos;Exit application&apos;)&#xa;        exit.connect(exit, QtCore.SIGNAL(&apos;triggered&apos;), QtGui.qApp, QtCore.SLOT(&apos;quit()&apos;))&#xa;       "/>
<node CREATED="1451443688365" ID="ID_1953767416" MODIFIED="1451443722390" TEXT="&#x589e;&#x52a0;TextEdit&#x63a7;&#x4ef6;:&#xa;    self.textEdit = QtGui.QTextEdit()&#xa;    self.setCentralWidget(self.textEdit)"/>
</node>
<node CREATED="1451553294007" ID="ID_1239431119" MODIFIED="1451553296766" TEXT="&#x5e03;&#x5c40;">
<node CREATED="1451553317556" ID="ID_243925212" MODIFIED="1451553345596" TEXT="&#x7eb5;&#x5411;&#x5e03;&#x5c40;:&#xa;vbox = QtGui.QVBoxLayout()&#xa;&#x6a2a;&#x5411;&#x5e03;&#x5c40;:&#xa;hbox = QtGui.QHBoxLayout()"/>
<node CREATED="1451553348807" ID="ID_1762995125" MODIFIED="1451553380836" TEXT="&#x5e03;&#x5c40;&#x589e;&#x52a0;&#x63a7;&#x4ef6;:&#xa;vbox.addWidget(self.label)&#xa;&#x5e03;&#x5c40;&#x589e;&#x52a0;&#x5f39;&#x7c27;:&#xa;vbox.addStretch(1)"/>
<node CREATED="1451553382473" ID="ID_1219882121" MODIFIED="1451553412258" TEXT="&#x5e03;&#x5c40;&#x5d4c;&#x5957;:&#xa;vbox.addLayout(hbox)"/>
</node>
</node>
<node CREATED="1451378453478" ID="ID_1959176855" MODIFIED="1451378502717" TEXT="3. &#x8fd0;&#x884c;app&#xa;sys.exit(app.exec_())">
<node CREATED="1451378506166" ID="ID_329791856" MODIFIED="1451378538861" TEXT="exec_()&#x8fdb;&#x5165;&#x6d88;&#x606f;&#x5faa;&#x73af;&#xa;&#x4e3b;&#x7a97;&#x4f53;&#x88ab;&#x5173;&#x95ed;&#x65f6;exec_()&#x9000;&#x51fa;"/>
</node>
</node>
<node CREATED="1451455170262" ID="ID_1206549978" MODIFIED="1451455185432" POSITION="right" TEXT="&#x5229;&#x7528;QT Creater&#x521b;&#x5efa;UI&#x754c;&#x9762;">
<node CREATED="1451455189533" ID="ID_886999870" MODIFIED="1451455210596" TEXT="1. &#x5229;&#x7528;&#x5de5;&#x5177;&#x753b;&#x754c;&#x9762;&#x5fc5;&#x987b;&#x5c06;&#x5de5;&#x7a0b;&#x5efa;&#x7acb;&#x4e3a;Project"/>
<node CREATED="1451455212015" ID="ID_1386653562" MODIFIED="1451459590827" TEXT="2. Project_viewer&#x89c6;&#x56fe;&#x91cc;, Forms&#x53f3;&#x952e;&#x65b0;&#x5efa;Form, &#x53cc;&#x51fb;&#x540e;&#x4f1a;&#x8c03;&#x7528;Qt Creator&#x8bbe;&#x8ba1;&#x754c;&#x9762;, &#x8bbe;&#x8ba1;&#x5b8c;&#x6210;&#x540e;&#x751f;&#x6210;&#x4e00;&#x4e2a;.ui&#x6587;&#x4ef6;, &#x70b9;&#x53f3;&#x952e;&#x9009;&#x7f16;&#x8bd1;form, &#x4f1a;&#x751f;&#x6210;&#x4e00;&#x4e2a;py&#x6587;&#x4ef6;, &#x8fd9;&#x4e2a;py&#x6587;&#x4ef6;&#x5c31;&#x662f;&#x7528;python&#x8bed;&#x8a00;, &#x751f;&#x6210;&#x4e00;&#x4e2a;&#x548c;ui&#x6587;&#x4ef6;&#x8bbe;&#x8ba1;&#x4e00;&#x6837;&#x7684;form, &#x6240;&#x6709;&#x7684;&#x8bbe;&#x8ba1;&#x903b;&#x8f91;&#x4e0d;&#x8981;&#x5728;&#x8fd9;&#x4e2a;py&#x6587;&#x4ef6;&#x91cc;&#x6dfb;&#x52a0;, &#x56e0;&#x4e3a;&#x6bcf;&#x6b21;&#x4fee;&#x6539;ui&#x4e4b;&#x540e;&#x91cd;&#x7f16;&#x8bd1;&#x90fd;&#x4f1a;&#x8986;&#x76d6;&#x6389;&#x8fd9;&#x4e2a;&#x6587;&#x4ef6;. &#x8bbe;&#x8ba1;&#x903b;&#x8f91;&#x5e94;&#x8be5;&#x5728;&#x53f3;&#x952e;, Generate Dialog code...&#x91cc;&#x8bbe;&#x8ba1;"/>
</node>
<node CREATED="1451459605112" ID="ID_426757756" MODIFIED="1451459614593" POSITION="right" TEXT="signal_slot&#x673a;&#x5236;">
<node CREATED="1451459615435" ID="ID_1954527892" MODIFIED="1451459668907" TEXT="&#x7b2c;&#x4e00;&#x79cd;&#x529e;&#x6cd5;:&#xa;&#x663e;&#x5f0f;&#x8c03;&#x7528;connect&#x51fd;&#x6570;&#xa;QtCore.QObject.connect(self.pushButton, QtCore.SIGNAL(_fromUtf8(&quot;clicked()&quot;)), self.label.show)&#xa;"/>
<node CREATED="1451459671247" ID="ID_1329334822" MODIFIED="1451459761381" TEXT="&#x7b2c;&#x4e8c;&#x79cd;&#x529e;&#x6cd5;:&#xa;@pyqtSignature(&quot;&quot;)&#x4f5c;&#x4e3a;&#x4fee;&#x9970;&#x7b26;, &#x5b9a;&#x4e49;&#x4e00;&#x4e2a;&#xa;on_&#x63a7;&#x4ef6;&#x540d;_&#x4fe1;&#x53f7;&#x540d;&#x7684;&#x51fd;&#x6570;&#x5373;&#x53ef;&#xa;@pyqtSignature(&quot;&quot;)&#xa;def on_pushButton_clicked(self):&#xa;    self.label.setText(&quot;okay clicked&quot;)">
<node CREATED="1451462739267" ID="ID_683097798" MODIFIED="1451462744444" TEXT="&#x5148;&#x51b3;&#x6761;&#x4ef6;:">
<node CREATED="1451462745862" ID="ID_1972989707" MODIFIED="1451462865330" TEXT="1. &#x63a7;&#x4ef6;&#x540d;&#x5b57;&#x7528;setObjectName&#x65b9;&#x6cd5;&#x547d;&#x540d;:&#xa;self.ok.setObjectName(&quot;ok&quot;)"/>
<node CREATED="1451462768877" ID="ID_742357970" MODIFIED="1451462824244" TEXT="2. &#x901a;&#x77e5;QtCore&#x4f7f;&#x7528;&#x540d;&#x5b57;&#x8fde;&#x63a5;&#x69fd;:&#xa;__init__():&#xa;    ...&#xa;     QtCore.QMetaObject.connectSlotsByName(self)"/>
</node>
</node>
</node>
<node CREATED="1451378587324" ID="ID_1047242682" MODIFIED="1451378592762" POSITION="right" TEXT="&#x5176;&#x4ed6;&#x77e5;&#x8bc6;&#x70b9;">
<node CREATED="1451378649380" ID="ID_385580442" MODIFIED="1451378667905" TEXT="&#x83dc;&#x5355;,&#x72b6;&#x6001;&#x680f;&#x7684;unicode&#x6587;&#x5b57;&#x8868;&#x793a;&#x6cd5;: u&apos;&#x6c49;&#x5b57;&apos;"/>
<node CREATED="1453445666385" ID="ID_1382246531" MODIFIED="1453445693458" TEXT="&#x7b2c;&#x4e00;&#x884c; &#x8868;&#x793a;&#x6587;&#x672c;&#x7684;&#x7f16;&#x7801;&#xa;# -*- coding: utf-8 -*-"/>
</node>
</node>
</map>
