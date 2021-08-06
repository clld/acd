<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "cognatesets" %>

<%block name="title">${_('Cognateset')} ${ctx.name}</%block>

<%def name="sidebar()">
    <div class="well">
        <h3>Reconstructions</h3>
        <table class="table-condensed table">
            <tbody>
                % for sets in ctx.grouped_sets():
                    % for set in sets:
                        <tr>
                            <td>
                                <a href="#s-${set.id}">
                                ${set.proto_language}
                                </a>
                            </td>
                            <td>
                                <a href="#s-${set.id}">
                                <span style="color: darkred; padding-right: 30px;">${set.name}</span>
                            </a></td>
                            <td>
                                <a href="#s-${set.id}">
                                <span>${u.shorten(set.description)}</span>
                                </a>
                            </td>
                        </tr>
                    % endfor
                % endfor
            </tbody>
        </table>
    </div>
    % if ctx.comment:
        <div class="well">
            <h3>Note</h3>
            ${u.markdown(req, ctx.comment)[0]|n}
        </div>
    % endif
</%def>

<h2>
    <span style="color: darkred; padding-right: 30px;">${ctx.name}</span>
    <span style="color: black; font-family: Times">${ctx.description}</span>
</h2>

% if map_ or request.map:
    ${(map_ or request.map).render()}
% endif

## An etymon
% for sets in ctx.grouped_sets():
    <div class="well well-small">
        % for set in sets:
            <%util:section level="4" id="s-${set.id}">
            <%def name="title()">
                ${h.link(req, set.language)}
                ${h.link(req, set.form)}
                <span style="color: black; font-family: Times">${set.description}</span>
            </%def>
                <table class="table table-condensed table-nonfluid">
                    <tbody>
                        % for grp, forms in set.grouped_cognates():
                            <tr>
                                <td style="font-weight: bold; color: darkolivegreen;" colspan="3">${grp}</td>
                            </tr>
                            % for lg, form, gloss in forms:
                                <tr>
                                    <td style="color: green">${h.link(request, lg) if lg else ''}</td>
                                    <td>${h.link(request, form)}</td>
                                    <td>${gloss}</td>
                                </tr>
                            % endfor
                        % endfor
                    </tbody>
                </table>
            % if set.comment:
                <div>
                    ${u.markdown(req, set.comment)[0]|n}
                </div>
            % endif
            </%util:section>
        % endfor
    </div>
% endfor
