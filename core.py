from PySide import QtCore, QtGui
import logging
import maya.cmds as cmds
import maya.OpenMayaUI as mui
from shiboken import wrapInstance

from pt_RSMultiMatteTool import ui as uic
from pt_RSMultiMatteTool import customWidget
from pt_RSMultiMatteTool import RedShift_engine
from pt_RSMultiMatteTool import Vray_engine

reload(uic)
reload(customWidget)
reload(RedShift_engine)
reload(Vray_engine)
#============================================================

logger = logging.getLogger( __name__ )
logger.addHandler(logging.NullHandler())

def getMayaWindow():
	ptr = mui.MQtUtil.mainWindow()
	if ptr is not  None:
		# ptr = mui.MQtUtil.mainWindow()
		return wrapInstance(long(ptr), QtGui.QMainWindow)

class app_ui(uic.Ui_MainWindow):

	_renderer_ = ''
	_hook_ = None
	_windowName_ = 'maTestWindow'

	def __init__(self):
		if cmds.window( 'MainWindow' , exists = True ):
			cmds.deleteUI( 'MainWindow' )

	def Renderer_comboBox_onChange(self):
		''' change Engine when change Renderer '''
		self._renderer_ = self.Renderer_comboBox.currentText()

		if self._renderer_ == 'Redshift' :
			self._hook_ = RedShift_engine.hook()

		elif self._renderer_ == 'Vray' :
			self._hook_ = Vray_engine.hook()

		else :
			logger.error('Cannot swith engine.' + self._renderer_ )
			cmds.error('Cannot swith engine.')

		logger.info('change Renderer to : ' + self._renderer_)
		self.statusbar.showMessage('App run as ' + self._renderer_ + '.')

		#Refresh all listView
		self.refresh(section='materialID')
		self.refresh(section='objectID')
		self.refresh(section='puzzlematte')

	def retranslateUi(self, retranslateUi ):
		''' inherite  '''

		logger.info( 'Setting up UI...' )

		super(app_ui , self).retranslateUi( retranslateUi )

		#Set renderEngine
		self.Renderer_comboBox_onChange()
		#MainWindow.setWindowTitle(QtGui.QApplication.translate(self._windowName_, self._windowName_, None, QtGui.QApplication.UnicodeUTF8))

		self.MatterialID_listWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
		self.ObjectID_listWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
		#self.PuzzleID_listWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)

		self.ObjectID_Start_LineEdit.setText('100')
		self.ObjectID_Increment_LineEdit.setText('1')
		self.MaterialID_Start_LineEdit.setText('100')
		self.MaterialID_Increment_LineEdit.setText('1')
		self.PuzzleID_Prefix_LineEdit.setText('mm')
		self.PuzzleID_Name_LineEdit.setText('friends')

		self.materialD_refresh.clicked.connect(self.material_refresh_onClick)
		self.Renderer_comboBox.activated.connect(self.Renderer_comboBox_onChange)
		self.SetMaterialID_button.clicked.connect(self.setMaterialIDButton_onclick)
		self.MatterialID_listWidget.itemSelectionChanged.connect(self.MatterialID_listWidget_onChangeSelect)
		self.ObjectID_listWidget.itemSelectionChanged.connect(self.ObjectID_listWidget_onChangeSelect)
		self.ObjectID_SetI_button.clicked.connect(self.ObjectID_SetID_button_onClick)
		self.objectID_refresh_button.clicked.connect(self.objectID_refresh_onClick)
		self.PuzzleID_refresh_button.clicked.connect(self.PuzzleID_refresh_button_onClick)
		self.pushButton_2.clicked.connect(self.createPuzzleAOV_fromSelectionLists_onClick)
		self.PuzzleID_listWidget.itemClicked.connect(self.PuzzleID_listWidget_onSelect)
		self.ObjectID_listWidget.itemClicked.connect(self.ObjectID_listWidget_onItemClick)
		self.MatterialID_listWidget.itemClicked.connect(self.MatterialID_listWidget_onItemSelected)

		#Refresh all listView
		self.refresh(section='materialID')
		self.refresh(section='objectID')
		self.refresh(section='puzzlematte')

		self.statusbar.showMessage('App run as ' + self._renderer_ + '.')

	def refresh (self, section='all'):

		logger.debug('refresh UI section : ' + section)

		if section is 'objectID':
			objectID_List = self._hook_.listObjectID()

			self.ObjectID_listWidget.clear()

			for item in objectID_List:
				setsName	= item
				ObjectID 	= self._hook_.getObjectID( setsName = setsName )
				self.addObjectID_toListView( setsName, ObjectID )


		elif section is 'materialID':
			'''reload material list'''

			material_List = self._hook_.listMaterial()

			self.MatterialID_listWidget.clear()

			for item_num in material_List:
				materialName	= item_num 
				materialID		= self._hook_.getMaterialID( materialName )
				self.addMaterialID_toListView( materialName, materialID )

		elif section is 'puzzlematte':
			
			multiMatte_List = self._hook_.listMultimatte()

			self.PuzzleID_listWidget.clear()

			for item_num in multiMatte_List:
				mmName		= item_num 
				matteID		= self._hook_.getPuzzleMatteID( mmName )
				iconPath 	= self._hook_.getIconPath(mmName)
				self.addPuzzleID_toListView( mmName, matteID['red'], matteID['green'], matteID['blue'] ,iconPath)
		else :
			''' refresh all section '''
			logger.warning('nothing reload : ' + section)

		self.statusbar.showMessage('Refresh '+ section + ' list.')

	def material_refresh_onClick(self):
		''' refresh material list view when click refresh button '''
		self.refresh(section='materialID')

	def objectID_refresh_onClick(self):
		self.refresh(section='objectID')

	def PuzzleID_refresh_button_onClick(self):
		self.refresh(section='puzzlematte')

	def MatterialID_listWidget_onChangeSelect(self):

		self.ObjectID_listWidget.clearSelection()
		return

	def ObjectID_listWidget_onChangeSelect(self):

		self.MatterialID_listWidget.clearSelection()

		selectedList = [self.ObjectID_listWidget.itemWidget(item).text1() for item in self.ObjectID_listWidget.selectedItems()]

		try: self.ObjectID_SetI_button.clicked.disconnect() 
		except Exception: pass

		if len(selectedList) is not 0:
			self.ObjectID_SetI_button.setText('Re-assign Object ID')
			self.ObjectID_SetI_button.clicked.connect(self.ReAssignObjectID_SetID_button_onClick)
		else :
			self.ObjectID_SetI_button.setText('Set object ID to selection')
			self.ObjectID_SetI_button.clicked.connect(self.ObjectID_SetID_button_onClick)

	def PuzzleID_listWidget_onSelect(self):

		selectedList = [self.PuzzleID_listWidget.itemWidget(item).text1() for item in self.PuzzleID_listWidget.selectedItems()]
		print selectedList
		cmds.select(selectedList)
		return

	def ObjectID_SetID_button_onClick(self):
		
		print ('ObjectID_SetID_button_onClick')
		if cmds.ls(sl=True) == [] :
			return

		allID = [ self.ObjectID_listWidget.itemWidget(self.ObjectID_listWidget.item(index)).text2() for index in range(self.ObjectID_listWidget.count())]
		Increment = self.ObjectID_Increment_LineEdit.text()

		try :
			maxIDValue = int(max(allID)) + int(Increment)
		except:
			maxIDValue = int( self.ObjectID_Start_LineEdit.text() )

		try:
			result = self._hook_.createObjectID_sets( maxIDValue )
			self.refresh(section='objectID')
			logger.info('CreateObjID : ' + result)
		except Exception as e:
			logger.error(e)

		self.statusbar.showMessage('Create object ID success.')
		return

	def addMaterialID_toListView(self, materialName, materialID):
		''' add material to materialID listView '''

		mycustomWidget = customWidget.customQWidgetItem()
		mycustomWidget.setText1( str(materialName) )
		mycustomWidget.setText2( str(materialID) )

		mycustomWidget.setTextColor1([240, 240, 240])
		mycustomWidget.setTextColor2([100, 160, 200])

		item = QtGui.QListWidgetItem(self.MatterialID_listWidget)
		item.setSizeHint(mycustomWidget.sizeHint())

		self.MatterialID_listWidget.addItem(item)
		self.MatterialID_listWidget.setItemWidget( item, mycustomWidget )

	def addObjectID_toListView(self, setsName, ObjectID):
		''' add Object to ObjectID listView '''

		mycustomWidget = customWidget.customQWidgetItem()
		mycustomWidget.setText1( str(setsName) )
		mycustomWidget.setText2( str(ObjectID) )

		mycustomWidget.setTextColor1([240, 240, 240])
		mycustomWidget.setTextColor2([100, 160, 200])

		item = QtGui.QListWidgetItem(self.ObjectID_listWidget)
		item.setSizeHint(mycustomWidget.sizeHint())

		self.ObjectID_listWidget.addItem(item)
		self.ObjectID_listWidget.setItemWidget( item, mycustomWidget )

	def addPuzzleID_toListView(self, mmName, red, green ,blue ,iconPath):

		mycustomWidget = customWidget.customQWidgetItem2()
		mycustomWidget.setIcon(iconPath)
		mycustomWidget.setText1( str(mmName) )
		mycustomWidget.setText2( str(red) )
		mycustomWidget.setText3( str(green) )
		mycustomWidget.setText4( str(blue) )

		mycustomWidget.setTextColor1([240, 240, 240])
		mycustomWidget.setTextColor2([200, 100, 100])
		mycustomWidget.setTextColor3([100, 200, 100])
		mycustomWidget.setTextColor4([100, 100, 200])

		item = QtGui.QListWidgetItem(self.PuzzleID_listWidget)
		item.setSizeHint(mycustomWidget.sizeHint())

		self.PuzzleID_listWidget.addItem(item)
		self.PuzzleID_listWidget.setItemWidget( item, mycustomWidget )

	def ObjectID_listWidget_onItemClick(self):
		''' when select item in list do select obj Node '''
		selectedList = [self.ObjectID_listWidget.itemWidget(item).text1() for item in self.ObjectID_listWidget.selectedItems()]
		cmds.select(selectedList,r=True,ne=True)
		return

	def MatterialID_listWidget_onItemSelected(self):
		''' when select item in list do select obj Node '''
		selectedList = [self.MatterialID_listWidget.itemWidget(item).text1() for item in self.MatterialID_listWidget.selectedItems()]
		cmds.select(selectedList,r=True)

	def setMaterialIDButton_onclick(self):
		''' set materialID to selected list '''

		selectedList = [self.MatterialID_listWidget.itemWidget(item).text1() for item in self.MatterialID_listWidget.selectedItems()]

		if len(selectedList) < 1:
			self.statusbar.showMessage( 'Please select material in list!!!' )
			logger.warning( 'Please select material in list!!!' )
			return

		startNum = self.MaterialID_Start_LineEdit.text()
		Increment = self.MaterialID_Increment_LineEdit.text()

		try :
			self._hook_.setMaterialID(selectedList = selectedList, startNum = startNum, increment = Increment)
		except Exception as e :
			logger.error(e)

		self.refresh(section='materialID')
		logger.info('Material ID was assigned.')
		self.statusbar.showMessage('assign Material ID success.')	

	def ReAssignObjectID_SetID_button_onClick(self):

		selectedList = [self.ObjectID_listWidget.itemWidget(item).text1() for item in self.ObjectID_listWidget.selectedItems()]

		if len(selectedList) < 1:
			self.statusbar.showMessage( 'Please select Object in list!!!' )
			logger.warning( 'Please select Object in list!!!' )
			return

		startNum = self.ObjectID_Start_LineEdit.text()
		Increment = self.ObjectID_Increment_LineEdit.text()

		self._hook_.setObjectID(selectedList = selectedList, startNum = startNum, increment = Increment )
		self.refresh(section='objectID')
		self.statusbar.showMessage('re-assign ObjectID success.')

	def createPuzzleAOV_fromSelectionLists_onClick(self):
		''' create puzzle matte from selcted list 
		group by type --> MatterialID and ObjectID '''

		#Material Selction
		selectedList 	= [self.MatterialID_listWidget.itemWidget(item).text1() for item in self.MatterialID_listWidget.selectedItems()]
		matteType 		= 'mat'

		if len(selectedList) < 1:
				#ObjectSelection
				selectedList = [self.ObjectID_listWidget.itemWidget(item).text1() for item in self.ObjectID_listWidget.selectedItems()]
				matteType = 'obj'
				if len(selectedList) < 1 :
					logger.warning('Noting Selected.')
					return

		multimatteName 	= self.PuzzleID_Prefix_LineEdit.text() + '_'+ matteType + '_' + self.PuzzleID_Name_LineEdit.text()

		try :
			self._hook_.setPuzzleMatteID( selectedList, multimatteName, matteType )
			logger.info('Create puzzle matte success.')
			self.statusbar.showMessage('Create puzzle matte success.')

		except Exception as e:
			logger.error(e)

		self.refresh(section='puzzlematte')
		self.statusbar.showMessage('Create Puzzle ID success.')
		return True


if __name__ == '__main__':

	def clear_Logger():
		import logging
		logger = logging.getLogger( )
		for each in logger.handlers[::-1] :
			if type(each).__name__ == 'StreamHandler':
				logger.removeHandler(each)
			
			if type(each).__name__ == 'NullHandler':
				logger.removeHandler(each)

			if type(each).__name__== 'FileHandler': 
				logger.removeHandler(each)
				each.flush()
				each.close()

	clear_Logger()
	MainWindow = QtGui.QMainWindow()
	ui = app_ui()
	ui.setupUi(MainWindow)
	MainWindow.show()