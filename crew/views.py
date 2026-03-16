from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q
from .models import CrewListing
from .forms import CrewListingForm
from django.utils.translation import gettext_lazy as _

class CrewListView(ListView):
    model = CrewListing
    template_name = 'crew/crew_list.html'
    context_object_name = 'crew_list'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().filter(status='AVAILABLE')
        
        # Filter by Nationality Type (Tab)
        tab = self.request.GET.get('tab', 'DOMESTIC')
        if tab == 'INTERNATIONAL':
            queryset = queryset.filter(nationality_type='INTERNATIONAL')
        else:
            queryset = queryset.filter(nationality_type='DOMESTIC')

        # Search
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(name__icontains=q) | 
                Q(position__icontains=q) |
                Q(nationality__icontains=q) |
                Q(resume__icontains=q)
            )
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_tab'] = self.request.GET.get('tab', 'DOMESTIC')
        return context

class CrewDetailView(LoginRequiredMixin, DetailView):
    model = CrewListing
    template_name = 'crew/crew_detail.html'
    context_object_name = 'crew'

class CrewCreateView(LoginRequiredMixin, CreateView):
    model = CrewListing
    form_class = CrewListingForm
    template_name = 'crew/crew_form.html'
    success_url = reverse_lazy('crew:crew_list')

    def dispatch(self, request, *args, **kwargs):
        # If user already has a profile, redirect to update
        if hasattr(request.user, 'crew_profile'):
            messages.info(request, _("You already have a crew profile. You can edit it here."))
            return redirect('crew:crew_update', pk=request.user.crew_profile.pk)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, _("Crew profile created successfully."))
        return super().form_valid(form)

class CrewUpdateView(LoginRequiredMixin, UpdateView):
    model = CrewListing
    form_class = CrewListingForm
    template_name = 'crew/crew_form.html'
    success_url = reverse_lazy('crew:crew_list')

    def get_queryset(self):
        # Only allow editing own profile
        return super().get_queryset().filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, _("Crew profile updated successfully."))
        return super().form_valid(form)
