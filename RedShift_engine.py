import logging
import os,sys

import maya.cmds as cmds
import maya.mel as mm

logger = logging.getLogger( __name__ )
logger.addHandler(logging.NullHandler())

class hook (object):

	def __init__(self):
		''' init '''
		pass

	def listMaterial(self):
		''' list all material '''

		materialArchi_List = cmds.ls(type='RedshiftArchitectural')
		materialrsMatte_List = cmds.ls(type='RedshiftMaterial')
		material_List = materialArchi_List + materialrsMatte_List

		return material_List

	def getMaterialID(self, materialName):
		''' get material ID from name '''
		materialSG = cmds.listConnections( materialName + '.outColor')[0]
		materialID = cmds.getAttr(materialSG+'.rsMaterialId')

		return materialID

	def setMaterialID(self,selectedList, startNum, increment):
		''' set material ID to slected lists '''
		count  = int(startNum)
		increment = int(increment)

		for material in selectedList :
			materialSG = cmds.listConnections( material + '.outColor')[0]
			cmds.setAttr(materialSG + '.rsMaterialId', count)
			count += increment

			#print startNum, increment

	def listObjectID(self):
		''' list all redshift object ID node '''
		ObjectID_list = cmds.ls(type='RedshiftObjectId')
		return ObjectID_list

	def getObjectID(self, setsName):
		objectID = cmds.getAttr(setsName+'.objectId')
		return objectID

	def createObjectID_sets(self, ID):
		''' create redshift object ID node and add selection to sets '''

		nodeName = mm.eval("redshiftCreateObjectIdNode();")
		cmds.setAttr(nodeName+'.objectId', ID)
		return nodeName

	def setObjectID(self, selectedList, startNum, increment):
		
		count  = int(startNum)
		increment = int(increment)

		for objectSets in selectedList:
			#print ('set ' + objectSets + ' : ' + str(count))
			cmds.setAttr(objectSets+'.objectId',count)
			count += increment

	def listMultimatte(self):
		''' list all node 'RedshiftAOV' and type is 'Puzzle Matte' '''
		result = []

		allAOV = cmds.ls(type='RedshiftAOV')
		for item in allAOV:
			if cmds.getAttr(item+'.aovType') == 'Puzzle Matte':
				result.append(item)

		return result

	def getPuzzleMatteID(self, AOV_nodeName):
		result = {'red':'','green':'','blue':''}

		result['red'] 	= cmds.getAttr(AOV_nodeName+'.redId')
		result['green'] = cmds.getAttr(AOV_nodeName+'.greenId')
		result['blue'] 	= cmds.getAttr(AOV_nodeName+'.blueId')

		return result

	def getIconPath (self, mmName):

		moduleFile = sys.modules[__name__].__file__
		idType = cmds.getAttr(mmName+'.mode')

		print idType
		print type(idType)

		if str(idType) is '1' :
			iconPath = os.path.dirname(moduleFile) + '/icon/redshiftObjectId.png'
		else :
			iconPath = os.path.dirname(moduleFile) + '/icon/redshiftMaterialId.png'

		return iconPath

	def setPuzzleMatteID(self, selectedList, multimatteName, matteType):
		''' create puzzle matte from selcted list 
		group by type --> MatterialID and ObjectID '''

		nodeName = mm.eval('rsCreateAov -type "Puzzle Matte";')
		nodeName = cmds.rename(nodeName, multimatteName)

		cmds.setAttr(nodeName+'.name',nodeName,type='string')

		if matteType == 'mat' :
			cmds.setAttr(nodeName+'.mode', 0)
		else :
			cmds.setAttr(nodeName+'.mode', 1)

		count = 0
		for item in selectedList:
			print item
			#Query ID of node
			if matteType == 'mat' :
				ID = self.getMaterialID(item)

			else :
				ID = self.getObjectID(item)

			#Assign ID to PuzzleMatte
			if count == 3 :
				count = 0
				nodeName = mm.eval('rsCreateAov -type "Puzzle Matte";')
				nodeName = cmds.rename(nodeName, multimatteName)
				cmds.setAttr(nodeName+'.name',nodeName,type='string')
				
				if matteType == 'mat' :
					cmds.setAttr(nodeName+'.mode', 0)
				else :
					cmds.setAttr(nodeName+'.mode', 1)

			try : 
				if count == 0 :
					cmds.setAttr(nodeName +'.redId', ID)

				elif count == 1 :
					cmds.setAttr(nodeName+'.greenId', ID)

				elif count == 2 :
					cmds.setAttr(nodeName+'.blueId', ID)

				else :
					logger.error('Count error.')

				count += 1
			except Exception as e:
				logger.error(e)
		try:
			mm.eval('redshiftUpdateActiveAovList;')
		except :
			pass
			
		return True
		