from rest_framework import viewsets, permissions, filters, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Section, Thread, Post
from .serializers import SectionSerializer, ThreadListSerializer, ThreadDetailSerializer, PostSerializer

class SectionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Section.objects.filter(is_active=True)
    serializer_class = SectionSerializer
    permission_classes = [permissions.AllowAny]

class ThreadViewSet(viewsets.ModelViewSet):
    queryset = Thread.objects.filter(status=Thread.Status.OPEN)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'content']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ThreadDetailSerializer
        return ThreadListSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.view_count += 1
        instance.save(update_fields=['view_count'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def reply(self, request, pk=None):
        thread = self.get_object()
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, thread=thread)
            
            # Update thread stats
            thread.reply_count += 1
            thread.save(update_fields=['reply_count', 'last_reply_at'])
            
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
