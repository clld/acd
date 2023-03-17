<%inherit file="home_comp.mako"/>
<% intro, md =  u.markdown(req, req.dataset.description.replace('## Introduction', '')) %>

<%def name="sidebar()">
    <% intro, md =  u.markdown(req, req.dataset.description.replace('## Introduction', '')) %>
    <div class="well">
        ${md.toc|n}
    </div>
</%def>

<h2>About The Austronesian Comparative Dictionary</h2>

${intro|n}