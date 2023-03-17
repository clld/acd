<%inherit file="../home_comp.mako"/>
<% intro, md =  u.markdown(req, ctx.description.replace('## Introduction', '')) %>

<%def name="sidebar()">
<div class="well well-small">
    <p>
        The ACD Online (this website) serves the
        <a href="https://doi.org/10.5281/zenodo.7737547">latest released version</a>
        of data curated in a ${h.external_link('https://github.com/lexibank/acd', label='repository on GitHub')}.
        When using this data, you should cite the exact version you are using following the citation
        recommendations at ${h.external_link('https://github.com/lexibank/acd/releases')}.
    </p>
    <p>The version currently served by this website (v1.2) should be cited as</p>
    <blockquote>
        Robert Bust, Stephen Trussel, & Alexander D. Smith. (2023). CLDF dataset derived from Blust's "Austronesian Comparative Dictionary" (v1.2) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.7741197
    </blockquote>
</div>
</%def>

<h2>The Austronesian Comparative Dictionary Online</h2>

<p>
    The Austronesian Comparative Dictionary (ACD) was created by Robert Blust and Steve Trussel and is
    the most comprehensive comparative dictionary for Austronesian languages ever compiled. The dictionary
    was originally hosted on a website designed by Trussel, and updated with content by Blust, until 2020 when,
    after Steve Trussel’s unexpected passing, Blust sought to move the ACD to its current and more permanent
    site hosted by the Max Planck Institute for Evolutionary Anthropology and managed by Robert Forkel.
    Approximately one month before Blust’s passing in 2022, responsibility for the maintenance of the
    content of the ACD, including the addition of new terms and editing of existing entries, was passed to
    Alexander D. Smith who began working with Forkel in late January 2022.
</p>

<p>
    To search and browse entries, begin by navigating to <a href="${req.route_url('cognatesets')}">Cognatesets</a> and
    search for specific reconstructions or glosses.
</p>

<p>
    The original introduction to the ACD, written by Blust, can be accessed <a href="${req.route_url('about')}">here</a>.
</p>