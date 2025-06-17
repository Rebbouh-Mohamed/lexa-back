# legal_framework/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _

class AlgerianLegalCode(models.Model):
    CODE_TYPES = [
        ('civil', _('Code Civil')),
        ('penal', _('Code Pénal')),
        ('procedure_civile', _('Code de Procédure Civile')),
        ('procedure_penale', _('Code de Procédure Pénale')),
        ('commerce', _('Code de Commerce')),
        ('travail', _('Code du Travail')),
        ('famille', _('Code de la Famille')),
        ('maritime', _('Code Maritime')),
        ('aerien', _('Code Aérien')),
        ('douanes', _('Code des Douanes')),
        ('impots', _('Code des Impôts')),
        ('investissement', _('Code des Investissements')),
        ('environnement', _('Code de l\'Environnement')),
        ('urbanisme', _('Code de l\'Urbanisme')),
    ]

    code_name_fr = models.CharField(max_length=200)
    code_name_ar = models.CharField(max_length=200)
    code_type = models.CharField(max_length=50, choices=CODE_TYPES)
    
    # Article details
    article_number = models.CharField(max_length=20, blank=True)
    article_title_fr = models.CharField(max_length=500, blank=True)
    article_title_ar = models.CharField(max_length=500, blank=True)
    article_content_fr = models.TextField(blank=True)
    article_content_ar = models.TextField(blank=True)
    
    # References
    related_articles = models.JSONField(default=list, blank=True)
    jurisprudence_references = models.JSONField(default=list, blank=True)
    
    # Metadata
    effective_date = models.DateField(null=True, blank=True)
    last_modified = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Algerian Legal Code')
        verbose_name_plural = _('Algerian Legal Codes')
        unique_together = ['code_type', 'article_number']
        ordering = ['code_type', 'article_number']

    def __str__(self):
        if self.article_number:
            return f"{self.code_name_fr} - Article {self.article_number}"
        return self.code_name_fr

class AlgerianCourt(models.Model):
    COURT_LEVELS = [
        ('premiere', _('Première Instance')),
        ('appel', _('Appel')),
        ('cassation', _('Cassation')),
    ]
    
    JURISDICTION_TYPES = [
        ('civil', _('Civil')),
        ('penal', _('Pénal')),
        ('administratif', _('Administratif')),
        ('commercial', _('Commercial')),
        ('famille', _('Famille')),
        ('social', _('Social')),
        ('maritime', _('Maritime')),
        ('militaire', _('Militaire')),
    ]

    court_name_fr = models.CharField(max_length=200)
    court_name_ar = models.CharField(max_length=200)
    court_level = models.CharField(max_length=20, choices=COURT_LEVELS)
    jurisdiction_type = models.CharField(max_length=30, choices=JURISDICTION_TYPES)
    
    # Location
    wilaya = models.CharField(max_length=2)  # Algerian province code
    city = models.CharField(max_length=100)
    address = models.TextField(blank=True)
    
    # Contact information
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    
    # Court officials
    president = models.CharField(max_length=200, blank=True)
    vice_president = models.CharField(max_length=200, blank=True)
    procureur = models.CharField(max_length=200, blank=True)
    secretary_general = models.CharField(max_length=200, blank=True)
    
    # Additional information
    specializations = models.JSONField(default=list, blank=True)
    working_hours = models.JSONField(default=dict, blank=True)
    
    is_active = models.BooleanField(default=True)
    established_date = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Algerian Court')
        verbose_name_plural = _('Algerian Courts')
        ordering = ['wilaya', 'court_name_fr']

    def __str__(self):
        return f"{self.court_name_fr} - {self.wilaya}"

class TaxConfiguration(models.Model):
    TAX_TYPES = [
        ('tva', _('TVA - Taxe sur la Valeur Ajoutée')),
        ('irg', _('IRG - Impôt sur le Revenu Global')),
        ('ibs', _('IBS - Impôt sur les Bénéfices des Sociétés')),
        ('tap', _('TAP - Taxe sur l\'Activité Professionnelle')),
        ('versement_forfaitaire', _('Versement Forfaitaire')),
        ('timbre', _('Droit de Timbre')),
        ('enregistrement', _('Droit d\'Enregistrement')),
    ]

    tax_type = models.CharField(max_length=30, choices=TAX_TYPES)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2)
    description_fr = models.TextField(blank=True)
    description_ar = models.TextField(blank=True)
    
    # Effective dates
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    
    # Additional parameters
    minimum_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    maximum_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Tax Configuration')
        verbose_name_plural = _('Tax Configurations')
        ordering = ['tax_type', '-effective_from']

    def __str__(self):
        return f"{self.get_tax_type_display()} - {self.tax_rate}%"

class LegalProcedure(models.Model):
    PROCEDURE_TYPES = [
        ('civil', _('Procédure Civile')),
        ('penal', _('Procédure Pénale')),
        ('administrative', _('Procédure Administrative')),
        ('commercial', _('Procédure Commerciale')),
        ('famille', _('Procédure de Famille')),
        ('execution', _('Procédure d\'Exécution')),
        ('arbitrage', _('Arbitrage')),
        ('mediation', _('Médiation')),
    ]

    procedure_name_fr = models.CharField(max_length=300)
    procedure_name_ar = models.CharField(max_length=300)
    procedure_type = models.CharField(max_length=30, choices=PROCEDURE_TYPES)
    court_level = models.CharField(max_length=20, choices=AlgerianCourt.COURT_LEVELS)
    
    # Procedure details
    description_fr = models.TextField()
    description_ar = models.TextField(blank=True)
    template_content_fr = models.TextField(blank=True)
    template_content_ar = models.TextField(blank=True)
    
    # Requirements
    required_documents = models.JSONField(default=list)
    timeline_days = models.PositiveIntegerField(null=True, blank=True)
    fees_range_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    fees_range_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Legal references
    legal_references = models.JSONField(default=list, blank=True)
    related_procedures = models.ManyToManyField('self', blank=True)
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)