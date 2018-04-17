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
		materialID = 0
		materialSG = cmds.listConnections( materialName + '.outColor')

		if materialSG :

			materialSG = materialSG[0]

			if cmds.objExists(materialSG+'.rsMaterialId'): 
				materialID = cmds.getAttr(materialSG+'.rsMaterialId')

			return materialID

		else :
			logger.warning("Unassign shader : " + materialName)
			return 0

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

	def createObjectID_sets(self, ID, newName):
		''' create redshift object ID node and add selection to sets '''

		nodeName = mm.eval("redshiftCreateObjectIdNode();")
		cmds.setAttr(nodeName+'.objectId', ID)
		cmds.rename(nodeName,newName)
		return nodeName

	def setObjectID(self, selectedList, startNum, increment, newName):
		
		count  = int(startNum)
		increment = int(increment)

		for objectSets in selectedList:

			cmds.setAttr(objectSets+'.objectId',count)
			cmds.rename(objectSets, newName)
			count += increment

	def listMultimatte(self):
		''' list all node 'RedshiftAOV' and type is 'Puzzle Matte' '''
		result = []

		allAOV = cmds.ls(type='RedshiftAOV')
		for item in allAOV:
			if cmds.getAttr(item+'.aovType') == 'Puzzle Matte':
				result.append(item)

		return result

	def listProxy(self):
		allRsProxy = cmds.ls(type='RedshiftProxyMesh')
		return allRsProxy

	def getProxyObjID(self, proxyNodeName):
		shapeNode = cmds.listConnections( proxyNodeName + '.outMesh', sh=True )
		if shapeNode: 
			shapeNode = shapeNode[0]
			result 	  = cmds.getAttr( shapeNode + '.rsObjectId' )
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

		if str(idType) is '1' :
			iconPath = os.path.dirname(moduleFile) + '/icon/redshiftObjectId.png'
		else :
			iconPath = os.path.dirname(moduleFile) + '/icon/redshiftMaterialId.png'

		return iconPath

	def setProxyID(self, selectedList, newName, startNum, increment, OverrideStage):
		''' set material ID to slected lists '''
		count  = int(startNum)
		increment = int(increment)

		for proxy in selectedList :
			shapeNode = cmds.listConnections( proxy + '.outMesh', sh=True )[0]
			cmds.setAttr( shapeNode + '.rsObjectId', count)

			# skip to rename if node is reference
			if not cmds.referenceQuery(proxy, inr=True):

				try :
					name = cmds.rename(proxy,newName)
					cmds.rename(shapeNode,'Shape_'+name)
				except :
					# Error if node is from Scene assembly
					name = proxy

			else : 
				logger.warning(proxy + " : is reference node skipped.")
				name = proxy

			if OverrideStage :
				cmds.setAttr( name + '.objectIdMode', 1)
			else :
				cmds.setAttr( name + '.objectIdMode', 0)

			count += increment



	def setPuzzleMatteID(self, selectedList, multimatteName, matteType):
		''' create puzzle matte from selcted list 
		group by type --> MatterialID and ObjectID '''

		allID=[]

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

			elif matteType == 'obj' :
				ID = self.getObjectID(item)

			else :
				PxshapeNode = cmds.listConnections( item + '.outMesh', sh=True )[0]
				ID = cmds.getAttr(PxshapeNode + '.rsObjectId')

			#QUERY PROXY ID HERE!!!!!!!
			# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

			# Pass duplicate ID
			if ID in allID :
				continue

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

			allID.append(ID)

		try:
			mm.eval('redshiftUpdateActiveAovList;')
		except :
			pass
			
		return True
		