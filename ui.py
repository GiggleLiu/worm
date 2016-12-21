'''
Command line user interface.
'''

from cmd import Cmd
import pdb

from models import get_sources,get_posts_bysid
from worm import Worm
from setting import POSTCACHE
from utils import browselink

helptext='''Table of Commands:
    ls: List sources.
    lp: <n=10>: List latest n(default 10) posts if <source_id> provided.
        e.g. >> l 2   # list latest 2 posts
    browse i: Open `i`-th post in system browser.

    update <i>: Update posts manually, for source `i` only if specified else all sources are updated.
    listen: Update at a frequency specified with `setting.UPDATE_SPAN`.
    nolisten: Stop updates.

    save: Save all posts.
    load: Load posts in database, flush runtime datas.

    h: Show this help text.
    quit: Quit.
    debug: Programmer debug interface.
'''

class MyApp(Cmd,object):
    '''My Console Application.'''
    def __init__(self,*args,**kwargs):
        super(MyApp,self).__init__(*args,**kwargs)
        self.worm=Worm(POSTCACHE)

    def do_ls(self,args):
        '''list informations from database.'''
        #list sources
        print 'Table of Sources:\n---------------------------'
        sources=[h.source for h in self.worm.handlers]
        for i,s in enumerate(sources):
            print i,s

    def do_lp(self,args):
        '''list posts'''
        posts=[]
        try:
            n=int(args)
        except:
            n=10
        for i,p in enumerate(self.worm.posts[:n]):
            print i,p

    def do_browse(self,args):
        '''open post on brower'''
        try:
            i=int(args)
        except:
            print 'Wrong type of input! Should be e.g. >> browse 1'
        if i<len(self.worm.posts) and i>=0:
            browselink(self.worm.posts[i].link)
        else:
            print 'Post index out of range!'

    def do_load(self,args):
        '''Load posts in database.'''
        self.worm.load_posts()

    def do_save(self,args):
        '''Save all posts.'''
        self.worm.save_posts()

    def do_listen(self,args):
        '''Listen updates.'''
        self.worm.listen()

    def do_nolisten(self,args):
        '''Stop Listen update.'''
        self.worm.stop_listen()

    def do_update(self,args):
        '''
        Update all posts.

        args:
            the group index, or empty.
        '''
        if len(args)==0:
            i=None
        else:
            try:
                i=int(args)
            except:
                print 'Wrong type of input! Should be e.g. >> update 1'
        info=self.worm.update_all(group=i)

    def do_h(self,args):
        '''Help'''
        print helptext

    def do_quit(self,args):
        '''Quit'''
        raise SystemExit

    def do_debug(self,args):
        '''Quick Debug'''
        pdb.set_trace()

if __name__=='__main__':
    app=MyApp()
    app.prompt='>> '
    app.cmdloop('')
