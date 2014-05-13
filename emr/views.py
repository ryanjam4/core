from django.shortcuts import render
from django.shortcuts import render_to_response
from django.db.models.loading import get_model
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.template import RequestContext
from models import UserProfile, AccessLog, Problem, Goal, ToDo, Guideline, TextNote, PatientImage
import traceback
from django.contrib.auth.decorators import login_required
import json
import os
#import pymedtermino.snomedct
#pymedtermino.snomedct.done()
class AccessLogMiddleware(object):

    def process_request(self, request):
        if request.user.is_authenticated() and not request.path.startswith('/list_of'):
            access_log = AccessLog(user=request.user, summary=request.path)
            access_log.save()

def update(request):
    os.system('sh /home/tim/core/update.sh &')
    return HttpResponse('<title>Update</title><script>setTimeout(function() { window.location = "/" }, 60000);</script> Going to homepage in 60 seconds')

@login_required
def home(request):
    try:
        
        profile = UserProfile.objects.get(user=request.user)
        role = profile.role
        context = {}
        context['role'] = role
        context = RequestContext(request, context)
        if (role == 'patient'):
            return view_patient(request, request.user.id)
        
        return render_to_response("home.html", context)

    except: 
        traceback.print_exc()
        if request.user.is_superuser:
            context = {}
            context['role'] = 'admin'
            context = RequestContext(request, context)
            return render_to_response("home.html", context)

            
        return HttpResponse('<script>setTimeout(function() { window.location = "/" }, 1000);</script> Waiting on manual approval')
    
@login_required
def list_of_unregistered_users(request):
    
    users = []
    for user in User.objects.all():
        try:
            profile = UserProfile.objects.get(user=user)
        except:
            users.append({'id': user.id, 'username': user.username, 'full_name': user.get_full_name()})
    return HttpResponse(json.dumps(users), content_type="application/json")

@login_required
def register_users(request): 
    for i in request.POST:
        try:
            user_profile = UserProfile(user=User.objects.get(id=i.split('_')[1]), role=request.POST[i])
            user_profile.save()
            if (request.POST[i] == 'admin'):
                user = User.objects.get(id=i.split('_')[1])
                user.is_superuser = True
                user.is_staff = True
                user.save()
        except:
            pass
    return HttpResponse('saved')


def is_patient(user):
    try:
        profile = UserProfile.objects.get(user=user)
        return profile.role == 'patient'
    except:
        return false
    

#@login_required
def list_users(request):

    users = [{'is_patient': is_patient(user), 'username': user.username, 'firstname': user.first_name, 'lastname': user.last_name, 'id': user.id} for user in User.objects.all().order_by('first_name')]
    return HttpResponse(json.dumps(users), content_type="application/json")

@login_required
def view_patient(request, user_id):
    from pain.models import PainAvatar
    user = User.objects.get(id=user_id)
    if (not is_patient(user)):
        return HttpResponse("Error: this user isn't a patient")
    context = {'patient': user, 'patient_profile': UserProfile.objects.get(user=user), 'problems': Problem.objects.filter(patient=user)}
    context.update({'pain_avatars': PainAvatar.objects.filter(patient=user).order_by('-datetime')})
    context = RequestContext(request, context)
    return render_to_response("patient.html", context)

@login_required
def get_problems(request, user_id):
    problems = [{'problem_id': problem.id, 'effected_by': problem.parent.id if problem.parent else None, 'affects': [{'problem_id': g.id, 'problem_name': g.problem_name} for g in problem.get_children()], 'problem_name': problem.problem_name, 'images': [g.image.url for g in PatientImage.objects.filter(problem=problem)], 'guidelines': [{'guideline': g.guideline, 'reference_url': g.reference_url} for g in Guideline.objects.filter(concept_id=problem.concept_id)], 'is_controlled': problem.is_controlled, 'is_authenticated': problem.authenticated, 'is_active': problem.is_active, 'goals': [{'id': g.id, 'goal': g.goal, 'accomplished': g.accomplished, 'notes': [{'by': n.by, 'note': n.note} for n in g.notes.all()]} for g in Goal.objects.filter(problem=problem)], 'todos': [{'todo': g.todo, 'id': g.id, 'accomplished': g.accomplished} for g in ToDo.objects.filter(problem=problem)], 'notes': {'by_physician': [{'note': g.note} for g in TextNote.objects.filter(problem=problem, by__in=['physician', 'admin'])[::-1]], 'by_patient': [{'note': g.note} for g in TextNote.objects.filter(problem=problem, by='patient')], 'all': [{'by': g.by, 'note': g.note} for g in TextNote.objects.filter(problem=problem)]}} for problem in Problem.objects.filter(patient=user_id)]
    return HttpResponse(json.dumps(problems), content_type="application/json")

@login_required
def change_status(request):
    print request.POST
    if request.POST['target'] == 'problem':
        problem = Problem.objects.get(id=request.POST['id'])
        value = True if request.POST['value'] == 'true' else False
        setattr(problem,request.POST['attr'], value)
        problem.save()
    elif request.POST['target'] == 'goal':
        goal = Goal.objects.get(id=request.POST['id'])
        value = True if request.POST['value'] == 'true' else False
        setattr(goal,'accomplished', value)
        goal.save()
    elif request.POST['target'] == 'todo':
        todo = ToDo.objects.get(id=request.POST['id'])
        value = True if request.POST['value'] == 'true' else False
        setattr(todo,'accomplished', value)
        todo.save()
    return HttpResponse('saved')

@login_required
def submit_data_for_problem(request, problem_id):
    print request.POST
    problem = Problem.objects.get(id=problem_id)

    if request.POST['type'] == 'note':
        problem = Problem.objects.get(id=problem_id)
        note = TextNote(by=UserProfile.objects.get(user=request.user).role, note=request.POST['data'])
        note.save()
        problem.notes.add(note)
        problem.save()
    elif request.POST['type'] == 'note_for_goal':
        goal = Goal.objects.get(id=problem_id)
        note = TextNote(by=UserProfile.objects.get(user=request.user).role, note=request.POST['data'])
        note.save()
        goal.notes.add(note)
        goal.save()
    elif request.POST['type'] == 'mark_parent':
        problem = Problem.objects.get(id=problem_id)
        if (request.POST['data'] == 'none'):
            problem.parent = None
        else:
            problem.parent = Problem.objects.get(id=request.POST['data'])
        problem.save()
    else:
        problem = Problem.objects.get(id=problem_id)
        model = get_model('emr', request.POST['type'].capitalize()) 
    
        m = model(patient=problem.patient, problem=problem)
        setattr(m,request.POST['type'], request.POST['data'] ) 
        m.save()
    return HttpResponse('saved')

@login_required
def add_problem(request, patient_id):
    role = UserProfile.objects.get(user=request.user).role
    authenticated = True if (role == 'physician' or role == 'admin') else False
    problem = Problem(patient=User.objects.get(id=patient_id), problem_name=request.POST['problem_name'], concept_id=request.POST['concept_id'], authenticated=authenticated)
    problem.save()
    return HttpResponse('added')

@login_required
def list_terms(request):
    query = request.GET['query']
    
    import pymedtermino.snomedct
    #return [i.__dict__ for i in SNOMEDCT.search(query)]
    # only disorders and finding
    results1 = [i.__dict__ for i in pymedtermino.snomedct.SNOMEDCT.search(query) if '(disorder)' in i.__dict__['term']]
    results1 = sorted(results1, key=lambda x: x["term"])
    results2 = [i.__dict__ for i in pymedtermino.snomedct.SNOMEDCT.search(query) if '(finding)' in i.__dict__['term']]
    results2 = sorted(results2, key=lambda x: x["term"])
    results = []
    results.extend(results1)
    results.extend(results2)
    results = json.dumps(results)
    #pymedtermino.snomedct.done()
    return HttpResponse(results, content_type="application/json")

@login_required
def upload_image_to_problem(request, problem_id):
    if request.POST:
        patient_image = PatientImage(patient=Problem.objects.get(id=problem_id).patient, problem=Problem.objects.get(id=problem_id), image=request.FILES['file'])
        patient_image.save()
        return HttpResponseRedirect('/patient/%s/' % (Problem.objects.get(id=problem_id).patient.id))
    else:
        context = RequestContext(request, {})
        return render_to_response('upload_image_to_problem.html', context)

from django.core.urlresolvers import reverse
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.base import View
from social_auth.exceptions import AuthFailed
from social_auth.views import complete
 
 
  
class AuthComplete(View):
    def get(self, request, *args, **kwargs):
        backend = kwargs.pop('backend')
        try:
            return complete(request, backend, *args, **kwargs)
        except AuthFailed:
            messages.error(request, "Your Google Apps domain isn't authorized for this app")
            return HttpResponseRedirect(reverse('home'))
 
 
class LoginError(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse(status=401)   
