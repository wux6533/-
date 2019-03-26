# -*- coding:utf-8 -*-
import os
import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class sendEmai(object):
    def __init__(self, receivers):
        mail_host = "smtp.163.com"  # SMTP服务器
        mail_user = "tiangebsj"  # 用户名
        mail_pass = "tiangebsj123sqm"  # 授权密码
        sender = "tiangebsj@163.com"  # 发件人邮箱
        file_path = os.path.dirname(os.path.dirname(__file__)).replace('/', '\\') + '\\report\\test_result.html'
        title = '博云视控自动化测试结果'  # 邮件主题
        message = MIMEMultipart()
        message['From'] = "{}".format(sender)
        message['To'] = ",".join(receivers)
        message['Subject'] = title
        mail_body = "查看测试报告请下载附件！！！"  #
        msgtext = MIMEText(mail_body, _subtype='plain', _charset='utf-8')
        message.attach(msgtext)  # 添加主邮件主体内容
        # 添加一个HTML文本附件
        ff = open(file_path, 'rb')
        att = MIMEText(ff.read(), 'base64', 'utf-8')
        # 附件设置内容类型，设置为二进制流
        att["Content-Type"] = 'application/octet-stream'
        # 设置附件头，添加文件名
        att["Content-Disposition"] = 'attachment; filename="test_result.html"'
        # 解决中文附件名乱码问题
        # att.add_header('Content-Disposition', 'attachment', filename=('utf-8', '', basename))
        message.attach(att)
        ff.close()
        try:
            smtpObj = smtplib.SMTP_SSL(mail_host, 994)  # 启用SSL发信, 端口一般是465 或 994
            smtpObj.login(mail_user, mail_pass)  # 登录验证
            smtpObj.sendmail(sender, receivers, message.as_string())  # 发送
            print("邮件已成功发送")
        except smtplib.SMTPException as e:
            print(e)

    def send_email2(SMTP_host, from_account, from_passwd, to_account, subject, content):
        email_client = smtplib.SMTP(SMTP_host)
        email_client.login(from_account, from_passwd)
        # create msg
        msg = MIMEText(content, 'plain', 'utf-8')
        msg['Subject'] = Header(subject, 'utf-8')  # subject
        msg['From'] = from_account
        msg['To'] = to_account
        email_client.sendmail(from_account, to_account, msg.as_string())
        email_client.quit()


if __name__ == "__main__":
    sendEmai(['1531996630@qq.com', '3003521126@qq.com'])
