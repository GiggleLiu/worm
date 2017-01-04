#-*-coding:utf-8-*-

import zlib,time,datetime
import pdb

from setting import SOURCE_CONFIG

__all__=['Source','Post','get_sources']

class Source(object):
    '''
    Source for update,

    Attributes:
        :name: str,
        :baselink: str, link for the list view.
        :update_span: int, time interval for updates.
        :group: int, the type of source.
        :status: str, 'ok', 'error'.
        :id: int, the id, leave -1 to generate one.
    '''
    _id=0
    def __init__(self,name,baselink,update_span=200,group=-1,status='ok',id=-1):
        if id==-1:
            Source._id+=1
            self.id=Source._id
        self.update_span,self.group,self.status=update_span,group,status
        self.baselink=baselink
        self.name=name

    def __str__(self):
        return '%s: %s (%s)'%(self.id,self.name,self.baselink)

    def __repr__(self):
        return self.__str__()

class Post(object):
    '''Single post.'''
    _id=0
    def __init__(self,title,link,time,source_id,money=-1,pagecontent='',is_important=False,id=-1):
        if id==-1:
            Post._id+=1
            self.id=Post._id
        if isinstance(pagecontent,memoryview):
            pagecontent=zlib.decompress(pagecontent)
        self.title,self.link,self.time,self.source_id=title.replace('\u200b',''),link,time,source_id
        self.money,self.pagecontent=money,pagecontent
        self.is_important=is_important

    def __str__(self):
        s='标题: %s/%s\n时间: %s%s\n链接: %s'%(self.title,'重要' if self.is_important else '',datetime.datetime.utcfromtimestamp(self.time),('' if self.money<=0 else '\n金额: %s万元'%self.money),self.link)
        return s

    def __repr__(self):
        return self.__str__()

    def __eq__(self,target):
        return self.title==target.title

def get_sources():
    '''Get all sources.'''
    return [Source(config[0],baselink=config[4],group=config[1],update_span=config[2],status=config[3]) for config in SOURCE_CONFIG]
