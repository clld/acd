<%inherit file="../snippet.mako"/>
<%namespace name="util" file="../util.mako"/>

    % for set in ctx.iter_explicit_reconstructions():
        % if loop.first:
            <h3>Reconstructions</h3>
        % endif
        <h4>
            <span class="proto-language">${set.proto_language}</span>
            <span class="proto-form">${set.form.name}</span>
            <span class="gloss">${set.form.valueset.parameter.label}</span>
        </h4>
        <p>
            Etymon: ${h.link(req, set.etymon)}
        </p>
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
                ${u.markdown(req, set.comment)[0]|n}
            </div>
        % endif
    % endfor

% for contrib, formsets in ctx.grouped_formsets():
    <h3>${contrib.name}</h3>
        <ul class="unstyled">
            % for formset in formsets:
            <li>
                ${h.link(req, formset)}
            </li>
            % endfor
        </ul>
% endfor
