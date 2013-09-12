from collections import OrderedDict

class FolderConf(object):
    '''Simple class holding configuration information for top-level project folders.'''
    
    def __init__(self, name, suburl, label):
        # folder name (example: 'Bookmark Folder')
        self.name = name
        # folder suburl (example: 'resources')
        self.suburl = suburl
        # tab label for this folder page (example: 'Resources')
        self.label = label
        

class FolderManager(object):
    
    def __init__(self):
        
        # dictionary key --> FolderConf instance
        self.TOP_FOLDERS = OrderedDict([ ('RESOURCES', FolderConf('Bookmark Folder','resources','Resources')),      
                                         ('PRESENTATIONS', FolderConf('Presentations','presentations','Presentations')), 
                                         ('PUBLICATIONS', FolderConf('Publications','publications','Publications')),
                                         ('NEWSLETTERS', FolderConf('Newsletters','newsletters','Newsletters')),
                                         ('PROPOSALS', FolderConf('Proposals','proposals','Proposals')),
                                         ('FIGURES', FolderConf('Figures','figures','Figures')),
                                         ('TESTCASES', FolderConf("Test Cases",'testcases','Test Cases')),
                                         ('EVALUATIONS', FolderConf('Evaluations','evaluations','Evaluations'))
                                         ])
                            
        
        # map: folder key --> folder name
        self._key2name = {}
        # map folder key --> folder suburl
        self._key2suburl = {}
        # map folder suburl --> folder name
        self._suburl2name = {}
        # map folder name --> folder suburl
        self._name2suburl = {}
        # map folder name --> folder label
        self._name2label = {}
        # map folder label --> folder name
        self._label2name = {}
        for key, obj in self.TOP_FOLDERS.items():
            self._key2name[key] = obj.name
            self._key2suburl[key] = obj.suburl
            self._suburl2name[obj.suburl] = obj.name
            self._name2suburl[obj.name] = obj.suburl
            self._name2label[obj.name] = obj.label
            self._label2name[obj.label] = obj.name
                    
    def getFolderNames(self):
        '''Returns the names of all top-level folders'''
        return self._key2name.values()
    
    def getFolderName(self, key):
        '''Returns the folder name for a given key'''
        return self._key2name[key]
    
    def getFolderSubUrl(self, key):
        '''Returns the folder suburl for a given key'''
        return self._key2suburl[key]
    
    def getFolderNameFromSubUrl(self, suburl):
        '''Returns the folder name for a given suburl.'''
        return self._suburl2name[suburl]
    
    def getFolderSubUrlFromName(self, name):
        '''Returns the folder suburl for a given name.'''
        return self._name2suburl[name]
    
    def getFolderLabelFromName(self, name):
        '''Returns the folder label for a given name.'''
        return self._name2label[name]
    
    def getFolderNamefromLabel(self, label):
        '''Returns the folder name for a given label.'''
        return self._label2name[label]
    
    def getTopFolderLabels(self):
        return self._name2label.values()
        
# singleton managing folders for the whole application
folderManager = FolderManager()
