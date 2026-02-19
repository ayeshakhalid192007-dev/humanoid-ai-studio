// @ts-check

/**
 * Docusaurus plugin for RAG Chatbot widget
 * Provides RAG chat functionality integrated into Docusaurus site
 */

const path = require('path');

module.exports = function RagChatPlugin(context, options) {
  return {
    name: 'docusaurus-rag-chat-plugin',

    getThemePath() {
      return path.resolve(__dirname, './theme');
    },

    getClientModules() {
      return [require.resolve('./theme/ChatbotWrapper')];
    },

    configureWebpack(config, isServer, utils) {
      return {
        resolve: {
          alias: {
            '@site/src/plugins/rag-chat-plugin': path.resolve(__dirname, './src'),
          },
        },
      };
    },

    // Inject the chatbot wrapper div in HTML
    injectHtmlTags() {
      return {
        postBodyTags: [
          // This div will host our chatbot component
          '<div id="rag-chat-wrapper" style="z-index: 10000;"></div>',
        ],
      };
    },
  };
};