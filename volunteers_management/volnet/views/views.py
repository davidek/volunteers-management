from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from volnet.models import *
from forms import *
from django.template import RequestContext


def home(request):
    #chiama funzione che assegna i volontari
    user = request.user
    if user.is_authenticated():
        return HttpResponseRedirect("/accounts/profile/")
    return HttpResponseRedirect("/emergencies/overview/")

def about(request):
    user = request.user
    volunteer = None
    member = None
    organization = None
    if user.is_authenticated():
        volunteer = is_volunteer(user)
        member = is_member(user)
        organization = is_organization(user)
    return render_to_response("about.html", locals())

def contact(request):
    user = request.user
    volunteer = None
    member = None
    organization = None
    if user.is_authenticated():
        volunteer = is_volunteer(user)
        member = is_member(user)
        organization = is_organization(user)
    return render_to_response("contact.html", locals())

def is_member(user):
    qset = (Q(user__exact=user))
    member = Member.objects.filter(qset)
    if member:
        return True
    else:
        return False

def is_organization(user):
    qset = (Q(user__exact=user))
    member = Organization.objects.filter(qset)
    if member:
        return True
    else:
        return False

def is_volunteer(user):
    qset = (Q(user__exact=user))
    member = Volunteer.objects.filter(qset)
    if member:
        return True
    else:
        return False

@login_required
def profile(request):
    user = request.user
    organization = is_organization(user)
    member = is_member(user)
    volunteer = is_volunteer(user)
    #emergency = None
    #emergency_list = Emergency.objects.filter(active=True)
    """
    if organization or member or volunteer:
        for em in emergency_list:
            if vol in em.volunteers.all():
                emergency = em
                break
        return render_to_response("home.html", locals())
    """
    if organization:
        qset = (Q(user__exact=user))
        org = Organization.objects.filter(qset)
        qset = (Q(organization__exact=org))
        all_ems = Emergency.objects.filter(qset)
        qset = (Q(active=True))
        ems = all_ems.filter(qset)
        if ems:
            return HttpResponseRedirect("/events/overview/")
        else:
            return HttpResponseRedirect("/emergencies/create/")
    elif member:
        return HttpResponseRedirect("/events/myevents/")
    elif volunteer:
        qset = (Q(active=True))
        active_ems = Emergency.objects.filter(qset)
        qset = (Q(user__exact=user))
        vol = Volunteer.objects.filter(qset)
        for em in active_ems:
            if vol in em.volunteers:
                return HttpResponseRedirect("/events/mytasks/")
        return HttpResponseRedirect("/emergencies/overview/")
    elif request.method == "POST":
        form = VolunteerInfoForm(request.POST)
        if form.is_valid():
            form.save_volunteer(user)
            return HttpResponseRedirect("/")
    else:
        form = VolunteerInfoForm()

    return render_to_response("insert_volunteer_info.html", locals(),
                              context_instance=RequestContext(request))

#dalla home (cioe`:da profiles): redirects
#    imbecille -> emergencies/overview/
#    volontario -> se enroled: events/mytask/
#                  else      : emergencies/overview/
#    member  -> events/myevents/
#    organization -> se ha emergenza aperta: events/overview/
#                    altrimenti: emergencies/create/

@login_required
def new_event(request):
    user = request.user
    qset = (Q(user__exact=user))
    member = Member.objects.filter(qset)[0]
    f = create_event_form(member)
    if request.method == "POST":
        form = f(request.POST)
        if form.is_valid():
            form.save_event()
            return HttpRedirectResponse("/")
    else:
        form = f()
    return render_to_response("events/create.html", locals())

def event_desc(request):
    user = request.user
    volunteer = None
    member = None
    organization = None
    if user.is_authenticated():
        volunteer = is_volunteer(user)
        member = is_member(user)
        organization = is_organization(user)
    ev_id  = request.GET.get("id")
    ev = None
    if ev_id:
        ev = Event.objects.filter(Q(pk__exact=ev_id))
        if ev_id and (volontario or member or organization):
            ev = Event.objects.filter(Q(pk__exact=ev_id))
            return render_to_response("events/create.html", locals())
    return  HttpResponseRedirect("/")

@login_required
def my_events(request):
    user = request.user
    organization = is_organization(user)
    member = is_member(user)
    volunteer = is_volunteer(user)
    qset = (Q(user__exact=user))
    mem = Member.objects.filter(qset)
    if mem:
        evs = Event.objects.filter(member=mem[0])
        return render_to_response("events/myevents.html", locals())
    else:
        return HttpRedirectResponse("/")

def event_overview(request):
    ems_open = Emergency.objects.filter(Q(active=True))
    result = {}
    for ems in ems_open:
        qset = (Q(emergency__exact=ems))
        result[ems] = Event.objects.filter(qset)
    return render_to_response("events/overview.html", locals())

def my_task(request):
    organization = is_organization(user)
    member = is_member(user)
    volunteer = is_volunteer(user)
    qset = (Q(user__exact=user))
    vol = Member.objects.filter(qset)
    evs_open = Event.objects.filter(active=True)
    evs = None
    for ev in evs_open:
        if vol in ev.volunteers:
            evs = ev
            break
    return HttpResponseRedirect("/events/description/?id=%d" % evs.pk)

def members_manage(reuqest):
    pass

def emergency_manage(request):
    pass

def emergency_overview(request):
    user = request.user
    volunteer = None
    member = None
    organization = None
    if user.is_authenticated():
        volunteer = is_volunteer(user)
        member = is_member(user)
        organization = is_organization(user)

    ems_open = Emergency.objects.filter(Q(active=True))
    ems_closed = Emergency.objects.filter(Q(active=False))
    return render_to_response("emergencies/overview.html", locals())

def emergency_join(request):
    pass

def emergency_leave(request):
    pass

def emergency_close(request):
    pass

def call_volunteers(request):
    pass
