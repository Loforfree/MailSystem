from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from .models import Email , Contacts, PersonalInfo
from .forms import EmailForm, ContactForm,PersonalInfoForm 
from django.http import JsonResponse,FileResponse,HttpResponseRedirect,HttpResponse
import email,os,imaplib,json
from email.header import decode_header
from email.utils import parsedate_to_datetime
from django.contrib import messages
from django.core.mail import EmailMessage

def email_list(request):
    inbox_emails = Email.objects.filter(folder='inbox',is_deleted=False).order_by('-timestamp')
    sent_emails = Email.objects.filter(folder='sent',is_deleted=False).order_by('-timestamp')
    context = {
        'inbox_emails': inbox_emails,
        'sent_emails': sent_emails,
    }
    return render(request, 'mail_app/email_list.html', context)

def email_detail(request, pk):
    email_obj = get_object_or_404(Email, pk=pk)
    return render(request, 'mail_app/email_detail.html', {'email': email_obj})

def compose_email(request):
    if request.method == 'POST':
        recipient = request.POST.get('recipient')
        subject = request.POST.get('subject')
        body = request.POST.get('body')
        attachment = request.FILES.get('attachment')  # 获取上传的文件

        recipientList = [email.strip() for email in recipient.split(',') if email.strip()]
        if not recipientList:
            error_message = "请填写至少一个邮件的收件人邮件地址"
            return render(request,'mail_app/compose_email.html',{'error_message':error_message})
        


        try:
            email = EmailMessage(
                subject,
                body,
                settings.EMAIL_HOST_USER,  # 发件人
                recipientList,
            )
            
            # 如果有附件，添加到邮件
            if attachment:
                email.attach(attachment.name, attachment.read(), attachment.content_type)
            
            email.send()
            
            return redirect('some_success_url')  # 发送成功后重定向
        except Exception as e:
            # 处理发送失败的情况
            error_message = f"发送邮件时出错: {str(e)}"
            return render(request, 'mail_app/compose_email.html', {'error_message': error_message})
    
    return render(request, 'mail_app/compose_email.html')

def trash_email(request):
    deleted_emails = Email.objects.filter(is_deleted=True).order_by('-timestamp')
    return render(request, 'mail_app/trashList.html', {'deleted_emails': deleted_emails})


def delete_email(request, pk):
    print(f'PK: {pk}')
    email_obj = get_object_or_404(Email, pk=pk)
    email_obj.is_deleted = True
    email_obj.save()
    return redirect('email_list')

def receive_email(request):
    IMAP_SERVER = 'imap.qq.com'
    IMAP_PORT = 993
    EMAIL_ADDRESS = settings.EMAIL_HOST_USER
    EMAIL_PASSWORD = settings.EMAIL_HOST_PASSWORD

    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        mail.select("inbox")

        status, messages = mail.search(None, "ALL")
        mail_ids = messages[0].split()

        for mail_id in mail_ids[-10:]:
            status, msg_data = mail.fetch(mail_id, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])
            
            # 解析邮件头
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding if encoding else "utf-8")
            
            sender = msg.get("From")
            recipient = msg.get("To")
            timestamp = parsedate_to_datetime(msg.get("Date"))
            
            # 解析正文和附件
            body = ""
            attachments = []
            
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    
                    # 处理正文
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        try:
                            body = part.get_payload(decode=True).decode("utf-8")
                        except UnicodeDecodeError:
                            body = part.get_payload(decode=True).decode("latin-1")
                    
                    # 处理附件
                    elif "attachment" in content_disposition:
                        filename = part.get_filename()
                        if filename:
                            # 标准化文件名（去除路径）
                            filename = os.path.basename(filename)
                            
                            # 保存附件到本地
                            attachment_dir = os.path.join(settings.MEDIA_ROOT, "email_attachments")
                            os.makedirs(attachment_dir, exist_ok=True)
                            attachment_path = os.path.join(attachment_dir, filename)
                            
                            with open(attachment_path, "wb") as f:
                                f.write(part.get_payload(decode=True))
                            
                            attachments.append(filename)
            
            # 创建邮件记录（使用JSON格式存储附件列表）
            if not Email.objects.filter(subject=subject, sender=sender, timestamp=timestamp).exists():
                Email.objects.create(
                    subject=subject,
                    sender=sender,
                    recipient=recipient,
                    body=body,
                    folder="inbox",
                    timestamp=timestamp,
                    attachment_url=json.dumps(attachments) if attachments else None
                )

        mail.logout()
        return redirect("email_list")

    except Exception as e:
        return HttpResponse(f"接收邮件时出错: {str(e)}", status=500)

def download_attachment(request, pk, filename):
    email_obj = get_object_or_404(Email, pk=pk)
    
    if not email_obj.attachment_url:
        return HttpResponse("此邮件没有附件", status=404)
    
    try:
        # 解析附件列表（支持JSON和旧版逗号分隔格式）
        attachments = json.loads(email_obj.attachment_url) if email_obj.attachment_url.startswith('[') \
                     else [f.strip() for f in email_obj.attachment_url.split(',') if f.strip()]
    except (json.JSONDecodeError, AttributeError):
        attachments = []
    
    # URL解码文件名
    from urllib.parse import unquote
    requested_file = unquote(filename)
    
    # 查找匹配的附件（不区分大小写）
    actual_filename = None
    for stored_file in attachments:
        if stored_file.lower() == requested_file.lower():
            actual_filename = stored_file  # 保留原始大小写
            break
    
    if not actual_filename:
        return HttpResponse(
            f"附件不存在于邮件记录中。请求: '{requested_file}'，可用: {attachments}",
            status=404
        )
    
    # 构建文件路径
    file_path = os.path.normpath(os.path.join(
        settings.MEDIA_ROOT,
        "email_attachments",
        actual_filename
    ))
    
    # 安全检查：防止目录遍历
    if not file_path.startswith(os.path.join(settings.MEDIA_ROOT, "email_attachments")):
        return HttpResponse("非法文件路径", status=403)
    
    if os.path.exists(file_path):
        try:
            with open(file_path, 'rb') as f:
                response = HttpResponse(
                    f.read(),
                    content_type="application/octet-stream"
                )
                response['Content-Disposition'] = (
                    f'attachment; filename="{os.path.basename(file_path)}"'
                )
                return response
        except Exception as e:
            return HttpResponse(f"读取文件时出错: {str(e)}", status=500)
    return HttpResponse(f"附件文件不存在于服务器: {file_path}", status=404)
    
def contacts(request):
    contacts_list = Contacts.objects.all()
    if request.method == 'POST':
        print('post')
        form = ContactForm(request.POST)
        print(form)
        if form.is_valid():
            print('is_valid')
            form.save()
            return redirect('contacts')
    else:
        form = ContactForm()
    return render(request, 'mail_app/contacts_list.html', {'contacts': contacts_list, 'form': form})



def restore_email(request, pk):
    email = get_object_or_404(Email, pk=pk)
    email.is_deleted = False  # 假设你的模型有 `is_deleted` 字段
    email.save()
    return redirect('trash_email')

def true_delete_email(request, pk):
    email = get_object_or_404(Email, pk=pk)
    email.delete()  # 永久删除
    return redirect('trash_email')

def handle_trash_actions(request):
    if request.method == 'POST':
        action = request.POST.get('action')  # 'restore' 或 'delete_permanently'
        email_ids = request.POST.getlist('email_ids')  # 获取选中的邮件ID列表
        
        if not email_ids:
            messages.warning(request, "请至少选择一封邮件！")
            return redirect('trash_email')
        
        if action == 'restore':
            # 恢复邮件（将 is_deleted 设为 False）
            Email.objects.filter(id__in=email_ids).update(is_deleted=False)
            messages.success(request, "已恢复选中的邮件！")
        
        elif action == 'true_delete':
            # 永久删除邮件（从数据库彻底删除）
            Email.objects.filter(id__in=email_ids).delete()
            messages.success(request, "已永久删除选中的邮件！")
        
        return redirect('trash_email')
    
    return redirect('trash_email')


def flagged_emails(request):
    flagged_emails = Email.objects.filter(is_flagged=True,is_deleted=False).order_by('-timestamp')
    return render(request, 'mail_app/flagList.html', {'flagged_emails': flagged_emails})

def flag_email(request, pk):
    email = get_object_or_404(Email, pk=pk)
    email.is_flagged = True
    email.save()
    return redirect('email_list')

def unflag_email(request, pk):
    email = get_object_or_404(Email, pk=pk)
    email.is_flagged = False
    email.save()
    return redirect('flagged_emails')

def personal_info_view(request):
    try:
        # 直接获取ID=1的记录（你的账户）
        info = PersonalInfo.objects.get(id=1)
        data = {
            'name': info.name,
            'age': info.age,
            'gender': info.gender,
            'email': info.email,
            'phone': info.phone,
            'address': info.address,
        }
    except PersonalInfo.DoesNotExist:
        # 如果没有找到记录，返回空值
        data = None
    
    return render(request, 'mail_app/personal_info.html', {'data': data})

def personal_input_view(request):
    if request.method == 'POST':
        # 获取或创建ID=1的记录
        info, created = PersonalInfo.objects.get_or_create(
            id=1,
            defaults={
                'name': '',
                'age': 0,
                'gender': '',
                'email': '',
                'phone': '',
                'address': ''
            }
        )
        # 更新个人资料
        info.name = request.POST.get('name', '')
        info.age = request.POST.get('age', 0)
        info.gender = request.POST.get('gender', '')
        info.email = request.POST.get('email', '')
        info.phone = request.POST.get('phone', '')
        info.address = request.POST.get('address', '')
        info.save()
        return redirect('personal_info')
    
    # GET请求时显示表单
    try:
        info = PersonalInfo.objects.get(id=1)
    except PersonalInfo.DoesNotExist:
        info = None
    
    return render(request, 'mail_app/personal_input.html', {'info': info})
