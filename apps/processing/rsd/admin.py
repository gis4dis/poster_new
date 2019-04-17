from apps.common.actions import stream_as_csv_action
from apps.common.list_filter import DateRangeRangeFilter
from .models import EventCategory, EventObservation, AdminUnit, CategoryCustomGroup, NumberOfEventsObservation
from django.contrib import admin


class EventObservationAdmin(admin.ModelAdmin):
    list_display = ['Event_Category_name','Event_Category_group','first_admin_unit','admin_units','phenomenon_time_from','phenomenon_time_duration', 'time_slots']
    fields = ['Event_Category_name','Event_Category_group','first_admin_unit','admin_units','phenomenon_time_from','phenomenon_time_duration', 'created_at', 'updated_at']
    readonly_fields = list_display
    list_filter = ['category__group',DateRangeRangeFilter, ('time_slots', admin.RelatedOnlyFieldListFilter)]
    

    def Event_Category_name(self, event):
        return event.category.name
    def Event_Category_group(self, event):
        return event.category.group
    def first_admin_unit(self, event):
        return event.result.admin_units.first().name
    def admin_units(self, event):
        return len(event.result.admin_units.all())


class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ['name','group', 'id_by_provider','custom_group']
    fields = ['name','group','id_by_provider','custom_group']
    readonly_fields = ['name','group','id_by_provider']
    list_filter = ['group']


class AdminUnitAdmin(admin.ModelAdmin):
    list_display = ['name', 'id_by_provider','level']
    fields = ['name','id_by_provider','level']
    readonly_fields = list_display
    list_filter = ['level']


class CategoryCustomGroupAdmin(admin.ModelAdmin):
    list_display = ['name_id', 'name']
    fields = ['name_id','name']


class NumberOfEventsObservationAdmin(admin.ModelAdmin):
    list_display = ['feature_of_interest', 'category_custom_group_name','phenomenon_time_from','phenomenon_time_duration','result', 'time_slots']
    fields = ['feature_of_interest','category_custom_group','phenomenon_time_from','phenomenon_time_duration','result', 'created_at', 'updated_at']
    readonly_fields = list_display

    def category_custom_group_name(self, event):
        return event.category_custom_group.name


admin.site.register(EventObservation, EventObservationAdmin)
admin.site.register(EventCategory, EventCategoryAdmin)
admin.site.register(AdminUnit, AdminUnitAdmin)
admin.site.register(CategoryCustomGroup, CategoryCustomGroupAdmin)
admin.site.register(NumberOfEventsObservation, NumberOfEventsObservationAdmin)