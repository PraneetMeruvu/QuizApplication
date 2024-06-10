from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from account.models import Profile
from quiz.models import UserRank, Quiz, QuizSubmission, Question
from django.contrib.auth.decorators import login_required, user_passes_test
import datetime
from .models import Message
from django.db.models import Count, Q
import math
from django.db.models.functions import ExtractYear

# Create your views here.
def home(request):

    leaderboard_users = UserRank.objects.order_by('rank')[:4]

    if request.user.is_authenticated:
        # request user
        user_object = User.objects.get(username=request.user)
        user_profile = Profile.objects.get(user=user_object)
        context = {"user_profile": user_profile, "leaderboard_users": leaderboard_users}
    else:
        context = {"leaderboard_users": leaderboard_users}

    return render(request, 'welcome.html', context)


@login_required(login_url="login")
def leaderboard_view(request):

    user_object = User.objects.get(username=request.user)
    user_profile = Profile.objects.get(user=user_object)

    leaderboard_users = UserRank.objects.order_by('rank')

    context = {"leaderboard_users": leaderboard_users, "user_profile": user_profile}
    return render(request, "leaderboard.html", context)


def is_superuser(user):
    return user.is_superuser

#@user_passes_test(is_superuser)
@login_required(login_url='login')
def dashboard_view(request):

    user_object = User.objects.get(username=request.user)
    user_profile = Profile.objects.get(user=user_object)


    # Total Number
    total_users = User.objects.all().count()
    total_quizzes = Quiz.objects.all().count()
    total_quiz_submit = QuizSubmission.objects.all().count()
    total_questions = Question.objects.all().count()

    # today_numbers
    today_users = User.objects.filter(date_joined__date=datetime.date.today()).count()
    today_quizzes_objs = Quiz.objects.filter(created_at__date=datetime.date.today())
    today_quizzes = Quiz.objects.filter(created_at__date=datetime.date.today()).count()
    today_quiz_submit = QuizSubmission.objects.filter(submitted_at__date=datetime.date.today()).count()
    today_questions = 0
    for quiz in today_quizzes_objs:
        today_questions += quiz.question_set.count()

    # Gain %
    gain_users = gain_percentage(total_users, today_users)
    gain_quizzes = gain_percentage(total_quizzes, today_quizzes)
    gain_quiz_submit = gain_percentage(total_quiz_submit, today_quiz_submit)
    gain_questions = gain_percentage(total_questions, today_questions)

    # Inbox Messages
    messages = Message.objects.filter(created_at__date=datetime.date.today()).order_by('-created_at')

    # User submissions 
    submissions = QuizSubmission.objects.all().order_by('-submitted_at')


    context = {"user_profile": user_profile, 
               "total_users": total_users,
               "total_quizzes": total_quizzes,
               "total_quiz_submit": total_quiz_submit,
               "total_questions": total_questions,
               "today_users":today_users,
               "today_quizzes":today_quizzes,
               "today_quiz_submit":today_quiz_submit,
               "today_questions":today_questions,
               "gain_users": gain_users,
               "gain_quizzes": gain_quizzes,
               "gain_quiz_submit": gain_quiz_submit,
               "gain_questions": gain_questions,
               "messages": messages,
               "submissions": submissions,
               }
    return render(request, "dashboard.html", context)

def gain_percentage(total, today):
    if total > 0 and today > 0:
        gain = math.floor((today *100)/total)
        return gain

def about_view(request):

    if request.user.is_authenticated:
        # request user
        user_object = User.objects.get(username=request.user)
        user_profile = Profile.objects.get(user=user_object)
        context = {"user_profile": user_profile}
    else:
        context = {}
    return render(request, "about.html", context)


@login_required(login_url='login')
def contact_view(request):

    user_object = User.objects.get(username=request.user)
    user_profile = Profile.objects.get(user=user_object)

    if request.method == "POST":
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        if subject is not None and message is not None:
            form = Message.objects.create(user=request.user, subject=subject, message=message)
            form.save()
            messages.success(request, "We got your message. We will resolve your query soon.")
            return redirect('profile', request.user.username)
        
        else:
            return redirect('contact')
    
    context = {"user_profile": user_profile}
    return render(request, "contact.html", context)


def search_users_view(request):

    query = request.GET.get('q')

    if query:
        users = User.objects.filter(
            Q(username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query)
        ).order_by('date_joined')

    else:
        users = []

    if request.user.is_authenticated:
        # request user
        user_object = User.objects.get(username=request.user)
        user_profile = Profile.objects.get(user=user_object)
        context = {"user_profile": user_profile, "query": query, "users": users}
    else:
        context = {"query": query, "users": users}
    return render(request, "search-users.html", context)