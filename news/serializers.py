from rest_framework import serializers
from .models import Article, Comment

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    # user_avatar = serializers.ImageField(source='user.avatar', read_only=True) # Avatar not confirmed in User model
    
    class Meta:
        model = Comment
        fields = ['id', 'user', 'content', 'created_at'] # Removed user_avatar
        read_only_fields = ['created_at']

class ArticleListSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    
    class Meta:
        model = Article
        fields = ['id', 'title', 'slug', 'author', 'summary', 'cover_image', 'published_at', 'view_count']

class ArticleDetailSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    comments = CommentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Article
        fields = ['id', 'title', 'slug', 'author', 'content', 'summary', 'cover_image', 'published_at', 'view_count', 'comments']
