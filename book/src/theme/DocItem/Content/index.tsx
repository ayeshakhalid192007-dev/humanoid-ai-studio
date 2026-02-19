/**
 * Swizzled DocItem/Content component
 *
 * Wraps the original Docusaurus DocItem Content component
 * and injects the ChapterToolbar above the doc content.
 * Enhanced with glassmorphism styling and animations.
 */

import React from "react";
import Content from "@theme-original/DocItem/Content";
import type ContentType from "@theme/DocItem/Content";
import type { WrapperProps } from "@docusaurus/types";
import BrowserOnly from "@docusaurus/BrowserOnly";
import { motion } from 'framer-motion';

type Props = WrapperProps<typeof ContentType>;

function ChapterToolbarWrapper({
  children,
}: {
  children: React.ReactNode;
}) {
  // Get current doc slug from URL path
  // Docusaurus docs URLs are like /docs/module1/lesson1-ros2-basics
  const { useLocation } =
    require("@docusaurus/router") as typeof import("@docusaurus/router");
  const ChapterToolbar =
    require("../../../components/ChapterToolbar").default;

  const location = useLocation();
  const path = location.pathname;

  // Extract chapter slug from /docs/module1/lesson1-ros2-basics
  const docsPrefix = "/docs/";
  if (!path.startsWith(docsPrefix)) {
    return <>{children}</>;
  }

  const chapterSlug = path.slice(docsPrefix.length).replace(/\/$/, "");

  if (!chapterSlug) {
    return <>{children}</>;
  }

  return (
    <ChapterToolbar chapterSlug={chapterSlug}>
      {children}
    </ChapterToolbar>
  );
}

export default function ContentWrapper(props: Props): JSX.Element {
  return (
    <BrowserOnly fallback={<Content {...props} />}>
      {() => (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          className="glass-card doc-content"
        >
          <ChapterToolbarWrapper>
            <Content {...props} />
          </ChapterToolbarWrapper>
        </motion.div>
      )}
    </BrowserOnly>
  );
}
