from django.contrib import admin
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.html import format_html
from django.urls import path
from .models import Production, NomenclatureProduits
from django.utils import timezone
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from io import BytesIO
# Enhanced Django Admin styling

@admin.register(Production)
class ProductionAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_produit_nom', 'quantite_prevue', 'quantite_produite', 'date_debut', 'statut', 'cree_par', 'print_button')
    list_filter = ('statut', 'date_debut', 'date_fin', 'cree_par')
    search_fields = ('produit_semi_fini__nom', 'produit_fini__nom', 'cree_par__nom')
    readonly_fields = ('cree_le', 'cree_par')
    actions = ['print_selected', 'print_all']
    
    # Enhanced fieldsets
    fieldsets = (
        ('🏭 Informations de base', {
            'fields': ('produit_semi_fini', 'produit_fini', 'quantite_prevue'),
            'classes': ('wide', 'extrapretty'),
            'description': 'Informations principales de la production'
        }),
        ('📊 Progression et statut', {
            'fields': ('quantite_produite', 'statut', 'date_debut', 'date_fin'),
            'classes': ('wide', 'extrapretty'),
            'description': 'Suivi de la production et dates'
        }),
        ('👤 Responsabilité', {
            'fields': ('cree_par', 'cree_le'),
            'classes': ('wide', 'extrapretty'),
            'description': 'Responsable et date de création'
        }),
    )
    
    # Enhanced list display
    list_display_links = ('id',)
    list_per_page = 25
    list_max_show_all = 100
    date_hierarchy = 'date_debut'
    
    # Enhanced search
    search_help_text = "Rechercher par nom du produit ou créateur"
    
    # Enhanced autocomplete
    autocomplete_fields = ['produit_semi_fini', 'produit_fini', 'cree_par']

    def get_produit_nom(self, obj):
        if obj.produit_semi_fini:
            return obj.produit_semi_fini.nom
        elif obj.produit_fini:
            return obj.produit_fini.nom
        return 'N/A'
    get_produit_nom.short_description = 'Produit'

    def print_button(self, obj):
        return format_html(
            '<a class="material-icons" href="{}" target="_blank" style="color: #2196F3; text-decoration: none;" title="Imprimer">print</a>',
            f'/admin/production_app/production/{obj.id}/print/'
        )
    print_button.short_description = '🖨️ Imprimer'

    def print_selected(self, request, queryset):
        return self.generate_pdf_report(queryset, "Rapport des Productions Sélectionnées")
    print_selected.short_description = "🖨️ Imprimer les productions sélectionnées"

    def print_all(self, request, queryset):
        all_items = Production.objects.all().select_related('produit_semi_fini', 'produit_fini', 'cree_par')
        return self.generate_pdf_report(all_items, "Rapport Complet des Productions")
    print_all.short_description = "🖨️ Imprimer toutes les productions"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_print_all'] = True
        extra_context['print_all_url'] = '/admin/production_app/production/print_all/'
        return super().changelist_view(request, extra_context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:production_id>/print/', self.admin_site.admin_view(self.print_production_view), name='production_app_production_print'),
            path('print_all/', self.admin_site.admin_view(self.print_all_view), name='production_app_production_print_all'),
        ]
        return custom_urls + urls

    def print_production_view(self, request, production_id):
        try:
            production = Production.objects.get(id=production_id)
            return self.generate_pdf_report([production], f"Production - {production.get_produit_nom()}")
        except Production.DoesNotExist:
            return HttpResponse("Production non trouvée", status=404)

    def print_all_view(self, request):
        all_items = Production.objects.all().select_related('produit_semi_fini', 'produit_fini', 'cree_par')
        return self.generate_pdf_report(all_items, "Rapport Complet des Productions")

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
        
        data = [['ID', 'Produit', 'Qte Prévue', 'Qte Produite', 'Statut', 'Date Début', 'Créé par']]
        for item in queryset:
            data.append([
                str(item.id), 
                item.get_produit_nom(),
                str(item.quantite_prevue),
                str(item.quantite_produite),
                item.get_statut_display(),
                item.date_debut.strftime('%d/%m/%Y') if item.date_debut else 'N/A',
                item.cree_par.nom if item.cree_par else 'N/A'
            ])
        
        table = Table(data, colWidths=[1.2*inch, 1.5*inch, 1*inch, 1*inch, 1*inch, 1*inch, 1.2*inch])
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

@admin.register(NomenclatureProduits)
class NomenclatureProduitsAdmin(admin.ModelAdmin):
    list_display = ('get_produit_parent', 'get_composant', 'quantite_requise', 'unite', 'print_button')
    list_filter = ('type_produit_parent', 'type_composant')
    search_fields = ('content_type_parent__model', 'content_type_composant__model')
    actions = ['print_selected', 'print_all']
    
    # Enhanced fieldsets
    fieldsets = (
        ('🏭 Produit parent', {
            'fields': ('content_type_parent', 'id_produit_parent', 'type_produit_parent'),
            'classes': ('wide', 'extrapretty'),
            'description': 'Produit parent de la nomenclature'
        }),
        ('📦 Composant', {
            'fields': ('content_type_composant', 'id_composant', 'type_composant', 'quantite_requise', 'unite'),
            'classes': ('wide', 'extrapretty'),
            'description': 'Composant et quantité requise'
        }),
    )
    
    # Enhanced list display
    list_display_links = ('get_produit_parent',)
    list_per_page = 25
    list_max_show_all = 100
    
    # Enhanced search
    search_help_text = "Rechercher par type de produit parent ou composant"
    
    # Enhanced autocomplete
    autocomplete_fields = []

    def get_produit_parent(self, obj):
        return f"{obj.type_produit_parent} - {obj.produit_parent}"
    get_produit_parent.short_description = 'Produit Parent'

    def get_composant(self, obj):
        return f"{obj.type_composant} - {obj.composant}"
    get_composant.short_description = 'Composant'

    def print_button(self, obj):
        return format_html(
            '<a class="material-icons" href="{}" target="_blank" style="color: #2196F3; text-decoration: none;" title="Imprimer">print</a>',
            f'/admin/production_app/nomenclatureproduits/{obj.id}/print/'
        )
    print_button.short_description = '🖨️ Imprimer'

    def print_selected(self, request, queryset):
        return self.generate_pdf_report(queryset, "Rapport des Nomenclatures Sélectionnées")
    print_selected.short_description = "🖨️ Imprimer les nomenclatures sélectionnées"

    def print_all(self, request, queryset):
        all_items = NomenclatureProduits.objects.all().select_related('content_type_parent', 'content_type_composant')
        return self.generate_pdf_report(all_items, "Rapport Complet des Nomenclatures")
    print_all.short_description = "🖨️ Imprimer toutes les nomenclatures"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_print_all'] = True
        extra_context['print_all_url'] = '/admin/production_app/nomenclatureproduits/print_all/'
        return super().changelist_view(request, extra_context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:nomenclature_id>/print/', self.admin_site.admin_view(self.print_nomenclature_view), name='production_app_nomenclatureproduits_print'),
            path('print_all/', self.admin_site.admin_view(self.print_all_view), name='production_app_nomenclatureproduits_print_all'),
        ]
        return custom_urls + urls

    def print_nomenclature_view(self, request, nomenclature_id):
        try:
            nomenclature = NomenclatureProduits.objects.get(id=nomenclature_id)
            return self.generate_pdf_report([nomenclature], f"Nomenclature - {nomenclature.produit_final}")
        except NomenclatureProduits.DoesNotExist:
            return HttpResponse("Nomenclature non trouvée", status=404)

    def print_all_view(self, request):
        all_items = NomenclatureProduits.objects.all().select_related('produit_final', 'matiere_premiere')
        return self.generate_pdf_report(all_items, "Rapport Complet des Nomenclatures")

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
        
        data = [['Produit Final', 'Matière Première', 'Quantité Requise', 'Unité']]
        for item in queryset:
            data.append([
                str(item.produit_final) if item.produit_final else 'N/A',
                str(item.matiere_premiere) if item.matiere_premiere else 'N/A',
                str(item.quantite_requise),
                item.unite or 'N/A'
            ])
        
        table = Table(data, colWidths=[2*inch, 2*inch, 1.2*inch, 1*inch])
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
