import os
import sys
import secrets
from PIL import Image
from io import BytesIO
from django.db import models
from django.urls import reverse
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from users.models import User

class Thing(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Thing"
        verbose_name_plural = "Things"
        
class Expert(models.Model):
    name = models.CharField(max_length=200)
    bio = models.CharField(max_length=200)
    photo = models.ImageField(upload_to='expert_photos/')
    
    def save(self, *args, **kwargs):
        if self.photo:
            self.photo = self.compress_image(self.photo)
        super().save(*args, **kwargs)
    
    def compress_image(self, image):
        img = Image.open(image)
        img = img.convert('RGB')
        
        if img.width > 400:
            ratio = 400 / img.width
            new_height = int(img.height * ratio)
            img = img.resize((400, new_height), Image.Resampling.LANCZOS)
        
        output = BytesIO()
        img.save(output, format='WebP', quality=85, optimize=True)
        output.seek(0)
        
        name = os.path.splitext(image.name)[0] + '.webp'
        return ContentFile(output.read(), name=name)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Эксперт"
        verbose_name_plural = "Эксперты"
        
        
class NewsCategory(models.Model):
   TYPE_CHOICES = [
       ('news', 'Новости'),
       ('guide', 'Агро-гид'),
       ('expert', 'Экспертный блог'),
   ]
   
   name = models.CharField(max_length=100)
   slug = models.SlugField()
   type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='news')
   
   def __str__(self):
       return self.name
   
   class Meta:
       verbose_name = "News Category"
       verbose_name_plural = "News Categories"


class News(models.Model):
    title = models.CharField(max_length=200)
    short_description = models.CharField(max_length=300)
    expert = models.ForeignKey(Expert, related_name='news', on_delete=models.CASCADE, blank=True, null=True)
    content = models.TextField()
    image = models.ImageField(upload_to='news_images/')
    category = models.ForeignKey(NewsCategory, related_name='news', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=True)
    is_expert_news = models.BooleanField(default=False, help_text="Отображать в разделе Блог экспертов")
    is_guide = models.BooleanField(default=False, help_text="Отображать в разделе Агро-гид")
    
    def save(self, *args, **kwargs):
        if self.image:
            self.image = self.compress_image(self.image)
        super().save(*args, **kwargs)
    
    def compress_image(self, image):
        img = Image.open(image)
        img = img.convert('RGB')
        
        if img.width > 1200:
            ratio = 1200 / img.width
            new_height = int(img.height * ratio)
            img = img.resize((1200, new_height), Image.Resampling.LANCZOS)
        
        output = BytesIO()
        img.save(output, format='WebP', quality=85, optimize=True)
        output.seek(0)
        
        name = os.path.splitext(image.name)[0] + '.webp'
        return ContentFile(output.read(), name=name)
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "News"
        verbose_name_plural = "News"
        ordering = ['-created_at']


class Newsletter(models.Model):
    email = models.EmailField()
    subscribed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.email
    
    class Meta:
        verbose_name = "Newsletter Subscription"
        verbose_name_plural = "Newsletter Subscriptions"
        

class ServiceProvider(models.Model):
    """Поставщик услуг (Агротехнопарк, Инжиниринг центр, Shakarim Lab)"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    is_active = models.BooleanField(default=True)
    head = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Руководитель поставщика услуг (будет отображаться в акте выполненных работ)")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Service Provider"
        verbose_name_plural = "Service Providers"
        ordering = ['name']


class ServiceCategory(models.Model):
    """Категории услуг (анализ крови, почвы, молока и т.д.)"""
    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    provider = models.ForeignKey(ServiceProvider, related_name='categories', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Service Category"
        verbose_name_plural = "Service Categories"
        ordering = ['order', 'name']
        unique_together = ['provider', 'slug']


class Service(models.Model):
    """Конкретная услуга"""
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    short_description = models.CharField(max_length=300)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='KZT')
    
    # Связи
    category = models.ForeignKey(ServiceCategory, related_name='services', on_delete=models.CASCADE)
    operator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Оператор услуги")
    
    # Дополнительные поля
    duration = models.CharField(max_length=100, blank=True, help_text="Время выполнения")
    
    # Мета информация
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            import uuid
            self.slug = f"{slugify(self.name)}-{str(uuid.uuid4())[:8]}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} - {self.price} {self.currency}"
    
    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Services"
        ordering = ['category', 'name']


class ServiceImage(models.Model):
    """Изображения для услуг"""
    service = models.ForeignKey(Service, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='service_images/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    
    def save(self, *args, **kwargs):
        if self.image:
            self.image = self.compress_image(self.image)
        super().save(*args, **kwargs)
    
    def compress_image(self, image):
        img = Image.open(image)
        img = img.convert('RGB')
        
        if img.width > 800:
            ratio = 800 / img.width
            new_height = int(img.height * ratio)
            img = img.resize((800, new_height), Image.Resampling.LANCZOS)
        
        output = BytesIO()
        img.save(output, format='WebP', quality=85, optimize=True)
        output.seek(0)
        
        name = os.path.splitext(image.name)[0] + '.webp'
        return ContentFile(output.read(), name=name)
    
    def __str__(self):
        return f"Image for {self.service.name}"
    
    class Meta:
        verbose_name = "Service Image"
        verbose_name_plural = "Service Images"
        ordering = ['order']


class ServiceRequest(models.Model):
    """Заявки на услуги - теперь поддерживает множественный выбор"""
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('confirmed', 'Подтверждена'),
        ('in_progress', 'В работе'),
        ('completed', 'Завершена'),
        ('cancelled', 'Отменена'),
    ]
    CLIENT_TYPE_CHOICES = [
        ('individual', 'Физическое лицо'),
        ('legal', 'Юридическое лицо'),
    ]

    services = models.ManyToManyField(Service, related_name='requests')
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='service_requests',
        verbose_name='Пользователь',
    )
    client_name = models.CharField(max_length=200)
    client_email = models.EmailField()
    client_phone = models.CharField(max_length=20)
    client_type = models.CharField(
        max_length=20,
        choices=CLIENT_TYPE_CHOICES,
        default='individual',
        verbose_name='Тип клиента',
    )
    company_bin = models.CharField(max_length=200, blank=True, verbose_name='БИН / компания')
    client_iin = models.CharField(max_length=12, blank=True, verbose_name='ИИН')
    message = models.TextField(blank=True)
    tracking_token = models.CharField(max_length=64, unique=True, blank=True)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.tracking_token:
            self.tracking_token = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)

    def get_request_number(self):
        return f'{self.created_at.year}-{self.id:04d}'

    def get_status_path(self):
        return reverse('service_request_status')

    def get_status_url(self):
        domain = getattr(settings, 'SITE_DOMAIN', '').rstrip('/')
        path = self.get_status_path()
        query = f'?number={self.get_request_number()}&token={self.tracking_token}'
        return f'{domain}{path}{query}'

    def calculate_total(self):
        """Подсчет общей стоимости заказа"""
        total = sum(service.price for service in self.services.all())
        self.total_price = total
        self.save()
        return total
    
    def get_services_list(self):
        """Получить список названий услуг"""
        return ", ".join([service.name for service in self.services.all()])
    
    def __str__(self):
        services_count = self.services.count()
        if services_count == 1:
            return f"Request for {self.services.first().name} by {self.client_name}"
        else:
            return f"Request for {services_count} services by {self.client_name}"
    
    class Meta:
        verbose_name = "Service Request"
        verbose_name_plural = "Service Requests"
        ordering = ['-created_at']

class CourseCategory(models.Model):
    """Категории курсов (Бизнес, Биология, Тамақ өнеркәсібі)"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = "Course Category"
        verbose_name_plural = "Course Categories"
        ordering = ['order', 'name']


class Course(models.Model):
    """Основная модель курса"""
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300)
    
    # Основная информация
    category = models.ForeignKey(CourseCategory, related_name='courses', on_delete=models.CASCADE)
    instructors = models.ManyToManyField('Instructor', related_name='taught_courses', blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.PositiveIntegerField(default=0, blank=True)
    
    # Характеристики курса
    duration_hours = models.PositiveIntegerField(help_text="Общее количество часов")
    hours_per_week = models.PositiveIntegerField(help_text="Часов в неделю")
    
    # Изображения
    main_image = models.ImageField(upload_to='course_images/')
    
    # Статусы и метки
    is_active = models.BooleanField(default=True)
    is_popular = models.BooleanField(default=False, help_text="ТОП курс")
    has_discount = models.BooleanField(default=False, help_text="Есть скидка")
    
    # Временные метки
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Course"
        verbose_name_plural = "Courses"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if self.main_image:
            self.main_image = self.compress_image(self.main_image)
        super().save(*args, **kwargs)
    
    def compress_image(self, image):
        img = Image.open(image)
        img = img.convert('RGB')
        
        if img.width > 1200:
            ratio = 1200 / img.width
            new_height = int(img.height * ratio)
            img = img.resize((1200, new_height), Image.Resampling.LANCZOS)
        
        output = BytesIO()
        img.save(output, format='WebP', quality=85, optimize=True)
        output.seek(0)
        
        name = os.path.splitext(image.name)[0] + '.webp'
        return ContentFile(output.read(), name=name)


class Instructor(models.Model):
    """Преподаватели курсов"""
    name = models.CharField(max_length=200)
    title = models.CharField(max_length=200, help_text="Должность/звание")
    bio = models.TextField()
    photo = models.ImageField(upload_to='instructor_photos/')
    
    class Meta:
        verbose_name = "Instructor"
        verbose_name_plural = "Instructors"
    
    def save(self, *args, **kwargs):
        if self.photo:
            self.photo = self.compress_image(self.photo)
        super().save(*args, **kwargs)
    
    def compress_image(self, image):
        img = Image.open(image)
        img = img.convert('RGB')
        
        if img.width > 400:
            ratio = 400 / img.width
            new_height = int(img.height * ratio)
            img = img.resize((400, new_height), Image.Resampling.LANCZOS)
        
        output = BytesIO()
        img.save(output, format='WebP', quality=85, optimize=True)
        output.seek(0)
        
        name = os.path.splitext(image.name)[0] + '.webp'
        return ContentFile(output.read(), name=name)


class CourseModule(models.Model):
    """Модули курса"""
    course = models.ForeignKey(Course, related_name='modules', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = "Course Module"
        verbose_name_plural = "Course Modules"
        ordering = ['order']
        
    def __str__(self):
        return f"{self.title}"


class CourseTopic(models.Model):
    """Темы в модулях"""
    module = models.ForeignKey(CourseModule, related_name='topics', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = "Course Topic"
        verbose_name_plural = "Course Topics"
        ordering = ['order']


class CourseReview(models.Model):
    """Отзывы о курсах"""
    course = models.ForeignKey(Course, related_name='reviews', on_delete=models.CASCADE)
    reviewer_name = models.CharField(max_length=200)
    reviewer_photo = models.ImageField(upload_to='reviewer_photos/', blank=True)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Course Review"
        verbose_name_plural = "Course Reviews"
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if self.reviewer_photo:
            self.reviewer_photo = self.compress_image(self.reviewer_photo)
        super().save(*args, **kwargs)
    
    def compress_image(self, image):
        img = Image.open(image)
        img = img.convert('RGB')
        
        if img.width > 300:
            ratio = 300 / img.width
            new_height = int(img.height * ratio)
            img = img.resize((300, new_height), Image.Resampling.LANCZOS)
        
        output = BytesIO()
        img.save(output, format='WebP', quality=85, optimize=True)
        output.seek(0)
        
        name = os.path.splitext(image.name)[0] + '.webp'
        return ContentFile(output.read(), name=name)


class CourseApplication(models.Model):
    """Заявки на курсы"""
    course = models.ForeignKey(Course, related_name='applications', on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    
    # Статус заявки
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('contacted', 'Связались'),
        ('enrolled', 'Записан'),
        ('rejected', 'Отклонен'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Course Application"
        verbose_name_plural = "Course Applications"
        ordering = ['-created_at']
        

class ProjectDirection(models.Model):
    """Направления проектов (Сельское хозяйство, Машиностроение, Биотехнология и т.д.)"""
    name = models.CharField(max_length=150, verbose_name="Название направления")
    slug = models.SlugField(unique=True, verbose_name="URL slug")
    is_active = models.BooleanField(default=True, verbose_name="Активно")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок сортировки")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Направление проекта"
        verbose_name_plural = "Направления проектов"
        ordering = ['order', 'name']


class ProjectStatus(models.Model):
    """Статусы проектов"""
    STATUS_CHOICES = [
        ('idea', 'Идея в разработке'),
        ('prototype', 'Прототип'),
        ('ready', 'Готов к внедрению'),
        ('implementing', 'Реализуется'),
        ('closed', 'Закрыт'),
    ]
    
    # Цвета для статусов (как в дизайне)
    COLOR_CHOICES = [
        ('#adb5bd', 'Серый'),  # Идея в разработке
        ('#ff9b10', 'Оранжевый'),  # Прототип
        ('#003C71', 'Синий'),  # Готов к внедрению
        ('#234287', 'Тёмно-синий'),  # Реализуется
        ('#c91d00', 'Красный'),  # Закрыт
    ]
    
    name = models.CharField(max_length=100, verbose_name="Название статуса")
    slug = models.SlugField(unique=True, verbose_name="URL slug")
    status_type = models.CharField(max_length=20, choices=STATUS_CHOICES, unique=True, verbose_name="Тип статуса")
    color = models.CharField(max_length=7, choices=COLOR_CHOICES, verbose_name="Цвет")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок сортировки")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Статус проекта"
        verbose_name_plural = "Статусы проектов"
        ordering = ['order']


class Project(models.Model):
    """Основная модель проекта"""
    title = models.CharField(max_length=250, verbose_name="Название проекта")
    slug = models.SlugField(unique=True, blank=True, verbose_name="URL slug")
    
    # Описания
    short_description = models.TextField(max_length=500, verbose_name="Краткое описание", 
                                       help_text="Описание для карточки в каталоге")
    description = models.TextField(verbose_name="Полное описание", 
                                 help_text="Подробное описание проекта")
    client_problem = models.TextField(
        blank=True,
        verbose_name="Проблема клиента",
        help_text="Каждый пункт с новой строки (для детальной страницы)",
    )
    our_solution = models.TextField(
        blank=True,
        verbose_name="Наше решение",
        help_text="Каждый пункт с новой строки (для детальной страницы)",
    )
    
    # Основная информация
    direction = models.ForeignKey(ProjectDirection, related_name='projects', on_delete=models.CASCADE, 
                                verbose_name="Направление")
    status = models.ForeignKey(ProjectStatus, related_name='projects', on_delete=models.CASCADE, 
                             verbose_name="Статус")
    
    # Финансовая информация
    investment_amount = models.DecimalField(max_digits=15, blank=True, null=True, decimal_places=2, verbose_name="Сумма инвестиций", 
                                          help_text="В тенге")
    currency = models.CharField(max_length=10, default='KZT', verbose_name="Валюта")
    
    # Временные рамки
    implementation_period = models.CharField(max_length=100, blank=True, null=True, verbose_name="Срок реализации", 
                                           help_text="Например: '3 года', '18 месяцев'")
    
    # Изображения
    main_image = models.ImageField(upload_to='project_images/', verbose_name="Основное изображение")
    
    # Дополнительные поля
    is_featured = models.BooleanField(default=False, verbose_name="Рекомендуемый проект")
    is_published = models.BooleanField(default=True, verbose_name="Опубликован")
    
    # Временные метки
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    def save(self, *args, **kwargs):
        # Автогенерация slug
        if not self.slug:
            from django.utils.text import slugify
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Project.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
            
        # Сжатие изображения
        if self.main_image:
            self.main_image = self.compress_image(self.main_image)
            
        super().save(*args, **kwargs)
    
    def compress_image(self, image):
        """Сжатие изображения"""
        img = Image.open(image)
        img = img.convert('RGB')

        if img.width > 800:
            ratio = 800 / img.width
            new_height = int(img.height * ratio)
            img = img.resize((800, new_height), Image.Resampling.LANCZOS)

        output = BytesIO()
        img.save(output, format='WebP', quality=85)
        output.seek(0)

        new_name = os.path.splitext(image.name)[0] + '.webp'
        return InMemoryUploadedFile(
            output,               # file
            'ImageField',         # field_name
            new_name,             # name
            'image/webp',         # content_type
            sys.getsizeof(output),# size
            None                  # charset
        )
    def get_formatted_investment(self):
        """Форматированная сумма инвестиций"""
        if not self.investment_amount:
            return "Не указано"
        
        if self.investment_amount >= 1000000000:
            return f"{self.investment_amount / 1000000000:.0f} млрд"
        elif self.investment_amount >= 1000000:
            return f"{self.investment_amount / 1000000:.0f} млн"
        else:
            return f"{self.investment_amount:,.0f}".replace(',', ' ')
    
    def get_problem_list(self):
        if not self.client_problem:
            return []
        return [line.strip() for line in self.client_problem.splitlines() if line.strip()]

    def get_solution_list(self):
        if not self.our_solution:
            return []
        return [line.strip() for line in self.our_solution.splitlines() if line.strip()]

    def get_absolute_url(self):
        return reverse('project', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"
        ordering = ['-created_at']


class ProjectImage(models.Model):
    """Дополнительные изображения проекта"""
    project = models.ForeignKey(Project, related_name='images', on_delete=models.CASCADE, 
                               verbose_name="Проект")
    image = models.ImageField(upload_to='project_gallery/', verbose_name="Изображение")
    caption = models.CharField(max_length=200, blank=True, verbose_name="Подпись к изображению")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    
    def save(self, *args, **kwargs):
        if self.image:
            self.image = self.compress_image(self.image)
        super().save(*args, **kwargs)
    
    def compress_image(self, image):
        """Сжатие изображения для галереи"""
        img = Image.open(image)
        img = img.convert('RGB')
        
        if img.width > 1200:
            ratio = 1200 / img.width
            new_height = int(img.height * ratio)
            img = img.resize((1200, new_height), Image.Resampling.LANCZOS)
        
        output = BytesIO()
        img.save(output, format='WebP', quality=90, optimize=True)
        output.seek(0)
        
        name = os.path.splitext(image.name)[0] + '.webp'
        return ContentFile(output.read(), name=name)
    
    def __str__(self):
        return f"Изображение для {self.project.title}"
    
    class Meta:
        verbose_name = "Изображение проекта"
        verbose_name_plural = "Изображения проектов"
        ordering = ['order']


class ProjectTeamMember(models.Model):
    """Участники команды проекта"""
    project = models.ForeignKey(Project, related_name='team_members', on_delete=models.CASCADE, 
                               verbose_name="Проект")
    name = models.CharField(max_length=200, verbose_name="ФИО")
    position = models.CharField(max_length=150, verbose_name="Должность")
    bio = models.TextField(blank=True, verbose_name="Биография")
    photo = models.ImageField(upload_to='team_photos/', blank=True, verbose_name="Фото")
    email = models.EmailField(blank=True, verbose_name="Email")
    
    def save(self, *args, **kwargs):
        if self.photo:
            self.photo = self.compress_image(self.photo)
        super().save(*args, **kwargs)
    
    def compress_image(self, image):
        """Сжатие фото участника"""
        img = Image.open(image)
        img = img.convert('RGB')
        
        if img.width > 300:
            ratio = 300 / img.width
            new_height = int(img.height * ratio)
            img = img.resize((300, new_height), Image.Resampling.LANCZOS)
        
        output = BytesIO()
        img.save(output, format='WebP', quality=85, optimize=True)
        output.seek(0)
        
        name = os.path.splitext(image.name)[0] + '.webp'
        return ContentFile(output.read(), name=name)
    
    def __str__(self):
        return f"{self.name} - {self.project.title}"
    
    class Meta:
        verbose_name = "Участник команды"
        verbose_name_plural = "Участники команды"


class ProjectInfoPanel(models.Model):
    """Информационные карточки / модальные окна на странице проекта."""
    DISPLAY_INLINE = 'inline'
    DISPLAY_MODAL = 'modal'
    DISPLAY_CHOICES = [
        (DISPLAY_INLINE, 'Карточка на странице'),
        (DISPLAY_MODAL, 'Модальное окно'),
    ]

    project = models.ForeignKey(
        Project,
        related_name='info_panels',
        on_delete=models.CASCADE,
        verbose_name='Проект',
    )
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    items = models.TextField(
        verbose_name='Пункты списка',
        help_text='Каждый пункт с новой строки',
    )
    display_mode = models.CharField(
        max_length=20,
        choices=DISPLAY_CHOICES,
        default=DISPLAY_INLINE,
        verbose_name='Тип отображения',
    )
    trigger_label = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Текст кнопки',
        help_text='Для модального окна. Если пусто — используется заголовок.',
    )
    accent_color = models.CharField(
        max_length=7,
        default='#c91d00',
        verbose_name='Цвет линии под заголовком',
    )
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')
    is_active = models.BooleanField(default=True, verbose_name='Активна')

    def get_items_list(self):
        if not self.items:
            return []
        return [line.strip() for line in self.items.splitlines() if line.strip()]

    def get_trigger_label(self):
        return self.trigger_label.strip() or self.title

    def __str__(self):
        return f'{self.title} ({self.project.title})'

    class Meta:
        verbose_name = 'Информационная панель'
        verbose_name_plural = 'Информационные панели'
        ordering = ['order', 'id']


class ProjectsCatalogSettings(models.Model):
    projects_hero_image = models.ImageField(
        upload_to='catalog_heroes/',
        blank=True,
        null=True,
        verbose_name="Картинка героя (Проекты)",
    )
    patents_hero_image = models.ImageField(
        upload_to='catalog_heroes/',
        blank=True,
        null=True,
        verbose_name="Картинка героя (Патенты / ИС)",
        help_text="Эта картинка показывается во вкладке «Интеллектуальная собственность»",
    )
    projects_title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Заголовок (Проекты)",
    )
    patents_title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Заголовок (Патенты / ИС)",
    )
    projects_lead = models.TextField(
        blank=True,
        verbose_name="Текст под заголовком (Проекты)",
        help_text="Если пусто — используется текст по умолчанию из переводов",
    )
    patents_lead = models.TextField(
        blank=True,
        verbose_name="Текст под заголовком (Патенты / ИС)",
        help_text="Если пусто — используется текст по умолчанию из переводов",
    )

    class Meta:
        verbose_name = "Настройки каталога проектов"
        verbose_name_plural = "Настройки каталога проектов"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Настройки каталога проектов"


class PatentType(models.Model):
    """Типы объектов ИС: патент, авторское свидетельство и т.д."""
    name = models.CharField(max_length=150, verbose_name="Название")
    slug = models.SlugField(unique=True, verbose_name="URL slug")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тип объекта ИС"
        verbose_name_plural = "Типы объектов ИС"
        ordering = ['order', 'name']


class Patent(models.Model):
    """Объект интеллектуальной собственности (патент и др.)."""
    title = models.CharField(max_length=300, verbose_name="Название")
    slug = models.SlugField(unique=True, blank=True, verbose_name="URL slug")
    patent_type = models.ForeignKey(
        PatentType,
        related_name='patents',
        on_delete=models.CASCADE,
        verbose_name="Тип",
    )
    registration_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Номер",
        help_text="Например: № 17350",
    )
    authors = models.CharField(
        max_length=300,
        blank=True,
        verbose_name="Авторы / правообладатель",
    )
    country = models.CharField(
        max_length=100,
        blank=True,
        default="Казахстан",
        verbose_name="Страна",
    )
    badge_letter = models.CharField(
        max_length=2,
        blank=True,
        verbose_name="Буква на иконке",
        help_text="Если иконка не загружена. Например: C, П",
    )
    icon = models.ImageField(
        upload_to='patent_icons/',
        blank=True,
        null=True,
        verbose_name="Иконка / логотип",
        help_text="Круглая картинка слева на карточке",
    )
    application_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="Дата заявки",
    )
    registration_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="Дата выдачи",
    )
    is_active_status = models.BooleanField(
        default=True,
        verbose_name="Действует",
        help_text="Показывать статус «Действует»",
    )
    short_description = models.TextField(
        max_length=500,
        blank=True,
        verbose_name="Краткое описание",
    )
    description = models.TextField(verbose_name="Полное описание", blank=True)
    benefits = models.TextField(
        blank=True,
        verbose_name="Что получает заказчик",
        help_text="Каждый пункт с новой строки",
    )
    document = models.FileField(
        upload_to='patent_docs/',
        blank=True,
        null=True,
        verbose_name="PDF / документ",
        help_text="Кнопка «Скачать PDF»",
    )
    read_url = models.URLField(
        blank=True,
        verbose_name="Ссылка «Читать патент»",
    )
    is_published = models.BooleanField(default=True, verbose_name="Опубликован")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            base_slug = slugify(self.title)
            slug = base_slug or 'patent'
            counter = 1
            while Patent.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_benefits_list(self):
        if not self.benefits:
            return []
        return [line.strip() for line in self.benefits.splitlines() if line.strip()]

    def get_letter(self):
        if self.badge_letter:
            return self.badge_letter.strip()[:1].upper()
        name = (self.patent_type.name if self.patent_type_id else '') or 'П'
        return name.strip()[:1].upper()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Патент / объект ИС"
        verbose_name_plural = "Патенты / объекты ИС"
        ordering = ['order', '-registration_date', '-created_at']


class Partner(models.Model):
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=50)
    manager_phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    slug = models.SlugField(unique=True)
    
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Партнер"
        verbose_name_plural = "Партнеры"

class Product(models.Model):
    name = models.CharField(max_length=200)
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    article_number = models.CharField(max_length=50)
    availability = models.CharField(max_length=100, default='Под заказ')
    delivery_time = models.CharField(max_length=100)
    image = models.ImageField(upload_to='products_images/')
    
    def save(self, *args, **kwargs):
        if self.image:
            self.image = self.compress_image(self.image)
        super().save(*args, **kwargs)
    
    def compress_image(self, image):
        img = Image.open(image)
        img = img.convert('RGB')
        
        if img.width > 800:
            ratio = 800 / img.width
            new_height = int(img.height * ratio)
            img = img.resize((800, new_height), Image.Resampling.LANCZOS)
        
        output = BytesIO()
        img.save(output, format='WebP', quality=85, optimize=True)
        output.seek(0)
        
        name = os.path.splitext(image.name)[0] + '.webp'
        return ContentFile(output.read(), name=name)
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Партнерский продукт"
        verbose_name_plural = "Партнерские продукты"


class AboutPageSettings(models.Model):
    hero_title = models.CharField(max_length=200, blank=True, verbose_name="Заголовок героя")
    hero_subtitle = models.TextField(blank=True, verbose_name="Подзаголовок героя")
    hero_image = models.ImageField(
        upload_to='page_heroes/',
        blank=True,
        null=True,
        verbose_name="Картинка героя",
    )

    card_company_title = models.CharField(max_length=150, blank=True, verbose_name="Карточка: О компании — заголовок")
    card_company_desc = models.TextField(blank=True, verbose_name="Карточка: О компании — описание")
    card_team_title = models.CharField(max_length=150, blank=True, verbose_name="Карточка: Команда — заголовок")
    card_team_desc = models.TextField(blank=True, verbose_name="Карточка: Команда — описание")
    card_lab_title = models.CharField(max_length=150, blank=True, verbose_name="Карточка: Лаборатория — заголовок")
    card_lab_desc = models.TextField(blank=True, verbose_name="Карточка: Лаборатория — описание")
    card_eng_title = models.CharField(max_length=150, blank=True, verbose_name="Карточка: Инжиниринг — заголовок")
    card_eng_desc = models.TextField(blank=True, verbose_name="Карточка: Инжиниринг — описание")

    cta_title = models.CharField(max_length=200, blank=True, verbose_name="CTA: заголовок")
    cta_propose = models.CharField(max_length=100, blank=True, verbose_name="CTA: кнопка «Предложить проект»")
    cta_partner = models.CharField(max_length=100, blank=True, verbose_name="CTA: кнопка «Стать партнером»")

    who_we_are_title = models.CharField(max_length=150, blank=True, verbose_name="Кто мы? — заголовок")
    who_we_are_p1 = models.TextField(blank=True, verbose_name="Кто мы? — абзац 1")
    who_we_are_p2 = models.TextField(blank=True, verbose_name="Кто мы? — абзац 2")
    who_we_are_p3 = models.TextField(blank=True, verbose_name="Кто мы? — абзац 3")
    who_we_are_p4 = models.TextField(blank=True, verbose_name="Кто мы? — абзац 4")

    purpose_title = models.CharField(max_length=150, blank=True, verbose_name="Наша цель — заголовок")
    purpose_p1 = models.TextField(blank=True, verbose_name="Наша цель — абзац 1")
    purpose_p2 = models.TextField(blank=True, verbose_name="Наша цель — абзац 2")
    purpose_p3 = models.TextField(blank=True, verbose_name="Наша цель — абзац 3")
    purpose_p4 = models.TextField(blank=True, verbose_name="Наша цель — абзац 4")

    mission_title = models.CharField(max_length=150, blank=True, verbose_name="Наша миссия — заголовок")
    mission_p1 = models.TextField(blank=True, verbose_name="Наша миссия — абзац 1")
    mission_p2 = models.TextField(blank=True, verbose_name="Наша миссия — абзац 2")
    mission_p3 = models.TextField(blank=True, verbose_name="Наша миссия — абзац 3")
    mission_p4 = models.TextField(blank=True, verbose_name="Наша миссия — абзац 4")

    team_cta_title = models.CharField(max_length=150, blank=True, verbose_name="Команда — заголовок")
    team_cta_description = models.TextField(blank=True, verbose_name="Команда — описание")
    team_cta_button = models.CharField(max_length=100, blank=True, verbose_name="Команда — кнопка")

    class Meta:
        verbose_name = "Настройки страницы «О нас»"
        verbose_name_plural = "Настройки страницы «О нас»"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Настройки страницы «О нас»"


class TeamDepartment(models.Model):
    """Отделы / подразделения на странице команды."""
    name = models.CharField(max_length=150, verbose_name="Название")
    slug = models.SlugField(unique=True, verbose_name="URL slug")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    def has_leadership(self):
        return any(m.is_leadership for m in self.members.all())

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Отдел команды"
        verbose_name_plural = "Отделы команды"
        ordering = ['order', 'name']


class TeamMember(models.Model):
    """Участник команды (фото, ФИО, должность)."""
    department = models.ForeignKey(
        TeamDepartment,
        related_name='members',
        on_delete=models.CASCADE,
        verbose_name="Отдел",
    )
    name = models.CharField(max_length=200, verbose_name="ФИО")
    position = models.CharField(max_length=250, verbose_name="Должность")
    photo = models.ImageField(
        upload_to='team_members/',
        blank=True,
        null=True,
        verbose_name="Фото",
        help_text="Загрузите фото сюда (приоритетнее ссылки и static)",
    )
    external_photo = models.URLField(
        blank=True,
        verbose_name="Ссылка на фото",
        help_text="Если фото на внешнем сайте",
    )
    static_photo = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Путь static",
        help_text="Например: images/team/agrotechnopark/Agrotechnopark2.webp",
    )
    email = models.EmailField(blank=True, verbose_name="Email")
    phone = models.CharField(max_length=50, blank=True, verbose_name="Телефон")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    is_leadership = models.BooleanField(
        default=False,
        verbose_name="Руководство",
        help_text="Крупная карточка с контактами",
    )

    def get_photo_url(self):
        if self.photo:
            return self.photo.url
        if self.external_photo:
            return self.external_photo
        if self.static_photo:
            from django.templatetags.static import static
            return static(self.static_photo)
        return ''

    def __str__(self):
        return f"{self.name} — {self.position}"

    class Meta:
        verbose_name = "Сотрудник (страница Команда)"
        verbose_name_plural = "Команда (сотрудники)"
        ordering = ['order', 'name']


class HomePageSettings(models.Model):
    brand = models.CharField(max_length=150, blank=True, verbose_name="Бренд")
    hero_title = models.CharField(max_length=200, blank=True, verbose_name="Заголовок героя")
    hero_subtitle = models.TextField(blank=True, verbose_name="Подзаголовок героя")
    hero_btn_primary = models.CharField(max_length=100, blank=True, verbose_name="Кнопка героя (основная)")
    hero_btn_secondary = models.CharField(max_length=100, blank=True, verbose_name="Кнопка героя (вторичная)")
    hero_image = models.ImageField(
        upload_to='page_heroes/', blank=True, null=True, verbose_name="Картинка героя",
    )

    services_title = models.CharField(max_length=200, blank=True, verbose_name="Заголовок блока услуг")

    advantages_title = models.CharField(max_length=200, blank=True, verbose_name="Заголовок преимуществ")
    advantage_1_title = models.CharField(max_length=150, blank=True, verbose_name="Преимущество 1 — заголовок")
    advantage_1_description = models.TextField(blank=True, verbose_name="Преимущество 1 — описание")
    advantage_2_title = models.CharField(max_length=150, blank=True, verbose_name="Преимущество 2 — заголовок")
    advantage_2_description = models.TextField(blank=True, verbose_name="Преимущество 2 — описание")
    advantage_3_title = models.CharField(max_length=150, blank=True, verbose_name="Преимущество 3 — заголовок")
    advantage_3_description = models.TextField(blank=True, verbose_name="Преимущество 3 — описание")
    advantage_4_title = models.CharField(max_length=150, blank=True, verbose_name="Преимущество 4 — заголовок")
    advantage_4_description = models.TextField(blank=True, verbose_name="Преимущество 4 — описание")

    news_title = models.CharField(max_length=150, blank=True, verbose_name="Заголовок новостей")
    news_read_more = models.CharField(max_length=100, blank=True, verbose_name="Кнопка «Читать подробнее»")
    news_all_btn = models.CharField(max_length=100, blank=True, verbose_name="Кнопка «Все новости»")

    cta_title = models.CharField(max_length=200, blank=True, verbose_name="CTA — заголовок")
    cta_description = models.TextField(blank=True, verbose_name="CTA — описание")
    cta_button = models.CharField(max_length=100, blank=True, verbose_name="CTA — кнопка")

    class Meta:
        verbose_name = "Настройки главной страницы"
        verbose_name_plural = "Настройки главной страницы"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Настройки главной страницы"


class HomeServiceSlide(models.Model):
    page = models.ForeignKey(
        HomePageSettings, related_name='slides', on_delete=models.CASCADE,
        verbose_name="Страница",
    )
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    image = models.ImageField(
        upload_to='home_slides/', blank=True, null=True, verbose_name="Картинка",
    )
    external_image = models.URLField(blank=True, verbose_name="Внешняя ссылка на картинку")
    link_url = models.CharField(max_length=255, default='/services/', verbose_name="Ссылка")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    def get_image_url(self):
        if self.image:
            return self.image.url
        if self.external_image:
            return self.external_image
        return ''

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Слайд услуг (главная)"
        verbose_name_plural = "Слайды услуг (главная)"
        ordering = ['order', 'id']


class LabPageSettings(models.Model):
    hero_title = models.CharField(max_length=200, blank=True, verbose_name="Заголовок героя")
    hero_subtitle = models.TextField(blank=True, verbose_name="Подзаголовок героя")
    hero_image = models.ImageField(
        upload_to='page_heroes/', blank=True, null=True, verbose_name="Картинка героя",
    )

    page_title = models.CharField(max_length=200, blank=True, verbose_name="Заголовок страницы")

    about_title = models.CharField(max_length=150, blank=True, verbose_name="О центре — заголовок")
    about_p1 = models.TextField(blank=True, verbose_name="О центре — абзац 1")
    about_p2 = models.TextField(blank=True, verbose_name="О центре — абзац 2")
    about_p3 = models.TextField(blank=True, verbose_name="О центре — абзац 3")
    about_image = models.ImageField(
        upload_to='lab_page/', blank=True, null=True, verbose_name="О центре — картинка",
    )

    services_title = models.CharField(max_length=200, blank=True, verbose_name="Заголовок услуг")
    labs_title = models.CharField(max_length=200, blank=True, verbose_name="Заголовок лабораторий")

    testing_title = models.CharField(max_length=200, blank=True, verbose_name="Испытательная лаб. — заголовок")
    testing_desc = models.TextField(blank=True, verbose_name="Испытательная лаб. — описание")
    testing_image = models.ImageField(
        upload_to='lab_page/', blank=True, null=True, verbose_name="Испытательная лаб. — картинка",
    )

    collective_title = models.CharField(max_length=200, blank=True, verbose_name="Коллективная лаб. — заголовок")
    collective_desc = models.TextField(blank=True, verbose_name="Коллективная лаб. — описание")
    collective_image = models.ImageField(
        upload_to='lab_page/', blank=True, null=True, verbose_name="Коллективная лаб. — картинка",
    )

    agro_title = models.CharField(max_length=200, blank=True, verbose_name="Агротехнопарк — заголовок")
    agro_p1 = models.TextField(blank=True, verbose_name="Агротехнопарк — абзац 1")
    agro_p2 = models.TextField(blank=True, verbose_name="Агротехнопарк — абзац 2")

    food_title = models.CharField(max_length=200, blank=True, verbose_name="Пищевая безопасность — заголовок")
    food_desc = models.TextField(blank=True, verbose_name="Пищевая безопасность — описание")
    food_image = models.ImageField(
        upload_to='lab_page/', blank=True, null=True, verbose_name="Пищевая безопасность — картинка",
    )

    vet_title = models.CharField(max_length=200, blank=True, verbose_name="Ветклиника — заголовок")
    vet_desc = models.TextField(blank=True, verbose_name="Ветклиника — описание")
    vet_image = models.ImageField(
        upload_to='lab_page/', blank=True, null=True, verbose_name="Ветклиника — картинка",
    )

    milk_title = models.CharField(max_length=200, blank=True, verbose_name="Анализ молока — заголовок")
    milk_desc = models.TextField(blank=True, verbose_name="Анализ молока — описание")
    milk_image = models.ImageField(
        upload_to='lab_page/', blank=True, null=True, verbose_name="Анализ молока — картинка",
    )

    contact_title = models.CharField(max_length=200, blank=True, verbose_name="Контакты — заголовок")
    address_label = models.CharField(max_length=100, blank=True, verbose_name="Адрес — метка")
    address_text = models.TextField(blank=True, verbose_name="Адрес — текст")
    contacts_label = models.CharField(max_length=100, blank=True, verbose_name="Контакты — метка")
    email_text = models.CharField(max_length=200, blank=True, verbose_name="Email")
    phone_text = models.CharField(max_length=200, blank=True, verbose_name="Телефон")

    class Meta:
        verbose_name = "Настройки страницы Lab"
        verbose_name_plural = "Настройки страницы Lab"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Настройки страницы Lab"


class LabServiceCard(models.Model):
    page = models.ForeignKey(
        LabPageSettings, related_name='service_cards', on_delete=models.CASCADE,
        verbose_name="Страница",
    )
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    icon_class = models.CharField(max_length=100, default='fas fa-flask', verbose_name="CSS-класс иконки")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Карточка услуги (Lab)"
        verbose_name_plural = "Карточки услуг (Lab)"
        ordering = ['order', 'id']


class EngineeringPageSettings(models.Model):
    hero_title = models.CharField(max_length=200, blank=True, verbose_name="Заголовок героя")
    hero_subtitle = models.TextField(blank=True, verbose_name="Подзаголовок героя")
    hero_image = models.ImageField(
        upload_to='page_heroes/', blank=True, null=True, verbose_name="Картинка героя",
    )

    page_title = models.CharField(max_length=200, blank=True, verbose_name="Заголовок страницы")

    about_title = models.CharField(max_length=150, blank=True, verbose_name="О центре — заголовок")
    about_p1 = models.TextField(blank=True, verbose_name="О центре — абзац 1")
    about_p2 = models.TextField(blank=True, verbose_name="О центре — абзац 2")
    about_p3 = models.TextField(blank=True, verbose_name="О центре — абзац 3")
    about_image = models.ImageField(
        upload_to='eng_page/', blank=True, null=True, verbose_name="О центре — картинка",
    )

    services_title = models.CharField(max_length=200, blank=True, verbose_name="Заголовок услуг")
    labs_title = models.CharField(max_length=200, blank=True, verbose_name="Заголовок лабораторий")

    plasma_title = models.CharField(max_length=200, blank=True, verbose_name="Плазменная лаб. — заголовок")
    plasma_desc = models.TextField(blank=True, verbose_name="Плазменная лаб. — описание")
    plasma_image = models.ImageField(
        upload_to='eng_page/', blank=True, null=True, verbose_name="Плазменная лаб. — картинка",
    )

    materials_title = models.CharField(max_length=200, blank=True, verbose_name="Материаловедение — заголовок")
    materials_desc = models.TextField(blank=True, verbose_name="Материаловедение — описание")
    materials_image = models.ImageField(
        upload_to='eng_page/', blank=True, null=True, verbose_name="Материаловедение — картинка",
    )

    contact_title = models.CharField(max_length=200, blank=True, verbose_name="Контакты — заголовок")
    address_label = models.CharField(max_length=100, blank=True, verbose_name="Адрес — метка")
    address_text = models.TextField(blank=True, verbose_name="Адрес — текст")
    contacts_label = models.CharField(max_length=100, blank=True, verbose_name="Контакты — метка")
    email_text = models.CharField(max_length=200, blank=True, verbose_name="Email")
    phone_text = models.CharField(max_length=200, blank=True, verbose_name="Телефон")

    class Meta:
        verbose_name = "Настройки страницы Инжиниринг"
        verbose_name_plural = "Настройки страницы Инжиниринг"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Настройки страницы Инжиниринг"


class EngineeringServiceCard(models.Model):
    page = models.ForeignKey(
        EngineeringPageSettings, related_name='service_cards', on_delete=models.CASCADE,
        verbose_name="Страница",
    )
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    icon_class = models.CharField(max_length=100, default='fas fa-flask', verbose_name="CSS-класс иконки")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Карточка услуги (Инжиниринг)"
        verbose_name_plural = "Карточки услуг (Инжиниринг)"
        ordering = ['order', 'id']


class PartnersPageSettings(models.Model):
    hero_title = models.CharField(max_length=200, blank=True, verbose_name="Заголовок героя")
    hero_subtitle = models.TextField(blank=True, verbose_name="Подзаголовок героя")
    hero_image = models.ImageField(
        upload_to='page_heroes/', blank=True, null=True, verbose_name="Картинка героя",
    )

    card_about_title = models.CharField(max_length=150, blank=True, verbose_name="Карточка «О партнёрах» — заголовок")
    card_about_desc = models.TextField(blank=True, verbose_name="Карточка «О партнёрах» — описание")
    card_shop_title = models.CharField(max_length=150, blank=True, verbose_name="Карточка «Магазин» — заголовок")
    card_shop_desc = models.TextField(blank=True, verbose_name="Карточка «Магазин» — описание")

    cta_title = models.CharField(max_length=200, blank=True, verbose_name="CTA — заголовок")
    cta_propose = models.CharField(max_length=100, blank=True, verbose_name="CTA — кнопка «Предложить»")
    cta_shop = models.CharField(max_length=100, blank=True, verbose_name="CTA — кнопка «Магазин»")

    content_title = models.CharField(max_length=200, blank=True, verbose_name="Контент — заголовок")
    content_p1 = models.TextField(blank=True, verbose_name="Контент — абзац 1")
    content_p2 = models.TextField(blank=True, verbose_name="Контент — абзац 2")

    class Meta:
        verbose_name = "Настройки страницы Партнёры"
        verbose_name_plural = "Настройки страницы Партнёры"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Настройки страницы Партнёры"


class ServicesPageSettings(models.Model):
    heading = models.CharField(max_length=200, blank=True, verbose_name="Заголовок")
    lead = models.TextField(blank=True, verbose_name="Подзаголовок")
    hero_image = models.ImageField(
        upload_to='page_heroes/', blank=True, null=True, verbose_name="Картинка героя",
    )
    btn_price = models.CharField(max_length=100, blank=True, verbose_name="Кнопка прайса")
    btn_catalog = models.CharField(max_length=100, blank=True, verbose_name="Кнопка каталога")

    class Meta:
        verbose_name = "Настройки страницы Услуги"
        verbose_name_plural = "Настройки страницы Услуги"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Настройки страницы Услуги"


class CoursesPageSettings(models.Model):
    heading = models.CharField(max_length=200, blank=True, verbose_name="Заголовок")
    lead = models.TextField(blank=True, verbose_name="Подзаголовок")
    category_lead = models.TextField(blank=True, verbose_name="Подзаголовок категории")
    hero_image = models.ImageField(
        upload_to='page_heroes/', blank=True, null=True, verbose_name="Картинка героя",
    )
    btn_price = models.CharField(max_length=100, blank=True, verbose_name="Кнопка прайса")
    btn_catalog = models.CharField(max_length=100, blank=True, verbose_name="Кнопка каталога")

    class Meta:
        verbose_name = "Настройки страницы Курсы"
        verbose_name_plural = "Настройки страницы Курсы"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Настройки страницы Курсы"


class TeamPageSettings(models.Model):
    title = models.CharField(max_length=200, blank=True, verbose_name="Заголовок")
    subtitle = models.TextField(blank=True, verbose_name="Подзаголовок")
    hero_image = models.ImageField(
        upload_to='page_heroes/', blank=True, null=True, verbose_name="Картинка героя",
    )

    class Meta:
        verbose_name = "Настройки страницы Команда"
        verbose_name_plural = "Настройки страницы Команда"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Настройки страницы Команда"


class NewsPageSettings(models.Model):
    title = models.CharField(max_length=200, blank=True, verbose_name="Заголовок")
    description = models.TextField(blank=True, verbose_name="Описание")
    subscribe_button = models.CharField(max_length=100, blank=True, verbose_name="Кнопка подписки")
    hero_image = models.ImageField(
        upload_to='page_heroes/', blank=True, null=True, verbose_name="Картинка героя",
    )

    class Meta:
        verbose_name = "Настройки страницы Новости"
        verbose_name_plural = "Настройки страницы Новости"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Настройки страницы Новости"
