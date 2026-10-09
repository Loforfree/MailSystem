from django import forms
from .models import Email,Contacts,PersonalInfo

class EmailForm(forms.ModelForm):
    class Meta:
        model = Email #指定了所属类型
        fields = ['recipient', 'subject', 'body'] #指定了Email中需要显示的字段


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contacts #指定了所属类型
        fields = ['name', 'email'] #指定了Contacts中需要显示的字段

class PersonalInfoForm(forms.ModelForm):
    class Meta:
        model = PersonalInfo
        fields = ['name', 'age', 'gender', 'email', 'phone', 'address']
        labels = {
            'name': '姓名',
            'age': '年龄',
            'gender': '性别',
            'email': '邮件地址',
            'phone': '电话号码',
            'address': '地址'
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
