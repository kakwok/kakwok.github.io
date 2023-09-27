---
layout: default
title: Home
---

<div class="row">
  <div class="col-sm-8">
<div style="text-align:justify"> 
I am Martin Kwok. I am a research associate at [Fermilab](https://cms.fnal.gov/), working on the [CMS experiment](https://cms.cern/).

I search for the most fundamental particles in the largest scientific experiment. 

Learn about me [here]({% link about.md %})  

</div>
<hr style="width:75%">

<!--
<div class="posts">
  {% for post in site.posts limit:3%}
  <div class="post">
    <h1 class="post-title">
      <a href="{{ site.baseurl }}{{ post.url }}">
        {{ post.title }}
      </a>
    </h1>

    <span class="post-date">{{ post.date | date_to_string }}</span>

    {{ post.content }}
  </div>
  {% endfor %}
</div>
-->
</div>
  <div class="col-sm-4">
  <img align='right' src="/assets/images/propic.jpg">
  </div>
</div>


<!--
<div class="pagination">
  {% if paginator.next_page %}
    <a class="pagination-item older" href="{{ site.baseurl }}/page{{paginator.next_page}}">Older</a>
  {% else %}
    <span class="pagination-item older">Older</span>
  {% endif %}
  {% if paginator.previous_page %}
    {% if paginator.page == 2 %}
      <a class="pagination-item newer" href="{{ site.baseurl }}/">Newer</a>
    {% else %}
      <a class="pagination-item newer" href="{{ site.baseurl }}/page{{paginator.previous_page}}">Newer</a>
    {% endif %}
  {% else %}
    <span class="pagination-item newer">Newer</span>
  {% endif %}
</div>
-->

