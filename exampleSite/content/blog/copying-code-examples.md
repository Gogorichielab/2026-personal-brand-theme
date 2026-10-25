---
title: "Copying Code Examples"
date: 2026-10-20T09:00:00-05:00
tags: ["notes", "hugo"]
lead: "A post with Terraform, YAML and shell examples, each with a copy button."
---

Every code block on this site has a **Copy code** button above it. It copies the code exactly as written, with indentation and line breaks, and never the line numbers.

A Terraform resource:

```terraform
resource "aws_s3_bucket" "site" {
  bucket = "example-personal-site"

  tags = {
    Purpose = "static-site"
  }
}
```

A GitHub Actions step in YAML, shown with line numbers:

```yaml {linenos=table}
- name: Build the site
  run: hugo --gc --minify
  env:
    HUGO_ENVIRONMENT: production
```

And a shell command:

```shell
hugo server --source exampleSite --themesDir ../..
```
