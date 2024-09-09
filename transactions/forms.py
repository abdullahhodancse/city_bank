from django import forms
from .models import Transactions
from accounts.models import UserBankAccount

class TransactionForm(forms.ModelForm):
    class Meta:
        model=Transactions
        fields=['amount','transaction_type']
        #amara transaction type ta user k dekhte dibo na tai nicher code gula likhchi
    def __init__(self,*args,**kwargs):
            self.account=kwargs.pop('account') 
            #aita korle account k bar bar check kora lagbe na j login kina...karon ai form onek deposit,withdraw,loan sob jaigai use hobe
            super().__init__(*args,**kwargs)
            self.fields['transaction_type'].disabled=True
            self.fields['transaction_type'].widget=forms.HiddenInput()   

    def save(self,commit=True):
            self.instance.account=self.account  
            self.instance.amount_after_transaction=self.account.balance
            return super().save()    
        

class DepositeForm(TransactionForm):
    def clean_amount(self):#form er kono field jodi bar bar change hoi tahole aita use kora lagbe
        min_deposite_amount=100
        amount=self.cleaned_data.get('amount')  #form e user jei amount dicilo oita ai khane read korlam

        if amount<min_deposite_amount:
            raise forms.ValidationError(
                f'You need to deposite minimun{min_deposite_amount}TK'
            )
        return amount
class WithdrawForm(TransactionForm):
    def clean_amount(self):
        min_withdraw_amount=500
        max_withdraw_amount=50000
        account=self.account
        balance=account.balance
        amount=self.cleaned_data.get('amount')

        if amount<min_withdraw_amount:
            raise forms.ValidationError(
                f'You need to withdraw at least{min_withdraw_amount}TK'
            )
        
        if amount>max_withdraw_amount:
            raise forms.ValidationError(
                f'You need to withdraw at most{max_withdraw_amount}TK'
            )
        
        if amount>balance:
            raise forms.ValidationError(
                f'Insufficient Balance'
            )
        return amount
class LoanRequestForm(TransactionForm):
    def clean_amount(self):
        amount=self.cleaned_data.get('amount')
        return amount




class TransferForm(forms.ModelForm):
    recipient_account_no = forms.CharField(label='Recipient Account No')

    class Meta:
        model = Transactions
        fields = ['amount', 'transaction_type']  # No account_no here

    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account') 
        super().__init__(*args, **kwargs)
        self.fields['transaction_type'].disabled = True
        self.fields['transaction_type'].widget = forms.HiddenInput()

    def save(self, commit=True):
        self.instance.account = self.account  
        self.instance.amount_after_transaction = self.account.balance
        return super().save()

    def clean(self):
        cleaned_data = super().clean()
        recipient_account_no = cleaned_data.get('recipient_account_no')
        amount = cleaned_data.get('amount')

        if amount <= 50:
            raise forms.ValidationError('Amount must be greater than 50.')

        # Check if recipient account exists
        if not UserBankAccount.objects.filter(account_no=recipient_account_no).exists():
            raise forms.ValidationError('Recipient account does not exist.')
