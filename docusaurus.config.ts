import { themes as prismThemes } from 'prism-react-renderer';
import type { Config } from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

// This runs in Node.js - Don't use client-side code here

const config: Config = {
  title: 'Physical AI & Humanoid Robotics',
  tagline: 'Bridging the gap between digital AI and physical robots',
  favicon: 'img/favicon.ico',

  future: {
    v4: true,
  },

  trailingSlash: false,

  // ✅ YOUR DEPLOYED VERCEL URL
  url: 'https://rag-book.vercel.app',
  baseUrl: '/',

  organizationName: 'Sajida-haider',
  projectName: 'Rag_book',

  onBrokenLinks: 'throw',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          sidebarCollapsible: true,
          editUrl:
            'https://github.com/Sajida-haider/Rag_book',
        },

        blog: {
          showReadingTime: true,
          feedOptions: {
            type: ['rss', 'atom'],
            xslt: true,
          },
          editUrl:
            'https://github.com/Sajida-haider/Rag_book',
          onInlineTags: 'warn',
          onInlineAuthors: 'warn',
          onUntruncatedBlogPosts: 'warn',
        },

        // ✅ VERY IMPORTANT FOR RAG
        sitemap: {
          changefreq: 'weekly',
          priority: 0.5,
          filename: 'sitemap.xml',
        },

        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    image: 'img/docusaurus-social-card.jpg',

    colorMode: {
      respectPrefersColorScheme: true,
    },

    tableOfContents: {
      minHeadingLevel: 2,
      maxHeadingLevel: 5,
    },

    docs: {
      sidebar: {
        autoCollapseCategories: true,
      },
    },

    navbar: {
      title: 'Physical AI & Robotics',
      logo: {
        alt: 'My Site Logo',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'tutorialSidebar',
          position: 'left',
          label: 'Book',
        },
        {
          href: 'https://github.com/Sajida-haider/Rag_book',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },

    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            {
              label: 'Module 1: ROS 2',
              to: '/docs/module-1/chapter-1-ros2-fundamentals',
            },
          ],
        },
        {
          title: 'Community',
          items: [
            {
              label: 'GitHub',
              href: 'https://github.com/Sajida-haider/Rag_book',
            },
            {
              label: 'Discussions',
              href: 'https://github.com/Sajida-haider/Rag_book/discussions',
            },
            {
              label: 'Issues',
              href: 'https://github.com/Sajida-haider/Rag_book/issues',
            },
          ],
        },
        {
          title: 'More',
          items: [
            {
              label: 'Physical AI & Robotics',
              to: '/',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Physical AI & Humanoid Robotics. Built with Docusaurus.`,
    },

    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['python', 'bash', 'json'],
    },

    stylesheets: [
      {
        href: 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Roboto:wght@400;500;700&display=swap',
        rel: 'stylesheet',
      },
    ],
  } satisfies Preset.ThemeConfig,
};

export default config;
