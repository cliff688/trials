"""The polls app"""
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from .models import Question, Choice
# Create your views here.

def index(request):
    latest_questions = Question.objects.order_by('-publication_date')[:5]
    context={
        'latest_question_list':latest_questions,
    }
    return render(request, 'polls/index.html', context)

def details(request,question_id):
    question=Question.objects.get(pk=question_id)
    context={'question':question}
    return render(request, 'polls/details.html', context)

def results(request, question_id):
    question = Question.objects.get(pk=question_id)
    return render(request,'polls/results.html',{'question':question})

def vote(request,question_id):
    question = get_object_or_404(Question,pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except(KeyError, Choice.DoesNotExist):
        return render(request, 'polls/details.html', {
            'question':question,
            'error_message':'You did not select a choice',
        })
    else:
        selected_choice.votes+=1
        selected_choice.save()
        return HttpResponseRedirect(reverse('polls:results',args=(question.id,)))
