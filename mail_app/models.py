from django.db import models
from django.contrib.auth.models import User
import json

FOLDER_CHOICES = (
    ('inbox', '收件箱'),
    ('sent', '已发送'),
)

class Email(models.Model):
    subject = models.CharField("主题", max_length=255)
    body = models.TextField("内容")
    sender = models.EmailField("发件人")
    recipient = models.EmailField("收件人")
    timestamp = models.DateTimeField("时间", auto_now_add=True)
    folder = models.CharField("文件夹", max_length=10, choices=FOLDER_CHOICES, default='inbox')
    is_deleted = models.BooleanField("是否删除", default=False)
    is_flagged = models.BooleanField("是否星标", default=False)
    is_draft = models.BooleanField(default=False)
    #附件
    attachment_url = models.URLField(blank=True, null=True)  # 新增字段存储QQ邮箱附件URL

    def __str__(self):
        return self.subject
    
    def set_attachments(self, file_list):
        """存储附件列表"""
        self.attachment_url = json.dumps(file_list)
    
    def get_attachments(self):
        """获取附件列表"""
        if self.attachment_url:
            try:
                return json.loads(self.attachment_url)
            except (json.JSONDecodeError, TypeError):
                # 兼容旧格式（逗号分隔）
                return [f.strip() for f in str(self.attachment_url).split(',') if f.strip()]
        return []
    
    def add_attachment(self, filename):
        """添加单个附件"""
        attachments = self.get_attachments()
        attachments.append(filename)
        self.set_attachments(attachments)
    

class Contacts(models.Model):
    name = models.CharField("姓名",max_length=255)
    email = models.EmailField("邮件地址",max_length=255)

class PersonalInfo(models.Model):
    name = models.CharField("姓名",max_length=255)
    age = models.IntegerField("年龄")
    gender = models.CharField("性别",max_length=255)
    email = models.EmailField("邮件地址",max_length=255)
    phone = models.CharField("电话号码",max_length=255)
    address = models.CharField("城市",max_length=255)

    def __str__(self):
        return self.name
