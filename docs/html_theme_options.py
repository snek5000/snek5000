__common_css_variables = {
    "font-size--small--2": "84%",
}
light_css_variables = {
    "color-brand-primary": "#1954a6",
    "color-brand-content": "#1954a6",
    **__common_css_variables,
}
dark_css_variables = {**__common_css_variables}

#  # Material theme options (see theme.conf for more information)
#  html_theme_options = {
#      # Set the name of the project to appear in the navigation.
#      "nav_title": f"{project} documentation",
#      # ??
#      "touch_icon": html_favicon,
#      # Logo to the left of the title
#      "logo_icon": "&#x1F30A",  # https://emojipedia.org/water-wave/
#      #
#      "nav_links": [{"href": "doxygen/index", "title": "fortran docs", "internal": True}],
#      # Specify a base_url used to generate sitemap.xml. If not
#      # specified, then no sitemap will be built.
#      "base_url": f"https://{project}.readthedocs.io",
#      # Set the color and the accent color
#      "color_primary": "indigo",
#      "color_accent": "deep-purple",
#      # Set the repo location to get a badge with stats
#      "repo_url": f"https://github.com/snek5000/{project}/",
#      "repo_name": project,
#      # Visible levels of the global TOC; -1 means unlimited
#      "globaltoc_depth": 2,
#      # If False, expand all TOC entries
#      "globaltoc_collapse": True,
#      # If True, show hidden TOC entries
#      "globaltoc_includehidden": False,
#  }
