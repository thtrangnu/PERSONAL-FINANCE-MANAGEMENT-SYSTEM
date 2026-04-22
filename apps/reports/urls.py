from django.urls import path

from apps.reports import views


urlpatterns = [
    path('reports/', views.overview_summary, name='report_overview'),
    path('reports/monthly/', views.monthly_summary, name='report_monthly'),
    path('reports/yearly/', views.yearly_summary, name='report_yearly'),
    path('reports/categories/', views.category_expenses, name='report_categories'),
    path('reports/trends/', views.trend_report, name='report_trends'),
    path('reports/export/monthly.xlsx', views.export_monthly_excel, name='export_monthly_excel'),
    path('reports/export/overview.xlsx', views.export_overview_excel, name='export_overview_excel'),
    path('reports/export/yearly.xlsx', views.export_yearly_excel, name='export_yearly_excel'),
    path('reports/export/categories.xlsx', views.export_categories_excel, name='export_categories_excel'),
    path('reports/export/trends.xlsx', views.export_trends_excel, name='export_trends_excel'),
    path('reports/export/monthly.pdf', views.export_monthly_pdf, name='export_monthly_pdf'),
    path('reports/export/overview.pdf', views.export_overview_pdf, name='export_overview_pdf'),
    path('reports/export/yearly.pdf', views.export_yearly_pdf, name='export_yearly_pdf'),
    path('reports/export/categories.pdf', views.export_categories_pdf, name='export_categories_pdf'),
    path('reports/export/trends.pdf', views.export_trends_pdf, name='export_trends_pdf'),
    path('reports/export/expenses.xlsx', views.export_expense_history_excel, name='export_expense_history_excel'),
]
