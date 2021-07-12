<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "cognatesets" %>

<%block name="title">${_('Cognateset')} ${ctx.name}</%block>

<%def name="sidebar()">
    <div class="well">
        <h3>Reconstructions</h3>
        <table class="table-condensed table">
            <tbody>
                % for set in ctx.sets:
                    <tr>
                        <td><a href="#s-${set.id}">
                            <span style="color: darkslategray;">${set.proto_language}</span>
                        </a></td>
                        <td><a href="#s-${set.id}">
                        <span style="color: darkred; padding-right: 30px;">${set.name}</span>
                        </a></td>
                        <td><a href="#s-${set.id}">
                        <span>${u.shorten(set.description)}</span>
                        </a></td>
                    </tr>
                % endfor

            </tbody>
        </table>
        <ul class="unstyled">
</ul>
</div>
</%def>

<h2>
    <span style="color: darkred; padding-right: 30px;">${ctx.name}</span>
    <span style="color: black; font-family: Times">${ctx.description}</span>
</h2>

% if ctx.comment:
    <div>${u.markdown(ctx.comment)|n}</div>
% endif

% if map_ or request.map:
${(map_ or request.map).render()}
% endif

## An etymon
% if ctx.sets:
    % for set in ctx.sets:
        <%util:section level="4" id="s-${set.id}">
            <%def name="title()">
                <span style="color: darkslategray;">${set.proto_language}</span>
                <span style="color: darkred; padding-right: 30px;">${set.name}</span>
                <span style="color: black; font-family: Times">${set.description}</span>
            </%def>
            <table class="table table-condensed">
                <tbody>
                    % for grp, forms in set.grouped_cognates():
                        <tr><td style="font-weight: bold; color: darkolivegreen;" colspan="3">${grp}</td></tr>
                        % for lg, form, gloss in forms:
                            <tr>
                                <td style="color: green">${h.link(request, lg)}</td>
                                <td>${h.link(request, form)}</td>
                                <td>${gloss}</td>
                            </tr>
                        % endfor
                    % endfor
                </tbody>
            </table>
                % if set.comment:
                    <div>
                        ${u.markdown(set.comment)|n}
                    </div>
                % endif
        </%util:section>
    % endfor
% endif

