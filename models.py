#-*-coding:utf-8-*-

import requests,sqlite3,zlib,os,time,datetime,webbrowser
import pdb

__all__=['dbfile','Source','Post','save_post','get_sources','get_source',
        'get_posts_bysid','init_tables','init_sources','get_posts']

dbfile='data.db'

class Source(object):
    def __init__(self,name,baselink,id=-1):
        self.id=id
        if isinstance(baselink,unicode):
            baselink=baselink.encode('utf-8')
        if isinstance(name,unicode):
            name=name.encode('utf-8')
        self.baselink=baselink
        self.name=name

    def __str__(self):
        return '<源: %s> %s'%(self.name,self.baselink)

    def __repr__(self):
        return self.__str__()

    def get_page(self):
        '''Get the site page'''
        page=requests.get(self.baselink).content
        return page

class Post(object):
    '''Single post.'''
    def __init__(self,title,link,time,source_id,money=0,pagecontent='',id=-1):
        self.id=id
        if isinstance(title,unicode):
            title=title.encode('utf-8')
        if isinstance(link,unicode):
            link=link.encode('utf-8')
        if isinstance(time,unicode):
            time=time.encode('utf-8')
        if isinstance(pagecontent,buffer):
            pagecontent=zlib.decompress(pagecontent)
        self.title,self.link,self.time,self.source_id=title,link,time,source_id
        self.money,self.pagecontent=money,pagecontent

    def __str__(self):
        s='<中标: %s>\n时间: %s\n来源: %s\n金额: %s万元\n链接: %s'%(self.title,self.time,self.source_id,self.money,self.link)
        return s

    def __repr__(self):
        return self.__str__()

    def formatted_str(self):
        '''Formatted string for display.'''
        info='{:<100} {:<20} {:<5}'.format(self.title,self.time,self.source_id.strip())
        link='{:<100}'.format(self.link)
        res='%s'%(info)
        return res

    def browse(self):
        '''View this post on browser.'''
        path=os.path.abspath('temp.html')
        url='file://'+path
        with open(path,'w') as f:
            f.write(self.pagecontent)
        f.close()
        webbrowser.open(url)

    def get_page(self):
        '''Get the detailed information page of post.'''
        page=requests.get(self.link).content
        return page

    def get_time(self):
        '''Get the absolute time.'''
        dt=datetime.datetime.strptime(self.time,'%Y-%m-%d %H:%M:%S').timetuple()
        t=time.mktime(dt)
        return t

def save_post(post):
    '''Save a source or post.'''
    conn=sqlite3.connect(dbfile)
    try:
        conn.execute('''insert into post (title,time,link,source_id,money,pagecontent) values ('%s','%s','%s',%s,%s,?)'''\
                %(post.title,post.time,post.link,post.source_id,post.money),(sqlite3.Binary(zlib.compress(post.pagecontent)),))
        conn.commit()
        info=1
    except:
        info=0
    finally:
        conn.close()
        return info

def get_sources():
    '''Get all sources.'''
    conn=sqlite3.connect(dbfile)
    res=[Source(item[1],item[2],id=item[0]) for item in conn.execute('''select * from source''')]
    conn.close()
    return res

def get_posts():
    '''Get sources by source id.'''
    sqstr='''select * from post;'''
    conn=sqlite3.connect(dbfile)
    posts=[Post(title=item[1],time=item[2],link=item[3],id=item[0],source_id=item[4],money=item[5],pagecontent=item[6])\
            for item in conn.execute(sqstr)]
    conn.close()
    return posts

def get_source(sid):
    '''Get single source by id.'''
    conn=sqlite3.connect(dbfile)
    res=[Source(item[1],item[2],id=item[0]) for item in conn.execute('''select * from source where id=%s;'''%sid)]
    conn.close()
    return res

def get_posts_bysid(sid):
    '''Get sources by source id.'''
    sqstr='''select * from post where source_id='%s';'''%sid
    conn=sqlite3.connect(dbfile)
    posts=[Post(title=item[1],time=item[2],link=item[3],id=item[0],source_id=item[4],money=item[5],pagecontent=item[6])\
            for item in conn.execute(sqstr)]
    conn.close()
    return posts

def init_tables():
    '''initialize tables.'''
    if os.path.isfile(dbfile):
        print 'Skip creating database!'
        return
    conn=sqlite3.connect(dbfile)
    conn.execute('''create table source
            (id integer primary key autoincrement,
            name text unique not null,
            link text not null);''')
    conn.execute('''create table post
            (id integer primary key autoincrement,
            title text unique not null,
            time char(50) not null,
            link text not null,
            source_id integer,
            money real,
            pagecontent binary,
            foreign key(source_id) references source(id));''')
    conn.commit()
    conn.close()

def init_sources():
    '''initialize sources.'''
    source_list=[
            (u'中国政府采购网','http://www.ccgp.gov.cn/ppp/pppzhbgg/'),
            ]
    conn=sqlite3.connect(dbfile)
    for source in source_list:
        conn.execute('''insert into source (name,link) values ('%s','%s')'''%(source[0],source[1]))
    conn.commit()
    conn.close()

if __name__=='__main__':
    init_tables()
    init_sources()
