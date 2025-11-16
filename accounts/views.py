from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, MentorApplicationForm
from .forms import UserForm, ProfileForm
from django.contrib.auth.models import User
from .models import Mentor
from django.db.models import Q
from django.db.models import Value, F, DecimalField
from django.db.models.functions import Coalesce, Least

from .constants import CLASSES as CLASSES_TUPLES

# convert tuples to dicts for templates
classes = [{'code': c[0], 'name': c[1]} for c in CLASSES_TUPLES]

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


def search(request, classes=classes):
    query = request.GET.get('q', '').strip()
    mentors = []
    class_matches = []
    if query:
        # match mentors by username, subjects, or bio (partial, case-insensitive)
        mentors = Mentor.objects.filter(
            approved=True
        ).filter(
            Q(user__username__icontains=query) | Q(subjects__icontains=query) | Q(bio__icontains=query)
        ).select_related('user')[:50]

        # simple class list (kept in sync with top_classes view); search these by code or name
        
        qlow = query.lower()
        for c in classes:
            if qlow in c['code'].lower() or qlow in c['name'].lower():
                class_matches.append(c)
    return render(request, 'search_results.html', {'query': query, 'mentors': mentors, 'classes': class_matches})


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


@login_required
def profile(request):
    user = request.user
    # get or create profile instance
    try:
        profile = user.profile
    except Exception:
        profile = None

    try:
        mentor = user.mentor_profile
    except Mentor.DoesNotExist:
        mentor = None

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        # Always provide a mentor_form so users can opt into mentoring via profile
        mentor_form = MentorApplicationForm(request.POST, request.FILES, instance=mentor)

        forms_ok = user_form.is_valid() and profile_form.is_valid() and mentor_form.is_valid()
        if forms_ok:
            user_form.save()
            p = profile_form.save(commit=False)
            if p and not getattr(p, 'user', None):
                p.user = user
            p.save()

            # Save or create Mentor record
            m = mentor_form.save(commit=False)
            m.user = user
            # keep approved False until admin approves (or retain existing approval)
            if not getattr(m, 'approved', False):
                m.approved = False
            m.save()

            messages.success(request, 'Profile updated.')
            return redirect('profile')
    else:
        user_form = UserForm(instance=user)
        profile_form = ProfileForm(instance=profile)
        # render mentor form even if the user is not yet a mentor so they can select classes
        mentor_form = MentorApplicationForm(instance=mentor)

    return render(request, 'profile.html', {'user_form': user_form, 'profile_form': profile_form, 'mentor_form': mentor_form})


def top_classes(request,classes=classes):
    # example list of top classes - in a real app this would come from models
    
    return render(request, 'top_classes.html', {'classes': classes})


def top_class_detail(request, course):
    # Show mentors who signed up for this class
    # course arrives as the code used in URLs (e.g. 'CS-150')
    mentors = Mentor.objects.filter(approved=True, class_codes__icontains=course).select_related('user')[:12]
    course_display = course.replace('-', ' ')
    return render(request, 'top_class_detail.html', {'course': course_display, 'mentors': mentors})


def top_mentors(request):
    mentors = Mentor.objects.filter(approved=True)[:12]
    return render(request, 'top_mentors.html', {'mentors': mentors})


def leaderboard(request):
    # Sort mentors by rating (treat null as 0), cap ratings at 5, and show top 10
    leaders = (
        Mentor.objects.filter(approved=True)
        # treat null rating as 0 (Decimal), and ensure expressions use Decimal output_field
        .annotate(effective_rating=Coalesce('rating', Value(0, output_field=DecimalField()), output_field=DecimalField()))
        # cap the rating at 5.0
        .annotate(capped_rating=Least(Value(5, output_field=DecimalField()), F('effective_rating'), output_field=DecimalField()))
        .select_related('user')
        .order_by('-capped_rating')[:10]
    )
    return render(request, 'leaderboard.html', {'leaders': leaders})


def ratings(request):
    # placeholder ratings page
    return render(request, 'ratings.html')


def appointments(request):
    # placeholder appointments page
    return render(request, 'appointments.html')



