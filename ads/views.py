from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from .models import Advertisement
from .forms import AdvertisementForm



class AdListView(ListView):
    model = Advertisement
    template_name = 'ads/ad_list.html'
    context_object_name = 'ads'
    ordering = ['-created_at']

    def get_queryset(self):
        return Advertisement.objects.filter(is_active=True).order_by('-activated_at')

class AdDetailView(DetailView):
    model = Advertisement
    template_name = 'ads/ad_detail.html'
    context_object_name = 'ad'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ad = self.object
        if ad.user:
            context['other_ads'] = Advertisement.objects.filter(
                user=ad.user, 
                is_active=True
            ).exclude(pk=ad.pk).order_by('-created_at')[:4]
        return context

class AdCreateView(LoginRequiredMixin, CreateView):
    model = Advertisement
    form_class = AdvertisementForm
    template_name = 'ads/ad_form.html'
    success_url = reverse_lazy('ads:ad_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        # Auto-activate for now, or pending approval?
        # Let's set to active to test the FIFO queue logic, or inactive if approval needed.
        # Let's assume auto-active for now as per "FIFO ad queue" implying rotation.
        form.instance.is_active = True
        
        # FIFO Logic: If we are activating this new ad, ensure max 4 active.
        # Check active ads count
        active_ads = Advertisement.objects.filter(is_active=True).order_by('activated_at')
        if active_ads.count() >= 4:
            # Deactivate the oldest one
            oldest = active_ads.first()
            if oldest:
                oldest.is_active = False
                oldest.save()
                messages.info(self.request, _("The oldest ad was deactivated to make space for your new ad."))

        messages.success(self.request, _("Ad posted successfully."))
        return super().form_valid(form)

class AdUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Advertisement
    form_class = AdvertisementForm
    template_name = 'ads/ad_form.html'
    
    def test_func(self):
        obj = self.get_object()
        return obj.user == self.request.user or self.request.user.is_superuser

    def get_success_url(self):
        return reverse_lazy('ads:ad_detail', kwargs={'pk': self.object.pk})

class AdDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Advertisement
    template_name = 'ads/ad_confirm_delete.html'
    success_url = reverse_lazy('ads:ad_list')

    def test_func(self):
        obj = self.get_object()
        return obj.user == self.request.user or self.request.user.is_superuser
