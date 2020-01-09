from django.test import TestCase

import datetime

from django.urls import reverse
from django.utils import timezone
from .models import Question
# Create your tests here.


class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        :return:
        """
        time = timezone.now()+datetime.timedelta(days=30)
        future_qsn = Question(publication_date=time)
        self.assertIs(future_qsn.was_published_recently(),False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is over a day ago.
        :return:
        """
        time = timezone.now()-datetime.timedelta(days=1,seconds=1)
        old_question = Question(publication_date=time)
        self.assertIs(old_question.was_published_recently(),False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is less than a day ago.
        :return:
        """
        time = timezone.now()-datetime.timedelta(hours=23,minutes=59,seconds=59)
        recent_question=Question(publication_date=time)
        self.assertIs(recent_question.was_published_recently(),True)

def create_question(text,days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=text,publication_date=time)

class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """if no question exist, an appropriate message is displayed"""
        response=self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No polls are available')
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_questions(self):
        """Questions with a past publication date are displayed in the page"""
        past_qsn = create_question("Past question.", -30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Past question.>'])

    def test_future_questions(self):
        """"""
        future_question = create_question("Future question.", 10)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, 'No polls are available')
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_and_past_questions(self):
        """The future question should be excluded from the context"""
        future_qsn = create_question("Future question.", 30)
        past_qsn = create_question("Past question.", -30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Past question.>'])

    def test_two_past_questions(self):
        """Both should be in the context"""
        past_qsn_1 = create_question("Past Question 1.", -10)
        past_qsn_2 = create_question("Past Question 2.", -5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Past Question 1.>', '<Question: Past Question 2.>'])

class QuestionDetailsViewTests(TestCase):

    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question('Future question.', 5)
        url = reverse('polls:details', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question('Past Question.', -5)
        url = reverse('polls:details', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
