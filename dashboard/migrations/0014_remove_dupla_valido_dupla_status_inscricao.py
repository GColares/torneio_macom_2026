from django.db import migrations, models

def migrate_valido(apps, schema_editor):
    Dupla = apps.get_model('dashboard', 'Dupla')
    for d in Dupla.objects.all():
        if d.valido:
            d.status_inscricao = 'Validada'
        else:
            d.status_inscricao = 'Pendente'
        d.save()

class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0013_comprovante_fichainscricao_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='dupla',
            name='status_inscricao',
            field=models.CharField(choices=[('Pendente', 'Pendente'), ('Validada', 'Validada'), ('Inscrita', 'Inscrita'), ('Cancelada', 'Cancelada'), ('Teste', 'Teste'), ('Impugnada', 'Impugnada'), ('Eliminada', 'Eliminada')], default='Pendente', max_length=20, verbose_name='Status da Inscrição'),
        ),
        migrations.RunPython(migrate_valido),
        migrations.RemoveField(
            model_name='dupla',
            name='valido',
        ),
    ]
