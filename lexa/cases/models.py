from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class Jurisdiction(models.Model):
    JURISDICTION_TYPES = [
        ('tribunal', _('Tribunal')),
        ('tribunal_commercial', _('Tribunal Commercial')),
        ('tribunal_administratif', _('Tribunal Administratif')),
        ('tribunal_criminel', _('Tribunal Criminel')),
        ('cour', _('Cour d\'Appel')),
        ('cour_supreme', _('Cour Suprême')),
        ('conseil_etat', _('Conseil d\'État')),
    ]
    
    COURT_LEVELS = [
        ('premiere', _('Première Instance')),
        ('appel', _('Appel')),
        ('cassation', _('Cassation')),
    ]

    name_fr = models.CharField(max_length=200)
    name_ar = models.CharField(max_length=200)
    type_fr = models.CharField(max_length=50, choices=JURISDICTION_TYPES)
    type_ar = models.CharField(max_length=200)
    wilaya = models.CharField(max_length=2)  # Algerian province code
    level = models.CharField(max_length=20, choices=COURT_LEVELS)
    
    # Court officials
    president = models.CharField(max_length=200, blank=True)
    vice_president = models.CharField(max_length=200, blank=True)
    procureur = models.CharField(max_length=200, blank=True)
    
    # Additional info
    sections = models.JSONField(default=list, blank=True)
    chambers = models.JSONField(default=list, blank=True)
    competence = models.JSONField(default=list, blank=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True)
    established = models.DateField(null=True, blank=True)
    specialization = models.CharField(max_length=200, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Jurisdiction')
        verbose_name_plural = _('Jurisdictions')
        ordering = ['wilaya', 'name_fr']

    def __str__(self):
        return f"{self.name_fr} - {self.wilaya}"

class CaseType(models.Model):
    CASE_CATEGORIES = [
        ('civil', _('Civil')),
        ('penal', _('Pénal')),
        ('administratif', _('Administratif')),
        ('commercial', _('Commercial')),
        ('famille', _('Famille')),
        ('foncier', _('Foncier')),
        ('social', _('Social')),
    ]

    category_fr = models.CharField(max_length=50, choices=CASE_CATEGORIES)
    category_ar = models.CharField(max_length=200)
    subtype_fr = models.CharField(max_length=200)
    subtype_ar = models.CharField(max_length=200)
    reference_article = models.CharField(max_length=200, blank=True)
    description_fr = models.TextField(blank=True)
    description_ar = models.TextField(blank=True)
    typical_duration_days = models.PositiveIntegerField(null=True, blank=True)
    required_documents = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Case Type')
        verbose_name_plural = _('Case Types')
        unique_together = ['category_fr', 'subtype_fr']

    def __str__(self):
        return f"{self.category_fr} - {self.subtype_fr}"

class Case(models.Model):
    CASE_STATUSES = [
        ('ouvert', _('Ouvert')),
        ('en_cours_instruction', _('En cours d\'instruction')),
        ('en_delibere', _('En délibéré')),
        ('juge', _('Jugé')),
        ('appel_interjete', _('Appel interjeté')),
        ('pourvoi_cassation', _('Pourvoi en cassation')),
        ('clos', _('Clos')),
        ('archive', _('Archivé')),
    ]

    # Basic information
    reference = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=300)
    client_name = models.CharField(max_length=200)
    client_email = models.EmailField(blank=True)
    client_phone = models.CharField(max_length=20, blank=True)
    client_address = models.TextField(blank=True)
    
    # Case classification
    jurisdiction = models.ForeignKey(Jurisdiction, on_delete=models.PROTECT)
    case_type = models.ForeignKey(CaseType, on_delete=models.PROTECT)
    status = models.CharField(max_length=50, choices=CASE_STATUSES, default='ouvert')
    
    # Dates
    open_date = models.DateField()
    close_date = models.DateField(null=True, blank=True)
    
    # Case details
    description = models.TextField()
    amount_in_dispute = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='DZD')
    
    # Legal requirements (from your original service)
    confidentiality_agreement = models.BooleanField(default=False)
    no_conflict_interest = models.BooleanField(default=False)
    lawyer_mandate = models.BooleanField(default=False)
    consent_given = models.BooleanField(default=False)
    
    # Internal tracking
    priority = models.CharField(max_length=20, choices=[
        ('low', _('Low')), ('medium', _('Medium')), ('high', _('High')), ('urgent', _('Urgent'))
    ], default='medium')
    
    # User relationship
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cases')
    assigned_lawyers = models.ManyToManyField(User, related_name='assigned_cases', blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Case')
        verbose_name_plural = _('Cases')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reference} - {self.title}"

    @property
    def is_active(self):
        return self.status not in ['clos', 'archive']

class Audience(models.Model):
    AUDIENCE_TYPES = [
        ('mise_en_etat', _('Mise en état')),
        ('plaidoirie', _('Plaidoirie')),
        ('jugement', _('Jugement')),
        ('enquete', _('Enquête')),
        ('expertise', _('Expertise')),
        ('renvoi', _('Renvoi')),
    ]
    
    CHAMBER_TYPES = [
        ('civile', _('Civile')),
        ('penale', _('Pénale')),
        ('administrative', _('Administrative')),
        ('commerciale', _('Commerciale')),
        ('famille', _('Famille')),
        ('sociale', _('Sociale')),
    ]
    
    AUDIENCE_RESULTS = [
        ('report', _('Report')),
        ('delibere', _('Délibéré')),
        ('juge', _('Jugé')),
        ('expertise', _('Expertise ordonnée')),
        ('enquete', _('Enquête ordonnée')),
        ('renvoi', _('Renvoi')),
    ]
    
    PROCEDURAL_STAGES = [
        ('introduction', _('Introduction')),
        ('instruction', _('Instruction')),
        ('plaidoirie', _('Plaidoirie')),
        ('delibere', _('Délibéré')),
        ('jugement', _('Jugement')),
    ]

    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='audiences')
    date = models.DateTimeField()
    
    # Audience details
    type_fr = models.CharField(max_length=50, choices=AUDIENCE_TYPES)
    type_ar = models.CharField(max_length=200)
    chamber_fr = models.CharField(max_length=50, choices=CHAMBER_TYPES)
    chamber_ar = models.CharField(max_length=200)
    result_fr = models.CharField(max_length=50, choices=AUDIENCE_RESULTS)
    result_ar = models.CharField(max_length=200)
    stage_fr = models.CharField(max_length=50, choices=PROCEDURAL_STAGES)
    stage_ar = models.CharField(max_length=200)
    
    # Additional information
    notes = models.TextField(blank=True)
    judge_name = models.CharField(max_length=200, blank=True)
    court_clerk = models.CharField(max_length=200, blank=True)
    opposing_counsel = models.CharField(max_length=200, blank=True)
    next_hearing_date = models.DateTimeField(null=True, blank=True)
    
    # User relationship
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Audience')
        verbose_name_plural = _('Audiences')
        ordering = ['-date']

    def __str__(self):
        return f"{self.case.reference} - {self.type_fr} - {self.date.date()}"

class CaseMetric(models.Model):
    case = models.OneToOneField(Case, on_delete=models.CASCADE, related_name='metrics')
    
    # Time metrics
    total_hours_worked = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    billable_hours = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Financial metrics
    total_fees = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_expenses = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Progress metrics
    documents_count = models.PositiveIntegerField(default=0)
    audiences_count = models.PositiveIntegerField(default=0)
    tasks_completed = models.PositiveIntegerField(default=0)
    tasks_pending = models.PositiveIntegerField(default=0)
    
    # Quality metrics
    client_satisfaction = models.PositiveSmallIntegerField(null=True, blank=True)  # 1-5 scale
    case_complexity = models.PositiveSmallIntegerField(default=3)  # 1-5 scale
    
    # User relationship
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Case Metric')
        verbose_name_plural = _('Case Metrics')

    def __str__(self):
        return f"Metrics for {self.case.reference}"