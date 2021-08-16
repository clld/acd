<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "formsets" %>

<h3>${ctx.contribution.name}: ${ctx.name}</h3>
% if ctx.comment:
    <div class="well well-small">
        ${u.markdown(req, ctx.comment)[0]|n}
    </div>
% endif

<table class="table table-condensed table-nonfluid">
    <tbody>
        % for grp, forms in ctx.grouped_forms():
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
