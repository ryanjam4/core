from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from mptt.models import MPTTModel, TreeForeignKey

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    ROLE_CHOICES = (
        ('patient', 'patient'),
        ('physician', 'physician'),
        ('admin', 'admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='patient')
    data = models.TextField(blank=True) 
    cover_image = models.ImageField(upload_to='cover_image/', blank=True)
    portrait_image = models.ImageField(upload_to='cover_image/', blank=True)

    def __unicode__(self):
        return '%s' % (self.user.get_full_name())

class AccessLog(models.Model):
    user = models.ForeignKey(User)
    datetime = models.DateTimeField(auto_now_add=True)
    summary = models.TextField()

    def __unicode__(self):
        return '%s %s %s' % (self.user.username, self.datetime, self.summary)

def get_path(instance, filename):
    try:
        return '%s/%s/%s' % (instance.patient.id, instance.problem.id, filename)
    except:
        return '%s/%s' % (instance.patient.id, filename)
 
class Encounter(models.Model):
    physician = models.ForeignKey(User, related_name="physician")
    patient = models.ForeignKey(User, related_name="patient")
    starttime = models.DateTimeField(auto_now_add=True)
    stoptime = models.DateTimeField(null=True, blank=True)
    #events = generic.GenericRelation('EncounterEvent',
    #    content_type_field='content_type',
    #    object_id_field='object_id'
    #)
    events = models.ManyToManyField('EncounterEvent')
    audio = models.FileField(upload_to=get_path, blank=True) 
    
    def __unicode__(self):
        return 'Patient: %s Time: %s' % (self.patient.get_full_name(), self.physician.get_full_name())

class EncounterEvent(models.Model):
    datetime = models.DateTimeField(auto_now_add=True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    event = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return unicode(self.event)
        
class EventSummary(models.Model):
    patient = models.ForeignKey(User)
    datetime = models.DateTimeField(auto_now_add=True)
    summary = models.TextField()

    def __unicode__(self):
        return '%s %s' % (unicode(self.patient), self.summary)

class TextNote(models.Model):
    BY_CHOICES = (
        ('patient', 'patient'),
        ('physician', 'physician'),
    )
    by = models.CharField(max_length=20, choices=BY_CHOICES)
    note = models.TextField()
    datetime = models.DateTimeField(auto_now_add=True)

class Problem(MPTTModel):
    patient = models.ForeignKey(User)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children')
    problem_name = models.CharField(max_length=200)
    concept_id = models.CharField(max_length=20, blank=True)
    is_controlled = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    authenticated = models.BooleanField(default=False)
    notes = models.ManyToManyField(TextNote, blank=True)
    start_date = models.DateField(auto_now_add=True)
    
    def __unicode__(self):
        return '%s %s' % (self.patient, self.problem_name)

class Goal(models.Model):
    patient = models.ForeignKey(User)
    problem = models.ForeignKey(Problem, null=True, blank=True)
    goal = models.TextField()
    is_controlled = models.BooleanField(default=False)
    accomplished = models.BooleanField(default=False)
    notes = models.ManyToManyField(TextNote, blank=True)
    start_date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '%s %s' % (unicode(self.patient), unicode(self.problem))

class ToDo(models.Model):
    patient = models.ForeignKey(User)
    problem = models.ForeignKey(Problem, null=True, blank=True)
    todo = models.TextField()
    accomplished = models.BooleanField(default=False)    
    notes = models.ManyToManyField(TextNote, blank=True)


    def __unicode__(self):
        return '%s' % (unicode(self.patient))

class Guideline(models.Model):
    concept_id = models.CharField(max_length=20, blank=True)
    guideline = models.TextField()
    reference_url = models.CharField(max_length=400, blank=True)

    def __unicode__(self):
        return '%s %s' % (self.concept_id, self.guideline)

class PatientImage(models.Model):
    patient = models.ForeignKey(User)
    problem = models.ForeignKey(Problem, null=True, blank=True)
    image = models.ImageField(upload_to=get_path) 
    datetime = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '%s' % (unicode(self.patient))
        
class Sharing(models.Model):
    patient = models.ForeignKey(User, related_name='target_patient')
    other_patient = models.ForeignKey(User, related_name='other_patient')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    item = generic.GenericForeignKey('content_type', 'object_id')
    relationship_to_patient = models.CharField(max_length=20, blank=True)
    relationship_to_patient_snomed = models.CharField(max_length=20, blank=True)
    relationship_to_other_patient = models.CharField(max_length=20, blank=True)
    relationship_to_other_patient_snomed = models.CharField(max_length=20, blank=True)
    
    def __unicode__(self):
        return '%s %s' % (unicode(self.patient), unicode(self.other_patient))
        
class Viewer(models.Model):
    patient = models.ForeignKey(User, related_name='viewed_patient')
    viewer = models.ForeignKey(User, related_name='viewer')
    datetime = models.DateTimeField(auto_now=True)
    tracking_id = models.CharField(max_length=20, blank=True) # for tracking open browser instances e.g. multiple tabs
    user_agent = models.CharField(max_length=200, blank=True) # user agent is type of browser/OS/version
    
class ViewStatus(models.Model):
    patient = models.ForeignKey(User)
    status = models.TextField()
    
    
