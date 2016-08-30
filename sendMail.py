# -*- coding:utf-8 -*-

from email import encoders
from email.header import Header
from email.mime.multipart import MIMEMultipart  
from email.mime.base import MIMEBase  
from email.mime.text import MIMEText  
from email.utils import parseaddr, formataddr
import smtplib
"""
def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr(( \
    Header(name, 'utf-8').encode(), \
    addr.encode('utf-8') if isinstance(addr, unicode) else addr))
"""
def send_mail(from_addr,to_addr,subjest_content,mail_content,cc_addr=None,bcc_addr=None,attachment=None):
    mail_content='[%s]' % from_addr + mail_content
    msg = MIMEText(mail_content, 'plain', 'utf-8')
    if attachment:
        file_name=attachment.split('/')[-1]
        msg = MIMEMultipart()
        att = MIMEText(open(attachment, 'rb').read(), 'base64', 'utf-8')    
        att["Content-Type"] = 'application/octet-stream'    
        att["Content-Disposition"] = 'attachment; filename=%s' % file_name   
        msg.attach(att)    
        msg.attach(MIMEText(mail_content, 'plain', 'utf-8'))
    #msg['From'] = _format_addr('<%s>' % from_addr)
    msg['To'] = to_addr
    if isinstance(to_addr, list):
        msg['To'] = ','.join(to_addr)
    msg['Cc'] = cc_addr
    if isinstance(cc_addr, list):
        msg['Cc'] = ','.join(cc_addr)
        cc_addr=','.join(cc_addr)
    msg['Bcc'] = bcc_addr
    if isinstance(bcc_addr, list):
        msg['Cc'] = ','.join(bcc_addr)
    msg['Subject'] = Header(subjest_content, 'utf-8').encode()
    smtp = smtplib.SMTP()
    #smtp.connect('142.133.1.1') 
    smtp.connect('146.11.115.136') 
    #smtp.login('Administrator')  
    smtp.sendmail('Administrator@ems.eld.gz.cn.ao.ericsson.se', [to_addr,cc_addr,bcc_addr], msg.as_string()) 
    #smtp.sendmail(from_addr, to_addr, msg.as_string()) 
    smtp.quit()
    """
    try: 
        smtp = smtplib.SMTP()
        smtp.connect('142.133.1.1') 
        #smtp.login('Administrator')  
        smtp.sendmail('Administrator@ems.eld.gz.cn.ao.ericsson.se', [to_addr,cc_addr,bcc_addr], msg.as_string()) 
        #smtp.sendmail(from_addr, to_addr, msg.as_string()) 
        smtp.quit()
    except:
        print('smtp SMS expception error')
    return
    """
"""
raw_db_file_name="C:/BarScannerExcels/hist/CGC_asset.xls"
send_mail(from_addr='jason.g.zhang@ericsson.com', to_addr='jason.g.zhang@ericsson.com',cc_addr='jason.g.zhang@ericsson.com',
           subjest_content='E-location update', mail_content='Please see the update in the attachment', 
           attachment=raw_db_file_name)
"""
""" 
from_addr = raw_input('From: ')
password = raw_input('Password: ')
to_addr = raw_input('To: ')
smtp_server = raw_input('SMTP server: ')
 
msg = MIMEText('hello, send by Python...', 'plain', 'utf-8')
msg['From'] = _format_addr(u'Python������ <%s>' % from_addr)
msg['To'] = _format_addr(u'����Ա <%s>' % to_addr)
msg['Subject'] = Header(u'����SMTP���ʺ򡭡�', 'utf-8').encode()
 
server = smtplib.SMTP(smtp_server, 25)
server.set_debuglevel(1)
server.login(from_addr, password)
server.sendmail(from_addr, [to_addr], msg.as_string())
server.quit()


# 邮件对象:
msg = MIMEMultipart()
msg['From'] = _format_addr(u'Python爱好者 <%s>' % from_addr)
msg['To'] = _format_addr(u'管理员 <%s>' % to_addr)
msg['Subject'] = Header(u'来自SMTP的问候……', 'utf-8').encode()
 
# 邮件正文是MIMEText:
msg.attach(MIMEText('send with file...', 'plain', 'utf-8'))
 
# 添加附件就是加上一个MIMEBase，从本地读取一个图片:
with open('/Users/michael/Downloads/test.png', 'rb') as f:
  # 设置附件的MIME和文件名，这里是png类型:
  mime = MIMEBase('image', 'png', filename='test.png')
  # 加上必要的头信息:
  mime.add_header('Content-Disposition', 'attachment', filename='test.png')
  mime.add_header('Content-ID', '<0>')
  mime.add_header('X-Attachment-Id', '0')
  # 把附件的内容读进来:
  mime.set_payload(f.read())
  # 用Base64编码:
  encoders.encode_base64(mime)
  # 添加到MIMEMultipart:
  msg.attach(mime)

"""