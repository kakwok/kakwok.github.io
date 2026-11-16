---
layout: page
title: Projects
permalink: /projects/
description: Tools I build for working with AI, and for physics computing.
nav: true
nav_order: 6
horizontal: false
---

<div class="projects">
{% assign sorted_projects = site.projects | sort: "importance" %}
<div class="row row-cols-1 row-cols-md-3">
  {% for project in sorted_projects %}
    {% include projects.liquid %}
  {% endfor %}
</div>
</div>
