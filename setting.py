#-*-coding:utf-8-*-

TESTMODE=False

#number of posts alive.
POSTCACHE=1000

#numer of beeps
NBEEP=1

#time span between two updates [`中标`,`流动信息`,`回答`].
UPDATE_SPAN=[5]*3 if TESTMODE else [200,20,150]

#target money(Wan), above which will considered.
TARGET_MONEY=20000   #200,000,000  #the target amount of money

#key words for messages.
#KEYWORDS_MES=[u'涨价',u'提价',u'上涨',u'停产',u'上调',u'价格',u'资产注入',u'进入',u'资本市场']
KEYWORDS_MES=['涨价','提价','上涨','停产','上调','价格','资产注入','进入','资本市场']

#key words for answers.
KEYWORDS_ANS=['百度','阿里','腾讯','支付宝','蚂蚁金服','360','万达','宝能',\
        '安邦','阳光','恒大','中标','采购','股权','分配','高送转','苹果','三星','华为','特斯拉','KK','亿','供货','签订']

BROWSER_HEAD=[
        ('Connection', 'Keep-Alive'),
        ('Accept', 'text/html, application/xhtml+xml, */*'),
        ('Accept-Language', 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3'),
        ('User-Agent', 'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko')]

