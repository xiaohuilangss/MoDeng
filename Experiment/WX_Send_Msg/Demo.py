# encoding=utf-8

import itchat

itchat.auto_login()

# itchat.send('Hello, filehelper', toUserName='filehelper')

user = itchat.search_friends(name=u'主人')[0]
user.send(u'机器人say hello')