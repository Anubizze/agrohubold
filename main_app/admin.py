from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from modeltranslation.admin import TranslationAdmin
from .models import *


@admin.register(Thing)
class ThingAdmin(TranslationAdmin):
    list_display = ['name', 'description', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    
    # Show all language fields in the form
    fields = ('name_ru', 'name_kk', 'name_en', 'description_ru', 'description_kk', 'description_en')
    
    class Meta:
        model = Thing
        

@admin.register(NewsCategory)
class NewsCategoryAdmin(TranslationAdmin):
   list_display = ('name', 'slug', 'type')
   prepopulated_fields = {'slug': ('name',)}
   search_fields = ('name',)


@admin.register(News)
class NewsAdmin(TranslationAdmin):
   list_display = ('title', 'category', 'created_at', 'is_published', 'is_expert_news', 'is_guide')
   list_filter = ('category', 'is_published', 'created_at', 'is_expert_news', 'is_guide')
   search_fields = ('title', 'content')
   prepopulated_fields = {'slug': ('title',)} if hasattr(News, 'slug') else {}
   date_hierarchy = 'created_at'
   list_editable = ('is_published',)
   
   fieldsets = (
       (None, {
           'fields': ('title', 'short_description', 'content', 'image', 'category', 'is_published', 'is_expert_news', 'expert', 'is_guide')
       }),
   )


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at')
    list_filter = ('subscribed_at',)
    search_fields = ('email',)
    readonly_fields = ('subscribed_at',)


# Service models
@admin.register(ServiceProvider)
class ServiceProviderAdmin(TranslationAdmin):
    list_display = ('name', 'head', 'slug', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        (None, {'fields': ('name', 'slug', 'head', 'is_active')}),
        ('Контакты для каталога услуг', {
            'fields': ('contact_org', 'contact_division', 'contact_address', 'contact_email', 'contact_phone'),
        }),
    )


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(TranslationAdmin):
    list_display = ('name', 'provider', 'slug', 'order', 'is_active')
    list_filter = ('provider', 'is_active')
    search_fields = ('name', 'provider__name')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('order', 'is_active')
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'provider', 'order', 'is_active')
        }),
    )



class ServiceImageInline(admin.TabularInline):
    model = ServiceImage
    extra = 1
    fields = ('image', 'alt_text', 'is_primary', 'order')
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" style="max-height: 50px; max-width: 100px;">'
        return "No image"
    image_preview.allow_tags = True
    image_preview.short_description = "Preview"


@admin.register(Service)
class ServiceAdmin(TranslationAdmin):
    list_display = ('name', 'contact_member', 'operator', 'category', 'get_provider', 'price', 'currency', 'is_active', 'created_at')
    list_filter = ('category__provider', 'category', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'short_description', 'contact_member__name')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('price', 'is_active')
    date_hierarchy = 'created_at'
    autocomplete_fields = ('contact_member',)
    inlines = [ServiceImageInline]
    
    def get_provider(self, obj):
        return obj.category.provider.name
    get_provider.short_description = 'Provider'
    get_provider.admin_order_field = 'category__provider__name'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'category')
        }),
        ('Описание', {
            'fields': ('short_description', 'description', 'duration')
        }),
        ('Цена', {
            'fields': ('price', 'currency')
        }),
        ('Контакт на сайте', {
            'fields': ('contact_member', 'contact_member_preview'),
            'description': 'Выберите человека из реестра команды — фото, ФИО и должность появятся в карточке услуги.',
        }),
        ('Настройки', {
            'fields': ('operator', 'is_active',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'contact_member_preview')
    
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('created_at', 'updated_at')
        return self.readonly_fields

    def contact_member_preview(self, obj):
        if not obj or not obj.contact_member_id:
            return '—'
        member = obj.contact_member
        url = member.get_photo_url()
        html = f'<strong>{member.name}</strong><br>{member.position}'
        if url:
            html = (
                f'<img src="{url}" width="72" height="72" '
                f'style="object-fit:cover;border-radius:12px;margin-right:12px;float:left;" />'
                + html
            )
        return format_html(html)
    contact_member_preview.short_description = 'Предпросмотр'
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "category":
            kwargs["queryset"] = ServiceCategory.objects.filter(is_active=True).select_related('provider').order_by('provider__name', 'order', 'name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(ServiceImage)
class ServiceImageAdmin(admin.ModelAdmin):
    list_display = ('service', 'alt_text', 'is_primary', 'order', 'image_preview')
    list_filter = ('is_primary', 'service__category')
    search_fields = ('service__name', 'alt_text')
    list_editable = ('is_primary', 'order')
    
    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" style="max-height: 50px; max-width: 100px;">'
        return "No image"
    image_preview.allow_tags = True
    image_preview.short_description = "Preview"


class HubRequestAdminMixin(admin.ModelAdmin):
    list_display = (
        'get_request_number_display', 'client_name', 'get_context_display',
        'status', 'source_page', 'created_at',
    )
    list_filter = ('status', 'created_at')
    search_fields = (
        'client_name', 'client_email', 'client_iin', 'company_bin',
        'object_title', 'proposal_title', 'message', 'source_page',
    )
    list_editable = ('status',)
    date_hierarchy = 'created_at'
    readonly_fields = (
        'created_at', 'updated_at', 'total_price', 'tracking_token',
        'get_request_number_display', 'request_type', 'object_type', 'object_id',
        'source_page',
    )

    def get_request_number_display(self, obj):
        return obj.get_request_number() if obj.pk else '—'
    get_request_number_display.short_description = 'Номер заявки'

    def get_context_display(self, obj):
        return obj.get_context_label()
    get_context_display.short_description = 'Контекст'

    actions = ['mark_as_confirmed', 'mark_as_completed', 'mark_as_cancelled']

    def mark_as_confirmed(self, request, queryset):
        updated = queryset.update(status='confirmed')
        self.message_user(request, f'{updated} заявок отмечены как подтвержденные.')
    mark_as_confirmed.short_description = 'Отметить как подтвержденные'

    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} заявок отмечены как завершенные.')
    mark_as_completed.short_description = 'Отметить как завершенные'

    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} заявок отмечены как отмененные.')
    mark_as_cancelled.short_description = 'Отметить как отмененные'


@admin.register(ServiceRequestProxy)
class ServiceRequestAdmin(HubRequestAdminMixin):
    filter_horizontal = ('services',)

    def get_queryset(self, request):
        return super().get_queryset(request).filter(request_type='SERVICE')

    def save_model(self, request, obj, form, change):
        obj.request_type = 'SERVICE'
        super().save_model(request, obj, form, change)
        obj.calculate_total()

    fieldsets = (
        ('Услуги', {'fields': ('services', 'object_title', 'object_type', 'object_id')}),
        ('Клиент', {
            'fields': (
                'user', 'client_name', 'client_email', 'client_phone',
                'client_type', 'client_iin', 'company_bin',
            )
        }),
        ('Заявка', {
            'fields': (
                'message', 'status', 'total_price', 'source_page',
                'get_request_number_display', 'tracking_token', 'attachment',
            )
        }),
        ('Временные метки', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    actions = HubRequestAdminMixin.actions + ['recalculate_totals']

    def recalculate_totals(self, request, queryset):
        for obj in queryset:
            obj.calculate_total()
        self.message_user(request, f'Пересчитана сумма для {queryset.count()} заявок.')
    recalculate_totals.short_description = 'Пересчитать общие суммы'


@admin.register(ProjectCollaborationRequest)
class ProjectCollaborationRequestAdmin(HubRequestAdminMixin):
    autocomplete_fields = ('project',)

    def get_queryset(self, request):
        return super().get_queryset(request).filter(request_type='PROJECT')

    def save_model(self, request, obj, form, change):
        obj.request_type = 'PROJECT'
        super().save_model(request, obj, form, change)

    fieldsets = (
        ('Проект', {'fields': ('project', 'object_title', 'object_type', 'object_id')}),
        ('Клиент', {
            'fields': ('user', 'client_name', 'client_email', 'client_phone', 'client_type', 'client_iin', 'company_bin')
        }),
        ('Заявка', {
            'fields': ('message', 'status', 'source_page', 'get_request_number_display', 'tracking_token', 'attachment')
        }),
        ('Временные метки', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


@admin.register(ProjectProposalRequest)
class ProjectProposalRequestAdmin(HubRequestAdminMixin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(request_type='PROJECT_PROPOSAL')

    def save_model(self, request, obj, form, change):
        obj.request_type = 'PROJECT_PROPOSAL'
        super().save_model(request, obj, form, change)

    fieldsets = (
        ('Предложение', {'fields': ('proposal_title', 'message', 'attachment')}),
        ('Клиент', {
            'fields': ('user', 'client_name', 'client_email', 'client_phone')
        }),
        ('Заявка', {
            'fields': ('status', 'source_page', 'get_request_number_display', 'tracking_token')
        }),
        ('Временные метки', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


@admin.register(GeneralRequestProxy)
class GeneralRequestAdmin(HubRequestAdminMixin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(request_type='GENERAL')

    def save_model(self, request, obj, form, change):
        obj.request_type = 'GENERAL'
        super().save_model(request, obj, form, change)

    fieldsets = (
        ('Запрос', {'fields': ('category', 'message', 'object_type', 'object_id', 'object_title', 'attachment')}),
        ('Клиент', {
            'fields': ('user', 'client_name', 'client_email', 'client_phone')
        }),
        ('Заявка', {
            'fields': ('status', 'source_page', 'get_request_number_display', 'tracking_token')
        }),
        ('Временные метки', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


@admin.register(CourseCategory)
class CourseCategoryAdmin(TranslationAdmin):
    list_display = ('name', 'slug', 'order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('order', 'is_active')
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'order', 'is_active')
        }),
    )


class CourseModuleInline(admin.TabularInline):
    model = CourseModule
    extra = 1
    fields = ('title', 'order')
    show_change_link = True


class CourseTopicInline(admin.TabularInline):
    model = CourseTopic
    extra = 1
    fields = ('title', 'order')


@admin.register(Course)
class CourseAdmin(TranslationAdmin):
    list_display = ('title', 'category', 'price', 'duration_hours', 'is_active', 'is_popular', 'has_discount', 'created_at')
    list_filter = ('category', 'is_active', 'is_popular', 'has_discount', 'created_at')
    search_fields = ('title', 'description', 'short_description')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('price', 'is_active', 'is_popular', 'has_discount')
    date_hierarchy = 'created_at'
    inlines = [CourseModuleInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug', 'category', 'main_image')
        }),
        ('Описание', {
            'fields': ('short_description', 'description')
        }),
        ('Стоимость и скидки', {
            'fields': ('price', 'discount_percentage', 'has_discount')
        }),
        ('Характеристики курса', {
            'fields': ('duration_hours', 'hours_per_week')
        }),
        ('Преподаватели', {
            'fields': ('instructors',)
        }),
        ('Контакты на странице курса', {
            'fields': ('contact_person', 'contact_org', 'contact_division', 'contact_address', 'contact_email', 'contact_phone'),
        }),
        ('Настройки', {
            'fields': ('is_active', 'is_popular')
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('created_at', 'updated_at')
        return self.readonly_fields
    
    def save_model(self, request, obj, form, change):
        if not obj.slug:
            from django.utils.text import slugify
            import uuid
            obj.slug = f"{slugify(obj.title)}-{str(uuid.uuid4())[:8]}"
        super().save_model(request, obj, form, change)


@admin.register(Instructor)
class InstructorAdmin(TranslationAdmin):
    list_display = ('name', 'title', 'get_courses_count')
    search_fields = ('name', 'title', 'bio')
    
    def get_courses_count(self, obj):
        return obj.taught_courses.count()
    get_courses_count.short_description = 'Количество курсов'
    
    fieldsets = (
        ('Личная информация', {
            'fields': ('name', 'title', 'photo')
        }),
        ('Биография', {
            'fields': ('bio',)
        }),
    )


@admin.register(CourseModule)
class CourseModuleAdmin(TranslationAdmin):
    list_display = ('title', 'course', 'order', 'get_topics_count')
    list_filter = ('course',)
    search_fields = ('title', 'course__title')
    list_editable = ('order',)
    inlines = [CourseTopicInline]
    
    def get_topics_count(self, obj):
        return obj.topics.count()
    get_topics_count.short_description = 'Количество тем'
    
    fieldsets = (
        (None, {
            'fields': ('course', 'title', 'order')
        }),
    )


@admin.register(CourseTopic)
class CourseTopicAdmin(TranslationAdmin):
    list_display = ('title', 'get_module', 'get_course', 'order')
    list_filter = ('module__course', 'module')
    search_fields = ('title', 'module__title', 'module__course__title')
    list_editable = ('order',)
    
    def get_module(self, obj):
        return obj.module.title
    get_module.short_description = 'Модуль'
    get_module.admin_order_field = 'module__title'
    
    def get_course(self, obj):
        return obj.module.course.title
    get_course.short_description = 'Курс'
    get_course.admin_order_field = 'module__course__title'
    
    fieldsets = (
        (None, {
            'fields': ('module', 'title', 'order')
        }),
    )


@admin.register(CourseReview)
class CourseReviewAdmin(TranslationAdmin):
    list_display = ('reviewer_name', 'course', 'rating', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_approved', 'created_at', 'course')
    search_fields = ('reviewer_name', 'comment', 'course__title')
    list_editable = ('is_approved',)
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Отзыв', {
            'fields': ('course', 'reviewer_name', 'reviewer_photo', 'rating')
        }),
        ('Комментарий', {
            'fields': ('comment',)
        }),
        ('Модерация', {
            'fields': ('is_approved', 'created_at')
        }),
    )
    
    actions = ['approve_reviews', 'disapprove_reviews']
    
    def approve_reviews(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} отзывов одобрено.')
    approve_reviews.short_description = "Одобрить отзывы"
    
    def disapprove_reviews(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} отзывов отклонено.')
    disapprove_reviews.short_description = "Отклонить отзывы"


@admin.register(CourseApplication)
class CourseApplicationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'course', 'phone', 'email', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'course')
    search_fields = ('full_name', 'phone', 'email', 'course__title')
    list_editable = ('status',)
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Заявка', {
            'fields': ('course', 'status')
        }),
        ('Контактная информация', {
            'fields': ('full_name', 'phone', 'email')
        }),
        ('Временные метки', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_contacted', 'mark_as_enrolled', 'mark_as_rejected']
    
    def mark_as_contacted(self, request, queryset):
        updated = queryset.update(status='contacted')
        self.message_user(request, f'{updated} заявок отмечены как "Связались".')
    mark_as_contacted.short_description = "Отметить как 'Связались'"
    
    def mark_as_enrolled(self, request, queryset):
        updated = queryset.update(status='enrolled')
        self.message_user(request, f'{updated} заявок отмечены как "Записан".')
    mark_as_enrolled.short_description = "Отметить как 'Записан'"
    
    def mark_as_rejected(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} заявок отмечены как "Отклонен".')
    mark_as_rejected.short_description = "Отметить как 'Отклонен'"


@admin.register(ProjectDirection)
class ProjectDirectionAdmin(TranslationAdmin):
    list_display = ('name', 'slug', 'is_active', 'order', 'projects_count')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active', 'order')
    ordering = ('order', 'name')
    
    def projects_count(self, obj):
        return obj.projects.count()
    projects_count.short_description = 'Количество проектов'


@admin.register(ProjectStatus)
class ProjectStatusAdmin(TranslationAdmin):
    list_display = ('name', 'status_type', 'color_preview', 'is_active', 'order', 'projects_count')
    list_filter = ('status_type', 'is_active')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active', 'order')
    ordering = ('order',)
    
    def color_preview(self, obj):
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border: 1px solid #ccc; border-radius: 50%;"></div>',
            obj.color
        )
    color_preview.short_description = 'Цвет'
    
    def projects_count(self, obj):
        return obj.projects.count()
    projects_count.short_description = 'Количество проектов'


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    fields = ('image', 'caption', 'order')
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" style="object-fit: cover;" />', obj.image.url)
        return "Нет изображения"
    image_preview.short_description = 'Превью'


class ProjectTeamMemberInline(admin.TabularInline):
    model = ProjectTeamMember
    extra = 1
    fields = ('name', 'position', 'email', 'photo_preview')
    readonly_fields = ('photo_preview',)
    
    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 50%;" />', obj.photo.url)
        return "Нет фото"
    photo_preview.short_description = 'Фото'


class ProjectInfoPanelInline(admin.StackedInline):
    model = ProjectInfoPanel
    extra = 1
    fields = (
        'title',
        'display_mode',
        'trigger_label',
        'accent_color',
        'items',
        'order',
        'is_active',
    )


@admin.register(ProjectInfoPanel)
class ProjectInfoPanelAdmin(TranslationAdmin):
    list_display = ('title', 'project', 'display_mode', 'order', 'is_active')
    list_filter = ('display_mode', 'is_active', 'project__direction')
    search_fields = ('title', 'items', 'project__title')
    list_editable = ('order', 'is_active')
    ordering = ('project', 'order', 'id')

    fieldsets = (
        (None, {
            'fields': ('project', 'title', 'display_mode', 'trigger_label', 'accent_color', 'order', 'is_active'),
        }),
        ('Содержимое', {
            'fields': ('items',),
            'description': 'Каждый пункт списка — с новой строки.',
        }),
    )


@admin.register(Project)
class ProjectAdmin(TranslationAdmin):
    list_display = (
        'title', 'direction', 'status_with_color', 'investment_formatted', 
        'implementation_period', 'is_featured', 'is_published', 'created_at'
    )
    list_filter = ('direction', 'status', 'is_featured', 'is_published', 'created_at')
    search_fields = ('title', 'short_description', 'description')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_featured', 'is_published')
    readonly_fields = ('image_preview', 'created_at', 'updated_at', 'get_absolute_url')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug', 'direction', 'status')
        }),
        ('Описания', {
            'fields': ('short_description', 'description', 'client_problem', 'our_solution'),
            'classes': ('wide',)
        }),
        ('Финансы и сроки', {
            'fields': ('investment_amount', 'implementation_period')
        }),
        ('Контакты (таб на странице проекта)', {
            'fields': ('contact_person', 'contact_org', 'contact_division', 'contact_address', 'contact_email', 'contact_phone'),
        }),
        ('Изображение', {
            'fields': ('main_image', 'image_preview')
        }),
        ('Настройки', {
            'fields': ('is_featured', 'is_published'),
            'classes': ('collapse',)
        }),
        ('Служебная информация', {
            'fields': ('created_at', 'updated_at', 'get_absolute_url'),
            'classes': ('collapse',),
        }),
    )
    
    inlines = [ProjectInfoPanelInline, ProjectImageInline, ProjectTeamMemberInline]
    
    def status_with_color(self, obj):
        return format_html(
            '<span style="display: inline-flex; align-items: center;">'
            '<div style="width: 12px; height: 12px; background-color: {}; border-radius: 50%; margin-right: 8px;"></div>'
            '{}</span>',
            obj.status.color,
            obj.status.name
        )
    status_with_color.short_description = 'Статус'
    
    def investment_formatted(self, obj):
        return f"{obj.get_formatted_investment()} ₸"
    investment_formatted.short_description = 'Инвестиции'
    
    def image_preview(self, obj):
        if obj.main_image:
            return format_html('<img src="{}" width="300" style="max-height: 200px; object-fit: cover;" />', obj.main_image.url)
        return "Нет изображения"
    image_preview.short_description = 'Превью изображения'
    
    def get_absolute_url(self, obj):
        if obj.pk:
            url = obj.get_absolute_url()
            return format_html('<a href="{}" target="_blank">Посмотреть на сайте</a>', url)
        return "Сохраните проект для получения ссылки"
    get_absolute_url.short_description = 'Ссылка на сайте'
    
    actions = ['make_featured', 'remove_featured', 'publish', 'unpublish']
    
    def make_featured(self, request, queryset):
        queryset.update(is_featured=True)
        self.message_user(request, f"Отмечено как рекомендуемые: {queryset.count()} проектов")
    make_featured.short_description = "Отметить как рекомендуемые"
    
    def remove_featured(self, request, queryset):
        queryset.update(is_featured=False)
        self.message_user(request, f"Убрано из рекомендуемых: {queryset.count()} проектов")
    remove_featured.short_description = "Убрать из рекомендуемых"
    
    def publish(self, request, queryset):
        queryset.update(is_published=True)
        self.message_user(request, f"Опубликовано: {queryset.count()} проектов")
    publish.short_description = "Опубликовать"
    
    def unpublish(self, request, queryset):
        queryset.update(is_published=False)
        self.message_user(request, f"Снято с публикации: {queryset.count()} проектов")
    unpublish.short_description = "Снять с публикации"


@admin.register(ProjectImage)
class ProjectImageAdmin(admin.ModelAdmin):
    list_display = ('project', 'caption', 'order', 'image_preview')
    list_filter = ('project__direction', 'project__status')
    search_fields = ('project__title', 'caption')
    list_editable = ('order',)
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" style="object-fit: cover;" />', obj.image.url)
        return "Нет изображения"
    image_preview.short_description = 'Превью'


@admin.register(ProjectTeamMember)
class ProjectTeamMemberAdmin(TranslationAdmin):
    list_display = ('name', 'position', 'project', 'email', 'photo_preview')
    list_filter = ('project__direction', 'project__status')
    search_fields = ('name', 'position', 'project__title', 'email')
    readonly_fields = ('photo_preview',)
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('project', 'name', 'position', 'email')
        }),
        ('Дополнительно', {
            'fields': ('bio', 'photo', 'photo_preview'),
            'classes': ('wide',)
        }),
    )
    
    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="100" height="100" style="object-fit: cover; border-radius: 50%;" />', obj.photo.url)
        return "Нет фото"
    photo_preview.short_description = 'Фото'


@admin.register(ProjectsCatalogSettings)
class ProjectsCatalogSettingsAdmin(TranslationAdmin):
    def has_add_permission(self, request):
        return not ProjectsCatalogSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    readonly_fields = ('projects_hero_preview', 'patents_hero_preview')

    fieldsets = (
        ('Картинки героя', {
            'fields': (
                'projects_hero_image', 'projects_hero_preview',
                'patents_hero_image', 'patents_hero_preview',
            ),
        }),
        ('Заголовки', {
            'fields': ('projects_title', 'patents_title'),
        }),
        ('Тексты под заголовком', {
            'fields': ('projects_lead', 'patents_lead'),
            'classes': ('wide',),
        }),
    )

    def projects_hero_preview(self, obj):
        if obj and obj.projects_hero_image:
            return format_html(
                '<img src="{}" style="max-width: 360px; max-height: 200px; object-fit: cover; border-radius: 8px;" />',
                obj.projects_hero_image.url,
            )
        return "Не загружено"
    projects_hero_preview.short_description = 'Превью (Проекты)'

    def patents_hero_preview(self, obj):
        if obj and obj.patents_hero_image:
            return format_html(
                '<img src="{}" style="max-width: 360px; max-height: 200px; object-fit: cover; border-radius: 8px;" />',
                obj.patents_hero_image.url,
            )
        return "Не загружено"
    patents_hero_preview.short_description = 'Превью (Патенты)'


@admin.register(PatentType)
class PatentTypeAdmin(TranslationAdmin):
    list_display = ('name', 'slug', 'is_active', 'order', 'patents_count')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active', 'order')
    ordering = ('order', 'name')

    def patents_count(self, obj):
        return obj.patents.count()
    patents_count.short_description = 'Количество'


@admin.register(Patent)
class PatentAdmin(TranslationAdmin):
    list_display = (
        'icon_thumb', 'title', 'patent_type', 'registration_number',
        'registration_date', 'is_active_status', 'is_published', 'order',
    )
    list_filter = ('patent_type', 'is_published', 'is_active_status', 'registration_date')
    search_fields = ('title', 'registration_number', 'authors', 'short_description', 'description')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_published', 'is_active_status', 'order')
    date_hierarchy = 'registration_date'
    ordering = ('order', '-registration_date')
    readonly_fields = ('icon_preview',)

    fieldsets = (
        ('Основное', {
            'fields': ('title', 'slug', 'patent_type', 'registration_number', 'authors', 'country'),
        }),
        ('Иконка карточки', {
            'fields': ('icon', 'icon_preview', 'badge_letter'),
        }),
        ('Даты и статус', {
            'fields': ('application_date', 'registration_date', 'is_active_status'),
        }),
        ('Описания', {
            'fields': ('short_description', 'description', 'benefits'),
            'classes': ('wide',),
        }),
        ('Документы и ссылки', {
            'fields': ('document', 'read_url'),
        }),
        ('Публикация', {
            'fields': ('is_published', 'order'),
        }),
    )

    def icon_thumb(self, obj):
        if obj.icon:
            return format_html(
                '<img src="{}" width="40" height="40" style="object-fit:cover;border-radius:50%;" />',
                obj.icon.url,
            )
        return format_html(
            '<span style="display:inline-flex;width:40px;height:40px;border-radius:50%;'
            'background:#00263E;color:#fff;align-items:center;justify-content:center;font-weight:700;">{}</span>',
            obj.get_letter(),
        )
    icon_thumb.short_description = 'Иконка'

    def icon_preview(self, obj):
        if obj and obj.icon:
            return format_html(
                '<img src="{}" style="width:96px;height:96px;object-fit:cover;border-radius:50%;" />',
                obj.icon.url,
            )
        return "Не загружено — будет буква типа"
    icon_preview.short_description = 'Превью'


@admin.register(Expert)
class ExpertAdmin(TranslationAdmin):
    list_display = ('name', 'bio')
    search_fields = ('name', 'bio')
    
    fieldsets = (
        ('Личная информация', {
            'fields': ('name', 'photo')
        }),
        ('Биография', {
            'fields': ('bio',)
        }),
    )


@admin.register(Partner)
class PartnerAdmin(TranslationAdmin):
    list_display = ['name', 'phone', 'email', 'slug']
    search_fields = ['name', 'email', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    fields = ('name', 'slug', 'phone', 'manager_phone', 'email', 'website')

@admin.register(Product)
class ProductAdmin(TranslationAdmin):
    list_display = ['name', 'partner', 'price', 'article_number']
    list_filter = ['partner']
    search_fields = ['name', 'article_number']
    fields = ('name', 'partner', 'price', 'article_number', 'availability','delivery_time', 'image')


@admin.register(TeamDepartment)
class TeamDepartmentAdmin(TranslationAdmin):
    list_display = ('name', 'slug', 'is_active', 'order', 'members_count')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active', 'order')
    ordering = ('order', 'name')

    def members_count(self, obj):
        return obj.members.count()
    members_count.short_description = 'Участников'


@admin.register(TeamMember)
class TeamMemberAdmin(TranslationAdmin):
    list_display = (
        'photo_thumb', 'name', 'position', 'department',
        'is_leadership', 'is_active', 'order',
    )
    list_filter = ('department', 'is_leadership', 'is_active')
    search_fields = ('name', 'position', 'email', 'phone')
    list_editable = ('order', 'is_active', 'is_leadership')
    ordering = ('department__order', 'order', 'name')
    readonly_fields = ('photo_preview',)

    fieldsets = (
        ('Основное', {
            'fields': ('department', 'name', 'position'),
            'description': 'ФИО и должность отображаются на карточке участника.',
        }),
        ('Фото', {
            'fields': ('photo', 'photo_preview', 'external_photo', 'static_photo'),
        }),
        ('Контакты', {
            'fields': ('email', 'phone'),
        }),
        ('Настройки', {
            'fields': ('is_leadership', 'is_active', 'order'),
        }),
    )

    def photo_thumb(self, obj):
        url = obj.get_photo_url()
        if url:
            return format_html(
                '<img src="{}" width="44" height="44" style="object-fit:cover;border-radius:10px;" />',
                url,
            )
        return "—"
    photo_thumb.short_description = 'Фото'

    def photo_preview(self, obj):
        url = obj.get_photo_url() if obj else ''
        if url:
            return format_html(
                '<img src="{}" style="max-width:220px;max-height:220px;object-fit:cover;border-radius:14px;" />',
                url,
            )
        return "Фото не задано"
    photo_preview.short_description = 'Превью'


@admin.register(AboutPageSettings)
class AboutPageSettingsAdmin(TranslationAdmin):
    def has_add_permission(self, request):
        return not AboutPageSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    readonly_fields = ('hero_image_preview',)

    fieldsets = (
        ('Герой', {
            'fields': ('hero_title', 'hero_subtitle', 'hero_image', 'hero_image_preview'),
        }),
        ('Карточки', {
            'fields': (
                'card_company_title', 'card_company_desc',
                'card_team_title', 'card_team_desc',
                'card_lab_title', 'card_lab_desc',
                'card_eng_title', 'card_eng_desc',
            ),
        }),
        ('CTA (сотрудничество)', {
            'fields': ('cta_title', 'cta_propose', 'cta_partner'),
        }),
        ('Кто мы?', {
            'fields': (
                'who_we_are_title',
                'who_we_are_p1', 'who_we_are_p2', 'who_we_are_p3', 'who_we_are_p4',
            ),
        }),
        ('Наша цель', {
            'fields': (
                'purpose_title',
                'purpose_p1', 'purpose_p2', 'purpose_p3', 'purpose_p4',
            ),
        }),
        ('Наша миссия', {
            'fields': (
                'mission_title',
                'mission_p1', 'mission_p2', 'mission_p3', 'mission_p4',
            ),
        }),
        ('Блок команды', {
            'fields': ('team_cta_title', 'team_cta_description', 'team_cta_button'),
        }),
    )

    def hero_image_preview(self, obj):
        if obj and obj.hero_image:
            return format_html(
                '<img src="{}" style="max-width: 360px; max-height: 200px; object-fit: cover; border-radius: 8px;" />',
                obj.hero_image.url,
            )
        return "Не загружено"
    hero_image_preview.short_description = 'Превью героя'


class HomeServiceSlideInline(admin.TabularInline):
    model = HomeServiceSlide
    extra = 0
    fields = ('title', 'image', 'external_image', 'link_url', 'order', 'is_active')
    ordering = ('order',)


@admin.register(HomePageSettings)
class HomePageSettingsAdmin(TranslationAdmin):
    def has_add_permission(self, request):
        return not HomePageSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    inlines = [HomeServiceSlideInline]
    readonly_fields = ('hero_image_preview',)

    fieldsets = (
        ('Герой', {
            'fields': (
                'brand', 'hero_title', 'hero_subtitle',
                'hero_btn_primary', 'hero_btn_secondary',
                'hero_image', 'hero_image_preview',
            ),
        }),
        ('Услуги', {
            'fields': ('services_title',),
        }),
        ('Преимущества', {
            'fields': (
                'advantages_title',
                'advantage_1_title', 'advantage_1_description',
                'advantage_2_title', 'advantage_2_description',
                'advantage_3_title', 'advantage_3_description',
                'advantage_4_title', 'advantage_4_description',
            ),
        }),
        ('Новости', {
            'fields': ('news_title', 'news_read_more', 'news_all_btn'),
        }),
        ('CTA', {
            'fields': ('cta_title', 'cta_description', 'cta_button'),
        }),
    )

    def hero_image_preview(self, obj):
        if obj and obj.hero_image:
            return format_html(
                '<img src="{}" style="max-width: 360px; max-height: 200px; object-fit: cover; border-radius: 8px;" />',
                obj.hero_image.url,
            )
        return "Не загружено"
    hero_image_preview.short_description = 'Превью героя'


class LabServiceCardInline(admin.TabularInline):
    model = LabServiceCard
    extra = 0
    fields = ('title', 'icon_class', 'order', 'is_active')
    ordering = ('order',)


@admin.register(LabPageSettings)
class LabPageSettingsAdmin(TranslationAdmin):
    def has_add_permission(self, request):
        return not LabPageSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    inlines = [LabServiceCardInline]
    readonly_fields = (
        'hero_image_preview', 'about_image_preview',
        'testing_image_preview', 'collective_image_preview',
        'food_image_preview', 'vet_image_preview', 'milk_image_preview',
    )

    fieldsets = (
        ('Герой', {
            'fields': ('hero_title', 'hero_subtitle', 'hero_image', 'hero_image_preview'),
        }),
        ('Заголовок страницы', {
            'fields': ('page_title',),
        }),
        ('О центре', {
            'fields': ('about_title', 'about_p1', 'about_p2', 'about_p3', 'about_image', 'about_image_preview'),
        }),
        ('Услуги и лаборатории', {
            'fields': ('services_title', 'labs_title'),
        }),
        ('Испытательная лаборатория', {
            'fields': ('testing_title', 'testing_desc', 'testing_image', 'testing_image_preview'),
        }),
        ('Коллективная лаборатория', {
            'fields': ('collective_title', 'collective_desc', 'collective_image', 'collective_image_preview'),
        }),
        ('Агротехнопарк', {
            'fields': ('agro_title', 'agro_p1', 'agro_p2'),
        }),
        ('Пищевая безопасность', {
            'fields': ('food_title', 'food_desc', 'food_image', 'food_image_preview'),
        }),
        ('Ветеринарная клиника', {
            'fields': ('vet_title', 'vet_desc', 'vet_image', 'vet_image_preview'),
        }),
        ('Анализ молока', {
            'fields': ('milk_title', 'milk_desc', 'milk_image', 'milk_image_preview'),
        }),
        ('Контакты', {
            'fields': (
                'contact_title', 'address_label', 'address_text',
                'contacts_label', 'email_text', 'phone_text',
            ),
        }),
    )

    def _img_preview(self, img):
        if img:
            return format_html(
                '<img src="{}" style="max-width: 280px; max-height: 160px; object-fit: cover; border-radius: 8px;" />',
                img.url,
            )
        return "Не загружено"

    def hero_image_preview(self, obj):
        return self._img_preview(obj.hero_image if obj else None)
    hero_image_preview.short_description = 'Превью героя'

    def about_image_preview(self, obj):
        return self._img_preview(obj.about_image if obj else None)
    about_image_preview.short_description = 'Превью'

    def testing_image_preview(self, obj):
        return self._img_preview(obj.testing_image if obj else None)
    testing_image_preview.short_description = 'Превью'

    def collective_image_preview(self, obj):
        return self._img_preview(obj.collective_image if obj else None)
    collective_image_preview.short_description = 'Превью'

    def food_image_preview(self, obj):
        return self._img_preview(obj.food_image if obj else None)
    food_image_preview.short_description = 'Превью'

    def vet_image_preview(self, obj):
        return self._img_preview(obj.vet_image if obj else None)
    vet_image_preview.short_description = 'Превью'

    def milk_image_preview(self, obj):
        return self._img_preview(obj.milk_image if obj else None)
    milk_image_preview.short_description = 'Превью'


class EngineeringServiceCardInline(admin.TabularInline):
    model = EngineeringServiceCard
    extra = 0
    fields = ('title', 'icon_class', 'order', 'is_active')
    ordering = ('order',)


@admin.register(EngineeringPageSettings)
class EngineeringPageSettingsAdmin(TranslationAdmin):
    def has_add_permission(self, request):
        return not EngineeringPageSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    inlines = [EngineeringServiceCardInline]
    readonly_fields = (
        'hero_image_preview', 'about_image_preview',
        'plasma_image_preview', 'materials_image_preview',
    )

    fieldsets = (
        ('Герой', {
            'fields': ('hero_title', 'hero_subtitle', 'hero_image', 'hero_image_preview'),
        }),
        ('Заголовок страницы', {
            'fields': ('page_title',),
        }),
        ('О центре', {
            'fields': ('about_title', 'about_p1', 'about_p2', 'about_p3', 'about_image', 'about_image_preview'),
        }),
        ('Услуги и лаборатории', {
            'fields': ('services_title', 'labs_title'),
        }),
        ('Плазменная лаборатория', {
            'fields': ('plasma_title', 'plasma_desc', 'plasma_image', 'plasma_image_preview'),
        }),
        ('Материаловедение', {
            'fields': ('materials_title', 'materials_desc', 'materials_image', 'materials_image_preview'),
        }),
        ('Контакты', {
            'fields': (
                'contact_title', 'address_label', 'address_text',
                'contacts_label', 'email_text', 'phone_text',
            ),
        }),
    )

    def _img_preview(self, img):
        if img:
            return format_html(
                '<img src="{}" style="max-width: 280px; max-height: 160px; object-fit: cover; border-radius: 8px;" />',
                img.url,
            )
        return "Не загружено"

    def hero_image_preview(self, obj):
        return self._img_preview(obj.hero_image if obj else None)
    hero_image_preview.short_description = 'Превью героя'

    def about_image_preview(self, obj):
        return self._img_preview(obj.about_image if obj else None)
    about_image_preview.short_description = 'Превью'

    def plasma_image_preview(self, obj):
        return self._img_preview(obj.plasma_image if obj else None)
    plasma_image_preview.short_description = 'Превью'

    def materials_image_preview(self, obj):
        return self._img_preview(obj.materials_image if obj else None)
    materials_image_preview.short_description = 'Превью'


@admin.register(PartnersPageSettings)
class PartnersPageSettingsAdmin(TranslationAdmin):
    def has_add_permission(self, request):
        return not PartnersPageSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    readonly_fields = ('hero_image_preview',)

    fieldsets = (
        ('Герой', {
            'fields': ('hero_title', 'hero_subtitle', 'hero_image', 'hero_image_preview'),
        }),
        ('Карточки', {
            'fields': (
                'card_about_title', 'card_about_desc',
                'card_shop_title', 'card_shop_desc',
            ),
        }),
        ('CTA', {
            'fields': ('cta_title', 'cta_propose', 'cta_shop'),
        }),
        ('Контент', {
            'fields': ('content_title', 'content_p1', 'content_p2'),
        }),
    )

    def hero_image_preview(self, obj):
        if obj and obj.hero_image:
            return format_html(
                '<img src="{}" style="max-width: 360px; max-height: 200px; object-fit: cover; border-radius: 8px;" />',
                obj.hero_image.url,
            )
        return "Не загружено"
    hero_image_preview.short_description = 'Превью героя'


@admin.register(InnovationOfficeSettings)
class InnovationOfficeSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not InnovationOfficeSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    fieldsets = (
        (None, {
            'fields': ('title', 'lead', 'organization', 'division', 'address', 'email', 'phone'),
        }),
    )


@admin.register(ServicesPageSettings)
class ServicesPageSettingsAdmin(TranslationAdmin):
    def has_add_permission(self, request):
        return not ServicesPageSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    readonly_fields = ('hero_image_preview',)

    fieldsets = (
        (None, {
            'fields': ('heading', 'lead', 'btn_price', 'btn_catalog', 'hero_image', 'hero_image_preview'),
        }),
    )

    def hero_image_preview(self, obj):
        if obj and obj.hero_image:
            return format_html(
                '<img src="{}" style="max-width: 360px; max-height: 200px; object-fit: cover; border-radius: 8px;" />',
                obj.hero_image.url,
            )
        return "Не загружено"
    hero_image_preview.short_description = 'Превью'


@admin.register(CoursesPageSettings)
class CoursesPageSettingsAdmin(TranslationAdmin):
    def has_add_permission(self, request):
        return not CoursesPageSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    readonly_fields = ('hero_image_preview',)

    fieldsets = (
        (None, {
            'fields': (
                'heading', 'lead', 'category_lead',
                'btn_price', 'btn_catalog', 'hero_image', 'hero_image_preview',
            ),
        }),
    )

    def hero_image_preview(self, obj):
        if obj and obj.hero_image:
            return format_html(
                '<img src="{}" style="max-width: 360px; max-height: 200px; object-fit: cover; border-radius: 8px;" />',
                obj.hero_image.url,
            )
        return "Не загружено"
    hero_image_preview.short_description = 'Превью'


@admin.register(TeamPageSettings)
class TeamPageSettingsAdmin(TranslationAdmin):
    def has_add_permission(self, request):
        return not TeamPageSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    readonly_fields = ('hero_image_preview',)

    fieldsets = (
        (None, {
            'fields': ('title', 'subtitle', 'hero_image', 'hero_image_preview'),
        }),
    )

    def hero_image_preview(self, obj):
        if obj and obj.hero_image:
            return format_html(
                '<img src="{}" style="max-width: 360px; max-height: 200px; object-fit: cover; border-radius: 8px;" />',
                obj.hero_image.url,
            )
        return "Не загружено"
    hero_image_preview.short_description = 'Превью'


@admin.register(NewsPageSettings)
class NewsPageSettingsAdmin(TranslationAdmin):
    def has_add_permission(self, request):
        return not NewsPageSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    readonly_fields = ('hero_image_preview',)

    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'subscribe_button', 'hero_image', 'hero_image_preview'),
        }),
    )

    def hero_image_preview(self, obj):
        if obj and obj.hero_image:
            return format_html(
                '<img src="{}" style="max-width: 360px; max-height: 200px; object-fit: cover; border-radius: 8px;" />',
                obj.hero_image.url,
            )
        return "Не загружено"
    hero_image_preview.short_description = 'Превью'
