---
layout: about
title: About
permalink: /
subtitle: Research Assistant Professor, University of Nebraska-Lincoln &middot; CMS experiment, LHC

profile:
  align: right
  image: prof_pic.jpg
  image_circular: false
  more_info: >
    <p>Fermi National Accelerator Laboratory</p>
    <p>Batavia, IL</p>

selected_papers: false
social: true

announcements:
  enabled: true
  scrollable: false
  limit: 3

latest_posts:
  enabled: false
---

I am a particle physicist on the [CMS experiment](https://cms.cern/) at the
[Large Hadron Collider](https://home.cern/science/accelerators/large-hadron-collider),
and a Research Assistant Professor at the University of Nebraska-Lincoln, based at
[Fermilab](https://cms.fnal.gov/).

I look for particles that conventional reconstruction was never built to see. My current
focus is **long-lived particles**: new states that travel some distance before they decay,
and leave a distinctive shower of hits in the CMS muon detectors. I work on the
[searches](/research/) themselves and on the triggers and computing that make them possible.

Before that I searched for highly boosted Higgs bosons decaying to bottom quarks with my thesis
advisor [Greg Landsberg](https://vivo.brown.edu/display/glandsbe) at Brown. A non-technical
introduction is in this [CMS physics briefing](https://cms.cern/news/boosting-unknown-highest-energy-higgs-bosons).

I am also the manager of the CMS Remote Operations Center (ROC) at Fermilab.

I also build tools. Some are for physics (GPU-portable reconstruction), and lately some are for
working *with* AI: [Claude Code mods and a team-collaboration framework](/projects/).

Outside physics I enjoy badminton and bouldering.

My academic CV is available as a [PDF]({{ '/assets/cv.pdf' | relative_url }}).

<div class="projects">
  <div class="row row-cols-1 row-cols-md-3">
  {% for tile in site.data.home_tiles %}
    <div class="col">
      <a href="{{ tile.url | relative_url }}">
        <div class="card h-100 hoverable">
          <div class="card-body" style="flex:none;padding-bottom:.5rem">
            <h2 class="card-title">{{ tile.title }}</h2>
            <p class="card-text" style="margin-bottom:0">{{ tile.description }}</p>
          </div>
          {% if tile.img %}<img src="{{ tile.img | relative_url }}" class="card-img" style="border-bottom-left-radius:.25rem;border-bottom-right-radius:.25rem" alt="{{ tile.img_alt | default: tile.title }}">{% endif %}
        </div>
      </a>
    </div>
  {% endfor %}
  </div>
</div>
