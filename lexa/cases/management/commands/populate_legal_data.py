# ===================================
# PATH: legal_system/management/__init__.py
# ===================================
# This file makes the directory a Python package

# ===================================
# PATH: legal_system/management/commands/__init__.py
# ===================================
# This file makes the directory a Python package

# ===================================
# PATH: legal_system/management/commands/populate_legal_data.py
# ===================================
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from legal_framework.models import AlgerianLegalCode, AlgerianCourt, TaxConfiguration, LegalProcedure
from datetime import date

class Command(BaseCommand):
    help = 'Populate legal framework with comprehensive Algerian legal data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update existing data',
        )
        parser.add_argument(
            '--type',
            type=str,
            choices=['codes', 'courts', 'taxes', 'procedures', 'all'],
            default='all',
            help='Type of data to populate',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting Algerian legal framework data population...')
        )
        
        try:
            with transaction.atomic():
                if options['type'] in ['codes', 'all']:
                    self.populate_legal_codes(options['force'])
                
                if options['type'] in ['courts', 'all']:
                    self.populate_courts(options['force'])
                
                if options['type'] in ['taxes', 'all']:
                    self.populate_tax_configurations(options['force'])
                
                if options['type'] in ['procedures', 'all']:
                    self.populate_legal_procedures(options['force'])
            
            self.stdout.write(
                self.style.SUCCESS('✅ Successfully populated legal framework data!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error populating data: {str(e)}')
            )
            raise CommandError(f'Population failed: {str(e)}')

    def populate_legal_codes(self, force=False):
        self.stdout.write('📖 Populating legal codes...')
        
        legal_codes_data = [
            # Civil Code
            {
                'code_type': 'civil',
                'article_number': '124',
                'code_name_fr': 'Code Civil Algérien',
                'code_name_ar': 'القانون المدني الجزائري',
                'article_title_fr': 'Obligation de payer les dettes',
                'article_title_ar': 'التزام دفع الديون',
                'article_content_fr': 'Tout débiteur doit s\'acquitter de ses obligations dans les délais convenus.',
                'article_content_ar': 'على كل مدين أن يفي بالتزاماته في الآجال المتفق عليها.',
                'effective_date': date(1975, 9, 26),
                'is_active': True
            },
            {
                'code_type': 'civil',
                'article_number': '126',
                'code_name_fr': 'Code Civil Algérien',
                'code_name_ar': 'القانون المدني الجزائري',
                'article_title_fr': 'Règles de succession',
                'article_title_ar': 'قواعد الإرث',
                'article_content_fr': 'La succession s\'ouvre par le décès du de cujus.',
                'article_content_ar': 'تنفتح التركة بوفاة المورث.',
                'effective_date': date(1975, 9, 26),
                'is_active': True
            },
            # Penal Code
            {
                'code_type': 'penal',
                'article_number': '350',
                'code_name_fr': 'Code Pénal Algérien',
                'code_name_ar': 'قانون العقوبات الجزائري',
                'article_title_fr': 'Vol simple',
                'article_title_ar': 'السرقة البسيطة',
                'article_content_fr': 'Est qualifié vol, la soustraction frauduleuse de la chose d\'autrui.',
                'article_content_ar': 'تعتبر سرقة الأخذ الاحتيالي لمال الغير.',
                'effective_date': date(1966, 6, 8),
                'is_active': True
            },
            {
                'code_type': 'penal',
                'article_number': '264',
                'code_name_fr': 'Code Pénal Algérien',
                'code_name_ar': 'قانون العقوبات الجزائري',
                'article_title_fr': 'Homicide volontaire',
                'article_title_ar': 'القتل العمد',
                'article_content_fr': 'Tout homicide commis volontairement est qualifié meurtre.',
                'article_content_ar': 'كل قتل ارتكب عمدا يوصف بالقتل العمد.',
                'effective_date': date(1966, 6, 8),
                'is_active': True
            },
            # Commercial Code
            {
                'code_type': 'commerce',
                'article_number': '15',
                'code_name_fr': 'Code de Commerce Algérien',
                'code_name_ar': 'القانون التجاري الجزائري',
                'article_title_fr': 'Registre de commerce',
                'article_title_ar': 'السجل التجاري',
                'article_content_fr': 'Toute personne physique ou morale ayant la qualité de commerçant doit s\'immatriculer au registre de commerce.',
                'article_content_ar': 'يجب على كل شخص طبيعي أو معنوي له صفة التاجر أن يسجل في السجل التجاري.',
                'effective_date': date(1975, 9, 26),
                'is_active': True
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for code_data in legal_codes_data:
            obj, created = AlgerianLegalCode.objects.update_or_create(
                code_type=code_data['code_type'],
                article_number=code_data['article_number'],
                defaults=code_data if force else {}
            )
            
            if created:
                created_count += 1
            elif force:
                updated_count += 1
        
        self.stdout.write(f'   Created: {created_count}, Updated: {updated_count} legal codes')

    def populate_courts(self, force=False):
        self.stdout.write('🏛️ Populating courts...')
        
        courts_data = [
            # Supreme Court
            {
                'court_name_fr': 'Cour Suprême',
                'court_name_ar': 'المحكمة العليا',
                'court_level': 'cassation',
                'jurisdiction_type': 'civil',
                'wilaya': '16',
                'city': 'Alger',
                'address': 'Rue 11 Décembre 1960, El-Biar, Alger',
                'phone': '+213 21 92 15 16',
                'president': 'Mohamed Abdelmalek',
                'specializations': ['Civil', 'Pénal', 'Commercial', 'Social', 'Foncier'],
                'working_hours': {
                    'sunday_thursday': '08:00-16:30',
                    'friday': 'Fermé',
                    'saturday': 'Fermé'
                },
                'established_date': date(2011, 7, 26),
                'is_active': True
            },
            # Council of State
            {
                'court_name_fr': 'Conseil d\'État',
                'court_name_ar': 'مجلس الدولة',
                'court_level': 'cassation',
                'jurisdiction_type': 'administratif',
                'wilaya': '16',
                'city': 'Alger',
                'address': 'Place Ahmed Bey, Alger',
                'phone': '+213 21 67 89 12',
                'president': 'Leila Benmansour',
                'specializations': ['Administratif', 'Foncier'],
                'established_date': date(1998, 5, 30),
                'is_active': True
            },
            # Algiers Court of Appeal
            {
                'court_name_fr': 'Cour d\'Alger',
                'court_name_ar': 'مجلس قضاء الجزائر',
                'court_level': 'appel',
                'jurisdiction_type': 'civil',
                'wilaya': '16',
                'city': 'Alger',
                'address': 'Place des Martyrs, Alger Centre',
                'phone': '+213 21 63 45 78',
                'president': 'Fatima Zerhouni',
                'vice_president': 'Hamid Boubekeur',
                'procureur': 'Ahmed Talaouinet',
                'specializations': ['Civil', 'Pénal', 'Commercial', 'Famille', 'Social'],
                'is_active': True
            },
            # Tribunal of Sidi M'hamed
            {
                'court_name_fr': 'Tribunal de Sidi M\'hamed',
                'court_name_ar': 'محكمة سيدي امحمد',
                'court_level': 'premiere',
                'jurisdiction_type': 'civil',
                'wilaya': '16',
                'city': 'Alger',
                'address': 'Rue Larbi Ben M\'hidi, Alger',
                'phone': '+213 21 73 25 41',
                'president': 'Ahmed Benamar',
                'procureur': 'Karim Boudali',
                'specializations': ['Civil', 'Pénal', 'Famille', 'Commercial'],
                'is_active': True
            },
            # Commercial Specialized Tribunal of Algiers
            {
                'court_name_fr': 'Tribunal Commercial Spécialisé d\'Alger',
                'court_name_ar': 'المحكمة التجارية المتخصصة بالجزائر',
                'court_level': 'premiere',
                'jurisdiction_type': 'commercial',
                'wilaya': '16',
                'city': 'Alger',
                'address': 'Zone d\'activité de Baba Hassen, Alger',
                'phone': '+213 21 38 67 92',
                'president': 'Mourad Hadj Ali',
                'specializations': ['Propriété Commerciale', 'Sociétés Commerciales', 'Faillite', 'Banque', 'Commerce International'],
                'established_date': date(2022, 7, 12),
                'is_active': True
            },
            # Oran Courts
            {
                'court_name_fr': 'Cour d\'Oran',
                'court_name_ar': 'مجلس قضاء وهران',
                'court_level': 'appel',
                'jurisdiction_type': 'civil',
                'wilaya': '31',
                'city': 'Oran',
                'address': 'Boulevard de la Révolution, Oran',
                'phone': '+213 41 33 24 67',
                'president': 'Noureddine Sahli',
                'specializations': ['Civil', 'Pénal', 'Commercial'],
                'is_active': True
            },
            {
                'court_name_fr': 'Tribunal d\'Oran',
                'court_name_ar': 'محكمة وهران',
                'court_level': 'premiere',
                'jurisdiction_type': 'civil',
                'wilaya': '31',
                'city': 'Oran',
                'address': 'Place du 1er Novembre, Oran',
                'phone': '+213 41 39 15 28',
                'president': 'Omar Benali',
                'procureur': 'Salima Khodja',
                'specializations': ['Civil', 'Pénal', 'Famille', 'Maritime', 'Commercial'],
                'is_active': True
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for court_data in courts_data:
            obj, created = AlgerianCourt.objects.update_or_create(
                court_name_fr=court_data['court_name_fr'],
                wilaya=court_data['wilaya'],
                defaults=court_data if force else {}
            )
            
            if created:
                created_count += 1
            elif force:
                updated_count += 1
        
        self.stdout.write(f'   Created: {created_count}, Updated: {updated_count} courts')

    def populate_tax_configurations(self, force=False):
        self.stdout.write('💰 Populating tax configurations...')
        
        tax_configs_data = [
            # TVA
            {
                'tax_type': 'tva',
                'tax_rate': 19.00,
                'description_fr': 'Taxe sur la Valeur Ajoutée - Taux normal',
                'description_ar': 'الرسم على القيمة المضافة - المعدل العادي',
                'effective_from': date(2017, 1, 1),
                'minimum_amount': 0,
                'is_active': True
            },
            {
                'tax_type': 'tva',
                'tax_rate': 9.00,
                'description_fr': 'Taxe sur la Valeur Ajoutée - Taux réduit',
                'description_ar': 'الرسم على القيمة المضافة - المعدل المخفض',
                'effective_from': date(2017, 1, 1),
                'minimum_amount': 0,
                'is_active': True
            },
            # IRG
            {
                'tax_type': 'irg',
                'tax_rate': 23.00,
                'description_fr': 'Impôt sur le Revenu Global - Tranche supérieure',
                'description_ar': 'الضريبة على الدخل الإجمالي - الشريحة العليا',
                'effective_from': date(2023, 1, 1),
                'minimum_amount': 240000,
                'is_active': True
            },
            {
                'tax_type': 'irg',
                'tax_rate': 35.00,
                'description_fr': 'Impôt sur le Revenu Global - Revenus exceptionnels',
                'description_ar': 'الضريبة على الدخل الإجمالي - الإيرادات الاستثنائية',
                'effective_from': date(2023, 1, 1),
                'minimum_amount': 1440000,
                'is_active': True
            },
            # IBS
            {
                'tax_type': 'ibs',
                'tax_rate': 25.00,
                'description_fr': 'Impôt sur les Bénéfices des Sociétés - Taux normal',
                'description_ar': 'الضريبة على أرباح الشركات - المعدل العادي',
                'effective_from': date(2022, 1, 1),
                'minimum_amount': 0,
                'is_active': True
            },
            # TAP
            {
                'tax_type': 'tap',
                'tax_rate': 2.00,
                'description_fr': 'Taxe sur l\'Activité Professionnelle',
                'description_ar': 'الرسم على النشاط المهني',
                'effective_from': date(2020, 1, 1),
                'minimum_amount': 0,
                'is_active': True
            },
            # Versement Forfaitaire
            {
                'tax_type': 'versement_forfaitaire',
                'tax_rate': 12.00,
                'description_fr': 'Versement Forfaitaire - Salaires',
                'description_ar': 'الدفع الجزافي - الأجور',
                'effective_from': date(2020, 1, 1),
                'minimum_amount': 0,
                'is_active': True
            },
            # Timbre
            {
                'tax_type': 'timbre',
                'tax_rate': 0.00,
                'description_fr': 'Droit de Timbre - Actes juridiques',
                'description_ar': 'رسم الطابع - الأعمال القانونية',
                'effective_from': date(2020, 1, 1),
                'minimum_amount': 1000,
                'maximum_amount': 100000,
                'is_active': True
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for tax_data in tax_configs_data:
            obj, created = TaxConfiguration.objects.update_or_create(
                tax_type=tax_data['tax_type'],
                tax_rate=tax_data['tax_rate'],
                effective_from=tax_data['effective_from'],
                defaults=tax_data if force else {}
            )
            
            if created:
                created_count += 1
            elif force:
                updated_count += 1
        
        self.stdout.write(f'   Created: {created_count}, Updated: {updated_count} tax configurations')

    def populate_legal_procedures(self, force=False):
        self.stdout.write('⚖️ Populating legal procedures...')
        
        procedures_data = [
            # Civil Procedures
            {
                'procedure_name_fr': 'Requête introductive d\'instance',
                'procedure_name_ar': 'عريضة افتتاح الدعوى',
                'procedure_type': 'civil',
                'court_level': 'premiere',
                'description_fr': 'Procédure d\'introduction d\'une action civile devant le tribunal de première instance.',
                'description_ar': 'إجراءات رفع دعوى مدنية أمام محكمة الدرجة الأولى.',
                'template_content_fr': 'REQUÊTE INTRODUCTIVE D\'INSTANCE\n\nMonsieur le Président du Tribunal de [JURIDICTION],\n\nJ\'ai l\'honneur de porter à votre connaissance...',
                'template_content_ar': 'عريضة افتتاح دعوى\n\nسيدي رئيس محكمة [الجهة القضائية],\n\nيشرفني أن أعرض عليكم...',
                'required_documents': [
                    'Pièce d\'identité du demandeur',
                    'Justificatifs du litige',
                    'Mandat d\'avocat',
                    'Certificat de non-réconciliation (si applicable)'
                ],
                'timeline_days': 30,
                'fees_range_min': 1000,
                'fees_range_max': 5000,
                'legal_references': ['Art. 13 à 16 CPC'],
                'is_active': True
            },
            {
                'procedure_name_fr': 'Appel',
                'procedure_name_ar': 'الاستئناف',
                'procedure_type': 'civil',
                'court_level': 'appel',
                'description_fr': 'Procédure d\'appel d\'un jugement rendu en première instance.',
                'description_ar': 'إجراءات استئناف حكم صادر عن الدرجة الأولى.',
                'required_documents': [
                    'Copie du jugement attaqué',
                    'Déclaration d\'appel',
                    'Mémoire d\'appel',
                    'Mandat d\'avocat'
                ],
                'timeline_days': 15,
                'fees_range_min': 2000,
                'fees_range_max': 10000,
                'legal_references': ['Art. 35 à 45 CPC'],
                'is_active': True
            },
            # Commercial Procedures
            {
                'procedure_name_fr': 'Procédure de sauvegarde',
                'procedure_name_ar': 'إجراءات الحماية',
                'procedure_type': 'commercial',
                'court_level': 'premiere',
                'description_fr': 'Procédure préventive permettant à une entreprise en difficulté de négocier avec ses créanciers.',
                'description_ar': 'إجراءات وقائية تتيح للمؤسسة المتعثرة التفاوض مع دائنيها.',
                'required_documents': [
                    'États financiers des 3 dernières années',
                    'Liste des créanciers',
                    'Plan de redressement',
                    'Justificatifs des difficultés'
                ],
                'timeline_days': 60,
                'fees_range_min': 50000,
                'fees_range_max': 200000,
                'legal_references': ['Art. 200 à 230 Code Commerce'],
                'is_active': True
            },
            # Administrative Procedures
            {
                'procedure_name_fr': 'Recours pour excès de pouvoir',
                'procedure_name_ar': 'طعن بتجاوز السلطة',
                'procedure_type': 'administrative',
                'court_level': 'premiere',
                'description_fr': 'Recours contre une décision administrative illégale.',
                'description_ar': 'طعن ضد قرار إداري غير قانوني.',
                'required_documents': [
                    'Copie de la décision attaquée',
                    'Justificatifs de l\'intérêt à agir',
                    'Mémoire exposant les moyens',
                    'Preuve de notification préalable'
                ],
                'timeline_days': 60,
                'fees_range_min': 3000,
                'fees_range_max': 15000,
                'legal_references': ['Art. 7 à 12 CPA'],
                'is_active': True
            },
            # Criminal Procedures
            {
                'procedure_name_fr': 'Constitution de partie civile',
                'procedure_name_ar': 'الانضمام كطرف مدني',
                'procedure_type': 'penal',
                'court_level': 'premiere',
                'description_fr': 'Procédure permettant à la victime de se constituer partie civile dans une instance pénale.',
                'description_ar': 'إجراءات تتيح للضحية الانضمام كطرف مدني في دعوى جزائية.',
                'required_documents': [
                    'Plainte avec constitution de partie civile',
                    'Justificatifs du préjudice',
                    'Pièces d\'identité',
                    'Certificat médical (si applicable)'
                ],
                'timeline_days': 10,
                'fees_range_min': 500,
                'fees_range_max': 3000,
                'legal_references': ['Art. 72 à 78 CPP'],
                'is_active': True
            },
            # Family Procedures
            {
                'procedure_name_fr': 'Divorce pour discorde',
                'procedure_name_ar': 'الطلاق للشقاق',
                'procedure_type': 'famille',
                'court_level': 'premiere',
                'description_fr': 'Procédure de divorce pour mésentente entre époux.',
                'description_ar': 'إجراءات الطلاق للخلاف بين الزوجين.',
                'required_documents': [
                    'Acte de mariage',
                    'Actes de naissance des enfants',
                    'Justificatifs des revenus',
                    'Certificat de non-réconciliation'
                ],
                'timeline_days': 90,
                'fees_range_min': 5000,
                'fees_range_max': 25000,
                'legal_references': ['Art. 53 à 57 Code Famille'],
                'is_active': True
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for procedure_data in procedures_data:
            obj, created = LegalProcedure.objects.update_or_create(
                procedure_name_fr=procedure_data['procedure_name_fr'],
                procedure_type=procedure_data['procedure_type'],
                defaults=procedure_data if force else {}
            )
            
            if created:
                created_count += 1
            elif force:
                updated_count += 1
        
        self.stdout.write(f'   Created: {created_count}, Updated: {updated_count} legal procedures')

# ===================================
# PATH: legal_system/management/commands/create_sample_data.py
# ===================================
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.db import transaction
from cases.models import Case, Jurisdiction, CaseType, Audience
from documents.models import Document, DocumentTemplate
from billing.models import BillingInfo, Invoice, Expense
from tasks.models import Task
from notifications.models import Notification
from admin_panel.models import Subscription
from datetime import date, datetime, timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Create comprehensive sample data for testing and demonstration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=10,
            help='Number of sample users to create'
        )
        parser.add_argument(
            '--cases',
            type=int,
            default=50,
            help='Number of sample cases to create'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing sample data before creating new'
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.clear_sample_data()
        
        self.stdout.write('🚀 Creating comprehensive sample data...')
        
        try:
            with transaction.atomic():
                # Create users
                users = self.create_sample_users(options['users'])
                
                # Create jurisdictions and case types
                jurisdictions = self.create_sample_jurisdictions()
                case_types = self.create_sample_case_types()
                
                # Create document templates
                self.create_document_templates(users[0])
                
                # Create cases with related data
                self.create_sample_cases(users, jurisdictions, case_types, options['cases'])
                
            self.stdout.write(
                self.style.SUCCESS(f'✅ Successfully created sample data!')
            )
            self.stdout.write(f'   👥 Users: {len(users)}')
            self.stdout.write(f'   📁 Cases: {options["cases"]}')
            self.stdout.write(f'   🏛️ Jurisdictions: {len(jurisdictions)}')
            self.stdout.write(f'   📋 Case Types: {len(case_types)}')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error creating sample data: {str(e)}')
            )
            raise CommandError(f'Sample data creation failed: {str(e)}')

    def clear_sample_data(self):
        self.stdout.write('🗑️ Clearing existing sample data...')
        
        # Delete users with 'test' or 'sample' in username
        test_users = User.objects.filter(
            username__icontains='test'
        ) | User.objects.filter(
            username__icontains='sample'
        ) | User.objects.filter(
            username__icontains='lawyer'
        )
        
        deleted_count = test_users.count()
        test_users.delete()
        
        self.stdout.write(f'   Deleted {deleted_count} test users and related data')

    def create_sample_users(self, count):
        self.stdout.write(f'👥 Creating {count} sample users...')
        
        users = []
        wilayas = ['16', '31', '09', '25', '06', '15', '13', '07', '34', '35']
        
        for i in range(count):
            user = User.objects.create_user(
                username=f'lawyer_test_{i+1:03d}',
                email=f'lawyer.test.{i+1:03d}@legal-system.dz',
                password='TestPassword123!',
                first_name=f'Ahmed' if i % 2 == 0 else 'Fatima',
                last_name=f'Benali_{i+1:03d}',
                role='lawyer',
                status='active',
                subscription_status='active',
                subscription_plan='professional',
                phone=f'055{random.randint(1000000, 9999999)}',
                wilaya=random.choice(wilayas),
                bar_number=f'ALG{i+1:05d}',
                address=f'{random.randint(1, 150)} Rue de la Justice, Alger'
            )
            
            # Create subscription for each user
            Subscription.objects.create(
                user=user,
                plan_name='professional',
                status='active',
                start_date=date.today() - timedelta(days=random.randint(30, 365)),
                end_date=date.today() + timedelta(days=365),
                amount=random.randint(15000, 25000),
                currency='DZD',
                max_cases=100,
                max_documents=1000,
                max_storage_gb=10,
                api_access=True,
                priority_support=True
            )
            
            users.append(user)
        
        # Create one admin user
        admin_user = User.objects.create_user(
           username='admin_test',
            email='admin.test@legal-system.dz',
            password='AdminPassword123!',
            first_name='Admin',
            last_name='System',
            role='admin',
            status='active',
            is_staff=True,
            is_superuser=True
        )
        users.append(admin_user)
        
        return users

    def create_sample_jurisdictions(self):
        self.stdout.write('🏛️ Creating sample jurisdictions...')
        
        jurisdictions_data = [
            {
                'name_fr': 'Tribunal de Sidi M\'hamed',
                'name_ar': 'محكمة سيدي امحمد',
                'type_fr': 'tribunal',
                'type_ar': 'محكمة',
                'wilaya': '16',
                'level': 'premiere'
            },
            {
                'name_fr': 'Cour d\'Alger',
                'name_ar': 'مجلس قضاء الجزائر',
                'type_fr': 'cour',
                'type_ar': 'مجلس قضاء',
                'wilaya': '16',
                'level': 'appel'
            },
            {
                'name_fr': 'Tribunal Commercial d\'Alger',
                'name_ar': 'المحكمة التجارية الجزائر',
                'type_fr': 'tribunal_commercial',
                'type_ar': 'محكمة تجارية',
                'wilaya': '16',
                'level': 'premiere'
            },
            {
                'name_fr': 'Tribunal d\'Oran',
                'name_ar': 'محكمة وهران',
                'type_fr': 'tribunal',
                'type_ar': 'محكمة',
                'wilaya': '31',
                'level': 'premiere'
            }
        ]
        
        jurisdictions = []
        for data in jurisdictions_data:
            jurisdiction, created = Jurisdiction.objects.get_or_create(**data)
            jurisdictions.append(jurisdiction)
        
        return jurisdictions

    def create_sample_case_types(self):
        self.stdout.write('📋 Creating sample case types...')
        
        case_types_data = [
            {
                'category_fr': 'civil',
                'category_ar': 'مدني',
                'subtype_fr': 'Dette commerciale',
                'subtype_ar': 'دين تجاري',
                'reference_article': 'Art. 124 Code Civil'
            },
            {
                'category_fr': 'civil',
                'category_ar': 'مدني',
                'subtype_fr': 'Succession',
                'subtype_ar': 'إرث',
                'reference_article': 'Art. 126 Code Civil'
            },
            {
                'category_fr': 'penal',
                'category_ar': 'جزائي',
                'subtype_fr': 'Vol',
                'subtype_ar': 'سرقة',
                'reference_article': 'Art. 350 Code Pénal'
            },
            {
                'category_fr': 'commercial',
                'category_ar': 'تجاري',
                'subtype_fr': 'Litige contractuel',
                'subtype_ar': 'نزاع تعاقدي',
                'reference_article': 'Art. 106 Code Commerce'
            },
            {
                'category_fr': 'administratif',
                'category_ar': 'إداري',
                'subtype_fr': 'Recours contre décision',
                'subtype_ar': 'طعن ضد قرار',
                'reference_article': 'Art. 7 CPA'
            }
        ]
        
        case_types = []
        for data in case_types_data:
            case_type, created = CaseType.objects.get_or_create(
                category_fr=data['category_fr'],
                subtype_fr=data['subtype_fr'],
                defaults=data
            )
            case_types.append(case_type)
        
        return case_types

    def create_document_templates(self, user):
        self.stdout.write('📄 Creating document templates...')
        
        templates_data = [
            {
                'name': 'Constitution d\'Avocat',
                'template_type': 'constitution_avocat',
                'description': 'Modèle de constitution d\'avocat standard',
                'content_fr': '''CONSTITUTION D'AVOCAT

Monsieur le Président du Tribunal de {{ jurisdiction }},

J'ai l'honneur de vous faire savoir que Monsieur/Madame {{ client_name }}, 
demeurant à {{ client_address }}, m'a constitué son avocat dans l'affaire 
qui l'oppose à {{ opponent }} concernant {{ case_description }}.

En conséquence, je vous prie de bien vouloir noter ma constitution et 
m'adresser toutes les notifications relatives à cette affaire.

Fait à Alger, le {{ date }}

Maître {{ lawyer_name }}
Avocat au Barreau d'{{ wilaya }}''',
                'variables': ['jurisdiction', 'client_name', 'client_address', 'opponent', 'case_description', 'date', 'lawyer_name', 'wilaya'],
                'is_active': True,
                'is_public': True
            },
            {
                'name': 'Requête Introductive',
                'template_type': 'requete_introductive',
                'description': 'Modèle de requête introductive d\'instance',
                'content_fr': '''REQUÊTE INTRODUCTIVE D'INSTANCE

Monsieur le Président du Tribunal de {{ jurisdiction }},

{{ client_name }}, {{ client_profession }}, demeurant à {{ client_address }},
représenté(e) par Maître {{ lawyer_name }}, avocat au barreau d'{{ wilaya }},

A l'honneur d'exposer respectueusement ce qui suit :

EXPOSÉ DES FAITS :
{{ facts }}

EN DROIT :
{{ legal_basis }}

PAR CES MOTIFS :
Plaise au Tribunal ordonner {{ requested_action }}

Avec dépens.

Fait à {{ city }}, le {{ date }}

Maître {{ lawyer_name }}''',
                'variables': ['jurisdiction', 'client_name', 'client_profession', 'client_address', 'lawyer_name', 'wilaya', 'facts', 'legal_basis', 'requested_action', 'city', 'date'],
                'is_active': True,
                'is_public': True
            }
        ]
        
        for template_data in templates_data:
            DocumentTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults={**template_data, 'user': user}
            )

    def create_sample_cases(self, users, jurisdictions, case_types, count):
        self.stdout.write(f'📁 Creating {count} sample cases with related data...')
        
        statuses = ['ouvert', 'en_cours_instruction', 'en_delibere', 'juge', 'appel_interjete', 'clos']
        priorities = ['low', 'medium', 'high', 'urgent']
        
        client_names = [
            'Ahmed Benali', 'Fatima Kaci', 'Omar Boumediene', 'Aicha Zenati',
            'Mohamed Cherif', 'Samira Hadj', 'Karim Benaissa', 'Nadia Brahimi',
            'Youcef Meziane', 'Leila Bouaziz', 'Said Mohand', 'Zineb Taleb'
        ]
        
        for i in range(count):
            user = random.choice(users[:-1])  # Exclude admin user
            jurisdiction = random.choice(jurisdictions)
            case_type = random.choice(case_types)
            client_name = random.choice(client_names)
            
            # Create case
            open_date = date.today() - timedelta(days=random.randint(1, 730))
            close_date = None
            status = random.choice(statuses)
            
            if status in ['juge', 'clos']:
                close_date = open_date + timedelta(days=random.randint(30, 365))
            
            case = Case.objects.create(
                reference=f'{case_type.category_fr.upper()[:3]}-{date.today().year}-{i+1:04d}',
                title=f'Affaire {client_name} c/ Partie Adverse {i+1}',
                client_name=client_name,
                client_email=f'{client_name.lower().replace(" ", ".")}@email.dz',
                client_phone=f'055{random.randint(1000000, 9999999)}',
                client_address=f'{random.randint(1, 200)} Rue {random.choice(["des Martyrs", "de l\'Indépendance", "1er Novembre"])}, {jurisdiction.name_fr.split()[-1]}',
                jurisdiction=jurisdiction,
                case_type=case_type,
                status=status,
                priority=random.choice(priorities),
                open_date=open_date,
                close_date=close_date,
                description=f'Litige concernant {case_type.subtype_fr.lower()} entre {client_name} et la partie adverse.',
                amount_in_dispute=random.randint(50000, 5000000) if random.choice([True, False]) else None,
                confidentiality_agreement=True,
                no_conflict_interest=True,
                lawyer_mandate=True,
                consent_given=True,
                user=user
            )
            
            # Create related data for each case
            self.create_case_documents(case)
            self.create_case_audiences(case)
            self.create_case_billing(case)
            self.create_case_tasks(case)
            self.create_case_expenses(case)
            self.create_case_notifications(case)

    def create_case_documents(self, case):
        """Create sample documents for a case"""
        doc_types = ['constitution_avocat', 'requete_introductive', 'conclusions', 'memoire']
        
        for i, doc_type in enumerate(random.sample(doc_types, random.randint(2, 4))):
            Document.objects.create(
                title_fr=f'{doc_type.replace("_", " ").title()} - {case.reference}',
                document_type='template',
                template_type=doc_type,
                language='fr',
                case=case,
                content=f'Contenu du document {doc_type} pour l\'affaire {case.reference}...',
                version=1,
                is_final=random.choice([True, False]),
                user=case.user,
                created_at=case.open_date + timedelta(days=i*7)
            )

    def create_case_audiences(self, case):
        """Create sample audiences for a case"""
        if case.status in ['ouvert', 'en_cours_instruction']:
            return  # No audiences yet for new cases
        
        audience_types = [
            ('mise_en_etat', 'Mise en état'),
            ('plaidoirie', 'Plaidoirie'),
            ('jugement', 'Jugement')
        ]
        
        results = [
            ('report', 'Report'),
            ('delibere', 'Délibéré'),
            ('juge', 'Jugé')
        ]
        
        current_date = case.open_date + timedelta(days=random.randint(30, 60))
        
        for i, (type_key, type_label) in enumerate(audience_types[:random.randint(1, 3)]):
            if current_date > (case.close_date or date.today()):
                break
                
            result_key, result_label = random.choice(results)
            
            Audience.objects.create(
                case=case,
                date=datetime.combine(current_date, datetime.min.time()) + timedelta(hours=random.randint(9, 16)),
                type_fr=type_label,
                type_ar=f'النوع {i+1}',
                chamber_fr='Civile',
                chamber_ar='مدنية',
                result_fr=result_label,
                result_ar=f'النتيجة {i+1}',
                stage_fr='Instruction',
                stage_ar='التحقيق',
                notes=f'Audience {type_label.lower()} du {current_date}. {result_label}.',
                judge_name=random.choice(['Juge Benali', 'Juge Kaci', 'Juge Meziane']),
                user=case.user
            )
            
            current_date += timedelta(days=random.randint(30, 90))

    def create_case_billing(self, case):
        """Create billing information for a case"""
        fee_types = ['fixed', 'hourly', 'contingency']
        fee_type = random.choice(fee_types)
        
        amount = random.randint(50000, 300000)
        if fee_type == 'hourly':
            hourly_rate = random.randint(5000, 15000)
            hours_worked = random.randint(10, 100)
            amount = hourly_rate * hours_worked
        
        invoice_date = case.open_date + timedelta(days=random.randint(7, 30))
        
        BillingInfo.objects.create(
            case=case,
            fee_type=fee_type,
            amount=amount,
            hourly_rate=random.randint(5000, 15000) if fee_type == 'hourly' else None,
            hours_worked=random.randint(10, 100) if fee_type == 'hourly' else 0,
            advanced_expenses=random.randint(1000, 10000),
            court_fees=random.randint(500, 5000),
            nif='123456789012345',
            nis='098765432109876',
            rc='12A3456789',
            tva='123456',
            invoice_number=f'INV-{case.reference}-001',
            invoice_date=invoice_date,
            due_date=invoice_date + timedelta(days=30),
            payment_status=random.choice(['pending', 'paid', 'partially_paid', 'overdue']),
            payment_date=invoice_date + timedelta(days=random.randint(1, 45)) if random.choice([True, False]) else None,
            user=case.user
        )

        # Create detailed invoice
        Invoice.objects.create(
            invoice_number=f'INV-{case.reference}-001',
            invoice_date=invoice_date,
            due_date=invoice_date + timedelta(days=30),
            case=case,
            client_name=case.client_name,
            client_address=case.client_address,
            client_email=case.client_email,
            client_phone=case.client_phone,
            status=random.choice(['draft', 'sent', 'paid']),
            subtotal=amount,
            tax_rate=19.00,
            tax_amount=amount * 0.19,
            total_amount=amount * 1.19,
            amount_paid=amount * 1.19 if random.choice([True, False]) else 0,
            payment_date=invoice_date + timedelta(days=random.randint(1, 30)) if random.choice([True, False]) else None,
            user=case.user
        )

    def create_case_tasks(self, case):
        """Create sample tasks for a case"""
        task_templates = [
            'Préparer le dossier client',
            'Rédiger la requête introductive',
            'Collecter les pièces justificatives',
            'Préparer les conclusions',
            'Organiser l\'expertise',
            'Préparer la plaidoirie',
            'Suivi post-jugement'
        ]
        
        task_statuses = ['pending', 'in_progress', 'completed', 'cancelled']
        priorities = ['low', 'medium', 'high', 'urgent']
        
        for i, task_title in enumerate(random.sample(task_templates, random.randint(3, 6))):
            due_date = case.open_date + timedelta(days=random.randint(1, 180))
            status = random.choice(task_statuses)
            
            completed_date = None
            if status == 'completed':
                completed_date = due_date - timedelta(days=random.randint(1, 10))
            
            Task.objects.create(
                title=f'{task_title} - {case.reference}',
                description=f'Tâche pour l\'affaire {case.title}',
                case=case,
                priority=random.choice(priorities),
                status=status,
                due_date=datetime.combine(due_date, datetime.min.time()) + timedelta(hours=random.randint(9, 17)),
                completed_date=completed_date,
                assigned_to=case.user,
                created_by=case.user,
                estimated_hours=random.randint(2, 20),
                actual_hours=random.randint(1, 25) if status == 'completed' else 0,
                progress_percentage=100 if status == 'completed' else random.randint(0, 80),
                user=case.user
            )

    def create_case_expenses(self, case):
        """Create sample expenses for a case"""
        expense_categories = [
            ('court_fees', 'Frais de justice'),
            ('expert_fees', 'Honoraires d\'expert'),
            ('travel', 'Frais de déplacement'),
            ('administrative', 'Frais administratifs'),
            ('translation', 'Frais de traduction')
        ]
        
        for i in range(random.randint(1, 4)):
            category, description = random.choice(expense_categories)
            expense_date = case.open_date + timedelta(days=random.randint(1, 200))
            
            Expense.objects.create(
                case=case,
                category=category,
                description=f'{description} - {case.reference}',
                amount=random.randint(1000, 50000),
                expense_date=expense_date,
                receipt_number=f'REC-{case.reference}-{i+1:03d}',
                is_reimbursable=random.choice([True, False]),
                is_reimbursed=random.choice([True, False]),
                user=case.user
            )

    def create_case_notifications(self, case):
        """Create sample notifications for a case"""
        notification_types = [
            ('case_update', 'Mise à jour du dossier'),
            ('audience_reminder', 'Rappel d\'audience'),
            ('task_due', 'Tâche à échéance'),
            ('payment_received', 'Paiement reçu')
        ]
        
        for i in range(random.randint(1, 3)):
            notif_type, title = random.choice(notification_types)
            
            Notification.objects.create(
                user=case.user,
                title=f'{title} - {case.reference}',
                message=f'Notification concernant l\'affaire {case.title}',
                notification_type=notif_type,
                priority=random.choice(['low', 'medium', 'high']),
                is_read=random.choice([True, False]),
                related_object_type='case',
                related_object_id=case.id,
                created_at=case.open_date + timedelta(days=random.randint(1, 100))
            )