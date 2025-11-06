# declaratives/urls.py
from django.urls import path, include, re_path
from django.views.generic import RedirectView, TemplateView
from django.conf import settings
import sys

from . import views
from . import component_views


app_name = "declaratives"

# ======================================================
# ✅ Component API URL patterns — logically grouped
# ======================================================
component_patterns = [

    # --------------------------------------------------
    # TABLE COMPONENTS
    # --------------------------------------------------
    path("table/data/", component_views.paginated_table_api, name="paginated_table_data"),
    path("table/export/<str:format>/", component_views.export_table_data, name="export_table_data"),
    path("table/bulk-delete/", component_views.bulk_delete_users, name="bulk_delete_users"),

    # --------------------------------------------------
    # FORMS
    # --------------------------------------------------
    path("forms/profile/", component_views.dynamic_form_handler, name="dynamic_form_handler"),
    path("forms/task/", component_views.dynamic_form_handler, name="task_form_handler"),
    path("forms/validate-field/", component_views.validate_field, name="validate_field"),
    path("forms/char-counter/", component_views.char_counter, name="char_counter"),
    path("forms/cities/", component_views.get_cities, name="get_cities"),
    path("forms/tag-suggestions/", component_views.tag_suggestions, name="tag_suggestions"),
    path("forms/recent-tasks/", component_views.recent_tasks, name="recent_tasks"),
    path("forms/conditional-fields/", component_views.conditional_fields, name="conditional_fields"),
    path("forms/color-preview/", component_views.color_preview, name="color_preview"),
    path("forms/autosave/", component_views.autosave_notes, name="autosave_notes"),

    # --------------------------------------------------
    # CHARTS & VISUALIZATIONS
    # --------------------------------------------------
    path("charts/<str:chart_type>/", component_views.chart_data_api, name="chart_data_api"),
    path("charts/live-stats/", component_views.live_stats, name="live_stats"),
    path("charts/interactive/", component_views.interactive_chart, name="interactive_chart"),
    path("charts/export-data/", component_views.export_chart_data, name="export_chart_data"),

    # Performance & Real-time Charts
    path("api/charts/<str:chart_type>/", component_views.chart_data_api, name="chart_data_api_v2"),
    path("api/charts/live-stream/", component_views.live_chart_stream, name="live_chart_stream"),
    path("components/chart-performance/", component_views.chart_performance_test, name="chart_performance_test"),

    # --------------------------------------------------
    # REAL-TIME (SSE / WebSocket Simulation)
    # --------------------------------------------------
    path("realtime/activity/", component_views.live_activity, name="live_activity"),
    path("realtime/notifications/", component_views.live_notifications, name="live_notifications"),
    path("realtime/notification-count/", component_views.notification_count, name="notification_count"),
    path("realtime/test-notification/", component_views.test_notification, name="test_notification"),
    path("realtime/messages/", component_views.live_messages, name="live_messages"),
    path("realtime/send-message/", component_views.send_message, name="send_message"),
    path("realtime/system-status/", component_views.system_status, name="system_status"),
    path("realtime/online-count/", component_views.online_count, name="online_count"),
    path("realtime/sessions-count/", component_views.sessions_count, name="sessions_count"),
    path("realtime/uptime/", component_views.server_uptime, name="server_uptime"),
    path("realtime/clear-feed/", component_views.clear_activity_feed, name="clear_activity_feed"),

    # --------------------------------------------------
    # NEW DYNAMIC / DATABASE-DRIVEN COMPONENT APIs
    # --------------------------------------------------
    path("api/system-performance/", views.api_system_performance, name="api_system_performance"),
    path("api/sales-by-region/", views.api_sales_by_region, name="api_sales_by_region"),
    path("api/activity-feed/", views.api_activity_feed, name="api_activity_feed"),
    path("api/gallery/", views.api_gallery_items, name="api_gallery_items"),
    path("api/file-manager/", views.api_file_manager, name="api_file_manager"),
    path("api/dynamic-tabs/", views.api_dynamic_tabs, name="api_dynamic_tabs"),
    path("api/drag-drop/", views.api_drag_drop_items, name="api_drag_drop_items"),

    # --------------------------------------------------
    # UI COMPONENTS
    # --------------------------------------------------
    path("ui/search-dropdown/", component_views.search_dropdown, name="search_dropdown"),
    path("ui/tags-dropdown/", component_views.tags_dropdown, name="tags_dropdown"),
    path("ui/bulk-action/", component_views.bulk_action, name="bulk_action"),
    path("ui/tab-content/", component_views.tab_content, name="tab_content"),
    path("ui/accordion-content/", component_views.accordion_content, name="accordion_content"),
    path("ui/toast/", component_views.show_toast, name="show_toast"),
    path("ui/alert/", component_views.show_alert, name="show_alert"),
    path("ui/carousel/", component_views.image_carousel, name="image_carousel"),

    # --------------------------------------------------
    # MODALS
    # --------------------------------------------------
    path("modal/content/", component_views.modal_content_api, name="modal_content"),
    path("modal/user/<int:user_id>/", component_views.user_modal, name="user_modal"),
    path("modal/confirm/<str:action>/", component_views.confirmation_modal, name="confirmation_modal"),

    # --------------------------------------------------
    # FILE OPERATIONS
    # --------------------------------------------------
    path("files/upload/", component_views.file_upload_handler, name="file_upload"),
    path("files/browse/", component_views.file_browser, name="file_browser"),
    path("files/<int:file_id>/download/", component_views.file_download, name="file_download"),
    path("files/<int:file_id>/delete/", component_views.file_delete, name="file_delete"),
    path("files/progress/<str:upload_id>/", component_views.upload_progress, name="upload_progress"),

    # --------------------------------------------------
    # ADVANCED PATTERNS
    # --------------------------------------------------
    path("advanced/infinite-scroll/", component_views.infinite_scroll_data, name="infinite_scroll"),
    path("advanced/sortable-list/", component_views.sortable_list_data, name="sortable_list"),
    path("advanced/wizard/<int:step>/", component_views.wizard_step, name="wizard_step"),
    path("advanced/drag-drop/reorder/", component_views.reorder_items, name="reorder_items"),
]


# ======================================================
# ✅ Core Declaratives URLs (Showcases + APIs)
# ======================================================
urlpatterns = [

    # --------------------------------------------------
    # HyperX Showcase Pages
    # --------------------------------------------------
    path("", views.showcase_home, name="showcase_home"),
    path("components/", views.component_gallery, name="component_gallery"),
    path("playground/", views.hyperx_playground, name="hyperx_playground"),

    # --------------------------------------------------
    # Legacy Demos (for backward compatibility)
    # --------------------------------------------------
    path("search/", views.live_search_tasks, name="live_search"),
    path("websocket-demo/", views.websocket_demo, name="websocket_demo"),
    path("form-validation/", views.form_validation_demo, name="form_validation"),

    # --------------------------------------------------
    # Component API Inclusion
    # --------------------------------------------------
    path("component/", include(component_patterns)),
    re_path(r"^api/v1/components/", include(component_patterns)),

    # --------------------------------------------------
    # Shortcuts for quick redirects
    # --------------------------------------------------
    path("table/", RedirectView.as_view(pattern_name="declaratives:component_gallery", permanent=False)),
    path("forms/", RedirectView.as_view(pattern_name="declaratives:component_gallery", permanent=False)),
    path("charts/", RedirectView.as_view(pattern_name="declaratives:component_gallery", permanent=False)),

    # --------------------------------------------------
    # Legacy HTMX / Task APIs
    # --------------------------------------------------
    path("api/tasks/quick-add/", views.quick_add_task, name="quick_add_task"),
    path("api/tasks/<int:task_id>/toggle/", views.toggle_task, name="toggle_task"),
    path("api/tasks/<int:task_id>/delete/", views.delete_task, name="delete_task"),
    path("api/tasks/<int:task_id>/comments/", views.lazy_load_comments, name="lazy_load_comments"),
    path("api/tasks/<int:task_id>/comments/add/", views.add_comment, name="add_comment"),

    # --------------------------------------------------
    # Live Metrics + Validation
    # --------------------------------------------------
    path("api/metrics/", views.live_metrics_api, name="live_metrics"),
    path("api/validate/task-title/", views.validate_task_title, name="validate_task_title"),

    # --------------------------------------------------
    # Experimental & Dynamic APIs
    # --------------------------------------------------
    re_path(r"^dynamic/(?P<component_type>\w+)/(?P<component_id>\w+)/$", component_views.dynamic_component_loader, name="dynamic_component"),
    re_path(r"^rest/(?P<resource>\w+)/$", component_views.rest_api_handler, name="rest_api_list"),
    re_path(r"^rest/(?P<resource>\w+)/(?P<resource_id>\d+)/$", component_views.rest_api_handler, name="rest_api_detail"),
    path("htmx-files/", views.list_htmx_files, name="list_htmx_files"),

    # --------------------------------------------------
    # SSE Streams (Server-Sent Events)
    # --------------------------------------------------
    path("stream/<str:channel>/", component_views.sse_stream, name="sse_stream"),
    path("stream/<str:channel>/subscribe/", component_views.sse_subscribe, name="sse_subscribe"),

    # --------------------------------------------------
    # HyperX Pattern Testing Routes
    # --------------------------------------------------
    path("test/polling/<int:interval>/", component_views.test_polling, name="test_polling"),
    path("test/debounce/<int:delay>/", component_views.test_debounce, name="test_debounce"),
    path("test/infinite-scroll/<int:page>/", component_views.test_infinite_scroll, name="test_infinite_scroll"),

    # --------------------------------------------------
    # System Health & Debug
    # --------------------------------------------------
    path("health/", component_views.component_health, name="component_health"),
    path("status/<str:component>/", component_views.component_status, name="component_status"),
    path("debug/htmx/", TemplateView.as_view(template_name="declaratives/debug/htmx_debug.html"), name="htmx_debug"),
    path("debug/components/", component_views.component_debug, name="component_debug"),
    path("debug/performance/", component_views.performance_debug, name="performance_debug"),

    # --------------------------------------------------
    # Catch-All & Variants
    # --------------------------------------------------
    re_path(r"^component-(?P<variant>\w+)/$", component_views.component_variant_handler, name="component_variant"),
]


# ======================================================
# 🧩 DEBUG MODE ONLY ROUTES
# ======================================================
if getattr(settings, "DEBUG", False):
    urlpatterns += [
        path("_dev/reset-data/", views.reset_demo_data, name="reset_demo_data"),
        path("_dev/generate-data/", views.generate_demo_data, name="gene_
