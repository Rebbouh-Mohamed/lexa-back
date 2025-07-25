# Generated by Django 4.2.7 on 2025-06-17 00:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cases', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title_fr', models.CharField(max_length=300)),
                ('title_ar', models.CharField(blank=True, max_length=300)),
                ('document_type', models.CharField(choices=[('template', 'Generated from template'), ('uploaded', 'Uploaded file'), ('scanned', 'Scanned document'), ('external', 'External document')], default='uploaded', max_length=20)),
                ('template_type', models.CharField(blank=True, max_length=50)),
                ('language', models.CharField(choices=[('fr', 'French'), ('ar', 'Arabic'), ('bilingual', 'Bilingual')], default='fr', max_length=20)),
                ('content', models.TextField(blank=True)),
                ('file', models.FileField(blank=True, null=True, upload_to='documents/%Y/%m/')),
                ('file_size', models.PositiveIntegerField(blank=True, null=True)),
                ('file_type', models.CharField(blank=True, max_length=50)),
                ('version', models.PositiveIntegerField(default=1)),
                ('is_final', models.BooleanField(default=False)),
                ('is_confidential', models.BooleanField(default=False)),
                ('tags', models.JSONField(blank=True, default=list)),
                ('date_signed', models.DateField(blank=True, null=True)),
                ('signatory', models.CharField(blank=True, max_length=200)),
                ('witness', models.CharField(blank=True, max_length=200)),
                ('is_shared_with_client', models.BooleanField(default=False)),
                ('client_access_expires', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('case', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='cases.case')),
            ],
            options={
                'verbose_name': 'Document',
                'verbose_name_plural': 'Documents',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='DocumentTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('template_type', models.CharField(choices=[('constitution_avocat', "Constitution d'avocat"), ('requete_introductive', 'Requête introductive'), ('conclusions', 'Conclusions'), ('memoire', 'Mémoire'), ('assignation', 'Assignation'), ('citation', 'Citation'), ('ordonnance', 'Ordonnance'), ('jugement', 'Jugement'), ('appel', 'Appel'), ('pourvoi', 'Pourvoi'), ('contrat', 'Contrat'), ('acte_notarie', 'Acte notarié'), ('attestation', 'Attestation'), ('lettre_mise_demeure', 'Lettre de mise en demeure'), ('rapport_expertise', "Rapport d'expertise"), ('proces_verbal', 'Procès-verbal')], max_length=50)),
                ('description', models.TextField(blank=True)),
                ('content_fr', models.TextField()),
                ('content_ar', models.TextField(blank=True)),
                ('variables', models.JSONField(default=list, help_text='List of variables that can be replaced in template')),
                ('is_active', models.BooleanField(default=True)),
                ('is_public', models.BooleanField(default=False)),
                ('category', models.CharField(blank=True, max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='document_templates', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Document Template',
                'verbose_name_plural': 'Document Templates',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='DocumentShare',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shared_with_email', models.EmailField(max_length=254)),
                ('access_level', models.CharField(choices=[('view', 'View only'), ('download', 'View and download'), ('edit', 'View, download and edit')], default='view', max_length=20)),
                ('access_token', models.CharField(max_length=100, unique=True)),
                ('expires_at', models.DateTimeField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('accessed_count', models.PositiveIntegerField(default=0)),
                ('last_accessed', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shares', to='documents.document')),
                ('shared_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Document Share',
                'verbose_name_plural': 'Document Shares',
            },
        ),
        migrations.AddField(
            model_name='document',
            name='template',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='documents.documenttemplate'),
        ),
        migrations.AddField(
            model_name='document',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='DocumentVersion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version_number', models.PositiveIntegerField()),
                ('content', models.TextField(blank=True)),
                ('file', models.FileField(blank=True, null=True, upload_to='document_versions/%Y/%m/')),
                ('change_notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='versions', to='documents.document')),
            ],
            options={
                'verbose_name': 'Document Version',
                'verbose_name_plural': 'Document Versions',
                'ordering': ['-version_number'],
                'unique_together': {('document', 'version_number')},
            },
        ),
    ]
