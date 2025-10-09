from django.db import models


class City(models.Model):
    id = models.BigAutoField(primary_key=True)
    country_id = models.IntegerField()
    name = models.CharField(max_length=150)
    lat = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    lng = models.DecimalField(max_digits=9, decimal_places=6, null=True)

    class Meta:
        managed = False
        db_table = 'cities'


class Destination(models.Model):
    id = models.BigAutoField(primary_key=True)
    city = models.ForeignKey(City, on_delete=models.DO_NOTHING, db_column='city_id')
    title = models.CharField(max_length=200)
    description = models.TextField(null=True)
    avg_price_level = models.SmallIntegerField(null=True)
    popularity_score = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    image_url = models.CharField(max_length=500, null=True)

    class Meta:
        managed = False
        db_table = 'destinations'


class Attraction(models.Model):
    id = models.BigAutoField(primary_key=True)
    city_id = models.BigIntegerField()
    category = models.CharField(max_length=80, null=True)

    class Meta:
        managed = False
        db_table = 'attractions'


class RoomOffer(models.Model):
    id = models.BigAutoField(primary_key=True)
    room_type_id = models.BigIntegerField()
    price_per_night = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3)
    available_from = models.DateField()
    available_to = models.DateField()

    class Meta:
        managed = False
        db_table = 'room_offers'


class UserPreference(models.Model):
    user_id = models.BigIntegerField(primary_key=True)
    currency = models.CharField(max_length=3)
    min_budget = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    max_budget = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    interests = models.JSONField(null=True)

    class Meta:
        managed = False
        db_table = 'user_preferences'
