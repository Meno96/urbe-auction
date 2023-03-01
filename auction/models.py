from django.db import models

# Create your models here.
class AddUriToArrayForm(models.Model):
    name = models.CharField('NFT Name', max_length=30)
    image = models.ImageField(upload_to="images/")

    def __str__(self):
        return self.name
    
class EndAuction(models.Model):
    nftId = models.IntegerField(primary_key=True)
    winner = models.CharField(max_length=200)
    price = models.IntegerField()
    txHash = models.CharField(max_length=255, null=True)

    def __str__(self):
        return str(self.nftId)
    
# Class that attributes IP and login date
class IpAddress(models.Model):
    pubDate = models.DateTimeField('date published')
    ipAddress = models.GenericIPAddressField()

