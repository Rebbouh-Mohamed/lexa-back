# Generated by Django 4.2.7 on 2025-06-17 00:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Case',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reference', models.CharField(max_length=50, unique=True)),
                ('title', models.CharField(max_length=300)),
                ('client_name', models.CharField(max_length=200)),
                ('client_email', models.EmailField(blank=True, max_length=254)),
                ('client_phone', models.CharField(blank=True, max_length=20)),
                ('client_address', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('ouvert', 'Ouvert'), ('en_cours_instruction', "En cours d'instruction"), ('en_delibere', 'En délibéré'), ('juge', 'Jugé'), ('appel_interjete', 'Appel interjeté'), ('pourvoi_cassation', 'Pourvoi en cassation'), ('clos', 'Clos'), ('archive', 'Archivé')], default='ouvert', max_length=50)),
                ('open_date', models.DateField()),
                ('close_date', models.DateField(blank=True, null=True)),
                ('description', models.TextField()),
                ('amount_in_dispute', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True)),
                ('currency', models.CharField(default='DZD', max_length=3)),
                ('confidentiality_agreement', models.BooleanField(default=False)),
                ('no_conflict_interest', models.BooleanField(default=False)),
                ('lawyer_mandate', models.BooleanField(default=False)),
                ('consent_given', models.BooleanField(default=False)),
                ('priority', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')], default='medium', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assigned_lawyers', models.ManyToManyField(blank=True, related_name='assigned_cases', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Case',
                'verbose_name_plural': 'Cases',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Jurisdiction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_fr', models.CharField(max_length=200)),
                ('name_ar', models.CharField(max_length=200)),
                ('type_fr', models.CharField(choices=[('tribunal', 'Tribunal'), ('tribunal_commercial', 'Tribunal Commercial'), ('tribunal_administratif', 'Tribunal Administratif'), ('tribunal_criminel', 'Tribunal Criminel'), ('cour', "Cour d'Appel"), ('cour_supreme', 'Cour Suprême'), ('conseil_etat', "Conseil d'État")], max_length=50)),
                ('type_ar', models.CharField(max_length=200)),
                ('wilaya', models.CharField(max_length=2)),
                ('level', models.CharField(choices=[('premiere', 'Première Instance'), ('appel', 'Appel'), ('cassation', 'Cassation')], max_length=20)),
                ('president', models.CharField(blank=True, max_length=200)),
                ('vice_president', models.CharField(blank=True, max_length=200)),
                ('procureur', models.CharField(blank=True, max_length=200)),
                ('sections', models.JSONField(blank=True, default=list)),
                ('chambers', models.JSONField(blank=True, default=list)),
                ('competence', models.JSONField(blank=True, default=list)),
                ('address', models.TextField(blank=True)),
                ('phone', models.CharField(blank=True, max_length=20)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('is_active', models.BooleanField(default=True)),
                ('established', models.DateField(blank=True, null=True)),
                ('specialization', models.CharField(blank=True, max_length=200)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Jurisdiction',
                'verbose_name_plural': 'Jurisdictions',
                'ordering': ['wilaya', 'name_fr'],
            },
        ),
        migrations.CreateModel(
            name='CaseType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category_fr', models.CharField(choices=[('civil', 'Civil'), ('penal', 'Pénal'), ('administratif', 'Administratif'), ('commercial', 'Commercial'), ('famille', 'Famille'), ('foncier', 'Foncier'), ('social', 'Social')], max_length=50)),
                ('category_ar', models.CharField(max_length=200)),
                ('subtype_fr', models.CharField(max_length=200)),
                ('subtype_ar', models.CharField(max_length=200)),
                ('reference_article', models.CharField(blank=True, max_length=200)),
                ('description_fr', models.TextField(blank=True)),
                ('description_ar', models.TextField(blank=True)),
                ('typical_duration_days', models.PositiveIntegerField(blank=True, null=True)),
                ('required_documents', models.JSONField(blank=True, default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Case Type',
                'verbose_name_plural': 'Case Types',
                'unique_together': {('category_fr', 'subtype_fr')},
            },
        ),
        migrations.CreateModel(
            name='CaseMetric',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_hours_worked', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('billable_hours', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total_fees', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('total_expenses', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('amount_paid', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('documents_count', models.PositiveIntegerField(default=0)),
                ('audiences_count', models.PositiveIntegerField(default=0)),
                ('tasks_completed', models.PositiveIntegerField(default=0)),
                ('tasks_pending', models.PositiveIntegerField(default=0)),
                ('client_satisfaction', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('case_complexity', models.PositiveSmallIntegerField(default=3)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('case', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='metrics', to='cases.case')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Case Metric',
                'verbose_name_plural': 'Case Metrics',
            },
        ),
        migrations.AddField(
            model_name='case',
            name='case_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='cases.casetype'),
        ),
        migrations.AddField(
            model_name='case',
            name='jurisdiction',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='cases.jurisdiction'),
        ),
        migrations.AddField(
            model_name='case',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cases', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Audience',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField()),
                ('type_fr', models.CharField(choices=[('mise_en_etat', 'Mise en état'), ('plaidoirie', 'Plaidoirie'), ('jugement', 'Jugement'), ('enquete', 'Enquête'), ('expertise', 'Expertise'), ('renvoi', 'Renvoi')], max_length=50)),
                ('type_ar', models.CharField(max_length=200)),
                ('chamber_fr', models.CharField(choices=[('civile', 'Civile'), ('penale', 'Pénale'), ('administrative', 'Administrative'), ('commerciale', 'Commerciale'), ('famille', 'Famille'), ('sociale', 'Sociale')], max_length=50)),
                ('chamber_ar', models.CharField(max_length=200)),
                ('result_fr', models.CharField(choices=[('report', 'Report'), ('delibere', 'Délibéré'), ('juge', 'Jugé'), ('expertise', 'Expertise ordonnée'), ('enquete', 'Enquête ordonnée'), ('renvoi', 'Renvoi')], max_length=50)),
                ('result_ar', models.CharField(max_length=200)),
                ('stage_fr', models.CharField(choices=[('introduction', 'Introduction'), ('instruction', 'Instruction'), ('plaidoirie', 'Plaidoirie'), ('delibere', 'Délibéré'), ('jugement', 'Jugement')], max_length=50)),
                ('stage_ar', models.CharField(max_length=200)),
                ('notes', models.TextField(blank=True)),
                ('judge_name', models.CharField(blank=True, max_length=200)),
                ('court_clerk', models.CharField(blank=True, max_length=200)),
                ('opposing_counsel', models.CharField(blank=True, max_length=200)),
                ('next_hearing_date', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('case', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='audiences', to='cases.case')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Audience',
                'verbose_name_plural': 'Audiences',
                'ordering': ['-date'],
            },
        ),
    ]
