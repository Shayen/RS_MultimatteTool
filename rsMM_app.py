#Version 1.2Release
import os,sys
from PySide import QtCore, QtGui
import maya.cmds as cmds
import maya.OpenMayaUI as mui
from shiboken import wrapInstance

try :
	import ui
	import core
	import customWidget 
	import RedShift_engine
	import Vray_engine
	
except :

	try:
		modulepath = '/'.join( sys.modules[__name__].__file__.replace('\\',"/").split('/')[:-2] )
	except :
		modulepath = '/'.join( os.path.dirname(__file__).replace('\\\\',"/").split('/')[:-1] )

	if modulepath not in sys.path :
		sys.path.append( modulepath )
		print ('append : ' + modulepath)
	else :
		print ("path is already in sys.path but not load Module.")

	print modulepath
	import ui
	import core
	import customWidget 
	import RedShift_engine
	import Vray_engine

reload(ui)
reload(core)

#===================== LOGGING TEMPLATE =====================

from datetime import date
import logging
logger = logging.getLogger( )

#                 DELETE EXISTSED HANDLER

for each in logger.handlers[::-1] :
	if type(each).__name__ == 'StreamHandler':
		logger.removeHandler(each)

	if type(each).__name__ == 'NullHandler':
		logger.removeHandler(each)

	if type(each).__name__== 'FileHandler': 
		logger.removeHandler(each)
		each.flush()
		each.close()

#              ------------------------------

if not os.path.isdir( os.path.dirname(__file__)+'/log' ) :
	os.mkdir( os.path.dirname(__file__)+'/log' )

ex_file = os.listdir( os.path.dirname(__file__) + '/log' )

#-------------------------------------------------------------

log_filename = str(date.today()) + '.log'
logfile_path = os.path.dirname(__file__)+'/log' + '/' + log_filename


fh = logging.FileHandler( logfile_path )
formatter = logging.Formatter('%(asctime)s - %(name)s - %(lineno)d - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)

logger.setLevel(logging.INFO)

#-------------------------------------------------------------

logger.info('===================== # App start # =====================')

#-------------------------------------------------------------
_version_ = '1.2Release'
_windowName_ = 'Redshift Multimatte V'+_version_

if cmds.window( 'MainWindow' , exists = True ):
	cmds.deleteUI( 'MainWindow' )

def getMayaWindow():
    ptr = mui.MQtUtil.mainWindow()
    if ptr is not  None:
        # ptr = mui.MQtUtil.mainWindow()
        return wrapInstance(long(ptr), QtGui.QMainWindow)

class myWindow(QtGui.QMainWindow):

		def __init__(self, parent=None):
			super(myWindow, self).__init__(parent)


MainWindow = myWindow( getMayaWindow() )
ui = core.app_ui( )
ui._windowName_ = _windowName_
ui.setupUi(MainWindow)
MainWindow.show()
MainWindow.setWindowTitle( _windowName_ )

logger.info('UI loaded ...')

