# dictionary that associates each key with a tuple of the form (folder_name, folder_suburl)
TOP_FOLDERS = { 
               'RESOURCES': ('Bookmark Folder','resources'),
               'PRESENTATIONS': ('Presentations','presentations'), 
               'PUBLICATIONS': ('Publications','publications'),
               'NEWSLETTERS': ('Newsletters','newsletters'),
               'PROPOSALS': ('Proposals','proposals'),
               'FIGURES': ('Figures','figures'),
               'TESTCASES': ("Test Cases",'testcases'),
               'EVALUATIONS': ('Evaluations','evaluations'),
              }

class FolderManager(object):
    
    def __init__(self):
        
        # map: folder key --> folder name
        self._key2name = {}
        # map folder key --> folder suburl
        self._key2suburl = {}
        # map folder suburl --> folder name
        self._suburl2name = {}
        for key, tuple in TOP_FOLDERS.items():
            self._key2name[key] = tuple[0]
            self._key2suburl[key] = tuple[1]
            self._suburl2name[tuple[1]] = tuple[0]
                    
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
        
# singleton managing folders for the whole application
folderManager = FolderManager()
