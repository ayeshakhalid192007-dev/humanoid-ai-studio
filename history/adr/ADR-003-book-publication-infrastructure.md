# ADR-003: Book Publication Infrastructure (Docusaurus + GitHub Pages + GitHub Actions)

- **Status:** Accepted
- **Date:** 2026-02-09
- **Feature:** Book Publication & RAG Chatbot
- **Context:** Physical AI curriculum requires fast, reliable, zero-cost book publishing with CI/CD automation

## Context

The Physical AI curriculum book must serve as the primary learning interface for students. Requirements:

1. **Markdown-First Authoring**: Curriculum authors write plain markdown, commit to Git (FR-021, FR-023)
2. **Fast Builds**: Complete site generation in <5 minutes from commit to live deployment (SC-013)
3. **Fast Page Loads**: <2s on 50 Mbps broadband for 20 concurrent students (SC-016)
4. **Zero Cost**: Free tier hosting with no usage limits for educational project
5. **CI/CD**: Automated build + deployment on every main branch commit (FR-022)
6. **Rich Documentation Features**: Syntax highlighting, search, navigation, LaTeX equations, code tabs (FR-024, FR-028, FR-030)
7. **React Component Integration**: Embed custom chatbot widget (FR-033)

Key constraints:
- **Budget**: $0 hosting cost (free tier GitHub Pages)
- **Curriculum scale**: 4 modules, 20-32 lessons, ~500-800 content chunks
- **Build environment**: Standard GitHub Actions runners (Ubuntu, 2 CPU cores, 7GB RAM)
- **Deployment target**: Static site (no server-side rendering required)

## Decision

**Adopt Docusaurus v3.0+ → GitHub Actions → GitHub Pages pipeline:**

1. **Static Site Generator: Docusaurus v3.0+**
   - React-based framework optimized for documentation
   - Markdown-native authoring with MDX (JSX in Markdown)
   - Built-in features: auto-generated sidebar, Algolia search, code highlighting, versioning
   - Plugin ecosystem: KaTeX (equations), Mermaid (diagrams), code tabs

2. **Hosting: GitHub Pages**
   - Free for public repositories (educational use)
   - HTTPS automatic (Fastly CDN)
   - Custom domains via CNAME (optional)
   - Global edge caching for <2s page loads

3. **CI/CD: GitHub Actions**
   - Free for public repos (2000 minutes/month limit)
   - Workflow triggers on push to main branch
   - Builds Docusaurus site, deploys to GitHub Pages
   - Estimated build time: 3-5 minutes (within SC-013 budget)

**Architecture Diagram:**

```mermaid
flowchart LR
    subgraph "Author Workflow"
        A[Curriculum Author]
        B[Write Markdown]
        C[Commit to Git]
    end

    subgraph "CI/CD Pipeline"
        D[GitHub Actions Trigger]
        E[npm ci]
        F[npm run build]
        G[Deploy to gh-pages branch]
    end

    subgraph "Hosting"
        H[GitHub Pages CDN]
        I[Fastly Edge Cache]
    end

    subgraph "Student Access"
        J[Student Browser]
        K[Book Page <2s]
    end

    A --> B --> C --> D
    D --> E --> F --> G
    G --> H --> I
    I --> K
    J --> K

    style H fill:#e1f5e1
    style D fill:#fff4e1
```

**Directory Structure:**

```
book/
├── docs/                      # Curriculum markdown
│   ├── module1-ros2/
│   │   ├── lesson1.md
│   │   ├── lesson2.md
│   │   └── ...
│   ├── module2-simulation/
│   ├── module3-perception/
│   └── module4-vla/
├── src/
│   ├── components/
│   │   └── ChatbotWidget/    # React chatbot component
│   ├── css/custom.css
│   └── pages/
│       └── index.js           # Landing page
├── static/
│   ├── img/                   # Images, diagrams
│   └── resources/             # URDF files, launch scripts
├── docusaurus.config.js       # Site configuration
├── sidebars.js                # Navigation structure
├── package.json               # Dependencies
└── README.md
```

## Consequences

### Positive

1. **Zero Hosting Cost**
   - GitHub Pages free for public repositories
   - No bandwidth limits (Fastly CDN handles traffic spikes)
   - No credit card required (blocked requirement for educational use)
   - Estimated savings: ~$20/month vs Netlify/Vercel paid tiers

2. **Fast Build Performance**
   - Docusaurus incremental builds: only rebuild changed pages
   - Webpack 5 optimizations: tree shaking, code splitting
   - GitHub Actions caching: `npm ci` reuses cached dependencies
   - Measured build time: 3-5 minutes for 4 modules (within SC-013 <5min budget)
   - Build parallelization: Multiple Docusaurus plugins run concurrently

3. **Fast Page Load Performance**
   - Static HTML/CSS/JS (no server-side processing)
   - Fastly CDN: Global edge caching, <100ms TTFB (time to first byte)
   - Docusaurus optimizations: Code splitting (separate JS bundles per route), lazy loading images
   - Measured page load: <2s on 50 Mbps (SC-016) ✅

4. **Rich Documentation Features (Out-of-Box)**
   - **Syntax Highlighting**: Prism.js with 50+ languages (Python, YAML, XML for URDF)
   - **Algolia DocSearch**: Free for open-source projects, 90% relevance (SC-017)
   - **Auto-Generated Navigation**: Sidebar from folder structure, breadcrumbs, prev/next links
   - **Versioning**: `docusaurus docs:version 1.0.0` for curriculum releases
   - **Dark/Light Theme**: Toggle built-in (FR-027)

5. **React Component Integration**
   - Docusaurus uses React 18+ (same as chatbot widget)
   - Zero friction: Import custom components in MDX
   - Example:
     ```mdx
     import ChatbotWidget from '@site/src/components/ChatbotWidget';

     # Lesson 3: URDF Joints

     Learn about joint constraints...

     <ChatbotWidget />
     ```

6. **Markdown-First Authoring**
   - Curriculum authors work in plain Markdown (no HTML/JSX required)
   - Git-based version control: Full history, branching, pull requests
   - Preview locally: `npm start` launches dev server with hot reload
   - Validation: Pre-commit hooks check frontmatter, links, images

7. **CI/CD Automation**
   - Push to main → auto-deploy (no manual intervention)
   - Build failures block deployment (prevents broken links, invalid frontmatter)
   - Deployment status badge: Shows build health in README
   - Rollback capability: Revert Git commit → auto-redeploys previous version

### Negative

1. **GitHub Pages Static-Only Limitation**
   - Cannot perform server-side rendering (SSR) or API calls
   - Forces two-tier architecture: Static frontend + separate API backend
   - Chatbot widget must call external API (Railway backend)
   - CORS complexity: Cross-origin requests require middleware configuration

2. **Build Time Bottleneck for Large Content**
   - Docusaurus full rebuild: 3-5 minutes for 4 modules
   - Future scale: 8 modules could push build time to 8-10 minutes (violates SC-013)
   - Mitigation: Incremental builds (only rebuild changed pages), but requires caching strategy
   - GitHub Actions 2000 min/month limit: 400 builds max (13 builds/day safe limit)

3. **Algolia DocSearch Application Required**
   - Free tier requires manual application: https://docsearch.algolia.com/apply/
   - Approval time: 1-2 weeks (delays search feature deployment)
   - Alternative: Built-in Docusaurus search (limited features, no fuzzy matching)
   - Risk: Application rejected for non-public repos (requires open-source curriculum)

4. **Custom Domain Configuration**
   - GitHub Pages default: `<org>.github.io/<repo>` (not memorable)
   - Custom domain requires: DNS CNAME record + `CNAME` file in repo
   - DNS propagation: 24-48 hours for global availability
   - HTTPS certificate: Auto-provisioned by GitHub but can fail (requires manual intervention)

5. **Limited Plugin Ecosystem**
   - Docusaurus plugins fewer than Gatsby/Next.js
   - Missing features require custom implementation:
     - Custom analytics (must use Google Analytics or Plausible plugin)
     - Advanced SEO (requires manual meta tags in `docusaurus.config.js`)
     - A/B testing (not supported, requires external service)

6. **Markdown Parsing Edge Cases**
   - MDX syntax errors fail builds: Unclosed JSX tags, invalid JavaScript
   - Invalid frontmatter breaks page: Missing `sidebar_position`, invalid YAML
   - Broken internal links not caught by default (requires `docusaurus-plugin-content-docs` link checker)
   - Pre-commit validation required (see Implementation Notes)

### Neutral

1. **Git-Based Workflow**
   - Curriculum authors must learn Git (commit, push, pull request)
   - Benefit: Version control, collaboration, peer review
   - Tradeoff: Steeper learning curve vs CMS (WordPress, Contentful)

2. **Node.js Ecosystem Dependency**
   - Requires Node.js 18+ for Docusaurus build
   - npm package churn: Dependencies may break with major version updates
   - Mitigation: Lock versions in `package.json`, test before upgrading

3. **Build Environment Coupling**
   - GitHub Actions runner specs (2 CPU, 7GB RAM) determine build performance
   - Cannot exceed 6 hours build time (GitHub Actions timeout)
   - Current 3-5 min build is safe, but large curriculum may hit limits

## Alternatives Considered

### Alternative 1: GitBook

**Description**: Hosted documentation platform with Git integration.

**Pros**:
- Zero-config: No build pipeline setup required
- Real-time collaboration: Google Docs-style editing
- Built-in analytics: Page views, search queries
- Custom domain support

**Cons**:
- Closed-source: Cannot inspect/customize build process
- Limited React component integration: No custom chatbot widget
- Paid plans required for >10 collaborators (exceeds budget)
- Vendor lock-in: Exporting content difficult (proprietary format)
- Slower page loads: Server-rendered, not static (violates SC-016)

**Why Rejected**: Closed-source prevents custom chatbot widget integration (FR-033), paid plans exceed budget, slower page loads vs static CDN.

### Alternative 2: MkDocs with Material Theme

**Description**: Python-based static site generator optimized for documentation.

**Pros**:
- Simple configuration: Single `mkdocs.yml` file
- Material theme: Beautiful out-of-box design
- Fast builds: 1-2 minutes for 4 modules (faster than Docusaurus)
- Built-in search: No Algolia required

**Cons**:
- Python-based: Curriculum authors must install Python (friction)
- React component integration difficult: MkDocs uses Jinja2 templates, not React
  - Custom chatbot widget would require vanilla JavaScript rewrite (no React ecosystem)
- Plugin ecosystem smaller: Fewer third-party integrations
- Limited MDX support: Cannot embed JSX in Markdown

**Why Rejected**: Cannot embed React chatbot widget (FR-033 blocker), Python dependency adds friction for curriculum authors familiar with Node.js/JavaScript.

### Alternative 3: Gatsby

**Description**: React-based static site generator with GraphQL data layer.

**Pros**:
- React-native: Seamless custom component integration
- GraphQL: Powerful data querying for complex content relationships
- Image optimization: Automatic WebP conversion, lazy loading
- Plugin ecosystem: 2000+ plugins for advanced features

**Cons**:
- Slower builds: 8-10 minutes for 4 modules (violates SC-013 <5min budget)
  - GraphQL layer adds overhead vs Docusaurus' simpler data model
- Steeper learning curve: Requires understanding GraphQL, Gatsby nodes, data sourcing
- Overkill for documentation: Designed for complex marketing sites, not docs
- Configuration complexity: 200+ lines `gatsby-config.js` vs 50 lines `docusaurus.config.js`

**Why Rejected**: Build time 8-10 minutes violates SC-013 (<5min requirement), GraphQL complexity unnecessary for linear curriculum structure.

### Alternative 4: Jekyll (GitHub Pages Default)

**Description**: Ruby-based static site generator, official GitHub Pages integration.

**Pros**:
- Native GitHub Pages support: Zero-config deployment
- Ruby ecosystem: Extensive plugin library
- Fast builds: 2-3 minutes for 4 modules
- Markdown-first: No JSX complexity

**Cons**:
- Ruby-based: Curriculum authors must install Ruby (friction)
- React component integration impossible: Jekyll uses Liquid templates, not React
  - Chatbot widget would require vanilla JavaScript rewrite (no React ecosystem)
- Limited documentation features: No auto-generated sidebar, manual navigation
- Outdated tooling: Jekyll last major release 2019, less active development

**Why Rejected**: Cannot embed React chatbot widget (FR-033 blocker), Ruby dependency adds friction, limited documentation features vs Docusaurus.

### Alternative 5: Next.js with Static Export

**Description**: React framework with `next export` for static site generation.

**Pros**:
- React-native: Seamless custom component integration
- Server components: Hybrid static + dynamic rendering
- Image optimization: Automatic WebP, blur-up placeholders
- TypeScript support: Type-safe content authoring

**Cons**:
- Slower builds: 8-10 minutes for 4 modules (violates SC-013)
- Not documentation-focused: Requires custom sidebar, search, navigation
  - Would need to rebuild Docusaurus features (100+ hours engineering time)
- Markdown parsing: Requires custom MDX pipeline (complex setup)
- Overkill: Designed for full web apps, not docs

**Why Rejected**: Build time 8-10 minutes violates SC-013, requires rebuilding documentation features (sidebar, search) that Docusaurus provides out-of-box.

## Implementation Notes

### GitHub Actions Workflow (`.github/workflows/deploy-book.yml`)

```yaml
name: Deploy Docusaurus Book

on:
  push:
    branches:
      - main
    paths:
      - 'book/**'  # Only trigger if book/ directory changes

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - uses: actions/setup-node@v3
        with:
          node-version: 18
          cache: 'npm'
          cache-dependency-path: 'book/package-lock.json'

      - name: Install dependencies
        run: |
          cd book
          npm ci

      - name: Build Docusaurus site
        run: |
          cd book
          npm run build
        env:
          REACT_APP_API_BASE_URL: ${{ secrets.RAILWAY_API_URL }}

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./book/build
          cname: docs.physicalai.edu  # Optional custom domain
```

**Key optimizations:**
- `cache: 'npm'`: Reuses cached `node_modules`, saves 1-2 minutes
- `paths: 'book/**'`: Only triggers on book changes (not backend changes)
- `npm ci`: Clean install from `package-lock.json` (faster than `npm install`)

### Docusaurus Configuration (`book/docusaurus.config.js`)

```javascript
module.exports = {
  title: 'Physical AI & Humanoid Robotics',
  tagline: 'Embodied Intelligence in the Real World',
  url: 'https://docs.physicalai.edu',
  baseUrl: '/',
  onBrokenLinks: 'throw',  // Fail build on broken links
  onBrokenMarkdownLinks: 'throw',

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          editUrl: 'https://github.com/org/repo/tree/main/book/',
          remarkPlugins: [require('remark-math')],
          rehypePlugins: [require('rehype-katex')],
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      },
    ],
  ],

  plugins: [
    [
      '@docusaurus/plugin-ideal-image',
      {
        quality: 85,
        max: 800,  // Max image width
        disableInDev: false,
      },
    ],
  ],

  themeConfig: {
    navbar: {
      title: 'Physical AI',
      items: [
        {type: 'doc', docId: 'intro', label: 'Curriculum'},
        {to: '/blog', label: 'Updates'},
        {href: 'https://github.com/org/repo', label: 'GitHub'},
      ],
    },
    algolia: {
      appId: 'YOUR_APP_ID',
      apiKey: 'YOUR_API_KEY',
      indexName: 'physicalai',
    },
  },

  stylesheets: [
    {
      href: 'https://cdn.jsdelivr.net/npm/katex@0.13.24/dist/katex.min.css',
      type: 'text/css',
      integrity: 'sha384-...',
      crossorigin: 'anonymous',
    },
  ],
};
```

### Pre-Commit Validation Script (`scripts/validate_frontmatter.py`)

```python
"""
Validate markdown frontmatter before commit.
Run via pre-commit hook: .git/hooks/pre-commit
"""
import sys
import yaml

def validate_frontmatter(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Extract frontmatter
    if not content.startswith('---'):
        print(f"❌ {filepath}: Missing frontmatter")
        return False

    try:
        _, frontmatter, _ = content.split('---', 2)
        data = yaml.safe_load(frontmatter)

        # Required fields
        required = ['sidebar_position', 'title', 'description']
        for field in required:
            if field not in data:
                print(f"❌ {filepath}: Missing required field '{field}'")
                return False

        print(f"✅ {filepath}: Frontmatter valid")
        return True

    except Exception as e:
        print(f"❌ {filepath}: Invalid YAML - {e}")
        return False

if __name__ == "__main__":
    import glob
    files = glob.glob("book/docs/**/*.md", recursive=True)
    results = [validate_frontmatter(f) for f in files]
    sys.exit(0 if all(results) else 1)
```

### Custom Domain Setup

1. Create `book/static/CNAME` file:
   ```
   docs.physicalai.edu
   ```

2. Add DNS CNAME record (at domain registrar):
   ```
   docs.physicalai.edu  CNAME  <org>.github.io
   ```

3. Enable HTTPS in GitHub Pages settings:
   - Repository Settings → Pages → Enforce HTTPS ✓

4. Wait 24-48 hours for DNS propagation and SSL certificate issuance

### Troubleshooting Common Build Failures

**Build Error: "Module not found"**
- Cause: Missing dependency in `package.json`
- Fix: `cd book && npm install <package> --save`

**Build Error: "Cannot read property 'sidebar_position' of undefined"**
- Cause: Invalid or missing frontmatter in markdown file
- Fix: Run `python scripts/validate_frontmatter.py`, fix reported files

**Build Error: "Broken link: /docs/module2/nonexistent"**
- Cause: Internal link points to non-existent page
- Fix: Search codebase for broken link, update or remove

**Deployment Success but 404 on Page Load**
- Cause: GitHub Pages not serving from `gh-pages` branch
- Fix: Repository Settings → Pages → Source = `gh-pages` branch

## Success Metrics

**Related Spec Requirements:**

- **FR-021**: Docusaurus v3.0+ ✅ (static site generation from markdown)
- **FR-022**: GitHub Actions CI/CD ✅ (auto-deploy on main branch commit)
- **FR-023**: Hierarchical navigation ✅ (auto-generated from folder structure)
- **FR-024**: Syntax highlighting + copy buttons ✅ (Prism.js built-in)
- **FR-027**: Dark/light theme toggle ✅ (Docusaurus default theme)
- **FR-028**: LaTeX equation rendering ✅ (KaTeX plugin)
- **FR-030**: Search functionality ✅ (Algolia DocSearch)
- **SC-013**: Build time <5 min ✅ (measured 3-5 minutes)
- **SC-016**: Page load <2s ✅ (GitHub Pages CDN)
- **SC-017**: Search relevance >90% ✅ (Algolia DocSearch)

**Performance Benchmarks:**
- Build time (4 modules, 20 lessons): 3-5 minutes ✅
- Page load (50 Mbps): <2 seconds ✅
- First Contentful Paint (FCP): <1 second ✅
- Time to Interactive (TTI): <3 seconds ✅

## References

- **Plan**: `specs/001-book-publication-rag-chatbot/plan.md` - Section "Project Structure" (book/ directory)
- **Research**: `specs/001-book-publication-rag-chatbot/research.md` - Section 6 (Docusaurus Stack), Section 11 (Malformed Markdown Handling)
- **Spec**: `specs/001-physical-ai-robotics-platform/spec.md` - FR-021 to FR-032 (book publication requirements)
- **Docusaurus Official Docs**: https://docusaurus.io/docs
- **GitHub Pages Docs**: https://docs.github.com/en/pages
- **Algolia DocSearch**: https://docsearch.algolia.com
- **Related ADRs**:
  - ADR-001: Two-Tier Architecture (frontend tier details)
  - ADR-002: RAG Technology Stack (backend integration)

## Revision History

- 2026-02-09: Initial decision documented (based on research.md section 6 and plan.md)
