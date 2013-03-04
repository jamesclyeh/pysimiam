#!/usr/bin/python
#QtSimiam
#Author: Tim Fuchs
#Description: This is the top-level application for QtSimiam.
import sys
sys.path.insert(0, './scripts')
from PyQt4 import QtGui, QtCore
import os
from qtrenderer import QtRenderer
from dockwindow import ParamDock, DockManager

import simulator as sim
import Queue as queue
from traceback import format_exception

class PlayPauseAction(QtGui.QAction):
    def __init__(self, parent, run_slot, pause_slot):
        QtGui.QAction.__init__(self, parent)
        self.playset = (QtGui.QIcon.fromTheme("media-playback-start",
                            QtGui.QIcon("./res/image/arrow-right.png")),
                        "Run",
                        run_slot,
                        "Run simulation")
        self.pauseset = (QtGui.QIcon.fromTheme("media-playback-pause",
                            QtGui.QIcon("./res/image/media-playback-pause-7.png")),
                         "Pause",
                         pause_slot,
                         "Pause simulation")
        self.triggered.connect(self.__on_click)
        self.reset()
        
    def __on_click(self):
        self.callback()
        self.set_state()

    def reset(self):
        self.click_to_run = False
        self.set_state(self.playset)
        
    def set_state(self, actset = None):
        if actset is None:
            if self.click_to_run:
                actset = self.pauseset
            else:
                actset = self.playset
        self.click_to_run = not self.click_to_run
        self.setIcon(actset[0])
        self.setText(actset[1])
        self.callback = actset[2]
        self.setStatusTip(actset[3])

class SimulationWidget(QtGui.QMainWindow):
    def __init__(self,parent=None):
        QtGui.QMainWindow.__init__(self,parent)
        self.setWindowTitle("QtSimiam")
        self.setWindowIcon(QtGui.QIcon("./res/image/appicon.png"))
        self.resize(700,700)
        
        self.create_actions()
        self.create_toolbars()
        self.create_menu()
        self.create_statusbar()
        # Set intro message
        self.status_label.setText("Welcome to QtSimiam")
        
        # create XML file dialog
        self.world_dialog = QtGui.QFileDialog(self,
                                "Select World File",
                                "worlds", 
                                "WorldFile (*.xml)")
        self.world_dialog.setAcceptMode(QtGui.QFileDialog.AcceptOpen)
        self.world_dialog.setFileMode(QtGui.QFileDialog.ExistingFile)     

        # create supervisor file dialog
        self.supervisor_dialog = QtGui.QFileDialog(self,
                                     "Select Supervisor File",
                                     "supervisors", 
                                     "Supervisor (*.py)")
        self.supervisor_dialog.setAcceptMode(QtGui.QFileDialog.AcceptOpen)
        self.supervisor_dialog.setFileMode(QtGui.QFileDialog.ExistingFile)     
        
        scrollArea = QtGui.QScrollArea(self)
        self.setCentralWidget(scrollArea)
        self.viewer = SimulatorViewer()
        scrollArea.setWidget(self.viewer)
        scrollArea.setWidgetResizable(True)

        #self.setDockOptions(QtGui.QMainWindow.AllowNestedDocks)
        self.setDockOptions(QtGui.QMainWindow.DockOptions())

        self.sim_timer = QtCore.QTimer(self)
        self.sim_timer.setInterval(10)
        self.sim_timer.timeout.connect(self.update_time)
        
        self.sim_queue = queue.Queue()
        
        # create the simulator thread
        self.simulator_thread = sim.Simulator(self.viewer.renderer,
                                               self.sim_queue)

        self.in_queue = self.simulator_thread._out_queue
                                               
        self.dockmanager = DockManager(self)
        self.dockmanager.apply_request.connect(self.apply_parameters)

        self.simulator_thread.start()
        self.sim_timer.start()

    def create_actions(self):
        
        self.open_world_action = \
            QtGui.QAction(QtGui.QIcon.fromTheme("document-open",
                            QtGui.QIcon("./res/image/open.png")),
                          "Open XML &World",
                          self)
        self.open_world_action.triggered.connect(self.on_open_world)
        self.open_world_action.setShortcut(QtGui.QKeySequence(QtGui.QKeySequence.Open))

        self.open_world_action.setStatusTip("Open a new simulation")
                            
        self.exit_action = \
            QtGui.QAction(QtGui.QIcon.fromTheme("application-exit"),
                    "E&xit",
                    self)
        self.exit_action.triggered.connect(self.close)
        self.exit_action.setShortcut(QtGui.QKeySequence(QtGui.QKeySequence.Quit))
        self.exit_action.setToolTip("Quit the Program")
        self.exit_action.setStatusTip("Exit QtSimiam")
        
        self.rev_action = \
            QtGui.QAction(QtGui.QIcon.fromTheme("media-seek-backward",
                            QtGui.QIcon("./res/image/arrow-left-double.png")),
                          "Rewind", self)
        self.rev_action.triggered.connect(self.on_rewind)
        self.rev_action.setStatusTip("Reset simulation")
        
        self.run_action = PlayPauseAction(self, self.on_run,self.on_pause)        
        self.run_action.setEnabled(False)

        self.grid_action = \
            QtGui.QAction(QtGui.QIcon("./res/image/grid.png"),
                          "Show/Hide grid", self)
        self.grid_action.setStatusTip("Show/hide grid")
        self.grid_action.triggered[bool].connect(self.show_grid)
        self.grid_action.setCheckable(True)
        self.grid_action.setChecked(False)

        self.sens_action = \
            QtGui.QAction(QtGui.QIcon("./res/image/robot-sensors.png"),
                          "Show/Hide sensors", self)
        self.sens_action.setStatusTip("Show/hide robot sensors")
        self.sens_action.triggered[bool].connect(self.show_sensors)
        self.sens_action.setCheckable(True)
        self.sens_action.setChecked(True)

        self.trace_action = \
            QtGui.QAction(QtGui.QIcon("./res/image/robot-tracks.png"),
                          "Show/Hide robot trajectores", self)
        self.trace_action.setStatusTip("Show/hide robot trajectores")
        self.trace_action.triggered[bool].connect(self.show_tracks)
        self.trace_action.setCheckable(True)
        self.trace_action.setChecked(True)

        zoom_group = QtGui.QActionGroup(self)

        self.zoom_world_action = \
            QtGui.QAction(QtGui.QIcon("./res/image/zoom-scene.png"),
                          "Show all", self)
        self.zoom_world_action.triggered.connect(self.zoom_scene)
        self.zoom_world_action.setStatusTip("Show the whole world in view")
        self.zoom_world_action.setCheckable(True)
        self.zoom_world_action.setChecked(True)
        zoom_group.addAction(self.zoom_world_action)
        
        self.zoom_robot_action = \
            QtGui.QAction(QtGui.QIcon("./res/image/zoom-robot.png"),
                          "Follow robot", self)
        self.zoom_robot_action.triggered.connect(self.zoom_robot)
        self.zoom_robot_action.setStatusTip("Center the view on robot")
        self.zoom_robot_action.setCheckable(True)
        self.zoom_robot_action.setChecked(False)
        zoom_group.addAction(self.zoom_robot_action)

        self.rotate_action = \
            QtGui.QAction(QtGui.QIcon("./res/image/zoom-robot-rot.png"),
                          "Follow robot orientation", self)
        self.rotate_action.triggered.connect(self.rot_robot)
        self.rotate_action.setStatusTip("Rotate the view with the robot")
        self.rotate_action.setCheckable(True)
        self.rotate_action.setChecked(False)
        self.rotate_action.setEnabled(False)
        
        self.about_action = \
            QtGui.QAction(QtGui.QIcon.fromTheme("help-about",
                            self.windowIcon()),
                          "About",self)
        self.about_action.setStatusTip("About QtSimiam")
        self.about_action.triggered.connect(self.about)
        
    def create_toolbars(self):
        
        tbar = QtGui.QToolBar("Control",self)
        tbar.setAllowedAreas(QtCore.Qt.TopToolBarArea | QtCore.Qt.BottomToolBarArea)
        
        tbar.addAction(self.open_world_action)
        tbar.addSeparator()
        
        tbar.addAction(self.rev_action)
        tbar.addAction(self.run_action)
        
        self.speed_slider = QtGui.QSlider(QtCore.Qt.Horizontal,self)
        self.speed_slider.setToolTip("Adjust speed")
        self.speed_slider.setStatusTip("Adjust simulation speed")
        self.speed_slider.setTickPosition(QtGui.QSlider.NoTicks)
        self.speed_slider.setMaximumWidth(300)
        self.speed_slider.setRange(-100,100)
        self.speed_slider.setValue(0)
        self.speed_slider.setEnabled(False)
        self.speed_slider.valueChanged[int].connect(self.scale_time)
        tbar.addWidget(self.speed_slider)
        
        self.speed_label = QtGui.QLabel(" Speed: 1.0x ",self)
        self.speed_label.setToolTip("Current speed multiplier")
        tbar.addWidget(self.speed_label)
                       
        self.addToolBar(tbar)

        tbar = QtGui.QToolBar("View",self)
        tbar.setAllowedAreas(QtCore.Qt.TopToolBarArea | QtCore.Qt.BottomToolBarArea)

        tbar.addAction(self.grid_action)        
        tbar.addAction(self.sens_action)
        tbar.addAction(self.trace_action)
        tbar.addSeparator()
        
        tbar.addAction(self.zoom_world_action)
        tbar.addAction(self.zoom_robot_action)
        tbar.addAction(self.rotate_action)
        
        self.zoom_slider = QtGui.QSlider(QtCore.Qt.Horizontal,self)
        self.zoom_slider.setTickPosition(QtGui.QSlider.NoTicks)
        self.zoom_slider.setToolTip("Adjust zoom")
        self.zoom_slider.setStatusTip("Zoom in/out on robot")
        self.zoom_slider.setMaximumWidth(300)
        self.zoom_slider.setRange(-100,100)
        self.zoom_slider.setValue(0)
        self.zoom_slider.setEnabled(False)
        self.zoom_slider.valueChanged[int].connect(self.scale_zoom)
        tbar.addWidget(self.zoom_slider)
        self.zoom_label = QtGui.QLabel(" Zoom: 1.0x ",self)
        self.zoom_label.setToolTip("Current zoom factor")
        tbar.addWidget(self.zoom_label)
        
        self.zoom_factor = 0
                       
        self.addToolBar(tbar)

    def create_menu(self):
        menu = QtGui.QMenuBar(self)
        self.setMenuBar(menu)
        
        file_menu = menu.addMenu("&File")
        
        file_menu.addAction(self.open_world_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)
        
        view_menu = menu.addMenu("&View")
        
        view_menu.addAction(self.zoom_world_action)
        view_menu.addAction(self.zoom_robot_action)
        view_menu.addAction(self.rotate_action)
        view_menu.addSeparator()
        
        view_menu.addAction(self.grid_action)
        view_menu.addAction(self.sens_action)
        view_menu.addAction(self.trace_action)
        
        run_menu = menu.addMenu("&Simulation")
        
        run_menu.addAction(self.run_action)
        run_menu.addAction(self.rev_action)
        
        help_menu = menu.addMenu("&Help")
        help_menu.addAction(self.about_action)
        
    def create_statusbar(self):      
        self.setStatusBar(QtGui.QStatusBar())
        self.status_label = QtGui.QLabel("",self.statusBar())
        self.statusBar().addWidget(self.status_label)

    def closeEvent(self,event):
        self.sim_timer.stop()
        self.sim_queue.put(('stop',()))
        while self.simulator_thread.isAlive():
            self.process_events(True)
            self.simulator_thread.join(0.1)
        super(SimulationWidget,self).closeEvent(event)

    def load_world(self,filename):
        self.run_action.setEnabled(False)
        if not os.path.exists(filename):
            filename = os.path.join('worlds',filename)
            if not os.path.exists(filename):
                print "Cannot open file {}".format(filename)
                return
        self.dockmanager.clear()
        self.sim_queue.put(('read_config',(filename,)))

    # Slots
    def about(self):
        QtGui.QMessageBox.about(self,"About QtSimiam",
        """<b>PySimiam (Qt)</b><br>
        Robot simulator<br>
        &copy; Pysimiam Team
        """)
    
    @QtCore.pyqtSlot()
    def on_rewind(self): # Start from the beginning
        self.speed_slider.setEnabled(False)
        #self.time_label.setText("00:00.0")
        self.sim_queue.put(('reset_simulation',()))

    @QtCore.pyqtSlot()
    def on_run(self): # Run/unpause
        self.sim_queue.put(('start_simulation',()))

    @QtCore.pyqtSlot()
    def on_pause(self): # Pause
        self.speed_slider.setEnabled(False)        
        self.sim_queue.put(('pause_simulation',()))

    @QtCore.pyqtSlot()
    def on_open_world(self):
        self.on_pause()
        if self.world_dialog.exec_():
            self.load_world(self.world_dialog.selectedFiles()[0])
            
    @QtCore.pyqtSlot(bool)
    def show_grid(self,show):
        self.sim_queue.put(('show_grid',(show,)))

    @QtCore.pyqtSlot(bool)
    def show_sensors(self,show):
        self.sim_queue.put(('show_sensors',(show,)))
            
    @QtCore.pyqtSlot(bool)
    def show_tracks(self,show):
        self.sim_queue.put(('show_tracks',(show,)))
            
    @QtCore.pyqtSlot()
    def zoom_scene(self):
        self.zoom_slider.setEnabled(False)
        self.rotate_action.setEnabled(False)
        self.sim_queue.put(('focus_on_world',()))

    @QtCore.pyqtSlot()
    def zoom_robot(self):
        self.zoom_slider.setEnabled(True)
        self.rotate_action.setEnabled(True)
        self.sim_queue.put(('focus_on_robot',(self.rotate_action.isChecked(),)))
        self.sim_queue.put(('adjust_zoom',(5.0**(self.zoom_slider.value()/100.0),)))

    @QtCore.pyqtSlot()
    def rot_robot(self):
        self.sim_queue.put(('focus_on_robot',(self.rotate_action.isChecked(),)))
            
    @QtCore.pyqtSlot(int)
    def scale_zoom(self,value):
        zoom = 5.0**(value/100.0)
        self.sim_queue.put(('adjust_zoom',(zoom,)))
        self.zoom_label.setText(" Zoom: %.1fx "%(zoom))

    @QtCore.pyqtSlot(int)
    def scale_time(self,value):
        m = 10.0**((value-self.zoom_factor)/100.0)
        self.sim_queue.put(('set_time_multiplier',(m,)))
        self.speed_label.setText(" Speed: %.1fx "%m)

    @QtCore.pyqtSlot()
    def update_time(self):
        if self.simulator_thread.is_running():
            t = self.simulator_thread.get_time()
            minutes = int(t//60)
            #self.time_label.setText("%02d:%04.1f"%(minutes,t - minutes*60))
            self.status_label.setText(
                "Simulation running... {:02d}:{:04.1f}".format(minutes,t - minutes*60))
        self.process_events(True)
    
    def process_events(self, process_all = False):
        while not self.in_queue.empty():
            tpl = self.in_queue.get()
            if isinstance(tpl,tuple) and len(tpl) == 2:
                name, args = tpl
                # Scramble
                name = "simulator_{}".format(name)
                if name in self.__class__.__dict__:
                    try:
                        self.__class__.__dict__[name](self,*args)
                    except TypeError:
                        print "Wrong UI event parameters {}{}".format(name,args)
                        raise
                else:
                    print "Unknown UI event '{}'".format(name)
            else:
                print "Wrong UI event format '{}'".format(tpl)
            self.in_queue.task_done()
            if not process_all:
                return
    
    def apply_parameters(self, robot_id, params):
        self.sim_queue.put(('apply_parameters', (robot_id, params)))
            
### Simulator events

    def simulator_make_param_window(self,robot_id,name,parameters):       
        # FIXME adding to the right for no reason
        self.dockmanager.add_dock_right(robot_id, name, parameters)
        
    def simulator_running(self):
        self.speed_slider.setEnabled(True)
    
    def simulator_paused(self):
        self.speed_slider.setEnabled(False)
        t = self.simulator_thread.get_time()
        minutes = int(t//60)
        self.status_label.setText(
            "Simulation paused... {:02d}:{:04.1f}".format(minutes,t - minutes*60))

    def simulator_reset(self):
        self.run_action.reset()
        self.run_action.setEnabled(True)
        self.status_label.setText("Simulation ready")

    def simulator_stopped(self):
        # FIXME this function isn't necessary
        self.speed_slider.setEnabled(False)
        
    def simulator_update_view(self):
        self.viewer.update_bitmap()
        
    def simulator_exception(self,e_type, e_value, e_traceback):
        QtGui.QMessageBox.critical(self,"{}: {}".format(e_type.__name__,e_value),"\n".join(format_exception(e_type,e_value,e_traceback)))
        self.run_action.setEnabled(False)
            
#end QtSimiamFrame class

class SimulatorViewer(QtGui.QFrame):
    def __init__(self, parent = None):
        super(SimulatorViewer, self).__init__(parent)
        self.bitmap = QtGui.QPixmap()
        self.blt_bitmap = QtGui.QImage(self.size(), QtGui.QImage.Format_ARGB32)
        self.renderer = QtRenderer(self.blt_bitmap)
        self.resize_on_paint = False
        # code for async calling of update
        self.update_ = self.metaObject().method(self.metaObject().indexOfMethod('update()'))

    def paintEvent(self, event):
        super(SimulatorViewer, self).paintEvent(event)
        painter = QtGui.QPainter(self)
        painter.fillRect(self.rect(),QtCore.Qt.white)
        s = self.bitmap.rect().size()
        s.scale(self.rect().size(),QtCore.Qt.KeepAspectRatio)
        dx = (self.width() - s.width())/2
        dy = (self.height() - s.height())/2
        painter.drawPixmap(QtCore.QRect(QtCore.QPoint(dx,dy),s),self.bitmap,self.bitmap.rect())
        
    def update_bitmap(self):
        self.bitmap = QtGui.QPixmap.fromImage(self.blt_bitmap)
        # resize the canvas - at this point nothing is being drawn
        if self.resize_on_paint:
            self.blt_bitmap = QtGui.QImage(self.width(),
                                            self.height(),
                                            QtGui.QImage.Format_ARGB32)
            self.renderer.set_canvas(self.blt_bitmap)          
            self.resize_on_paint = False
        self.update()

    def resizeEvent(self,event):
        """Resize panel and canvas"""
        # use cached size and flag
        self.resize_on_paint = True

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    simWidget = SimulationWidget()
    simWidget.show()
    if len(sys.argv) > 1:
        if len(sys.argv) == 2:
            simWidget.load_world(sys.argv[1])
        else:
            print "Too many command-line options"
    app.exec_()
