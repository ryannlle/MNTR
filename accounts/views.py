from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, MentorApplicationForm
from django.contrib.auth.models import User
from .models import Mentor


def home(request):
    return render(request, 'home.html')


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})


def search(request):
    query = request.GET.get('q', '').strip()
    mentors = []
    if query:
        mentors = Mentor.objects.filter(approved=True, user__username__icontains=query)[:20]
    return render(request, 'search_results.html', {'query': query, 'mentors': mentors})


def autosuggest(request):
    """Return a small JSON list of suggestions for the search box.
    Suggests matching usernames (and example static suggestions).
    """
    q = request.GET.get('q', '').strip()
    suggestions = []
    if q:
        users = Mentor.objects.filter(approved=True, user__username__icontains=q).select_related('user')[:8]
        suggestions = [u.user.username for u in users]
        # add a couple of helpful static suggestions if none found
        if not suggestions:
            suggestions = [f"{q} study group", f"{q} mentor"]

    return JsonResponse({'query': q, 'suggestions': suggestions})


@login_required
def apply_mentor(request):
    """Allow an existing user to apply to be a mentor or update their application."""
    try:
        mentor = request.user.mentor_profile
    except Mentor.DoesNotExist:
        mentor = None

    if request.method == 'POST':
        form = MentorApplicationForm(request.POST, request.FILES, instance=mentor)
        if form.is_valid():
            m = form.save(commit=False)
            m.user = request.user
            # keep approved False until admin approves
            m.approved = False
            m.save()
            messages.success(request, 'Your mentor application was submitted. An admin will review it.')
            return redirect('home')
    else:
        form = MentorApplicationForm(instance=mentor)

    return render(request, 'apply_mentor.html', {'form': form, 'mentor': mentor})


def top_classes(request):
    # example list of top classes - in a real app this would come from models
    classes = [
        {'code': 'CS-150', 'name': 'CS 150'},
        {'code': 'MATH-20', 'name': 'Math 20'},
        {'code': 'PHYS-101', 'name': 'Physics 101'},
    ]
    return render(request, 'top_classes.html', {'classes': classes})


def top_class_detail(request, course):
    # Show example mentors for a class (placeholder data)
    mentors = Mentor.objects.filter(approved=True)[:6]
    course_display = course.replace('-', ' ')
    return render(request, 'top_class_detail.html', {'course': course_display, 'mentors': mentors})


def top_mentors(request):
    mentors = Mentor.objects.filter(approved=True)[:12]
    return render(request, 'top_mentors.html', {'mentors': mentors})


def leaderboard(request):
    # placeholder leaderboard
    leaders = Mentor.objects.filter(approved=True)[:10]
    return render(request, 'leaderboard.html', {'leaders': leaders})


def ratings(request):
    # placeholder ratings page
    return render(request, 'ratings.html')


def appointments(request):
    # placeholder appointments page
    return render(request, 'appointments.html')
