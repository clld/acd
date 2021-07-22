<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "contributions" %>


<h2>Words for
    <span class="gloss">${h.link(request, ctx.parameter, label=ctx.parameter.label)}</span>
    in
    ${h.link(request, ctx.language)}
</h2>

% for i, value in enumerate(ctx.values):
<div style="clear: right;">
    <h4>
        ${value}
    </h4>
    <ul>
    % for cs in value.cognates:
        <li>
            ${h.link(req, cs.cognateset)} <span class="gloss">${cs.cognateset.description}</span>
            % if not cs.cognateset.etymon:
                [Etymon]
            % elif cs.cognateset.implicit:
                [implicit]
            % endif
        </li>
    % endfor
    </ul>
    <dl>
% for contrib, formsets in value.grouped_formsets():
    <dt>${contrib.name}</dt>
        % for formset in formsets:
            <dd>
                <table class="table table-condensed table-nonfluid">
                    <caption>${formset.name}</caption>
                    <tbody>
                        % for grp, forms in formset.grouped_forms():
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
            </dd>
        % endfor
        </dl>
% endfor

</div>
% endfor
<%def name="sidebar()">
<div class="well well-small">
<dl>
    <dt class="contribution">${_('Contribution')}:</dt>
    <dd class="contribution">
        ${h.link(request, ctx.contribution)}
        by
        ${h.linked_contributors(request, ctx.contribution)}
        ${h.button('cite', onclick=h.JSModal.show(ctx.contribution.name, request.resource_url(ctx.contribution, ext='md.html')))}
    </dd>
    <dt class="language">${_('Language')}:</dt>
    <dd class="language">${h.link(request, ctx.language)}</dd>
    <dt class="parameter">${_('Parameter')}:</dt>
    <dd class="parameter">${h.link(request, ctx.parameter)}</dd>
    % if ctx.references or ctx.source:
    <dt class="source">${_('Source')}:</dt>
        % if ctx.source:
        <dd>${ctx.source}</dd>
        % endif
        % if ctx.references:
        <dd class="source">${h.linked_references(request, ctx)|n}</dd>
        % endif
    % endif
    ${util.data(ctx, with_dl=False)}
</dl>
</div>
</%def>
