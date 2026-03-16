from rest_framework import viewsets, permissions, filters
from .models import JobPosition, JobListing
from .serializers import JobPositionSerializer, JobListingSerializer
from apps.users.models import CrewProfile
from apps.users.serializers import CrewProfileSerializer
from apps.core.permissions import IsOwnerOrReadOnly

class CrewResumeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for listing available Crew Profiles (Resumes).
    """
    queryset = CrewProfile.objects.filter(status=CrewProfile.Status.AVAILABLE).order_by('-updated_at')
    serializer_class = CrewProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['real_name', 'position', 'bio']
    ordering_fields = ['years_of_experience', 'updated_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        position = self.request.query_params.get('position', None)
        if position:
            queryset = queryset.filter(position__icontains=position)
        return queryset

class JobPositionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Job Positions.
    List action returns only root positions (Departments) with recursive children.
    """
    queryset = JobPosition.objects.all()
    serializer_class = JobPositionSerializer

    def get_queryset(self):
        if self.action == 'list':
            return JobPosition.objects.filter(parent__isnull=True).order_by('order')
        return JobPosition.objects.all()

class JobListingViewSet(viewsets.ModelViewSet):
    queryset = JobListing.objects.all().order_by('-created_at')
    serializer_class = JobListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'requirements']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        position_id = self.request.query_params.get('position', None)
        employer_id = self.request.query_params.get('employer', None)
        
        if position_id:
            queryset = queryset.filter(position_id=position_id)
        
        if employer_id:
            queryset = queryset.filter(employer_id=employer_id)
            
        return queryset

    def perform_create(self, serializer):
        # In a real app, we might check if user.role == COMPANY
        serializer.save(employer=self.request.user)
