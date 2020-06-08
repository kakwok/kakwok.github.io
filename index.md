---
layout: default
title: Home
---

<div class="row">
  <div class="col-sm-8">
Hi, I am Martin Kwok. I am a Physics Ph.D. student at [Brown University](https://www.brown.edu/academics/physics/), 
expecting to graduate in August 2020. 

I search for most fundamental particles in the largest scientific experiment with machine learning. 

Learn about me [here]({% link about.md %})  

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
  <img align='right' width='200' height='200' src="/assets/images/propic.jpg">
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

