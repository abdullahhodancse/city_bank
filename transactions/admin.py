from django.contrib import admin
from django.core.mail import EmailMessage,EmailMultiAlternatives
from django.template.loader import render_to_string

# from transactions.models import Transaction
from .models import Transactions
@admin.register(Transactions)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['account', 'amount', 'amount_after_transaction', 'transaction_type', 'loan_approve']
    
    def save_model(self, request, obj, form, change):
        obj.account.balance += obj.amount
        obj.balance_after_transaction = obj.account.balance
        obj.account.save()
        mail_subject="Loan Approval"
        message=render_to_string('transactions/admin_approval_mail.html',{
            'user':request.user,
            'amount':obj.amount,
            'new_balance':obj.account.balance,
            

        })
        to_email=request.user.email
        send_email=EmailMultiAlternatives(mail_subject,'',to=[to_email])
        send_email.attach_alternative(message,"text/html")
        send_email.send()



        super().save_model(request, obj, form, change)