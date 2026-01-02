import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';

export default [
  {
    path: '/blog',
    component: ComponentCreator('/blog', 'b2f'),
    exact: true
  },
  {
    path: '/blog/archive',
    component: ComponentCreator('/blog/archive', '182'),
    exact: true
  },
  {
    path: '/blog/authors',
    component: ComponentCreator('/blog/authors', '0b7'),
    exact: true
  },
  {
    path: '/blog/authors/all-sebastien-lorber-articles',
    component: ComponentCreator('/blog/authors/all-sebastien-lorber-articles', '4a1'),
    exact: true
  },
  {
    path: '/blog/authors/yangshun',
    component: ComponentCreator('/blog/authors/yangshun', 'a68'),
    exact: true
  },
  {
    path: '/blog/first-blog-post',
    component: ComponentCreator('/blog/first-blog-post', '89a'),
    exact: true
  },
  {
    path: '/blog/long-blog-post',
    component: ComponentCreator('/blog/long-blog-post', '9ad'),
    exact: true
  },
  {
    path: '/blog/mdx-blog-post',
    component: ComponentCreator('/blog/mdx-blog-post', 'e9f'),
    exact: true
  },
  {
    path: '/blog/tags',
    component: ComponentCreator('/blog/tags', '287'),
    exact: true
  },
  {
    path: '/blog/tags/docusaurus',
    component: ComponentCreator('/blog/tags/docusaurus', '704'),
    exact: true
  },
  {
    path: '/blog/tags/facebook',
    component: ComponentCreator('/blog/tags/facebook', '858'),
    exact: true
  },
  {
    path: '/blog/tags/hello',
    component: ComponentCreator('/blog/tags/hello', '299'),
    exact: true
  },
  {
    path: '/blog/tags/hola',
    component: ComponentCreator('/blog/tags/hola', '00d'),
    exact: true
  },
  {
    path: '/blog/welcome',
    component: ComponentCreator('/blog/welcome', 'd2b'),
    exact: true
  },
  {
    path: '/markdown-page',
    component: ComponentCreator('/markdown-page', '3d7'),
    exact: true
  },
  {
    path: '/docs',
    component: ComponentCreator('/docs', 'ee5'),
    routes: [
      {
        path: '/docs',
        component: ComponentCreator('/docs', 'd2a'),
        routes: [
          {
            path: '/docs',
            component: ComponentCreator('/docs', 'fba'),
            routes: [
              {
                path: '/docs',
                component: ComponentCreator('/docs', '8ae'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/book_content',
                component: ComponentCreator('/docs/book_content', '2a5'),
                exact: true
              },
              {
                path: '/docs/guides/docusaurus-global-components',
                component: ComponentCreator('/docs/guides/docusaurus-global-components', '2c0'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/guides/floating-widget-implementation',
                component: ComponentCreator('/docs/guides/floating-widget-implementation', '942'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/module-1/chapter-1-ros2-fundamentals',
                component: ComponentCreator('/docs/module-1/chapter-1-ros2-fundamentals', 'd17'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/module-1/chapter-2-python-agents-ros2',
                component: ComponentCreator('/docs/module-1/chapter-2-python-agents-ros2', '7b2'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/module-1/chapter-3-urdf-humanoid-models',
                component: ComponentCreator('/docs/module-1/chapter-3-urdf-humanoid-models', '91f'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/module-2/chapter-1-physics-simulation-gazebo',
                component: ComponentCreator('/docs/module-2/chapter-1-physics-simulation-gazebo', '056'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/module-2/chapter-2-high-fidelity-unity',
                component: ComponentCreator('/docs/module-2/chapter-2-high-fidelity-unity', '191'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/module-2/chapter-3-sensor-simulation',
                component: ComponentCreator('/docs/module-2/chapter-3-sensor-simulation', '7b2'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/module-3/chapter-1-nvidia-isaac-sim',
                component: ComponentCreator('/docs/module-3/chapter-1-nvidia-isaac-sim', 'd2e'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/module-3/chapter-2-isaac-ros-perception',
                component: ComponentCreator('/docs/module-3/chapter-2-isaac-ros-perception', '102'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/module-3/chapter-3-nav2-navigation',
                component: ComponentCreator('/docs/module-3/chapter-3-nav2-navigation', 'd91'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/module-4/chapter-1-voice-to-action',
                component: ComponentCreator('/docs/module-4/chapter-1-voice-to-action', '086'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/module-4/chapter-2-cognitive-planning-with-llms',
                component: ComponentCreator('/docs/module-4/chapter-2-cognitive-planning-with-llms', 'bc9'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/module-4/chapter-3-capstone-autonomous-humanoid',
                component: ComponentCreator('/docs/module-4/chapter-3-capstone-autonomous-humanoid', '48a'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/tutorial-basics/congratulations',
                component: ComponentCreator('/docs/tutorial-basics/congratulations', '70e'),
                exact: true
              },
              {
                path: '/docs/tutorial-basics/create-a-blog-post',
                component: ComponentCreator('/docs/tutorial-basics/create-a-blog-post', '315'),
                exact: true
              },
              {
                path: '/docs/tutorial-basics/create-a-document',
                component: ComponentCreator('/docs/tutorial-basics/create-a-document', 'f86'),
                exact: true
              },
              {
                path: '/docs/tutorial-basics/create-a-page',
                component: ComponentCreator('/docs/tutorial-basics/create-a-page', '9f6'),
                exact: true
              },
              {
                path: '/docs/tutorial-basics/deploy-your-site',
                component: ComponentCreator('/docs/tutorial-basics/deploy-your-site', 'b91'),
                exact: true
              },
              {
                path: '/docs/tutorial-basics/markdown-features',
                component: ComponentCreator('/docs/tutorial-basics/markdown-features', '272'),
                exact: true
              },
              {
                path: '/docs/tutorial-extras/manage-docs-versions',
                component: ComponentCreator('/docs/tutorial-extras/manage-docs-versions', 'a34'),
                exact: true
              },
              {
                path: '/docs/tutorial-extras/translate-your-site',
                component: ComponentCreator('/docs/tutorial-extras/translate-your-site', '739'),
                exact: true
              }
            ]
          }
        ]
      }
    ]
  },
  {
    path: '/',
    component: ComponentCreator('/', '2e1'),
    exact: true
  },
  {
    path: '*',
    component: ComponentCreator('*'),
  },
];
