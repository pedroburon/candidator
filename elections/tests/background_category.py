from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import IntegrityError

from elections.models import Election, BackgroundCategory
from elections.forms import BackgroundCategoryForm


class BackgroundCategoryModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                            owner=self.user,
                                                            slug='barbaz')

    def test_create_background_category(self):
        background_category, created = BackgroundCategory.objects.get_or_create(election=self.election,
                                                                    name='foo')
        self.assertTrue(created)
        self.assertEqual(background_category.name, 'foo')
        self.assertEqual(background_category.election, self.election)


class BackgroundCategoryCreateView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                            owner=self.user,
                                                            slug='barbaz')

    def test_create_background_category_by_user_without_login(self):
        request = self.client.get(reverse('background_category_create',
                                    kwargs={'election_slug': self.election.slug}))
        self.assertEquals(request.status_code, 302)

    def test_create_background_category_by_user_success(self):
        self.client.login(username='joe', password='doe')
        request = self.client.get(reverse('background_category_create',
                                    kwargs={'election_slug': self.election.slug}))

        self.assertEqual(request.status_code, 200)
        self.assertTrue('form' in request.context)
        self.assertTrue(isinstance(request.context['form'], BackgroundCategoryForm))
        self.assertTrue('election' in request.context)
        self.assertTrue(isinstance(request.context['election'], Election))


    def test_post_background_category_create_without_login(self):
        params = {'name': 'Bar'}
        response = self.client.post(reverse('background_category_create',
                                        kwargs={'election_slug': self.election.slug}),
                                    params)

        self.assertEquals(response.status_code, 302)

    def test_get_background_category_create_with_login_stranger_election(self):
        self.client.login(username='joe', password='doe')
        response = self.client.get(reverse('background_category_create',
                                    kwargs={'election_slug': 'strager_election_slug'}))
        self.assertEquals(response.status_code, 404)

    def test_post_background_category_create_with_login_stranger_election(self):
        self.client.login(username='joe', password='doe')

        params = {'name': 'Bar'}
        response = self.client.post(reverse('background_category_create',
                                        kwargs={'election_slug': 'strager_election_slug'}),
                                    params)
        self.assertEquals(response.status_code, 404)

    def test_post_background_category_create_logged(self):
        self.client.login(username='joe', password='doe')

        params = {'name': 'Bar'}
        response = self.client.post(reverse('background_category_create',
                                        kwargs={'election_slug': self.election.slug}),
                                    params,
                                    follow=True)

        self.assertEquals(response.status_code, 200)
        qs = BackgroundCategory.objects.filter(name='Bar')
        self.assertEquals(qs.count(), 1)
        background_category = qs.get()
        self.assertEqual(background_category.name, params['name'])
        self.assertEqual(background_category.election, self.election)

        self.assertRedirects(response, reverse('background_category_create',
                                               kwargs={'election_slug': self.election.slug}))