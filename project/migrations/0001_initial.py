# Generated by Django 3.1.5 on 2021-04-17 07:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Pdf',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('author', models.CharField(max_length=100)),
                ('pdf', models.FileField(upload_to='pdfs/')),
            ],
        ),
        migrations.CreateModel(
            name='TraitTable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('verbatimScientificName', models.CharField(max_length=100, null=True)),
                ('verbatimTraitName', models.CharField(max_length=100)),
                ('verbatimTraitValue', models.CharField(max_length=100)),
                ('verbatimTraitUnit', models.CharField(max_length=100)),
                ('sex', models.CharField(max_length=100, null=True)),
                ('pdf_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project.pdf')),
            ],
        ),
    ]
