#-*-coding:utf-8-*-

'''
Command line user interface.
'''


from cmd import Cmd
import argparse,sys
import pdb

from worm import Worm

helptext='''Table of Commands:
    ls: List sources and summary.
    lp [-h] [-n npost] [-s isource [isource ...]] [-w keyword] [-a]:
        List latest posts. Optional arguments are,

        -h, --help            show this help message of this command
        -n npost              number of posts (default = 10)
        -s isource [...]      id(s) of source (default = 7,8)
        -w keyword            keyword as a filter
        -a                    show all posts(including unimportant posts)

        e.g. 1 `>> lp -n 2 -s 7,9 -w 注入 -a`
            will list latest 2 posts with keyword 注入 from source 7 and 9 no matter they are important or not.
        e.g. 2 `>> lp -n 12`
            will list latest 12 important posts from source 7 and 8.

    update <i>: Update posts manually.
        Here, `i` is the source id, e.g. `update 1,2,3`.
        Leave no argument to make all sources updated.
    listen [i]: Update automatically.
    nolisten [i]: Stop automatic updates.

    h: Show this help text.
    quit: Quit.
    debug: Programmer debug interface.
'''

lp_argp=argparse.ArgumentParser(prog='lp',description='List recent posts.')
lp_argp.add_argument('-n',type=int,help='number of posts',metavar='npost',default=10)
lp_argp.add_argument('-s',type=int,nargs='+',help='id(s) of source',metavar='isource',default=[7,8])
lp_argp.add_argument('-w',type=str,help='keyword as a filter',metavar='keyword',default=None)
lp_argp.add_argument('-a',help='show all posts(including unimportant posts)',action='store_true')

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
                print('Wrong type of input! Should be e.g. >> update 1')

    def do_lp(self,args):
        '''list posts'''
        try:
            args=lp_argp.parse_args(args.replace(',',' ').split())
        except:
            return
        n,isource,kw,ni=args.n,args.s,args.w,args.a
        posts=[]
        for i,p in enumerate(self.worm.get_posts(maxN=n,isource=isource,kw=kw,important=not ni)):
            print(str(i)+p.__str__()+'\n来源: %s'%self.worm.get_handler_bysid(p.source_id).source.name)

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
        print(helptext)

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
