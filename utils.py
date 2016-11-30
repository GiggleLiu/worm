#-*-coding:utf-8-*-

import cPickle as pickle
import os,platform,time
import pdb

__all__=['quicksave','quickload','beep','inherit_docstring_from']

def quicksave(filename,obj):
    '''Save an instance.'''
    f=open(filename,'wb')
    pickle.dump(obj,f,1)
    f.close()

def quickload(filename):
    '''Load an instance.'''
    f=open(filename,'rb')
    obj=pickle.load(f)
    f.close()
    return obj

def load_samplepage(i=None):
    '''sample page for source/post(if i specified)'''
    if i is None:
        page=quickload('samples/sample_page.dat')
    else:
        page=quickload('samples/sample_page_%s.dat'%i)
    return page

def beep(span=2,ntimes=1):
    '''Beep!'''
    if platform.system()=='Linux':
        for i in xrange(ntimes):
            os.system('canberra-gtk-play --file=/usr/share/sounds/ubuntu/stereo/phone-incoming-call.ogg')
            time.sleep(span)
    else:
        import winsound
        for i in xrange(ntimes):
            winsound.Beep(1000,1000) #1000 Hz, 1000 ms
            time.sleep(span)

def inherit_docstring_from(cls):
    def docstring_inheriting_decorator(fn):
        fn.__doc__ = getattr(cls, fn.__name__).__doc__
        return fn
    return docstring_inheriting_decorator


