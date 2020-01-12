import random

from django.test import TestCase

import datetime

from django.urls import reverse
from django.utils import timezone
from .models import Question
import string
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

def create_question_with_choices(text, days, minutes=0, choice='Choice is provided here'):
    time = timezone.now() + datetime.timedelta(days=days, minutes=minutes)
    q = Question(question_text=text, publication_date=time)
    q.save()
    q.choice_set.create(choice_text=choice, votes=0)

def create_question_without_choices(text, days, minutes=0):
    time = timezone.now() + datetime.timedelta(days=days, minutes=minutes)
    return Question.objects.create(question_text=text, publication_date=time)

def create_question_to_reference(text, days, minutes=0):
    time = timezone.now() + datetime.timedelta(days=days, minutes=minutes)
    question = Question.objects.create(question_text=text, publication_date=time)
    question.choice_set.create(choice_text="Text choice is provided here", votes=0)

    return  question

def random_old_question_args():
    text = ''
    word_count = random.choice(range(3, 10))
    for i in range(word_count):
        word_length = random.choice(range(1, 8))
        random_letters = list(string.ascii_lowercase)
        random.shuffle(random_letters)
        word = ''.join(random_letters[:word_length])
        if text == '':
            text += word
        else:
            text += ' ' + word
    text = text.capitalize()
    return text + '?', random.choice(range(-1, -10, -1))

def generate_n_random_old_questions(n):
    for i in range(n):
        create_question_with_choices(*random_old_question_args())

class QuestionIndexViewTests(TestCase):
    def test_last_five_published_questions_are_displayed(self):
        """
        if more than five questions are available only the most recent questions are displayed
        """
        generate_n_random_old_questions(5)
        #add a recent question with a publication date 10 minutes ago
        create_question_with_choices("This is a new question", days=0, minutes=-10)
        create_question_with_choices("This is another new question", days=0, minutes=-1)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "This is a new question")
        self.assertContains(response, "This is another new question")

    def test_questions_without_choices(self):
        """Questions with no choices should not be displayed"""
        create_question_without_choices("Question has no choice", -1)
        response = self.client.get(reverse('polls:index'))
        self.assertNotContains(response, "Question has no choice")


    def test_no_questions(self):
        """if no question exist, an appropriate message is displayed"""
        response=self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No polls are available')
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_questions(self):
        """Questions with a past publication date are displayed in the page"""
        create_question_with_choices("Past question.", -30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Past question.>'])

    def test_future_questions(self):
        """"""
        create_question_with_choices("Future question.", 10)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, 'No polls are available')
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_and_past_questions(self):
        """The future question should be excluded from the context"""
        create_question_with_choices("Future question.", 30)
        create_question_with_choices("Past question.", -30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Past question.>'])

    def test_two_past_questions(self):
        """Both should be in the context"""
        create_question_with_choices("Past Question 1.", -10)
        create_question_with_choices("Past Question 2.", -5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Past Question 2.>', '<Question: Past Question 1.>'])

class QuestionDetailsViewTests(TestCase):

    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question_to_reference('Future question.', 5)
        url = reverse('polls:details', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question_to_reference('Past Question.', -5)
        url = reverse('polls:details', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

class VoteDetailsViewTests(TestCase):
    pass
