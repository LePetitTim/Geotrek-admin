# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2019-01-14 13:29
from __future__ import unicode_literals

from django.db import migrations


def remove_infrastructuretype_signage(apps, schema_editor):
    AttachmentModel = apps.get_model('common', 'Attachment')
    InfrastructureModel = apps.get_model('infrastructure', 'Infrastructure')
    SignageModel = apps.get_model('signage', 'Signage')
    ContentTypeModel = apps.get_model("contenttypes", "ContentType")
    attachments = AttachmentModel.objects.filter(content_type__model='baseinfrastructure')
    for attachment in attachments:
        if InfrastructureModel.objects.filter(id=attachment.object_id).exists():
            attachment.content_type = ContentTypeModel.objects.get(app_label='infrastructure', model='infrastructure')
        elif SignageModel.objects.filter(id=attachment.object_id).exists():
            attachment.content_type = ContentTypeModel.objects.get(app_label='signage', model='signage')
        attachment.save()


class Migration(migrations.Migration):

    dependencies = [
        ('infrastructure', '0012_remove_signagetype_rename_infrastructure_type'),
    ]

    operations = [
        migrations.RunPython(remove_infrastructuretype_signage),
    ]
