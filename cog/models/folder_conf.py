# dictionary that associates each top-level folder name to its suburl
TOP_FOLDERS = { 
               'Bookmark Folder':'resources',
               'Presentations':'presentations', 
               'Publications':'publications', 
               'Newsletters':'newsletters', 
               'Proposals':'proposals', 
               'Figures':'figures', 
               'Test Cases':'testcases', 
               'Evaluations':'evaluations',
              }

class FolderManager(object):
    
    def __init__(self):
        
        # map: folder name --> folder suburl
        self._map = TOP_FOLDERS
        
        # map folder suburl --> folder name
        self._invmap = {}
        for key, value in self._map.items():
            self._invmap[value] = key
            
    def getNames(self):
        '''Returns the names of all top-level folders'''
        return self._map.keys()
    
    def getName(self, suburl):
        '''Returns the name of the folder with a given suburl'''
        return self._invmap[suburl]
    
    def getSubUrl(self, name):
        '''Returns the suburl of the folder with a given name'''
        return self._map[name]
        
# singleton managing folders for the whole application
folderManager = FolderManager()
