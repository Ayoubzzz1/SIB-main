from django.contrib import admin
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.html import format_html
from django.urls import path
from .models import Client, Commande, ArticleCommande, Fournisseur
from django.utils import timezone
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from io import BytesIO
# Enhanced Django Admin styling

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('nom_entreprise', 'personne_contact', 'telephone', 'email', 'adresse', 'cree_le', 'print_button')
    list_filter = ('cree_le',)
    search_fields = ('nom_entreprise', 'personne_contact', 'email', 'telephone')
    readonly_fields = ('cree_le',)
    actions = ['print_selected', 'print_all']
    
    # Enhanced fieldsets
    fieldsets = (
        ('🏢 Informations de base', {
            'fields': ('nom_entreprise', 'personne_contact', 'telephone', 'email'),
            'classes': ('wide', 'extrapretty'),
            'description': 'Informations principales du client'
        }),
        ('📍 Adresse', {
            'fields': ('adresse',),
            'classes': ('wide', 'extrapretty'),
            'description': 'Adresse complète du client'
        }),
        ('📊 Informations système', {
            'fields': ('cree_le',),
            'classes': ('wide', 'extrapretty'),
            'description': 'Informations de création'
        }),
    )
    
    # Enhanced list display
    list_display_links = ('nom_entreprise',)
    list_per_page = 25
    list_max_show_all = 100
    date_hierarchy = 'cree_le'
    
    # Enhanced search
    search_help_text = "Rechercher par nom d'entreprise, personne de contact, email ou téléphone"

    def print_button(self, obj):
        return format_html(
            '<a class="material-icons" href="{}" target="_blank" style="color: #2196F3; text-decoration: none;" title="Imprimer">print</a>',
            f'/admin/sales_app/client/{obj.id}/print/'
        )
    print_button.short_description = '🖨️ Imprimer'

    def print_selected(self, request, queryset):
        return self.generate_pdf_report(queryset, "Rapport des Clients Sélectionnés")
    print_selected.short_description = "🖨️ Imprimer les clients sélectionnés"

    def print_all(self, request, queryset):
        all_items = Client.objects.all()
        return self.generate_pdf_report(all_items, "Rapport Complet des Clients")
    print_all.short_description = "🖨️ Imprimer tous les clients"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_print_all'] = True
        extra_context['print_all_url'] = '/admin/sales_app/client/print_all/'
        return super().changelist_view(request, extra_context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:client_id>/print/', self.admin_site.admin_view(self.print_client_view), name='sales_app_client_print'),
            path('print_all/', self.admin_site.admin_view(self.print_all_view), name='sales_app_client_print_all'),
        ]
        return custom_urls + urls

    def print_client_view(self, request, client_id):
        try:
            client = Client.objects.get(id=client_id)
            return self.generate_pdf_report([client], f"Client - {client.nom_entreprise}")
        except Client.DoesNotExist:
            return HttpResponse("Client non trouvé", status=404)

    def print_all_view(self, request):
        all_items = Client.objects.all()
        return self.generate_pdf_report(all_items, "Rapport Complet des Clients")

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
        
        data = [['Entreprise', 'Personne Contact', 'Téléphone', 'Email', 'Adresse', 'Créé le']]
        for item in queryset:
            data.append([
                item.nom_entreprise, item.personne_contact or 'N/A', item.telephone or 'N/A', item.email or 'N/A',
                item.adresse or 'N/A',
                item.cree_le.strftime('%d/%m/%Y %H:%M') if item.cree_le else 'N/A'
            ])
        
        table = Table(data, colWidths=[1.5*inch, 1.2*inch, 1*inch, 1.5*inch, 2*inch, 1*inch])
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

@admin.register(Fournisseur)
class FournisseurAdmin(admin.ModelAdmin):
    list_display = ('nom_entreprise', 'code_fournisseur', 'personne_contact', 'telephone', 'email', 'est_actif', 'cree_le', 'print_button')
    list_filter = ('est_actif', 'cree_le')
    search_fields = ('nom_entreprise', 'code_fournisseur', 'email', 'telephone')
    readonly_fields = ('cree_le',)
    actions = ['print_selected', 'print_all']
    
    # Enhanced fieldsets
    fieldsets = (
        ('🏭 Informations de base', {
            'fields': ('nom_entreprise', 'code_fournisseur', 'personne_contact', 'telephone', 'email'),
            'classes': ('wide', 'extrapretty'),
            'description': 'Informations principales du fournisseur'
        }),
        ('📍 Adresse', {
            'fields': ('adresse',),
            'classes': ('wide', 'extrapretty'),
            'description': 'Adresse complète du fournisseur'
        }),
        ('📊 Statut et informations', {
            'fields': ('est_actif', 'cree_le'),
            'classes': ('wide', 'extrapretty'),
            'description': 'Statut du fournisseur et informations de création'
        }),
    )
    
    # Material Admin specific list display
    list_display_links = ('nom_entreprise', 'code_fournisseur')
    list_per_page = 25
    list_max_show_all = 100
    date_hierarchy = 'cree_le'
    
    # Material Admin specific search
    search_help_text = "Rechercher par nom d'entreprise, code fournisseur, email ou téléphone"
    
    # Material Admin specific list editable
    list_editable = ('est_actif',)

    def print_button(self, obj):
        return format_html(
            '<a class="material-icons" href="{}" target="_blank" style="color: #2196F3; text-decoration: none;" title="Imprimer">print</a>',
            f'/admin/sales_app/fournisseur/{obj.id}/print/'
        )
    print_button.short_description = '🖨️ Imprimer'

    def print_selected(self, request, queryset):
        return self.generate_pdf_report(queryset, "Rapport des Fournisseurs Sélectionnés")
    print_selected.short_description = "🖨️ Imprimer les fournisseurs sélectionnés"

    def print_all(self, request, queryset):
        all_items = Fournisseur.objects.all()
        return self.generate_pdf_report(all_items, "Rapport Complet des Fournisseurs")
    print_all.short_description = "🖨️ Imprimer tous les fournisseurs"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_print_all'] = True
        extra_context['print_all_url'] = '/admin/sales_app/fournisseur/print_all/'
        return super().changelist_view(request, extra_context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:fournisseur_id>/print/', self.admin_site.admin_view(self.print_fournisseur_view), name='sales_app_fournisseur_print'),
            path('print_all/', self.admin_site.admin_view(self.print_all_view), name='sales_app_fournisseur_print_all'),
        ]
        return custom_urls + urls

    def print_fournisseur_view(self, request, fournisseur_id):
        try:
            fournisseur = Fournisseur.objects.get(id=fournisseur_id)
            return self.generate_pdf_report([fournisseur], f"Fournisseur - {fournisseur.nom_entreprise}")
        except Fournisseur.DoesNotExist:
            return HttpResponse("Fournisseur non trouvé", status=404)

    def print_all_view(self, request):
        all_items = Fournisseur.objects.all()
        return self.generate_pdf_report(all_items, "Rapport Complet des Fournisseurs")

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
        
        data = [['Entreprise', 'Code Fournisseur', 'Téléphone', 'Email', 'Ville', 'Pays', 'Actif', 'Créé le']]
        for item in queryset:
            data.append([
                item.nom_entreprise, item.code_fournisseur, item.telephone or 'N/A', item.email or 'N/A',
                item.ville or 'N/A', item.pays or 'N/A', 'Oui' if item.est_actif else 'Non',
                item.cree_le.strftime('%d/%m/%Y %H:%M') if item.cree_le else 'N/A'
            ])
        
        table = Table(data, colWidths=[1.5*inch, 1.2*inch, 1*inch, 1.5*inch, 1*inch, 0.8*inch, 0.6*inch, 1*inch])
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

class ArticleCommandeInline(admin.TabularInline):
    model = ArticleCommande
    extra = 1
    fields = ('id_produit', 'quantite', 'prix_unitaire')
    
    # Enhanced styling
    classes = ('wide', 'extrapretty')
    verbose_name = "Article de commande"
    verbose_name_plural = "Articles de commande"

@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_client', 'date_commande', 'statut', 'get_total_commande', 'print_button')
    list_filter = ('statut', 'date_commande', 'id_client')
    search_fields = ('id', 'id_client__nom_entreprise')
    readonly_fields = ('cree_le',)
    actions = ['print_selected', 'print_all']
    inlines = [ArticleCommandeInline]
    
    # Enhanced fieldsets
    fieldsets = (
        ('📋 Informations de base', {
            'fields': ('id_client', 'statut'),
            'classes': ('wide', 'extrapretty'),
            'description': 'Informations principales de la commande'
        }),
        ('📅 Dates et informations', {
            'fields': ('date_commande', 'date_livraison', 'cree_par'),
            'classes': ('wide', 'extrapretty'),
            'description': 'Dates et responsable de la commande'
        }),
        ('📊 Informations système', {
            'fields': ('cree_le',),
            'classes': ('wide', 'extrapretty'),
            'description': 'Informations de création'
        }),
    )
    
    # Enhanced list display
    list_display_links = ('id',)
    list_per_page = 25
    list_max_show_all = 100
    date_hierarchy = 'date_commande'
    
    # Enhanced search
    search_help_text = "Rechercher par ID ou nom du client"
    
    # Material Admin specific autocomplete
    autocomplete_fields = ['id_client', 'cree_par']

    def get_total_commande(self, obj):
        total = sum(item.quantite * item.prix_unitaire for item in obj.articles.all())
        return f"{total:.2f} €"
    get_total_commande.short_description = 'Total Commande'

    def print_button(self, obj):
        return format_html(
            '<a class="material-icons" href="{}" target="_blank" style="color: #2196F3; text-decoration: none;" title="Imprimer">print</a>',
            f'/admin/sales_app/commande/{obj.id}/print/'
        )
    print_button.short_description = '🖨️ Imprimer'

    def print_selected(self, request, queryset):
        return self.generate_pdf_report(queryset, "Rapport des Commandes Sélectionnées")
    print_selected.short_description = "🖨️ Imprimer les commandes sélectionnées"

    def print_all(self, request, queryset):
        all_items = Commande.objects.all().select_related('id_client').prefetch_related('articles')
        return self.generate_pdf_report(all_items, "Rapport Complet des Commandes")
    print_all.short_description = "🖨️ Imprimer toutes les commandes"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_print_all'] = True
        extra_context['print_all_url'] = '/admin/sales_app/commande/print_all/'
        return super().changelist_view(request, extra_context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:commande_id>/print/', self.admin_site.admin_view(self.print_commande_view), name='sales_app_commande_print'),
            path('print_all/', self.admin_site.admin_view(self.print_all_view), name='sales_app_commande_print_all'),
        ]
        return custom_urls + urls

    def print_commande_view(self, request, commande_id):
        try:
            commande = Commande.objects.get(id=commande_id)
            return self.generate_pdf_report([commande], f"Commande - {commande.id}")
        except Commande.DoesNotExist:
            return HttpResponse("Commande non trouvée", status=404)

    def print_all_view(self, request):
        all_items = Commande.objects.all().select_related('id_client').prefetch_related('articles')
        return self.generate_pdf_report(all_items, "Rapport Complet des Commandes")

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
        
        data = [['N° Commande', 'Client', 'Date Commande', 'Statut', 'Total', 'Articles']]
        grand_total = 0
        for item in queryset:
            articles_count = item.articles.count()
            total_commande = sum(a.quantite * a.prix_unitaire for a in item.articles.all()) if articles_count else 0
            grand_total += total_commande
            data.append([
                str(item.id),
                item.id_client.nom_entreprise if item.id_client else 'N/A',
                item.date_commande.strftime('%d/%m/%Y') if item.date_commande else 'N/A',
                item.get_statut_display(),
                f"{total_commande:.2f} €",
                str(articles_count)
            ])
        # Append a grand total row
        data.append(['', '', '', 'Total général', f"{grand_total:.2f} €", ''])
        
        table = Table(data, colWidths=[1.2*inch, 2*inch, 1.2*inch, 1*inch, 1*inch, 0.8*inch])
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

    def save_model(self, request, obj, form, change):
        # Ensure required defaults
        if not obj.date_commande:
            obj.date_commande = timezone.now().date()
        if not obj.cree_par and hasattr(request.user, 'utilisateur'):
            obj.cree_par = request.user.utilisateur
        super().save_model(request, obj, form, change)

@admin.register(ArticleCommande)
class ArticleCommandeAdmin(admin.ModelAdmin):
    list_display = ('id_commande', 'id_produit', 'quantite', 'prix_unitaire', 'get_total', 'print_button')
    list_filter = ('id_commande__statut', 'id_commande__date_commande')
    search_fields = ('id_commande__id', 'id_produit__nom')
    readonly_fields = ('get_total',)
    actions = ['print_selected', 'print_all']
    
    # Enhanced fieldsets
    fieldsets = (
        ('📋 Informations de base', {
            'fields': ('id_commande', 'id_produit'),
            'classes': ('wide', 'extrapretty'),
            'description': 'Informations principales de l\'article'
        }),
        ('📊 Quantités et prix', {
            'fields': ('quantite', 'prix_unitaire'),
            'classes': ('wide', 'extrapretty'),
            'description': 'Quantité et prix unitaire'
        }),
    )
    
    # Enhanced list display
    list_display_links = ('id_commande',)
    list_per_page = 25
    list_max_show_all = 100
    
    # Enhanced search
    search_help_text = "Rechercher par ID de commande ou nom du produit"
    
    # Enhanced autocomplete
    autocomplete_fields = ['id_commande', 'id_produit']

    def get_total(self, obj):
        return f"{obj.quantite * obj.prix_unitaire:.2f} €"
    get_total.short_description = 'Total'

    def print_button(self, obj):
        return format_html(
            '<a class="material-icons" href="{}" target="_blank" style="color: #2196F3; text-decoration: none;" title="Imprimer">print</a>',
            f'/admin/sales_app/articlecommande/{obj.id}/print/'
        )
    print_button.short_description = '🖨️ Imprimer'

    def print_selected(self, request, queryset):
        return self.generate_pdf_report(queryset, "Rapport des Articles de Commande Sélectionnés")
    print_selected.short_description = "🖨️ Imprimer les articles sélectionnés"

    def print_all(self, request, queryset):
        all_items = ArticleCommande.objects.all().select_related('id_commande', 'id_produit')
        return self.generate_pdf_report(all_items, "Rapport Complet des Articles de Commande")
    print_all.short_description = "🖨️ Imprimer tous les articles"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_print_all'] = True
        extra_context['print_all_url'] = '/admin/sales_app/articlecommande/print_all/'
        return super().changelist_view(request, extra_context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:article_id>/print/', self.admin_site.admin_view(self.print_article_view), name='sales_app_articlecommande_print'),
            path('print_all/', self.admin_site.admin_view(self.print_all_view), name='sales_app_articlecommande_print_all'),
        ]
        return custom_urls + urls

    def print_article_view(self, request, article_id):
        try:
            article = ArticleCommande.objects.get(id=article_id)
            return self.generate_pdf_report([article], f"Article de Commande - {article.id_produit}")
        except ArticleCommande.DoesNotExist:
            return HttpResponse("Article de commande non trouvé", status=404)

    def print_all_view(self, request):
        all_items = ArticleCommande.objects.all().select_related('id_commande', 'id_produit')
        return self.generate_pdf_report(all_items, "Rapport Complet des Articles de Commande")

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
        
        data = [['Commande', 'Produit', 'Quantité', 'Prix Unitaire', 'Total']]
        for item in queryset:
            data.append([
                str(item.id_commande.id) if item.id_commande else 'N/A',
                str(item.id_produit) if item.id_produit else 'N/A',
                str(item.quantite),
                f"{item.prix_unitaire:.2f} €" if item.prix_unitaire else '0.00 €',
                f"{item.quantite * item.prix_unitaire:.2f} €" if item.quantite and item.prix_unitaire else '0.00 €'
            ])
        
        table = Table(data, colWidths=[1.5*inch, 2*inch, 1*inch, 1.2*inch, 1*inch])
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
