from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.http import HttpResponse
from django.views.generic import CreateView, ListView
from transactions.constants import DEPOSIT, WITHDRAW,LOAN, LOAN_PAID,TRANSFER
from datetime import datetime
from django.db.models import Sum
from transactions.forms import (
    DepositeForm,
    WithdrawForm,
    LoanRequestForm,
)

from .models import Transactions, UserBankAccount
from .forms import TransferForm
from django.core.mail import EmailMessage,EmailMultiAlternatives
from django.template.loader import render_to_string




class TransactionCreateMixin( LoginRequiredMixin,CreateView):
    template_name='transactions/transaction_form.html'
    model=Transactions
    title=''
    success_url=reverse_lazy('transaction_report')

    def get_form_kwargs(self):#aitoko kora hoyeche karon form.py e account pop kora hoyechge oi opo account er data ai khane ane oi data niya kiso kaj kora hoice..jemon balance update ettadi.
        kwargs=super().get_form_kwargs()
        kwargs.update({
                'account':self.request.user.account
            })
           
        
        return kwargs
    def get_context_data(self,**kwargs):#aitoko title dekhabe
        context=super().get_context_data(**kwargs)
        context.update({
            'title':self.title
        })
        return context
class DepositMoneyView(TransactionCreateMixin):
    form_class = DepositeForm
    title = 'Deposit'

    def get_initial(self):
        initial = {'transaction_type': DEPOSIT}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
      
       
        account = self.request.user.account
        account.balance += amount # amount = 200, tar ager balance = 0 taka new balance = 0+200 = 200
        account.save(
            update_fields=[
                'balance'
            ]
        )

        messages.success(
            self.request,
            f'{"{:,.2f}".format(float(amount))}TK was deposited to your account successfully'
        )
        mail_subject="Deposite message"
        message=render_to_string('transactions/deposite_mail.html',{
            'user':self.request.user,
            'amount':amount,
            

        })
        to_email=self.request.user.email
        send_email=EmailMultiAlternatives(mail_subject,'',to=[to_email])
        send_email.attach_alternative(message,"text/html")
        send_email.send()


        return super().form_valid(form)
    # def form_invalid(self, form):
    #     print("Form is invalid")  
    #     print(form.errors)
    #     return super().form_invalid(form)    


class LoanRequestView(TransactionCreateMixin):
    form_class = LoanRequestForm
    title = 'Loan Request Form'

    def get_initial(self):
        initial = {'transaction_type':LOAN }
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account
        current_loan_count=Transactions.objects.filter(account=self.request.user.account,transaction_type=3,loan_approve=True).count()
        
       
        if current_loan_count>3:
            return HttpResponse("You Have Cross The Loan Limits")
       
        account.save(
            update_fields=[
                'balance'
            ]
        )

        messages.success(
            self.request,
            f'{"{:,.2f}".format(float(amount))}$ loan request is submited  successfully'
        )
        mail_subject="Loan Request Message"
        message=render_to_string('transactions/loan_request_mail.html',{
            'user':self.request.user,
            'amount':amount
        })
        to_email=self.request.user.email
        send_email=EmailMultiAlternatives(mail_subject,'',to=[to_email])
        send_email.attach_alternative(message,"text/html")
        send_email.send()

        return super().form_valid(form)




class WithdrawMoneyView(TransactionCreateMixin):
    form_class = WithdrawForm
    title = 'Withdeaw Money'

    def get_initial(self):
        initial = {'transaction_type':WITHDRAW}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account
        account.balance -= amount # amount = 200, tar ager balance = 0 taka new balance = 0+200 = 200
        account.save(
            update_fields=[
                'balance'
            ]
        )

        messages.success(
            self.request,
            f'{"{:,.2f}".format(float(amount))}TK was withdraw from your account successfully'
        )
        mail_subject="Withdraw Message"
        message=render_to_string('transactions/withdraw_mail.html',{
            'user':self.request.user,
            'amount':amount
        })
        to_email=self.request.user.email
        send_email=EmailMultiAlternatives(mail_subject,'',to=[to_email])
        send_email.attach_alternative(message,"text/html")
        send_email.send()

        return super().form_valid(form)

# class TransactionReportView(LoginRequiredMixin, ListView):
#     template_name = 'transactions/reansaction_report.html'
#     model = Transactions
#     balance = 0 # filter korar pore ba age amar total balance ke show korbe
    
#     def get_queryset(self):#acount gula filter kolrlam
#         queryset = super().get_queryset().filter(
#             account=self.request.user.account
#         )
#         start_date_str = self.request.GET.get('start_date')
#         end_date_str = self.request.GET.get('end_date')
        
#         if start_date_str and end_date_str:
#             start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()#date time string form theke datetime form e nilam
#             end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            
#             queryset = queryset.filter(timestamp__range=(start_date, end_date))
#             self.balance = Transactions.objects.filter(
#                 timestamp__date__range=(start_date, end_date)
#             ).aggregate(Sum('amount'))['amount__sum']
#         else:
#             self.balance = self.request.user.account.balance
       
#         return queryset.distinct() # unique queryset hote hobe
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context.update({
#             'account': self.request.user.account
#         })

#         return context
class TransactionReportView(LoginRequiredMixin, ListView):
    template_name = 'transactions/reansaction_report.html'  # Corrected template name
    model = Transactions
    balance = 0
    
    def get_queryset(self):
        queryset = super().get_queryset().filter(account=self.request.user.account)
        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')
        
        if start_date_str and end_date_str:
            try:
                # Parse dates from query parameters
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                
                # Create datetime objects for filtering
                start_datetime = datetime.combine(start_date, datetime.min.time())
                end_datetime = datetime.combine(end_date, datetime.max.time())
                
                queryset = queryset.filter(timestamp__range=(start_datetime, end_datetime))
                self.balance = Transactions.objects.filter(
                    timestamp__range=(start_datetime, end_datetime)
                ).aggregate(Sum('amount'))['amount__sum'] or 0
            except ValueError:
                # Handle invalid date format
                self.balance = self.request.user.account.balance
        else:
            self.balance = self.request.user.account.balance
        
        return queryset.distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'account': self.request.user.account,
            'balance': self.balance  # Add balance to context
        })
        return context

class PayLoanView(LoginRequiredMixin, View):
    def get(self, request, loan_id):
        loan = get_object_or_404(Transactions, id=loan_id)
        print(loan)
        if loan.loan_approve:
            user_account = loan.account
                # Reduce the loan amount from the user's balance
                # 5000, 500 + 5000 = 5500
                # balance = 3000, loan = 5000
            if loan.amount < user_account.balance:
                user_account.balance -= loan.amount
                loan.balance_after_transaction = user_account.balance
                user_account.save()
                loan.loan_approved = True
                loan.transaction_type = LOAN_PAID
                loan.save()
                mail_subject="Loan Pay"
                message=render_to_string('transactions/loan_pay_mail.html',{
                'user':self.request.user,
                'amount':loan.amount
                                        })
                to_email=self.request.user.email
                send_email=EmailMultiAlternatives(mail_subject,'',to=[to_email])
                send_email.attach_alternative(message,"text/html")
                send_email.send()
           
                return redirect('loan_list')
            else:
                messages.error(
                    self.request,
            f'Loan amount is greater than available balance'
        )
       

        return redirect('loan_list')


class LoanListView(LoginRequiredMixin,ListView):
    model = Transactions
    template_name = 'transactions/loan_request.html'
    context_object_name = 'loans' # loan list ta ei loans context er moddhe thakbe
    
    def get_queryset(self):
        user_account = self.request.user.account
        queryset = Transactions.objects.filter(account=user_account,transaction_type=LOAN)
        return queryset 


class TransferView(LoginRequiredMixin, CreateView):
    template_name = 'transactions/transfer.html'
    model = Transactions
    form_class = TransferForm
    success_url = reverse_lazy('transaction_report')
    title = 'Transfer'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'account': self.request.user.account
        })
        return kwargs

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        return context

    def get_initial(self):
        initial = {'transaction_type':TRANSFER }
        return initial
       
        

    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        amount = cleaned_data.get('amount')
        recipient_account_no = cleaned_data.get('recipient_account_no')
        sender_account = self.request.user.account

        try:
            recipient_account = UserBankAccount.objects.get(account_no=recipient_account_no)

            # Check if the sender has enough balance
            if sender_account.balance < amount:
                messages.error(self.request, 'Insufficient balance.')
                return self.form_invalid(form)
            else:
                # Update balances for both accounts
                sender_account.balance -= amount
                recipient_account.balance += amount
                sender_account.save()
                recipient_account.save()

                messages.success(self.request, 'Transfer successful!')
                return redirect('transaction_report')

        except UserBankAccount.DoesNotExist:
            messages.error(self.request, 'Recipient account not found.')
            return self.form_invalid(form)

        return super().form_valid(form)
