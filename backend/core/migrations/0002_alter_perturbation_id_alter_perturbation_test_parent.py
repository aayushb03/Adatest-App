# Generated by Django 4.2.10 on 2024-04-22 22:01

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='perturbation',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='perturbation',
            name='test_parent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.test'),
        ),
    ]
