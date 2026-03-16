from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import AdminMessage, MemberMessage, MessageReply
from ads.models import Advertisement
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _

def home(request):
    # Active ads
    ads = Advertisement.objects.filter(is_active=True).order_by('activated_at')[:4]
    return render(request, 'core/home.html', {'ads': ads})

def rules(request):
    return render(request, 'core/rules.html')

def contact_admin(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        company = request.POST.get('company')
        phone = request.POST.get('phone')
        message = request.POST.get('message')
        
        AdminMessage.objects.create(
            name=name,
            company_name=company,
            phone_number=phone,
            message=message
        )
        messages.success(request, 'Message sent to administrator.')
        return redirect('home') # Or stay on page
    return redirect('home') # Should probably be an ajax call or handled in footer

@login_required
def reply_message(request, pk):
    message_obj = MemberMessage.objects.get(pk=pk)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            MessageReply.objects.create(
                message=message_obj,
                user=request.user,
                content=content
            )
            messages.success(request, _('Reply posted successfully.'))
    return redirect('member_messages')

def member_message_list(request):
    member_messages = MemberMessage.objects.all()
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, _('Please login to leave a message.'))
            return redirect('login')
        
        content = request.POST.get('content')
        if content:
            MemberMessage.objects.create(user=request.user, content=content)
            messages.success(request, _('Message posted successfully.'))
            return redirect('member_messages')
    
    return render(request, 'core/member_message_list.html', {'member_messages': member_messages})

class MemberMessageUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = MemberMessage
    fields = ['content']
    template_name = 'core/member_message_form.html'
    success_url = reverse_lazy('member_messages')

    def test_func(self):
        message = self.get_object()
        return self.request.user == message.user or self.request.user.is_superuser

class MemberMessageDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = MemberMessage
    template_name = 'core/member_message_confirm_delete.html'
    success_url = reverse_lazy('member_messages')

    def test_func(self):
        message = self.get_object()
        return self.request.user == message.user or self.request.user.is_superuser
