<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "contributions" %>

<h2>${ctx.name}</h2>

<div class="well well-small">
    ${ctx.description}
</div>

${request.get_datatable('formsets', u.Formset, contribution=ctx, eid='lo-table').render()}
