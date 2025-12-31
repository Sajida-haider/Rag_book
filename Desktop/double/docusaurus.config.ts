import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

// Optional: import prism themes if needed
import prismThemes from 'prism-react-renderer/themes/github';
import draculaTheme from 'prism-react-renderer/themes/dracula';

const config: Config = {
  title: 'Physical AI & Humanoid Robotics',
  tagline: 'Bridging the gap between digital AI and physical robots',
  favicon: 'img/favicon.ico',

  future: { v4: true },
  trailingSlash: false,

  url: 'https://mybook-murex.vercel.app', // Your live site
  baseUrl: '/',

  organizationName: 'Sajida-haider',
  projectName: 'My-book',

  onBrokenLinks: 'throw',
  i18n: { defaultLocale: 'en', locales: ['en'] },

  presets: [
    [
      'classic',
      {
        docs: {
          path: 'docs',
          routeBasePath: '/',  // Important: docs served at root
          sidebarPath: require.resolve('./sidebars.ts'),
          sidebarCollapsible: true,
          editUrl: 'https://github.com/Sajida-haider/My-book',
        },
        blog: false,  // Disable blog
        theme: { customCss: require.resolve('./src/css/custom.css') },
        sitemap: {
          changefreq: 'weekly',
          priority: 0.5,
          filename: 'sitemap.xml',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    image: 'img/docusaurus-social-card.jpg',
    colorMode: { respectPrefersColorScheme: true },
    tableOfContents: { minHeadingLevel: 2, maxHeadingLevel: 5 },
    docs: { sidebar: { autoCollapseCategories: true } },
    navbar: {
      title: 'Physical AI & Robotics',
      logo: { alt: 'My Site Logo', src: 'img/logo.svg' },
      items: [
        { type: 'docSidebar', sidebarId: 'tutorialSidebar', position: 'left', label: 'Book' },
        { href: 'https://github.com/Sajida-haider/My-book', label: 'GitHub', position: 'right' },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [{ label: 'Module 1: ROS 2', to: '/module-1/chapter-1-ros2-fundamentals' }],
        },
        { title: 'More', items: [{ label: 'GitHub', href: 'https://github.com/Sajida-haider/My-book' }] },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Physical AI & Humanoid Robotics. Built with Docusaurus.`,
    },
    prism: { theme: prismThemes, darkTheme: draculaTheme, additionalLanguages: ['python', 'bash', 'json'] },
  } satisfies Preset.ThemeConfig,
};

export default config;

