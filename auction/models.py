from django.db import models

# Create your models here.
class AddUriToArrayForm(models.Model):
    name = models.CharField('NFT Name', max_length=30)
    image = models.ImageField(upload_to="images/")

    def __str__(self):
        return self.name
    
class Auction(models.Model):
    itemName = models.CharField(max_length=200)
    bidder = models.CharField(max_length=200)
    bidPrice = models.DecimalField(max_digits=10, decimal_places=6)

    def __str__(self):
        return self.itemName
