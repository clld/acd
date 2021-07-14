<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "languages" %>
<%block name="title">${_('Language')} ${ctx.name}</%block>

<h2>${_('Language')} ${ctx.name}</h2>

${request.get_datatable('values', h.models.Value, language=ctx).render()}

<%def name="sidebar()">
    % if ctx.is_proto:
        <div class="well well-small" style="width: 100%">
            ${u.proto_tree(req, ctx)|n}
        </div>
    % else:
        ${util.language_meta()}
    % endif
</%def>
