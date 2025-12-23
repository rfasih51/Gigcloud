from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from home.models import Contact
from django.contrib import messages
from .models import Project, Skill, Client, Experience, Education, UserProfile, Category
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q


# Create your views here.
def greet(request):
    projects = Project.objects.all().order_by('-created_at')
    categories = Category.objects.all()
    return render(request,'index.html',{'projects': projects, 'categories': categories})

def explore(request):
    # Redirect old resume page to gigs listing
    return redirect('gigs')


def gigs_list(request):
    """Render a professional Gigs / Projects listing with category filtering."""
    from .models import Category
    category_id = request.GET.get('category')
    search = request.GET.get('q', '').strip()

    projects = Project.objects.all().order_by('-created_at')

    if category_id:
        try:
            projects = projects.filter(categories__id=int(category_id))
        except (ValueError, TypeError):
            pass

    if search:
        projects = projects.filter(Q(title__icontains=search) | Q(description__icontains=search) | Q(client__name__icontains=search) | Q(skills__name__icontains=search)).distinct()

    categories = Category.objects.all()
    return render(request, 'projects.html', {'projects': projects, 'categories': categories, 'selected_category': category_id, 'search_query': search})


def gigs_api(request):
    """Simple JSON endpoint to fetch gigs/projects (supports ?category= and ?q=)."""
    category_id = request.GET.get('category')
    search = request.GET.get('q', '').strip()

    projects = Project.objects.all().order_by('-created_at')
    if category_id:
        try:
            projects = projects.filter(categories__id=int(category_id))
        except (ValueError, TypeError):
            pass

    if search:
        projects = projects.filter(Q(title__icontains=search) | Q(description__icontains=search) | Q(client__name__icontains=search) | Q(skills__name__icontains=search)).distinct()

    data = []
    for p in projects:
        data.append({
            'id': p.id,
            'title': p.title,
            'description': p.description,
            'image': p.image.url if p.image else None,
            'client': p.client.name if p.client else None,
            'skills': [s.name for s in p.skills.all()],
            'categories': [c.name for c in p.categories.all()],
            'owner': p.owner.username if p.owner else None,
            'created_at': p.created_at.isoformat(),
        })
    return JsonResponse({'projects': data})

# New login view for admin
def admin_login(request):
    if request.user.is_authenticated:
        return redirect('admin')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('admin')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'admin_login.html')

# Add login_required decorator to protect admin view
@login_required(login_url='admin_login')
def admin(request):
    total_contacts = Contact.objects.count()
    total_projects = Project.objects.count()
    projects = Project.objects.all().order_by('-created_at')
    return render(request,'admin.html',{'total_contacts': total_contacts, 'total_projects': total_projects, 'projects': projects})

# Add logout view
def admin_logout(request):
    logout(request)
    return redirect('admin_login')

@login_required(login_url='admin_login')
def mycontacts(request):
    contact = Contact.objects.all()
    return render(request,'mycontacts.html',{'Contacts': contact})


@login_required(login_url='admin_login')
def addnewproject(request):
    clients = Client.objects.all()
    clients = Client.objects.all()
    skills = Skill.objects.all()
    if request.method == 'POST':
        title = request.POST.get('project_title')
        description = request.POST.get('project_description')
        image = request.FILES.get('project_image')
        client_id = request.POST.get('client')
        skill_ids = request.POST.getlist('skills')
        client = Client.objects.get(id=client_id) if client_id else None
        price = request.POST.get('price') or 0
        currency = request.POST.get('currency') or 'USD'
        delivery_time = request.POST.get('delivery_time') or 3
        revisions = request.POST.get('revisions') or 1
        offers_consultation = True if request.POST.get('offers_consultation') == 'on' else False
        project = Project.objects.create(
            title=title,
            description=description,
            image=image,
            client=client,
            owner=request.user,
            price=price,
            currency=currency,
            delivery_time=delivery_time,
            revisions=revisions,
            offers_consultation=offers_consultation
        )
        if skill_ids:
            project.skills.set(skill_ids)
        project.save()
        return redirect('admin')
    return render(request, 'addnewproject.html', {'clients': clients, 'skills': skills})

def contactus(request):
    if request.method == 'POST':
        firstName  = request.POST.get('firstName')
        lastName  = request.POST.get('lastName')
        email  = request.POST.get('email')
        message  = request.POST.get('message')
        image = request.FILES.get('image')

        contactme  = Contact(firstName = firstName , lastName = lastName, email = email, message =message, image =image)
        contactme.save()                                                               
    return render(request,'contact.html')

@login_required(login_url='admin_login')
def delete(request,id):
    dell = Contact.objects.get(id=id)
    dell.delete()
    return redirect('/mycontacts')

@login_required(login_url='admin_login')
def update(request,id):
    contact = Contact.objects.get(id=id)
    return render(request, 'update.html',{'contact':contact})

@login_required(login_url='admin_login')
def do_update(request,id):
    id = Contact.objects.get(id=id)
    if request.method == 'POST':
        id.firstName  = request.POST.get('firstName')
        id.lastName  = request.POST.get('lastName')
        id.email  = request.POST.get('email')
        id.message  = request.POST.get('message')
        id.image = request.FILES.get('image')

        id.save()
    return redirect('/mycontacts')

@login_required(login_url='admin_login')
def update_project(request, id):
    project = Project.objects.get(id=id)
    clients = Client.objects.all()
    skills = Skill.objects.all()
    if request.method == 'POST':
        project.title = request.POST.get('project_title')
        project.description = request.POST.get('project_description')
        if request.FILES.get('project_image'):
            project.image = request.FILES.get('project_image')
        # gig-specific fields
        project.price = request.POST.get('price') or project.price
        project.currency = request.POST.get('currency') or project.currency
        project.delivery_time = request.POST.get('delivery_time') or project.delivery_time
        project.revisions = request.POST.get('revisions') or project.revisions
        project.offers_consultation = True if request.POST.get('offers_consultation') == 'on' else project.offers_consultation
        client_id = request.POST.get('client')
        skill_ids = request.POST.getlist('skills')
        project.client = Client.objects.get(id=client_id) if client_id else None
        project.save()
        if skill_ids:
            project.skills.set(skill_ids)
        else:
            project.skills.clear()
        return redirect('admin')
    return render(request, 'addnewproject.html', {'project': project, 'clients': clients, 'skills': skills})

@login_required(login_url='admin_login')
def delete_project(request, id):
    project = Project.objects.get(id=id)
    project.delete()
    return redirect('admin')



@csrf_exempt
def ajax_add_skill(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            skill, created = Skill.objects.get_or_create(name=name)
            return JsonResponse({'id': skill.id, 'name': skill.name, 'created': created})
    return JsonResponse({'error': 'Invalid request'}, status=400)

def project_detail(request, id):
    project = Project.objects.get(id=id)
    return render(request, 'project_detail.html', {'project': project})

def user_login(request):
    if request.user.is_authenticated:
        return redirect('greet')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('greet')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    return redirect('greet')

def register(request):
    if request.user.is_authenticated:
        return redirect('greet')
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if password1 != password2:
            messages.error(request, 'Passwords do not match')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
        else:
            user = User.objects.create_user(username=username, email=email, password=password1)
            login(request, user)
            return redirect('greet')
    return render(request, 'register.html')

@login_required
def profile(request):
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)
    projects = user.projects.all().order_by('-created_at')
    experiences = user.experiences.all().order_by('-start_date')
    educations = user.educations.all().order_by('-start_date')
    return render(request, 'profile.html', {'user': user, 'profile': profile, 'projects': projects, 'experiences': experiences, 'educations': educations})

@login_required
def edit_profile(request):
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)
    if request.method == 'POST':
        user.email = request.POST.get('email')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.save()
        profile.about_me = request.POST.get('about_me', '')
        profile.languages = request.POST.get('languages', '')
        profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    return render(request, 'edit_profile.html', {'user': user, 'profile': profile})

@login_required
def user_projects(request):
    projects = request.user.projects.all().order_by('-created_at')
    return render(request, 'user_projects.html', {'projects': projects})

@login_required
def add_project(request):
    from .models import Skill, Client
    skills = Skill.objects.all()
    clients = Client.objects.all()
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        client_id = request.POST.get('client')
        skill_ids = request.POST.getlist('skills')
        client = Client.objects.get(id=client_id) if client_id else None
        price = request.POST.get('price') or 0
        currency = request.POST.get('currency') or 'USD'
        delivery_time = request.POST.get('delivery_time') or 3
        revisions = request.POST.get('revisions') or 1
        offers_consultation = True if request.POST.get('offers_consultation') == 'on' else False
        project = Project.objects.create(
            title=title,
            description=description,
            image=image,
            client=client,
            owner=request.user,
            price=price,
            currency=currency,
            delivery_time=delivery_time,
            revisions=revisions,
            offers_consultation=offers_consultation
        )
        if skill_ids:
            project.skills.set(skill_ids)
        project.save()
        messages.success(request, 'Project added!')
        return redirect('user_projects')
    return render(request, 'add_project.html', {'skills': skills, 'clients': clients})

@login_required
def edit_project(request, id):
    from .models import Skill, Client
    project = Project.objects.get(id=id, owner=request.user)
    skills = Skill.objects.all()
    clients = Client.objects.all()
    if request.method == 'POST':
        project.title = request.POST.get('title')
        project.description = request.POST.get('description')
        if request.FILES.get('image'):
            project.image = request.FILES.get('image')
        # gig-specific fields
        project.price = request.POST.get('price') or project.price
        project.currency = request.POST.get('currency') or project.currency
        project.delivery_time = request.POST.get('delivery_time') or project.delivery_time
        project.revisions = request.POST.get('revisions') or project.revisions
        project.offers_consultation = True if request.POST.get('offers_consultation') == 'on' else project.offers_consultation
        client_id = request.POST.get('client')
        skill_ids = request.POST.getlist('skills')
        project.client = Client.objects.get(id=client_id) if client_id else None
        project.save()
        if skill_ids:
            project.skills.set(skill_ids)
        else:
            project.skills.clear()
        messages.success(request, 'Project updated!')
        return redirect('user_projects')
    return render(request, 'edit_project.html', {'project': project, 'skills': skills, 'clients': clients})

@login_required
def delete_project_user(request, id):
    project = Project.objects.get(id=id, owner=request.user)
    project.delete()
    messages.success(request, 'Project deleted!')
    return redirect('user_projects')

@login_required
def add_experience(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        company = request.POST.get('company')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        description = request.POST.get('description')
        Experience.objects.create(user=request.user, title=title, company=company, start_date=start_date, end_date=end_date, description=description)
        messages.success(request, 'Experience added!')
        return redirect('profile')
    return render(request, 'add_experience.html')

@login_required
def edit_experience(request, id):
    exp = Experience.objects.get(id=id, user=request.user)
    if request.method == 'POST':
        exp.title = request.POST.get('title')
        exp.company = request.POST.get('company')
        exp.start_date = request.POST.get('start_date')
        exp.end_date = request.POST.get('end_date')
        exp.description = request.POST.get('description')
        exp.save()
        messages.success(request, 'Experience updated!')
        return redirect('profile')
    return render(request, 'edit_experience.html', {'exp': exp})

@login_required
def delete_experience(request, id):
    exp = Experience.objects.get(id=id, user=request.user)
    exp.delete()
    messages.success(request, 'Experience deleted!')
    return redirect('profile')

@login_required
def add_education(request):
    if request.method == 'POST':
        degree = request.POST.get('degree')
        institution = request.POST.get('institution')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        description = request.POST.get('description')
        Education.objects.create(user=request.user, degree=degree, institution=institution, start_date=start_date, end_date=end_date, description=description)
        messages.success(request, 'Education added!')
        return redirect('profile')
    return render(request, 'add_education.html')

@login_required
def edit_education(request, id):
    edu = Education.objects.get(id=id, user=request.user)
    if request.method == 'POST':
        edu.degree = request.POST.get('degree')
        edu.institution = request.POST.get('institution')
        edu.start_date = request.POST.get('start_date')
        edu.end_date = request.POST.get('end_date')
        edu.description = request.POST.get('description')
        edu.save()
        messages.success(request, 'Education updated!')
        return redirect('profile')
    return render(request, 'edit_education.html', {'edu': edu})

@login_required
def delete_education(request, id):
    edu = Education.objects.get(id=id, user=request.user)
    edu.delete()
    messages.success(request, 'Education deleted!')
    return redirect('profile')

@login_required
def public_profile(request):
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)
    projects = user.projects.all().order_by('-created_at')
    experiences = user.experiences.all().order_by('-start_date')
    educations = user.educations.all().order_by('-start_date')
    return render(request, 'public_profile.html', {
        'user': user,
        'profile': profile,
        'projects': projects,
        'experiences': experiences,
        'educations': educations
    })

def user_profile_view(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        profile, created = UserProfile.objects.get_or_create(user=user)
        projects = user.projects.all().order_by('-created_at')
        experiences = user.experiences.all().order_by('-start_date')
        educations = user.educations.all().order_by('-start_date')
        
        return render(request, 'public_profile.html', {
            'user': user,
            'profile': profile,
            'projects': projects,
            'experiences': experiences,
            'educations': educations,
            'is_public': True
        })
    except User.DoesNotExist:
        messages.error(request, 'User profile not found')
        return redirect('greet')


def users_list(request):
    """List user profile cards. Clicking a card goes to the user's public profile page."""
    users = User.objects.all()
    users_data = []
    for u in users:
        profile, _ = UserProfile.objects.get_or_create(user=u)
        projects = u.projects.all()
        # aggregate distinct skills from user's projects
        skills = Skill.objects.filter(projects__owner=u).distinct()
        avatar = None
        first_proj = projects.first()
        try:
            if first_proj and first_proj.image:
                avatar = first_proj.image.url
        except Exception:
            avatar = None
        if not avatar:
            avatar = f"https://i.pravatar.cc/150?u={u.id}"

        users_data.append({
            'id': u.id,
            'username': u.username,
            'full_name': f"{u.first_name} {u.last_name}".strip(),
            'profile': profile,
            'skills': skills,
            'projects_count': projects.count(),
            'avatar': avatar,
        })

    return render(request, 'users.html', {'users_data': users_data})
