# Generated by Django 3.1.1 on 2020-09-01 17:36

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Arret',
            fields=[
                ('identifiant', models.SlugField(primary_key=True, serialize=False)),
                ('date', models.CharField(max_length=20)),
                ('juridiction', models.CharField(max_length=200)),
                ('page', models.IntegerField()),
                ('contenu', models.TextField()),
                ('selected', models.BooleanField(default=False)),
                ('image', models.URLField()),
            ],
        ),
        migrations.CreateModel(
            name='Receuil',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(blank=True, max_length=150, null=True)),
                ('arrets', models.ManyToManyField(to='main_app.Arret')),
            ],
        ),
    ]
