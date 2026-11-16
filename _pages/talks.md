---
layout: page
permalink: /talks/
title: Talks
description: Seminars, conference talks and lectures.
nav: true
nav_order: 4
---

{% assign talks = site.data.talks | sort: "date" | reverse %}
{% assign kinds = "seminar,plenary,parallel,lecture,poster" | split: "," %}
{% assign kind_titles = "Invited seminars,Plenary talks,Parallel talks,Lectures,Posters" | split: "," %}
{% for kind in kinds %}
{% assign group = talks | where: "kind", kind %}
{% if group.size > 0 %}
<h2>{{ kind_titles[forloop.index0] }}</h2>
<ul>
{% for t in group %}
<li>
  {{ t.date | append: "-01" | date: "%b %Y" }} &middot;
  {% if t.url %}<a href="{{ t.url }}">{{ t.title | strip }}</a>{% else %}{{ t.title | strip }}{% endif %}<br>
  <span class="opacity-70">{{ t.event }}{% if t.location %}, {{ t.location }}{% endif %}</span>
</li>
{% endfor %}
</ul>
{% endif %}
{% endfor %}
