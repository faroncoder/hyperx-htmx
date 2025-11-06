Template Tags (18 total):

htmx_headers() - Generate HTMX HTML headers
htmx_csrf_headers() - CSRF headers for HTMX requests
htmx_config() - HTMX configuration as JSON
htmx_boost_links() - Enable HTMX boost for links
htmx_swap_oob() - Out-of-band swap directive
htmx_trigger() - Generate trigger events
htmx_loading_indicator() - Inclusion tag for loading indicators
htmx_polling() - Polling attributes
htmx_confirm() - Confirmation dialogs
htmx_delete_confirm() - Delete confirmation
htmx_form_submit() - Form submission attributes
htmx_lazy_load() - Lazy loading attributes
htmx_url() - URL generation with context
htmx_websocket() - WebSocket connection
htmx_redirect() - Redirect header
htmx_refresh() - Refresh directive
htmx_version() - Version info
htmx_debug() - Debug enabling
Filters (3 total):

htmx_target - Convert to HTMX target selector
htmx_indicator - Convert to indicator format
is_htmx - Check if request is from HTMX
4. Usage in Templates:
Now you can use these in your Django templates like:


{% load htmx_tags %}{% htmx_headers %}{% htmx_config timeout=15000 %}<div {% htmx_trigger "click" "#target" %}>Click me</div><form {% htmx_form_submit "#content" %}>...</form>
The template tags are now fully functional and integrated with your HTMX Core system!