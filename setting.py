#-*-coding:utf-8-*-
import platform

TESTMODE=False

#number of posts alive.
POSTCACHE=1000

#platform, 'Windows'/'Linux'
PLATFORM=platform.system()

#numer of beeps
NBEEP=1

#the browser header informations.
BROWSER_HEAD=[
        ('Connection', 'Keep-Alive'),
        ('Accept', 'text/html, application/xhtml+xml, */*'),
        ('Accept-Language', 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3'),
        ('User-Agent', 'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko')]

#alert mode (non-important message, important message),
#'print' -> print,
#'beep' -> beep,
ALERT_MODE=(('print',),('print','beep'))  #print all messages and beep for important messages

############################ Filters ########################################
#target money(Wan), above which will considered.
TARGET_MONEY=20000   #200,000,000  #the target amount of money

#key words for messages.
KEYWORDS_MES=['涨价','提价','上涨','停产','上调','价格','资产注入','进入','资本市场','共享']

#key words for answers.
KEYWORDS_ANS=['百度','阿里','腾讯','支付宝','蚂蚁金服','360','万达','宝能',\
        '安邦','阳光','恒大','中标','采购','股权','分配','高送转','苹果','三星','华为','特斯拉','KK','亿','供货','签订']

########################### Source Config ###################################
#config sources, (name, group(0, 1, 2), update_span(seconds), status('ok'/'error'), url).
#group 0: 中标网站
#group 1: 咨询网站
#group 2: 问答网站
#status 'ok': 该源可以正常解析
#status 'error': 该源不可以正常解析，更新时跳过
SOURCE_CONFIG=[
        ('中国政府采购网-PPP',0,200,'ok','http://www.ccgp.gov.cn/ppp/pppzhbgg/'),
        ('北京财政',0,200,'error','http://www.bjcz.gov.cn/zfcg/cggg/sycjjggg/index.htm'),          #reason, no uniform money format.
        ('广州市政府采购网',0,200,'error','http://www.gzg2b.gov.cn/Sites/_Layouts/ApplicationPages/News/News.aspx?ColumnName=%e6%8b%9b%e6%a0%87%e7%bb%93%e6%9e%9c%e5%85%ac%e5%91%8a'),     #reason, no uniform money format.
        ('云财经',1,20,'error','http://www.yuncaijing.com/insider/main.html'),     #reason, unable to handle websocket.
        ('证快讯',1,150,'ok','http://news.cnstock.com/bwsd/index.html'),
        ('财联社',1,20,'ok','http://www.cailianpress.com'),
        ('互动易',2,150,'ok','http://irm.cninfo.com.cn/ircs/interaction/lastRepliesForSzse.do'),
        ('上证e互动',2,150,'ok','http://sns.sseinfo.com/ajax/feeds.do?page=1&type=11&pageSize=10&lastid=-1&show=1'),
        ('淘财经',1,20,'ok','http://www.taoguba.com/'),
        ('淘股吧',1,100,'ok','http://www.taoguba.com.cn/moreWonderList'),
        ('中国政府采购网-中央标',0,200,'ok','http://www.ccgp.gov.cn/cggg/zygg/zbgg/'),
        ('中国政府采购网-地方标',0,200,'error','http://www.ccgp.gov.cn/cggg/dfgg/zbgg/'),
        ]
