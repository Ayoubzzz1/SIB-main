from django.contrib import admin
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.html import format_html
from django.urls import path
from .models import HistoriqueActivite
from django.utils import timezone
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from io import BytesIO
# Enhanced Django Admin styling

@admin.register(HistoriqueActivite)
class HistoriqueActiviteAdmin(admin.ModelAdmin):
    list_display = ('horodatage', 'action', 'id_utilisateur', 'get_modele', 'id_entite', 'details_apercu', 'print_button')
    list_filter = ('action', 'horodatage', 'id_utilisateur')
    search_fields = ('action', 'id_utilisateur__nom', 'details')
    readonly_fields = ('horodatage', 'id_utilisateur', 'action', 'content_type', 'id_entite', 'details')
    actions = ['print_selected', 'print_all']
    
    # Enhanced fieldsets
    fieldsets = (
        ('📊 Informations de base', {
            'fields': ('action', 'content_type', 'id_entite'),
            'classes': ('wide', 'extrapretty'),
            'description': 'Informations principales de l\'activité'
        }),
        ('👤 Utilisateur et timing', {
            'fields': ('id_utilisateur', 'horodatage'),
            'classes': ('wide', 'extrapretty'),
            'description': 'Utilisateur responsable et horodatage'
        }),
        ('📝 Contenu de l\'activité', {
            'fields': ('details',),
            'classes': ('wide', 'extrapretty'),
            'description': 'Détails de l\'activité'
        }),
    )
    
    # Enhanced list display
    list_display_links = ('horodatage',)
    list_per_page = 25
    list_max_show_all = 100
    date_hierarchy = 'horodatage'
    
    # Enhanced search
    search_help_text = "Rechercher par action, utilisateur ou détails"
    
    # Enhanced autocomplete
    autocomplete_fields = ['id_utilisateur']

    def get_modele(self, obj):
        return obj.content_type.model if obj.content_type else 'N/A'
    get_modele.short_description = 'Modèle'

    def details_apercu(self, obj):
        if obj.details:
            return obj.details[:50] + '...' if len(obj.details) > 50 else obj.details
        return 'N/A'
    details_apercu.short_description = 'Détails (aperçu)'

    def print_button(self, obj):
        return format_html(
            '<a class="button" href="{}" target="_blank" style="background-color: #2196F3; color: white; padding: 5px 10px; border-radius: 4px; text-decoration: none;" title="Imprimer">🖨️ Imprimer</a>',
            f'/admin/logs_app/historiqueactivite/{obj.id}/print/'
        )
    print_button.short_description = '🖨️ Imprimer'

    def print_selected(self, request, queryset):
        return self.generate_pdf_report(queryset, "Rapport des Activités Sélectionnées")
    print_selected.short_description = "🖨️ Imprimer les activités sélectionnées"

    def print_all(self, request, queryset):
        all_items = HistoriqueActivite.objects.all().select_related('id_utilisateur')
        return self.generate_pdf_report(all_items, "Rapport Complet des Activités")
    print_all.short_description = "🖨️ Imprimer tous les logs"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_print_all'] = True
        extra_context['print_all_url'] = '/admin/logs_app/historiqueactivite/print_all/'
        return super().changelist_view(request, extra_context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:activite_id>/print/', self.admin_site.admin_view(self.print_activite_view), name='logs_app_historiqueactivite_print'),
            path('print_all/', self.admin_site.admin_view(self.print_all_view), name='logs_app_historiqueactivite_print_all'),
        ]
        return custom_urls + urls

    def print_activite_view(self, request, activite_id):
        try:
            activite = HistoriqueActivite.objects.get(id=activite_id)
            return self.generate_pdf_report([activite], f"Activité - {activite.action}")
        except HistoriqueActivite.DoesNotExist:
            return HttpResponse("Activité non trouvée", status=404)

    def print_all_view(self, request):
        all_items = HistoriqueActivite.objects.all().select_related('id_utilisateur')
        return self.generate_pdf_report(all_items, "Rapport Complet des Activités")

    def generate_pdf_report(self, queryset, title):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=16, spaceAfter=30, alignment=1)
        date_style = ParagraphStyle('DateStyle', parent=styles['Normal'], fontSize=10, alignment=1)
        
        elements.append(Paragraph(title, title_style))
        elements.append(Spacer(1, 20))
        elements.append(Paragraph(f"Généré le: {timezone.now().strftime('%d/%m/%Y %H:%M')}", date_style))
        elements.append(Spacer(1, 20))
        
        data = [['Horodatage', 'Utilisateur', 'Action', 'Modèle', 'ID Entité', 'Détails']]
        for item in queryset:
            data.append([
                item.horodatage.strftime('%d/%m/%Y %H:%M:%S') if item.horodatage else 'N/A',
                item.id_utilisateur.nom if item.id_utilisateur else 'N/A',
                item.action,
                item.content_type.model if item.content_type else 'N/A',
                str(item.id_entite) if item.id_entite else 'N/A',
                item.details[:40] + '...' if item.details and len(item.details) > 40 else (item.details or 'N/A')
            ])
        
        table = Table(data, colWidths=[1.5*inch, 1.2*inch, 1*inch, 1*inch, 0.8*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey), ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10), ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige), ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        footer_style = ParagraphStyle('FooterStyle', parent=styles['Normal'], fontSize=8, alignment=1, textColor=colors.grey)
        elements.append(Paragraph("SIB - Système d'Inventaire et de Bilan", footer_style))
        elements.append(Paragraph("Page générée automatiquement", footer_style))
        
        doc.build(elements)
        pdf = buffer.getvalue()
        buffer.close()
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{title.lower().replace(" ", "_")}.pdf"'
        response.write(pdf)
        return response
