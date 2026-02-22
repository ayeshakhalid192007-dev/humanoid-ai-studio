// @ts-check
// Note: type annotations allow type checking and IDE autocompletion

const {themes} = require('prism-react-renderer');
const lightCodeTheme = themes.github;
const darkCodeTheme = themes.dracula;

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Physical AI & Humanoid Robotics Platform',
  tagline: 'Learn ROS 2, simulation, perception, and voice-to-action pipelines',
  favicon: 'img/favicon.ico',

  // Set the production url of your site here
  url: 'https://yourusername.github.io', // TODO: Replace with your GitHub username
  baseUrl: '/', // Adjusted for local development

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: 'yourusername', // TODO: Replace with your GitHub username
  projectName: '', // Adjusted for local development - empty string for default baseUrl '/'

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  customFields: {
    backendUrl: process.env.BACKEND_URL || 'http://localhost:8000',
  },

  // Even if you don't use internalization, you can use this field to set useful
  // metadata like html lang. For example, if your site is Chinese, you may want
  // to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl:
            'https://github.com/yourusername/physical_ai/tree/main/book/', // TODO: Replace
        },
        blog: false, // Disable blog for now
        theme: {
          customCss: [
            require.resolve('./src/css/custom.css'),
            require.resolve('./src/css/glassmorphism.css'),
            require.resolve('./src/css/futuristic-minimalism.css'),
          ],
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      // Replace with your project's social card
      image: 'img/docusaurus-social-card.jpg',
      navbar: {
        title: 'Physical AI Platform',
        logo: {
          alt: 'Physical AI Logo',
          src: 'img/logo.svg',
        },
        items: [
          {
            href: 'https://github.com/yourusername/physical_ai', // TODO: Replace
            label: 'GitHub',
            position: 'right',
          },
        ],
        // Hide the default navbar items since we're using a swizzled navbar
        hideOnScroll: false,
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Curriculum',
            items: [
              {
                label: 'Module 1: ROS 2 Middleware',
                to: '/docs/module1/intro',
              },
              {
                label: 'Module 2: Simulation',
                to: '/docs/module2/intro',
              },
              {
                label: 'Module 3: Perception',
                to: '/docs/module3/intro',
              },
              {
                label: 'Module 4: Voice-to-Action',
                to: '/docs/module4/intro',
              },
            ],
          },
          {
            title: 'Resources',
            items: [
              {
                label: 'ROS 2 Documentation',
                href: 'https://docs.ros.org/en/humble/',
              },
              {
                label: 'Gazebo',
                href: 'https://gazebosim.org/',
              },
              {
                label: 'OpenAI API',
                href: 'https://platform.openai.com/docs',
              },
            ],
          },
          {
            title: 'Community',
            items: [
              {
                label: 'GitHub',
                href: 'https://github.com/yourusername/physical_ai', // TODO: Replace
              },
              {
                label: 'Issues',
                href: 'https://github.com/yourusername/physical_ai/issues', // TODO: Replace
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} Physical AI Platform. Built with Docusaurus.`,
      },
      prism: {
        theme: lightCodeTheme,
        darkTheme: darkCodeTheme,
        additionalLanguages: ['python', 'bash', 'yaml', 'markup'],
      },
      // Color mode configuration
      colorMode: {
        defaultMode: 'light',
        disableSwitch: false,
        respectPrefersColorScheme: true,
      },
      // Algolia search (optional - configure when ready)
      // algolia: {
      //   appId: 'YOUR_APP_ID',
      //   apiKey: 'YOUR_SEARCH_API_KEY',
      //   indexName: 'physical_ai',
      // },
    }),

  // Markdown features - mermaid disabled for compatibility
  // markdown: {
  //   mermaid: true,
  // },

  // Plugins
  plugins: [
    require.resolve('./src/plugins/rag-chat-plugin'),
  ],

  themes: [
    //   [
    //     require.resolve("@easyops-cn/docusaurus-search-local"),
    //     /** @type {import("@easyops-cn/docusaurus-search-local").PluginOptions} */
    //     ({
    //       hashed: true,
    //       language: ["en"],
    //       highlightSearchTermsOnTargetPage: true,
    //       explicitSearchResultPath: true,
    //     }),
    //   ],
  ],

  // Scripts for chatbot widget (to be added in Phase 3)
  scripts: [
    // {
    //   src: '/chatbot-widget.js',
    //   async: true,
    // },
  ],
};

module.exports = config;
