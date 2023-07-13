      
import os,sys,re,json

from cumulusci.tasks.sfdx import SFDXBaseTask

class PreCommit(SFDXBaseTask):
    task_options = {
    }
    
    def _init_options(self, kwargs):
        super(PreCommit, self)._init_options(kwargs)
        
    def _run_task(self):
        ignoredirs=['./cci','./.cci','./config','./.config/sfdx','./.git','./.git/objects','./.qbrix','./qbrix','./.vscode','./.sfdx']
        ignorefiles=['.DS_Store','.forceignore','.lock','.prettierignore']
        rootdir = "."
        pattern = re.compile("AIza[0-9A-Za-z-_]{35}")
        results=[]
        for subdir, dirs, files in os.walk(rootdir):
            for file in files:
                continuepprocessing=True
                for ign in ignoredirs:
                    if ign in subdir:
                        continuepprocessing=False
                        
                for ign in ignorefiles:
                    if ign in file:
                        continuepprocessing=False
                
                if(continuepprocessing):        
                    filepath = subdir + os.sep + file
                    #print(subdir)
                    try:
                        for i, line in enumerate(open(filepath)):
                            for match in re.finditer(pattern, line):
                                results.append(filepath)
                    except UnicodeDecodeError:
                        pass
                        
        if(len(results)>0):
            self.logger.error(f'*********************************************************************************')
            self.logger.error(f'*****COMMIT BLOCKED Possible Key(s) Google API Keys found in these files:********')
            self.logger.error(f'*********************************************************************************')
            for file in results:
                self.logger.error(file)
            sys.exit(os.EX_DATAERR)