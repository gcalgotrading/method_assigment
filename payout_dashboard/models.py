from django.db import models

class Entity(models.Model):
    ENTITY_TYPES = (
        ('individual', 'Individual'),
        ('corporation', 'Corporation'),
    )

    entity_id = models.CharField(max_length=100, null=True)
    type = models.CharField(max_length=100, choices=ENTITY_TYPES)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    ein = models.CharField(max_length=100, blank=True, null=True)
    corporation_name = models.CharField(max_length=100, blank=True, null=True)
    dunkin_id = models.CharField(max_length=100, blank=True, null=True)

class Account(models.Model):
    account_id = models.CharField(max_length=255)
    holder_id = models.CharField(max_length=255)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    # Add other fields relevant to the account model

    def __str__(self):
        return self.account_id
    
class Payment(models.Model):
    source = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)