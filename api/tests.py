from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from crew.models import CrewListing

User = get_user_model()

from market.models import Favorite
from users.models import UserFollow
from django.contrib.contenttypes.models import ContentType
from core.models import MemberMessage, MessageReply

class CrewApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password', phone_number='1111111111')
        self.crew = CrewListing.objects.create(
            user=self.user,
            name='Captain Jack',
            position='Captain',
            phone='1234567890',
            email='jack@blackpearl.com',
            status='AVAILABLE',
            nationality_type='DOMESTIC',
            # Add required fields if any (based on model definition, many are CharFields with defaults or nullable? 
            # Model definition:
            # name, gender(default), nationality_type(default), nationality, residence, position, 
            # total_sea_experience, current_rank_experience, cert_number, phone, email, expected_salary, resume, status(default)
            # Decimals need values.
            total_sea_experience=10.0,
            current_rank_experience=5.0,
            cert_number='CJ123',
            residence='Caribbean',
            nationality='Pirate',
            expected_salary='All the gold',
            resume='I am Captain Jack Sparrow'
        )
        self.url = reverse('crew-list')

    def test_list_crew_anonymous(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check structure (pagination)
        if 'results' in response.data:
            results = response.data['results']
        else:
            results = response.data
            
        self.assertEqual(len(results), 1)
        data = results[0]
        self.assertIsNone(data['phone'])
        self.assertIsNone(data['email'])

    def test_list_crew_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if 'results' in response.data:
            results = response.data['results']
        else:
            results = response.data
        data = results[0]
        self.assertEqual(data['phone'], '1234567890')

    def test_create_crew_profile(self):
        user2 = User.objects.create_user(username='testuser2', password='password', phone_number='2222222222')
        self.client.force_authenticate(user=user2)
        data = {
            'name': 'Will Turner',
            'position': 'Blacksmith',
            'phone': '0987654321',
            'email': 'will@blackpearl.com',
            'nationality_type': 'DOMESTIC',
            'nationality': 'UK',
            'residence': 'Port Royal',
            'total_sea_experience': 5.0,
            'current_rank_experience': 2.0,
            'cert_number': 'ABC12345',
            'expected_salary': '1000',
            'resume': 'Good with swords'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(CrewListing.objects.filter(user=user2).exists())

    def test_create_duplicate_profile_fails(self):
        self.client.force_authenticate(user=self.user) # Already has profile
        data = {
            'name': 'Duplicate',
            'position': 'Imposter',
            # ... other fields ...
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_social_status_fields(self):
        # Create another user to view the crew listing
        viewer = User.objects.create_user(username='viewer', password='password', phone_number='3333333333')
        self.client.force_authenticate(user=viewer)
        
        # Initially not following/favorited
        response = self.client.get(self.url)
        if 'results' in response.data:
            results = response.data['results']
        else:
            results = response.data
        data = results[0]
        self.assertFalse(data['is_following'])
        self.assertFalse(data['is_favorited'])
        
        # Follow the crew user
        UserFollow.objects.create(follower=viewer, followed=self.user)
        
        # Favorite the crew listing
        ct = ContentType.objects.get_for_model(CrewListing)
        Favorite.objects.create(user=viewer, content_type=ct, object_id=self.crew.id)
        
        # Check again
        response = self.client.get(self.url)
        if 'results' in response.data:
            results = response.data['results']
        else:
            results = response.data
        data = results[0]
        self.assertTrue(data['is_following'])
        self.assertTrue(data['is_favorited'])

class ForumTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='forumuser', password='password', phone_number='4444444444')
        self.post = MemberMessage.objects.create(user=self.user, content='Hello World')
        self.url = '/api/v1/messages/'

    def test_retrieve_post_includes_replies(self):
        # Create a reply
        replier = User.objects.create_user(username='replier', password='password', phone_number='5555555555')
        MessageReply.objects.create(message=self.post, user=replier, content='Nice post')
        
        response = self.client.get(f'{self.url}{self.post.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('replies', response.data)
        self.assertEqual(len(response.data['replies']), 1)
        self.assertEqual(response.data['replies'][0]['content'], 'Nice post')

    def test_list_post_excludes_replies(self):
         # Create a reply
        replier = User.objects.create_user(username='replier2', password='password', phone_number='6666666666')
        MessageReply.objects.create(message=self.post, user=replier, content='Nice post 2')
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if 'results' in response.data:
            data = response.data['results'][0]
        else:
            data = response.data[0]
            
        # Should not have 'replies' field in list view to save bandwidth
        self.assertNotIn('replies', data)
        # But should have count
        self.assertEqual(data['replies_count'], 1)
