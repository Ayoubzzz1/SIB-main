from django.contrib import admin
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.html import format_html
from django.urls import path
from .models import Message
from django.utils import timezone
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from io import BytesIO
# Enhanced Django Admin styling

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('message', 'id_expediteur', 'id_destinataire', 'statut_lu', 'cree_le', 'print_button')
    list_filter = ('statut_lu', 'cree_le', 'id_expediteur', 'id_destinataire')
    search_fields = ('message', 'id_expediteur__nom', 'id_destinataire__nom')
    readonly_fields = ('cree_le',)
    actions = ['print_selected', 'print_all']
    
    # Enhanced fieldsets
    fieldsets = (
        ('📧 Informations de base', {
            'fields': ('id_expediteur', 'id_destinataire'),
            'classes': ('wide', 'extrapretty'),
            'description': 'Expéditeur et destinataire du message'
        }),
        ('📝 Contenu', {
            'fields': ('message',),
            'classes': ('wide', 'extrapretty'),
            'description': 'Contenu du message'
        }),
        ('📊 Statut et informations', {
            'fields': ('statut_lu', 'cree_le'),
            'classes': ('wide', 'extrapretty'),
            'description': 'Statut de lecture et date de création'
        }),
    )
    
    # Enhanced list display
    list_display_links = ('message',)
    list_per_page = 25
    list_max_show_all = 100
    date_hierarchy = 'cree_le'
    
    # Enhanced search
    search_help_text = "Rechercher par message, expéditeur ou destinataire"
    
    # Enhanced list editable
    list_editable = ('statut_lu',)
    
    # Enhanced autocomplete
    autocomplete_fields = ['id_expediteur', 'id_destinataire']

    def print_button(self, obj):
        return format_html(
            '<a class="material-icons" href="{}" target="_blank" style="color: #2196F3; text-decoration: none;" title="Imprimer">print</a>',
            f'/admin/communication_app/message/{obj.id}/print/'
        )
    print_button.short_description = '🖨️ Imprimer'

    def print_selected(self, request, queryset):
        return self.generate_pdf_report(queryset, "Rapport des Messages Sélectionnés")
    print_selected.short_description = "🖨️ Imprimer les messages sélectionnés"

    def print_all(self, request, queryset):
        all_items = Message.objects.all().select_related('id_expediteur', 'id_destinataire')
        return self.generate_pdf_report(all_items, "Rapport Complet des Messages")
    print_all.short_description = "🖨️ Imprimer tous les messages"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_print_all'] = True
        extra_context['print_all_url'] = '/admin/communication_app/message/print_all/'
        return super().changelist_view(request, extra_context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:message_id>/print/', self.admin_site.admin_view(self.print_message_view), name='communication_app_message_print'),
            path('print_all/', self.admin_site.admin_view(self.print_all_view), name='communication_app_message_print_all'),
        ]
        return custom_urls + urls

    def print_message_view(self, request, message_id):
        try:
            message = Message.objects.get(id=message_id)
            return self.generate_pdf_report([message], f"Message - {message.message[:30]}...")
        except Message.DoesNotExist:
            return HttpResponse("Message non trouvé", status=404)

    def print_all_view(self, request):
        all_items = Message.objects.all().select_related('id_expediteur', 'id_destinataire')
        return self.generate_pdf_report(all_items, "Rapport Complet des Messages")

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
        
        data = [['Message', 'Expéditeur', 'Destinataire', 'Lu', 'Date Création']]
        for item in queryset:
            data.append([
                item.message[:50] + '...' if len(item.message) > 50 else item.message,
                item.id_expediteur.nom if item.id_expediteur else 'N/A',
                item.id_destinataire.nom if item.id_destinataire else 'N/A',
                'Oui' if item.statut_lu else 'Non',
                item.cree_le.strftime('%d/%m/%Y %H:%M') if item.cree_le else 'N/A'
            ])
        
        table = Table(data, colWidths=[2.5*inch, 1.2*inch, 1.2*inch, 0.6*inch, 1.2*inch])
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
