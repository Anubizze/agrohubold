from modeltranslation.translator import TranslationOptions, register
from .models import *


@register(Thing)
class ThingTranslationOptions(TranslationOptions):
    fields = ('name', 'description')
    
@register(Expert)
class ExpertTranslationOptions(TranslationOptions):
   fields = ('name', 'bio')

@register(NewsCategory)
class NewsCategoryTranslationOptions(TranslationOptions):
   fields = ('name',)


@register(News)
class NewsTranslationOptions(TranslationOptions):
   fields = ('title', 'content', 'short_description')


@register(Newsletter)
class NewsletterTranslationOptions(TranslationOptions):
   fields = ()
   
   
@register(ServiceProvider)
class ServiceProviderTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(ServiceCategory)
class ServiceCategoryTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Service)
class ServiceTranslationOptions(TranslationOptions):
    fields = ('name', 'description', 'short_description', 'duration')
    

@register(CourseCategory)
class CourseCategoryTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Course)
class CourseTranslationOptions(TranslationOptions):
    fields = ('title', 'description', 'short_description')


@register(Instructor)
class InstructorTranslationOptions(TranslationOptions):
    fields = ('name', 'title', 'bio')


@register(CourseModule)
class CourseModuleTranslationOptions(TranslationOptions):
    fields = ('title',)


@register(CourseTopic)
class CourseTopicTranslationOptions(TranslationOptions):
    fields = ('title',)


@register(CourseReview)
class CourseReviewTranslationOptions(TranslationOptions):
    fields = ('reviewer_name', 'comment')
    

@register(ProjectDirection)
class ProjectDirectionTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(ProjectStatus)
class ProjectStatusTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Project)
class ProjectTranslationOptions(TranslationOptions):
    fields = ('title', 'short_description', 'description', 'implementation_period')


@register(ProjectImage)
class ProjectImageTranslationOptions(TranslationOptions):
    fields = ('caption',)


@register(ProjectTeamMember)
class ProjectTeamMemberTranslationOptions(TranslationOptions):
    fields = ('name', 'position', 'bio')


@register(ProjectInfoPanel)
class ProjectInfoPanelTranslationOptions(TranslationOptions):
    fields = ('title', 'items', 'trigger_label')


@register(ProjectsCatalogSettings)
class ProjectsCatalogSettingsTranslationOptions(TranslationOptions):
    fields = ('projects_title', 'patents_title', 'projects_lead', 'patents_lead')


@register(PatentType)
class PatentTypeTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Patent)
class PatentTranslationOptions(TranslationOptions):
    fields = ('title', 'short_description', 'description', 'benefits')

    
@register(Partner)
class PartnerTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = ('name', 'availability', 'delivery_time')


@register(TeamDepartment)
class TeamDepartmentTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(TeamMember)
class TeamMemberTranslationOptions(TranslationOptions):
    fields = ('name', 'position')


@register(AboutPageSettings)
class AboutPageSettingsTranslationOptions(TranslationOptions):
    fields = (
        'hero_title', 'hero_subtitle',
        'card_company_title', 'card_company_desc',
        'card_team_title', 'card_team_desc',
        'card_lab_title', 'card_lab_desc',
        'card_eng_title', 'card_eng_desc',
        'cta_title', 'cta_propose', 'cta_partner',
        'who_we_are_title', 'who_we_are_p1', 'who_we_are_p2', 'who_we_are_p3', 'who_we_are_p4',
        'purpose_title', 'purpose_p1', 'purpose_p2', 'purpose_p3', 'purpose_p4',
        'mission_title', 'mission_p1', 'mission_p2', 'mission_p3', 'mission_p4',
        'team_cta_title', 'team_cta_description', 'team_cta_button',
    )


@register(HomePageSettings)
class HomePageSettingsTranslationOptions(TranslationOptions):
    fields = (
        'brand', 'hero_title', 'hero_subtitle', 'hero_btn_primary', 'hero_btn_secondary',
        'services_title',
        'advantages_title',
        'advantage_1_title', 'advantage_1_description',
        'advantage_2_title', 'advantage_2_description',
        'advantage_3_title', 'advantage_3_description',
        'advantage_4_title', 'advantage_4_description',
        'news_title', 'news_read_more', 'news_all_btn',
        'cta_title', 'cta_description', 'cta_button',
    )


@register(HomeServiceSlide)
class HomeServiceSlideTranslationOptions(TranslationOptions):
    fields = ('title',)


@register(LabPageSettings)
class LabPageSettingsTranslationOptions(TranslationOptions):
    fields = (
        'hero_title', 'hero_subtitle', 'page_title',
        'about_title', 'about_p1', 'about_p2', 'about_p3',
        'services_title', 'labs_title',
        'testing_title', 'testing_desc',
        'collective_title', 'collective_desc',
        'agro_title', 'agro_p1', 'agro_p2',
        'food_title', 'food_desc',
        'vet_title', 'vet_desc',
        'milk_title', 'milk_desc',
        'contact_title', 'address_label', 'address_text',
        'contacts_label', 'email_text', 'phone_text',
    )


@register(LabServiceCard)
class LabServiceCardTranslationOptions(TranslationOptions):
    fields = ('title',)


@register(EngineeringPageSettings)
class EngineeringPageSettingsTranslationOptions(TranslationOptions):
    fields = (
        'hero_title', 'hero_subtitle', 'page_title',
        'about_title', 'about_p1', 'about_p2', 'about_p3',
        'services_title', 'labs_title',
        'plasma_title', 'plasma_desc',
        'materials_title', 'materials_desc',
        'contact_title', 'address_label', 'address_text',
        'contacts_label', 'email_text', 'phone_text',
    )


@register(EngineeringServiceCard)
class EngineeringServiceCardTranslationOptions(TranslationOptions):
    fields = ('title',)


@register(PartnersPageSettings)
class PartnersPageSettingsTranslationOptions(TranslationOptions):
    fields = (
        'hero_title', 'hero_subtitle',
        'card_about_title', 'card_about_desc',
        'card_shop_title', 'card_shop_desc',
        'cta_title', 'cta_propose', 'cta_shop',
        'content_title', 'content_p1', 'content_p2',
    )


@register(ServicesPageSettings)
class ServicesPageSettingsTranslationOptions(TranslationOptions):
    fields = ('heading', 'lead', 'btn_price', 'btn_catalog')


@register(CoursesPageSettings)
class CoursesPageSettingsTranslationOptions(TranslationOptions):
    fields = ('heading', 'lead', 'category_lead', 'btn_price', 'btn_catalog')


@register(TeamPageSettings)
class TeamPageSettingsTranslationOptions(TranslationOptions):
    fields = ('title', 'subtitle')


@register(NewsPageSettings)
class NewsPageSettingsTranslationOptions(TranslationOptions):
    fields = ('title', 'description', 'subscribe_button')
