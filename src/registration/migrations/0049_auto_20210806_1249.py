# Generated by Django 3.2.6 on 2021-08-06 10:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0048_rename_ask_vegetarian_event_ask_nutrition'),
    ]

    operations = [
        migrations.AddField(
            model_name='helper',
            name='nutrition',
            field=models.CharField(choices=[('NO_PREFERENCE', 'No preference'), ('VEGETARIAN', 'Vegetarian'), ('VEGAN', 'Vegan'), ('OTHER', 'Other (please specify in comment)')], default='NO_PREFERENCE', help_text='This helps us estimating the food for our helpers.', max_length=20, verbose_name='Nutrition'),
        ),
        migrations.AlterField(
            model_name='event',
            name='ask_nutrition',
            field=models.BooleanField(default=True, verbose_name='Ask for nutrition'),
        ),
    ]