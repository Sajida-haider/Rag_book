import React from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <h1 className="hero__title">{siteConfig.title}</h1>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/docs/module-1/chapter-1-ros2-fundamentals">
            Get Started
          </Link>
        </div>
      </div>
    </header>
  );
}

function NavigationBoxes() {
  const boxes = [
    {
      title: 'The Robotic Nervous System (ROS 2)',
      to: '/docs/module-1/chapter-1-ros2-fundamentals'
    },
    {
      title: 'The Digital Twin (Gazebo & Unity)',
      to: '/docs/module-2/chapter-1-physics-simulation-gazebo'
    },
    {
      title: 'The AI-Robot Brain (NVIDIA Isaac™)',
      to: '/docs/module-3/chapter-1-nvidia-isaac-sim'
    },
    {
      title: 'Vision-Language-Action (VLA)',
      to: '/docs/module-4/chapter-1-voice-to-action'
    }
  ];

  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {boxes.map((box, idx) => (
            <div key={idx} className={clsx('col col--3', styles.featureBox)}>
              <Link to={box.to} className={styles.moduleBox}>
                {box.title}
              </Link>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export default function Home() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={`Hello from ${siteConfig.title}`}
      description="Physical AI & Humanoid Robotics Documentation">
      <HomepageHeader />
      <NavigationBoxes />
    </Layout>
  );
}