---
title: People
date: 2024-01-01
type: landing

sections:
  - block: hero
    content:
      title: ''
      text: ''
    design:
      css_class: people-page-hero
      background:
        image:
          filename: banner-group.png
          filters:
            brightness: 0.85
          size: cover
          position: center top
        text_color_light: true

  - block: people
    content:
      title: ''
      user_groups:
        - Principal Investigator
        - Postdoctoral Researchers
        - Graduate Students
        - Junior Specialists & Undergraduates
      sort_by: Params.last_name
      sort_ascending: true
    design:
      show_interests: false
      show_role: true
      show_social: true

  - block: people
    content:
      title: Alumni
      user_groups:
        - Alumni
      sort_by: Params.last_name
      sort_ascending: true
    design:
      show_interests: false
      show_role: true
      show_social: false
---
