<%inherit file="../snippet.mako"/>
<%namespace name="util" file="../util.mako"/>

% if ctx.reconstruction:
<% set = ctx.reconstruction.explicit or ctx.reconstruction %>

<table class="table table-condensed table-nonfluid">
    <tbody>
        % for grp, forms in set.grouped_cognates():
            <tr>
                <td style="font-weight: bold; color: darkolivegreen;" colspan="3">${grp}</td>
            </tr>
            % for lg, form, gloss in forms:
                <tr>
                    <td style="color: green">${h.link(req, lg) if lg else ''}</td>
                    <td>${h.link(req, form)}</td>
                    <td>${gloss}</td>
                </tr>
            % endfor
        % endfor
    </tbody>
</table>
% if set.comment:
    <div>
        ${u.markdown(req, ().comment)|n}
    </div>
% endif
% endif:
