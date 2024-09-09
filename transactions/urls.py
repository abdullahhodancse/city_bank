from django.urls import path  
from .views import  DepositMoneyView,LoanRequestView,WithdrawMoneyView,TransactionReportView,PayLoanView,LoanListView,TransferView

urlpatterns=[
    path('deposit/',DepositMoneyView.as_view(),name='deposit_money'),
    path('loan_request/',LoanRequestView.as_view(),name='loan_money_request'),
    path('withdraw/',WithdrawMoneyView.as_view(),name='withdraw_money'),
    path('transaction/',TransactionReportView.as_view(),name='transaction_report'),
    path('loanpay/<int:loan_id>',PayLoanView.as_view(),name='loanpay'),
    path('loan_lost/',LoanListView.as_view(),name='loan_list'),
    path('loan_lost/',LoanListView.as_view(),name='loan_list'),
    path('transfer_money/',TransferView.as_view(),name='transfer_money'),

]
