<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "formsets" %>
<%block name="title">Modules</%block>


<h2>Modules</h2>

<div class="tabbable">
    <ul class="nav nav-tabs">
        <li class="active"><a href="#roots" data-toggle="tab">Roots</a></li>
        <li><a href="#loans" data-toggle="tab">Loans</a></li>
        <li><a href="#near" data-toggle="tab">Near Cognates</a></li>
        <li><a href="#noise" data-toggle="tab">Chance Resemblances</a></li>
    </ul>
    <div class="tab-content" style="overflow: visible;">
        <div id="roots" class="tab-pane active">
            <div>
                ${Root.description}
            </div>
            ${request.get_datatable('formsets', u.Formset, contribution=Root, eid='r-table').render()}
        </div>
        <div id="loans" class="tab-pane active">
            <div>
                ${Loan.description}
            </div>
            ${request.get_datatable('formsets', u.Formset, contribution=Loan, eid='lo-table').render()}
        </div>
        <div id="near" class="tab-pane active">
            <div>
                ${Near.description}
            </div>
            ${request.get_datatable('formsets', u.Formset, contribution=Near, eid='near-table').render()}
        </div>
        <div id="noise" class="tab-pane active">
            <div>
                ${Noise.description}
            </div>
            ${request.get_datatable('formsets', u.Formset, contribution=Noise, eid='n-table').render()}
        </div>
    </div>
    <script>
$(document).ready(function() {
    if (location.hash !== '') {
        $('a[href="#' + location.hash.substr(2) + '"]').tab('show');
    }
    return $('a[data-toggle="tab"]').on('shown', function(e) {
        return location.hash = 't' + $(e.target).attr('href').substr(1);
    });
});
    </script>
</div>