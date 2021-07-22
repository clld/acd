<%inherit file="../home_comp.mako"/>
<% intro, md =  u.markdown(req, ctx.description.replace('## Introduction', '')) %>

<%def name="sidebar()">
    <% intro, md =  u.markdown(req, ctx.description.replace('## Introduction', '')) %>
    <div class="well">
        ${md.toc|n}
    </div>
</%def>

<h2>The Austronesian Comparative Dictionary Online</h2>

${intro|n}