// ─────────────────────────────────────────────────────────────────────────────
// firebase.js  —  Firebase initialisation (CDN ESM, no npm needed)
// ─────────────────────────────────────────────────────────────────────────────
import { initializeApp }                            from "https://www.gstatic.com/firebasejs/11.10.0/firebase-app.js";
import { getFirestore, enableIndexedDbPersistence } from "https://www.gstatic.com/firebasejs/11.10.0/firebase-firestore.js";
import { getAuth }                                  from "https://www.gstatic.com/firebasejs/11.10.0/firebase-auth.js";

const config = window.__FIREBASE_CONFIG;

const isPlaceholder = !config || !config.apiKey
  || config.apiKey.includes('PASTE')
  || config.projectId.includes('PASTE')
  || config.apiKey === 'YOUR_API_KEY';

let app, db, auth;

if (config && config.apiKey && !isPlaceholder) {
  app  = initializeApp(config);
  db   = getFirestore(app);
  auth = getAuth(app);

  enableIndexedDbPersistence(db).catch(err => {
    if (err.code !== 'failed-precondition' && err.code !== 'unimplemented') {
      console.warn('[Firebase] Persistence error:', err.code);
    }
  });

  console.log('[Firebase] ✅ Connected:', config.projectId);
} else {
  console.warn('[Firebase] ⚠️  No valid config — running in offline/localStorage mode.');
}

export { db, auth };
