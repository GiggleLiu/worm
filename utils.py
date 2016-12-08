#-*-coding:utf-8-*-

import cPickle as pickle
import os,platform,time,re
import pdb

__all__=['quicksave','quickload','beep','inherit_docstring_from','match_money','load_samplepage']

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

def match_money(s):
    '''
    Search money string from a string, in wan yuan.
    '''
    if isinstance(s,unicode): s=s.encode('utf-8')
    format1=[r'￥([\d|,]+\.?\d*)',r'([\d|,]+\.?\d*) ?元']
    format2=[r'([\d|,]+\.?\d*) ?万元']
    res1=reduce(lambda x,y:x+y,[re.findall(f,s) for f in format1])
    res2=reduce(lambda x,y:x+y,[re.findall(f,s) for f in format2])
    m=0
    for d in res1:
        m+=float(''.join(d.split(',')))/1e4
    for d in res2:
        m+=float(''.join(d.split(',')))
    return m

def load_samplepage(isource,i=None):
    '''sample page for source/post(if i specified)'''
    if i is None:
        page=quickload('samples%s/sample_page.dat'%isource)
    else:
        page=quickload('samples%s/sample_page_%s.dat'%(isource,i))
    return page

