<%inherit file="app.mako"/>

##
## define app-level blocks:
##
<%block name="header">
    <div style="font-size: x-large; margin-left: 20px; padding-top: 10px; margin-bottom: 0.5em">
        ##<a href="${request.route_url('dataset')}">
            The Austronesian Comparative Dictionary
        ##</a>
    </div>
</%block>

${next.body()}
