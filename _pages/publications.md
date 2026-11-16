---
layout: page
permalink: /publications/
title: Publications
description: A short, curated selection. The complete list is on INSPIRE.
nav: true
nav_order: 3
---

{% assign pubs = site.data.publications | sort: "date" | reverse %}
{% assign domains = "physics,computing" | split: "," %}
{% for domain in domains %}
<h2>{% if domain == "physics" %}Physics{% else %}Computing{% endif %}</h2>
<ul>
{% for p in pubs %}{% if p.domain == domain %}
<li>
  {% assign a = p.authors | strip %}
  {% assign ref_head = p.ref | slice: 0, 5 %}
  <strong>{{ p.title | strip }}</strong><br>
  {% if a contains "et al." %}{{ a }}{% else %}{{ a }}.{% endif %}
  {% if ref_head == "arXiv" %}<a href="https://arxiv.org/abs/{{ p.arxiv }}">{{ p.ref }}</a>{% else %}{{ p.ref }}.{% if p.arxiv %} <a href="https://arxiv.org/abs/{{ p.arxiv }}">arXiv</a>{% endif %}{% endif %}
  {% if p.doi %}&middot; <a href="https://doi.org/{{ p.doi }}">DOI</a>{% endif %}
  {% if p.inspire %}&middot; <a href="https://inspirehep.net/literature/{{ p.inspire }}">INSPIRE</a>{% endif %}
</li>
{% endif %}{% endfor %}
</ul>
{% endfor %}

<p>
  <a href="https://inspirehep.net/authors/{{ site.data.socials.inspirehep_id }}">Full publication list</a>
  ({{ site.data.inspire_stats.papers }} papers, {{ site.data.inspire_stats.citations }} citations)
  on INSPIRE.
</p>
