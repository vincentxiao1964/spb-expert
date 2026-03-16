from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext as _
from .models import ShipListing, MarketNews, CrawledShip
from .forms import ShipListingForm, ListingImageFormSet
from django.db.models import Q
from django.views import View

class CrawledShipListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = CrawledShip
    template_name = 'market/crawled_ship_list.html'
    context_object_name = 'ships'
    paginate_by = 50

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

    def get_queryset(self):
        queryset = CrawledShip.objects.all().order_by('-crawled_at')
        
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(source_id__icontains=q) | 
                Q(full_description__icontains=q)
            )
        
        width_min = self.request.GET.get('width_min')
        width_max = self.request.GET.get('width_max')
        
        if width_min:
            queryset = queryset.filter(width__gte=width_min)
        if width_max:
            queryset = queryset.filter(width__lte=width_max)
            
        return queryset

class ListingListView(ListView):
    model = ShipListing
    template_name = 'market/listing_list.html'
    context_object_name = 'listings'
    paginate_by = 20

    def get_queryset(self):
        queryset = ShipListing.objects.filter(status=ShipListing.Status.APPROVED)
        if self.request.user.is_authenticated:
            queryset = queryset | ShipListing.objects.filter(user=self.request.user)
        
        queryset = queryset.distinct().select_related('user').prefetch_related('images').order_by('-created_at')
        
        # Filters
        ship_category = self.request.GET.get('category')
        if ship_category:
            queryset = queryset.filter(ship_category=ship_category)
            
        listing_types = self.request.GET.getlist('type')
        if listing_types:
            queryset = queryset.filter(listing_type__in=listing_types)

        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(contact_info__icontains=q) | 
                Q(class_society__icontains=q) |
                Q(flag_state__icontains=q)
            )
            
        return queryset

class ListingDetailView(LoginRequiredMixin, DetailView):
    model = ShipListing
    template_name = 'market/listing_detail.html'
    context_object_name = 'listing'

class ListingCreateView(LoginRequiredMixin, CreateView):
    model = ShipListing
    form_class = ShipListingForm
    template_name = 'market/listing_form.html'
    success_url = reverse_lazy('market:list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        
        # Handle images
        image_formset = ListingImageFormSet(self.request.POST, self.request.FILES, instance=self.object)
        if image_formset.is_valid():
            image_formset.save()
        
        messages.success(self.request, _('Listing posted successfully!'))
        if self.object.status == ShipListing.Status.PENDING:
            messages.info(self.request, _('Your listing is pending approval.'))
            
        return response

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['images'] = ListingImageFormSet(self.request.POST, self.request.FILES)
        else:
            data['images'] = ListingImageFormSet()
        return data

class ListingUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = ShipListing
    form_class = ShipListingForm
    template_name = 'market/listing_form.html'
    success_url = reverse_lazy('market:list')

    def form_valid(self, form):
        response = super().form_valid(form)
        image_formset = ListingImageFormSet(self.request.POST, self.request.FILES, instance=self.object)
        if image_formset.is_valid():
            image_formset.save()
        return response

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['images'] = ListingImageFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            data['images'] = ListingImageFormSet(instance=self.object)
        return data

    def test_func(self):
        listing = self.get_object()
        return self.request.user == listing.user or self.request.user.is_superuser or self.request.user.is_staff

class ListingDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = ShipListing
    success_url = reverse_lazy('market:list')
    template_name = 'market/listing_confirm_delete.html'

    def test_func(self):
        listing = self.get_object()
        return self.request.user == listing.user or self.request.user.is_superuser or self.request.user.is_staff

# Market News Views

class MarketNewsListView(ListView):
    model = MarketNews
    template_name = 'market/news_list.html'
    context_object_name = 'news_list'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = MarketNews.objects.filter(status=MarketNews.Status.APPROVED)
        if self.request.user.is_authenticated:
            queryset = queryset | MarketNews.objects.filter(user=self.request.user)
        return queryset.distinct().order_by('-created_at')

class MarketNewsDetailView(DetailView):
    model = MarketNews
    template_name = 'market/news_detail.html'
    context_object_name = 'news'

class MarketNewsCreateView(LoginRequiredMixin, CreateView):
    model = MarketNews
    fields = ['title', 'content', 'image']
    template_name = 'market/news_form.html'
    success_url = reverse_lazy('market:news_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, _('News posted successfully!'))
        if self.object.status == MarketNews.Status.PENDING:
            messages.info(self.request, _('Your post is pending approval.'))
        return response

class MarketNewsUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = MarketNews
    fields = ['title', 'title_en', 'content', 'content_en', 'image']
    template_name = 'market/news_form.html'
    success_url = reverse_lazy('market:news_list')

    def test_func(self):
        news = self.get_object()
        return self.request.user == news.user or self.request.user.is_superuser or self.request.user.is_staff

class MarketNewsDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = MarketNews
    success_url = reverse_lazy('market:news_list')
    template_name = 'market/news_confirm_delete.html'

    def test_func(self):
        news = self.get_object()
        return self.request.user == news.user or self.request.user.is_superuser or self.request.user.is_staff
