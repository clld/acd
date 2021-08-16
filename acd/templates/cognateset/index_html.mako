<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "cognatesets" %>

<%block name="head">
    <style>
        .sent {
            background: lightblue;
            border: 1px solid darkblue;
        }
    </style>
</%block>

<%block name="title">${_('Cognatesets')}</%block>

<h2>${title()}</h2>

<table style="width: 90%; margin-left: 5%">
<tbody>
<tr>
    % for _, v, px in initials:
        <td style="width: ${100 // len(initials)}%; vertical-align: bottom"><div class="sent" style="height: ${px}px;"> </div></td>
    % endfor
</tr>
##<tr>
##    % for _, v, _ in initials:
##        <td>${v}</td>
##    % endfor
##</tr>
<tr>
    % for c, v, _ in initials:
        <th>
            <a href="${req.route_url('cognatesets', _query=dict(sSearch_1='^*' + c))}" title="${v} sets">
                ${c}
            </a>
        </th>
    % endfor
</tr>
</tbody>
</table>

<div>
    ${ctx.render()}
</div>

