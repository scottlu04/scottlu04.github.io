# updated website

Zhenyu Lu's webpage

## Current public homepage

Edit `homepage/` to update **https://scottlu.top/**. This is the approved Claude
Design export: Academic has the complete profile; Lab, World, Digital Twin,
Portal and the old Exploration route are matching placeholders. Their `noindex`
metadata keeps unfinished pages out of the sitemap. The shared styles are
`academic.css` and `topbar.css`. Keep placeholder `noindex` until real content is
ready. The build validates local references before publication.

Only this curated static directory is uploaded to Cloudflare. The original
design archive, uploaded source documents and design-editor files are not
published. The older Jekyll source serves GitHub Pages independently.

## Hosting

The canonical homepage is **https://scottlu.top/**, deployed as Cloudflare Worker
`scottlu-home` with Static Assets. Source remains in this repository. The existing
GitHub Pages site stays online and its homepage canonical points to the new domain.
This is a canonical hint, not an HTTP redirect. WAG stays at its existing GitHub
Pages URL; do not set a GitHub Pages custom domain because that would change the
inherited addresses of project sites.

`invest.scottlu.top` is a separate, private application. Its DNS, Access policies,
server and database are not managed by this repository.

### Publish the Cloudflare homepage

The homepage is live and automatic publication is **enabled**.
The workflow `.github/workflows/cloudflare.yml` is gated by repository variable
`CLOUDFLARE_DEPLOY_ENABLED=true` and requires repository secret
`CLOUDFLARE_API_TOKEN` with Workers Scripts Edit permission for the account.
The authorized deployment token is stored in GitHub Actions Secrets; it has only
Workers Scripts Write permission in this Cloudflare account. Pushes to `master`
build and publish the homepage and its sitemap together. No manual upload or
Search Console resubmission is needed for routine updates. To pause deployment,
set `CLOUDFLARE_DEPLOY_ENABLED=false` without deleting the existing website.
Never commit tokens or put them in workflow source.

The same build can be run manually with Python 3.12:

```sh
python deployment/prepare.py
python deployment/deploy.py --dry-run
# Supply CLOUDFLARE_API_TOKEN through your secret manager/environment first.
python deployment/deploy.py
```

The initial upload used the connected Cloudflare API with a short-lived asset
upload session. No deployment credential is committed in repository source.
`deployment/metadata.json` records the Worker settings. Routine deployment does
not change DNS or Access. The 34 MB `/paper/dfcil.pdf` remains on GitHub Pages;
the Cloudflare URL redirects there because it exceeds the static asset limit.

For future albums, keep media files in object storage and descriptions and
permissions in a separate database. Add authenticated API routes to
`deployment/worker.mjs` and explicitly configure `run_worker_first` for those
routes. No media storage, database or upload/admin endpoint has been created yet.

Search Console has a DNS-verified Domain property for `scottlu.top`. Keep the
verification TXT record. The new site's `sitemap.xml` contains only its own
existing indexable public URLs; `robots.txt` advertises it. New HTML pages in
`homepage/` are included automatically unless marked `noindex`. Private
application URLs must not be added.

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

For projects hosted elsewhere, add an absolute `url` field to keep the link stable
on both sites (WAG demonstrates this). A local `path` refers to a published page,
not a request to deploy a new project. On Cloudflare the preparation step removes
the GitHub project sitemap, so external project addresses are not falsely listed
under `scottlu.top`. The enabled Cloudflare workflow publishes homepage changes
from `homepage/` on the same `master` commit automatically. The Jekyll project
registry does not modify the new Cloudflare homepage; add its links directly
to `homepage/index.html` when needed.

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
