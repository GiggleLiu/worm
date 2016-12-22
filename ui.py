#-*-coding:utf-8-*-

'''
Command line user interface.
'''

from cmd import Cmd
import pdb

from worm import Worm

helptext='''Table of Commands:
    ls: List sources and summary.
    lp: <n=10>: List latest n(default 10) posts if <source_id> provided.
        e.g. >> l 2   # list latest 2 posts

    update <i>: Update posts manually.
        Here, `i` is the source id, e.g. `update 1,2,3`.
        Leave no argument to make all sources updated.
    listen <i>: Update automatically.
    nolisten <i>: Stop automatic updates.

    h: Show this help text.
    quit: Quit.
    debug: Programmer debug interface.
'''

class MyApp(Cmd,object):
    '''My Console Application.'''
    def __init__(self,*args,**kwargs):
        super(MyApp,self).__init__(*args,**kwargs)
        self.worm=Worm()

    def _parse_sid(self,args):
        if len(args)==0:
            i=None
        else:
            try:
                i=[int(arg) for arg in args.split(',')]
                return i
            except:
                return -1
                print 'Wrong type of input! Should be e.g. >> update 1'

    def do_lp(self,args):
        '''list posts'''
        posts=[]
        try:
            n=int(args)
        except:
            n=10
        for i,p in enumerate(self.worm.get_posts(maxN=n)):
            print i,p.__str__()+'\n来源: %s'%self.worm.get_handler_bysid(p.source_id).source.name

    def do_ls(self,args):
        '''Show Status.'''
        self.worm.print_stat()

    def do_listen(self,args):
        '''
        Listen updates.

        args:
            a source id, or empty.
        '''
        i=self._parse_sid(args)
        if i is not -1:
            info=self.worm.do('listen',isource=i)

    def do_nolisten(self,args):
        '''
        Stop Listen update.

        args:
            a source id, or empty.
        '''
        i=self._parse_sid(args)
        if i is not -1:
            info=self.worm.do('stop_listen',isource=i)

    def do_update(self,args):
        '''
        Update all posts.

        args:
            a source id, or empty.
        '''
        i=self._parse_sid(args)
        if i is not -1:
            info=self.worm.do('update',isource=i)

    def do_refresh(self,args):
        '''
        Refresh all posts.

        args:
            a source id, or empty.
        '''
        i=self._parse_sid(args)
        if i is not -1:
            info=self.worm.do('refresh',isource=i)

    def do_h(self,args):
        '''Help'''
        print helptext

    def do_quit(self,args):
        '''Quit'''
        raise SystemExit

    def do_EOF(self,args):
        '''Ctrl+D'''
        self.do_quit('')

    def do_debug(self,args):
        '''Quick Debug'''
        pdb.set_trace()

if __name__=='__main__':
    app=MyApp()
    app.prompt='>> '
    app.cmdloop('')
