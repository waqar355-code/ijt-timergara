from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Halqa, Member, ElqaUpdate


# ─── ELQA MAP ─────────────────────────────
ELQA_USER_MAP = {
    'admin_sindhakhall': 'sindhakhall',
    'admin_talash':      'talash',
    'admin_collage':     'collage',
    'admin_shaher':      'shaher',
    'admin_bazam':       'bazam',
    'admin_colleges':    'colleges',
}


def get_user_elqa(user):
    if user.is_superuser:
        return 'all'
    return ELQA_USER_MAP.get(user.username)


# ─── LOGIN ────────────────────────────────
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )
        if user:
            login(request, user)
            if user.is_superuser:
                return redirect('home')
            elqa = get_user_elqa(user)
            if elqa:
                return redirect('elqa_page', elqa_key=elqa)
            return redirect('home')
        messages.error(request, "Invalid username or password")
    return render(request, 'login.html')


# ─── LOGOUT ───────────────────────────────
def logout_view(request):
    logout(request)
    return redirect('login')


# ─── HOME ─────────────────────────────────
@login_required
def home(request):
    return render(request, 'home.html')


# ─── TEAM ─────────────────────────────────
@login_required
def team(request):
    return render(request, 'about-timergara-moqam.html')


# ─── UPDATES ──────────────────────────────
@login_required
def updates(request):
    if request.user.is_superuser:
        is_admin = True
        elqa_key = request.GET.get('elqa', 'colleges')
    else:
        elqa_key = get_user_elqa(request.user)
        is_admin = elqa_key is not None

    all_updates = ElqaUpdate.objects.all().order_by('-created_at')
    return render(request, 'updates.html', {
        'updates':      all_updates,
        'is_admin':     is_admin,
        'elqa_key':     elqa_key,
        'is_superuser': request.user.is_superuser,
        'all_elqas':    ['collage', 'colleges', 'bazam', 'shaher', 'talash', 'sindhakhall'],
    })


# ─── ADMIN CHECK DECORATOR ────────────────
def admin_required(view_func):
    def wrapper(request, elqa_key, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        # superuser can access everything
        if request.user.is_superuser:
            return view_func(request, elqa_key, *args, **kwargs)
        if get_user_elqa(request.user) != elqa_key:
            messages.error(request, "Not allowed")
            return redirect('home')
        return view_func(request, elqa_key, *args, **kwargs)
    return wrapper


# ─── ELQA PAGE ────────────────────────────
@login_required
def elqa_page(request, elqa_key):
    template_map = {
        'sindhakhall': 'elqa_sindhakhall.html',
        'talash':      'elqa_talash.html',
        'collage':     'elqa_collage.html',
        'shaher':      'elqa_shaher.html',
        'bazam':       'bazam.html',
        'colleges':    'elqa_colleges.html',
    }
    template = template_map.get(elqa_key)
    if not template:
        return redirect('home')

    # superuser is admin everywhere
    if request.user.is_superuser:
        is_admin = True
    else:
        is_admin = get_user_elqa(request.user) == elqa_key

    if elqa_key in ['collage', 'colleges', 'bazam', 'shaher', 'talash', 'sindhakhall']:
        total_karkunan = Member.objects.filter(elqa=elqa_key, member_type='karkun').count()
        total_rufaqa   = Member.objects.filter(elqa=elqa_key, member_type='rafiq').count()
        total_umeedwar = Member.objects.filter(elqa=elqa_key, member_type='umeedwar').count()
    else:
        total_karkunan = total_rufaqa = total_umeedwar = 0

    context = {
        'elqa_key':       elqa_key,
        'is_admin':       is_admin,
        'halqas':         Halqa.objects.filter(elqa=elqa_key),
        'members':        Member.objects.filter(elqa=elqa_key),
        'updates':        ElqaUpdate.objects.filter(elqa=elqa_key),
        'total_karkunan': total_karkunan,
        'total_rufaqa':   total_rufaqa,
        'total_umeedwar': total_umeedwar,
    }
    return render(request, template, context)


# ─── ADD HALQA ────────────────────────────
@admin_required
def add_halqa(request, elqa_key):
    if request.method == "POST":
        name = request.POST.get("name")
        if name:
            Halqa.objects.create(elqa=elqa_key, name=name)
    return redirect('elqa_page', elqa_key=elqa_key)


# ─── DELETE HALQA ─────────────────────────
@admin_required
def delete_halqa(request, elqa_key, pk):
    Halqa.objects.filter(id=pk, elqa=elqa_key).delete()
    return redirect('elqa_page', elqa_key=elqa_key)


# ─── ADD MEMBER (normal form) ─────────────
@admin_required
def add_member(request, elqa_key):
    if request.method == "POST":
        halqa_id    = request.POST.get("halqa_id")
        member_type = request.POST.get("member_type", "karkun")
        Member.objects.create(
            elqa        = elqa_key,
            halqa_id    = halqa_id if halqa_id else None,
            name        = request.POST.get("name"),
            member_type = member_type,
            role        = request.POST.get("role"),
            photo       = request.FILES.get("photo")
        )
    return redirect('elqa_page', elqa_key=elqa_key)


# ─── ADD MEMBER AJAX ──────────────────────
@login_required
def add_member_ajax(request, elqa_key):
    if request.method == 'POST':
        name        = request.POST.get('name', '').strip()
        member_type = request.POST.get('member_type', 'karkun')
        halqa_id    = request.POST.get('halqa_id', '')

        if not name:
            return JsonResponse({'success': False, 'error': 'Name required'})

        # superuser or elqa admin can add
        if not request.user.is_superuser and get_user_elqa(request.user) != elqa_key:
            return JsonResponse({'success': False, 'error': 'Not allowed'})

        member = Member.objects.create(
            elqa        = elqa_key,
            halqa_id    = halqa_id if halqa_id else None,
            name        = name,
            member_type = member_type,
        )

        karkunan = Member.objects.filter(halqa_id=halqa_id, member_type='karkun').count()
        rufaqa   = Member.objects.filter(halqa_id=halqa_id, member_type='rafiq').count()
        umeedwar = Member.objects.filter(halqa_id=halqa_id, member_type='umeedwar').count()

        return JsonResponse({
            'success':   True,
            'member_id': member.id,
            'name':      member.name,
            'karkunan':  karkunan,
            'rufaqa':    rufaqa,
            'umeedwar':  umeedwar,
        })

    return JsonResponse({'success': False, 'error': 'POST required'})


# ─── DELETE MEMBER ────────────────────────
@admin_required
def delete_member(request, elqa_key, pk):
    Member.objects.filter(id=pk, elqa=elqa_key).delete()
    return redirect('elqa_page', elqa_key=elqa_key)


# ─── ADD UPDATE ───────────────────────────
@admin_required
def add_update(request, elqa_key):
    if request.method == "POST":
        title   = request.POST.get("title", "").strip()
        content = request.POST.get("content", "").strip()
        image   = request.FILES.get("image")
        if title and content:
            ElqaUpdate.objects.create(
                elqa    = elqa_key,
                title   = title,
                content = content,
                image   = image
            )
    return redirect('updates')


# ─── DELETE UPDATE ────────────────────────
@admin_required
def delete_update(request, elqa_key, pk):
    ElqaUpdate.objects.filter(id=pk, elqa=elqa_key).delete()
    return redirect('updates')


# ─── COLLEGES HOME ────────────────────────
@login_required
def colleges_home(request):
    elqa_key = 'colleges'
    total_karkunan = Member.objects.filter(elqa=elqa_key, member_type='karkun').count()
    total_rufaqa   = Member.objects.filter(elqa=elqa_key, member_type='rafiq').count()
    total_umeedwar = Member.objects.filter(elqa=elqa_key, member_type='umeedwar').count()
    halqas         = Halqa.objects.filter(elqa=elqa_key)
    return render(request, 'elqa_colleges.html', {
        'total_karkunan': total_karkunan,
        'total_rufaqa':   total_rufaqa,
        'total_umeedwar': total_umeedwar,
        'halqas':         halqas,
        'is_admin':       get_user_elqa(request.user) == elqa_key,
    })


# ─── AJAX: GET HALQA COUNTS + NAMES ───────
@login_required
def get_halqa_counts(request):
    halqa_id = request.GET.get('halqa_id', '')
    elqa_key = request.GET.get('elqa_key', 'colleges')

    if halqa_id:
        karkunan_qs = Member.objects.filter(halqa_id=halqa_id, member_type='karkun').values('id', 'name')
        rufaqa_qs   = Member.objects.filter(halqa_id=halqa_id, member_type='rafiq').values('id', 'name')
        umeedwar_qs = Member.objects.filter(halqa_id=halqa_id, member_type='umeedwar').values('id', 'name')
    else:
        karkunan_qs = Member.objects.filter(elqa=elqa_key, member_type='karkun').values('id', 'name')
        rufaqa_qs   = Member.objects.filter(elqa=elqa_key, member_type='rafiq').values('id', 'name')
        umeedwar_qs = Member.objects.filter(elqa=elqa_key, member_type='umeedwar').values('id', 'name')

    return JsonResponse({
        'karkunan': list(karkunan_qs),
        'rufaqa':   list(rufaqa_qs),
        'umeedwar': list(umeedwar_qs),
    })




























































































































'''from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Halqa, Member, ElqaUpdate


# ─── ELQA MAP ─────────────────────────────
ELQA_USER_MAP = {
    'admin_sindhakhall': 'sindhakhall',
    'admin_talash':      'talash',
    'admin_collage':     'collage',
    'admin_shaher':      'shaher',
    'admin_bazam':       'bazam',
    'admin_colleges':    'colleges',
}


def get_user_elqa(user):
    return ELQA_USER_MAP.get(user.username)


# ─── LOGIN ────────────────────────────────
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )
        if user:
            login(request, user)
            elqa = get_user_elqa(user)
            if elqa:
                return redirect('elqa_page', elqa_key=elqa)
            return redirect('home')
        messages.error(request, "Invalid username or password")
    return render(request, 'login.html')


# ─── LOGOUT ───────────────────────────────
def logout_view(request):
    logout(request)
    return redirect('login')


# ─── HOME ─────────────────────────────────
@login_required
def home(request):
    return render(request, 'home.html')


# ─── TEAM ─────────────────────────────────
@login_required
def team(request):
    return render(request, 'about-timergara-moqam.html')


# ─── UPDATES ──────────────────────────────
@login_required
def updates(request):
    elqa_key = get_user_elqa(request.user)
    is_admin = elqa_key is not None
    all_updates = ElqaUpdate.objects.all().order_by('-created_at')
    return render(request, 'updates.html', {
        'updates':  all_updates,
        'is_admin': is_admin,
        'elqa_key': elqa_key,
    })


# ─── ADMIN CHECK DECORATOR ────────────────
def admin_required(view_func):
    def wrapper(request, elqa_key, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if get_user_elqa(request.user) != elqa_key:
            messages.error(request, "Not allowed")
            return redirect('home')
        return view_func(request, elqa_key, *args, **kwargs)
    return wrapper


# ─── ELQA PAGE ────────────────────────────
@login_required
def elqa_page(request, elqa_key):
    template_map = {
        'sindhakhall': 'elqa_sindhakhall.html',
        'talash':      'elqa_talash.html',
        'collage':     'elqa_collage.html',
        'shaher':      'elqa_shaher.html',
        'bazam':       'bazam.html',
        'colleges':    'elqa_colleges.html',
    }
    template = template_map.get(elqa_key)
    if not template:
        return redirect('home')

    is_admin = get_user_elqa(request.user) == elqa_key

    if elqa_key in ['collage', 'colleges', 'bazam', 'shaher', 'talash', 'sindhakhall']:
        total_karkunan = Member.objects.filter(elqa=elqa_key, member_type='karkun').count()
        total_rufaqa   = Member.objects.filter(elqa=elqa_key, member_type='rafiq').count()
        total_umeedwar = Member.objects.filter(elqa=elqa_key, member_type='umeedwar').count()
    else:
        total_karkunan = total_rufaqa = total_umeedwar = 0

    context = {
        'elqa_key':       elqa_key,
        'is_admin':       is_admin,
        'halqas':         Halqa.objects.filter(elqa=elqa_key),
        'members':        Member.objects.filter(elqa=elqa_key),
        'updates':        ElqaUpdate.objects.filter(elqa=elqa_key),
        'total_karkunan': total_karkunan,
        'total_rufaqa':   total_rufaqa,
        'total_umeedwar': total_umeedwar,
    }
    return render(request, template, context)


# ─── ADD HALQA ────────────────────────────
@admin_required
def add_halqa(request, elqa_key):
    if request.method == "POST":
        name = request.POST.get("name")
        if name:
            Halqa.objects.create(elqa=elqa_key, name=name)
    return redirect('elqa_page', elqa_key=elqa_key)


# ─── DELETE HALQA ─────────────────────────
@admin_required
def delete_halqa(request, elqa_key, pk):
    Halqa.objects.filter(id=pk, elqa=elqa_key).delete()
    return redirect('elqa_page', elqa_key=elqa_key)


# ─── ADD MEMBER (normal form) ─────────────
@admin_required
def add_member(request, elqa_key):
    if request.method == "POST":
        halqa_id    = request.POST.get("halqa_id")
        member_type = request.POST.get("member_type", "karkun")
        Member.objects.create(
            elqa        = elqa_key,
            halqa_id    = halqa_id if halqa_id else None,
            name        = request.POST.get("name"),
            member_type = member_type,
            role        = request.POST.get("role"),
            photo       = request.FILES.get("photo")
        )
    return redirect('elqa_page', elqa_key=elqa_key)


# ─── ADD MEMBER AJAX ──────────────────────
@login_required
def add_member_ajax(request, elqa_key):
    if request.method == 'POST':
        name        = request.POST.get('name', '').strip()
        member_type = request.POST.get('member_type', 'karkun')
        halqa_id    = request.POST.get('halqa_id', '')

        if not name:
            return JsonResponse({'success': False, 'error': 'Name required'})

        if get_user_elqa(request.user) != elqa_key and not request.user.is_superuser:
            return JsonResponse({'success': False, 'error': 'Not allowed'})

        member = Member.objects.create(
            elqa        = elqa_key,
            halqa_id    = halqa_id if halqa_id else None,
            name        = name,
            member_type = member_type,
        )

        karkunan = Member.objects.filter(halqa_id=halqa_id, member_type='karkun').count()
        rufaqa   = Member.objects.filter(halqa_id=halqa_id, member_type='rafiq').count()
        umeedwar = Member.objects.filter(halqa_id=halqa_id, member_type='umeedwar').count()

        return JsonResponse({
            'success':   True,
            'member_id': member.id,
            'name':      member.name,
            'karkunan':  karkunan,
            'rufaqa':    rufaqa,
            'umeedwar':  umeedwar,
        })

    return JsonResponse({'success': False, 'error': 'POST required'})


# ─── DELETE MEMBER ────────────────────────
@admin_required
def delete_member(request, elqa_key, pk):
    Member.objects.filter(id=pk, elqa=elqa_key).delete()
    return redirect('elqa_page', elqa_key=elqa_key)


# ─── ADD UPDATE ───────────────────────────
@admin_required
def add_update(request, elqa_key):
    if request.method == "POST":
        title   = request.POST.get("title", "").strip()
        content = request.POST.get("content", "").strip()
        image   = request.FILES.get("image")
        if title and content:
            ElqaUpdate.objects.create(
                elqa    = elqa_key,
                title   = title,
                content = content,
                image   = image
            )
    return redirect('updates')


# ─── DELETE UPDATE ────────────────────────
@admin_required
def delete_update(request, elqa_key, pk):
    ElqaUpdate.objects.filter(id=pk, elqa=elqa_key).delete()
    return redirect('updates')


# ─── COLLEGES HOME ────────────────────────
@login_required
def colleges_home(request):
    elqa_key = 'colleges'
    total_karkunan = Member.objects.filter(elqa=elqa_key, member_type='karkun').count()
    total_rufaqa   = Member.objects.filter(elqa=elqa_key, member_type='rafiq').count()
    total_umeedwar = Member.objects.filter(elqa=elqa_key, member_type='umeedwar').count()
    halqas         = Halqa.objects.filter(elqa=elqa_key)
    return render(request, 'elqa_colleges.html', {
        'total_karkunan': total_karkunan,
        'total_rufaqa':   total_rufaqa,
        'total_umeedwar': total_umeedwar,
        'halqas':         halqas,
        'is_admin':       get_user_elqa(request.user) == elqa_key,
    })


# ─── AJAX: GET HALQA COUNTS + NAMES ───────
@login_required
def get_halqa_counts(request):
    halqa_id = request.GET.get('halqa_id', '')
    elqa_key = request.GET.get('elqa_key', 'colleges')

    if halqa_id:
        karkunan_qs = Member.objects.filter(halqa_id=halqa_id, member_type='karkun').values('id', 'name')
        rufaqa_qs   = Member.objects.filter(halqa_id=halqa_id, member_type='rafiq').values('id', 'name')
        umeedwar_qs = Member.objects.filter(halqa_id=halqa_id, member_type='umeedwar').values('id', 'name')
    else:
        karkunan_qs = Member.objects.filter(elqa=elqa_key, member_type='karkun').values('id', 'name')
        rufaqa_qs   = Member.objects.filter(elqa=elqa_key, member_type='rafiq').values('id', 'name')
        umeedwar_qs = Member.objects.filter(elqa=elqa_key, member_type='umeedwar').values('id', 'name')

    return JsonResponse({
        'karkunan': list(karkunan_qs),
        'rufaqa':   list(rufaqa_qs),
        'umeedwar': list(umeedwar_qs),
    })

'''





































































































































'''from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Halqa, Member, ElqaUpdate


# ─── ELQA MAP ─────────────────────────────
ELQA_USER_MAP = {
    'admin_sindhakhall': 'sindhakhall',
    'admin_talash':      'talash',
    'admin_collage':     'collage',
    'admin_shaher':      'shaher',
    'admin_bazam':       'bazam',
    'admin_colleges':    'colleges',
}


def get_user_elqa(user):
    return ELQA_USER_MAP.get(user.username)


# ─── LOGIN ────────────────────────────────
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )
        if user:
            login(request, user)
            elqa = get_user_elqa(user)
            if elqa:
                return redirect('elqa_page', elqa_key=elqa)
            return redirect('home')
        messages.error(request, "Invalid username or password")
    return render(request, 'login.html')


# ─── LOGOUT ───────────────────────────────
def logout_view(request):
    logout(request)
    return redirect('login')


# ─── HOME ─────────────────────────────────
@login_required
def home(request):
    return render(request, 'home.html')


# ─── TEAM ─────────────────────────────────
@login_required
def team(request):
    return render(request, 'about-timergara-moqam.html')


# ─── UPDATES ──────────────────────────────
@login_required
def updates(request):
    return render(request, 'updates.html')


# ─── ADMIN CHECK DECORATOR ────────────────
def admin_required(view_func):
    def wrapper(request, elqa_key, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if get_user_elqa(request.user) != elqa_key:
            messages.error(request, "Not allowed")
            return redirect('home')
        return view_func(request, elqa_key, *args, **kwargs)
    return wrapper


# ─── ELQA PAGE ────────────────────────────
@login_required
def elqa_page(request, elqa_key):
    template_map = {
        'sindhakhall': 'elqa_sindhakhall.html',
        'talash':      'elqa_talash.html',
        'collage':     'elqa_collage.html',
        'shaher':      'elqa_shaher.html',
        'bazam':       'bazam.html',
        'colleges':    'elqa_colleges.html',
    }
    template = template_map.get(elqa_key)
    if not template:
        return redirect('home')

    is_admin = get_user_elqa(request.user) == elqa_key

    if elqa_key in ['collage', 'colleges', 'bazam', 'shaher', 'talash', 'sindhakhall']:
        total_karkunan = Member.objects.filter(elqa=elqa_key, member_type='karkun').count()
        total_rufaqa   = Member.objects.filter(elqa=elqa_key, member_type='rafiq').count()
        total_umeedwar = Member.objects.filter(elqa=elqa_key, member_type='umeedwar').count()
    else:
        total_karkunan = total_rufaqa = total_umeedwar = 0

    context = {
        'elqa_key':       elqa_key,
        'is_admin':       is_admin,
        'halqas':         Halqa.objects.filter(elqa=elqa_key),
        'members':        Member.objects.filter(elqa=elqa_key),
        'updates':        ElqaUpdate.objects.filter(elqa=elqa_key),
        'total_karkunan': total_karkunan,
        'total_rufaqa':   total_rufaqa,
        'total_umeedwar': total_umeedwar,
    }
    return render(request, template, context)


# ─── ADD HALQA ────────────────────────────
@admin_required
def add_halqa(request, elqa_key):
    if request.method == "POST":
        name = request.POST.get("name")
        if name:
            Halqa.objects.create(elqa=elqa_key, name=name)
    return redirect('elqa_page', elqa_key=elqa_key)


# ─── DELETE HALQA ─────────────────────────
@admin_required
def delete_halqa(request, elqa_key, pk):
    Halqa.objects.filter(id=pk, elqa=elqa_key).delete()
    return redirect('elqa_page', elqa_key=elqa_key)


# ─── ADD MEMBER (normal form) ─────────────
@admin_required
def add_member(request, elqa_key):
    if request.method == "POST":
        halqa_id    = request.POST.get("halqa_id")
        member_type = request.POST.get("member_type", "karkun")
        Member.objects.create(
            elqa        = elqa_key,
            halqa_id    = halqa_id if halqa_id else None,
            name        = request.POST.get("name"),
            member_type = member_type,
            role        = request.POST.get("role"),
            photo       = request.FILES.get("photo")
        )
    return redirect('elqa_page', elqa_key=elqa_key)


# ─── ADD MEMBER AJAX (colleges dashboard) ─
@login_required
def add_member_ajax(request, elqa_key):
    if request.method == 'POST':
        name        = request.POST.get('name', '').strip()
        member_type = request.POST.get('member_type', 'karkun')
        halqa_id    = request.POST.get('halqa_id', '')

        if not name:
            return JsonResponse({'success': False, 'error': 'Name required'})

        if get_user_elqa(request.user) != elqa_key and not request.user.is_superuser:
            return JsonResponse({'success': False, 'error': 'Not allowed'})

        member = Member.objects.create(
            elqa        = elqa_key,
            halqa_id    = halqa_id if halqa_id else None,
            name        = name,
            member_type = member_type,
        )

        karkunan = Member.objects.filter(halqa_id=halqa_id, member_type='karkun').count()
        rufaqa   = Member.objects.filter(halqa_id=halqa_id, member_type='rafiq').count()
        umeedwar = Member.objects.filter(halqa_id=halqa_id, member_type='umeedwar').count()

        return JsonResponse({
            'success':   True,
            'member_id': member.id,
            'name':      member.name,
            'karkunan':  karkunan,
            'rufaqa':    rufaqa,
            'umeedwar':  umeedwar,
        })

    return JsonResponse({'success': False, 'error': 'POST required'})


# ─── DELETE MEMBER ────────────────────────
@admin_required
def delete_member(request, elqa_key, pk):
    Member.objects.filter(id=pk, elqa=elqa_key).delete()
    return redirect('elqa_page', elqa_key=elqa_key)


# ─── ADD UPDATE ───────────────────────────
@admin_required
def add_update(request, elqa_key):
    if request.method == "POST":
        ElqaUpdate.objects.create(
            elqa    = elqa_key,
            title   = request.POST.get("title"),
            content = request.POST.get("content"),
            image   = request.FILES.get("image")
        )
    return redirect('elqa_page', elqa_key=elqa_key)


# ─── DELETE UPDATE ────────────────────────
@admin_required
def delete_update(request, elqa_key, pk):
    ElqaUpdate.objects.filter(id=pk, elqa=elqa_key).delete()
    return redirect('elqa_page', elqa_key=elqa_key)


# ─── COLLEGES HOME (separate URL) ─────────
@login_required
def colleges_home(request):
    elqa_key = 'colleges'
    total_karkunan = Member.objects.filter(elqa=elqa_key, member_type='karkun').count()
    total_rufaqa   = Member.objects.filter(elqa=elqa_key, member_type='rafiq').count()
    total_umeedwar = Member.objects.filter(elqa=elqa_key, member_type='umeedwar').count()
    halqas         = Halqa.objects.filter(elqa=elqa_key)
    return render(request, 'elqa_colleges.html', {
        'total_karkunan': total_karkunan,
        'total_rufaqa':   total_rufaqa,
        'total_umeedwar': total_umeedwar,
        'halqas':         halqas,
        'is_admin':       get_user_elqa(request.user) == elqa_key,
    })


# ─── AJAX: GET HALQA COUNTS ───────────────
@login_required
def get_halqa_counts(request):
    halqa_id = request.GET.get('halqa_id', '')

    if halqa_id:
        karkunan_members = Member.objects.filter(halqa_id=halqa_id, member_type='karkun').values('id', 'name')
        rufaqa_members   = Member.objects.filter(halqa_id=halqa_id, member_type='rafiq').values('id', 'name')
        umeedwar_members = Member.objects.filter(halqa_id=halqa_id, member_type='umeedwar').values('id', 'name')
    else:
        karkunan_members = Member.objects.filter(elqa='colleges', member_type='karkun').values('id', 'name')
        rufaqa_members   = Member.objects.filter(elqa='colleges', member_type='rafiq').values('id', 'name')
        umeedwar_members = Member.objects.filter(elqa='colleges', member_type='umeedwar').values('id', 'name')

    return JsonResponse({
        'karkunan':  list(karkunan_members),
        'rufaqa':    list(rufaqa_members),
        'umeedwar':  list(umeedwar_members),
    })
    '''