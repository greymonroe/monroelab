---
title: People
date: 2024-01-01
type: landing

sections:
  - block: hero
    content:
      title: Meet the Team
      text: ''
    design:
      background:
        image:
          filename: hero-tgca.png
          filters:
            brightness: 0.6
          size: cover
          position: center
        text_color_light: true

  - block: people
    content:
      title: Meet the Team
      user_groups:
        - Principal Investigator
        - Postdoctoral Researchers
        - Graduate Students
        - Junior Specialists & Undergraduates
        - Alumni
      sort_by: Params.last_name
      sort_ascending: true
    design:
      show_interests: false
      show_role: true
      show_social: true
---
