from django.db import models
from accounts.models import UserBankAccount,User
from .constants import TRANSACTION_TYPE

# Create your models here.


class Transactions(models.Model):
    account=models.ForeignKey(UserBankAccount,related_name='transactions',on_delete=models.CASCADE)
    amount=models.DecimalField(decimal_places=2,max_digits=12)
    amount_after_transaction=models.DecimalField(decimal_places=2,max_digits=12)
    transaction_type=models.IntegerField(choices=TRANSACTION_TYPE,null=True)
    timestamp=models.DateField(auto_now_add=True)
   
    transfer_money=models.DecimalField(decimal_places=2,max_digits=12,default=0)
    loan_approve=models.BooleanField(default=False)
   

   



    class Meta:
        ordering=['timestamp']


