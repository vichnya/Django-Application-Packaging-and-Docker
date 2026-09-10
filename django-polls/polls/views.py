from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views import View, generic
from django.utils import timezone

from .models import Choice, Question
from .forms import CreateQuestionForm

class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[
               :5
               ]


class DetailView(generic.DetailView):
    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

    model = Question
    template_name = "polls/detail.html"

class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"

class CreateView(generic.FormView):
    form_class = CreateQuestionForm
    template_name = "polls/create_question.html"
    success_url = reverse_lazy('polls:index')

    def form_valid(self, form):
        question_text = form.cleaned_data['question_text']
        question, created = Question.objects.get_or_create(question_text=question_text, pub_date=timezone.now())

        choice_texts = form.cleaned_data['choice_texts'].split('\n')

        for choice_text in choice_texts:
            choice_text = choice_text.strip()
            if choice_text:
                Choice.objects.create(question=question, choice_text=choice_text)

        return HttpResponseRedirect(self.success_url)

class StatisticsView(View):
    def get(self, request, *args, **kwargs):
        context = {'message': 'Привет, это GET-запрос!'}
        return render(request, 'polls/statistics.html', context)

    def post(self, request, *args, **kwargs):
        context = {'message': 'Привет, это POST-запрос!'}
        return render(request, 'polls/statistics.html', context)

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))


# =================================================================================

from rest_framework.views import APIView
# from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import parsers, status
from datetime import datetime, timedelta
from django.utils import timezone
from .serializers import QuestionSerializer
from .models import Question


class QuestionView(APIView):
    parser_classes = (parsers.JSONParser,)

    def post(self, request, format=None):
        # Получение данных из тела POST-запроса
        request_data = request.data

        date_range_provided = ('publication-dates' in request_data) \
                              and ('from' in request_data['publication-dates'] and 'to' in request_data[
            'publication-dates'])

        date_range = None
        if date_range_provided:
            publication_dates = request_data['publication-dates']
            date_from = datetime.strptime(publication_dates['from'], '%Y-%m-%d')
            date_from = date_from.replace(hour=0, minute=0, second=0)
            date_to = datetime.strptime(publication_dates['to'], '%Y-%m-%d')
            date_to = date_to.replace(hour=23, minute=59, second=59)
            date_range = [date_from, date_to]
        else:
            date_now = timezone.now()
            date_from = (date_now - timedelta(days=60)).replace(hour=0, minute=0, second=0)
            date_to = date_now.replace(hour=23, minute=59, second=59)
            date_range = [date_from, date_to]

        tz = timezone.get_current_timezone()

        # Запрос в базу данных по интервалу дат публикации
        questions = Question.objects.filter(pub_date__range=date_range)

        print(f"Questions: {questions}")

        # Сериализация данных и создание нового вопроса
        question_serializer = QuestionSerializer(questions, many=True)
        # question_serializer.is_valid()
        # question_serializer.save()
        # print(f"Serializer errors: {question_serializer.errors}")
        # if question_serializer.is_valid():
        #     question_serializer.save()
        #     print("SAVED")
        # else:

        print(f"Serialized: {question_serializer.data}")

        response_data = {
            'publication-dates': {
                'from': date_range[0],
                'to': date_range[1]
            },
            'questions': question_serializer.data
        }

        return Response(response_data, status=status.HTTP_200_OK)

        # return Response(question_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# =================================================================================


from django.utils import timezone
from django.http import JsonResponse
from django.contrib import admin

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Question, Choice

import matplotlib.pyplot as plt
import io


class QuestionStatsAPIView(APIView):
    def get(self, request, pk):
        try:
            question = Question.objects.get(pk=pk)
        except Question.DoesNotExist:
            return Response("Question does not exist", status=status.HTTP_404_NOT_FOUND)

        choices = question.choice_set.all()
        total_votes = sum(choice.votes for choice in choices)

        stats = {
            'question': question.question_text,
            'total_votes': total_votes,
            'choices': []
        }

        for choice in choices:
            choice_percentage = (choice.votes / total_votes) * 100 if total_votes != 0 else 0
            stats['choices'].append({
                'choice_text': choice.choice_text,
                'votes': choice.votes,
                'percentage': round(choice_percentage, 2)
            })

        most_popular_choice = max(choices, key=lambda choice: choice.votes)
        least_popular_choice = min(choices, key=lambda choice: choice.votes)

        stats['most_popular_choice'] = most_popular_choice.choice_text
        stats['least_popular_choice'] = least_popular_choice.choice_text

        fig, ax = plt.subplots()
        plt.style.use('ggplot')
        ax.bar([choice.choice_text for choice in choices], [choice.votes for choice in choices])
        plt.xticks(rotation=20)
        plt.xlabel('Choices')
        plt.ylabel('Votes')
        plt.title('Votes Distribution')
        plt.subplots_adjust(bottom=0.2)
        buffer = io.BytesIO()
        plt.savefig(buffer, format='svg')
        plt.close(fig)
        buffer.seek(0)

        stats['histogram_svg'] = buffer.getvalue().decode()

        return Response(stats)
