from rest_framework import serializers
from .models import Section, Thread, Post

class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    # author_avatar = serializers.ImageField(source='author.avatar', read_only=True)
    
    class Meta:
        model = Post
        fields = ['id', 'author', 'content', 'created_at']
        read_only_fields = ['created_at']

class ThreadListSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    section_name = serializers.ReadOnlyField(source='section.name')
    
    class Meta:
        model = Thread
        fields = ['id', 'title', 'author', 'section', 'section_name', 'reply_count', 'view_count', 'last_reply_at', 'is_pinned']

class ThreadDetailSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    section_name = serializers.ReadOnlyField(source='section.name')
    posts = PostSerializer(many=True, read_only=True)
    
    class Meta:
        model = Thread
        fields = ['id', 'title', 'content', 'author', 'section', 'section_name', 'created_at', 'view_count', 'reply_count', 'posts']

class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ['id', 'name', 'description']
