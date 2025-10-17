import os
import sys
from PIL import Image
from io import BytesIO
from django.db import models
from django.urls import reverse
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
    
    # Изменяем связь с услугами на ManyToMany
    services = models.ManyToManyField(Service, related_name='requests')
    
    # Клиентская информация
    client_name = models.CharField(max_length=200)
    client_email = models.EmailField()
    client_phone = models.CharField(max_length=20)
    message = models.TextField(blank=True)
    
    # Добавляем общую сумму
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Статус и временные метки
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
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
        ('#4caf50', 'Зеленый'),  # Готов к внедрению
        ('#234287', 'Синий'),  # Реализуется
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