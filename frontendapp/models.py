from django.db import models


# system modelw ith onboadring_systems as table in db.
class onboarding_system(models.Model):
    OAR_Id = models.CharField(max_length=20, blank=False, null=False, unique=True)
    Usecase_Id = models.CharField(max_length=20, blank=False, null=False)
    Usecase_Owner = models.CharField(max_length=100, blank=False, null=True)
    Oar_Status = models.CharField(max_length=50, blank=False, null=True)
    Grid_Owner = models.CharField(max_length=100, blank=False, null=True)
    Product_Owner = models.CharField(max_length=100, blank=False, null=True)
    Dedicated_Contact = models.CharField(max_length=100, blank=True, null=True)
    is_Golden_Source = models.BooleanField(blank=False, null=True)
    Is_Data_Sending_to_DIAL = models.BooleanField(blank=False, null=True)

    class Meta:
        db_table = "onboarding_systems"

    def __str__(self) -> str:
        return self.OAR_Id


# application modelw ith onboadring_applications as table in db.
class onboarding_applications(models.Model):
    Services = models.CharField(max_length=50, blank=False, null=False)
    Solution_Intent_Link = models.CharField(max_length=50, blank=False, null=False)
    Getting_Data_From_OAR = models.CharField(max_length=50, blank=False, null=False)
    Sending_Data_To_OAR = models.CharField(max_length=50, blank=False, null=False)
    Environment = models.CharField(max_length=50, blank=False, null=False)
    Data_Hop_Layers = models.CharField(max_length=50, blank=False, null=False)
    #Final_Data_Zone = models.CharField(max_length=50, blank=False, null=False)
    Target_Completion_Sprint = models.DateField(max_length=50, blank=False, null=False)

    class Meta:
        db_table = "onboarding_application"

    def __str__(self) -> str:
        return self.Services
