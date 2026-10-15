# updated website

Zhenyu Lu's webpage

## Add a project website

Edit `_data/projects.yml` and append one entry after the project is publicly deployed:

```yaml
- name: "My new project"
  path: "/my-new-project/"
  code: "https://github.com/scottlu04/my-new-project"
  description: "A short explanation of what the project does."
```

Commit the change to `master`. GitHub Pages' existing Jekyll build will update:

- The homepage's Projects section, with crawlable project and code links.
- `/projects-sitemap.xml`, with each registered project website listed once.

`path` is required and must be a published path under `https://scottlu04.github.io/`,
starting with a single `/`. `name` is required; `code` and `description` are optional.
Use the final canonical path, normally with a trailing `/`. Do not put a GitHub
repository URL or an unrelated domain in `path`. New domains need their own
Search Console property. Remove an entry if its project website is retired.

The existing `/sitemap.xml` continues to cover pages and documents built by this
repository. `/robots.txt` advertises both sitemaps. Project websites deployed
from separate repositories are registered explicitly; this does not scan or
publish all repositories on the account.

Search Console setup is once per website: verify the URL-prefix property
`https://scottlu04.github.io/` and submit `sitemap.xml` and `projects-sitemap.xml`.
Future projects under that prefix need no new verification or repeated sitemap
submission. Google discovers updates through the links and sitemaps; discovery
does not guarantee indexing or a particular ranking. Keep the existing Google
Analytics verification code, or establish another verification method before
removing it.

## Template

This repo is built on a fork of **Jekyll Now** from [this repository](https://github.com/barryclark/jekyll-now). **Jekyll** is a static site generator that's perfect for GitHub hosted blogs ([Jekyll Repository](https://github.com/jekyll/jekyll))

The website design is just a modification of [Jon Barron's website](https://jonbarron.info/) and is converted for my own use, re-purposing my old markdown posts. **Feel free to use template for your own purposes**, but please respect copyright for all the images/content in my `images`, `pdfs`, `_posts` folders. 
