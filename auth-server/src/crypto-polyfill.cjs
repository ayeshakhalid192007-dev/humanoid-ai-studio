/**
 * Crypto polyfill — loaded via --require BEFORE any ESM modules.
 * Sets globalThis.crypto so that @better-auth/utils/random.mjs
 * can reference `crypto` as a bare global identifier.
 */
'use strict';
const nodeCrypto = require('crypto');
if (!globalThis.crypto?.subtle) {
  globalThis.crypto = nodeCrypto.webcrypto;
}
