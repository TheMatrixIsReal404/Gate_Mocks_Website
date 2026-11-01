# -*- coding: utf-8 -*-
import sys
import re

def main():
    with open('app.js', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. CACHE & BOOKMARKS -> INDEXEDDB & CACHE
    old_cache_pat = r'// ─── CACHE & BOOKMARKS ────────────────────────────────────────────────────────\r?\nfunction saveCache\(\) \{[\s\S]*?function toggleBookmark\(questionId\) \{'
    new_cache = '''// ─── CACHE, INDEXEDDB & BOOKMARKS ────────────────────────────────────────────
const IDB_NAME = 'GATE_CSE_QUESTION_BANK';
const IDB_STORE = 'questions_store';
const IDB_VERSION = 1;

function openQuestionsIDB() {
  return new Promise(resolve => {
    if (typeof window === 'undefined' || !window.indexedDB) return resolve(null);
    try {
      const req = window.indexedDB.open(IDB_NAME, IDB_VERSION);
      req.onupgradeneeded = e => {
        const db = e.target.result;
        if (!db.objectStoreNames.contains(IDB_STORE)) {
          db.createObjectStore(IDB_STORE);
        }
      };
      req.onsuccess = e => resolve(e.target.result);
      req.onerror = () => resolve(null);
    } catch(e) {
      resolve(null);
    }
  });
}

async function idbSaveQuestions(questions) {
  if (!questions || !questions.length) return false;
  try {
    const db = await openQuestionsIDB();
    if (!db) return false;
    return new Promise(resolve => {
      const tx = db.transaction(IDB_STORE, 'readwrite');
      const store = tx.objectStore(IDB_STORE);
      store.put(questions, 'master_questions');
      tx.oncomplete = () => resolve(true);
      tx.onerror = () => resolve(false);
    });
  } catch(e) {
    return false;
  }
}

async function idbLoadQuestions() {
  try {
    const db = await openQuestionsIDB();
    if (!db) return null;
    return new Promise(resolve => {
      const tx = db.transaction(IDB_STORE, 'readonly');
      const store = tx.objectStore(IDB_STORE);
      const req = store.get('master_questions');
      req.onsuccess = () => resolve(req.result || null);
      req.onerror = () => resolve(null);
    });
  } catch(e) {
    return null;
  }
}

function mergeQuestionArrays(baseList, incomingList) {
  if (!incomingList || !incomingList.length) return baseList || [];
  if (!baseList || !baseList.length) return incomingList || [];
  const map = new Map();
  for (const q of baseList) {
    if (q && q.id) map.set(q.id, q);
  }
  for (const q of incomingList) {
    if (q && q.id) {
      const existing = map.get(q.id);
      map.set(q.id, existing ? { ...existing, ...q } : q);
    }
  }
  return Array.from(map.values());
}

function saveCache() {
  try {
    // User attempts and sessions are lightweight (<100KB) -> safe for localStorage
    localStorage.setItem(`${LS_KEY}_${uid()}`, JSON.stringify({
      attempts: state.attempts,
      testSessions: state.testSessions,
    }));
    saveBookmarks();
  } catch(e) {
    console.warn('[Cache] localStorage save:', e);
  }
  // Questions are stored safely in IndexedDB without localStorage 5MB quota restrictions
  if (state.questions && state.questions.length) {
    idbSaveQuestions(state.questions);
  }
}

async function loadCache() {
  try {
    const d = JSON.parse(localStorage.getItem(`${LS_KEY}_${uid()}`) || '{}');
    state.attempts     = d.attempts     || [];
    state.testSessions = d.testSessions || [];
    loadBookmarks();
  } catch(e) {}

  try {
    const cached = await idbLoadQuestions();
    if (cached && Array.isArray(cached) && cached.length) {
      state.questions = mergeQuestionArrays(state.questions, cached);
    }
  } catch(e) {}
}

function saveBookmarks() {
  try {
    localStorage.setItem(`gate_bookmarks_${uid()}`, JSON.stringify([...state.bookmarks]));
  } catch(e) {}
}

function loadBookmarks() {
  try {
    const raw = localStorage.getItem(`gate_bookmarks_${uid()}`);
    state.bookmarks = new Set(raw ? JSON.parse(raw) : []);
  } catch(e) {
    state.bookmarks = new Set();
  }
}

function toggleBookmark(questionId) {'''

    assert re.search(old_cache_pat, content), "Could not match old_cache_pat"
    content = re.sub(old_cache_pat, new_cache, content, count=1)
    print("✅ Step 1: CACHE, INDEXEDDB & BOOKMARKS updated.")

    # 2. LOAD FROM FIRESTORE & SETUP LISTENERS
    old_fs_pat = r'// ─── LOAD FROM FIRESTORE ──────────────────────────────────────────────────────\r?\nasync function loadFromFirestore\(\) \{[\s\S]*?// ─── NETWORK EVENTS ───────────────────────────────────────────────────────────'
    new_fs = '''// ─── LOAD FROM FIRESTORE ──────────────────────────────────────────────────────
async function loadFromFirestore() {
  setSyncStatus('syncing');
  try {
    const timeoutPromise = new Promise((_, reject) =>
      setTimeout(() => reject(new Error('timeout')), 12000)
    );
    const [questions, attempts, sessions] = await Promise.race([
      Promise.all([fsAll(qCol()), fsAll(attCol()), fsAll(sesCol())]),
      timeoutPromise
    ]);
    // Merge Firestore questions with existing/local questions so local mocks are never wiped
    state.questions    = mergeQuestionArrays(state.questions, questions);
    state.attempts     = attempts;
    state.testSessions = sessions;
    saveCache();
    state.firestoreReady = true;
    setSyncStatus('online');
    return true;
  } catch(e) {
    console.warn('[FS] Load timed out or offline:', e.message);
    setSyncStatus('offline');
    return false;
  }
}

// ─── REALTIME LISTENERS ───────────────────────────────────────────────────────
let _unQ=null, _unA=null, _unS=null;

function setupListeners() {
  if (!USE_FB) return;

  // Shared questions — merge incoming docs with state.questions
  _unQ = onSnapshot(qCol(), snap => {
    const fsQs = snap.docs.map(d=>({_id:d.id,...d.data()}));
    state.questions = mergeQuestionArrays(state.questions, fsQs);
    saveCache();
    setSyncStatus('online');
    const noTest = !document.getElementById('test-overlay')?.classList.contains('active');
    if (noTest && ['dashboard','subjects','practice','pyqs','upload'].includes(state.currentPage))
      renderPage(state.currentPage, state.currentParams||{});
  }, e=>{ console.error('[FS] q listener:', e); setSyncStatus('error'); });

  // Per-user attempts
  _unA = onSnapshot(attCol(), snap => {
    state.attempts = snap.docs.map(d=>d.data());
    saveCache();
    const noTest = !document.getElementById('test-overlay')?.classList.contains('active');
    if (noTest && ['dashboard','performance'].includes(state.currentPage))
      renderPage(state.currentPage, state.currentParams||{});
  }, e=>console.error('[FS] att listener:', e));

  // Per-user sessions
  _unS = onSnapshot(sesCol(), snap => {
    state.testSessions = snap.docs.map(d=>d.data());
    saveCache();
    const noTest = !document.getElementById('test-overlay')?.classList.contains('active');
    if (noTest && ['dashboard','mocks','pyq-exams','performance'].includes(state.currentPage))
      renderPage(state.currentPage, state.currentParams||{});
  }, e=>console.error('[FS] ses listener:', e));
}

function teardownListeners() {
  _unQ?.(); _unA?.(); _unS?.();
  _unQ=_unA=_unS=null;
}

// ─── NETWORK EVENTS ───────────────────────────────────────────────────────────'''

    assert re.search(old_fs_pat, content), "Could not match old_fs_pat"
    content = re.sub(old_fs_pat, new_fs, content, count=1)
    print("✅ Step 2: LOAD FROM FIRESTORE & SETUP LISTENERS updated.")

    # 3. BULK IMPORT, STATIC LOADER & SEED QUESTIONS
    old_bulk_pat = r'// ─── BULK IMPORT ─────────────────────────────────────────────────────────────\r?\nasync function bulkImportQuestions\(newQs\) \{[\s\S]*?// ─── LOGIN UI ─────────────────────────────────────────────────────────────────'
    new_bulk = '''// ─── BULK IMPORT ─────────────────────────────────────────────────────────────
async function bulkImportQuestions(newQs) {
  let added=0, dupes=0, invalid=0;
  const existingIds = new Set(state.questions.map(q => q.id));
  const toAdd=[];
  for (const q of newQs) {
    if (!q.id||!q.question) { invalid++; continue; }
    if (existingIds.has(q.id)) { dupes++; continue; }
    existingIds.add(q.id);
    toAdd.push(q); added++;
  }
  if (!toAdd.length) {
    showToast(`No new questions — ${dupes} duplicates, ${invalid} invalid`,'info');
    return;
  }

  // Merge into local state immediately and save to IndexedDB
  state.questions = mergeQuestionArrays(state.questions, toAdd);
  saveCache();

  if (USE_FB && db) {
    setSyncStatus('syncing');
    let uploaded = 0;
    try {
      const CHUNK = 75;
      const total = toAdd.length;
      for (let i = 0; i < total; i += CHUNK) {
        const chunk = toAdd.slice(i, i + CHUNK);
        const b = writeBatch(db);
        chunk.forEach(q => {
          b.set(qDoc(q.id), JSON.parse(JSON.stringify(q)), { merge: true });
        });
        await b.commit();
        uploaded += chunk.length;
        showToast(`☁️ Syncing to Cloud: ${uploaded} / ${total} questions...`, 'info', 1500);
      }
      setSyncStatus('online');
      showToast(`✅ Successfully synced all ${uploaded} questions to Cloud Database!`, 'success', 5000);
    } catch(e) {
      console.warn('[FS] Batch commit error:', e);
      setSyncStatus('online');
      showToast(`⚠️ Cloud sync paused at ${uploaded}/${toAdd.length}. All questions saved locally!`, 'warning', 5000);
    }
  } else {
    showToast(`✅ Added ${added} question${added>1?'s':''} locally!`, 'success', 4000);
  }

  renderUpload(document.getElementById('page-content'));
}

// ─── STATIC MASTER QUESTIONS LOADER ──────────────────────────────────────────
async function loadMasterStaticQuestions() {
  try {
    const res = await fetch('./data/sample_questions.json');
    if (res.ok) {
      const data = await res.json();
      if (Array.isArray(data) && data.length) {
        state.questions = mergeQuestionArrays(state.questions, data);
        saveCache();
      }
    }
  } catch(e) {
    console.warn('[Static] sample_questions.json load:', e);
  }
}

// ─── CLOUD SYNC UTILITY ──────────────────────────────────────────────────────
window.pushAllQuestionsToCloud = async function() {
  if (!USE_FB || !db) {
    showToast('Firebase is offline or not configured', 'error');
    return;
  }
  if (!currentUser) {
    showToast('Please sign in to sync questions to cloud', 'warning');
    return;
  }
  if (!confirm(`Sync entire question bank (${state.questions.length} questions) to Google Cloud Firestore?`)) return;

  setSyncStatus('syncing');
  showToast('Starting cloud synchronization...', 'info', 2000);

  const CHUNK = 75;
  const total = state.questions.length;
  let uploaded = 0;
  let errors = 0;

  for (let i = 0; i < total; i += CHUNK) {
    const chunk = state.questions.slice(i, i + CHUNK);
    const b = writeBatch(db);
    chunk.forEach(q => {
      b.set(qDoc(q.id), JSON.parse(JSON.stringify(q)), { merge: true });
    });
    try {
      await b.commit();
      uploaded += chunk.length;
      showToast(`☁️ Uploaded ${uploaded} / ${total} questions to Cloud...`, 'info', 1500);
    } catch(err) {
      console.warn('Batch commit error at index', i, err);
      errors++;
    }
  }

  setSyncStatus('online');
  if (errors === 0) {
    showToast(`✅ Successfully synced all ${uploaded} questions to Cloud Firestore!`, 'success', 6000);
  } else {
    showToast(`⚠️ Synced ${uploaded} questions with ${errors} batch retries.`, 'warning', 6000);
  }
  renderUpload(document.getElementById('page-content'));
};

// ─── SEED SAMPLE QUESTIONS ───────────────────────────────────────────────────
async function seedSampleQuestions() {
  await loadMasterStaticQuestions();
}

// ─── LOGIN UI ─────────────────────────────────────────────────────────────────'''

    assert re.search(old_bulk_pat, content), "Could not match old_bulk_pat"
    content = re.sub(old_bulk_pat, new_bulk, content, count=1)
    print("✅ Step 3: BULK IMPORT & CLOUD SYNC updated.")

    # 4. HANDLE SIGN OUT
    old_signout = '''async function handleSignOut() {
  if (!confirm('Sign out?')) return;
  teardownListeners();
  state.questions=[]; state.attempts=[]; state.testSessions=[];
  await signOut(auth);
  // onAuthStateChanged fires → shows login
}'''
    new_signout = '''async function handleSignOut() {
  if (!confirm('Sign out?')) return;
  teardownListeners();
  // Clear user-private attempts & test sessions only; preserve question bank in memory & IndexedDB
  state.attempts=[]; state.testSessions=[];
  await signOut(auth);
  // onAuthStateChanged fires → shows login
}'''
    assert old_signout in content, "Could not find old_signout"
    content = content.replace(old_signout, new_signout)
    print("✅ Step 4: handleSignOut updated.")

    # 5. BOOTAPP
    old_boot_pat = r'// ─── INIT ─────────────────────────────────────────────────────────────────────\r?\nasync function bootApp\(user\) \{[\s\S]*?navigate\(\'dashboard\'\);\r?\n\}'
    new_boot = '''// ─── INIT ─────────────────────────────────────────────────────────────────────
async function bootApp(user) {
  currentUser = user;
  updateTopbarUser();

  // 1. Instantly load cached user attempts/sessions and IndexedDB questions
  await loadCache();

  // 2. Fetch master static questions from ./data/sample_questions.json (6,218+ questions,
  //    including all 30 easy mocks and PYQs) and merge with state.questions
  await loadMasterStaticQuestions();

  // 3. If Firebase is active, fetch cloud questions from Firestore and merge
  if (USE_FB) {
    document.getElementById('loading-msg').textContent = 'Syncing questions with cloud…';
    const ok = await loadFromFirestore();
    if (ok) {
      setupListeners();
    } else {
      setSyncStatus('offline');
      document.getElementById('loading-msg').textContent = 'Using local question bank…';
    }
  } else {
    setSyncStatus('offline');
  }

  // 4. Save merged result to IndexedDB
  saveCache();

  // Show app
  document.getElementById('loading-screen').style.display = 'none';
  document.getElementById('page-content').classList.remove('hidden');

  // Sidebar nav
  document.querySelectorAll('.sidebar-nav-item').forEach(item=>{
    item.addEventListener('click', ()=>navigate(item.dataset.page));
  });

  setupMobileMenu();
  setupKeyboardShortcuts();
  navigate('dashboard');
}'''
    assert re.search(old_boot_pat, content), "Could not match old_boot_pat"
    content = re.sub(old_boot_pat, new_boot, content, count=1)
    print("✅ Step 5: bootApp updated.")

    # 6. PUSH TO CLOUD BUTTON IN UPLOAD UI
    old_btn = '''<div class="flex gap-2 mt-4">
            <button class="btn btn-primary" onclick="document.getElementById('file-input').click()">📂 Choose File</button>
            <button class="btn btn-secondary" onclick="downloadSampleJSON()">⬇ Sample JSON</button>
          </div>'''
    new_btn = '''<div class="flex gap-2 mt-4" style="flex-wrap:wrap">
            <button class="btn btn-primary" onclick="document.getElementById('file-input').click()">📂 Choose File</button>
            <button class="btn btn-secondary" onclick="downloadSampleJSON()">⬇ Sample JSON</button>
            ${USE_FB ? `<button class="btn btn-secondary" onclick="pushAllQuestionsToCloud()" style="background:rgba(20,184,166,0.15);color:var(--teal);border-color:var(--teal)">☁️ Push Questions to Cloud (${state.questions.length})</button>` : ''}
          </div>'''
    if old_btn in content:
        content = content.replace(old_btn, new_btn)
        print("✅ Step 6: Upload UI Push to Cloud button added.")

    with open('app.js', 'w', encoding='utf-8') as f:
        f.write(content)
    print("🎉 Successfully wrote updated app.js!")

if __name__ == '__main__':
    main()
