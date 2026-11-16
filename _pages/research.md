---
layout: page
title: Research
permalink: /research/
description: What I work on, in plain language.
nav: true
nav_order: 2
---

{% assign themes = site.data.research | sort: "start" | reverse %}
{% assign domains = "physics,computing" | split: "," %}
{% for domain in domains %}
<h2>{% if domain == "physics" %}Physics{% else %}Computing{% endif %}</h2>
{% for t in themes %}{% if t.domain == domain %}
<h3>{{ t.title }}</h3>
<p class="text-sm opacity-70">{{ t.start }} &ndash; {% if t.end %}{{ t.end }}{% else %}present{% endif %}</p>
{% if t.narrative %}
<p>{{ t.narrative }}</p>
{% else %}
<ul>{% for h in t.highlights %}<li>{{ h }}</li>{% endfor %}</ul>
{% endif %}
{% if t.figure %}
<figure>
  <img src="{{ t.figure | relative_url }}" alt="{{ t.figure_alt | default: t.title }}" style="max-width:100%">
  {% if t.figure_caption %}<figcaption class="text-sm opacity-70">{{ t.figure_caption }}</figcaption>{% endif %}
</figure>
{% endif %}
{% endif %}{% endfor %}
{% endfor %}
