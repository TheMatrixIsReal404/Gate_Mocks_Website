// ─────────────────────────────────────────────────────────────────────────────

// GATE CSE PRACTICE PLATFORM — app.js

// ─────────────────────────────────────────────────────────────────────────────

// Data Architecture:

//   questions/          → SHARED by all users (single question bank)

//   users/{uid}/attempts/     → private per-user practice attempts

//   users/{uid}/testSessions/ → private per-user test history

// ─────────────────────────────────────────────────────────────────────────────



import { db, auth } from './firebase.js';



import {

  collection, doc, getDoc, getDocs, setDoc, addDoc,

  deleteDoc, writeBatch, onSnapshot, serverTimestamp, query, where

} from "https://www.gstatic.com/firebasejs/11.10.0/firebase-firestore.js";



import {

  onAuthStateChanged, signInWithEmailAndPassword,

  createUserWithEmailAndPassword, signOut,

  GoogleAuthProvider, signInWithPopup, signInWithRedirect, getRedirectResult, updateProfile,
  sendPasswordResetEmail

} from "https://www.gstatic.com/firebasejs/11.10.0/firebase-auth.js";



// ─── CONSTANTS ────────────────────────────────────────────────────────────────

const ADMIN_EMAILS = new Set([

  'sahu1999ankit@gmail.com',

  'admin_1@gateprep.com',

  'admin_2@gateprep.com',

  'admin_3@gateprep.com',

  'admin_4@gateprep.com',

  'admin_5@gateprep.com',

  'admin_6@gateprep.com',

  'admin_7@gateprep.com',

  'admin_8@gateprep.com',

  'admin_9@gateprep.com',

  'admin_10@gateprep.com'

]);

// 32 Curated Hard Mocks (Mocks 1-4, 10, 11-14, 25, 29-32, 38-41, 59-68, 71, 73, 83 + paper-systems)
const CURATED_HARD_MOCK_IDS = new Set([
  'mock-me24-f-adv1', 'mock-me24-f-adv2', 'mock-me24-f-adv3', 'mock-me24-f-adv4',
  'mock-me24-mock-4',
  'mock-me23-f-adv1', 'mock-me23-f-adv2', 'mock-me23-f-adv3', 'mock-me23-f-adv4',
  'mock-go-ts25-aim-05',
  'mock-go-ts26-aim-04', 'mock-go-ts26-aim-05-s1', 'mock-go-ts26-aim-05-s2', 'mock-go-ts26-aim-06',
  'mock-go-ts25-mg-06', 'mock-go-ts25-mg-07', 'mock-go-ts25-mg-08', 'mock-go-ts25-mg-09',
  'mock-flm-03', 'mock-flm-11', 'mock-flm-12', 'mock-flm-13', 'mock-flm-14', 'mock-flm-15',
  'mock-flm-16', 'mock-flm-17', 'mock-flm-18', 'mock-flm-19', 'mock-flm-20',
  'mock-full-hard', 'mock-full-002', 'mock-cat2-set5', 'paper-systems'
]);



function checkIsAdminUser(user) {

  if (!user) return false;

  const email = (user.email || '').toLowerCase().trim();

  if (ADMIN_EMAILS.has(email)) return true;

  return false;

}



const SUBJECTS = [

  { id:'c-programming',           name:'C Programming',           icon:'💻', color:'#3b82f6', desc:'Programming in C, recursion, memory layout, pointers, arrays and structures.' },

  { id:'data-structures',         name:'Data Structures',         icon:'🗂️', color:'#6c63ff', desc:'Arrays, stacks, queues, linked lists, trees, binary search trees, binary heaps, graphs.' },

  { id:'algorithms',              name:'Algorithms',              icon:'⚙️', color:'#f97316', desc:'Searching, sorting, hashing, asymptotic complexity, greedy, dynamic programming, divide & conquer, MST, shortest paths.' },

  { id:'operating-systems',       name:'Operating Systems',       icon:'🖥️', color:'#22c55e', desc:'System calls, processes, threads, IPC, concurrency & synchronization, deadlocks, CPU & I/O scheduling, virtual memory, file systems.' },

  { id:'computer-networks',       name:'Computer Networks',       icon:'🌐', color:'#14b8a6', desc:'Layering, switching, MAC, Ethernet, distance vector & link state routing, IPv4 fragmentation, CIDR, NAT, TCP, sockets, DNS, HTTP.' },

  { id:'dbms',                    name:'DBMS',                    icon:'🗄️', color:'#ef4444', desc:'ER-model, relational algebra, tuple calculus, SQL, integrity constraints, normal forms, B and B+ trees, transactions, concurrency.' },

  { id:'theory-of-computation',   name:'Theory of Computation',  icon:'🔣', color:'#a855f7', desc:'Regular expressions, finite automata, CFG, push-down automata, pumping lemma, Turing machines, undecidability.' },

  { id:'compiler-design',         name:'Compiler Design',         icon:'🔧', color:'#f59e0b', desc:'Lexical analysis, parsing, syntax-directed translation, runtime environments, intermediate code, local optimisation, data flow analyses.' },

  { id:'digital-logic',           name:'Digital Logic',           icon:'🔌', color:'#06b6d4', desc:'Boolean algebra, algebraic technique, K-maps, tabular method, combinational & sequential circuits, fixed and floating point arithmetic.' },

  { id:'computer-organization',   name:'Computer Organization',   icon:'🖩', color:'#84cc16', desc:'Instruction set & addressing modes, ALU design, hardwired/microprogrammed control unit, cache mapping, I/O DMA, pipelining hazards.' },

  { id:'discrete-mathematics',    name:'Discrete Mathematics',    icon:'🔢', color:'#ec4899', desc:'Propositional & first order logic, sets, relations, partial orders, lattices, monoids, groups, graph matching/colouring, combinatorics.' },

  { id:'engineering-mathematics', name:'Engineering Mathematics', icon:'📐', color:'#8b5cf6', desc:'Matrices, determinants, eigenvalues, LU decomposition, calculus, distributions (uniform, normal, exponential, Poisson, binomial), Bayes theorem.' },

  { id:'aptitude',                name:'Aptitude',                icon:'🧮', color:'#0ea5e9', desc:'Verbal deduction, English grammar, numerical computation, estimation, and analytical reasoning.' },

];



const MOCK_TESTS = [
  {
    id: 'mock-me24-f-adv1',
    provider: "Comprehensive Series",
    type: 'full',
    difficulty: 'hard',
    rating: 8.2,
    cutoff: '25-28',
    air100: '66-70',
    tier: 'Advance Level Full Mock',
    name: "Mock 1",
    subject: null,
    questions: 69,
    duration: 180,
    marks: 100,
    desc: "High-difficulty capstone mock testing multi-concept analytical questions and intricate derivations (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Hard (Rating: 8.2/10)."
  },
  {
    id: 'mock-me24-f-adv2',
    provider: "Comprehensive Series",
    type: 'full',
    difficulty: 'hard',
    rating: 8.4,
    cutoff: '24-27',
    air100: '65-69',
    tier: 'Advance Level Full Mock',
    name: "Mock 2",
    subject: null,
    questions: 66,
    duration: 180,
    marks: 100,
    desc: "High-difficulty capstone mock testing multi-concept analytical questions and intricate derivations (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Hard (Rating: 8.4/10)."
  },
  {
    id: 'mock-me24-f-adv3',
    provider: "Comprehensive Series",
    type: 'full',
    difficulty: 'hard',
    rating: 8.5,
    cutoff: '23-26',
    air100: '64-68',
    tier: 'Advance Level Full Mock',
    name: "Mock 3",
    subject: null,
    questions: 67,
    duration: 180,
    marks: 100,
    desc: "High-difficulty capstone mock testing multi-concept analytical questions and intricate derivations (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Hard (Rating: 8.5/10)."
  },
  {
    id: 'mock-me24-f-adv4',
    provider: "Comprehensive Series",
    type: 'full',
    difficulty: 'hard',
    rating: 8.6,
    cutoff: '22-25',
    air100: '63-67',
    tier: 'Advance Level Full Mock',
    name: "Mock 4",
    subject: null,
    questions: 68,
    duration: 180,
    marks: 100,
    desc: "High-difficulty capstone mock testing multi-concept analytical questions and intricate derivations (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Hard (Rating: 8.6/10)."
  },
  {
    id: 'mock-me24-f-bsc1',
    provider: "Comprehensive Series",
    type: 'full',
    difficulty: 'medium',
    rating: 6.0,
    cutoff: '29-33',
    air100: '72-77',
    tier: 'Basic Foundational Full Mock',
    name: "Mock 5",
    subject: null,
    questions: 67,
    duration: 180,
    marks: 100,
    desc: "Balanced full-length test designed to build speed, accuracy, and foundational confidence (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 6.0/10)."
  },
  {
    id: 'mock-me24-f-bsc2',
    provider: "Comprehensive Series",
    type: 'full',
    difficulty: 'medium',
    rating: 6.2,
    cutoff: '28-32',
    air100: '71-76',
    tier: 'Basic Foundational Full Mock',
    name: "Mock 6",
    subject: null,
    questions: 68,
    duration: 180,
    marks: 100,
    desc: "Balanced full-length test designed to build speed, accuracy, and foundational confidence (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 6.2/10)."
  },
  {
    id: 'mock-me24-f-bsc3',
    provider: "Comprehensive Series",
    type: 'full',
    difficulty: 'medium',
    rating: 6.3,
    cutoff: '28-32',
    air100: '70-75',
    tier: 'Basic Foundational Full Mock',
    name: "Mock 7",
    subject: null,
    questions: 69,
    duration: 180,
    marks: 100,
    desc: "Balanced full-length test designed to build speed, accuracy, and foundational confidence (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 6.3/10)."
  },
  {
    id: 'mock-me24-f-bsc4',
    provider: "Comprehensive Series",
    type: 'full',
    difficulty: 'medium',
    rating: 6.4,
    cutoff: '27-31',
    air100: '69-74',
    tier: 'Basic Foundational Full Mock',
    name: "Mock 8",
    subject: null,
    questions: 67,
    duration: 180,
    marks: 100,
    desc: "Balanced full-length test designed to build speed, accuracy, and foundational confidence (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 6.4/10)."
  },
  {
    id: 'mock-me24-mock-3',
    provider: "Comprehensive Series",
    type: 'full',
    difficulty: 'medium',
    rating: 6.8,
    cutoff: '28-32',
    air100: '70-75',
    tier: 'National All-India Mock',
    name: "Mock 9",
    subject: null,
    questions: 67,
    duration: 180,
    marks: 100,
    desc: "Authentic nationwide mock exam simulating official GATE testing conditions across the complete syllabus (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 6.8/10)."
  },
  {
    id: 'mock-me24-mock-4',
    provider: "Comprehensive Series",
    type: 'full',
    difficulty: 'hard',
    rating: 7.2,
    cutoff: '26-30',
    air100: '67-72',
    tier: 'National All-India Mock',
    name: "Mock 10",
    subject: null,
    questions: 67,
    duration: 180,
    marks: 100,
    desc: "Authentic nationwide mock exam simulating official GATE testing conditions across the complete syllabus (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Hard (Rating: 7.2/10)."
  },
  {
    id: 'mock-me23-f-adv1',
    provider: "Comprehensive Series",
    type: 'full',
    difficulty: 'hard',
    rating: 8.0,
    cutoff: '25-28',
    air100: '66-70',
    tier: 'Advance Level Full Mock',
    name: "Mock 11",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "High-difficulty capstone mock testing multi-concept analytical questions and intricate derivations (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Hard (Rating: 8.0/10)."
  },
  {
    id: 'mock-me23-f-adv2',
    provider: "Comprehensive Series",
    type: 'full',
    difficulty: 'hard',
    rating: 8.2,
    cutoff: '24-27',
    air100: '65-69',
    tier: 'Advance Level Full Mock',
    name: "Mock 12",
    subject: null,
    questions: 67,
    duration: 180,
    marks: 100,
    desc: "High-difficulty capstone mock testing multi-concept analytical questions and intricate derivations (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Hard (Rating: 8.2/10)."
  },
  {
    id: 'mock-me23-f-adv3',
    provider: "Comprehensive Series",
    type: 'full',
    difficulty: 'hard',
    rating: 8.3,
    cutoff: '24-27',
    air100: '65-69',
    tier: 'Advance Level Full Mock',
    name: "Mock 13",
    subject: null,
    questions: 69,
    duration: 180,
    marks: 100,
    desc: "High-difficulty capstone mock testing multi-concept analytical questions and intricate derivations (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Hard (Rating: 8.3/10)."
  },
  {
    id: 'mock-me23-f-adv4',
    provider: "Comprehensive Series",
    type: 'full',
    difficulty: 'hard',
    rating: 8.4,
    cutoff: '23-26',
    air100: '64-68',
    tier: 'Advance Level Full Mock',
    name: "Mock 14",
    subject: null,
    questions: 66,
    duration: 180,
    marks: 100,
    desc: "High-difficulty capstone mock testing multi-concept analytical questions and intricate derivations (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Hard (Rating: 8.4/10)."
  },
  {
    id: 'mock-me23-f-bsc1',
    provider: "Comprehensive Series",
    type: 'full',
    difficulty: 'easy',
    rating: 5.6,
    cutoff: '32-36',
    air100: '74-79',
    tier: 'Basic Foundational Full Mock',
    name: "Mock 15",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "Balanced full-length test designed to build speed, accuracy, and foundational confidence (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Easy (Rating: 5.6/10)."
  },
  {
    id: 'mock-me23-f-bsc2',
    provider: "Comprehensive Series",
    type: 'full',
    difficulty: 'medium',
    rating: 6.0,
    cutoff: '29-33',
    air100: '72-77',
    tier: 'Basic Foundational Full Mock',
    name: "Mock 16",
    subject: null,
    questions: 68,
    duration: 180,
    marks: 100,
    desc: "Balanced full-length test designed to build speed, accuracy, and foundational confidence (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 6.0/10)."
  },
  {
    id: 'mock-me23-f-bsc3',
    provider: "Comprehensive Series",
    type: 'full',
    difficulty: 'medium',
    rating: 6.1,
    cutoff: '28-32',
    air100: '71-76',
    tier: 'Basic Foundational Full Mock',
    name: "Mock 17",
    subject: null,
    questions: 67,
    duration: 180,
    marks: 100,
    desc: "Balanced full-length test designed to build speed, accuracy, and foundational confidence (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 6.1/10)."
  },
  {
    id: 'mock-me23-f-bsc4',
    provider: "Comprehensive Series",
    type: 'full',
    difficulty: 'medium',
    rating: 6.2,
    cutoff: '28-32',
    air100: '70-75',
    tier: 'Basic Foundational Full Mock',
    name: "Mock 18",
    subject: null,
    questions: 67,
    duration: 180,
    marks: 100,
    desc: "Balanced full-length test designed to build speed, accuracy, and foundational confidence (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 6.2/10)."
  },
  {
    id: 'mock-me23-mock-2',
    provider: "Comprehensive Series",
    type: 'full',
    difficulty: 'medium',
    rating: 6.5,
    cutoff: '28-32',
    air100: '70-75',
    tier: 'National All-India Mock',
    name: "Mock 19",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "Authentic nationwide mock exam simulating official GATE testing conditions across the complete syllabus (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 6.5/10)."
  },
  {
    id: 'mock-me23-mock-3',
    provider: "Comprehensive Series",
    type: 'full',
    difficulty: 'medium',
    rating: 6.7,
    cutoff: '28-32',
    air100: '70-75',
    tier: 'National All-India Mock',
    name: "Mock 20",
    subject: null,
    questions: 68,
    duration: 180,
    marks: 100,
    desc: "Authentic nationwide mock exam simulating official GATE testing conditions across the complete syllabus (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 6.7/10)."
  },
  {
    id: 'mock-me23-mock-4',
    provider: "Comprehensive Series",
    type: 'full',
    difficulty: 'medium',
    rating: 6.9,
    cutoff: '27-31',
    air100: '69-74',
    tier: 'National All-India Mock',
    name: "Mock 21",
    subject: null,
    questions: 67,
    duration: 180,
    marks: 100,
    desc: "Authentic nationwide mock exam simulating official GATE testing conditions across the complete syllabus (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 6.9/10)."
  },
  {
    id: 'mock-go-ts25-aim-02',
    provider: "National Series",
    type: 'full',
    difficulty: 'medium',
    rating: 6.8,
    cutoff: '28-32',
    air100: '70-75',
    tier: 'All-India National Mock',
    name: "Mock 22",
    subject: null,
    questions: 63,
    duration: 180,
    marks: 100,
    desc: "Full-length exam replicating official GATE pattern with in-depth solutions (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 6.8/10)."
  },
  {
    id: 'mock-go-ts25-aim-03',
    provider: "National Series",
    type: 'full',
    difficulty: 'medium',
    rating: 7.0,
    cutoff: '27-31',
    air100: '69-74',
    tier: 'All-India National Mock',
    name: "Mock 23",
    subject: null,
    questions: 63,
    duration: 180,
    marks: 100,
    desc: "Full-length exam replicating official GATE pattern with in-depth solutions (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 7.0/10)."
  },
  {
    id: 'mock-go-ts25-aim-04',
    provider: "National Series",
    type: 'full',
    difficulty: 'medium',
    rating: 7.1,
    cutoff: '26-30',
    air100: '68-73',
    tier: 'All-India National Mock',
    name: "Mock 24",
    subject: null,
    questions: 63,
    duration: 180,
    marks: 100,
    desc: "Full-length exam replicating official GATE pattern with in-depth solutions (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 7.1/10)."
  },
  {
    id: 'mock-go-ts25-aim-05',
    provider: "National Series",
    type: 'full',
    difficulty: 'hard',
    rating: 7.5,
    cutoff: '25-29',
    air100: '66-71',
    tier: 'All-India National Mock',
    name: "Mock 25",
    subject: null,
    questions: 62,
    duration: 180,
    marks: 100,
    desc: "Full-length exam replicating official GATE pattern with in-depth solutions (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Hard (Rating: 7.5/10)."
  },
  {
    id: 'mock-go-ts26-aim-01',
    provider: "National Series",
    type: 'full',
    difficulty: 'medium',
    rating: 6.8,
    cutoff: '28-32',
    air100: '70-75',
    tier: 'All-India National Mock',
    name: "Mock 26",
    subject: null,
    questions: 62,
    duration: 180,
    marks: 100,
    desc: "Full-length exam replicating official GATE pattern with in-depth solutions (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 6.8/10)."
  },
  {
    id: 'mock-go-ts26-aim-02',
    provider: "National Series",
    type: 'full',
    difficulty: 'medium',
    rating: 7.0,
    cutoff: '27-31',
    air100: '69-74',
    tier: 'All-India National Mock',
    name: "Mock 27",
    subject: null,
    questions: 61,
    duration: 180,
    marks: 100,
    desc: "Full-length exam replicating official GATE pattern with in-depth solutions (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 7.0/10)."
  },
  {
    id: 'mock-go-ts26-aim-03',
    provider: "National Series",
    type: 'full',
    difficulty: 'medium',
    rating: 7.2,
    cutoff: '26-30',
    air100: '68-73',
    tier: 'All-India National Mock',
    name: "Mock 28",
    subject: null,
    questions: 61,
    duration: 180,
    marks: 100,
    desc: "Full-length exam replicating official GATE pattern with in-depth solutions (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 7.2/10)."
  },
  {
    id: 'mock-go-ts26-aim-04',
    provider: "National Series",
    type: 'full',
    difficulty: 'hard',
    rating: 7.6,
    cutoff: '25-29',
    air100: '66-71',
    tier: 'All-India National Mock',
    name: "Mock 29",
    subject: null,
    questions: 60,
    duration: 180,
    marks: 100,
    desc: "Full-length exam replicating official GATE pattern with in-depth solutions (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Hard (Rating: 7.6/10)."
  },
  {
    id: 'mock-go-ts26-aim-05-s1',
    provider: "National Series",
    type: 'full',
    difficulty: 'hard',
    rating: 7.7,
    cutoff: '24-28',
    air100: '65-70',
    tier: 'All-India National Mock',
    name: "Mock 30",
    subject: null,
    questions: 59,
    duration: 180,
    marks: 100,
    desc: "Full-length exam replicating official GATE pattern with in-depth solutions (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Hard (Rating: 7.7/10)."
  },
  {
    id: 'mock-go-ts26-aim-05-s2',
    provider: "National Series",
    type: 'full',
    difficulty: 'hard',
    rating: 7.7,
    cutoff: '24-28',
    air100: '65-70',
    tier: 'All-India National Mock',
    name: "Mock 31",
    subject: null,
    questions: 59,
    duration: 180,
    marks: 100,
    desc: "Full-length exam replicating official GATE pattern with in-depth solutions (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Hard (Rating: 7.7/10)."
  },
  {
    id: 'mock-go-ts26-aim-06',
    provider: "National Series",
    type: 'full',
    difficulty: 'hard',
    rating: 8.0,
    cutoff: '23-27',
    air100: '64-69',
    tier: 'All-India National Mock',
    name: "Mock 32",
    subject: null,
    questions: 58,
    duration: 180,
    marks: 100,
    desc: "Full-length exam replicating official GATE pattern with in-depth solutions (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Hard (Rating: 8.0/10)."
  },
  {
    id: 'mock-go-ts25-mg-01',
    provider: "National Series",
    type: 'full',
    difficulty: 'medium',
    rating: 6.8,
    cutoff: '28-32',
    air100: '70-75',
    tier: 'Full Syllabus Mock GATE',
    name: "Mock 33",
    subject: null,
    questions: 62,
    duration: 180,
    marks: 100,
    desc: "Full-syllabus mock testing core CS subjects and GA with standard GATE difficulty (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 6.8/10)."
  },
  {
    id: 'mock-go-ts25-mg-02',
    provider: "National Series",
    type: 'full',
    difficulty: 'medium',
    rating: 6.9,
    cutoff: '28-32',
    air100: '70-75',
    tier: 'Full Syllabus Mock GATE',
    name: "Mock 34",
    subject: null,
    questions: 58,
    duration: 180,
    marks: 100,
    desc: "Full-syllabus mock testing core CS subjects and GA with standard GATE difficulty (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 6.9/10)."
  },
  {
    id: 'mock-go-ts25-mg-03',
    provider: "National Series",
    type: 'full',
    difficulty: 'medium',
    rating: 7.0,
    cutoff: '27-31',
    air100: '69-74',
    tier: 'Full Syllabus Mock GATE',
    name: "Mock 35",
    subject: null,
    questions: 60,
    duration: 180,
    marks: 100,
    desc: "Full-syllabus mock testing core CS subjects and GA with standard GATE difficulty (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 7.0/10)."
  },
  {
    id: 'mock-go-ts25-mg-04',
    provider: "National Series",
    type: 'full',
    difficulty: 'medium',
    rating: 7.1,
    cutoff: '26-30',
    air100: '68-73',
    tier: 'Full Syllabus Mock GATE',
    name: "Mock 36",
    subject: null,
    questions: 61,
    duration: 180,
    marks: 100,
    desc: "Full-syllabus mock testing core CS subjects and GA with standard GATE difficulty (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 7.1/10)."
  },
  {
    id: 'mock-go-ts25-mg-05',
    provider: "National Series",
    type: 'full',
    difficulty: 'medium',
    rating: 7.2,
    cutoff: '26-30',
    air100: '68-73',
    tier: 'Full Syllabus Mock GATE',
    name: "Mock 37",
    subject: null,
    questions: 60,
    duration: 180,
    marks: 100,
    desc: "Full-syllabus mock testing core CS subjects and GA with standard GATE difficulty (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 7.2/10)."
  },
  {
    id: 'mock-go-ts25-mg-06',
    provider: "National Series",
    type: 'full',
    difficulty: 'hard',
    rating: 7.4,
    cutoff: '25-29',
    air100: '67-72',
    tier: 'Full Syllabus Mock GATE',
    name: "Mock 38",
    subject: null,
    questions: 57,
    duration: 180,
    marks: 100,
    desc: "Full-syllabus mock testing core CS subjects and GA with standard GATE difficulty (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Hard (Rating: 7.4/10)."
  },
  {
    id: 'mock-go-ts25-mg-07',
    provider: "National Series",
    type: 'full',
    difficulty: 'hard',
    rating: 7.5,
    cutoff: '25-29',
    air100: '66-71',
    tier: 'Full Syllabus Mock GATE',
    name: "Mock 39",
    subject: null,
    questions: 49,
    duration: 180,
    marks: 100,
    desc: "Full-syllabus mock testing core CS subjects and GA with standard GATE difficulty (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Hard (Rating: 7.5/10)."
  },
  {
    id: 'mock-go-ts25-mg-08',
    provider: "National Series",
    type: 'full',
    difficulty: 'hard',
    rating: 7.6,
    cutoff: '24-28',
    air100: '65-70',
    tier: 'Full Syllabus Mock GATE',
    name: "Mock 40",
    subject: null,
    questions: 55,
    duration: 180,
    marks: 100,
    desc: "Full-syllabus mock testing core CS subjects and GA with standard GATE difficulty (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Hard (Rating: 7.6/10)."
  },
  {
    id: 'mock-go-ts25-mg-09',
    provider: "National Series",
    type: 'full',
    difficulty: 'hard',
    rating: 7.8,
    cutoff: '24-28',
    air100: '65-70',
    tier: 'Full Syllabus Mock GATE',
    name: "Mock 41",
    subject: null,
    questions: 56,
    duration: 180,
    marks: 100,
    desc: "Full-syllabus mock testing core CS subjects and GA with standard GATE difficulty (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Hard (Rating: 7.8/10)."
  },
  {
    id: 'mock-go-ts25-mg-14',
    provider: "National Series",
    type: 'full',
    difficulty: 'medium',
    rating: 6.6,
    cutoff: '29-33',
    air100: '71-76',
    tier: 'Full Syllabus Mock GATE',
    name: "Mock 42",
    subject: null,
    questions: 51,
    duration: 180,
    marks: 100,
    desc: "Full-syllabus mock testing core CS subjects and GA with standard GATE difficulty (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 6.6/10)."
  },
  {
    id: 'mock-go25-mg-01',
    provider: "National Series",
    type: 'full',
    difficulty: 'medium',
    rating: 6.5,
    cutoff: '30-34',
    air100: '72-77',
    tier: 'Standard Test Series Mock',
    name: "Mock 43",
    subject: null,
    questions: 60,
    duration: 180,
    marks: 100,
    desc: "Full-syllabus GATE CS mock paper with verified detailed solutions (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 6.5/10)."
  },
  {
    id: 'mock-go25-mg-02',
    provider: "National Series",
    type: 'full',
    difficulty: 'medium',
    rating: 6.6,
    cutoff: '29-33',
    air100: '71-76',
    tier: 'Standard Test Series Mock',
    name: "Mock 44",
    subject: null,
    questions: 59,
    duration: 180,
    marks: 100,
    desc: "Full-syllabus GATE CS mock paper with verified detailed solutions (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 6.6/10)."
  },
  {
    id: 'mock-go25-mg-03',
    provider: "National Series",
    type: 'full',
    difficulty: 'medium',
    rating: 6.7,
    cutoff: '28-32',
    air100: '70-75',
    tier: 'Standard Test Series Mock',
    name: "Mock 45",
    subject: null,
    questions: 57,
    duration: 180,
    marks: 100,
    desc: "Full-syllabus GATE CS mock paper with verified detailed solutions (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 6.7/10)."
  },
  {
    id: 'mock-go25-mg-04',
    provider: "National Series",
    type: 'full',
    difficulty: 'medium',
    rating: 6.6,
    cutoff: '29-33',
    air100: '71-76',
    tier: 'Standard Test Series Mock',
    name: "Mock 46",
    subject: null,
    questions: 52,
    duration: 180,
    marks: 100,
    desc: "Full-syllabus GATE CS mock paper with verified detailed solutions (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 6.6/10)."
  },
  {
    id: 'mock-go25-mg-05',
    provider: "National Series",
    type: 'full',
    difficulty: 'medium',
    rating: 6.8,
    cutoff: '28-32',
    air100: '70-75',
    tier: 'Standard Test Series Mock',
    name: "Mock 47",
    subject: null,
    questions: 52,
    duration: 180,
    marks: 100,
    desc: "Full-syllabus GATE CS mock paper with verified detailed solutions (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 6.8/10)."
  },
  {
    id: 'mock-go25-mg-06',
    provider: "National Series",
    type: 'full',
    difficulty: 'medium',
    rating: 6.7,
    cutoff: '28-32',
    air100: '70-75',
    tier: 'Standard Test Series Mock',
    name: "Mock 48",
    subject: null,
    questions: 48,
    duration: 180,
    marks: 100,
    desc: "Full-syllabus GATE CS mock paper with verified detailed solutions (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 6.7/10)."
  },
  {

    id: 'mock-flm-01',
    provider: "Compendium FLM",

    type: 'full',

    difficulty: 'medium',

    rating: 4.5,

    cutoff: '31-33',

    air100: '74-78',

    tier: 'Standard GATE',

    name: "Mock 49",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Comprehensive full-syllabus simulation covering multi-topic numerical and conceptual challenges (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 4.5/10)."

  },
  {

    id: 'mock-flm-02',
    provider: "Compendium FLM",

    type: 'full',

    difficulty: 'medium',

    rating: 5.0,

    cutoff: '30-32',

    air100: '73-77',

    tier: 'Standard GATE',

    name: "Mock 50",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Comprehensive full-syllabus simulation covering multi-topic numerical and conceptual challenges (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 5.0/10)."

  },
  {

    id: 'mock-flm-03',
    provider: "Compendium FLM",

    type: 'full',

    difficulty: 'medium',

    rating: 5.5,

    cutoff: '29-31',

    air100: '72-76',

    tier: 'Standard GATE',

    name: "Mock 51",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Comprehensive full-syllabus simulation covering multi-topic numerical and conceptual challenges (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 5.5/10)."

  },
  {

    id: 'mock-flm-04',
    provider: "Compendium FLM",

    type: 'full',

    difficulty: 'medium',

    rating: 5.4,

    cutoff: '29-31',

    air100: '72-76',

    tier: 'Standard GATE',

    name: "Mock 52",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Comprehensive full-syllabus simulation covering multi-topic numerical and conceptual challenges (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 5.4/10)."

  },
  {

    id: 'mock-flm-05',
    provider: "Compendium FLM",

    type: 'full',

    difficulty: 'medium',

    rating: 5.2,

    cutoff: '30-32',

    air100: '73-77',

    tier: 'Standard GATE',

    name: "Mock 53",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Comprehensive full-syllabus simulation covering multi-topic numerical and conceptual challenges (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 5.2/10)."

  },
  {

    id: 'mock-flm-06',
    provider: "Compendium FLM",

    type: 'full',

    difficulty: 'medium',

    rating: 5.8,

    cutoff: '28-30',

    air100: '71-75',

    tier: 'Standard GATE',

    name: "Mock 54",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Comprehensive full-syllabus simulation covering multi-topic numerical and conceptual challenges (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 5.8/10)."

  },
  {

    id: 'mock-flm-07',
    provider: "Compendium FLM",

    type: 'full',

    difficulty: 'medium',

    rating: 5.6,

    cutoff: '28-30',

    air100: '71-75',

    tier: 'Standard GATE',

    name: "Mock 55",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Comprehensive full-syllabus simulation covering multi-topic numerical and conceptual challenges (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 5.6/10)."

  },
  {

    id: 'mock-flm-08',
    provider: "Compendium FLM",

    type: 'full',

    difficulty: 'medium',

    rating: 6.0,

    cutoff: '27-29',

    air100: '70-74',

    tier: 'Standard GATE',

    name: "Mock 56",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Comprehensive full-syllabus simulation covering multi-topic numerical and conceptual challenges (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 6.0/10)."

  },
  {

    id: 'mock-flm-09',
    provider: "Compendium FLM",

    type: 'full',

    difficulty: 'medium',

    rating: 6.1,

    cutoff: '27-29',

    air100: '70-74',

    tier: 'Standard GATE',

    name: "Mock 57",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Comprehensive full-syllabus simulation covering multi-topic numerical and conceptual challenges (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 6.1/10)."

  },
  {

    id: 'mock-flm-10',
    provider: "Compendium FLM",

    type: 'full',

    difficulty: 'medium',

    rating: 5.9,

    cutoff: '28-30',

    air100: '71-75',

    tier: 'Standard GATE',

    name: "Mock 58",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Comprehensive full-syllabus simulation covering multi-topic numerical and conceptual challenges (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 5.9/10)."

  },
  {

    id: 'mock-flm-11',
    provider: "Compendium FLM",

    type: 'full',

    difficulty: 'hard',

    rating: 6.8,

    cutoff: '25-27',

    air100: '66-70',

    tier: 'Rank Booster',

    name: "Mock 59",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Comprehensive full-syllabus simulation covering multi-topic numerical and conceptual challenges (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Hard (Rating: 6.8/10)."

  },
  {

    id: 'mock-flm-12',
    provider: "Compendium FLM",

    type: 'full',

    difficulty: 'hard',

    rating: 7.5,

    cutoff: '24-26',

    air100: '65-69',

    tier: 'Rank Booster',

    name: "Mock 60",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Comprehensive full-syllabus simulation covering multi-topic numerical and conceptual challenges (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Hard (Rating: 7.5/10)."

  },
  {

    id: 'mock-flm-13',
    provider: "Compendium FLM",

    type: 'full',

    difficulty: 'hard',

    rating: 7.0,

    cutoff: '25-27',

    air100: '66-70',

    tier: 'Rank Booster',

    name: "Mock 61",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Comprehensive full-syllabus simulation covering multi-topic numerical and conceptual challenges (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Hard (Rating: 7.0/10)."

  },
  {

    id: 'mock-flm-14',
    provider: "Compendium FLM",

    type: 'full',

    difficulty: 'hard',

    rating: 7.4,

    cutoff: '24-26',

    air100: '65-69',

    tier: 'Rank Booster',

    name: "Mock 62",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Comprehensive full-syllabus simulation covering multi-topic numerical and conceptual challenges (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Hard (Rating: 7.4/10)."

  },
  {

    id: 'mock-flm-15',
    provider: "Compendium FLM",

    type: 'full',

    difficulty: 'hard',

    rating: 8.0,

    cutoff: '23-25',

    air100: '63-67',

    tier: 'High Difficulty',

    name: "Mock 63",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Comprehensive full-syllabus simulation covering multi-topic numerical and conceptual challenges (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Hard (Rating: 8.0/10)."

  },
  {

    id: 'mock-flm-16',
    provider: "Compendium FLM",

    type: 'full',

    difficulty: 'hard',

    rating: 7.8,

    cutoff: '23-25',

    air100: '63-67',

    tier: 'High Difficulty',

    name: "Mock 64",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Comprehensive full-syllabus simulation covering multi-topic numerical and conceptual challenges (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Hard (Rating: 7.8/10)."

  },
  {

    id: 'mock-flm-17',
    provider: "Compendium FLM",

    type: 'full',

    difficulty: 'hard',

    rating: 7.9,

    cutoff: '23-25',

    air100: '63-67',

    tier: 'High Difficulty',

    name: "Mock 65",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Comprehensive full-syllabus simulation covering multi-topic numerical and conceptual challenges (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Hard (Rating: 7.9/10)."

  },
  {

    id: 'mock-flm-18',
    provider: "Compendium FLM",

    type: 'full',

    difficulty: 'hard',

    rating: 8.4,

    cutoff: '22-24',

    air100: '62-66',

    tier: 'Advanced Hard',

    name: "Mock 66",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Comprehensive full-syllabus simulation covering multi-topic numerical and conceptual challenges (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Hard (Rating: 8.4/10)."

  },
  {

    id: 'mock-flm-19',
    provider: "Compendium FLM",

    type: 'full',

    difficulty: 'hard',

    rating: 8.6,

    cutoff: '21-23',

    air100: '60-65',

    tier: 'Advanced Hard',

    name: "Mock 67",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Comprehensive full-syllabus simulation covering multi-topic numerical and conceptual challenges (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Hard (Rating: 8.6/10)."

  },
  {

    id: 'mock-flm-20',
    provider: "Compendium FLM",

    type: 'full',

    difficulty: 'hard',

    rating: 9.2,

    cutoff: '20-22',

    air100: '58-63',

    tier: 'Capstone Challenge',

    name: "Mock 68",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Comprehensive full-syllabus simulation covering multi-topic numerical and conceptual challenges (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Hard (Rating: 9.2/10)."

  },
  {

    id: 'mock-full-easy',
    provider: "Standard Full Mock",

    type: 'full',

    difficulty: 'easy',

    name: "Mock 69",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Comprehensive GATE CSE standard simulation across all subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Easy (Rating: 7.0/10)."

  },
  {

    id: 'mock-full-med',
    provider: "Standard Full Mock",

    type: 'full',

    difficulty: 'medium',

    name: "Mock 70",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Comprehensive GATE CSE standard simulation across all subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 7.0/10)."

  },
  {

    id: 'mock-full-hard',
    provider: "Standard Full Mock",

    type: 'full',

    difficulty: 'hard',

    name: "Mock 71",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Comprehensive GATE CSE standard simulation across all subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Hard (Rating: 7.0/10)."

  },
  {

    id: 'mock-full-001',
    provider: "Standard Full Mock",

    type: 'full',

    difficulty: 'medium',

    name: "Mock 72",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Comprehensive GATE CSE standard simulation across all subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 7.0/10)."

  },
  {

    id: 'mock-full-002',
    provider: "Standard Full Mock",

    type: 'full',

    difficulty: 'hard',

    name: "Mock 73",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Comprehensive GATE CSE standard simulation across all subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Hard (Rating: 7.0/10)."

  },
  {

    id: 'mock-cat1-set1',
    provider: "Category Core CS",

    type: 'full',

    difficulty: 'easy',

    name: "Mock 74",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "High-weightage topic-focused full-syllabus mock covering core concepts (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Easy (Rating: 7.0/10)."

  },
  {

    id: 'mock-cat1-set2',
    provider: "Category Core CS",

    type: 'full',

    difficulty: 'easy',

    name: "Mock 75",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "High-weightage topic-focused full-syllabus mock covering core concepts (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Easy (Rating: 7.0/10)."

  },
  {

    id: 'mock-cat1-set3',
    provider: "Category Core CS",

    type: 'full',

    difficulty: 'medium',

    name: "Mock 76",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "High-weightage topic-focused full-syllabus mock covering core concepts (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 7.0/10)."

  },
  {

    id: 'mock-cat1-set4',
    provider: "Category Core CS",

    type: 'full',

    difficulty: 'medium',

    name: "Mock 77",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "High-weightage topic-focused full-syllabus mock covering core concepts (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 7.0/10)."

  },
  {

    id: 'mock-cat1-set5',
    provider: "Category Core CS",

    type: 'full',

    difficulty: 'medium',

    name: "Mock 78",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "High-weightage topic-focused full-syllabus mock covering core concepts (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 7.0/10)."

  },
  {

    id: 'mock-cat2-set1',
    provider: "Category Core CS",

    type: 'full',

    difficulty: 'medium',

    name: "Mock 79",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "High-weightage topic-focused full-syllabus mock covering core concepts (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 7.0/10)."

  },
  {

    id: 'mock-cat2-set2',
    provider: "Category Core CS",

    type: 'full',

    difficulty: 'medium',

    name: "Mock 80",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "High-weightage topic-focused full-syllabus mock covering core concepts (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 7.0/10)."

  },
  {

    id: 'mock-cat2-set3',
    provider: "Category Core CS",

    type: 'full',

    difficulty: 'medium',

    name: "Mock 81",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "High-weightage topic-focused full-syllabus mock covering core concepts (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 7.0/10)."

  },
  {

    id: 'mock-cat2-set4',
    provider: "Category Core CS",

    type: 'full',

    difficulty: 'medium',

    name: "Mock 82",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "High-weightage topic-focused full-syllabus mock covering core concepts (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 7.0/10)."

  },
  {

    id: 'mock-cat2-set5',
    provider: "Category Core CS",

    type: 'full',

    difficulty: 'hard',

    name: "Mock 83",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "High-weightage topic-focused full-syllabus mock covering core concepts (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Hard (Rating: 7.0/10)."

  },
  {

    id: 'mock-med-01',
    provider: "Standard Series",

    type: 'full',

    difficulty: 'medium',

    rating: 4.8,

    cutoff: '31-33',

    air100: '74-78',

    tier: 'Standard GATE (Medium)',

    name: "Mock 84",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Standard official GATE difficulty with balanced distribution of MCQs, MSQs, and NATs across all subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 4.8/10)."

  },
  {

    id: 'mock-med-02',
    provider: "Standard Series",

    type: 'full',

    difficulty: 'medium',

    rating: 4.8,

    cutoff: '31-33',

    air100: '74-78',

    tier: 'Standard GATE (Medium)',

    name: "Mock 85",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Standard official GATE difficulty with balanced distribution of MCQs, MSQs, and NATs across all subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 4.8/10)."

  },
  {

    id: 'mock-med-03',
    provider: "Standard Series",

    type: 'full',

    difficulty: 'medium',

    rating: 4.9,

    cutoff: '31-33',

    air100: '74-78',

    tier: 'Standard GATE (Medium)',

    name: "Mock 86",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Standard official GATE difficulty with balanced distribution of MCQs, MSQs, and NATs across all subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 4.9/10)."

  },
  {

    id: 'mock-med-04',
    provider: "Standard Series",

    type: 'full',

    difficulty: 'medium',

    rating: 4.9,

    cutoff: '31-33',

    air100: '74-78',

    tier: 'Standard GATE (Medium)',

    name: "Mock 87",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Standard official GATE difficulty with balanced distribution of MCQs, MSQs, and NATs across all subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 4.9/10)."

  },
  {

    id: 'mock-med-05',
    provider: "Standard Series",

    type: 'full',

    difficulty: 'medium',

    rating: 4.9,

    cutoff: '31-33',

    air100: '74-78',

    tier: 'Standard GATE (Medium)',

    name: "Mock 88",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Standard official GATE difficulty with balanced distribution of MCQs, MSQs, and NATs across all subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 4.9/10)."

  },
  {

    id: 'mock-med-06',
    provider: "Standard Series",

    type: 'full',

    difficulty: 'medium',

    rating: 5.0,

    cutoff: '31-33',

    air100: '74-78',

    tier: 'Standard GATE (Medium)',

    name: "Mock 89",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Standard official GATE difficulty with balanced distribution of MCQs, MSQs, and NATs across all subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 5.0/10)."

  },
  {

    id: 'mock-med-07',
    provider: "Standard Series",

    type: 'full',

    difficulty: 'medium',

    rating: 5.0,

    cutoff: '31-33',

    air100: '74-78',

    tier: 'Standard GATE (Medium)',

    name: "Mock 90",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Standard official GATE difficulty with balanced distribution of MCQs, MSQs, and NATs across all subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 5.0/10)."

  },
  {

    id: 'mock-med-08',
    provider: "Standard Series",

    type: 'full',

    difficulty: 'medium',

    rating: 5.0,

    cutoff: '31-33',

    air100: '74-78',

    tier: 'Standard GATE (Medium)',

    name: "Mock 91",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Standard official GATE difficulty with balanced distribution of MCQs, MSQs, and NATs across all subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 5.0/10)."

  },
  {

    id: 'mock-med-09',
    provider: "Standard Series",

    type: 'full',

    difficulty: 'medium',

    rating: 5.0,

    cutoff: '31-33',

    air100: '74-78',

    tier: 'Standard GATE (Medium)',

    name: "Mock 92",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Standard official GATE difficulty with balanced distribution of MCQs, MSQs, and NATs across all subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 5.0/10)."

  },
  {

    id: 'mock-med-10',
    provider: "Standard Series",

    type: 'full',

    difficulty: 'medium',

    rating: 5.1,

    cutoff: '30-32',

    air100: '73-77',

    tier: 'Standard GATE (Medium)',

    name: "Mock 93",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Standard official GATE difficulty with balanced distribution of MCQs, MSQs, and NATs across all subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 5.1/10)."

  },
  {

    id: 'mock-med-11',
    provider: "Standard Series",

    type: 'full',

    difficulty: 'medium',

    rating: 5.1,

    cutoff: '30-32',

    air100: '73-77',

    tier: 'Standard GATE (Medium)',

    name: "Mock 94",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Standard official GATE difficulty with balanced distribution of MCQs, MSQs, and NATs across all subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 5.1/10)."

  },
  {

    id: 'mock-med-12',
    provider: "Standard Series",

    type: 'full',

    difficulty: 'medium',

    rating: 5.1,

    cutoff: '30-32',

    air100: '73-77',

    tier: 'Standard GATE (Medium)',

    name: "Mock 95",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Standard official GATE difficulty with balanced distribution of MCQs, MSQs, and NATs across all subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 5.1/10)."

  },
  {

    id: 'mock-med-13',
    provider: "Standard Series",

    type: 'full',

    difficulty: 'medium',

    rating: 5.2,

    cutoff: '30-32',

    air100: '73-77',

    tier: 'Standard GATE (Medium)',

    name: "Mock 96",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Standard official GATE difficulty with balanced distribution of MCQs, MSQs, and NATs across all subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 5.2/10)."

  },
  {

    id: 'mock-med-14',
    provider: "Standard Series",

    type: 'full',

    difficulty: 'medium',

    rating: 5.2,

    cutoff: '30-32',

    air100: '73-77',

    tier: 'Standard GATE (Medium)',

    name: "Mock 97",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Standard official GATE difficulty with balanced distribution of MCQs, MSQs, and NATs across all subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 5.2/10)."

  },
  {

    id: 'mock-med-15',
    provider: "Standard Series",

    type: 'full',

    difficulty: 'medium',

    rating: 5.2,

    cutoff: '30-32',

    air100: '73-77',

    tier: 'Standard GATE (Medium)',

    name: "Mock 98",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Standard official GATE difficulty with balanced distribution of MCQs, MSQs, and NATs across all subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 5.2/10)."

  },
  {

    id: 'mock-med-16',
    provider: "Standard Series",

    type: 'full',

    difficulty: 'medium',

    rating: 5.2,

    cutoff: '30-32',

    air100: '73-77',

    tier: 'Standard GATE (Medium)',

    name: "Mock 99",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Standard official GATE difficulty with balanced distribution of MCQs, MSQs, and NATs across all subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 5.2/10)."

  },
  {

    id: 'mock-med-17',
    provider: "Standard Series",

    type: 'full',

    difficulty: 'medium',

    rating: 5.3,

    cutoff: '30-32',

    air100: '73-77',

    tier: 'Standard GATE (Medium)',

    name: "Mock 100",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Standard official GATE difficulty with balanced distribution of MCQs, MSQs, and NATs across all subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 5.3/10)."

  },
  {

    id: 'mock-med-18',
    provider: "Standard Series",

    type: 'full',

    difficulty: 'medium',

    rating: 5.3,

    cutoff: '30-32',

    air100: '73-77',

    tier: 'Standard GATE (Medium)',

    name: "Mock 101",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Standard official GATE difficulty with balanced distribution of MCQs, MSQs, and NATs across all subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 5.3/10)."

  },
  {

    id: 'mock-med-19',
    provider: "Standard Series",

    type: 'full',

    difficulty: 'medium',

    rating: 5.3,

    cutoff: '30-32',

    air100: '73-77',

    tier: 'Standard GATE (Medium)',

    name: "Mock 102",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Standard official GATE difficulty with balanced distribution of MCQs, MSQs, and NATs across all subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 5.3/10)."

  },
  {

    id: 'mock-med-20',
    provider: "Standard Series",

    type: 'full',

    difficulty: 'medium',

    rating: 5.4,

    cutoff: '29-31',

    air100: '72-76',

    tier: 'Standard GATE (Medium)',

    name: "Mock 103",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Standard official GATE difficulty with balanced distribution of MCQs, MSQs, and NATs across all subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 5.4/10)."

  },
  {

    id: 'mock-med-21',
    provider: "Standard Series",

    type: 'full',

    difficulty: 'medium',

    rating: 5.4,

    cutoff: '29-31',

    air100: '72-76',

    tier: 'Standard GATE (Medium)',

    name: "Mock 104",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Standard official GATE difficulty with balanced distribution of MCQs, MSQs, and NATs across all subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 5.4/10)."

  },
  {

    id: 'mock-med-22',
    provider: "Standard Series",

    type: 'full',

    difficulty: 'medium',

    rating: 5.4,

    cutoff: '29-31',

    air100: '72-76',

    tier: 'Standard GATE (Medium)',

    name: "Mock 105",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Standard official GATE difficulty with balanced distribution of MCQs, MSQs, and NATs across all subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 5.4/10)."

  },
  {

    id: 'mock-med-23',
    provider: "Standard Series",

    type: 'full',

    difficulty: 'medium',

    rating: 5.5,

    cutoff: '29-31',

    air100: '72-76',

    tier: 'Standard GATE (Medium)',

    name: "Mock 106",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Standard official GATE difficulty with balanced distribution of MCQs, MSQs, and NATs across all subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 5.5/10)."

  },
  {

    id: 'mock-med-24',
    provider: "Standard Series",

    type: 'full',

    difficulty: 'medium',

    rating: 5.5,

    cutoff: '29-31',

    air100: '72-76',

    tier: 'Standard GATE (Medium)',

    name: "Mock 107",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Standard official GATE difficulty with balanced distribution of MCQs, MSQs, and NATs across all subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 5.5/10)."

  },
  {

    id: 'mock-med-25',
    provider: "Standard Series",

    type: 'full',

    difficulty: 'medium',

    rating: 5.5,

    cutoff: '29-31',

    air100: '72-76',

    tier: 'Standard GATE (Medium)',

    name: "Mock 108",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Standard official GATE difficulty with balanced distribution of MCQs, MSQs, and NATs across all subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 5.5/10)."

  },
  {

    id: 'mock-med-26',
    provider: "Standard Series",

    type: 'full',

    difficulty: 'medium',

    rating: 5.5,

    cutoff: '29-31',

    air100: '72-76',

    tier: 'Standard GATE (Medium)',

    name: "Mock 109",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Standard official GATE difficulty with balanced distribution of MCQs, MSQs, and NATs across all subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 5.5/10)."

  },
  {

    id: 'mock-med-27',
    provider: "Standard Series",

    type: 'full',

    difficulty: 'medium',

    rating: 5.6,

    cutoff: '29-31',

    air100: '72-76',

    tier: 'Standard GATE (Medium)',

    name: "Mock 110",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Standard official GATE difficulty with balanced distribution of MCQs, MSQs, and NATs across all subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 5.6/10)."

  },
  {

    id: 'mock-med-28',
    provider: "Standard Series",

    type: 'full',

    difficulty: 'medium',

    rating: 5.6,

    cutoff: '29-31',

    air100: '72-76',

    tier: 'Standard GATE (Medium)',

    name: "Mock 111",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Standard official GATE difficulty with balanced distribution of MCQs, MSQs, and NATs across all subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 5.6/10)."

  },
  {

    id: 'mock-med-29',
    provider: "Standard Series",

    type: 'full',

    difficulty: 'medium',

    rating: 5.6,

    cutoff: '29-31',

    air100: '72-76',

    tier: 'Standard GATE (Medium)',

    name: "Mock 112",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Standard official GATE difficulty with balanced distribution of MCQs, MSQs, and NATs across all subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 5.6/10)."

  },
  {

    id: 'mock-med-30',
    provider: "Standard Series",

    type: 'full',

    difficulty: 'medium',

    rating: 5.7,

    cutoff: '28-30',

    air100: '71-75',

    tier: 'Standard GATE (Medium)',

    name: "Mock 113",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Standard official GATE difficulty with balanced distribution of MCQs, MSQs, and NATs across all subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Medium (Rating: 5.7/10)."

  },
  {

    id: 'mock-easy-01',
    provider: "Easy Series",

    type: 'full',

    difficulty: 'easy',

    rating: 3.5,

    cutoff: '34-36',

    air100: '78-82',

    tier: 'Foundational Easy',

    name: "Mock 114",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Direct formula application, fundamental definitions, and standard scoring problems across all 13 subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Easy (Rating: 3.5/10)."

  },
  {

    id: 'mock-easy-02',
    provider: "Easy Series",

    type: 'full',

    difficulty: 'easy',

    rating: 3.5,

    cutoff: '34-36',

    air100: '78-82',

    tier: 'Foundational Easy',

    name: "Mock 115",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Direct formula application, fundamental definitions, and standard scoring problems across all 13 subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Easy (Rating: 3.5/10)."

  },
  {

    id: 'mock-easy-03',
    provider: "Easy Series",

    type: 'full',

    difficulty: 'easy',

    rating: 3.5,

    cutoff: '34-36',

    air100: '78-82',

    tier: 'Foundational Easy',

    name: "Mock 116",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Direct formula application, fundamental definitions, and standard scoring problems across all 13 subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Easy (Rating: 3.5/10)."

  },
  {

    id: 'mock-easy-04',
    provider: "Easy Series",

    type: 'full',

    difficulty: 'easy',

    rating: 3.5,

    cutoff: '34-36',

    air100: '78-82',

    tier: 'Foundational Easy',

    name: "Mock 117",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Direct formula application, fundamental definitions, and standard scoring problems across all 13 subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Easy (Rating: 3.5/10)."

  },
  {

    id: 'mock-easy-05',
    provider: "Easy Series",

    type: 'full',

    difficulty: 'easy',

    rating: 3.5,

    cutoff: '34-36',

    air100: '78-82',

    tier: 'Foundational Easy',

    name: "Mock 118",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Direct formula application, fundamental definitions, and standard scoring problems across all 13 subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Easy (Rating: 3.5/10)."

  },
  {

    id: 'mock-easy-06',
    provider: "Easy Series",

    type: 'full',

    difficulty: 'easy',

    rating: 3.5,

    cutoff: '34-36',

    air100: '78-82',

    tier: 'Foundational Easy',

    name: "Mock 119",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Direct formula application, fundamental definitions, and standard scoring problems across all 13 subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Easy (Rating: 3.5/10)."

  },
  {

    id: 'mock-easy-07',
    provider: "Easy Series",

    type: 'full',

    difficulty: 'easy',

    rating: 3.5,

    cutoff: '34-36',

    air100: '78-82',

    tier: 'Foundational Easy',

    name: "Mock 120",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Direct formula application, fundamental definitions, and standard scoring problems across all 13 subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Easy (Rating: 3.5/10)."

  },
  {

    id: 'mock-easy-08',
    provider: "Easy Series",

    type: 'full',

    difficulty: 'easy',

    rating: 3.5,

    cutoff: '34-36',

    air100: '78-82',

    tier: 'Foundational Easy',

    name: "Mock 121",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Direct formula application, fundamental definitions, and standard scoring problems across all 13 subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Easy (Rating: 3.5/10)."

  },
  {

    id: 'mock-easy-09',
    provider: "Easy Series",

    type: 'full',

    difficulty: 'easy',

    rating: 3.5,

    cutoff: '34-36',

    air100: '78-82',

    tier: 'Foundational Easy',

    name: "Mock 122",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Direct formula application, fundamental definitions, and standard scoring problems across all 13 subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Easy (Rating: 3.5/10)."

  },
  {

    id: 'mock-easy-10',
    provider: "Easy Series",

    type: 'full',

    difficulty: 'easy',

    rating: 3.5,

    cutoff: '34-36',

    air100: '78-82',

    tier: 'Foundational Easy',

    name: "Mock 123",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Direct formula application, fundamental definitions, and standard scoring problems across all 13 subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Easy (Rating: 3.5/10)."

  },
  {

    id: 'mock-easy-11',
    provider: "Easy Series",

    type: 'full',

    difficulty: 'easy',

    rating: 3.5,

    cutoff: '34-36',

    air100: '78-82',

    tier: 'Foundational Easy',

    name: "Mock 124",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Direct formula application, fundamental definitions, and standard scoring problems across all 13 subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Easy (Rating: 3.5/10)."

  },
  {

    id: 'mock-easy-12',
    provider: "Easy Series",

    type: 'full',

    difficulty: 'easy',

    rating: 3.5,

    cutoff: '34-36',

    air100: '78-82',

    tier: 'Foundational Easy',

    name: "Mock 125",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Direct formula application, fundamental definitions, and standard scoring problems across all 13 subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Easy (Rating: 3.5/10)."

  },
  {

    id: 'mock-easy-13',
    provider: "Easy Series",

    type: 'full',

    difficulty: 'easy',

    rating: 3.5,

    cutoff: '34-36',

    air100: '78-82',

    tier: 'Foundational Easy',

    name: "Mock 126",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Direct formula application, fundamental definitions, and standard scoring problems across all 13 subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Easy (Rating: 3.5/10)."

  },
  {

    id: 'mock-easy-14',
    provider: "Easy Series",

    type: 'full',

    difficulty: 'easy',

    rating: 3.5,

    cutoff: '34-36',

    air100: '78-82',

    tier: 'Foundational Easy',

    name: "Mock 127",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Direct formula application, fundamental definitions, and standard scoring problems across all 13 subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Easy (Rating: 3.5/10)."

  },
  {

    id: 'mock-easy-15',
    provider: "Easy Series",

    type: 'full',

    difficulty: 'easy',

    rating: 3.5,

    cutoff: '34-36',

    air100: '78-82',

    tier: 'Foundational Easy',

    name: "Mock 128",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Direct formula application, fundamental definitions, and standard scoring problems across all 13 subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Easy (Rating: 3.5/10)."

  },
  {

    id: 'mock-easy-16',
    provider: "Easy Series",

    type: 'full',

    difficulty: 'easy',

    rating: 3.5,

    cutoff: '34-36',

    air100: '78-82',

    tier: 'Foundational Easy',

    name: "Mock 129",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Direct formula application, fundamental definitions, and standard scoring problems across all 13 subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Easy (Rating: 3.5/10)."

  },
  {

    id: 'mock-easy-17',
    provider: "Easy Series",

    type: 'full',

    difficulty: 'easy',

    rating: 3.5,

    cutoff: '34-36',

    air100: '78-82',

    tier: 'Foundational Easy',

    name: "Mock 130",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Direct formula application, fundamental definitions, and standard scoring problems across all 13 subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Easy (Rating: 3.5/10)."

  },
  {

    id: 'mock-easy-18',
    provider: "Easy Series",

    type: 'full',

    difficulty: 'easy',

    rating: 3.5,

    cutoff: '34-36',

    air100: '78-82',

    tier: 'Foundational Easy',

    name: "Mock 131",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Direct formula application, fundamental definitions, and standard scoring problems across all 13 subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Easy (Rating: 3.5/10)."

  },
  {

    id: 'mock-easy-19',
    provider: "Easy Series",

    type: 'full',

    difficulty: 'easy',

    rating: 3.5,

    cutoff: '34-36',

    air100: '78-82',

    tier: 'Foundational Easy',

    name: "Mock 132",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Direct formula application, fundamental definitions, and standard scoring problems across all 13 subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Easy (Rating: 3.5/10)."

  },
  {

    id: 'mock-easy-20',
    provider: "Easy Series",

    type: 'full',

    difficulty: 'easy',

    rating: 3.5,

    cutoff: '34-36',

    air100: '78-82',

    tier: 'Foundational Easy',

    name: "Mock 133",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Direct formula application, fundamental definitions, and standard scoring problems across all 13 subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Easy (Rating: 3.5/10)."

  },
  {

    id: 'mock-easy-21',
    provider: "Easy Series",

    type: 'full',

    difficulty: 'easy',

    rating: 3.5,

    cutoff: '34-36',

    air100: '78-82',

    tier: 'Foundational Easy',

    name: "Mock 134",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Direct formula application, fundamental definitions, and standard scoring problems across all 13 subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Easy (Rating: 3.5/10)."

  },
  {

    id: 'mock-easy-22',
    provider: "Easy Series",

    type: 'full',

    difficulty: 'easy',

    rating: 3.5,

    cutoff: '34-36',

    air100: '78-82',

    tier: 'Foundational Easy',

    name: "Mock 135",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Direct formula application, fundamental definitions, and standard scoring problems across all 13 subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Easy (Rating: 3.5/10)."

  },
  {

    id: 'mock-easy-23',
    provider: "Easy Series",

    type: 'full',

    difficulty: 'easy',

    rating: 3.5,

    cutoff: '34-36',

    air100: '78-82',

    tier: 'Foundational Easy',

    name: "Mock 136",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Direct formula application, fundamental definitions, and standard scoring problems across all 13 subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Easy (Rating: 3.5/10)."

  },
  {

    id: 'mock-easy-24',
    provider: "Easy Series",

    type: 'full',

    difficulty: 'easy',

    rating: 3.5,

    cutoff: '34-36',

    air100: '78-82',

    tier: 'Foundational Easy',

    name: "Mock 137",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Direct formula application, fundamental definitions, and standard scoring problems across all 13 subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Easy (Rating: 3.5/10)."

  },
  {

    id: 'mock-easy-25',
    provider: "Easy Series",

    type: 'full',

    difficulty: 'easy',

    rating: 3.5,

    cutoff: '34-36',

    air100: '78-82',

    tier: 'Foundational Easy',

    name: "Mock 138",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Direct formula application, fundamental definitions, and standard scoring problems across all 13 subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Easy (Rating: 3.5/10)."

  },
  {

    id: 'mock-easy-26',
    provider: "Easy Series",

    type: 'full',

    difficulty: 'easy',

    rating: 3.5,

    cutoff: '34-36',

    air100: '78-82',

    tier: 'Foundational Easy',

    name: "Mock 139",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Direct formula application, fundamental definitions, and standard scoring problems across all 13 subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Easy (Rating: 3.5/10)."

  },
  {

    id: 'mock-easy-27',
    provider: "Easy Series",

    type: 'full',

    difficulty: 'easy',

    rating: 3.5,

    cutoff: '34-36',

    air100: '78-82',

    tier: 'Foundational Easy',

    name: "Mock 140",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Direct formula application, fundamental definitions, and standard scoring problems across all 13 subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Easy (Rating: 3.5/10)."

  },
  {

    id: 'mock-easy-28',
    provider: "Easy Series",

    type: 'full',

    difficulty: 'easy',

    rating: 3.5,

    cutoff: '34-36',

    air100: '78-82',

    tier: 'Foundational Easy',

    name: "Mock 141",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Direct formula application, fundamental definitions, and standard scoring problems across all 13 subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Easy (Rating: 3.5/10)."

  },
  {

    id: 'mock-easy-29',
    provider: "Easy Series",

    type: 'full',

    difficulty: 'easy',

    rating: 3.5,

    cutoff: '34-36',

    air100: '78-82',

    tier: 'Foundational Easy',

    name: "Mock 142",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Direct formula application, fundamental definitions, and standard scoring problems across all 13 subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Easy (Rating: 3.5/10)."

  },
  {

    id: 'mock-easy-30',
    provider: "Easy Series",

    type: 'full',

    difficulty: 'easy',

    rating: 3.5,

    cutoff: '34-36',

    air100: '78-82',

    tier: 'Foundational Easy',

    name: "Mock 143",

    subject: null,

    questions: 65,

    duration: 180,

    marks: 100,

    desc: "Direct formula application, fundamental definitions, and standard scoring problems across all 13 subjects (65 Questions \u2022 180 Mins \u2022 100 Marks). Type: Full Syllabus Mock | Difficulty: Easy (Rating: 3.5/10)."

  },
    // ─── 30 EXTREME-HARD FULL-LENGTH MOCK EXAMINATIONS (hard_mocks.docx) ───
  {
    id: 'mock-hard-01',
    provider: "Extreme Hard Series",
    type: 'full',
    difficulty: 'hard',
    rating: 9.6,
    cutoff: '22-26',
    air100: '58-64',
    tier: 'Extreme Hard Mock (GO-Classes Caliber)',
    name: "Mock 144",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Extreme Hard Series (GO-Classes Caliber)] Extreme Hard Full Mock Exam #01. Difficulty: Hard (Rating: 9.6/10). Capstone extreme-difficulty examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-hard-02',
    provider: "Extreme Hard Series",
    type: 'full',
    difficulty: 'hard',
    rating: 9.7,
    cutoff: '22-26',
    air100: '58-64',
    tier: 'Extreme Hard Mock (GO-Classes Caliber)',
    name: "Mock 145",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Extreme Hard Series (GO-Classes Caliber)] Extreme Hard Full Mock Exam #02. Difficulty: Hard (Rating: 9.7/10). Capstone extreme-difficulty examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-hard-03',
    provider: "Extreme Hard Series",
    type: 'full',
    difficulty: 'hard',
    rating: 9.8,
    cutoff: '22-26',
    air100: '58-64',
    tier: 'Extreme Hard Mock (GO-Classes Caliber)',
    name: "Mock 146",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Extreme Hard Series (GO-Classes Caliber)] Extreme Hard Full Mock Exam #03. Difficulty: Hard (Rating: 9.8/10). Capstone extreme-difficulty examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-hard-04',
    provider: "Extreme Hard Series",
    type: 'full',
    difficulty: 'hard',
    rating: 9.9,
    cutoff: '22-26',
    air100: '58-64',
    tier: 'Extreme Hard Mock (GO-Classes Caliber)',
    name: "Mock 147",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Extreme Hard Series (GO-Classes Caliber)] Extreme Hard Full Mock Exam #04. Difficulty: Hard (Rating: 9.9/10). Capstone extreme-difficulty examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-hard-05',
    provider: "Extreme Hard Series",
    type: 'full',
    difficulty: 'hard',
    rating: 9.5,
    cutoff: '22-26',
    air100: '58-64',
    tier: 'Extreme Hard Mock (GO-Classes Caliber)',
    name: "Mock 148",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Extreme Hard Series (GO-Classes Caliber)] Extreme Hard Full Mock Exam #05. Difficulty: Hard (Rating: 9.5/10). Capstone extreme-difficulty examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-hard-06',
    provider: "Extreme Hard Series",
    type: 'full',
    difficulty: 'hard',
    rating: 9.6,
    cutoff: '22-26',
    air100: '58-64',
    tier: 'Extreme Hard Mock (GO-Classes Caliber)',
    name: "Mock 149",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Extreme Hard Series (GO-Classes Caliber)] Extreme Hard Full Mock Exam #06. Difficulty: Hard (Rating: 9.6/10). Capstone extreme-difficulty examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-hard-07',
    provider: "Extreme Hard Series",
    type: 'full',
    difficulty: 'hard',
    rating: 9.7,
    cutoff: '22-26',
    air100: '58-64',
    tier: 'Extreme Hard Mock (GO-Classes Caliber)',
    name: "Mock 150",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Extreme Hard Series (GO-Classes Caliber)] Extreme Hard Full Mock Exam #07. Difficulty: Hard (Rating: 9.7/10). Capstone extreme-difficulty examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-hard-08',
    provider: "Extreme Hard Series",
    type: 'full',
    difficulty: 'hard',
    rating: 9.8,
    cutoff: '22-26',
    air100: '58-64',
    tier: 'Extreme Hard Mock (GO-Classes Caliber)',
    name: "Mock 151",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Extreme Hard Series (GO-Classes Caliber)] Extreme Hard Full Mock Exam #08. Difficulty: Hard (Rating: 9.8/10). Capstone extreme-difficulty examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-hard-09',
    provider: "Extreme Hard Series",
    type: 'full',
    difficulty: 'hard',
    rating: 9.9,
    cutoff: '22-26',
    air100: '58-64',
    tier: 'Extreme Hard Mock (GO-Classes Caliber)',
    name: "Mock 152",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Extreme Hard Series (GO-Classes Caliber)] Extreme Hard Full Mock Exam #09. Difficulty: Hard (Rating: 9.9/10). Capstone extreme-difficulty examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-hard-10',
    provider: "Extreme Hard Series",
    type: 'full',
    difficulty: 'hard',
    rating: 9.5,
    cutoff: '22-26',
    air100: '58-64',
    tier: 'Extreme Hard Mock (GO-Classes Caliber)',
    name: "Mock 153",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Extreme Hard Series (GO-Classes Caliber)] Extreme Hard Full Mock Exam #10. Difficulty: Hard (Rating: 9.5/10). Capstone extreme-difficulty examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-hard-11',
    provider: "Extreme Hard Series",
    type: 'full',
    difficulty: 'hard',
    rating: 9.6,
    cutoff: '22-26',
    air100: '58-64',
    tier: 'Extreme Hard Mock (GO-Classes Caliber)',
    name: "Mock 154",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Extreme Hard Series (GO-Classes Caliber)] Extreme Hard Full Mock Exam #11. Difficulty: Hard (Rating: 9.6/10). Capstone extreme-difficulty examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-hard-12',
    provider: "Extreme Hard Series",
    type: 'full',
    difficulty: 'hard',
    rating: 9.7,
    cutoff: '22-26',
    air100: '58-64',
    tier: 'Extreme Hard Mock (GO-Classes Caliber)',
    name: "Mock 155",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Extreme Hard Series (GO-Classes Caliber)] Extreme Hard Full Mock Exam #12. Difficulty: Hard (Rating: 9.7/10). Capstone extreme-difficulty examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-hard-13',
    provider: "Extreme Hard Series",
    type: 'full',
    difficulty: 'hard',
    rating: 9.8,
    cutoff: '22-26',
    air100: '58-64',
    tier: 'Extreme Hard Mock (GO-Classes Caliber)',
    name: "Mock 156",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Extreme Hard Series (GO-Classes Caliber)] Extreme Hard Full Mock Exam #13. Difficulty: Hard (Rating: 9.8/10). Capstone extreme-difficulty examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-hard-14',
    provider: "Extreme Hard Series",
    type: 'full',
    difficulty: 'hard',
    rating: 9.9,
    cutoff: '22-26',
    air100: '58-64',
    tier: 'Extreme Hard Mock (GO-Classes Caliber)',
    name: "Mock 157",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Extreme Hard Series (GO-Classes Caliber)] Extreme Hard Full Mock Exam #14. Difficulty: Hard (Rating: 9.9/10). Capstone extreme-difficulty examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-hard-15',
    provider: "Extreme Hard Series",
    type: 'full',
    difficulty: 'hard',
    rating: 9.5,
    cutoff: '22-26',
    air100: '58-64',
    tier: 'Extreme Hard Mock (GO-Classes Caliber)',
    name: "Mock 158",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Extreme Hard Series (GO-Classes Caliber)] Extreme Hard Full Mock Exam #15. Difficulty: Hard (Rating: 9.5/10). Capstone extreme-difficulty examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-hard-16',
    provider: "Extreme Hard Series",
    type: 'full',
    difficulty: 'hard',
    rating: 9.6,
    cutoff: '22-26',
    air100: '58-64',
    tier: 'Extreme Hard Mock (GO-Classes Caliber)',
    name: "Mock 159",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Extreme Hard Series (GO-Classes Caliber)] Extreme Hard Full Mock Exam #16. Difficulty: Hard (Rating: 9.6/10). Capstone extreme-difficulty examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-hard-17',
    provider: "Extreme Hard Series",
    type: 'full',
    difficulty: 'hard',
    rating: 9.7,
    cutoff: '22-26',
    air100: '58-64',
    tier: 'Extreme Hard Mock (GO-Classes Caliber)',
    name: "Mock 160",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Extreme Hard Series (GO-Classes Caliber)] Extreme Hard Full Mock Exam #17. Difficulty: Hard (Rating: 9.7/10). Capstone extreme-difficulty examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-hard-18',
    provider: "Extreme Hard Series",
    type: 'full',
    difficulty: 'hard',
    rating: 9.8,
    cutoff: '22-26',
    air100: '58-64',
    tier: 'Extreme Hard Mock (GO-Classes Caliber)',
    name: "Mock 161",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Extreme Hard Series (GO-Classes Caliber)] Extreme Hard Full Mock Exam #18. Difficulty: Hard (Rating: 9.8/10). Capstone extreme-difficulty examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-hard-19',
    provider: "Extreme Hard Series",
    type: 'full',
    difficulty: 'hard',
    rating: 9.9,
    cutoff: '22-26',
    air100: '58-64',
    tier: 'Extreme Hard Mock (GO-Classes Caliber)',
    name: "Mock 162",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Extreme Hard Series (GO-Classes Caliber)] Extreme Hard Full Mock Exam #19. Difficulty: Hard (Rating: 9.9/10). Capstone extreme-difficulty examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-hard-20',
    provider: "Extreme Hard Series",
    type: 'full',
    difficulty: 'hard',
    rating: 9.5,
    cutoff: '22-26',
    air100: '58-64',
    tier: 'Extreme Hard Mock (GO-Classes Caliber)',
    name: "Mock 163",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Extreme Hard Series (GO-Classes Caliber)] Extreme Hard Full Mock Exam #20. Difficulty: Hard (Rating: 9.5/10). Capstone extreme-difficulty examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-hard-21',
    provider: "Extreme Hard Series",
    type: 'full',
    difficulty: 'hard',
    rating: 9.6,
    cutoff: '22-26',
    air100: '58-64',
    tier: 'Extreme Hard Mock (GO-Classes Caliber)',
    name: "Mock 164",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Extreme Hard Series (GO-Classes Caliber)] Extreme Hard Full Mock Exam #21. Difficulty: Hard (Rating: 9.6/10). Capstone extreme-difficulty examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-hard-22',
    provider: "Extreme Hard Series",
    type: 'full',
    difficulty: 'hard',
    rating: 9.7,
    cutoff: '22-26',
    air100: '58-64',
    tier: 'Extreme Hard Mock (GO-Classes Caliber)',
    name: "Mock 165",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Extreme Hard Series (GO-Classes Caliber)] Extreme Hard Full Mock Exam #22. Difficulty: Hard (Rating: 9.7/10). Capstone extreme-difficulty examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-hard-23',
    provider: "Extreme Hard Series",
    type: 'full',
    difficulty: 'hard',
    rating: 9.8,
    cutoff: '22-26',
    air100: '58-64',
    tier: 'Extreme Hard Mock (GO-Classes Caliber)',
    name: "Mock 166",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Extreme Hard Series (GO-Classes Caliber)] Extreme Hard Full Mock Exam #23. Difficulty: Hard (Rating: 9.8/10). Capstone extreme-difficulty examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-hard-24',
    provider: "Extreme Hard Series",
    type: 'full',
    difficulty: 'hard',
    rating: 9.9,
    cutoff: '22-26',
    air100: '58-64',
    tier: 'Extreme Hard Mock (GO-Classes Caliber)',
    name: "Mock 167",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Extreme Hard Series (GO-Classes Caliber)] Extreme Hard Full Mock Exam #24. Difficulty: Hard (Rating: 9.9/10). Capstone extreme-difficulty examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-hard-25',
    provider: "Extreme Hard Series",
    type: 'full',
    difficulty: 'hard',
    rating: 9.5,
    cutoff: '22-26',
    air100: '58-64',
    tier: 'Extreme Hard Mock (GO-Classes Caliber)',
    name: "Mock 168",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Extreme Hard Series (GO-Classes Caliber)] Extreme Hard Full Mock Exam #25. Difficulty: Hard (Rating: 9.5/10). Capstone extreme-difficulty examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-hard-26',
    provider: "Extreme Hard Series",
    type: 'full',
    difficulty: 'hard',
    rating: 9.6,
    cutoff: '22-26',
    air100: '58-64',
    tier: 'Extreme Hard Mock (GO-Classes Caliber)',
    name: "Mock 169",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Extreme Hard Series (GO-Classes Caliber)] Extreme Hard Full Mock Exam #26. Difficulty: Hard (Rating: 9.6/10). Capstone extreme-difficulty examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-hard-27',
    provider: "Extreme Hard Series",
    type: 'full',
    difficulty: 'hard',
    rating: 9.7,
    cutoff: '22-26',
    air100: '58-64',
    tier: 'Extreme Hard Mock (GO-Classes Caliber)',
    name: "Mock 170",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Extreme Hard Series (GO-Classes Caliber)] Extreme Hard Full Mock Exam #27. Difficulty: Hard (Rating: 9.7/10). Capstone extreme-difficulty examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-hard-28',
    provider: "Extreme Hard Series",
    type: 'full',
    difficulty: 'hard',
    rating: 9.8,
    cutoff: '22-26',
    air100: '58-64',
    tier: 'Extreme Hard Mock (GO-Classes Caliber)',
    name: "Mock 171",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Extreme Hard Series (GO-Classes Caliber)] Extreme Hard Full Mock Exam #28. Difficulty: Hard (Rating: 9.8/10). Capstone extreme-difficulty examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-hard-29',
    provider: "Extreme Hard Series",
    type: 'full',
    difficulty: 'hard',
    rating: 9.9,
    cutoff: '22-26',
    air100: '58-64',
    tier: 'Extreme Hard Mock (GO-Classes Caliber)',
    name: "Mock 172",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Extreme Hard Series (GO-Classes Caliber)] Extreme Hard Full Mock Exam #29. Difficulty: Hard (Rating: 9.9/10). Capstone extreme-difficulty examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-hard-30',
    provider: "Extreme Hard Series",
    type: 'full',
    difficulty: 'hard',
    rating: 9.5,
    cutoff: '22-26',
    air100: '58-64',
    tier: 'Extreme Hard Mock (GO-Classes Caliber)',
    name: "Mock 173",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Extreme Hard Series (GO-Classes Caliber)] Extreme Hard Full Mock Exam #30. Difficulty: Hard (Rating: 9.5/10). Capstone extreme-difficulty examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
    // ─── 30 EASY-LEVEL FULL-LENGTH MOCK EXAMINATIONS (SET 2) (easy1_mocks.docx) ───
  {
    id: 'mock-easy1-01',
    provider: "Easy Series (Set 2)",
    type: 'full',
    difficulty: 'easy',
    rating: 3.6,
    cutoff: '34-36',
    air100: '78-82',
    tier: 'Foundational Easy Mock (Set 2)',
    name: "Mock 174",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Easy Series (Set 2)] Easy Full Mock Exam #01. Difficulty: Easy (Rating: 3.6/10). Fundamental scoring examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-easy1-02',
    provider: "Easy Series (Set 2)",
    type: 'full',
    difficulty: 'easy',
    rating: 3.7,
    cutoff: '34-36',
    air100: '78-82',
    tier: 'Foundational Easy Mock (Set 2)',
    name: "Mock 175",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Easy Series (Set 2)] Easy Full Mock Exam #02. Difficulty: Easy (Rating: 3.7/10). Fundamental scoring examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-easy1-03',
    provider: "Easy Series (Set 2)",
    type: 'full',
    difficulty: 'easy',
    rating: 3.8,
    cutoff: '34-36',
    air100: '78-82',
    tier: 'Foundational Easy Mock (Set 2)',
    name: "Mock 176",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Easy Series (Set 2)] Easy Full Mock Exam #03. Difficulty: Easy (Rating: 3.8/10). Fundamental scoring examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-easy1-04',
    provider: "Easy Series (Set 2)",
    type: 'full',
    difficulty: 'easy',
    rating: 3.9,
    cutoff: '34-36',
    air100: '78-82',
    tier: 'Foundational Easy Mock (Set 2)',
    name: "Mock 177",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Easy Series (Set 2)] Easy Full Mock Exam #04. Difficulty: Easy (Rating: 3.9/10). Fundamental scoring examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-easy1-05',
    provider: "Easy Series (Set 2)",
    type: 'full',
    difficulty: 'easy',
    rating: 3.5,
    cutoff: '34-36',
    air100: '78-82',
    tier: 'Foundational Easy Mock (Set 2)',
    name: "Mock 178",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Easy Series (Set 2)] Easy Full Mock Exam #05. Difficulty: Easy (Rating: 3.5/10). Fundamental scoring examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-easy1-06',
    provider: "Easy Series (Set 2)",
    type: 'full',
    difficulty: 'easy',
    rating: 3.6,
    cutoff: '34-36',
    air100: '78-82',
    tier: 'Foundational Easy Mock (Set 2)',
    name: "Mock 179",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Easy Series (Set 2)] Easy Full Mock Exam #06. Difficulty: Easy (Rating: 3.6/10). Fundamental scoring examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-easy1-07',
    provider: "Easy Series (Set 2)",
    type: 'full',
    difficulty: 'easy',
    rating: 3.7,
    cutoff: '34-36',
    air100: '78-82',
    tier: 'Foundational Easy Mock (Set 2)',
    name: "Mock 180",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Easy Series (Set 2)] Easy Full Mock Exam #07. Difficulty: Easy (Rating: 3.7/10). Fundamental scoring examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-easy1-08',
    provider: "Easy Series (Set 2)",
    type: 'full',
    difficulty: 'easy',
    rating: 3.8,
    cutoff: '34-36',
    air100: '78-82',
    tier: 'Foundational Easy Mock (Set 2)',
    name: "Mock 181",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Easy Series (Set 2)] Easy Full Mock Exam #08. Difficulty: Easy (Rating: 3.8/10). Fundamental scoring examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-easy1-09',
    provider: "Easy Series (Set 2)",
    type: 'full',
    difficulty: 'easy',
    rating: 3.9,
    cutoff: '34-36',
    air100: '78-82',
    tier: 'Foundational Easy Mock (Set 2)',
    name: "Mock 182",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Easy Series (Set 2)] Easy Full Mock Exam #09. Difficulty: Easy (Rating: 3.9/10). Fundamental scoring examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-easy1-10',
    provider: "Easy Series (Set 2)",
    type: 'full',
    difficulty: 'easy',
    rating: 3.5,
    cutoff: '34-36',
    air100: '78-82',
    tier: 'Foundational Easy Mock (Set 2)',
    name: "Mock 183",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Easy Series (Set 2)] Easy Full Mock Exam #10. Difficulty: Easy (Rating: 3.5/10). Fundamental scoring examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-easy1-11',
    provider: "Easy Series (Set 2)",
    type: 'full',
    difficulty: 'easy',
    rating: 3.6,
    cutoff: '34-36',
    air100: '78-82',
    tier: 'Foundational Easy Mock (Set 2)',
    name: "Mock 184",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Easy Series (Set 2)] Easy Full Mock Exam #11. Difficulty: Easy (Rating: 3.6/10). Fundamental scoring examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-easy1-12',
    provider: "Easy Series (Set 2)",
    type: 'full',
    difficulty: 'easy',
    rating: 3.7,
    cutoff: '34-36',
    air100: '78-82',
    tier: 'Foundational Easy Mock (Set 2)',
    name: "Mock 185",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Easy Series (Set 2)] Easy Full Mock Exam #12. Difficulty: Easy (Rating: 3.7/10). Fundamental scoring examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-easy1-13',
    provider: "Easy Series (Set 2)",
    type: 'full',
    difficulty: 'easy',
    rating: 3.8,
    cutoff: '34-36',
    air100: '78-82',
    tier: 'Foundational Easy Mock (Set 2)',
    name: "Mock 186",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Easy Series (Set 2)] Easy Full Mock Exam #13. Difficulty: Easy (Rating: 3.8/10). Fundamental scoring examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-easy1-14',
    provider: "Easy Series (Set 2)",
    type: 'full',
    difficulty: 'easy',
    rating: 3.9,
    cutoff: '34-36',
    air100: '78-82',
    tier: 'Foundational Easy Mock (Set 2)',
    name: "Mock 187",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Easy Series (Set 2)] Easy Full Mock Exam #14. Difficulty: Easy (Rating: 3.9/10). Fundamental scoring examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-easy1-15',
    provider: "Easy Series (Set 2)",
    type: 'full',
    difficulty: 'easy',
    rating: 3.5,
    cutoff: '34-36',
    air100: '78-82',
    tier: 'Foundational Easy Mock (Set 2)',
    name: "Mock 188",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Easy Series (Set 2)] Easy Full Mock Exam #15. Difficulty: Easy (Rating: 3.5/10). Fundamental scoring examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-easy1-16',
    provider: "Easy Series (Set 2)",
    type: 'full',
    difficulty: 'easy',
    rating: 3.6,
    cutoff: '34-36',
    air100: '78-82',
    tier: 'Foundational Easy Mock (Set 2)',
    name: "Mock 189",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Easy Series (Set 2)] Easy Full Mock Exam #16. Difficulty: Easy (Rating: 3.6/10). Fundamental scoring examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-easy1-17',
    provider: "Easy Series (Set 2)",
    type: 'full',
    difficulty: 'easy',
    rating: 3.7,
    cutoff: '34-36',
    air100: '78-82',
    tier: 'Foundational Easy Mock (Set 2)',
    name: "Mock 190",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Easy Series (Set 2)] Easy Full Mock Exam #17. Difficulty: Easy (Rating: 3.7/10). Fundamental scoring examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-easy1-18',
    provider: "Easy Series (Set 2)",
    type: 'full',
    difficulty: 'easy',
    rating: 3.8,
    cutoff: '34-36',
    air100: '78-82',
    tier: 'Foundational Easy Mock (Set 2)',
    name: "Mock 191",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Easy Series (Set 2)] Easy Full Mock Exam #18. Difficulty: Easy (Rating: 3.8/10). Fundamental scoring examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-easy1-19',
    provider: "Easy Series (Set 2)",
    type: 'full',
    difficulty: 'easy',
    rating: 3.9,
    cutoff: '34-36',
    air100: '78-82',
    tier: 'Foundational Easy Mock (Set 2)',
    name: "Mock 192",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Easy Series (Set 2)] Easy Full Mock Exam #19. Difficulty: Easy (Rating: 3.9/10). Fundamental scoring examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-easy1-20',
    provider: "Easy Series (Set 2)",
    type: 'full',
    difficulty: 'easy',
    rating: 3.5,
    cutoff: '34-36',
    air100: '78-82',
    tier: 'Foundational Easy Mock (Set 2)',
    name: "Mock 193",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Easy Series (Set 2)] Easy Full Mock Exam #20. Difficulty: Easy (Rating: 3.5/10). Fundamental scoring examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-easy1-21',
    provider: "Easy Series (Set 2)",
    type: 'full',
    difficulty: 'easy',
    rating: 3.6,
    cutoff: '34-36',
    air100: '78-82',
    tier: 'Foundational Easy Mock (Set 2)',
    name: "Mock 194",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Easy Series (Set 2)] Easy Full Mock Exam #21. Difficulty: Easy (Rating: 3.6/10). Fundamental scoring examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-easy1-22',
    provider: "Easy Series (Set 2)",
    type: 'full',
    difficulty: 'easy',
    rating: 3.7,
    cutoff: '34-36',
    air100: '78-82',
    tier: 'Foundational Easy Mock (Set 2)',
    name: "Mock 195",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Easy Series (Set 2)] Easy Full Mock Exam #22. Difficulty: Easy (Rating: 3.7/10). Fundamental scoring examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-easy1-23',
    provider: "Easy Series (Set 2)",
    type: 'full',
    difficulty: 'easy',
    rating: 3.8,
    cutoff: '34-36',
    air100: '78-82',
    tier: 'Foundational Easy Mock (Set 2)',
    name: "Mock 196",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Easy Series (Set 2)] Easy Full Mock Exam #23. Difficulty: Easy (Rating: 3.8/10). Fundamental scoring examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-easy1-24',
    provider: "Easy Series (Set 2)",
    type: 'full',
    difficulty: 'easy',
    rating: 3.9,
    cutoff: '34-36',
    air100: '78-82',
    tier: 'Foundational Easy Mock (Set 2)',
    name: "Mock 197",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Easy Series (Set 2)] Easy Full Mock Exam #24. Difficulty: Easy (Rating: 3.9/10). Fundamental scoring examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-easy1-25',
    provider: "Easy Series (Set 2)",
    type: 'full',
    difficulty: 'easy',
    rating: 3.5,
    cutoff: '34-36',
    air100: '78-82',
    tier: 'Foundational Easy Mock (Set 2)',
    name: "Mock 198",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Easy Series (Set 2)] Easy Full Mock Exam #25. Difficulty: Easy (Rating: 3.5/10). Fundamental scoring examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-easy1-26',
    provider: "Easy Series (Set 2)",
    type: 'full',
    difficulty: 'easy',
    rating: 3.6,
    cutoff: '34-36',
    air100: '78-82',
    tier: 'Foundational Easy Mock (Set 2)',
    name: "Mock 199",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Easy Series (Set 2)] Easy Full Mock Exam #26. Difficulty: Easy (Rating: 3.6/10). Fundamental scoring examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-easy1-27',
    provider: "Easy Series (Set 2)",
    type: 'full',
    difficulty: 'easy',
    rating: 3.7,
    cutoff: '34-36',
    air100: '78-82',
    tier: 'Foundational Easy Mock (Set 2)',
    name: "Mock 200",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Easy Series (Set 2)] Easy Full Mock Exam #27. Difficulty: Easy (Rating: 3.7/10). Fundamental scoring examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-easy1-28',
    provider: "Easy Series (Set 2)",
    type: 'full',
    difficulty: 'easy',
    rating: 3.8,
    cutoff: '34-36',
    air100: '78-82',
    tier: 'Foundational Easy Mock (Set 2)',
    name: "Mock 201",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Easy Series (Set 2)] Easy Full Mock Exam #28. Difficulty: Easy (Rating: 3.8/10). Fundamental scoring examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-easy1-29',
    provider: "Easy Series (Set 2)",
    type: 'full',
    difficulty: 'easy',
    rating: 3.9,
    cutoff: '34-36',
    air100: '78-82',
    tier: 'Foundational Easy Mock (Set 2)',
    name: "Mock 202",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Easy Series (Set 2)] Easy Full Mock Exam #29. Difficulty: Easy (Rating: 3.9/10). Fundamental scoring examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  {
    id: 'mock-easy1-30',
    provider: "Easy Series (Set 2)",
    type: 'full',
    difficulty: 'easy',
    rating: 3.5,
    cutoff: '34-36',
    air100: '78-82',
    tier: 'Foundational Easy Mock (Set 2)',
    name: "Mock 203",
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: "[Provider: Easy Series (Set 2)] Easy Full Mock Exam #30. Difficulty: Easy (Rating: 3.5/10). Fundamental scoring examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions • 180 Mins • 100 Marks)."
  },
  { id:'paper-full-1',
    provider: "Practice Paper", mockId:'paper-full-1', name: "Mock 204", type:'practice-set', difficulty:'easy', rating:3.5, cutoff:'34-36', air100:'78-82', questions:65, duration:180, marks:100, desc: "[Provider: Curated Practice Paper] Curated Practice Set #144. Topic-focused practice questions with detailed step-by-step solutions. Difficulty: Easy (Rating: 3.5/10)." },
  { id:'paper-full-2',
    provider: "Practice Paper", mockId:'paper-full-2', name: "Mock 205", type:'practice-set', difficulty:'medium', rating:4.5, cutoff:'31-33', air100:'74-78', questions:65, duration:180, marks:100, desc: "[Provider: Curated Practice Paper] Curated Practice Set #145. Topic-focused practice questions with detailed step-by-step solutions. Difficulty: Medium (Rating: 4.5/10)." },
  { id:'paper-dsa',
    provider: "Practice Paper", mockId:'paper-dsa', name: "Mock 206", type:'practice-set', difficulty:'medium', rating:5.0, subjects:['Data Structures','Algorithms','C Programming'], questions:50, duration:120, marks:80, desc: "[Provider: Curated Practice Paper] Curated Practice Set #146. Topic-focused practice questions with detailed step-by-step solutions. Difficulty: Medium (Rating: 5.0/10)." },
  { id:'paper-systems',
    provider: "Practice Paper", mockId:'paper-systems', name: "Mock 207", type:'practice-set', difficulty:'hard', rating:6.0, subjects:['Operating Systems','Computer Networks','Computer Organization'], questions:50, duration:120, marks:80, desc: "[Provider: Curated Practice Paper] Curated Practice Set #147. Topic-focused practice questions with detailed step-by-step solutions. Difficulty: Hard (Rating: 6.0/10)." },
  { id:'paper-theory',
    provider: "Practice Paper", mockId:'paper-theory', name: "Mock 208", type:'practice-set', difficulty:'medium', rating:5.0, subjects:['Theory of Computation','Compiler Design'], questions:35, duration:90, marks:60, desc: "[Provider: Curated Practice Paper] Curated Practice Set #148. Topic-focused practice questions with detailed step-by-step solutions. Difficulty: Medium (Rating: 5.0/10)." },
  { id:'paper-maths',
    provider: "Practice Paper", mockId:'paper-maths', name: "Mock 209", type:'practice-set', difficulty:'medium', rating:4.5, subjects:['Discrete Mathematics','Engineering Mathematics','Aptitude'], questions:45, duration:110, marks:70, desc: "[Provider: Curated Practice Paper] Curated Practice Set #149. Topic-focused practice questions with detailed step-by-step solutions. Difficulty: Medium (Rating: 4.5/10)." },
  { id:'paper-decade-pyq',
    provider: "Practice Paper", mockId:'paper-decade-pyq', name: "Mock 210", type:'practice-set', difficulty:'medium', rating:5.5, cutoff:'28-30', air100:'72-76', questions:65, duration:180, marks:100, desc: "[Provider: Curated Practice Paper] Curated Practice Set #150. Topic-focused practice questions with detailed step-by-step solutions. Difficulty: Medium (Rating: 5.5/10)." },
  // ─── Set 1: Foundational / Standard Subject Tests (13 Subjects) ───
  { id:'mock-subwise-ds',   type:'subwise', difficulty:'medium', level:'Foundational', name:'Data Structures Full Mock (Set 1)',           subject:'Data Structures',         questions:30, duration:60, marks:45, rating:6.5, desc:'Arrays, linked lists, binary trees, BSTs, heaps, and hash tables.' },
  { id:'mock-subwise-algo', type:'subwise', difficulty:'hard',   level:'Foundational', name:'Algorithms Deep Dive (Set 1)',                subject:'Algorithms',              questions:30, duration:60, marks:45, rating:7.2, desc:'Sorting, divide & conquer, greedy, dynamic programming, and graph algorithms.' },
  { id:'mock-subwise-os',   type:'subwise', difficulty:'medium', level:'Foundational', name:'Operating Systems Mock (Set 1)',              subject:'Operating Systems',       questions:30, duration:60, marks:45, rating:6.8, desc:'Processes, CPU scheduling, virtual memory, synchronization, and deadlocks.' },
  { id:'mock-subwise-cn',   type:'subwise', difficulty:'medium', level:'Foundational', name:'Computer Networks Mock (Set 1)',              subject:'Computer Networks',       questions:30, duration:60, marks:45, rating:6.6, desc:'OSI, IP addressing, subnetting, TCP congestion control, and routing protocols.' },
  { id:'mock-subwise-dbms', type:'subwise', difficulty:'medium', level:'Foundational', name:'DBMS Comprehensive Mock (Set 1)',             subject:'DBMS',                    questions:25, duration:50, marks:40, rating:6.4, desc:'SQL queries, normal forms (1NF-BCNF), relational algebra, and ACID transactions.' },
  { id:'mock-subwise-toc',  type:'subwise', difficulty:'hard',   level:'Foundational', name:'Theory of Computation Mock (Set 1)',          subject:'Theory of Computation',   questions:25, duration:50, marks:40, rating:7.5, desc:'DFAs, NFAs, regular expressions, context-free languages, and grammars.' },
  { id:'mock-subwise-coa',  type:'subwise', difficulty:'hard',   level:'Foundational', name:'Computer Organization & Arch Mock (Set 1)',   subject:'Computer Organization',   questions:25, duration:50, marks:40, rating:7.4, desc:'Instruction pipelining, cache memory hierarchy, addressing modes, and IEEE 754.' },
  { id:'mock-subwise-cd',   type:'subwise', difficulty:'medium', level:'Foundational', name:'Compiler Design Mock (Set 1)',                subject:'Compiler Design',         questions:25, duration:50, marks:35, rating:6.5, desc:'Lexical analysis, FIRST & FOLLOW, LL(1) / LR parsing, and code generation.' },
  { id:'mock-subwise-dl',   type:'subwise', difficulty:'easy',   level:'Foundational', name:'Digital Logic Mock (Set 1)',                  subject:'Digital Logic',           questions:25, duration:50, marks:35, rating:5.8, desc:'Boolean algebra, K-maps, multiplexers, decoders, and flip-flop counters.' },
  { id:'mock-subwise-dm',   type:'subwise', difficulty:'medium', level:'Foundational', name:'Discrete Mathematics Mock (Set 1)',           subject:'Discrete Mathematics',    questions:25, duration:50, marks:40, rating:6.9, desc:'Graph theory, relations, posets, combinatorics, and modular arithmetic.' },
  { id:'mock-subwise-em',   type:'subwise', difficulty:'medium', level:'Foundational', name:'Engineering Mathematics Mock (Set 1)',        subject:'Engineering Mathematics', questions:25, duration:50, marks:40, rating:6.7, desc:'Linear algebra, eigenvalues, calculus, probability, and distributions.' },
  { id:'mock-subwise-c',    type:'subwise', difficulty:'easy',   level:'Foundational', name:'C Programming Fundamentals Mock (Set 1)',     subject:'C Programming',           questions:25, duration:50, marks:35, rating:6.0, desc:'Pointers, arrays, recursion, bitwise operations, and memory models.' },
  { id:'mock-subwise-apt',  type:'subwise', difficulty:'easy',   level:'Foundational', name:'General Aptitude Mock (Set 1)',               subject:'Aptitude',                questions:25, duration:50, marks:35, rating:5.5, desc:'Numerical ability, time & work, speed & distance, and verbal reasoning.' },

  // ─── Set 2: Advanced Booster Subject Tests (13 Subjects) ───
  { id:'mock-subwise-ds-adv',   type:'subwise', difficulty:'hard', level:'Advanced Booster', name:'Data Structures Advanced Mastery (Set 2)',       subject:'Data Structures',         questions:30, duration:60, marks:45, rating:8.0, desc:'AVL trees, Red-Black properties, min/max heap heapify, collision probing, and disjoint sets.' },
  { id:'mock-subwise-algo-adv', type:'subwise', difficulty:'hard', level:'Advanced Booster', name:'Algorithms & Complexity Booster (Set 2)',        subject:'Algorithms',              questions:30, duration:60, marks:45, rating:8.5, desc:'Asymptotic recurrences, dynamic programming proofs, Bellman-Ford, Kruskal/Prim, and NP-completeness.' },
  { id:'mock-subwise-os-adv',   type:'subwise', difficulty:'hard', level:'Advanced Booster', name:'Operating Systems Advanced Booster (Set 2)',      subject:'Operating Systems',       questions:30, duration:60, marks:45, rating:8.2, desc:'Multi-level page tables, inverted paging, disk scheduling, semaphore invariants, and deadlock avoidance.' },
  { id:'mock-subwise-cn-adv',   type:'subwise', difficulty:'hard', level:'Advanced Booster', name:'Computer Networks Advanced Drill (Set 2)',        subject:'Computer Networks',       questions:30, duration:60, marks:45, rating:8.1, desc:'CIDR subnets, TCP sliding window, slow start/AIMD, Go-Back-N/SR, DNS, HTTP, and CRC checksums.' },
  { id:'mock-subwise-dbms-adv', type:'subwise', difficulty:'hard', level:'Advanced Booster', name:'DBMS Advanced Concurrency & B+ Trees (Set 2)',  subject:'DBMS',                    questions:25, duration:50, marks:40, rating:8.0, desc:'2PL conflict serializability, recoverable schedules, B and B+ tree indexing, and canonical closures.' },
  { id:'mock-subwise-toc-adv',  type:'subwise', difficulty:'hard', level:'Advanced Booster', name:'TOC Decidability & Grammar Mastery (Set 2)',      subject:'Theory of Computation',   questions:25, duration:50, marks:40, rating:8.6, desc:'Minimization of DFAs, Myhill-Nerode theorem, PDA state transitions, Turing halting, and Rice\'s theorem.' },
  { id:'mock-subwise-coa-adv',  type:'subwise', difficulty:'hard', level:'Advanced Booster', name:'COA Pipelining Hazards & Cache Mastery (Set 2)',  subject:'Computer Organization',   questions:25, duration:50, marks:40, rating:8.4, desc:'Structural/data/control pipeline stalls, branch penalties, 2-level hierarchical memory, and Booth\'s multiplier.' },
  { id:'mock-subwise-cd-adv',   type:'subwise', difficulty:'hard', level:'Advanced Booster', name:'Compiler Design LR Parsing & SDT (Set 2)',        subject:'Compiler Design',         questions:25, duration:50, marks:35, rating:7.8, desc:'CLR(1)/LALR(1) parsing tables, conflict resolution, syntax-directed definitions, and basic blocks.' },
  { id:'mock-subwise-dl-adv',   type:'subwise', difficulty:'medium', level:'Advanced Booster', name:'Digital Logic Sequential Machines (Set 2)',     subject:'Digital Logic',           questions:25, duration:50, marks:35, rating:7.2, desc:'Synchronous counters, state reduction tables, setup and hold time margins, and race conditions.' },
  { id:'mock-subwise-dm-adv',   type:'subwise', difficulty:'hard', level:'Advanced Booster', name:'Discrete Mathematics Combinatorics & Logic (Set 2)', subject:'Discrete Mathematics',    questions:25, duration:50, marks:40, rating:8.3, desc:'Planar graphs, chromatic numbers, pigeonhole principle, generating functions, and first-order predicate logic.' },
  { id:'mock-subwise-em-adv',   type:'subwise', difficulty:'medium', level:'Advanced Booster', name:'Engineering Mathematics Matrices & Probability (Set 2)', subject:'Engineering Mathematics', questions:25, duration:50, marks:40, rating:7.4, desc:'Matrix diagonalization, Cayley-Hamilton theorem, conditional expectation, Bayes\' theorem, and calculus.' },
  { id:'mock-subwise-c-adv',    type:'subwise', difficulty:'medium', level:'Advanced Booster', name:'C Programming Pointers & Memory Drill (Set 2)', subject:'C Programming',           questions:25, duration:50, marks:35, rating:7.0, desc:'2D pointer arithmetic, function pointers, operator precedence, macros, and dynamic allocation.' },
  { id:'mock-subwise-apt-adv',  type:'subwise', difficulty:'medium', level:'Advanced Booster', name:'Quantitative & Verbal Reasoning Sprint (Set 2)', subject:'Aptitude',                questions:25, duration:50, marks:35, rating:6.8, desc:'Complex syllogisms, reading comprehension inference, data interpretation charts, and spatial paper folding.' },

  // ─── Set 3: Discrete Mathematics Subject Test Series (50 Tests • 5,000 Questions) ───
  { id: 'mock-sub-dm-01', type: 'subwise', difficulty: 'easy', level: 'Subject Test Series', name: 'Discrete Mathematics Test Series — Test 01', subject: 'Discrete Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Discrete Mathematics Subject Test Series — Test 01. Full syllabus coverage with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-dm-02', type: 'subwise', difficulty: 'easy', level: 'Subject Test Series', name: 'Discrete Mathematics Test Series — Test 02', subject: 'Discrete Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Discrete Mathematics Subject Test Series — Test 02. Full syllabus coverage with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-dm-03', type: 'subwise', difficulty: 'easy', level: 'Subject Test Series', name: 'Discrete Mathematics Test Series — Test 03', subject: 'Discrete Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Discrete Mathematics Subject Test Series — Test 03. Full syllabus coverage with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-dm-04', type: 'subwise', difficulty: 'easy', level: 'Subject Test Series', name: 'Discrete Mathematics Test Series — Test 04', subject: 'Discrete Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Discrete Mathematics Subject Test Series — Test 04. Full syllabus coverage with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-dm-05', type: 'subwise', difficulty: 'easy', level: 'Subject Test Series', name: 'Discrete Mathematics Test Series — Test 05', subject: 'Discrete Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Discrete Mathematics Subject Test Series — Test 05. Full syllabus coverage with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-dm-06', type: 'subwise', difficulty: 'easy', level: 'Subject Test Series', name: 'Discrete Mathematics Test Series — Test 06', subject: 'Discrete Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Discrete Mathematics Subject Test Series — Test 06. Full syllabus coverage with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-dm-07', type: 'subwise', difficulty: 'easy', level: 'Subject Test Series', name: 'Discrete Mathematics Test Series — Test 07', subject: 'Discrete Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Discrete Mathematics Subject Test Series — Test 07. Full syllabus coverage with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-dm-08', type: 'subwise', difficulty: 'easy', level: 'Subject Test Series', name: 'Discrete Mathematics Test Series — Test 08', subject: 'Discrete Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Discrete Mathematics Subject Test Series — Test 08. Full syllabus coverage with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-dm-09', type: 'subwise', difficulty: 'easy', level: 'Subject Test Series', name: 'Discrete Mathematics Test Series — Test 09', subject: 'Discrete Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Discrete Mathematics Subject Test Series — Test 09. Full syllabus coverage with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-dm-10', type: 'subwise', difficulty: 'easy', level: 'Subject Test Series', name: 'Discrete Mathematics Test Series — Test 10', subject: 'Discrete Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Discrete Mathematics Subject Test Series — Test 10. Full syllabus coverage with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-dm-11', type: 'subwise', difficulty: 'medium', level: 'Subject Test Series', name: 'Discrete Mathematics Test Series — Test 11', subject: 'Discrete Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Discrete Mathematics Subject Test Series — Test 11. Full syllabus coverage with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-dm-12', type: 'subwise', difficulty: 'medium', level: 'Subject Test Series', name: 'Discrete Mathematics Test Series — Test 12', subject: 'Discrete Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Discrete Mathematics Subject Test Series — Test 12. Full syllabus coverage with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-dm-13', type: 'subwise', difficulty: 'medium', level: 'Subject Test Series', name: 'Discrete Mathematics Test Series — Test 13', subject: 'Discrete Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Discrete Mathematics Subject Test Series — Test 13. Full syllabus coverage with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-dm-14', type: 'subwise', difficulty: 'medium', level: 'Subject Test Series', name: 'Discrete Mathematics Test Series — Test 14', subject: 'Discrete Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Discrete Mathematics Subject Test Series — Test 14. Full syllabus coverage with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-dm-15', type: 'subwise', difficulty: 'medium', level: 'Subject Test Series', name: 'Discrete Mathematics Test Series — Test 15', subject: 'Discrete Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Discrete Mathematics Subject Test Series — Test 15. Full syllabus coverage with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-dm-16', type: 'subwise', difficulty: 'medium', level: 'Subject Test Series', name: 'Discrete Mathematics Test Series — Test 16', subject: 'Discrete Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Discrete Mathematics Subject Test Series — Test 16. Full syllabus coverage with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-dm-17', type: 'subwise', difficulty: 'medium', level: 'Subject Test Series', name: 'Discrete Mathematics Test Series — Test 17', subject: 'Discrete Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Discrete Mathematics Subject Test Series — Test 17. Full syllabus coverage with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-dm-18', type: 'subwise', difficulty: 'medium', level: 'Subject Test Series', name: 'Discrete Mathematics Test Series — Test 18', subject: 'Discrete Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Discrete Mathematics Subject Test Series — Test 18. Full syllabus coverage with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-dm-19', type: 'subwise', difficulty: 'medium', level: 'Subject Test Series', name: 'Discrete Mathematics Test Series — Test 19', subject: 'Discrete Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Discrete Mathematics Subject Test Series — Test 19. Full syllabus coverage with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-dm-20', type: 'subwise', difficulty: 'medium', level: 'Subject Test Series', name: 'Discrete Mathematics Test Series — Test 20', subject: 'Discrete Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Discrete Mathematics Subject Test Series — Test 20. Full syllabus coverage with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-dm-21', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Discrete Mathematics Test Series — Test 21', subject: 'Discrete Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Discrete Mathematics Subject Test Series — Test 21. Full syllabus coverage with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-dm-22', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Discrete Mathematics Test Series — Test 22', subject: 'Discrete Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Discrete Mathematics Subject Test Series — Test 22. Full syllabus coverage with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-dm-23', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Discrete Mathematics Test Series — Test 23', subject: 'Discrete Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Discrete Mathematics Subject Test Series — Test 23. Full syllabus coverage with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-dm-24', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Discrete Mathematics Test Series — Test 24', subject: 'Discrete Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Discrete Mathematics Subject Test Series — Test 24. Full syllabus coverage with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-dm-25', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Discrete Mathematics Test Series — Test 25', subject: 'Discrete Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Discrete Mathematics Subject Test Series — Test 25. Full syllabus coverage with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-dm-26', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Discrete Mathematics Test Series — Test 26', subject: 'Discrete Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Discrete Mathematics Subject Test Series — Test 26. Full syllabus coverage with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-dm-27', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Discrete Mathematics Test Series — Test 27', subject: 'Discrete Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Discrete Mathematics Subject Test Series — Test 27. Full syllabus coverage with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-dm-28', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Discrete Mathematics Test Series — Test 28', subject: 'Discrete Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Discrete Mathematics Subject Test Series — Test 28. Full syllabus coverage with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-dm-29', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Discrete Mathematics Test Series — Test 29', subject: 'Discrete Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Discrete Mathematics Subject Test Series — Test 29. Full syllabus coverage with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-dm-30', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Discrete Mathematics Test Series — Test 30', subject: 'Discrete Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Discrete Mathematics Subject Test Series — Test 30. Full syllabus coverage with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-dm-31', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Discrete Mathematics Test Series — Test 31', subject: 'Discrete Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Discrete Mathematics Subject Test Series — Test 31. Full syllabus coverage with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-dm-32', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Discrete Mathematics Test Series — Test 32', subject: 'Discrete Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Discrete Mathematics Subject Test Series — Test 32. Full syllabus coverage with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-dm-33', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Discrete Mathematics Test Series — Test 33', subject: 'Discrete Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Discrete Mathematics Subject Test Series — Test 33. Full syllabus coverage with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-dm-34', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Discrete Mathematics Test Series — Test 34', subject: 'Discrete Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Discrete Mathematics Subject Test Series — Test 34. Full syllabus coverage with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-dm-35', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Discrete Mathematics Test Series — Test 35', subject: 'Discrete Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Discrete Mathematics Subject Test Series — Test 35. Full syllabus coverage with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-dm-36', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Discrete Mathematics Test Series — Test 36', subject: 'Discrete Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Discrete Mathematics Subject Test Series — Test 36. Full syllabus coverage with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-dm-37', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Discrete Mathematics Test Series — Test 37', subject: 'Discrete Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Discrete Mathematics Subject Test Series — Test 37. Full syllabus coverage with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-dm-38', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Discrete Mathematics Test Series — Test 38', subject: 'Discrete Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Discrete Mathematics Subject Test Series — Test 38. Full syllabus coverage with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-dm-39', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Discrete Mathematics Test Series — Test 39', subject: 'Discrete Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Discrete Mathematics Subject Test Series — Test 39. Full syllabus coverage with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-dm-40', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Discrete Mathematics Test Series — Test 40', subject: 'Discrete Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Discrete Mathematics Subject Test Series — Test 40. Full syllabus coverage with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-dm-41', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Discrete Mathematics Test Series — Test 41', subject: 'Discrete Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Discrete Mathematics Subject Test Series — Test 41. Full syllabus coverage with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-dm-42', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Discrete Mathematics Test Series — Test 42', subject: 'Discrete Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Discrete Mathematics Subject Test Series — Test 42. Full syllabus coverage with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-dm-43', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Discrete Mathematics Test Series — Test 43', subject: 'Discrete Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Discrete Mathematics Subject Test Series — Test 43. Full syllabus coverage with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-dm-44', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Discrete Mathematics Test Series — Test 44', subject: 'Discrete Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Discrete Mathematics Subject Test Series — Test 44. Full syllabus coverage with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-dm-45', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Discrete Mathematics Test Series — Test 45', subject: 'Discrete Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Discrete Mathematics Subject Test Series — Test 45. Full syllabus coverage with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-dm-46', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Discrete Mathematics Test Series — Test 46', subject: 'Discrete Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Discrete Mathematics Subject Test Series — Test 46. Full syllabus coverage with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-dm-47', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Discrete Mathematics Test Series — Test 47', subject: 'Discrete Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Discrete Mathematics Subject Test Series — Test 47. Full syllabus coverage with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-dm-48', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Discrete Mathematics Test Series — Test 48', subject: 'Discrete Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Discrete Mathematics Subject Test Series — Test 48. Full syllabus coverage with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-dm-49', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Discrete Mathematics Test Series — Test 49', subject: 'Discrete Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Discrete Mathematics Subject Test Series — Test 49. Full syllabus coverage with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-dm-50', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Discrete Mathematics Test Series — Test 50', subject: 'Discrete Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Discrete Mathematics Subject Test Series — Test 50. Full syllabus coverage with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },

  // ─── Set 4: Engineering Mathematics Subject Test Series (50 Tests • 5,000 Questions) ───
  { id: 'mock-sub-em-01', type: 'subwise', difficulty: 'easy', level: 'Subject Test Series', name: 'Engineering Mathematics Test Series — Test 01', subject: 'Engineering Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Engineering Mathematics Subject Test Series — Test 01. Full syllabus coverage (Linear Algebra, Calculus, Probability & Statistics) with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-em-02', type: 'subwise', difficulty: 'easy', level: 'Subject Test Series', name: 'Engineering Mathematics Test Series — Test 02', subject: 'Engineering Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Engineering Mathematics Subject Test Series — Test 02. Full syllabus coverage (Linear Algebra, Calculus, Probability & Statistics) with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-em-03', type: 'subwise', difficulty: 'easy', level: 'Subject Test Series', name: 'Engineering Mathematics Test Series — Test 03', subject: 'Engineering Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Engineering Mathematics Subject Test Series — Test 03. Full syllabus coverage (Linear Algebra, Calculus, Probability & Statistics) with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-em-04', type: 'subwise', difficulty: 'easy', level: 'Subject Test Series', name: 'Engineering Mathematics Test Series — Test 04', subject: 'Engineering Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Engineering Mathematics Subject Test Series — Test 04. Full syllabus coverage (Linear Algebra, Calculus, Probability & Statistics) with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-em-05', type: 'subwise', difficulty: 'easy', level: 'Subject Test Series', name: 'Engineering Mathematics Test Series — Test 05', subject: 'Engineering Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Engineering Mathematics Subject Test Series — Test 05. Full syllabus coverage (Linear Algebra, Calculus, Probability & Statistics) with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-em-06', type: 'subwise', difficulty: 'easy', level: 'Subject Test Series', name: 'Engineering Mathematics Test Series — Test 06', subject: 'Engineering Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Engineering Mathematics Subject Test Series — Test 06. Full syllabus coverage (Linear Algebra, Calculus, Probability & Statistics) with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-em-07', type: 'subwise', difficulty: 'easy', level: 'Subject Test Series', name: 'Engineering Mathematics Test Series — Test 07', subject: 'Engineering Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Engineering Mathematics Subject Test Series — Test 07. Full syllabus coverage (Linear Algebra, Calculus, Probability & Statistics) with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-em-08', type: 'subwise', difficulty: 'easy', level: 'Subject Test Series', name: 'Engineering Mathematics Test Series — Test 08', subject: 'Engineering Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Engineering Mathematics Subject Test Series — Test 08. Full syllabus coverage (Linear Algebra, Calculus, Probability & Statistics) with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-em-09', type: 'subwise', difficulty: 'easy', level: 'Subject Test Series', name: 'Engineering Mathematics Test Series — Test 09', subject: 'Engineering Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Engineering Mathematics Subject Test Series — Test 09. Full syllabus coverage (Linear Algebra, Calculus, Probability & Statistics) with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-em-10', type: 'subwise', difficulty: 'easy', level: 'Subject Test Series', name: 'Engineering Mathematics Test Series — Test 10', subject: 'Engineering Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Engineering Mathematics Subject Test Series — Test 10. Full syllabus coverage (Linear Algebra, Calculus, Probability & Statistics) with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-em-11', type: 'subwise', difficulty: 'medium', level: 'Subject Test Series', name: 'Engineering Mathematics Test Series — Test 11', subject: 'Engineering Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Engineering Mathematics Subject Test Series — Test 11. Full syllabus coverage (Linear Algebra, Calculus, Probability & Statistics) with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-em-12', type: 'subwise', difficulty: 'medium', level: 'Subject Test Series', name: 'Engineering Mathematics Test Series — Test 12', subject: 'Engineering Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Engineering Mathematics Subject Test Series — Test 12. Full syllabus coverage (Linear Algebra, Calculus, Probability & Statistics) with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-em-13', type: 'subwise', difficulty: 'medium', level: 'Subject Test Series', name: 'Engineering Mathematics Test Series — Test 13', subject: 'Engineering Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Engineering Mathematics Subject Test Series — Test 13. Full syllabus coverage (Linear Algebra, Calculus, Probability & Statistics) with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-em-14', type: 'subwise', difficulty: 'medium', level: 'Subject Test Series', name: 'Engineering Mathematics Test Series — Test 14', subject: 'Engineering Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Engineering Mathematics Subject Test Series — Test 14. Full syllabus coverage (Linear Algebra, Calculus, Probability & Statistics) with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-em-15', type: 'subwise', difficulty: 'medium', level: 'Subject Test Series', name: 'Engineering Mathematics Test Series — Test 15', subject: 'Engineering Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Engineering Mathematics Subject Test Series — Test 15. Full syllabus coverage (Linear Algebra, Calculus, Probability & Statistics) with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-em-16', type: 'subwise', difficulty: 'medium', level: 'Subject Test Series', name: 'Engineering Mathematics Test Series — Test 16', subject: 'Engineering Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Engineering Mathematics Subject Test Series — Test 16. Full syllabus coverage (Linear Algebra, Calculus, Probability & Statistics) with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-em-17', type: 'subwise', difficulty: 'medium', level: 'Subject Test Series', name: 'Engineering Mathematics Test Series — Test 17', subject: 'Engineering Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Engineering Mathematics Subject Test Series — Test 17. Full syllabus coverage (Linear Algebra, Calculus, Probability & Statistics) with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-em-18', type: 'subwise', difficulty: 'medium', level: 'Subject Test Series', name: 'Engineering Mathematics Test Series — Test 18', subject: 'Engineering Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Engineering Mathematics Subject Test Series — Test 18. Full syllabus coverage (Linear Algebra, Calculus, Probability & Statistics) with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-em-19', type: 'subwise', difficulty: 'medium', level: 'Subject Test Series', name: 'Engineering Mathematics Test Series — Test 19', subject: 'Engineering Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Engineering Mathematics Subject Test Series — Test 19. Full syllabus coverage (Linear Algebra, Calculus, Probability & Statistics) with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-em-20', type: 'subwise', difficulty: 'medium', level: 'Subject Test Series', name: 'Engineering Mathematics Test Series — Test 20', subject: 'Engineering Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Engineering Mathematics Subject Test Series — Test 20. Full syllabus coverage (Linear Algebra, Calculus, Probability & Statistics) with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-em-21', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Engineering Mathematics Test Series — Test 21', subject: 'Engineering Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Engineering Mathematics Subject Test Series — Test 21. Full syllabus coverage (Linear Algebra, Calculus, Probability & Statistics) with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-em-22', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Engineering Mathematics Test Series — Test 22', subject: 'Engineering Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Engineering Mathematics Subject Test Series — Test 22. Full syllabus coverage (Linear Algebra, Calculus, Probability & Statistics) with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-em-23', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Engineering Mathematics Test Series — Test 23', subject: 'Engineering Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Engineering Mathematics Subject Test Series — Test 23. Full syllabus coverage (Linear Algebra, Calculus, Probability & Statistics) with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-em-24', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Engineering Mathematics Test Series — Test 24', subject: 'Engineering Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Engineering Mathematics Subject Test Series — Test 24. Full syllabus coverage (Linear Algebra, Calculus, Probability & Statistics) with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-em-25', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Engineering Mathematics Test Series — Test 25', subject: 'Engineering Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Engineering Mathematics Subject Test Series — Test 25. Full syllabus coverage (Linear Algebra, Calculus, Probability & Statistics) with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-em-26', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Engineering Mathematics Test Series — Test 26', subject: 'Engineering Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Engineering Mathematics Subject Test Series — Test 26. Full syllabus coverage (Linear Algebra, Calculus, Probability & Statistics) with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-em-27', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Engineering Mathematics Test Series — Test 27', subject: 'Engineering Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Engineering Mathematics Subject Test Series — Test 27. Full syllabus coverage (Linear Algebra, Calculus, Probability & Statistics) with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-em-28', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Engineering Mathematics Test Series — Test 28', subject: 'Engineering Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Engineering Mathematics Subject Test Series — Test 28. Full syllabus coverage (Linear Algebra, Calculus, Probability & Statistics) with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-em-29', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Engineering Mathematics Test Series — Test 29', subject: 'Engineering Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Engineering Mathematics Subject Test Series — Test 29. Full syllabus coverage (Linear Algebra, Calculus, Probability & Statistics) with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-em-30', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Engineering Mathematics Test Series — Test 30', subject: 'Engineering Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Engineering Mathematics Subject Test Series — Test 30. Full syllabus coverage (Linear Algebra, Calculus, Probability & Statistics) with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-em-31', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Engineering Mathematics Test Series — Test 31', subject: 'Engineering Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Engineering Mathematics Subject Test Series — Test 31. Full syllabus coverage (Linear Algebra, Calculus, Probability & Statistics) with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-em-32', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Engineering Mathematics Test Series — Test 32', subject: 'Engineering Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Engineering Mathematics Subject Test Series — Test 32. Full syllabus coverage (Linear Algebra, Calculus, Probability & Statistics) with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-em-33', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Engineering Mathematics Test Series — Test 33', subject: 'Engineering Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Engineering Mathematics Subject Test Series — Test 33. Full syllabus coverage (Linear Algebra, Calculus, Probability & Statistics) with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-em-34', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Engineering Mathematics Test Series — Test 34', subject: 'Engineering Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Engineering Mathematics Subject Test Series — Test 34. Full syllabus coverage (Linear Algebra, Calculus, Probability & Statistics) with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-em-35', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Engineering Mathematics Test Series — Test 35', subject: 'Engineering Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Engineering Mathematics Subject Test Series — Test 35. Full syllabus coverage (Linear Algebra, Calculus, Probability & Statistics) with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-em-36', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Engineering Mathematics Test Series — Test 36', subject: 'Engineering Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Engineering Mathematics Subject Test Series — Test 36. Full syllabus coverage (Linear Algebra, Calculus, Probability & Statistics) with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-em-37', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Engineering Mathematics Test Series — Test 37', subject: 'Engineering Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Engineering Mathematics Subject Test Series — Test 37. Full syllabus coverage (Linear Algebra, Calculus, Probability & Statistics) with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-em-38', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Engineering Mathematics Test Series — Test 38', subject: 'Engineering Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Engineering Mathematics Subject Test Series — Test 38. Full syllabus coverage (Linear Algebra, Calculus, Probability & Statistics) with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-em-39', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Engineering Mathematics Test Series — Test 39', subject: 'Engineering Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Engineering Mathematics Subject Test Series — Test 39. Full syllabus coverage (Linear Algebra, Calculus, Probability & Statistics) with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-em-40', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Engineering Mathematics Test Series — Test 40', subject: 'Engineering Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Engineering Mathematics Subject Test Series — Test 40. Full syllabus coverage (Linear Algebra, Calculus, Probability & Statistics) with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-em-41', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Engineering Mathematics Test Series — Test 41', subject: 'Engineering Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Engineering Mathematics Subject Test Series — Test 41. Full syllabus coverage (Linear Algebra, Calculus, Probability & Statistics) with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-em-42', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Engineering Mathematics Test Series — Test 42', subject: 'Engineering Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Engineering Mathematics Subject Test Series — Test 42. Full syllabus coverage (Linear Algebra, Calculus, Probability & Statistics) with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-em-43', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Engineering Mathematics Test Series — Test 43', subject: 'Engineering Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Engineering Mathematics Subject Test Series — Test 43. Full syllabus coverage (Linear Algebra, Calculus, Probability & Statistics) with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-em-44', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Engineering Mathematics Test Series — Test 44', subject: 'Engineering Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Engineering Mathematics Subject Test Series — Test 44. Full syllabus coverage (Linear Algebra, Calculus, Probability & Statistics) with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-em-45', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Engineering Mathematics Test Series — Test 45', subject: 'Engineering Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Engineering Mathematics Subject Test Series — Test 45. Full syllabus coverage (Linear Algebra, Calculus, Probability & Statistics) with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-em-46', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Engineering Mathematics Test Series — Test 46', subject: 'Engineering Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Engineering Mathematics Subject Test Series — Test 46. Full syllabus coverage (Linear Algebra, Calculus, Probability & Statistics) with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-em-47', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Engineering Mathematics Test Series — Test 47', subject: 'Engineering Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Engineering Mathematics Subject Test Series — Test 47. Full syllabus coverage (Linear Algebra, Calculus, Probability & Statistics) with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-em-48', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Engineering Mathematics Test Series — Test 48', subject: 'Engineering Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Engineering Mathematics Subject Test Series — Test 48. Full syllabus coverage (Linear Algebra, Calculus, Probability & Statistics) with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-em-49', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Engineering Mathematics Test Series — Test 49', subject: 'Engineering Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Engineering Mathematics Subject Test Series — Test 49. Full syllabus coverage (Linear Algebra, Calculus, Probability & Statistics) with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
  { id: 'mock-sub-em-50', type: 'subwise', difficulty: 'hard', level: 'Subject Test Series', name: 'Engineering Mathematics Test Series — Test 50', subject: 'Engineering Mathematics', questions: 100, duration: 180, marks: 160, desc: 'Engineering Mathematics Subject Test Series — Test 50. Full syllabus coverage (Linear Algebra, Calculus, Probability & Statistics) with 40 1-mark & 60 2-mark questions (160 Marks • 180 Mins) modeled after official GATE standards.' },
];



const FULL_LENGTH_PYQ_EXAMS = [

  {

    id: 'pyq-exam-2026-1',

    year: 2026,

    set: 'Mock Paper 1',

    name: 'GATE CSE 2026 All-India Exam Paper 1',

    institute: 'Official Pattern GATE 2026',

    duration: 180,

    marks: 100,

    questions: 65,

    difficulty: 'medium',

    rating: 6.5,

    cutoff: '28-30',

    air100: '72-76',

    desc: 'Official-pattern 65-question GATE CSE 2026 full exam paper with balanced distribution of MCQs, MSQs, and multi-step NAT numericals.'

  },

  {

    id: 'pyq-exam-2026-2',

    year: 2026,

    set: 'Mock Paper 2',

    name: 'GATE CSE 2026 All-India Exam Paper 2',

    institute: 'Official Pattern GATE 2026',

    duration: 180,

    marks: 100,

    questions: 65,

    difficulty: 'hard',

    rating: 7.5,

    cutoff: '24-26',

    air100: '66-70',

    desc: 'Advanced full-length GATE CSE 2026 exam paper testing deep core CS, engineering mathematics, and general aptitude under strict 180-min timing.'

  },

  {

    id: 'pyq-exam-2025-s1',

    year: 2025,

    set: 'Set 1',

    name: 'Official GATE CSE 2025 Exam (Set 1)',

    institute: 'IIT Roorkee',

    duration: 180,

    marks: 100,

    questions: 65,

    difficulty: 'medium',

    rating: 5.5,

    cutoff: '28-30',

    air100: '72-76',

    desc: 'The official 65-question GATE 2025 Set 1 question paper conducted by IIT Roorkee under realistic 180-min TCS iON exam simulation.'

  },

  {

    id: 'pyq-exam-2025-s2',

    year: 2025,

    set: 'Set 2',

    name: 'Official GATE CSE 2025 Exam (Set 2)',

    institute: 'IIT Roorkee',

    duration: 180,

    marks: 100,

    questions: 65,

    difficulty: 'hard',

    rating: 7.0,

    cutoff: '24-26',

    air100: '64-68',

    desc: 'The official 65-question GATE 2025 Set 2 question paper conducted by IIT Roorkee with verified IITR answer keys and multi-step derivations.'

  },

  {

    id: 'pyq-exam-2024',

    year: 2024,

    set: 'Full Paper',

    name: 'Official GATE CSE 2024 Exam Paper',

    institute: 'IISc Bangalore',

    duration: 180,

    marks: 100,

    questions: 65,

    difficulty: 'hard',

    rating: 6.8,

    cutoff: '26-28',

    air100: '68-72',

    desc: 'Official GATE CSE 2024 paper conducted by IISc Bangalore covering discrete mathematics, systems, algorithms, and core CS.'

  },

  {

    id: 'pyq-exam-2023',

    year: 2023,

    set: 'Full Paper',

    name: 'Official GATE CSE 2023 Exam Paper',

    institute: 'IIT Kanpur',

    duration: 180,

    marks: 100,

    questions: 65,

    difficulty: 'medium',

    rating: 6.0,

    cutoff: '27-29',

    air100: '70-74',

    desc: 'Official GATE CSE 2023 examination paper conducted by IIT Kanpur with complete MCQs, MSQs, and NAT numericals.'

  },

  {

    id: 'pyq-exam-2022',

    year: 2022,

    set: 'Full Paper',

    name: 'Official GATE CSE 2022 Exam Paper',

    institute: 'IIT Kharagpur',

    duration: 180,

    marks: 100,

    questions: 65,

    difficulty: 'medium',

    rating: 5.8,

    cutoff: '28-30',

    air100: '71-75',

    desc: 'Official GATE CSE 2022 examination paper conducted by IIT Kharagpur.'

  },

  {

    id: 'pyq-exam-2021',

    year: 2021,

    set: 'Full Paper',

    name: 'Official GATE CSE 2021 Exam Paper',

    institute: 'IIT Bombay',

    duration: 180,

    marks: 100,

    questions: 65,

    difficulty: 'medium',

    rating: 5.5,

    cutoff: '28-30',

    air100: '72-76',

    desc: 'Official 65-question GATE CSE 2021 examination paper conducted by IIT Bombay.'

  },

  {

    id: 'pyq-exam-2020',

    year: 2020,

    set: 'Full Paper',

    name: 'Official GATE CSE 2020 Exam Paper',

    institute: 'IIT Delhi',

    duration: 180,

    marks: 100,

    questions: 65,

    difficulty: 'medium',

    rating: 5.5,

    cutoff: '28-30',

    air100: '72-76',

    desc: 'Official 65-question GATE CSE 2020 examination paper conducted by IIT Delhi.'

  },

  {

    id: 'pyq-exam-2019',

    year: 2019,

    set: 'Full Paper',

    name: 'Official GATE CSE 2019 Exam Paper',

    institute: 'IIT Madras',

    duration: 180,

    marks: 100,

    questions: 65,

    difficulty: 'medium',

    rating: 5.0,

    cutoff: '29-31',

    air100: '73-77',

    desc: 'Official 65-question GATE CSE 2019 paper conducted by IIT Madras.'

  },

  {

    id: 'pyq-exam-2018',

    year: 2018,

    set: 'Full Paper',

    name: 'Official GATE CSE 2018 Exam Paper',

    institute: 'IIT Guwahati',

    duration: 180,

    marks: 100,

    questions: 65,

    difficulty: 'medium',

    rating: 5.0,

    cutoff: '29-31',

    air100: '73-77',

    desc: 'Official 65-question GATE CSE 2018 paper conducted by IIT Guwahati.'

  },

  {

    id: 'pyq-exam-2017',

    year: 2017,

    set: 'Full Paper',

    name: 'Official GATE CSE 2017 Exam Paper',

    institute: 'IIT Roorkee',

    duration: 180,

    marks: 100,

    questions: 65,

    difficulty: 'medium',

    rating: 5.4,

    cutoff: '28-30',

    air100: '71-75',

    desc: 'Official GATE CSE 2017 examination paper conducted by IIT Roorkee.'

  },

  {

    id: 'pyq-exam-2016',

    year: 2016,

    set: 'Full Paper',

    name: 'Official GATE CSE 2016 Exam Paper',

    institute: 'IISc Bangalore',

    duration: 180,

    marks: 100,

    questions: 65,

    difficulty: 'medium',

    rating: 5.5,

    cutoff: '28-30',

    air100: '72-76',

    desc: 'Official GATE CSE 2016 examination paper conducted by IISc Bangalore.'

  },

  {

    id: 'pyq-exam-2015-s1',

    year: 2015,

    set: 'Set 1',

    name: 'Official GATE CSE 2015 Exam (Set 1)',

    institute: 'IIT Kanpur',

    duration: 180,

    marks: 100,

    questions: 65,

    difficulty: 'medium',

    rating: 5.2,

    cutoff: '29-31',

    air100: '72-76',

    desc: 'Official GATE CSE 2015 Set 1 examination paper conducted by IIT Kanpur.'

  },

  {

    id: 'pyq-exam-2015-s2',

    year: 2015,

    set: 'Set 2',

    name: 'Official GATE CSE 2015 Exam (Set 2)',

    institute: 'IIT Kanpur',

    duration: 180,

    marks: 100,

    questions: 65,

    difficulty: 'hard',

    rating: 6.2,

    cutoff: '26-28',

    air100: '68-72',

    desc: 'Official GATE CSE 2015 Set 2 examination paper conducted by IIT Kanpur.'

  },

  {

    id: 'pyq-exam-2015-s3',

    year: 2015,

    set: 'Set 3',

    name: 'Official GATE CSE 2015 Exam (Set 3)',

    institute: 'IIT Kanpur',

    duration: 180,

    marks: 100,

    questions: 65,

    difficulty: 'medium',

    rating: 5.8,

    cutoff: '27-29',

    air100: '70-74',

    desc: 'Official GATE CSE 2015 Set 3 examination paper conducted by IIT Kanpur.'

  },

  {

    id: 'pyq-exam-2014-s1',

    year: 2014,

    set: 'Set 1',

    name: 'Official GATE CSE 2014 Exam (Set 1)',

    institute: 'IIT Kharagpur',

    duration: 180,

    marks: 100,

    questions: 65,

    difficulty: 'medium',

    rating: 5.0,

    cutoff: '29-31',

    air100: '73-77',

    desc: 'Official GATE CSE 2014 Set 1 paper conducted by IIT Kharagpur.'

  },

  {

    id: 'pyq-exam-2014-s2',

    year: 2014,

    set: 'Set 2',

    name: 'Official GATE CSE 2014 Exam (Set 2)',

    institute: 'IIT Kharagpur',

    duration: 180,

    marks: 100,

    questions: 65,

    difficulty: 'medium',

    rating: 5.0,

    cutoff: '29-31',

    air100: '73-77',

    desc: 'Official GATE CSE 2014 Set 2 paper conducted by IIT Kharagpur.'

  },

  {

    id: 'pyq-exam-2014-s3',

    year: 2014,

    set: 'Set 3',

    name: 'Official GATE CSE 2014 Exam (Set 3)',

    institute: 'IIT Kharagpur',

    duration: 180,

    marks: 100,

    questions: 65,

    difficulty: 'hard',

    rating: 6.0,

    cutoff: '27-29',

    air100: '69-73',

    desc: 'Official GATE CSE 2014 Set 3 paper conducted by IIT Kharagpur.'

  },

  {

    id: 'pyq-exam-2011',

    year: 2011,

    set: 'Full Paper',

    name: 'Official GATE CSE 2011 Exam Paper',

    institute: 'IIT Madras',

    duration: 180,

    marks: 100,

    questions: 65,

    difficulty: 'easy',

    rating: 4.0,

    cutoff: '32-34',

    air100: '76-80',

    desc: 'Official 65-question GATE CSE 2011 examination paper.'

  },

  {

    id: 'pyq-exam-decade',

    year: '2014–2024',

    set: 'Decade Special',

    name: 'GATE Decade Special PYQ Exam (2014–2024)',

    institute: 'National Community Compilation',

    duration: 180,

    marks: 100,

    questions: 65,

    difficulty: 'medium',

    rating: 5.5,

    cutoff: '28-30',

    air100: '72-76',

    desc: 'Curated 65-question compilation across the last decade of GATE CSE exams.'

  }

];



// Backward-compatibility alias for legacy code

const PRACTICE_PAPERS = MOCK_TESTS.filter(m => m.type === 'practice-set' || m.type === 'full');

const PYQ_YEARS   = [2025,2024,2023,2022,2021,2020,2019,2018,2017,2016,2015,2014,2013,2012,2011,2010,2009,2008,2007];

const LS_KEY      = 'gate_cse_v8';

const USE_FB      = !!db;   // false when config has placeholder values



// ─── USER ─────────────────────────────────────────────────────────────────────

let currentUser = null;  // Firebase Auth user object



const uid       = () => currentUser?.uid || 'local';

const uName     = () => currentUser?.displayName || currentUser?.email?.split('@')[0] || 'Guest';

const uEmail    = () => currentUser?.email || '';

const uInitial  = () => uName().charAt(0).toUpperCase();



// Firestore paths

const qCol      = ()     => collection(db, 'questions');

const qDoc      = (id)   => doc(db, 'questions', id);

const attCol    = ()     => collection(db, 'users', uid(), 'attempts');

const attDoc    = (id)   => doc(db, 'users', uid(), 'attempts', id);

const sesCol    = ()     => collection(db, 'users', uid(), 'testSessions');

const sesDoc    = (id)   => doc(db, 'users', uid(), 'testSessions', id);



// ─── STATE ────────────────────────────────────────────────────────────────────

const state = {

  bookmarkTags:     {},

  activeBookmarkTag:'all',

  soundFxEnabled:   true,

  currentPage:      'dashboard',

  currentParams:    {},

  questions:        [],

  attempts:         [],

  testSessions:     [],

  bookmarks:        new Set(),

  activeTest:       null,

  currentQuestion:  0,

  practiceQueue:    [],

  practiceAnswered: false,

  practiceFilters:  { subject:'all', topic:'all', difficulty:'all', type:'all', category:'all', status:'all' },

  practicePage:     1,

  practicePageSize: 20,

  practiceSearch:   '',

  practiceSort:     'default',

  pyqFilters:       { year:'all', subject:'all' },

  pyqPage:          1,

  pyqPageSize:      20,

  pyqSearch:        '',

  topicPyqTab:      'chapters',

  selectedTopicPyqSubject: 'all',

  topicPyqSearch:   '',

  topicPyqDifficulty: 'all',

  topicPyqType:     'all',

  topicPyqExpandedTopic: null,

  mockTab:          'all',

  mockLevelFilter:  'all',

  questionNotes:    {},

  flashcardStats:   {},

  mockSort:         'default',
  mockViewMode:     (typeof localStorage !== 'undefined' && localStorage.getItem('gate_mock_view_mode')) || 'grid',
  pinnedMocks:      new Set(JSON.parse((typeof localStorage !== 'undefined' && localStorage.getItem('gate_pinned_mocks')) || '[]')),

  mockSearch:       '',

  mockSubSeries:    'all',

  paperLevelFilter: 'all',

  paperSort:        'default',

  pyqExamEraFilter: 'all',

  pyqExamDiffFilter:'all',

  pyqExamSort:      'year-desc',

  activeMockPaper:  null,

  firestoreReady:   false,

  errorTags:        {},

  playlists:        {},

  activePlaylistModalQ: null,

  activeMethodTab:  {},

  themeMode:         'dark',

  srsQueue:          {},   // SM-2 per-question review schedule

  reportedQuestions: {},   // flagged questions

  dailyGoal:         20,   // questions per day target

  lastPracticeState: null, // remembered filter/page state

};



// ─── CACHE, INDEXEDDB & BOOKMARKS ────────────────────────────────────────────

const IDB_NAME = 'GATE_CSE_QUESTION_BANK';

const IDB_STORE = 'questions_store';

const IDB_USER_STORE = 'userdata_store';

const IDB_VERSION = 2;



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

        if (!db.objectStoreNames.contains(IDB_USER_STORE)) {

          db.createObjectStore(IDB_USER_STORE);

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



async function idbSaveUserData(attempts, testSessions, srsQueue) {

  try {

    const db = await openQuestionsIDB();

    if (!db) return false;

    return new Promise(resolve => {

      const tx = db.transaction(IDB_USER_STORE, 'readwrite');

      const store = tx.objectStore(IDB_USER_STORE);

      store.put({ attempts: attempts || [], testSessions: testSessions || [], srsQueue: srsQueue || {}, updatedAt: Date.now() }, 'user_state');

      tx.oncomplete = () => resolve(true);

      tx.onerror = () => resolve(false);

    });

  } catch(e) { return false; }

}



async function idbLoadUserData() {

  try {

    const db = await openQuestionsIDB();

    if (!db) return null;

    return new Promise(resolve => {

      const tx = db.transaction(IDB_USER_STORE, 'readonly');

      const store = tx.objectStore(IDB_USER_STORE);

      const req = store.get('user_state');

      req.onsuccess = () => resolve(req.result || null);

      req.onerror = () => resolve(null);

    });

  } catch(e) { return null; }

}





const STATIC_BUNDLED_IDS = new Set();



function mergeQuestionArrays(baseList, incomingList) {

  if (!incomingList || !incomingList.length) return baseList || [];

  if (!baseList || !baseList.length) return incomingList || [];

  const map = new Map();

  for (const q of baseList) {

    if (q && q.id) map.set(q.id, q);

  }

  for (const q of incomingList) {

    if (q && q.id) {

      // Bundled static questions are authoritative and immutable — remote docs cannot override

      if (STATIC_BUNDLED_IDS.has(q.id)) {

        if (!map.has(q.id)) map.set(q.id, q);

        continue;

      }

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

    try { localStorage.setItem('gate_question_notes', JSON.stringify(state.questionNotes || {})); } catch(e){}

    try { localStorage.setItem('gate_question_error_tags', JSON.stringify(state.errorTags || {})); } catch(e){}

    try { localStorage.setItem('gate_custom_playlists', JSON.stringify(state.playlists || {})); } catch(e){}

    try { localStorage.setItem('gate_theme_mode', state.themeMode || 'dark'); } catch(e){}

    try { localStorage.setItem('gate_srs_queue', JSON.stringify(state.srsQueue || {})); } catch(e){}

    try { localStorage.setItem('gate_reported_qs', JSON.stringify(state.reportedQuestions || {})); } catch(e){}

    try { localStorage.setItem('gate_daily_goal', String(state.dailyGoal || 20)); } catch(e){}

    try { localStorage.setItem('gate_study_targets', JSON.stringify(state.studyPlannerTargets || [])); } catch(e){}

    idbSaveUserData(state.attempts, state.testSessions, state.srsQueue);

    try { localStorage.setItem('gate_last_practice', JSON.stringify(state.lastPracticeState || null)); } catch(e){}

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

    try { state.questionNotes = JSON.parse(localStorage.getItem('gate_question_notes') || '{}'); } catch(e){ state.questionNotes = {}; }

    try { state.flashcardStats = JSON.parse(localStorage.getItem('gate_formula_flashcards_srs') || '{}'); } catch(e){ state.flashcardStats = {}; }

    try { state.errorTags = JSON.parse(localStorage.getItem('gate_question_error_tags') || '{}'); } catch(e){ state.errorTags = {}; }

    try { state.playlists = JSON.parse(localStorage.getItem('gate_custom_playlists') || '{}'); } catch(e){ state.playlists = {}; }

    try { state.themeMode = localStorage.getItem('gate_theme_mode') || 'dark'; } catch(e){ state.themeMode = 'dark'; }

    try { state.srsQueue = JSON.parse(localStorage.getItem('gate_srs_queue') || '{}'); } catch(e){ state.srsQueue = {}; }

    try { state.reportedQuestions = JSON.parse(localStorage.getItem('gate_reported_qs') || '{}'); } catch(e){ state.reportedQuestions = {}; }

    try { state.dailyGoal = parseInt(localStorage.getItem('gate_daily_goal') || '20', 10) || 20; } catch(e){ state.dailyGoal = 20; }

    try { state.studyPlannerTargets = JSON.parse(localStorage.getItem('gate_study_targets') || '[]'); } catch(e){ state.studyPlannerTargets = []; }

    try { state.lastPracticeState = JSON.parse(localStorage.getItem('gate_last_practice') || 'null'); } catch(e){ state.lastPracticeState = null; }

    initDefaultPlaylists();

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

    localStorage.setItem(`gate_bookmark_tags_${uid()}`, JSON.stringify(state.bookmarkTags || {}));

  } catch(e) {}

}



function loadBookmarks() {

  try {

    const raw = localStorage.getItem(`gate_bookmarks_${uid()}`);

    state.bookmarks = new Set(raw ? JSON.parse(raw) : []);

    const rawTags = localStorage.getItem(`gate_bookmark_tags_${uid()}`);

    state.bookmarkTags = rawTags ? JSON.parse(rawTags) : {};

  } catch(e) {

    state.bookmarks = new Set();

    state.bookmarkTags = {};

  }

}



function toggleBookmark(questionId) {

  if (!questionId) return;

  const isBookmarked = state.bookmarks.has(questionId);

  if (isBookmarked) {

    state.bookmarks.delete(questionId);

    showToast('Removed from bookmarks', 'info');

  } else {

    state.bookmarks.add(questionId);

    showToast('Saved to bookmarks ⭐', 'success');

  }

  saveBookmarks();

  // Dynamically update all matching bookmark buttons

  document.querySelectorAll(`.star-btn[data-qid="${questionId}"]`).forEach(btn => {

    btn.classList.toggle('bookmarked', !isBookmarked);

    btn.setAttribute('title', !isBookmarked ? 'Remove Bookmark' : 'Add Bookmark');

    btn.innerHTML = !isBookmarked ? '⭐' : '☆';

  });

  // If practice list is currently filtered by bookmarks, refresh list

  if (state.currentPage === 'practice' && state.practiceFilters.status === 'bookmarked') {

    renderPractice(document.getElementById('page-content'));

  }

}



// ─── KaTeX MATH RENDERING HELPER ──────────────────────────────────────────────

// === CODE SYNTAX HIGHLIGHTING ===

function highlightCodeBlocks(container) {

  if (!container || !window.Prism) return;

  try {

    container.querySelectorAll('pre code, code[class*="language-"]').forEach(b => Prism.highlightElement(b));

  } catch(e) {}

}



let mathRenderQueue = new Set();

let mathRenderFrame = null;



function renderMath(container) {

  const el = container || document.getElementById('page-content') || document.body;

  if (!el) return;

  if (typeof window.renderMathInElement !== 'function') {

    setTimeout(() => renderMath(container), 150);

    return;

  }

  mathRenderQueue.add(el);

  if (!mathRenderFrame) {

    mathRenderFrame = requestAnimationFrame(() => {

      const targets = Array.from(mathRenderQueue);

      mathRenderQueue.clear();

      mathRenderFrame = null;

      targets.forEach(target => {

        try {

          window.renderMathInElement(target, {

            delimiters: [

              { left: '$$', right: '$$', display: true },

              { left: '$', right: '$', display: false },

              { left: '\\(', right: '\\)', display: false },

              { left: '\\[', right: '\\]', display: true }

            ],

            strict: false,

            throwOnError: false,

            ignoredTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code'],

            ignoredClasses: ['code-block', 'code-block-container', 'inline-code']

          });

        } catch(err) {

          console.warn('[KaTeX] render error:', err);

        }

      });

    });

  }

}



if (typeof window !== 'undefined') {

  window.addEventListener('DOMContentLoaded', () => setTimeout(() => renderMath(), 200));

  window.addEventListener('load', () => setTimeout(() => renderMath(), 400));

}



// ─── SYNC STATUS ─────────────────────────────────────────────────────────────

function setSyncStatus(s) {

  const dot   = document.getElementById('sync-dot');

  const label = document.getElementById('sync-label');

  if (!dot||!label) return;

  const isOnline = (typeof navigator !== 'undefined' && typeof navigator.onLine === 'boolean') ? navigator.onLine : true;

  if (!isOnline) {
    dot.style.background = '#9090b0';
    label.textContent    = 'Offline Mode';
    return;
  }

  const m = {
    connecting:{ color:'#f59e0b', text:'Connecting…'     },
    syncing:   { color:'#3b82f6', text:'Syncing…'         },
    online:    { color:'#22c55e', text: state.isGuest ? 'Online (Guest)' : 'Cloud Synced ✓' },
    offline:   { color:'#9090b0', text:'Offline Mode'     },
    error:     { color:'#ef4444', text:'Offline Available'},
  };

  if (state.isGuest) {
    if (s === 'connecting') {
      dot.style.background = m.connecting.color;
      label.textContent    = m.connecting.text;
    } else if (s === 'syncing') {
      dot.style.background = m.syncing.color;
      label.textContent    = m.syncing.text;
    } else {
      dot.style.background = m.online.color;
      label.textContent    = m.online.text;
    }
    return;
  }

  dot.style.background  = (m[s]||m.offline).color;

  label.textContent     = (m[s]||m.offline).text;

}



// ─── FS HELPERS ───────────────────────────────────────────────────────────────

async function fsAll(colRef)      { const s=await getDocs(colRef); return s.docs.map(d=>({_id:d.id,...d.data()})); }

async function fsSet(ref,data)    { await setDoc(ref,JSON.parse(JSON.stringify(data)),{merge:true}); }

async function fsAdd(ref,data)    { const r=await addDoc(ref,{...JSON.parse(JSON.stringify(data)),createdAt:serverTimestamp()}); return r.id; }

async function fsDel(ref)         { await deleteDoc(ref); }



// ─── LOAD FROM FIRESTORE ──────────────────────────────────────────────────────

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

  // Only query community-contributed questions to save bandwidth and Firestore quota

  const communityQuery = query(qCol(), where('source', '==', 'community'));

  _unQ = onSnapshot(communityQuery, snap => {

    const fsQs = snap.docs.map(d => ({ ...d.data(), id: d.id }));

    state.questions = mergeQuestionArrays(state.questions, fsQs);

    saveCache();

    setSyncStatus('online');

    const noTest = !document.getElementById('test-overlay')?.classList.contains('active');

    if (noTest && ['dashboard','subjects','practice','pyqs','upload'].includes(state.currentPage)) {

      renderPage(state.currentPage, state.currentParams || {});

    }

  }, e => {

    console.warn('[FS] Community questions listener fallback:', e);

    setSyncStatus('online');

  });



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



// ─── NETWORK EVENTS ───────────────────────────────────────────────────────────

function setupNetworkListeners() {

  window.addEventListener('online', async () => {

    showToast('🌐 Back online!','info',2500);

    setSyncStatus(state.isGuest ? 'online' : 'syncing');

    if (state.isGuest) {
      if (USE_FB) {
        try {
          const cloudQs = await fsAll(qCol());
          if (cloudQs && cloudQs.length) {
            state.questions = mergeQuestionArrays(state.questions, cloudQs);
            saveCache();
          }
        } catch(e){}
      }
      return;
    }

    if (USE_FB && currentUser) {

      teardownListeners();

      const ok = await loadFromFirestore();

      if (ok) {

        setupListeners();

        const noTest = !document.getElementById('test-overlay')?.classList.contains('active');

        if (noTest) renderPage(state.currentPage, state.currentParams||{});

        showToast('✅ Synced!','success',2000);

      }

    }

  });

  window.addEventListener('offline', () => {

    setSyncStatus('offline');

    showToast('📴 Offline — using local cache','info',3000);

  });

}



// ─── WRITE HELPERS ────────────────────────────────────────────────────────────

async function persistQuestion(q) {

  if (USE_FB) {

    try { await fsSet(qDoc(q.id), q); }

    catch(e) { showToast('⚠️ Sync error — saved locally','error'); }

  }

  const i = state.questions.findIndex(x=>x.id===q.id);

  if (i>=0) state.questions[i]=q; else state.questions.push(q);

  saveCache();

}



async function persistAttempt(att) {

  if (USE_FB) { try { await fsSet(attDoc(att.questionId), att); } catch(e){} }

  const i = state.attempts.findIndex(a=>a.questionId===att.questionId);

  if (i>=0) state.attempts[i]=att; else state.attempts.push(att);

  saveCache();

}



async function persistSession(session) {

  let id = session.id;

  if (USE_FB) {

    try {

      if (!id) id = await fsAdd(sesCol(), session);

      else await fsSet(sesDoc(id), session);

    } catch(e) { console.error(e); }

  }

  if (!id) id = 'local_'+Date.now();

  session.id = id;

  state.testSessions.push(session);

  saveCache();

}



async function removeQuestion(id) {

  if (STATIC_BUNDLED_IDS.has(id)) {

    showToast('⚠️ Built-in bank questions cannot be deleted', 'warning');

    return;

  }

  const qTarget = state.questions.find(x => x.id === id);

  const isOwner = qTarget && qTarget.uploadedBy && qTarget.uploadedBy === uid();

  if (!state.isAdmin && !isOwner) {

    showToast('⚠️ Admin privileges required to delete questions', 'error');

    return;

  }

  if (USE_FB) { try { await fsDel(qDoc(id)); } catch(e){} }

  state.questions = state.questions.filter(q=>q.id!==id);

  saveCache();

}



async function clearAllQuestions() {

  if (!state.isAdmin) {

    showToast('⚠️ Admin privileges required to clear questions', 'error');

    return;

  }

  if (!confirm('Delete all community questions? This cannot be undone!')) return;

  if (USE_FB) {

    setSyncStatus('syncing');

    try {

      const communityQs = state.questions.filter(q => !STATIC_BUNDLED_IDS.has(q.id));

      const CHUNK=450;

      for (let i=0;i<communityQs.length;i+=CHUNK){

        const b=writeBatch(db);

        communityQs.slice(i,i+CHUNK).forEach(q=>b.delete(qDoc(q.id)));

        await b.commit();

      }

      setSyncStatus('online');

    } catch(e) { setSyncStatus('error'); }

  }

  state.questions = state.questions.filter(q => STATIC_BUNDLED_IDS.has(q.id));

  saveCache();

  renderUpload(document.getElementById('page-content'));

  showToast('Community questions cleared (built-in bank preserved)','info');

}



// ─── DUPLICATE DETECTION ──────────────────────────────────────────────────────

function normalizeText(s) {

  return (s||'').toLowerCase().replace(/\s+/g,' ').replace(/[^a-z0-9 ]/g,'').trim();

}



function isDuplicate(q) {

  // Check 1: exact ID match

  if (state.questions.find(x=>x.id===q.id)) return { dupe:true, reason:'Same ID' };

  // Check 2: very similar question text (≥90% words overlap)

  const norm = normalizeText(q.question);

  for (const ex of state.questions) {

    const enorm = normalizeText(ex.question);

    if (norm.length>20 && enorm.length>20) {

      const a=new Set(norm.split(' ')), b=new Set(enorm.split(' '));

      const inter=[...a].filter(w=>b.has(w)).length;

      const union=new Set([...a,...b]).size;

      if (inter/union >= 0.85) return { dupe:true, reason:'Similar question text', similar:ex.id };

    }

  }

  return { dupe:false };

}



// ─── BULK IMPORT ─────────────────────────────────────────────────────────────

async function bulkImportQuestions(newQs) {

  let added=0, dupes=0, invalid=0;

  const existingIds = new Set(state.questions.map(q => q.id));

  const toAdd=[];

  for (const q of newQs) {

    if (!q.id||!q.question) { invalid++; continue; }

    if (existingIds.has(q.id)) { dupes++; continue; }

    existingIds.add(q.id);

    if (!q.uploadedBy && currentUser) q.uploadedBy = uid();

    if (!q.source) q.source = state.isAdmin ? 'official' : 'community';

    if (q.type === 'tf') q.type = 'mcq';

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

        data.forEach(item => { if (item && item.id) STATIC_BUNDLED_IDS.add(item.id); });

        state.questions = mergeQuestionArrays(state.questions, data);

        state.questions = state.questions.filter(q => q && q.question && q.question.trim().length >= 5);

        indexQuestionsForSearch(state.questions);

        saveCache();

      }

    }

  } catch(e) {

    console.warn('[Static] sample_questions.json load:', e);

  }

}



// ─── CLOUD SYNC UTILITY ──────────────────────────────────────────────────────

window.ingestHardMocks = async function() {
  if (!state.isAdmin) {
    showToast('⚠️ Admin privileges required to ingest mock tests', 'error');
    return;
  }
  showToast('Loading 30 Extreme Hard Mock Tests (1,950 questions)...', 'info', 2500);
  try {
    const res = await fetch('./data/gate_30_hard_mocks.json');
    if (!res.ok) throw new Error('File not found: ./data/gate_30_hard_mocks.json');
    const data = await res.json();
    await bulkImportQuestions(data);
  } catch(err) {
    showToast('Failed to load hard mocks: ' + err.message, 'error');
  }
};

window.ingestMediumMocks = async function() {

  if (!state.isAdmin) {

    showToast('⚠️ Admin privileges required to ingest mock tests', 'error');

    return;

  }

  showToast('Loading 30 Medium Mock Tests (1,950 questions)...', 'info', 2500);

  try {

    const res = await fetch('./data/gate_30_medium_mocks.json');

    if (!res.ok) throw new Error('File not found: ./data/gate_30_medium_mocks.json');

    const data = await res.json();

    await bulkImportQuestions(data);

  } catch(err) {

    showToast('Failed to load medium mocks: ' + err.message, 'error');

  }

};



window.ingestEasy1Mocks = async function() {
  if (!state.isAdmin) {
    showToast('⚠️ Admin privileges required to ingest mock tests', 'error');
    return;
  }
  showToast('Loading 30 Easy Mock Tests Set 2 (1,950 questions)...', 'info', 2500);
  try {
    const res = await fetch('./data/gate_30_easy1_mocks.json');
    if (!res.ok) throw new Error('File not found: ./data/gate_30_easy1_mocks.json');
    const data = await res.json();
    await bulkImportQuestions(data);
  } catch(err) {
    showToast('Failed to load easy mocks set 2: ' + err.message, 'error');
  }
};

window.ingestEasyMocks = async function() {

  if (!state.isAdmin) {

    showToast('⚠️ Admin privileges required to ingest mock tests', 'error');

    return;

  }

  showToast('Loading 30 Easy Mock Tests (1,950 questions)...', 'info', 2500);

  try {

    const res = await fetch('./data/gate_30_easy_mocks.json');

    if (!res.ok) throw new Error('File not found: ./data/gate_30_easy_mocks.json');

    const data = await res.json();

    await bulkImportQuestions(data);

  } catch(err) {

    showToast('Failed to load easy mocks: ' + err.message, 'error');

  }

};



window.pushAllQuestionsToCloud = async function() {

  if (!state.isAdmin) {

    showToast('⚠️ Admin privileges required to push question bank to Cloud', 'error');

    return;

  }

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



// ─── LOGIN UI ─────────────────────────────────────────────────────────────────

function renderLoginPage() {
  if (state.isGuest || (typeof sessionStorage !== 'undefined' && sessionStorage.getItem('gate_is_guest') === '1')) {
    return;
  }
  document.querySelectorAll('.auth-overlay').forEach(el => el.remove());

  // Hide main app
  const sb = document.getElementById('sidebar');
  if (sb) sb.style.display = 'none';
  const mn = document.getElementById('main');
  if (mn) mn.style.display = 'none';
  const tc = document.getElementById('toast-container');
  if (tc) tc.style.display = 'flex';

  let mode = 'login'; // 'login', 'signup', or 'forgot'

  const overlay = document.createElement('div');
  overlay.className  = 'auth-overlay';
  overlay.id         = 'auth-overlay';
  overlay.innerHTML  = buildAuthCard('login');
  document.body.appendChild(overlay);

  bindAuthEvents();

  function buildAuthCard(m) {
    const isLogin  = m === 'login';
    const isForgot = m === 'forgot';
    const isSignup = m === 'signup';
    const savedEmail = localStorage.getItem('gate_last_email') || '';

    let heading = 'Welcome back 👋';
    let subheading = 'Sign in to continue your GATE preparation.';
    if (isSignup) {
      heading = 'Create account 🎯';
      subheading = 'Join thousands of GATE aspirants.';
    } else if (isForgot) {
      heading = 'Reset Password 🔑';
      subheading = 'Enter your email address to receive a secure password reset link.';
    }

    return `
      <div class="auth-card">
        <div class="auth-logo">
          <div class="auth-logo-icon">G</div>
          <div class="auth-logo-text">
            <div class="auth-logo-title">GATE CSE</div>
            <div class="auth-logo-sub">Practice Platform</div>
          </div>
        </div>
        <h1 class="auth-heading">${heading}</h1>
        <p class="auth-subheading">${subheading}</p>

        <div class="auth-error" id="auth-error"></div>
        <div class="auth-success" id="auth-success"></div>

        <div class="auth-form">
          ${isSignup ? `<div class="auth-input-group">
            <label class="auth-label">Full Name</label>
            <input type="text" class="auth-input" id="auth-name" placeholder="Your Full Name" autocomplete="name"/>
          </div>` : ''}

          <div class="auth-input-group">
            <label class="auth-label">Email</label>
            <input type="email" class="auth-input" id="auth-email" value="${savedEmail}" placeholder="you@gmail.com" autocomplete="username email"/>
          </div>

          ${!isForgot ? `<div class="auth-input-group">
            <div style="display:flex;justify-content:space-between;align-items:center;">
              <label class="auth-label" style="margin:0;">Password</label>
              ${isLogin ? `<a href="javascript:void(0)" class="auth-forgot-link" onclick="switchAuthMode('forgot')" title="Forgot your password?">Forgot Password?</a>` : ''}
            </div>
            <input type="password" class="auth-input" id="auth-password" placeholder="Min. 6 characters" autocomplete="${isLogin ? 'current-password' : 'new-password'}"/>
          </div>` : ''}

          <button class="auth-btn-primary" id="auth-submit-btn" onclick="${isForgot ? 'handleForgotPassword()' : 'handleEmailAuth()'}">
            ${isForgot ? 'Send Password Reset Link' : (isLogin ? 'Sign In' : 'Create Account')}
          </button>

          ${!isForgot ? `
          <div class="auth-divider">OR</div>

          <button class="auth-btn-google" onclick="handleGoogleAuth()">
            <svg class="google-icon" viewBox="0 0 48 48">
              <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
              <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
              <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
              <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.18 1.48-4.97 2.34-8.16 2.34-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
            </svg>
            Continue with Google
          </button>` : ''}

          <div class="auth-switch">
            ${isForgot
              ? `Remember your password? <span class="auth-switch-link" onclick="switchAuthMode('login')">Back to Sign In</span>`
              : (isLogin
                ? `Don't have an account? <span class="auth-switch-link" onclick="switchAuthMode('signup')">Sign Up</span>`
                : `Already have an account? <span class="auth-switch-link" onclick="switchAuthMode('login')">Sign In</span>`)}
          </div>

          <div class="auth-offline-box">
            <div class="auth-offline-title">⚡ Instant Practice / Guest Mode</div>
            <div class="auth-offline-desc">Practice without an account — 32,383 verified questions, 231 full-length mocks, and 35 years of PYQs available online & offline with local storage saving.</div>
            <button class="btn btn-secondary btn-sm" id="auth-guest-btn" onclick="continueAsGuest(this)" style="width:100%;font-weight:700;touch-action:manipulation" type="button">
              ⚡ Start Instant Practice (Guest)
            </button>
          </div>
        </div>
      </div>`;
  }

  function bindAuthEvents() {
    // Allow Enter key to submit
    overlay.addEventListener('keydown', e => {
      if (e.key === 'Enter') {
        if (mode === 'forgot') handleForgotPassword();
        else handleEmailAuth();
      }
    });

    const gBtn = document.getElementById('auth-guest-btn');
    if (gBtn) {
      const triggerGuest = (e) => {
        if (e) { e.preventDefault(); e.stopPropagation(); }
        continueAsGuest(gBtn);
      };
      gBtn.addEventListener('click', triggerGuest);
      gBtn.addEventListener('touchend', triggerGuest);
    }
  }

  window.switchAuthMode = (m) => {
    const curEmail = document.getElementById('auth-email')?.value?.trim();
    if (curEmail) {
      try { localStorage.setItem('gate_last_email', curEmail); } catch(e){}
    }
    mode = m;
    overlay.innerHTML = buildAuthCard(m);
    overlay.scrollTop = 0;
    bindAuthEvents();
    setTimeout(() => {
      if (m === 'forgot') {
        const em = document.getElementById('auth-email');
        if (em && !em.value) em.focus();
        else document.getElementById('auth-submit-btn')?.focus();
      } else if (m === 'signup') {
        document.getElementById('auth-name')?.focus();
      } else {
        const em = document.getElementById('auth-email');
        if (em && !em.value) em.focus();
        else document.getElementById('auth-password')?.focus();
      }
    }, 50);
  };

  window.continueAsGuest = async (btn) => {
    state.isGuest = true;
    try { sessionStorage.setItem('gate_is_guest', '1'); } catch(e){}
    const activeBtn = btn || document.getElementById('auth-guest-btn') || document.querySelector('.auth-offline-box button');
    if (activeBtn) {
      activeBtn.disabled = true;
      activeBtn.innerHTML = '⚡ Launching Offline Practice…';
    }
    removeLoginPage();
    await bootApp(null);
  };

  window.handleForgotPassword = async () => {
    let rawInput = document.getElementById('auth-email')?.value?.trim() || '';
    const btn    = document.getElementById('auth-submit-btn');
    const errEl  = document.getElementById('auth-error');
    const sucEl  = document.getElementById('auth-success');

    if (errEl) { errEl.className = 'auth-error'; errEl.textContent = ''; }
    if (sucEl) { sucEl.className = 'auth-success'; sucEl.textContent = ''; }

    if (!rawInput) {
      if (errEl) {
        errEl.textContent = 'Please enter your registered email address.';
        errEl.className = 'auth-error show';
      }
      document.getElementById('auth-email')?.focus();
      return;
    }

    let email = rawInput.toLowerCase();
    const adminMatch = email.match(/^admin_?([1-9]|10)$/);
    if (adminMatch) {
      email = `admin_${adminMatch[1]}@gateprep.com`;
    }

    if (!email.includes('@') || !email.includes('.')) {
      if (errEl) {
        errEl.textContent = 'Please enter a valid email address.';
        errEl.className = 'auth-error show';
      }
      return;
    }

    if (!auth) {
      if (errEl) {
        errEl.textContent = '⚠️ Firebase Auth is not active. Password reset requires an active cloud connection.';
        errEl.className = 'auth-error show';
      }
      return;
    }

    if (btn) {
      btn.disabled = true;
      btn.innerHTML = `<span class="auth-spinner"></span> Sending reset link…`;
    }

    try {
      await sendPasswordResetEmail(auth, email);
      try { localStorage.setItem('gate_last_email', rawInput); } catch(e){}

      if (sucEl) {
        sucEl.innerHTML = `✅ Password reset email sent to <strong>${escapeHtml(email)}</strong>.<br><span style="font-size:12px;opacity:0.9">Please check your inbox (including Spam/Junk folder) and follow the link to reset your password.</span><div style="margin-top:12px"><button class="btn btn-secondary btn-sm" onclick="switchAuthMode('login')" style="width:100%" type="button">← Back to Sign In</button></div>`;
        sucEl.className = 'auth-success show';
      }

      if (btn) {
        btn.disabled = false;
        btn.textContent = 'Resend Reset Link';
      }
    } catch(e) {
      console.warn('[Forgot Password] Error:', e.code, e.message);

      if (btn) {
        btn.disabled = false;
        btn.textContent = 'Send Password Reset Link';
      }

      const msgs = {
        'auth/user-not-found': 'No account found with this email address.',
        'auth/invalid-email': 'Please enter a valid email address.',
        'auth/missing-email': 'Please enter your email address.',
        'auth/too-many-requests': 'Too many requests. Please wait a few moments before trying again.',
        'auth/network-request-failed': 'No internet connection. Please check your network and try again.',
      };

      if (errEl) {
        errEl.textContent = msgs[e.code] || e.message || 'Failed to send password reset email. Please try again.';
        errEl.className = 'auth-error show';
      }
    }
  };

  window.handleEmailAuth = async () => {

    let rawInput   = document.getElementById('auth-email')?.value?.trim() || '';

    const password = document.getElementById('auth-password')?.value;

    const name     = document.getElementById('auth-name')?.value?.trim();

    const btn      = document.getElementById('auth-submit-btn');

    const errEl    = document.getElementById('auth-error');

    const sucEl    = document.getElementById('auth-success');



    errEl.className='auth-error'; sucEl.className='auth-success';

    if (!rawInput||!password) { errEl.textContent='Please fill all fields'; errEl.className='auth-error show'; return; }

    if (password.length<6) { errEl.textContent='Password must be at least 6 characters'; errEl.className='auth-error show'; return; }



    btn.disabled=true;

    btn.innerHTML=`<span class="auth-spinner"></span> ${mode==='login'?'Signing in…':'Creating account…'}`;



    // Normalize input: map admin_1..admin_10 to admin_X@gateprep.com

    let email = rawInput.toLowerCase();

    const adminMatch = email.match(/^admin_?([1-9]|10)$/);

    if (adminMatch) {

      email = `admin_${adminMatch[1]}@gateprep.com`;

    } else if (!email.includes('@')) {

      email = email + '@gateprep.com';

    }



    try {

      if (mode==='login') {

        try {

          await signInWithEmailAndPassword(auth, email, password);

        } catch(loginErr) {

          // Security Hardening: Auto-provisioning is strictly restricted to localhost development.
          // In production (thematrixisreal404.github.io), admin accounts must be created in Firebase Console.
          const isLocalDev = typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');

          if (isLocalDev && ADMIN_EMAILS.has(email) && password === 'admin@1234' &&

              (loginErr.code === 'auth/user-not-found' || loginErr.code === 'auth/invalid-credential')) {

            const adminNum = email.split('@')[0];

            const cred = await createUserWithEmailAndPassword(auth, email, password);

            if (cred && cred.user) {

              await updateProfile(cred.user, { displayName: `Admin (${adminNum})` });

            }

          } else {

            throw loginErr;

          }

        }

      } else {

        // Block public registration using reserved admin email addresses
        if (ADMIN_EMAILS.has(email)) {
          throw new Error('Registration for administrative accounts is disabled. Please sign in directly.');
        }

        const cred = await createUserWithEmailAndPassword(auth, email, password);

        if (name) await updateProfile(cred.user, { displayName: name });

      }

      try { localStorage.setItem('gate_last_email', rawInput); } catch(e){}

      // onAuthStateChanged will fire and boot the app

    } catch(e) {

      // Security Hardening: Offline fallback for admin login is strictly restricted to localhost development
      const isLocalDev = typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');

      if (isLocalDev && ADMIN_EMAILS.has(email) && password === 'admin@1234' && (e.code === 'auth/network-request-failed' || !USE_FB)) {

        removeLoginPage();

        const fakeUser = {

          uid: 'admin_' + email.replace(/[^a-z0-9]/g, '_'),

          email: email,

          displayName: `Admin (${rawInput})`

        };

        await bootApp(fakeUser);

        showToast('🛡️ Signed in as Administrator (Offline / Local Mode)', 'success', 4000);

        return;

      }

      if (e.code === 'auth/network-request-failed') {

        errEl.innerHTML = `⚠️ No internet connection detected. <span style="text-decoration:underline;cursor:pointer;font-weight:700;color:var(--accent)" onclick="continueAsGuest()">Click here to enter Offline Mode →</span>`;

        errEl.className = 'auth-error show';

        btn.disabled = false;

        btn.textContent = mode==='login'?'Sign In':'Create Account';

        return;

      }

      const msgs = {

        'auth/user-not-found':    'No account found with this email.',

        'auth/wrong-password':    'Incorrect password. Try again.',

        'auth/email-already-in-use': 'This email is already registered. Sign in instead.',

        'auth/invalid-email':     'Please enter a valid email address.',

        'auth/network-request-failed': 'No internet connection.',

        'auth/too-many-requests': 'Too many attempts. Try again later.',

        'auth/invalid-credential': 'Incorrect email or password.',

      };

      errEl.textContent = msgs[e.code]||e.message;

      errEl.className   = 'auth-error show';

      btn.disabled=false;

      btn.textContent = mode==='login'?'Sign In':'Create Account';

    }

  };



  window.handleGoogleAuth = async () => {
    if (!auth) {
      const errEl = document.getElementById('auth-error');
      if (errEl) {
        errEl.textContent = '⚠️ Firebase Auth is not active. Use "Continue as Guest".';
        errEl.className = 'auth-error show';
      }
      return;
    }

    const btn = document.querySelector('.auth-btn-google');
    const originalHTML = btn ? btn.innerHTML : '';
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = `<span style="display:inline-block;width:14px;height:14px;border:2px solid #fff;border-top-color:transparent;border-radius:50%;animation:spin 0.8s linear infinite;margin-right:8px;vertical-align:middle;"></span> Connecting...`;
    }

    const errEl = document.getElementById('auth-error');
    if (errEl) {
      errEl.className = 'auth-error';
      errEl.textContent = '';
    }

    const provider = new GoogleAuthProvider();
    provider.setCustomParameters({ prompt: 'select_account' });

    try {
      // Primary: signInWithPopup avoids cross-origin redirect/cookie loops on GitHub Pages
      const res = await signInWithPopup(auth, provider);
      if (res && res.user) {
        removeLoginPage();
        await bootApp(res.user);
        showToast(`✅ Welcome, ${res.user.displayName || res.user.email}!`, 'success');
        return;
      }
    } catch(e) {
      console.warn('[Google Auth] Popup result:', e.code, e.message);

      if (e.code === 'auth/popup-closed-by-user') {
        if (btn) {
          btn.disabled = false;
          btn.innerHTML = originalHTML;
        }
        return;
      }

      if (e.code === 'auth/popup-blocked') {
        // Fallback to redirect if popup is blocked
        try {
          await signInWithRedirect(auth, provider);
          return;
        } catch(redErr) {
          displayGoogleAuthError(redErr, btn, originalHTML);
          return;
        }
      }

      displayGoogleAuthError(e, btn, originalHTML);
    }
  };

  function displayGoogleAuthError(e, btn, originalHTML) {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = originalHTML;
    }
    const errEl = document.getElementById('auth-error');
    if (!errEl) return;

    if (e.code === 'auth/unauthorized-domain') {
      errEl.textContent = `⚠️ Domain "${window.location.hostname}" is not authorized. Add it in Firebase Console → Authentication → Settings → Authorized domains.`;
    } else if (e.code === 'auth/operation-not-allowed') {
      errEl.textContent = '⚠️ Google Sign-In is disabled in Firebase. Enable "Google" under Firebase Console → Authentication → Sign-in method.';
    } else {
      errEl.textContent = '⚠️ ' + (e.message || e.code);
    }
    errEl.className = 'auth-error show';
  };

}



function removeLoginPage() {
  document.querySelectorAll('.auth-overlay').forEach(el => el.remove());
  const sb = document.getElementById('sidebar');
  if (sb) sb.style.display = '';
  const mn = document.getElementById('main');
  if (mn) mn.style.display = '';
  const pc = document.getElementById('page-content');
  if (pc) pc.classList.remove('hidden');
  const ls = document.getElementById('loading-screen');
  if (ls) ls.style.display = 'none';
}

async function continueAsGuest(btn) {
  state.isGuest = true;
  try { sessionStorage.setItem('gate_is_guest', '1'); } catch(e){}
  setSyncStatus(navigator.onLine ? 'online' : 'offline');

  const activeBtn = btn || document.getElementById('auth-guest-btn') || document.getElementById('loading-guest-btn') || document.querySelector('.auth-offline-box button');
  if (activeBtn) {
    activeBtn.disabled = true;
    activeBtn.innerHTML = '⚡ Launching Practice…';
  }

  const lMsg = document.getElementById('loading-msg');
  if (lMsg) lMsg.textContent = 'Preparing question bank…';

  removeLoginPage();

  // If questions are already cached in state, dismiss loading screen right away
  const ls = document.getElementById('loading-screen');
  const pc = document.getElementById('page-content');
  if (state.questions && state.questions.length > 500) {
    if (ls) ls.style.display = 'none';
    if (pc) pc.classList.remove('hidden');
  }

  await bootApp(null);
}

window.continueAsGuest = continueAsGuest;







// ─── UPDATE TOPBAR USER INFO ──────────────────────────────────────────────────

function updateTopbarUser() {

  const nameEl   = document.querySelector('.user-name');

  const roleEl   = document.querySelector('.user-role');

  const avatarEl = document.querySelector('.user-avatar');

  const badgeEl  = document.getElementById('topbar-badge');

  if (nameEl)   nameEl.innerHTML   = `${escapeHtml(uName())}${state.isAdmin ? ' <span class="admin-badge-topbar" style="background:var(--accent);color:#fff;font-size:10px;font-weight:700;padding:2px 6px;border-radius:4px;vertical-align:middle;margin-left:4px;letter-spacing:0.5px">🛡️ ADMIN</span>' : ''}`;

  if (roleEl)   roleEl.textContent   = state.isAdmin ? `Administrator • ${uEmail()}` : (uEmail() || (state.isGuest ? 'Guest Session' : ''));

  if (avatarEl) avatarEl.textContent = state.isAdmin ? '👑' : uInitial();

  if (badgeEl)  badgeEl.textContent  = state.isGuest ? 'Guest Mode' : uName();



  // Add sign-out button to topbar if not already there

  const topbarRight = document.querySelector('.topbar-right');

  if (topbarRight && !document.getElementById('signout-btn')) {

    const btn = document.createElement('button');

    btn.className = 'btn-signout';

    btn.id        = 'signout-btn';

    btn.textContent = '⎋ Sign Out';

    btn.onclick   = handleSignOut;

    topbarRight.appendChild(btn);

  }

}



async function handleSignOut() {

  if (!confirm('Sign out?')) return;
  state.isGuest = false;
  try { sessionStorage.removeItem('gate_is_guest'); } catch(e){}

  teardownListeners();

  // Clear user-private attempts & test sessions only; preserve question bank in memory & IndexedDB

  state.attempts=[]; state.testSessions=[];

  await signOut(auth);

  // onAuthStateChanged fires → shows login
}

window.promptPasswordReset = async () => {
  if (!currentUser || !currentUser.email) {
    showToast('⚠️ You are currently using Guest/Offline mode. Please sign in with an email account to manage your password.', 'warning', 4500);
    return;
  }
  const isGoogle = currentUser.providerData && currentUser.providerData.some(p => p.providerId === 'google.com');
  if (isGoogle) {
    showToast('ℹ️ Your account is signed in via Google. Manage your password in your Google Account settings.', 'info', 4500);
    return;
  }
  if (!confirm(`Send a password reset email to ${currentUser.email}?`)) {
    return;
  }
  try {
    await sendPasswordResetEmail(auth, currentUser.email);
    showToast(`✅ Password reset email sent to ${currentUser.email}! Please check your inbox.`, 'success', 5000);
  } catch(e) {
    showToast(`⚠️ Failed to send reset email: ${e.message}`, 'error', 4500);
  }

}



// ─── ROUTER ───────────────────────────────────────────────────────────────────

function navigate(page, params={}) {

  // Persist practice state when leaving the practice page

  if (state.currentPage === 'practice' && page !== 'practice') {

    state.lastPracticeState = {

      filters: { ...state.practiceFilters },

      page: state.practicePage,

      pageSize: state.practicePageSize,

      search: state.practiceSearch || ''

    };

  }

  if (page === 'papers') {

    navigate('mocks', { tab: 'practice-sets' });

    return;

  }

  state.currentPage   = page;

  state.currentParams = params;

  if (!params.mockId) {

    state.activeMockPaper = null;

  }

  if (window.innerWidth <= 768) {

    window.closeMobileSidebar?.();

  }

  document.querySelectorAll('.sidebar-nav-item').forEach(el=>

    el.classList.toggle('active', el.dataset.page===page));

  const titles = {
    dashboard:'Dashboard', subjects:'Subjects', practice:'Practice Questions',
    mocks:'Mock Tests', 'subject-tests':'Subject Tests', 'pyq-exams':'Full-Length PYQ Exams', pyqs:'Topic-Wise PYQs', 'topic-pyqs':'Topic-Wise PYQs',
    patterns:'Repeating Patterns Hub (1983–2026)', playlists:'Smart Playlists & Revision Buckets', mistakes:'Mistake Vault & Revision', performance:'Performance', upload:'Upload Questions',
  };

  document.getElementById('topbar-title').textContent = titles[page]||page;

  renderPage(page, params);

  document.querySelector('.main').scrollTop = 0;

}



function renderPage(page, params={}) {

  const c = document.getElementById('page-content');

  c.innerHTML=''; c.className='page-content fade-in';

  switch(page) {

    case 'dashboard':     renderDashboard(c);         break;

    case 'subjects':      renderSubjects(c);          break;

    case 'practice':      renderPractice(c, params);  break;

    case 'mocks':         renderMocks(c, params);     break;

    case 'subject-tests': renderSubjectTests(c, params); break;

    case 'patterns':      renderRepeatingPatterns(c, params); break;

    case 'pyq-exams':     renderPyqExams(c);          break;

    case 'papers':        renderMocks(c, { tab: 'practice-sets' }); break;

    case 'pyqs':

    case 'topic-pyqs':    renderPYQs(c);              break;

    case 'playlists':     renderPlaylists(c);         break;

    case 'mistakes':      renderMistakes(c);          break;

    case 'performance':   renderPerformance(c);       break;

    case 'upload':      renderUpload(c);            break;

    default: c.innerHTML='<div class="empty-state"><div class="empty-state-icon">🚧</div><div class="empty-state-title">Coming Soon</div></div>';

  }

  renderMath(c);

}



// ─── STATS HELPERS ───────────────────────────────────────────────────────────

function getStats() {

  const validAttempts = state.attempts.filter(a => !a.unscored);

  const attempted = validAttempts.length;

  const correct   = validAttempts.filter(a => a.correct).length;

  return {

    attempted, correct,

    accuracy:  attempted>0 ? Math.round((correct/attempted)*100) : 0,

    sessions:  state.testSessions.length,

  };

}



function getSubjectStats(subjectName) {

  const qs  = state.questions.filter(q=>q.subject===subjectName);

  const map = new Map(state.attempts.map(a=>[a.questionId,a]));

  const done= qs.filter(q=>map.has(q.id));

  const ok  = done.filter(q=>map.get(q.id)?.correct);

  return {

    total:     qs.length,

    doneCount: done.length,

    accuracy:  done.length>0 ? Math.round((ok.length/done.length)*100) : 0,

  };

}



// ─── DASHBOARD ───────────────────────────────────────────────────────────────

function renderDashboard(c) {

  const { attempted, accuracy, sessions } = getStats();

  c.innerHTML=`

    <div class="hero-banner">

      <h2>Keep going, ${uName().split(' ')[0]}. Your GATE rank is built here.</h2>

      <p>Practice subject-wise, analyze mistakes and improve every day.</p>

      <div class="hero-cta">

        <button class="btn btn-white" onclick="navigate('subjects')">📚 Practice Now</button>

        <button class="btn btn-outline-white" onclick="navigate('mocks')">🎯 Mock Tests</button>

        <button class="btn btn-outline-white" onclick="navigate('pyq-exams')">⏱️ Full-Length PYQ Exams</button>

      </div>

    </div>

    <div class="stats-grid">

      <div class="stat-card stat-card-accent" style="--accent-color:#6c63ff">

        <div class="stat-icon">📝</div><div class="stat-label">Questions Attempted</div>

        <div class="stat-value">${attempted}</div><div class="stat-sub">Across all subjects</div>

      </div>

      <div class="stat-card stat-card-accent" style="--accent-color:#22c55e">

        <div class="stat-icon">✅</div><div class="stat-label">Tests Completed</div>

        <div class="stat-value">${sessions}</div><div class="stat-sub">Mock + Subject tests</div>

      </div>

      <div class="stat-card stat-card-accent" style="--accent-color:#f59e0b">

        <div class="stat-icon">🎯</div><div class="stat-label">Accuracy</div>

        <div class="stat-value">${accuracy}%</div><div class="stat-sub">${attempted>0?'Overall performance':'Start practicing!'}</div>

      </div>

      <div class="stat-card stat-card-accent" style="--accent-color:#14b8a6">

        <div class="stat-icon">📚</div><div class="stat-label">Total Questions</div>

        <div class="stat-value">${state.questions.length}</div><div class="stat-sub">In question bank</div>

      </div>

    </div>

    <!-- 🎯 GATE READINESS BENCHMARK -->

    ${buildGateReadinessCardHTML()}

    <!-- PLANNER + FOCUS ZONE + SCORE HISTORY -->

    ${state.attempts.length > 0 ? buildFocusZoneHTML() : ''}

    ${buildStudyPlannerHTML()}

    ${state.testSessions.length >= 2 ? buildScoreHistoryHTML() : ''}

    <!-- ── FEATURED EXAM SERIES HUB ── -->

    <div class="section-header" style="margin-top:28px">

      <div class="section-title">Curated GATE Exam Series <span>Flagship Compendiums (210 Full Mocks • 21 PYQ Exams)</span></div>

      <button class="btn btn-secondary btn-sm" onclick="navigate('mocks')">View All Mocks →</button>

    </div>

    <div class="dashboard-series-grid">
      <div class="series-card" style="--series-color:#22c55e" onclick="navigate('mocks',{tab:'easy'})">
        <div>
          <div class="series-badge" style="background:rgba(34,197,94,0.15);color:#22c55e">🌟 FOUNDATIONAL EASY</div>
          <div class="series-title">65 Easy Mock Tests</div>
          <div class="series-sub">Direct formulas, canonical definitions, and core scoring fundamentals strictly aligned with the IISc/IIT syllabus (Includes 30 Set 1, 30 Set 2, and 5 Foundational Tests).</div>
        </div>
        <div class="series-footer">
          <span>4,225 Qs • 65 Full Tests • 3.5/10</span>
          <span class="series-footer-action">Explore →</span>
        </div>
      </div>
      <div class="series-card" style="--series-color:#eab308" onclick="navigate('mocks',{tab:'medium'})">
        <div>
          <div class="series-badge" style="background:rgba(234,179,8,0.15);color:#eab308">⚡ STANDARD GATE CS</div>
          <div class="series-title">83 Medium Mock Tests</div>
          <div class="series-sub">Standard GATE difficulty with multi-step NAT numericals, cache/pipeline timing, logic, and comprehensive algorithms across 83 calibrated exams.</div>
        </div>
        <div class="series-footer">
          <span>5,395 Qs • 83 Full Tests • 5.0/10</span>
          <span class="series-footer-action">Explore →</span>
        </div>
      </div>
      <div class="series-card" style="--series-color:#ef4444" onclick="navigate('mocks',{tab:'hard',subSeries:'hard-curated'})">
        <div>
          <div class="series-badge" style="background:rgba(239,68,68,0.15);color:#ef4444">🔴 RANK BOOSTERS</div>
          <div class="series-title">32 Hard Mock Tests</div>
          <div class="series-sub">Curated Rank Booster Series: 32 advanced mock exams (Mocks 1–4, 10–14, 25, 29–32, 38–41, 59–68, 71, 73, 83 + Advanced Papers) testing deep conceptual mastery and multi-step derivations.</div>
        </div>
        <div class="series-footer">
          <span>2,080 Qs • 32 Full Tests • 7.5/10</span>
          <span class="series-footer-action">Explore →</span>
        </div>
      </div>
      <div class="series-card" style="--series-color:#f43f5e" onclick="navigate('mocks',{tab:'hard',subSeries:'hard-30'})">
        <div>
          <div class="series-badge" style="background:rgba(244,63,94,0.15);color:#f43f5e">🔥 EXTREME HARD SERIES</div>
          <div class="series-title">30 Extreme Hard Mock Tests</div>
          <div class="series-sub">Capstone extreme-difficulty examinations (GO-Classes caliber, mock-hard-01 to 30) testing multi-concept proofs, subtle edge cases, and high-pressure rigor.</div>
        </div>
        <div class="series-footer">
          <span>1,950 Qs • 30 Full Tests • 8.5/10</span>
          <span class="series-footer-action">Explore →</span>
        </div>
      </div>
      <div class="series-card" style="--series-color:#a855f7" onclick="navigate('mocks',{tab:'hard',subSeries:'flm-20'})">
        <div>
          <div class="series-badge" style="background:rgba(168,85,247,0.15);color:#c084fc">🏆 FULL MOCKS COMPENDIUM</div>
          <div class="series-title">20 Full Mocks Compendium</div>
          <div class="series-sub">Deep conceptual mastery, edge-case analysis, advanced mathematics, and challenging gate-level problem solving.</div>
        </div>
        <div class="series-footer">
          <span>1,300 Qs • 20 Full Tests • 7.0/10</span>
          <span class="series-footer-action">Explore →</span>
        </div>
      </div>
      <div class="series-card" style="--series-color:#06b6d4" onclick="navigate('mocks',{tab:'go'})">
        <div>
          <div class="series-badge" style="background:rgba(6,182,212,0.15);color:#06b6d4">🌐 ALL-INDIA MOCKS</div>
          <div class="series-title">27 All-India Mocks</div>
          <div class="series-sub">Rigorous full-length All-India Mock Tests (2025–2026) crafted for peak exam calibration.</div>
        </div>
        <div class="series-footer">
          <span>1,568 Qs • 27 Full Tests • 7.2/10</span>
          <span class="series-footer-action">Explore →</span>
        </div>
      </div>
      <div class="series-card" style="--series-color:#8b5cf6" onclick="navigate('mocks',{tab:'comprehensive-mocks'})">
        <div>
          <div class="series-badge" style="background:rgba(139,92,246,0.15);color:#a78bfa">📘 ELITE COACHING</div>
          <div class="series-title">21 Comprehensive Full Mocks</div>
          <div class="series-sub">High-resolution visual question cards, Advance & Basic Level Full Syllabus Tests, and National Mock Exams (2023–2024).</div>
        </div>
        <div class="series-footer">
          <span>1,409 Qs • 21 Full Tests • 7.5/10</span>
          <span class="series-footer-action">Explore →</span>
        </div>
      </div>
      <div class="series-card" style="--series-color:#38bdf8" onclick="navigate('pyq-exams')">
        <div>
          <div class="series-badge" style="background:rgba(56,189,248,0.15);color:#38bdf8">🏛️ OFFICIAL PAPERS</div>
          <div class="series-title">21 Full-Length PYQ Exams</div>
          <div class="series-sub">Complete authentic year-wise examination papers from 2007 to 2025 in a realistic 180-minute timed environment.</div>
        </div>
        <div class="series-footer">
          <span>2,224+ PYQs • 2007–2025 • Official</span>
          <span class="series-footer-action">Practice →</span>
        </div>
      </div>
    </div>

    <!-- ── SUBJECT TESTS SECTION (BELOW MOCKS SECTION) ── -->
    <div class="section-header" style="margin-top:28px">
      <div class="section-title">Subject-Wise Practice Tests <span>26 Sectional Exams • All 13 Core GATE CS Subjects</span></div>
      <button class="btn btn-secondary btn-sm" onclick="navigate('subject-tests')">View All 26 Tests →</button>
    </div>
    <div class="dashboard-series-grid">
      <div class="series-card" style="--series-color:#3b82f6" onclick="navigate('subject-tests',{subject:'Operating Systems'})">
        <div>
          <div class="series-badge" style="background:rgba(59,130,246,0.15);color:#3b82f6">💻 SYSTEMS CORE</div>
          <div class="series-title">Operating Systems Tests</div>
          <div class="series-sub">Processes, CPU scheduling, virtual memory, synchronization semaphores, and deadlock prevention.</div>
        </div>
        <div class="series-footer">
          <span>60 Qs • 2 Full Tests • 6.8/10</span>
          <span class="series-footer-action">Practice →</span>
        </div>
      </div>
      <div class="series-card" style="--series-color:#a855f7" onclick="navigate('subject-tests',{subject:'Algorithms'})">
        <div>
          <div class="series-badge" style="background:rgba(168,85,247,0.15);color:#c084fc">⚡ ALGORITHMIC RIGOR</div>
          <div class="series-title">Algorithms &amp; Complexity</div>
          <div class="series-sub">Asymptotics, dynamic programming, divide &amp; conquer, Bellman-Ford, Kruskal/Prim, and NP-completeness.</div>
        </div>
        <div class="series-footer">
          <span>60 Qs • 2 Full Tests • 7.5/10</span>
          <span class="series-footer-action">Practice →</span>
        </div>
      </div>
      <div class="series-card" style="--series-color:#10b981" onclick="navigate('subject-tests',{subject:'Computer Networks'})">
        <div>
          <div class="series-badge" style="background:rgba(16,185,129,0.15);color:#10b981">🌐 PROTOCOL MASTERY</div>
          <div class="series-title">Computer Networks Tests</div>
          <div class="series-sub">CIDR subnets, TCP sliding window &amp; congestion control, DNS, routing protocols, and CRC.</div>
        </div>
        <div class="series-footer">
          <span>60 Qs • 2 Full Tests • 7.0/10</span>
          <span class="series-footer-action">Practice →</span>
        </div>
      </div>
      <div class="series-card" style="--series-color:#eab308" onclick="navigate('subject-tests',{subject:'DBMS'})">
        <div>
          <div class="series-badge" style="background:rgba(234,179,8,0.15);color:#eab308">🗄️ DATABASE SYSTEMS</div>
          <div class="series-title">Databases (DBMS) Tests</div>
          <div class="series-sub">SQL, relational algebra, B+ trees, 2PL serializability, and normal forms (1NF–BCNF).</div>
        </div>
        <div class="series-footer">
          <span>50 Qs • 2 Full Tests • 6.8/10</span>
          <span class="series-footer-action">Practice →</span>
        </div>
      </div>
      <div class="series-card" style="--series-color:#ec4899" onclick="navigate('subject-tests',{subject:'Theory of Computation'})">
        <div>
          <div class="series-badge" style="background:rgba(236,72,153,0.15);color:#ec4899">⚙️ AUTOMATA &amp; LOGIC</div>
          <div class="series-title">Theory of Computation</div>
          <div class="series-sub">DFAs, regular expressions, context-free languages, pushdown automata, and Turing decidability.</div>
        </div>
        <div class="series-footer">
          <span>50 Qs • 2 Full Tests • 8.0/10</span>
          <span class="series-footer-action">Practice →</span>
        </div>
      </div>
      <div class="series-card" style="--series-color:#06b6d4" onclick="navigate('subject-tests',{subject:'Computer Organization'})">
        <div>
          <div class="series-badge" style="background:rgba(6,182,212,0.15);color:#06b6d4">📐 ARCHITECTURE &amp; CPU</div>
          <div class="series-title">Computer Organization</div>
          <div class="series-sub">Instruction pipelining, cache memory hit/miss timing, addressing modes, and IEEE 754 floats.</div>
        </div>
        <div class="series-footer">
          <span>50 Qs • 2 Full Tests • 7.8/10</span>
          <span class="series-footer-action">Practice →</span>
        </div>
      </div>
    </div>

    <!-- ── 1983-2026 EMPIRICAL INTELLIGENCE & PATTERNS HUB ── -->
    <div class="section-header" style="margin-top:28px">
      <div class="section-title">Archival Intelligence &amp; Recurring Patterns (1983–2026) <span>338 Patterns • 44 Years</span></div>
      <button class="btn btn-secondary btn-sm" onclick="navigate('patterns')">Explore Patterns Hub →</button>
    </div>
    <div class="pattern-resources-grid">
      <div class="pattern-resource-card" style="--card-accent:#f59e0b" onclick="navigate('patterns')">
        <div>
          <div class="series-badge" style="background:rgba(245,158,11,0.15);color:#f59e0b">🔁 REPEATING PATTERNS DETECTOR</div>
          <div class="series-title" style="margin-top:6px;font-size:16px;font-weight:700">338 Recurring Patterns &amp; 4,910 Solved PYQs</div>
          <div class="series-sub" style="font-size:12px;color:var(--text-secondary);margin-top:6px;line-height:1.5">Empirically audited question patterns appearing in ≥ 4 distinct GATE examination years (1983–2026). Includes 466-page Solved Compendium PDF.</div>
        </div>
        <div class="series-footer" style="margin-top:16px;display:flex;justify-content:space-between;align-items:center;font-size:12px;color:var(--text-muted)">
          <span>466 Pages PDF • 338 Patterns • Top 10 Ranked</span>
          <span class="series-footer-action" style="color:var(--accent);font-weight:700">Explore Hub →</span>
        </div>
      </div>
      <div class="pattern-resource-card" style="--card-accent:#6c63ff" onclick="navigate('patterns',{tab:'archival'})">
        <div>
          <div class="series-badge" style="background:rgba(108,99,255,0.15);color:#6c63ff">📜 ARCHIVAL QUESTION BANK</div>
          <div class="series-title" style="margin-top:6px;font-size:16px;font-weight:700">GATE CSE 44-Year Question Bank (1983–2026)</div>
          <div class="series-sub" style="font-size:12px;color:var(--text-secondary);margin-top:6px;line-height:1.5">Consolidated historical &amp; modern reference edition across 7 execution batches. Includes official answer keys, derivations, and disputed/MTA audit report.</div>
        </div>
        <div class="series-footer" style="margin-top:16px;display:flex;justify-content:space-between;align-items:center;font-size:12px;color:var(--text-muted)">
          <span>562 Pages PDF • 55 Exam Papers • Batches 1–7</span>
          <span class="series-footer-action" style="color:var(--accent);font-weight:700">View Archive →</span>
        </div>
      </div>
    </div>

    <!-- ── QUESTION BANK DISTRIBUTION ── -->

    <div class="qbank-dist-box">

      <div class="qbank-dist-header">

        <div>

          <div style="font-size:14px;font-weight:700;color:var(--text-primary)">📚 Master Question Bank Telemetry</div>

          <div style="font-size:12px;color:var(--text-muted)">${state.questions.length.toLocaleString()} verified GATE CS questions with detailed mathematical derivations</div>

        </div>

        <button class="btn btn-secondary btn-sm" onclick="navigate('practice')">Browse All ${state.questions.length.toLocaleString()} Questions →</button>

      </div>

      <div class="qbank-dist-bar">

        <div class="qbank-dist-segment" style="width:52%;background:#eab308" title="Medium Difficulty: 4,252 Questions (52%)" onclick="navigate('practice',{difficulty:'medium'})"></div>

        <div class="qbank-dist-segment" style="width:41%;background:#22c55e" title="Easy Difficulty: 3,358 Questions (41%)" onclick="navigate('practice',{difficulty:'easy'})"></div>

        <div class="qbank-dist-segment" style="width:7%;background:#ef4444" title="Hard Difficulty: 558 Questions (7%)" onclick="navigate('practice',{difficulty:'hard'})"></div>

      </div>

      <div class="qbank-dist-legend">

        <div class="qbank-dist-legend-item" onclick="navigate('practice',{difficulty:'medium'})"><span class="qbank-dist-dot" style="background:#eab308"></span> Medium (4,252 Qs • 52%)</div>

        <div class="qbank-dist-legend-item" onclick="navigate('practice',{difficulty:'easy'})"><span class="qbank-dist-dot" style="background:#22c55e"></span> Easy (3,358 Qs • 41%)</div>

        <div class="qbank-dist-legend-item" onclick="navigate('practice',{difficulty:'hard'})"><span class="qbank-dist-dot" style="background:#ef4444"></span> Hard (558 Qs • 7%)</div>

        <div class="qbank-dist-legend-item" onclick="navigate('practice',{type:'nat'})"><span class="qbank-dist-dot" style="background:#06b6d4"></span> 3,726 NATs</div>

        <div class="qbank-dist-legend-item" onclick="navigate('practice',{type:'mcq'})"><span class="qbank-dist-dot" style="background:#8b5cf6"></span> 3,379 MCQs</div>

        <div class="qbank-dist-legend-item" onclick="navigate('practice',{type:'msq'})"><span class="qbank-dist-dot" style="background:#ec4899"></span> 1,063 MSQs</div>

      </div>

    </div>



    <div class="section-header">

      <div class="section-title">Subjects <span>${SUBJECTS.length} available</span></div>

      <button class="btn btn-secondary btn-sm" onclick="navigate('subjects')">View All →</button>

    </div>

    <div class="subjects-grid">${buildSubjectCards()}</div>`;

}



function buildSubjectCards() {

  return SUBJECTS.map(sub=>{

    const s=getSubjectStats(sub.name);

    return `

      <div class="subject-card" style="--subject-color:${sub.color}" onclick="navigate('practice',{subject:'${sub.name}'})">

        <span class="subject-icon">${sub.icon}</span>

        <div class="subject-name">${sub.name}</div>

        <div class="subject-desc">${sub.desc}</div>

        <div class="subject-footer">

          <span class="subject-count">${s.total} Q${s.doneCount>0?` • ${s.accuracy}% acc`:''}</span>

          ${s.total>0

            ? `<span class="subject-action">Practice →</span>`

            : `<span class="subject-action coming-soon"><span class="coming-soon-badge">+ Add</span></span>`}

        </div>

      </div>`;

  }).join('');

}



// ─── SUBJECTS ────────────────────────────────────────────────────────────────

function toggleSyllabusGuide() {
  const body = document.getElementById('syllabus-guide-body');
  const icon = document.getElementById('syllabus-toggle-icon');
  const strip = document.getElementById('syllabus-blueprint-strip');
  if (body) {
    const isHidden = body.style.display === 'none';
    body.style.display = isHidden ? 'grid' : 'none';
    if (strip) strip.style.display = isHidden ? 'flex' : 'none';
    if (icon) icon.textContent = isHidden ? '▲ Hide Guide' : '▼ View Full Syllabus';
  }
}

function filterSyllabusCategory(category, btn) {
  const cards = document.querySelectorAll('.syllabus-sec-card');
  const btns = document.querySelectorAll('.syllabus-filter-pill');
  const searchInput = document.querySelector('.syllabus-search-input');
  if (searchInput) searchInput.value = '';
  btns.forEach(b => b.classList.remove('active'));
  if (btn) btn.classList.add('active');

  cards.forEach(card => {
    card.classList.remove('syllabus-card-highlight');
    const cat = card.dataset.category || '';
    const weight = parseInt(card.dataset.weight || '0', 10);
    let show = true;
    if (category === 'core') show = (cat === 'core-cs');
    else if (category === 'high') show = (weight >= 10);
    else if (category === 'math-ga') show = (cat === 'math' || cat === 'ga');
    card.style.display = show ? '' : 'none';
  });
}

function filterSyllabusSearch(query) {
  const q = (query || '').trim().toLowerCase();
  const cards = document.querySelectorAll('.syllabus-sec-card');
  cards.forEach(card => {
    if (!q) {
      card.style.display = '';
      card.classList.remove('syllabus-card-highlight');
      return;
    }
    const text = card.textContent.toLowerCase();
    const match = text.includes(q);
    card.style.display = match ? '' : 'none';
    if (match) card.classList.add('syllabus-card-highlight');
    else card.classList.remove('syllabus-card-highlight');
  });
}

function jumpToSubjectPYQs(subName) {
  state.selectedTopicPyqSubject = subName;
  state.topicPyqTab = 'chapters';
  state.topicPyqExpandedTopic = null;
  navigate('topic-pyqs');
}

function buildOfficialSyllabusGuideHTML() {
  const sections = [
    {
      num: 'Section 1',
      badge: 'SEC 01',
      title: 'Engineering Mathematics',
      subject: 'Engineering Mathematics',
      subtitle: 'Discrete Math, Linear Algebra, Calculus & Probability',
      category: 'math',
      icon: '📐',
      color: '#8b5cf6',
      weightage: '~15% Weightage',
      weightNum: 15,
      tags: ['Discrete Math', 'Linear Algebra', 'Calculus', 'Probability & Stats'],
      topics: [
        { label: 'Discrete Mathematics', text: 'Propositional & 1st-order logic, sets, relations, partial orders, lattices, monoids, groups, graphs, combinatorics, recurrences.' },
        { label: 'Linear Algebra', text: 'Matrices, determinants, systems of linear equations, eigenvalues, eigenvectors & LU decomposition.' },
        { label: 'Calculus & Probability', text: 'Limits, continuity, maxima/minima, mean value theorem, random variables, Bayes theorem & distributions.' }
      ]
    },
    {
      num: 'Section 2',
      badge: 'SEC 02',
      title: 'Digital Logic',
      subject: 'Digital Logic',
      subtitle: 'Boolean Algebra, Combinational & Sequential Circuits',
      category: 'core-cs',
      icon: '🔌',
      color: '#06b6d4',
      weightage: '~5-6% Weightage',
      weightNum: 6,
      tags: ['Boolean Algebra', 'K-Maps', 'Combinational', 'Sequential Circuits', 'Number Systems'],
      topics: [
        { label: 'Boolean Logic & Minimization', text: 'Boolean algebra, canonical forms, logic gates, K-maps (up to 5 variables), Quine-McCluskey tabular method.' },
        { label: 'Combinational Circuits', text: 'Multiplexers, decoders, encoders, ripple-carry & carry-lookahead adders, magnitude comparators.' },
        { label: 'Sequential Circuits', text: 'Latches, flip-flops (SR, JK, D, T), registers, counters, state machines, fixed & floating point arithmetic.' }
      ]
    },
    {
      num: 'Section 3',
      badge: 'SEC 03',
      title: 'Computer Organization & Architecture',
      subject: 'Computer Organization',
      subtitle: 'ALU, Pipelining, Cache & Memory Hierarchy',
      category: 'core-cs',
      icon: '🖩',
      color: '#84cc16',
      weightage: '~8-10% Weightage',
      weightNum: 9,
      tags: ['Addressing Modes', 'ALU & Control Unit', 'Pipelining Hazards', 'Memory Hierarchy', 'DMA & I/O'],
      topics: [
        { label: 'CPU & Instruction Architecture', text: 'Addressing modes, instruction formats (RISC/CISC), ALU, data-path, hardwired vs microprogrammed control.' },
        { label: 'Pipelining & Hazards', text: 'Pipeline stages, throughput, structural/data/control hazards, branch prediction & operand forwarding.' },
        { label: 'Memory Systems & I/O', text: 'Cache mapping (direct/set-associative), miss penalties, virtual memory, TLB, DMA & interrupt handling.' }
      ]
    },
    {
      num: 'Section 4',
      badge: 'SEC 04',
      title: 'Programming & Data Structures',
      subject: 'Data Structures',
      subtitle: 'C Language, Stacks, Queues, Trees & Heaps',
      category: 'core-cs',
      icon: '🗂️',
      color: '#6366f1',
      weightage: '~10-12% Weightage',
      weightNum: 11,
      tags: ['C Programming', 'Recursion & Pointers', 'Stacks & Queues', 'Trees & BST', 'Graphs & Heaps'],
      topics: [
        { label: 'C Programming & Pointers', text: 'Pointers, pointer arithmetic, structs, parameter passing, recursion & runtime activation records.' },
        { label: 'Linear Data Structures', text: 'Arrays, singly/doubly linked lists, stacks (expressions & evaluation), queues (circular & priority).' },
        { label: 'Non-Linear Data Structures', text: 'Binary trees, BST properties & traversals, AVL trees, binary heaps (min/max heapify) & graph representations.' }
      ]
    },
    {
      num: 'Section 5',
      badge: 'SEC 05',
      title: 'Algorithms',
      subject: 'Algorithms',
      subtitle: 'Complexity, Greedy, Dynamic Programming & Graphs',
      category: 'core-cs',
      icon: '⚙️',
      color: '#f97316',
      weightage: '~8-10% Weightage',
      weightNum: 9,
      tags: ['Asymptotic Complexity', 'Sorting & Hashing', 'Greedy & DP', 'Graph Traversals', 'Shortest Paths & MST'],
      topics: [
        { label: 'Asymptotic Analysis & Sorting', text: 'Big-O, Ω, Θ notation, recurrence solving (Master theorem), divide-and-conquer, sorting bounds & hash tables.' },
        { label: 'Greedy & Dynamic Programming', text: 'Optimal substructure, greedy choice (Huffman, fractional knapsack), DP (0/1 knapsack, LCS, matrix chain).' },
        { label: 'Graph Algorithms', text: 'BFS/DFS, topological sort, MST (Prim, Kruskal), single-source & all-pairs shortest paths (Dijkstra, Bellman-Ford).' }
      ]
    },
    {
      num: 'Section 6',
      badge: 'SEC 06',
      title: 'Theory of Computation',
      subject: 'Theory of Computation',
      subtitle: 'Finite Automata, Grammars, PDA & Turing Machines',
      category: 'core-cs',
      icon: '🔣',
      color: '#a855f7',
      weightage: '~8-9% Weightage',
      weightNum: 8,
      tags: ['Regular Expressions', 'Finite Automata', 'CFG & PDA', 'Pumping Lemma', 'Turing Machines'],
      topics: [
        { label: 'Regular Languages & Automata', text: 'DFA, NFA, regex, state minimization, closure properties & pumping lemma for regular languages.' },
        { label: 'Context-Free Languages & PDA', text: 'Context-free grammars (CFG), parse trees, ambiguity removal, pushdown automata (PDA) & CFL closures.' },
        { label: 'Turing Machines & Decidability', text: 'Turing machines, recursively enumerable languages, undecidability, halting problem & reductions.' }
      ]
    },
    {
      num: 'Section 7',
      badge: 'SEC 07',
      title: 'Compiler Design',
      subject: 'Compiler Design',
      subtitle: 'Lexical Analysis, Parsing, SDT & Optimization',
      category: 'core-cs',
      icon: '🔧',
      color: '#f59e0b',
      weightage: '~4-5% Weightage',
      weightNum: 5,
      tags: ['Lexical Analysis', 'LL / LR Parsing', 'Syntax-Directed (SDT)', 'Intermediate Code', 'Optimization'],
      topics: [
        { label: 'Lexical Analysis & Parsing', text: 'Tokenization, regular definitions, LL(1) parsers (FIRST/FOLLOW), LR(0), SLR, LALR, CLR shift-reduce parsing.' },
        { label: 'Syntax-Directed Translation', text: 'Synthesized vs inherited attributes, S-attributed and L-attributed SDDs, parse tree evaluations.' },
        { label: 'Intermediate Code & Optimization', text: '3-address code, quadruples/triples, control-flow graphs, basic blocks, loop optimization & data-flow.' }
      ]
    },
    {
      num: 'Section 8',
      badge: 'SEC 08',
      title: 'Operating Systems',
      subject: 'Operating Systems',
      subtitle: 'Processes, Concurrency, Virtual Memory & File Systems',
      category: 'core-cs',
      icon: '🖥️',
      color: '#22c55e',
      weightage: '~8-10% Weightage',
      weightNum: 9,
      tags: ['Processes & Threads', 'CPU Scheduling', 'Deadlocks & Semaphores', 'Virtual Memory', 'File Systems'],
      topics: [
        { label: 'Processes & CPU Scheduling', text: 'Threads, kernel vs user space, system calls, preemptive CPU scheduling algorithms (FCFS, SJF, RR, Priority).' },
        { label: 'Concurrency & Deadlocks', text: 'Critical sections, Peterson’s solution, semaphores, mutex, deadlock prevention, detection & Banker’s algorithm.' },
        { label: 'Memory & Storage Systems', text: 'Multi-level paging, TLB, page replacement (FIFO, LRU, Optimal), disk scheduling & file allocation.' }
      ]
    },
    {
      num: 'Section 9',
      badge: 'SEC 09',
      title: 'Databases (DBMS)',
      subject: 'DBMS',
      subtitle: 'Relational Algebra, SQL, Normalization & Indexing',
      category: 'core-cs',
      icon: '🗄️',
      color: '#ef4444',
      weightage: '~7-8% Weightage',
      weightNum: 8,
      tags: ['ER-Model', 'Relational Algebra', 'SQL Queries', 'BCNF / 3NF Normalization', 'B & B+ Trees', 'ACID'],
      topics: [
        { label: 'ER-Models & Relational Theory', text: 'Entity-relationship diagrams, mapping to tables, relational algebra operators (joins, selections), tuple calculus.' },
        { label: 'SQL & Schema Normalization', text: 'Advanced SQL queries (GROUP BY, HAVING, subqueries), functional dependencies, canonical covers, 1NF to BCNF.' },
        { label: 'Storage, Indexing & Transactions', text: 'B-trees & B+ trees search/insertion, ACID properties, serializability, conflict/view equivalence & 2PL.' }
      ]
    },
    {
      num: 'Section 10',
      badge: 'SEC 10',
      title: 'Computer Networks',
      subject: 'Computer Networks',
      subtitle: 'OSI/TCP-IP, Routing, Sockets, TCP & DNS',
      category: 'core-cs',
      icon: '🌐',
      color: '#14b8a6',
      weightage: '~8-10% Weightage',
      weightNum: 9,
      tags: ['OSI & TCP/IP', 'Ethernet & Framing', 'IPv4, CIDR & NAT', 'Routing Protocols', 'Flow & Congestion', 'DNS / HTTP'],
      topics: [
        { label: 'Physical & Data Link Layers', text: 'Packet vs circuit switching, framing, Hamming codes, CRC error detection, CSMA/CD, sliding window (GBN, SR).' },
        { label: 'Network Layer & Routing', text: 'IPv4 addressing, CIDR subnetting, NAT, ARP, ICMP, distance-vector (Bellman-Ford) & link-state (OSPF).' },
        { label: 'Transport & Application Layers', text: 'TCP 3-way handshake, congestion control (slow start, AIMD), UDP sockets, DNS resolution & HTTP/HTTPS.' }
      ]
    },
    {
      num: 'General Aptitude',
      badge: 'MANDATORY GA',
      title: 'General Aptitude (GA)',
      subject: 'Aptitude',
      subtitle: 'Verbal Ability, Quantitative Aptitude & Spatial Deduction',
      category: 'ga',
      icon: '🧮',
      color: '#38bdf8',
      weightage: '15 Marks (Fixed)',
      weightNum: 15,
      isFeatured: true,
      tags: ['Verbal & Grammar', 'Reading Comprehension', 'Quantitative Aptitude', 'Logical Deduction', 'Spatial & Patterns'],
      topics: [
        { label: 'Verbal Ability', text: 'English grammar, sentence completion, vocabulary in context, reading comprehension & narrative analysis.' },
        { label: 'Quantitative Aptitude', text: 'Numerical computation, percentages, ratios, powers & exponents, permutations/combinations & elementary stats.' },
        { label: 'Analytical & Spatial Reasoning', text: 'Deductive logic, analogies, numerical induction, 2D/3D shape transformations (translation, rotation, folding).' }
      ]
    }
  ];

  return `
    <div class="syllabus-guide-card">
      <div class="syllabus-guide-topbar">
        <div class="syllabus-guide-header" onclick="toggleSyllabusGuide()">
          <div class="syllabus-guide-title">
            <div class="syllabus-guide-icon">🏛️</div>
            <div>
              <div class="syllabus-guide-title-text">Official GATE CSE Syllabus Guide</div>
              <div style="display:flex;align-items:center;gap:8px;margin-top:3px;flex-wrap:wrap">
                <span class="syllabus-guide-badge">IIT Madras Calibrated</span>
                <span style="font-size:11px;color:var(--text-muted)">10 Core Sections + General Aptitude &bull; 100 Marks Blueprint</span>
              </div>
            </div>
          </div>
          <div style="display:flex;align-items:center;gap:10px">
            <button class="syllabus-guide-toggle-btn" id="syllabus-toggle-icon" type="button" onclick="event.stopPropagation(); toggleSyllabusGuide();">
              ▲ Hide Guide
            </button>
          </div>
        </div>

        <div class="syllabus-blueprint-strip" id="syllabus-blueprint-strip">
          <div class="syllabus-blueprint-bar" title="GATE CS Official Marks Distribution (100 Marks Total)">
            <div class="blueprint-seg blueprint-seg-math" style="width:15%" title="Engineering Mathematics: 15 Marks (15%)">
              <span class="blueprint-seg-label">📐 Math 15M (15%)</span>
            </div>
            <div class="blueprint-seg blueprint-seg-cs" style="width:70%" title="Core Computer Science (9 Sections): 70 Marks (70%)">
              <span class="blueprint-seg-label">💻 Core CS 70M (70%)</span>
            </div>
            <div class="blueprint-seg blueprint-seg-ga" style="width:15%" title="General Aptitude: 15 Marks (15%)">
              <span class="blueprint-seg-label">🧮 GA 15M (15%)</span>
            </div>
          </div>
          <div class="syllabus-controls-row">
            <div class="syllabus-filter-group">
              <button class="syllabus-filter-pill active" onclick="event.stopPropagation(); filterSyllabusCategory('all', this)" type="button">All Sections (11)</button>
              <button class="syllabus-filter-pill" onclick="event.stopPropagation(); filterSyllabusCategory('core', this)" type="button">Core CS (9)</button>
              <button class="syllabus-filter-pill" onclick="event.stopPropagation(); filterSyllabusCategory('high', this)" type="button">High Weightage (≥10%)</button>
              <button class="syllabus-filter-pill" onclick="event.stopPropagation(); filterSyllabusCategory('math-ga', this)" type="button">Math &amp; GA</button>
            </div>
            <div class="syllabus-search-wrap" onclick="event.stopPropagation()">
              <svg class="syllabus-search-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
              <input type="text" class="syllabus-search-input" placeholder="Search syllabus topics (e.g. Pipelining, K-Maps, SQL)..." oninput="filterSyllabusSearch(this.value)">
            </div>
          </div>
        </div>
      </div>

      <div class="syllabus-sections-grid" id="syllabus-guide-body">
        ${sections.map(s => {
          const stats = getSubjectStats(s.subject);
          return `
          <div class="syllabus-sec-card ${s.isFeatured ? 'syllabus-sec-card-featured' : ''}" style="--sec-color:${s.color};" data-category="${s.category}" data-weight="${s.weightNum}">
            <div class="syllabus-card-inner">
              <div class="syllabus-card-topbar">
                <div class="syllabus-badges-left">
                  <span class="syllabus-badge-num" style="background:${s.color}18;color:${s.color};border:1px solid ${s.color}35">${escapeHtml(s.badge)}</span>
                  <span class="syllabus-badge-weight" title="Marks Weightage">
                    <span class="syllabus-weight-dot" style="background:${s.color}"></span>
                    ${escapeHtml(s.weightage)}
                  </span>
                </div>
                ${stats.total > 0 ? `<span class="syllabus-qcount">📚 ${stats.total.toLocaleString()} Qs</span>` : ''}
              </div>
              <div class="syllabus-card-header">
                <div class="syllabus-card-icon-wrap" style="background:${s.color}15;border-color:${s.color}35;color:${s.color}">
                  <span class="syllabus-card-icon">${s.icon}</span>
                </div>
                <div class="syllabus-card-title-wrap">
                  <h3 class="syllabus-card-title" title="${escapeHtml(s.title)}">${escapeHtml(s.title)}</h3>
                  <span class="syllabus-card-canonical" title="${escapeHtml(s.subtitle)}">${escapeHtml(s.subtitle)}</span>
                </div>
              </div>
              <div class="syllabus-card-tags">
                ${s.tags.slice(0, 4).map(t => `<span class="syllabus-tag-chip">${escapeHtml(t)}</span>`).join('')}
              </div>
              <div class="syllabus-card-topics">
                ${s.topics.map(t => `
                  <div class="syllabus-topic-block">
                    <div class="syllabus-topic-heading">
                      <span class="syllabus-topic-dot" style="background:${s.color}"></span>
                      <span>${escapeHtml(t.label)}</span>
                    </div>
                    <p class="syllabus-topic-body">${escapeHtml(t.text)}</p>
                  </div>
                `).join('')}
              </div>
            </div>
            <div class="syllabus-card-actions">
              <button class="syllabus-action-btn syllabus-action-practice" onclick="navigate('practice', { subject: '${escapeHtml(s.subject)}' })" type="button" title="Practice ${escapeHtml(s.title)}">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>
                <span>Practice</span>
              </button>
              <button class="syllabus-action-btn syllabus-action-pyqs" onclick="jumpToSubjectPYQs('${escapeHtml(s.subject)}')" type="button" title="Chapter-Wise PYQs">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>
                <span>PYQ Chapters</span>
              </button>
            </div>
          </div>
        `}).join('')}
      </div>
    </div>
  `;
}

function renderSubjects(c) {

  c.innerHTML=`

    ${buildOfficialSyllabusGuideHTML()}

    <div class="section-header"><div class="section-title">All Subjects <span>${SUBJECTS.length} available</span></div></div>

    <div class="subjects-grid">${buildSubjectCards()}</div>`;

}



// ─── HELPERS ─────────────────────────────────────────────────────────────────



// ── QUESTION CONTENT FORMATTER (Code Fences, Math Blocks & Formatting) ──

function formatQuestionContent(text) {

  if (!text) return '';



  const blocks = [];

  function saveBlock(html) {

    const placeholder = `@@@QB_BLOCK_${blocks.length}@@@`;

    blocks.push(html);

    return placeholder;

  }



  let str = String(text);



  // 1. Process fenced code blocks: ```lang ... ```

  str = str.replace(/```([a-zA-Z0-9_#+-]*)\n?([\s\S]*?)```/g, (match, lang, code) => {

    let language = (lang || '').trim().toLowerCase();

    const VALID_LANGS = new Set(['c', 'cpp', 'c++', 'python', 'py', 'sql', 'java', 'asm', 'assembly', 'pseudocode', 'text', 'sh', 'bash', 'javascript', 'js']);

    let cleanCode = code;

    if (!VALID_LANGS.has(language)) {

      cleanCode = (lang ? lang + '\n' : '') + code;

      language = 'c';

    }

    cleanCode = cleanCode.replace(/^\n+|\n+$/g, '');

    const escaped = escapeHtml(cleanCode);

    const codeId = 'code_' + Math.random().toString(36).substring(2, 9);

    const html = `<div class="code-block-container">

      <div class="code-block-header">

        <span class="code-block-lang">💻 ${escapeHtml(language.toUpperCase())}</span>

        <button class="code-copy-btn" onclick="copyCodeSnippet('${codeId}', this)" type="button">📋 Copy</button>

      </div>

      <pre class="code-block"><code id="${codeId}" class="language-${escapeHtml(language)}">${escaped}</code></pre>

    </div>`;

    return saveBlock(html);

  });



  // 2. Process inline backtick code `code`

  str = str.replace(/`([^`\n]+)`/g, (match, seg) => {

    return saveBlock(`<code class="inline-code">${escapeHtml(seg)}</code>`);

  });



  // 3. Protect display math $$ ... $$ and \[ ... \] (keeps LaTeX line breaks intact without <br/>)

  str = str.replace(/(\$\$[\s\S]*?\$\$|\\\[[\s\S]*?\\\])/g, (match) => {

    return saveBlock(match);

  });



    // 3.5. Defensively escape currency, assembly registers, and standalone terminal dollars
  str = str.replace(/(^|[\s(])\$(\d+(?:\.\d+)?)(?=[\s,.;:!?)]|$)/g, '$1\\$$2');
  str = str.replace(/(^|[\s(])\$([a-zA-Z0-9_]+)(?=[\s,.;:!?)]|$)/g, (m, p, reg) => {
    const MIPS_REGS = new Set(['s0','s1','s2','s3','s4','s5','s6','s7','t0','t1','t2','t3','t4','t5','t6','t7','t8','t9','a0','a1','a2','a3','v0','v1','k0','k1','gp','sp','fp','ra','zero','0','1','2','3','4','5']);
    return MIPS_REGS.has(reg.toLowerCase()) ? `${p}\\${reg}` : m;
  });
  str = str.replace(/(^|[\s({\[,])\$(?=[\s)}\.,;:!?]|$)/g, '$1\\$');

  // 4. Protect inline math $ ... $ and \( ... \)

  str = str.replace(/((?<!\\)\$[^\$\n]+(?<!\\)\$|\\\([\s\S]*?\\\))/g, (match) => {

    return saveBlock(match);

  });



  // 5. Protect safe pre-existing SVG diagrams and table elements

  str = str.replace(/(<figure[\s\S]*?<\/figure>|<svg[\s\S]*?<\/svg>|<table[\s\S]*?<\/table>)/gi, (match) => {

    return saveBlock(match);

  });



  // 6. Escape plain text to prevent Stored XSS and protect symbols

  str = escapeHtml(str);



  // 7. Convert line breaks outside code and math blocks

  str = str.replace(/\n{2,}/g, '<div class="q-para-spacer"></div>');

  str = str.replace(/\n/g, '<br/>');



  // 8. Restore all protected blocks cleanly

  for (let i = 0; i < blocks.length; i++) {

    str = str.replace(`@@@QB_BLOCK_${i}@@@`, blocks[i]);

  }



  return str;

}



window.copyCodeSnippet = function(id, btn) {

  const el = document.getElementById(id);

  if (!el) return;

  navigator.clipboard.writeText(el.textContent).then(() => {

    const orig = btn.innerHTML;

    btn.innerHTML = '✓ Copied!';

    btn.classList.add('copied');

    setTimeout(() => {

      btn.innerHTML = orig;

      btn.classList.remove('copied');

    }, 2000);

  }).catch(() => {

    showToast('Failed to copy to clipboard', 'error');

  });

};



function escapeHtml(str) {

  if (str === null || str === undefined) return '';

  return String(str)

    .replace(/&/g, '&amp;')

    .replace(/</g, '&lt;')

    .replace(/>/g, '&gt;')

    .replace(/"/g, '&quot;')

    .replace(/'/g, '&#039;');

}



function buildPaginationHTML({ currentPage, totalPages, totalCount, startIndex, endIndex, pageSize, onPageChangeFn, onPageSizeChangeFn, isTop = false }) {

  if (totalCount <= 0) return '';



  const pages = [];

  if (totalPages <= 7) {

    for (let i = 1; i <= totalPages; i++) pages.push(i);

  } else {

    pages.push(1);

    if (currentPage > 3) pages.push('...');

    const start = Math.max(2, currentPage - 1);

    const end = Math.min(totalPages - 1, currentPage + 1);

    for (let i = start; i <= end; i++) pages.push(i);

    if (currentPage < totalPages - 2) pages.push('...');

    pages.push(totalPages);

  }



  const isFirst = currentPage <= 1;

  const isLast = currentPage >= totalPages;



  return `

    <div class="pagination-container ${isTop ? 'top' : ''}">

      <div class="pagination-info">

        Showing <strong>${startIndex}–${endIndex}</strong> of <strong>${totalCount}</strong> questions

      </div>



      <div class="pagination-controls">

        <button class="pagination-btn" onclick="${onPageChangeFn}(1)" ${isFirst ? 'disabled' : ''} title="First Page">«</button>

        <button class="pagination-btn" onclick="${onPageChangeFn}(${currentPage - 1})" ${isFirst ? 'disabled' : ''} title="Previous Page">‹ Prev</button>



        <div class="pagination-numbers">

          ${pages.map(p => {

            if (p === '...') return `<span class="pagination-ellipsis">…</span>`;

            return `<button class="pagination-btn ${p === currentPage ? 'active' : ''}" onclick="${onPageChangeFn}(${p})">${p}</button>`;

          }).join('')}

        </div>



        <button class="pagination-btn" onclick="${onPageChangeFn}(${currentPage + 1})" ${isLast ? 'disabled' : ''} title="Next Page">Next ›</button>

        <button class="pagination-btn" onclick="${onPageChangeFn}(${totalPages})" ${isLast ? 'disabled' : ''} title="Last Page">»</button>

      </div>



      <div class="page-size-selector">

        <span>Per page:</span>

        <select class="page-size-select" onchange="${onPageSizeChangeFn}(this.value)">

          <option value="10" ${pageSize == 10 ? 'selected' : ''}>10</option>

          <option value="20" ${pageSize == 20 ? 'selected' : ''}>20</option>

          <option value="30" ${pageSize == 30 ? 'selected' : ''}>30</option>

          <option value="50" ${pageSize == 50 ? 'selected' : ''}>50</option>

          <option value="all" ${pageSize === 'all' ? 'selected' : ''}>All</option>

        </select>

      </div>

    </div>

  `;

}



// ─── PRACTICE ────────────────────────────────────────────────────────────────

function renderPractice(c, params={}) {

  // Restore last practice state when navigating back with no params

  if (Object.keys(params).length === 0 && state.lastPracticeState) {

    const lps = state.lastPracticeState;

    if (lps.filters) state.practiceFilters = { ...lps.filters };

    if (lps.page) state.practicePage = lps.page;

    if (lps.pageSize) state.practicePageSize = lps.pageSize;

    if (lps.search !== undefined) state.practiceSearch = lps.search;

    state.lastPracticeState = null; // consume once

  }

  if (params.category) {

    state.practiceFilters.category = params.category;

    state.practicePage = 1;

  }

  if (params.onlyPyq) {

    state.practiceFilters.category = 'pyq';

    state.practicePage = 1;

  }

  if (params.subject) {

    state.practiceFilters.subject = params.subject;

    state.practicePage = 1;

  }

  if (params.topic) {

    state.practiceFilters.topic = params.topic;

    state.practicePage = 1;

  }

  if (params.sort) {

    state.practiceSort = params.sort;

  }

  const f = state.practiceFilters;

  const isPyqActive = (f.category === 'pyq');

  const pyqTotalCount = state.questions.filter(q => isQuestionPyq(q)).length;

  // Base pool for category & subject calculation
  let baseCategoryQuestions = [...state.questions];

  if (f.category !== 'all') {

    if (f.category === 'pyq') {

      baseCategoryQuestions = baseCategoryQuestions.filter(q => isQuestionPyq(q));

    } else if (f.category === 'community') {

      baseCategoryQuestions = baseCategoryQuestions.filter(q => q.source === 'community' || q.category === 'community' || (q.uploadedBy && !STATIC_BUNDLED_IDS.has(q.id)));

    } else {

      baseCategoryQuestions = baseCategoryQuestions.filter(q => (q.category || 'subject') === f.category);

    }

  }

  // Calculate subject counts under current category filter
  const subjectCounts = {};

  baseCategoryQuestions.forEach(q => {

    if (q.subject) {

      subjectCounts[q.subject] = (subjectCounts[q.subject] || 0) + 1;

    }

  });

  const availableSubjects = Object.keys(subjectCounts).sort();

  if (f.subject !== 'all' && !subjectCounts[f.subject]) {

    f.subject = 'all';

  }

  let filtered = [...baseCategoryQuestions];

  if (f.subject !== 'all')    filtered = filtered.filter(q => q.subject === f.subject);

  // Calculate topic counts under current category + subject filter
  const topicCounts = {};

  filtered.forEach(q => {

    if (q.topic) {

      topicCounts[q.topic] = (topicCounts[q.topic] || 0) + 1;

    }

  });

  const availableTopics = Object.keys(topicCounts).sort();

  if (f.topic !== 'all' && !topicCounts[f.topic]) {

    f.topic = 'all';

  }

  if (f.topic !== 'all')      filtered = filtered.filter(q => q.topic === f.topic);

  if (f.difficulty !== 'all') filtered = filtered.filter(q => q.difficulty === f.difficulty);

  if (f.type !== 'all')       filtered = filtered.filter(q => q.type === f.type);



  // Status Filter: Mistakes / Unattempted / Correct / Bookmarked

  if (f.status === 'incorrect') {

    const wrongIds = new Set(state.attempts.filter(a => a.correct === false).map(a => a.questionId));

    filtered = filtered.filter(q => wrongIds.has(q.id));

  } else if (f.status === 'correct') {

    const correctIds = new Set(state.attempts.filter(a => a.correct === true).map(a => a.questionId));

    filtered = filtered.filter(q => correctIds.has(q.id));

  } else if (f.status === 'srs-due') {

    const now = Date.now();

    const dueIds = new Set(Object.entries(state.srsQueue || {})

      .filter(([, s]) => s.nextReview <= now).map(([id]) => id));

    filtered = filtered.filter(q => dueIds.has(q.id));

  } else if (f.status === 'unattempted') {

    const attemptedIds = new Set(state.attempts.map(a => a.questionId));

    filtered = filtered.filter(q => !attemptedIds.has(q.id));

  } else if (f.status === 'bookmarked') {

    filtered = filtered.filter(q => state.bookmarks.has(q.id));

    if (state.activeBookmarkTag && state.activeBookmarkTag !== 'all') {

      filtered = filtered.filter(q => (state.bookmarkTags[q.id] || 'exam') === state.activeBookmarkTag);

    }

  }



  if (state.practiceSearch && state.practiceSearch.trim()) {

    const pTerms = state.practiceSearch.trim().toLowerCase().split(/\s+/).filter(Boolean);

    filtered = filtered.filter(q => {

      const hay = ((q.question || '') + ' ' + (q.subject || '') + ' ' + (q.topic || '') + ' ' + (q.year || '') + ' ' + (q.explanation || '')).toLowerCase();

      return pTerms.every(t => hay.includes(t));

    });

  }



  // Deduplicate redundant cross-mock copies in general practice so each unique problem appears once

  const seenCanonical = new Set();

  filtered = filtered.filter(q => {

    const cid = q.canonicalId || q.id;

    if (seenCanonical.has(cid)) return false;

    seenCanonical.add(cid);

    return true;

  });



  // Sort order applied to practice questions & queue

  const sortMode = state.practiceSort || 'default';

  if (sortMode === 'year-desc') {

    filtered.sort((a, b) => {

      const ya = a.year ? parseInt(a.year, 10) : 0;

      const yb = b.year ? parseInt(b.year, 10) : 0;

      if (ya !== yb) return yb - ya;

      return (b.marks || 1) - (a.marks || 1);

    });

  } else if (sortMode === 'year-asc') {

    filtered.sort((a, b) => {

      const ya = a.year ? parseInt(a.year, 10) : 9999;

      const yb = b.year ? parseInt(b.year, 10) : 9999;

      if (ya !== yb) return ya - yb;

      return (b.marks || 1) - (a.marks || 1);

    });

  } else if (sortMode === 'diff-hard') {

    const rank = { hard: 3, medium: 2, easy: 1 };

    filtered.sort((a, b) => (rank[b.difficulty] || 2) - (rank[a.difficulty] || 2));

  } else if (sortMode === 'diff-easy') {

    const rank = { hard: 3, medium: 2, easy: 1 };

    filtered.sort((a, b) => (rank[a.difficulty] || 2) - (rank[b.difficulty] || 2));

  } else if (sortMode === 'marks-desc') {

    filtered.sort((a, b) => (b.marks || 1) - (a.marks || 1));

  }



  // Preserve full filtered list in queue for practice mode

  state.practiceQueue = filtered;



  // Pagination calculation

  const totalCount = filtered.length;

  const pageSize = state.practicePageSize === 'all' ? (totalCount || 1) : parseInt(state.practicePageSize, 10);

  const totalPages = Math.max(1, Math.ceil(totalCount / pageSize));

  if (state.practicePage > totalPages) state.practicePage = totalPages;

  if (state.practicePage < 1) state.practicePage = 1;



  const startIndex = (state.practicePage - 1) * pageSize;

  const endIndex = Math.min(startIndex + pageSize, totalCount);

  const pageItems = filtered.slice(startIndex, endIndex);



  const paginationArgs = {

    currentPage: state.practicePage,

    totalPages,

    totalCount,

    startIndex: totalCount > 0 ? startIndex + 1 : 0,

    endIndex,

    pageSize: state.practicePageSize,

    onPageChangeFn: 'setPracticePage',

    onPageSizeChangeFn: 'setPracticePageSize'

  };



  c.innerHTML = `

    <div class="breadcrumb">

      <span class="breadcrumb-item" onclick="navigate('subjects')" style="cursor:pointer;color:var(--accent)">Subjects</span>

      <span class="breadcrumb-sep">›</span><span class="breadcrumb-item active">Practice Questions</span>

    </div>

    <div class="section-header">

      <div class="section-title">Practice Questions <span>${totalCount} questions</span></div>

      <div style="display:flex;gap:8px;align-items:center">

        <button class="btn btn-secondary btn-sm" onclick="openRandomQuestion()" style="font-weight:700" type="button" title="Open a random question from current filter">🎲 Random</button>

        <button class="btn btn-secondary btn-sm" onclick="toggleCustomDrillModal(true)" style="border-color:var(--accent);color:var(--accent);font-weight:700" type="button">🎛️ Custom Drill</button>

        <button class="btn btn-primary btn-sm" onclick="startPracticeMode()" ${!filtered.length ? 'disabled' : ''}>▶ Start Practice</button>

      </div>

    </div>



    <div class="practice-quick-chips" style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:12px">

      <button class="chip ${f.category === 'all' && f.status === 'all' ? 'active' : ''}" onclick="resetPracticeQuickFilters()" type="button">All (${state.questions.length})</button>

      <button class="chip ${isPyqActive ? 'active' : ''}" onclick="togglePracticePyqFilter()" type="button" style="border-color:#38bdf8;color:#38bdf8;font-weight:700">🏛️ Only Official PYQs (${pyqTotalCount})</button>

      <button class="chip ${f.status === 'unattempted' ? 'active' : ''}" onclick="updateFilter('status','unattempted')" type="button" style="border-color:var(--accent);color:var(--accent);font-weight:700">⭐ Unattempted</button>

      <button class="chip ${f.status === 'incorrect' ? 'active' : ''}" onclick="updateFilter('status','incorrect')" type="button" style="color:var(--red)">❌ Mistakes</button>

      <button class="chip ${f.status === 'srs-due' ? 'active' : ''}" onclick="updateFilter('status','srs-due')" type="button" style="color:#a855f7">🔁 Due Review ${getSRSDueCount() > 0 ? `(${getSRSDueCount()})` : ''}</button>

      <button class="chip ${f.status === 'bookmarked' ? 'active' : ''}" onclick="updateFilter('status','bookmarked')" type="button">🔖 Starred (${state.bookmarks.size})</button>

    </div>

    ${isPyqActive ? `

      <div style="background:rgba(56,189,248,0.08);border:1px solid rgba(56,189,248,0.3);border-radius:8px;padding:8px 14px;margin-bottom:12px;display:flex;align-items:center;justify-content:space-between;gap:8px;font-size:12.5px">

        <div style="display:flex;align-items:center;gap:8px">

          <span style="font-size:16px">🏛️</span>

          <div>

            <strong style="color:#38bdf8">Official GATE PYQs Filter Active</strong> — Showing authentic past GATE examination questions. Filter by Subject &amp; Topic below, or sort by Exam Year.

          </div>

        </div>

        <button class="btn btn-secondary btn-sm" onclick="togglePracticePyqFilter()" style="font-size:11px;padding:2px 8px;white-space:nowrap" type="button">Clear PYQ Filter ✕</button>

      </div>` : ''}

    ${f.status === 'bookmarked' ? `

      <div style="display:flex;gap:6px;margin:-8px 0 16px 0;flex-wrap:wrap;align-items:center">

        <span style="font-size:11px;color:var(--text-muted);font-weight:700">TAG FILTER:</span>

        <button class="chip ${state.activeBookmarkTag === 'all' ? 'active' : ''}" onclick="setBookmarkTagFilter('all')" style="font-size:11px" type="button">All Starred</button>

        <button class="chip ${state.activeBookmarkTag === 'trap' ? 'active' : ''}" onclick="setBookmarkTagFilter('trap')" style="font-size:11px;color:#ef4444" type="button">🔴 Conceptual Traps</button>

        <button class="chip ${state.activeBookmarkTag === 'calc' ? 'active' : ''}" onclick="setBookmarkTagFilter('calc')" style="font-size:11px;color:#f59e0b" type="button">🟡 Calculation Heavy</button>

        <button class="chip ${state.activeBookmarkTag === 'exam' ? 'active' : ''}" onclick="setBookmarkTagFilter('exam')" style="font-size:11px;color:#10b981" type="button">🟢 Pre-Exam Revise</button>

      </div>` : ''}



    <div class="filter-bar" style="display:flex;gap:8px;flex-wrap:wrap;align-items:center">

      <select class="filter-select" onchange="updateFilter('status',this.value)" title="Attempt Status">

        <option value="all" ${f.status === 'all' ? 'selected' : ''}>All Status</option>

        <option value="incorrect" ${f.status === 'incorrect' ? 'selected' : ''}>❌ Mistakes / Incorrect</option>

        <option value="unattempted" ${f.status === 'unattempted' ? 'selected' : ''}>⬜ Unattempted</option>

        <option value="correct" ${f.status === 'correct' ? 'selected' : ''}>✅ Correct</option>

        <option value="bookmarked" ${f.status === 'bookmarked' ? 'selected' : ''}>⭐ Bookmarked</option>

      </select>

      <select class="filter-select" onchange="updateFilter('category',this.value)" id="practice-category-select" title="Question Category" style="${isPyqActive ? 'border-color:#38bdf8;color:#38bdf8;font-weight:700' : ''}">

        <option value="all" ${f.category === 'all' ? 'selected' : ''}>All Categories (${state.questions.length})</option>

        <option value="pyq" ${f.category === 'pyq' ? 'selected' : ''}>🏛️ Official GATE PYQs (${pyqTotalCount})</option>

        <option value="subject" ${f.category === 'subject' ? 'selected' : ''}>Subject Questions</option>

        <option value="mock" ${f.category === 'mock' ? 'selected' : ''}>Mock Questions</option>

        <option value="test_series" ${f.category === 'test_series' ? 'selected' : ''}>Test Series Questions</option>

        <option value="community" ${f.category === 'community' ? 'selected' : ''}>👥 Community Contributed</option>

      </select>

      <select class="filter-select" onchange="updateFilter('subject',this.value)" id="practice-subject-select" title="GATE Subject">

        <option value="all" ${f.subject === 'all' ? 'selected' : ''}>All Subjects (${baseCategoryQuestions.length})</option>

        ${availableSubjects.map(s => `<option value="${s}" ${f.subject === s ? 'selected' : ''}>${s} (${subjectCounts[s] || 0})</option>`).join('')}

      </select>

      <select class="filter-select" onchange="updateFilter('topic',this.value)" id="practice-topic-select" title="Subject Topic">

        <option value="all" ${f.topic === 'all' ? 'selected' : ''}>All Topics (${f.subject === 'all' ? 'All' : availableTopics.length})</option>

        ${availableTopics.map(t => `<option value="${t}" ${f.topic === t ? 'selected' : ''}>${t} (${topicCounts[t] || 0})</option>`).join('')}

      </select>

      <select class="filter-select" onchange="updatePracticeSort(this.value)" id="practice-sort-select" title="Sort Order" style="min-width:170px">

        <option value="default" ${state.practiceSort === 'default' ? 'selected' : ''}>🔀 Sort: Default</option>

        <option value="year-desc" ${state.practiceSort === 'year-desc' ? 'selected' : ''}>📅 GATE Year: 2025 → 1990</option>

        <option value="year-asc" ${state.practiceSort === 'year-asc' ? 'selected' : ''}>📅 GATE Year: 1990 → 2025</option>

        <option value="diff-hard" ${state.practiceSort === 'diff-hard' ? 'selected' : ''}>🔥 Hard to Easy</option>

        <option value="diff-easy" ${state.practiceSort === 'diff-easy' ? 'selected' : ''}>🌱 Easy to Hard</option>

        <option value="marks-desc" ${state.practiceSort === 'marks-desc' ? 'selected' : ''}>🎯 2 Marks First</option>

      </select>

      <select class="filter-select" onchange="updateFilter('difficulty',this.value)" title="Difficulty">

        <option value="all" ${f.difficulty === 'all' ? 'selected' : ''}>All Difficulty</option>

        <option value="easy" ${f.difficulty === 'easy' ? 'selected' : ''}>Easy</option>

        <option value="medium" ${f.difficulty === 'medium' ? 'selected' : ''}>Medium</option>

        <option value="hard" ${f.difficulty === 'hard' ? 'selected' : ''}>Hard</option>

      </select>

      <select class="filter-select" onchange="updateFilter('type',this.value)" title="Question Format">

        <option value="all" ${f.type === 'all' ? 'selected' : ''}>All Types</option>

        <option value="mcq" ${f.type === 'mcq' ? 'selected' : ''}>MCQ</option>

        <option value="msq" ${f.type === 'msq' ? 'selected' : ''}>MSQ</option>

        <option value="nat" ${f.type === 'nat' ? 'selected' : ''}>NAT</option>

      </select>

      <input type="text" class="search-input" placeholder="🔍 Search question or topic..."

        value="${escapeHtml(state.practiceSearch || '')}"

        oninput="updatePracticeSearch(this.value)" style="min-width:180px;flex:1" />

    </div>

    ${!totalCount

      ? `<div class="empty-state">

           <div class="empty-state-icon">📭</div>

           <div class="empty-state-title">No questions found</div>

           <div class="empty-state-sub">Adjust filters or <span class="text-accent" style="cursor:pointer" onclick="navigate('upload')">upload questions</span>.</div>

         </div>`

      : `${buildPaginationHTML({ ...paginationArgs, isTop: true })}

         <div class="pyq-grid" id="practice-questions-grid">

           ${pageItems.map((q, idx) => buildQListItem(q, startIndex + idx)).join('')}

         </div>

         ${buildPaginationHTML({ ...paginationArgs, isTop: false })}`

    }`;

  renderMath(c);

  highlightCodeBlocks(c);

}



function buildQListItem(q, overallIdx) {

  const att = state.attempts.find(a => a.questionId === q.id);

  const icon = att ? (att.correct ? '✅' : '❌') : '⬜';

  const numLabel = overallIdx !== undefined ? `Q${overallIdx + 1}` : '';

  const isBookmarked = state.bookmarks?.has(q.id);

  return `

    <div class="pyq-item" onclick="openSingleQuestion('${q.id}')">

      <div class="pyq-item-year" style="font-size:11px">

        ${icon}<br/>

        <span style="font-size:10px;color:var(--text-muted)">${q.type?.toUpperCase()}</span>

      </div>

      <div class="pyq-item-content">

        <div class="pyq-item-question">

          ${numLabel ? `<strong style="color:var(--accent);margin-right:6px">${numLabel}.</strong>` : ''}${q.question}

        </div>

        <div class="pyq-item-meta">

          ${isQuestionPyq(q) ? `<span class="chip" style="background:rgba(56,189,248,0.15);color:#38bdf8;font-weight:700">🏛️ GATE ${q.year || ''} PYQ</span>` : ''}

          <span class="chip">${q.subject}</span>

          ${q.topic ? `<span class="chip">${q.topic}</span>` : ''}

          <span class="q-badge ${q.difficulty}">${q.difficulty}</span>

          <span class="chip">${q.marks}m</span>

          ${(q.source === 'community' || (q.uploadedBy && !STATIC_BUNDLED_IDS.has(q.id))) ? `<span class="chip" style="background:rgba(168,85,247,0.15);color:#a855f7;font-weight:600">👥 Community</span>` : ''}

        </div>

      </div>

      <div style="display:flex;flex-direction:column;gap:4px;align-items:flex-end;flex-shrink:0">

        <button class="star-btn ${isBookmarked ? 'bookmarked' : ''}" data-qid="${q.id}" onclick="event.stopPropagation(); toggleBookmark('${q.id}')" title="${isBookmarked ? 'Remove Bookmark' : 'Add Bookmark'}" type="button">

          ${isBookmarked ? '⭐' : '☆'}

        </button>

        <button class="copy-q-btn" onclick="event.stopPropagation(); copyQuestionText('${q.id}', this)" title="Copy question text" type="button">📋 Copy</button>

        <button class="report-q-btn" onclick="event.stopPropagation(); openReportModal('${q.id}')" title="Report this question" type="button">🚨</button>

      </div>

    </div>`;

}





function updateFilter(k, v) {

  state.practiceFilters[k] = v;

  if (k === 'category' || k === 'subject') {

    state.practiceFilters.topic = 'all';

  }

  state.practicePage = 1;

  renderPractice(document.getElementById('page-content'));

}

function togglePracticePyqFilter() {

  if (state.practiceFilters.category === 'pyq') {

    state.practiceFilters.category = 'all';

  } else {

    state.practiceFilters.category = 'pyq';

  }

  state.practiceFilters.topic = 'all';

  state.practicePage = 1;

  renderPractice(document.getElementById('page-content'));

}

function updatePracticeSort(val) {

  state.practiceSort = val;

  state.practicePage = 1;

  renderPractice(document.getElementById('page-content'));

}

function resetPracticeQuickFilters() {

  state.practiceFilters = {

    status: 'all',

    category: 'all',

    subject: 'all',

    topic: 'all',

    difficulty: 'all',

    type: 'all'

  };

  state.practiceSearch = '';

  state.practiceSort = 'default';

  state.practicePage = 1;

  renderPractice(document.getElementById('page-content'));

}

function isQuestionPyq(q) {

  if (!q) return false;

  if (q.category === 'pyq' || q.isPyq === true) return true;

  if (typeof q.source === 'string' && q.source.toLowerCase().includes('pyq')) return true;

  if (typeof q.id === 'string' && q.id.startsWith('pyq-')) return true;

  return false;

}



function setPracticePage(p) {

  state.practicePage = p;

  renderPractice(document.getElementById('page-content'));

  const el = document.getElementById('practice-questions-grid');

  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });

}



function setPracticePageSize(sz) {

  state.practicePageSize = sz === 'all' ? 'all' : parseInt(sz, 10);

  state.practicePage = 1;

  renderPractice(document.getElementById('page-content'));

}



let practiceSearchTimer = null;

function updatePracticeSearch(val) {

  state.practiceSearch = val;

  state.practicePage = 1;

  clearTimeout(practiceSearchTimer);

  practiceSearchTimer = setTimeout(() => {

    renderPractice(document.getElementById('page-content'));

  }, 200);

}



// ─── PRACTICE MODE ───────────────────────────────────────────────────────────

let practiceTimer = null, practiceSeconds = 0, practiceSelectedOpts = new Set();



function startPracticeMode() {

  if (!state.practiceQueue.length) return;

  state.currentQuestion = 0;

  practiceSelectedOpts = new Set();

  renderPracticeQuestion();

}



function renderPracticeQuestion() {

  const q = state.practiceQueue[state.currentQuestion];

  if (!q) return;

  practiceSelectedOpts = new Set();

  state.practiceAnswered = false;

  practiceSeconds = 0;

  const ov = document.getElementById('test-overlay');

  ov.innerHTML = `

    <div class="test-topbar">

      <div class="test-topbar-left">

        <button class="btn btn-secondary btn-sm" onclick="closePracticeMode()">✕ Exit</button>

        <div class="test-title" title="${q.subject}">Practice • ${q.subject}</div>

      </div>

      <div class="test-topbar-right">

        <button class="btn btn-secondary btn-sm" id="exam-strict-btn" onclick="toggleExamStrictMode()" type="button" title="Toggle TCS iON Exam Strict Mode">${state.examStrictMode ? '🛡️ Strict: ON' : '🛡️ Strict: OFF'}</button>

        <button class="btn btn-secondary btn-sm" id="test-scribble-btn" onclick="toggleScribblePad()" type="button" title="Virtual Scribble Pad (Alt+S)">📝 <span class="hide-xs">Scratchpad</span></button>

        <button class="btn btn-secondary btn-sm" id="exam-fullscreen-btn" onclick="toggleExamFullscreen()" type="button" title="Toggle Fullscreen Exam Mode (F)">⛶ <span class="hide-xs">Fullscreen</span></button>

        <button class="btn btn-secondary btn-sm" onclick="toggleGateCalc()" type="button" title="GATE Virtual Calculator (C)">🧮 <span class="hide-xs">Calc</span></button>

        <button class="btn btn-secondary btn-sm" onclick="openFormulaFlashcardsModal('${getMatchingFlashcardId(q)}')" type="button" title="Formula Flashcards (H)">📇 <span class="hide-xs">Flashcards</span></button>

        <button class="btn btn-secondary btn-sm" onclick="toggleShortcutsModal()" type="button" title="Shortcuts (?)">⌨️</button>

        <span class="test-q-counter">${state.currentQuestion + 1} / ${state.practiceQueue.length}</span>

        <div class="test-timer-display" id="practice-timer">⏱ 00:00</div>

        <button class="btn btn-secondary btn-sm test-palette-toggle" onclick="toggleTestPalette()" type="button" title="Question Palette">

          📋 <span class="hide-xs">Palette</span>

        </button>

      </div>

    </div>

    <div class="test-content">

      <div class="palette-backdrop" id="palette-backdrop" onclick="toggleTestPalette()"></div>

      <div class="test-sidebar" id="test-sidebar">

        <div class="test-sidebar-header">

          <div class="section-title" style="font-size:13px">Question Navigator</div>

          <button class="palette-close-btn" onclick="toggleTestPalette()" type="button">✕</button>

        </div>

        <div class="question-palette">

          ${state.practiceQueue.map((pq, i) => {

            const a = state.attempts.find(x => x.questionId === pq.id);

            const cls = i === state.currentQuestion ? 'current' : a ? (a.correct ? 'attempted' : 'skipped') : '';

            return `<button class="palette-btn ${cls}" onclick="jumpToPracticeQ(${i})">${i + 1}</button>`;

          }).join('')}

        </div>

        <div class="divider"></div>

        <div class="palette-legend">

          <div class="palette-legend-item"><div class="legend-dot" style="background:var(--accent)"></div>Current</div>

          <div class="palette-legend-item"><div class="legend-dot" style="background:var(--green)"></div>Correct</div>

          <div class="palette-legend-item"><div class="legend-dot" style="background:var(--red)"></div>Wrong</div>

          <div class="palette-legend-item"><div class="legend-dot" style="background:var(--border)"></div>Not done</div>

        </div>

      </div>

      <div class="test-main" id="test-main">${buildPracticeQHTML(q)}</div>

    </div>`;

  ov.classList.add('active');

  startPracticeTimer();

  attachOptionListeners(q);

  renderMath(ov);

}



function buildPracticeQHTML(q) {

  const total = state.practiceQueue.length || 1;

  const pct = ((state.currentQuestion + 1) / total) * 100;

  const labels = ['A', 'B', 'C', 'D', 'E'];

  const hasPrev = state.currentQuestion > 0;

  const hasNext = state.currentQuestion < state.practiceQueue.length - 1;

  const isBookmarked = state.bookmarks?.has(q.id);



  return `

    <div class="question-progress-bar"><div class="question-progress-fill" style="width:${pct}%"></div></div>

    <div class="question-card">

      <div class="question-header">

        <div class="question-meta">

          <span class="q-badge ${q.type}">${q.type?.toUpperCase()}</span>

          <span class="q-badge ${q.difficulty}">${q.difficulty}</span>

          ${isQuestionPyq(q) ? `<span class="chip" style="background:rgba(56,189,248,0.15);color:#38bdf8;font-weight:700">🏛️ GATE ${q.year || ''} PYQ</span>` : ''}

          ${q.subject ? `<span class="chip">${q.subject}</span>` : ''}

          ${q.topic ? `<span class="chip">${q.topic}</span>` : ''}

        </div>

        <div style="display:flex;align-items:center;gap:8px">

          <button class="star-btn ${isBookmarked ? 'bookmarked' : ''}" data-qid="${q.id}" onclick="toggleBookmark('${q.id}')" title="${isBookmarked ? 'Remove Bookmark' : 'Add Bookmark'}" type="button">

            ${isBookmarked ? '⭐' : '☆'}

          </button>

          <button class="formula-hint-btn" onclick="toggleFormulaHint('${q.id}')" type="button" title="Peek Topic Formula Hint">💡 Formula Hint</button>

          <button class="btn btn-secondary btn-sm" onclick="openPlaylistModal('${q.id}')" style="font-size:11px;padding:2px 8px;border-color:var(--border)" title="Add to Smart Playlist" type="button">

            🗂️ Playlist

          </button>

          <span class="chip ${q.type === 'mcq' ? 'penalty-chip' : 'zero-penalty-chip'}" title="${q.type === 'mcq' ? `Negative mark penalty: ${(q.marks/3).toFixed(2)} marks for wrong answer` : 'Zero negative marking for this question'}">+${q.marks} / ${q.type === 'mcq' ? `-${(q.marks/3).toFixed(2)}` : '0 penalty'}</span>

        </div>

      </div>

      <div style="display:flex;align-items:center;justify-content:space-between;margin:6px 0 10px 0;">

        <div class="question-number" style="margin:0">Question ${state.currentQuestion + 1} of ${total}</div>

        <button class="btn btn-secondary btn-sm" onclick="togglePracticeHint()" type="button" title="View Concept Hint & Formula Flashcards (H)" style="border-color:var(--accent);color:var(--accent);font-weight:600;display:inline-flex;align-items:center;gap:5px;font-size:12px;padding:3px 10px">

          💡 <span>Hint / Formula</span>

        </button>

      </div>

      <div class="practice-hint-box" id="practice-hint-box" style="display:none">

        ${buildQuestionHintHTML(q)}

      </div>

      <div class="question-text">${formatQuestionContent(q.question)}</div>

      <div id="formula-hint-box-${q.id}" class="formula-hint-box" style="display:none"></div>

      ${q.type === 'nat'

        ? `<div class="nat-wrapper">

             <div class="nat-input-wrapper">

               <input type="text" inputmode="decimal" class="nat-input" id="nat-answer" placeholder="Enter answer" ${state.examStrictMode ? 'readonly="readonly" style="cursor:not-allowed"' : ''}/>

             </div>

             ${buildNatKeypadHTML()}

           </div>`

        : (!q.options || q.options.length === 0)
          ? `<div class="notice-box info" style="margin:12px 0;padding:12px 16px;background:rgba(255,160,0,0.08);border:1px solid rgba(255,160,0,0.3);border-radius:8px">
               ℹ️ <strong>Figure/Diagram Reference:</strong> The options for this question require visual diagrams from the official GATE paper.
             </div>`
          : `<div class="options-list">${(q.options || []).map((opt, i) => `

             <div class="option-item" data-idx="${i}">

               <div class="option-label">${labels[i]}</div>

               <div class="option-text">${formatQuestionContent(opt)}</div>

             </div>`).join('')}</div>`}

      <div class="explanation-box" id="explanation-box">

        ${buildMultiMethodExplanationHTML(q)}

        ${buildStudentShortcutNoteHTML(q.id)}

      </div>

    </div>

    <div class="question-actions" id="q-actions">

      <button class="btn btn-primary" onclick="submitPracticeAnswer()">Submit Answer</button>

      <button class="btn btn-secondary" onclick="togglePracticeHint()" type="button">💡 Hint / Formula</button>

      <button class="btn btn-secondary" onclick="skipQuestion()">Skip →</button>

      ${hasPrev ? `<button class="btn btn-secondary" onclick="prevPracticeQuestion()">← Prev</button>` : ''}

      ${hasNext ? `<button class="btn btn-secondary" onclick="nextPracticeQuestion()">Next →</button>` : ''}

    </div>

    <div class="question-actions hidden" id="q-next-actions">

      ${hasPrev ? `<button class="btn btn-secondary" onclick="prevPracticeQuestion()">← Prev</button>` : ''}

      ${hasNext

        ? `<button class="btn btn-primary" onclick="nextPracticeQuestion()">Next Question →</button>`

        : `<button class="btn btn-success" onclick="closePracticeMode()">🎉 Finish Practice</button>`}

      <button class="btn btn-secondary" onclick="closePracticeMode()">Exit Practice</button>

    </div>`;

}



function prevPracticeQuestion() {

  stopPracticeTimer();

  if (state.currentQuestion > 0) {

    state.currentQuestion--;

    renderPracticeQuestion();

  }

}



function toggleTestPalette() {

  const sb = document.getElementById('test-sidebar') || document.querySelector('.test-sidebar');

  const bd = document.getElementById('palette-backdrop');

  if (!sb) return;

  const isOpen = sb.classList.toggle('mobile-open');

  if (bd) bd.classList.toggle('active', isOpen);

}



function attachOptionListeners(q){

  if (q.type==='nat') return;

  document.querySelectorAll('.option-item').forEach(item=>{

    item.addEventListener('click',()=>{

      if (state.practiceAnswered||item.classList.contains('disabled')) return;

      playUiClickSound();

      const idx=parseInt(item.dataset.idx);

      if (q.type==='msq'){

        if (practiceSelectedOpts.has(idx)){practiceSelectedOpts.delete(idx);item.classList.remove('selected');}

        else{practiceSelectedOpts.add(idx);item.classList.add('selected');}

      } else {

        document.querySelectorAll('.option-item').forEach(i=>i.classList.remove('selected'));

        practiceSelectedOpts.clear(); practiceSelectedOpts.add(idx); item.classList.add('selected');

      }

    });

  });

}



async function submitPracticeAnswer(){

  const q=state.practiceQueue[state.currentQuestion];

  const hasKey = hasUsableAnswerKey(q);

  let ok=false;

  let userVal = null;

  if (q.type==='nat'){

    const inp=document.getElementById('nat-answer');

    if (!inp||inp.value.trim()===''){showToast('Enter a numerical answer','error');return;}

    userVal = inp.value.trim();

    inp.disabled=true;

    if (hasKey) {

      const ev = evaluateQuestionAnswer(q, userVal);

      ok = ev.correct;

      inp.classList.add(ok?'correct':'wrong');

    } else {

      inp.style.borderColor = 'var(--accent)';

      showToast('ℹ️ Answer Key Pending Verification in Archive — Practice Only', 'info', 3000);

    }

  } else {

    if (!practiceSelectedOpts.size){showToast('Select an option','error');return;}

    userVal = [...practiceSelectedOpts];

    document.querySelectorAll('.option-item').forEach(el=>{

      const idx=parseInt(el.dataset.idx); el.classList.add('disabled');

      if (hasKey) {

        if (q.correct.includes(idx)) el.classList.add('correct');

        else if (practiceSelectedOpts.has(idx)) el.classList.add('wrong');

      } else {

        if (practiceSelectedOpts.has(idx)) el.classList.add('selected');

      }

      el.classList.remove('selected');

    });

    if (hasKey) {

      const ev = evaluateQuestionAnswer(q, userVal);

      ok = ev.correct;

    } else {

      showToast('ℹ️ Answer Key Pending Verification in Archive — Practice Only', 'info', 3000);

    }

  }

  state.practiceAnswered=true; stopPracticeTimer();

  const expBox = document.getElementById('explanation-box');

  if (expBox) {

    expBox.innerHTML = `

      ${buildConfidenceSelectorHTML(q.id)}

      ${buildExpectedValueCardHTML(q)}

      ${q.type === 'nat' ? buildNatToleranceHTML(q) : ''}

      ${buildMultiMethodExplanationHTML(q)}

      ${buildStudentShortcutNoteHTML(q.id)}

    `;

    expBox.classList.add('show');

    renderMath(expBox);

  }

  document.getElementById('q-actions').classList.add('hidden');

  document.getElementById('q-next-actions').classList.remove('hidden');

  if (hasKey) {

    await persistAttempt({questionId:q.id, correct:ok, timeMs:practiceSeconds*1000, date:Date.now(), uid:uid()});

    recordDailyAttemptForStreak();

    updateSidebarSubjectProgress();

    // Update SRS spaced repetition queue

    if (q && q.id) updateSRSAfterAttempt(q.id, ok);

    showToast(ok?'✅ Correct!':'❌ Wrong answer', ok?'success':'error');

  } else {

    await persistAttempt({questionId:q.id, correct:false, unscored:true, timeMs:practiceSeconds*1000, date:Date.now(), uid:uid()});

    recordDailyAttemptForStreak();

    updateSidebarSubjectProgress();

  }

  updatePracticePalette();

}



function updatePracticePalette(){

  document.querySelectorAll('.palette-btn').forEach((btn,i)=>{

    const pq=state.practiceQueue[i];

    const a=state.attempts.find(x=>x.questionId===pq.id);

    btn.className='palette-btn';

    if (i===state.currentQuestion) btn.classList.add('current');

    else if (a) btn.classList.add(a.correct?'attempted':'skipped');

  });

}



function skipQuestion(){ stopPracticeTimer(); nextPracticeQuestion(); }

function nextPracticeQuestion(){

  if (state.currentQuestion<state.practiceQueue.length-1){state.currentQuestion++;renderPracticeQuestion();}

  else{closePracticeMode();showToast('🎉 Practice session complete!','success');}

}

function jumpToPracticeQ(i){

  state.currentQuestion=i;

  renderPracticeQuestion();

  if (window.innerWidth <= 768) {

    document.getElementById('test-sidebar')?.classList.remove('mobile-open');

    document.getElementById('palette-backdrop')?.classList.remove('active');

  }

}

function closePracticeMode(){

  stopPracticeTimer();

  const ov=document.getElementById('test-overlay');

  ov.innerHTML=''; ov.classList.remove('active');

  renderPage(state.currentPage, state.currentParams||{});

}

function openSingleQuestion(id){

  const idx = state.practiceQueue.findIndex(x => x.id === id);

  if (idx !== -1) {

    state.currentQuestion = idx;

  } else {

    const q=state.questions.find(x=>x.id===id);

    if (!q) return;

    state.practiceQueue=[q]; state.currentQuestion=0;

  }

  renderPracticeQuestion();

}



function startPracticeTimer(){

  stopPracticeTimer(); practiceSeconds=0;

  practiceTimer=setInterval(()=>{

    practiceSeconds++;

    const el=document.getElementById('practice-timer');

    if (el) el.textContent=`⏱ ${fmt(practiceSeconds)}`;

  },1000);

}

function stopPracticeTimer(){ if(practiceTimer){clearInterval(practiceTimer);practiceTimer=null;} }

function fmt(s){ return `${String(Math.floor(s/60)).padStart(2,'0')}:${String(s%60).padStart(2,'0')}`; }

function fmtH(s){ const h=Math.floor(s/3600),m=Math.floor((s%3600)/60),sec=s%60; return h>0?`${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}:${String(sec).padStart(2,'0')}`:`${String(m).padStart(2,'0')}:${String(sec).padStart(2,'0')}`; }



// ─── MOCK & PRACTICE PAPERS HELPERS ──────────────────────────────────────────

function getMockQuestions(mockId) {
  const targetMock = (typeof MOCK_TESTS !== 'undefined' ? MOCK_TESTS.find(m => m.id === mockId) : null) || 
                     (typeof FULL_LENGTH_PYQ_EXAMS !== 'undefined' ? FULL_LENGTH_PYQ_EXAMS.find(e => e.id === mockId) : null);

  // 1. Direct mock questions tagged with mockId (or matching paper mockId)

  const targetMockId = (mockId.startsWith('paper-cat') || mockId.startsWith('paper-flm') || mockId.startsWith('paper-easy') || mockId.startsWith('paper-med') || mockId.startsWith('paper-hard'))

    ? mockId.replace('paper-', 'mock-') : mockId;

  const directQs = state.questions.filter(q => q.mockId === targetMockId || q.mockId === mockId);

  if (directQs.length >= (targetMock ? targetMock.questions : 45)) return directQs;



  // 2. Full-Length PYQ Exam papers

  if (mockId === 'pyq-exam-2025-s1' || mockId === 'paper-gate-2025-s1' || mockId === 'mock-gate-2025-s1') {

    const s1 = state.questions.filter(q => q.paper === 'GATE 2025 Set 1' || q.id.startsWith('pyq_2025_s1'));

    if (s1.length) return s1.slice(0, 65);

  }

  if (mockId === 'pyq-exam-2025-s2' || mockId === 'paper-gate-2025-s2' || mockId === 'mock-gate-2025-s2') {

    const s2 = state.questions.filter(q => q.paper === 'GATE 2025 Set 2' || q.id.startsWith('pyq_2025_s2'));

    if (s2.length) return s2.slice(0, 65);

  }

  if (mockId === 'pyq-exam-2026-1' || mockId === 'mock-full-001') {

    const q1 = state.questions.filter(q => q.mockId === 'mock-full-001');

    if (q1.length) return q1.slice(0, 65);

  }

  if (mockId === 'pyq-exam-2026-2' || mockId === 'mock-full-002') {

    const q2 = state.questions.filter(q => q.mockId === 'mock-full-002');

    if (q2.length) return q2.slice(0, 65);

  }

  if (mockId === 'pyq-exam-2021' || mockId === 'paper-gate-2021') {

    const qs = state.questions.filter(q => q.year === 2021 || (q.paper && q.paper.includes('2021')));

    if (qs.length) return qs.slice(0, 65);

  }

  if (mockId === 'pyq-exam-2020' || mockId === 'paper-gate-2020') {

    const qs = state.questions.filter(q => q.year === 2020 || (q.paper && q.paper.includes('2020')));

    if (qs.length) return qs.slice(0, 65);

  }

  if (mockId === 'pyq-exam-2019' || mockId === 'paper-gate-2019') {

    const qs = state.questions.filter(q => q.year === 2019 || (q.paper && q.paper.includes('2019')));

    if (qs.length) return qs.slice(0, 65);

  }

  if (mockId === 'pyq-exam-2018' || mockId === 'paper-gate-2018') {

    const qs = state.questions.filter(q => q.year === 2018 || (q.paper && q.paper.includes('2018')));

    if (qs.length) return qs.slice(0, 65);

  }

  if (mockId === 'pyq-exam-2015-s1') {

    const qs = state.questions.filter(q => q.paper === 'GATE 2015 Set 1');

    const all2015 = state.questions.filter(q => q.year === 2015);

    const combined = [...qs, ...all2015.filter(q => !qs.includes(q))];

    if (combined.length) return combined.slice(0, 65);

  }

  if (mockId === 'pyq-exam-2015-s2') {

    const qs = state.questions.filter(q => q.paper === 'GATE 2015 Set 2');

    const all2015 = state.questions.filter(q => q.year === 2015);

    const combined = [...qs, ...all2015.filter(q => !qs.includes(q))];

    if (combined.length) return combined.slice(0, 65);

  }

  if (mockId === 'pyq-exam-2015-s3') {

    const qs = state.questions.filter(q => q.paper === 'GATE 2015 Set 3');

    const all2015 = state.questions.filter(q => q.year === 2015);

    const combined = [...qs, ...all2015.filter(q => !qs.includes(q))];

    if (combined.length) return combined.slice(0, 65);

  }

  if (mockId === 'pyq-exam-2014-s1') {

    const qs = state.questions.filter(q => q.paper === 'GATE 2014 Set 1');

    const all2014 = state.questions.filter(q => q.year === 2014);

    const combined = [...qs, ...all2014.filter(q => !qs.includes(q))];

    if (combined.length) return combined.slice(0, 65);

  }

  if (mockId === 'pyq-exam-2014-s2') {

    const qs = state.questions.filter(q => q.paper === 'GATE 2014 Set 2');

    const all2014 = state.questions.filter(q => q.year === 2014);

    const combined = [...qs, ...all2014.filter(q => !qs.includes(q))];

    if (combined.length) return combined.slice(0, 65);

  }

  if (mockId === 'pyq-exam-2014-s3') {

    const qs = state.questions.filter(q => q.paper === 'GATE 2014 Set 3');

    const all2014 = state.questions.filter(q => q.year === 2014);

    const combined = [...qs, ...all2014.filter(q => !qs.includes(q))];

    if (combined.length) return combined.slice(0, 65);

  }

  if (mockId === 'pyq-exam-2011' || mockId === 'paper-gate-2011') {

    const qs = state.questions.filter(q => q.year === 2011 || (q.paper && q.paper.includes('2011')));

    if (qs.length) return qs.slice(0, 65);

  }

  if (mockId === 'pyq-exam-decade' || mockId === 'paper-decade-pyq') {

    const dqs = state.questions.filter(q => q.category === 'pyq');

    if (dqs.length >= 65) return dqs.slice(0, 65);

  }

  // Generic match by year in exam id e.g. pyq-exam-2024, pyq-exam-2023, pyq-exam-2022, pyq-exam-2017, pyq-exam-2016

  const ym = mockId.match(/(?:19|20)\d\d/);

  if (ym) {

    const y = parseInt(ym[0], 10);

    const yrQs = state.questions.filter(q => q.year === y);

    if (yrQs.length >= 65) return yrQs.slice(0, 65);

    if (yrQs.length > 0) {

      const filler = state.questions.filter(q => q.category === 'pyq' && q.year !== y);

      return [...yrQs, ...filler.slice(0, 65 - yrQs.length)];

    }

  }



  // 3. Check Practice Sets

  if (mockId === 'paper-dsa') return state.questions.filter(q => ['Data Structures', 'Algorithms', 'C Programming'].includes(q.subject)).slice(0, 50);

  if (mockId === 'paper-systems') return state.questions.filter(q => ['Operating Systems', 'Computer Networks', 'Computer Organization'].includes(q.subject)).slice(0, 50);

  if (mockId === 'paper-theory') return state.questions.filter(q => ['Theory of Computation', 'Compiler Design'].includes(q.subject)).slice(0, 35);

  if (mockId === 'paper-maths') return state.questions.filter(q => ['Discrete Mathematics', 'Engineering Mathematics', 'Aptitude'].includes(q.subject)).slice(0, 45);

  if (mockId === 'paper-full-1') return state.questions.filter((_, idx) => (idx % 2) === 0).slice(0, 65);

  if (mockId === 'paper-full-2') return state.questions.filter((_, idx) => (idx % 2) === 1).slice(0, 65);



  // 4. Fallback to mock item or subject

  const mock = MOCK_TESTS.find(m => m.id === mockId) || FULL_LENGTH_PYQ_EXAMS.find(e => e.id === mockId);

  if (!mock) return [];



  if (mock.subject) {
    const subQs = state.questions.filter(q => q.subject === mock.subject);
    const count = mock.questions || 25;
    if (mock.id.endsWith('-adv')) {
      const advSlice = subQs.slice(count, count * 2);
      return advSlice.length >= count ? advSlice : subQs.slice(0, count);
    }
    return subQs.slice(0, count);
  }



  const targetCount = mock.questions || 65;

  if (mock.difficulty === 'easy') {

    const easyQs = state.questions.filter(q => q.difficulty === 'easy');

    const medQs = state.questions.filter(q => q.difficulty === 'medium');

    return [...easyQs, ...medQs].slice(0, targetCount);

  }

  if (mock.difficulty === 'hard') {

    const hardQs = state.questions.filter(q => q.difficulty === 'hard');

    const medQs = state.questions.filter(q => q.difficulty === 'medium');

    return [...hardQs, ...medQs].slice(0, targetCount);

  }

  return state.questions.slice(0, targetCount);

}



function getPaperDifficulty(p) {

  if (p && p.difficulty) return p.difficulty;

  if (p && p.mockId) {

    const m = MOCK_TESTS.find(x => x.id === p.mockId);

    if (m && m.difficulty) return m.difficulty;

  }

  if (!p || !p.id) return 'medium';

  if (p.id.includes('easy') || p.id.includes('cat1-set1') || p.id.includes('cat1-set2') || p.id === 'paper-full-1' || p.id === 'paper-gate-2011') return 'easy';

  if (p.id.includes('hard') || p.id.includes('cat2-set5') || p.id === 'paper-gate-2015' || p.id === 'paper-gate-2025-s2' || p.id === 'paper-systems') return 'hard';

  if (p.id.startsWith('paper-flm-')) {

    const num = parseInt(p.id.replace('paper-flm-', ''), 10);

    return num >= 11 ? 'hard' : 'medium';

  }

  return 'medium';

}



function getPaperRating(p) {

  if (p && typeof p.rating === 'number') return p.rating;

  if (p && p.mockId) {

    const m = MOCK_TESTS.find(x => x.id === p.mockId);

    if (m && typeof m.rating === 'number') return m.rating;

  }

  const diff = getPaperDifficulty(p);

  return diff === 'easy' ? 3.5 : (diff === 'hard' ? 7.5 : 5.0);

}



function toggleCalibrationTable() {

  state.showCalibrationTable = !state.showCalibrationTable;

  const c = document.getElementById('mock-tab-content');

  if (c) {

    const tab = state.mockTab || 'all';

    const fullMocks = MOCK_TESTS.filter(m => m.type === 'full' || m.type === 'practice-set');

    c.innerHTML = getMockTabHTML(tab, fullMocks);

    renderMath(c);

  }

}



function buildMockCalibrationGuide() {

  const isExpanded = state.showCalibrationTable || false;

  return `

    <div class="calibration-guide-box">

      <div class="calibration-guide-header">

        <div>

          <div style="font-size:16px;font-weight:700;color:var(--text-primary);display:flex;align-items:center;gap:8px">

            <span>🎯</span> 20 Full-Length Mocks: Difficulty Calibration & Rating Guide

          </div>

          <div style="font-size:12px;color:var(--text-muted);margin-top:2px">

            Official IISc/IIT GATE CS syllabus benchmark — Mocks #01–#10 (Medium) vs. Mocks #11–#20 (Hard)

          </div>

        </div>

        <button class="btn btn-secondary btn-sm" onclick="toggleCalibrationTable()" style="display:inline-flex;align-items:center;gap:6px" type="button">

          <span>${isExpanded ? '🔼 Hide Rating Table' : '📋 View 20-Mock Rating Matrix'}</span>

        </button>

      </div>



      <!-- Summary Tier Cards -->

      <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(280px, 1fr));gap:14px;margin-bottom:${isExpanded ? '16px' : '4px'}">

        <!-- Medium Tier Card -->

        <div class="calibration-tier-card medium">

          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px">

            <span class="q-badge medium" style="font-size:12px;padding:4px 12px">🟡 MEDIUM MOCKS (#01 – #10)</span>

            <span style="font-size:12px;font-weight:700;color:var(--yellow)">Rating: 4.5 – 6.1 / 10</span>

          </div>

          <div style="font-size:12.5px;color:var(--text-secondary);line-height:1.5;margin-bottom:8px">

            <strong>Standard GATE Pattern:</strong> Replicates typical IISc/IIT papers (e.g. GATE 2021, 2023, 2025 Set 1). Features clean arithmetic bounds, classical K-maps, standard planar graphs (\(V \le 26\)), and 2-level paging EMAT.

          </div>

          <div style="display:flex;gap:14px;font-size:12px;color:var(--text-primary);background:var(--bg-primary);padding:6px 10px;border-radius:6px;border:1px solid var(--border)">

            <span>🎯 <strong>Est. Cutoff:</strong> 28 – 32 Marks</span>

            <span>🏆 <strong>AIR &lt; 100:</strong> 72 – 78+ Marks</span>

          </div>

        </div>



        <!-- Hard Tier Card -->

        <div class="calibration-tier-card hard">

          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px">

            <span class="q-badge hard" style="font-size:12px;padding:4px 12px">🔴 HARD MOCKS (#11 – #20)</span>

            <span style="font-size:12px;font-weight:700;color:var(--red)">Rating: 6.8 – 9.2 / 10</span>

          </div>

          <div style="font-size:12.5px;color:var(--text-secondary);line-height:1.5;margin-bottom:8px">

            <strong>Rank Booster Challenges:</strong> High-intensity rank-booster exams. Modulo arithmetic up to \(\pmod{89}\), 64-state sliding-window DFAs, 141–266 leaf strict \(k\)-ary trees, 31-child fork trees, 8-fragment IPv4, and 144k matrix chains.

          </div>

          <div style="display:flex;gap:14px;font-size:12px;color:var(--text-primary);background:var(--bg-primary);padding:6px 10px;border-radius:6px;border:1px solid var(--border)">

            <span>🎯 <strong>Est. Cutoff:</strong> 20 – 26 Marks</span>

            <span>🏆 <strong>AIR &lt; 100:</strong> 60 – 68 Marks</span>

          </div>

        </div>

      </div>



      <!-- Expandable Table -->

      ${isExpanded ? `

        <div class="calibration-table-wrap">

          <table class="calibration-table">

            <thead>

              <tr>

                <th style="padding:10px 12px;white-space:nowrap">Mock Exam</th>

                <th style="padding:10px 12px;text-align:center">Difficulty Tier</th>

                <th style="padding:10px 12px;text-align:center">Rating</th>

                <th style="padding:10px 12px;text-align:center">Est. Cutoff</th>

                <th style="padding:10px 12px;text-align:center">AIR &lt; 100</th>

                <th style="padding:10px 12px">Key Technical Complexity Profile</th>

                <th style="padding:10px 12px;text-align:center">Action</th>

              </tr>

            </thead>

            <tbody>

              ${Array.from({length: 20}, (_, idx) => {

                const num = idx + 1;

                const id = 'mock-flm-' + String(num).padStart(2, '0');

                const m = MOCK_TESTS.find(t => t.id === id);

                if (!m) return '';

                const isMed = m.difficulty === 'medium';

                const tierBadge = isMed

                  ? '<span class="q-badge medium" style="padding:2px 8px;font-size:11px">🟡 Medium</span>'

                  : '<span class="q-badge hard" style="padding:2px 8px;font-size:11px">🔴 Hard</span>';

                const rowBg = idx % 2 === 0 ? 'var(--bg-card)' : 'rgba(255,255,255,0.02)';

                return `

                  <tr style="background:${rowBg};border-bottom:1px solid var(--border)">

                    <td style="padding:9px 12px;font-weight:700;white-space:nowrap;color:var(--text-primary)">Mock #${String(num).padStart(2, '0')}</td>

                    <td style="padding:9px 12px;text-align:center">${tierBadge}</td>

                    <td style="padding:9px 12px;text-align:center;font-weight:700;color:var(--yellow)">⭐ ${m.rating ? m.rating.toFixed(1) : ''}/10</td>

                    <td style="padding:9px 12px;text-align:center;color:var(--text-secondary)">${m.cutoff || '28-32'} M</td>

                    <td style="padding:9px 12px;text-align:center;color:var(--text-secondary)">${m.air100 || '72-78'} M</td>

                    <td style="padding:9px 12px;color:var(--text-muted);font-size:11.5px;max-width:320px">${m.desc.split(': ').slice(1).join(': ') || m.desc}</td>

                    <td style="padding:9px 12px;text-align:center;white-space:nowrap">

                      <button class="btn btn-secondary btn-sm" onclick="startMockTest('${m.id}')" style="padding:3px 8px;font-size:11px" type="button">Start Test</button>

                    </td>

                  </tr>

                `;

              }).join('')}

            </tbody>

          </table>

        </div>

      ` : ''}

    </div>

  `;

}



function getFilteredAndSortedMocks(mockList) {

  const currentSort = state.mockSort || 'default';

  const subSeries = state.mockSubSeries || 'all';

  const query = (state.mockSearch || '').trim().toLowerCase();

  let list = (mockList || []).slice();



  // 1. Sub-series filter
  if (subSeries === 'pinned') {
    list = list.filter(m => state.pinnedMocks && state.pinnedMocks.has(m.id));
  } else if (subSeries === 'hard-curated') {
    list = list.filter(m => CURATED_HARD_MOCK_IDS.has(m.id) || (!m.id.startsWith('mock-hard-') && m.difficulty === 'hard' && !m.id.startsWith('mock-subwise-')));
  } else if (subSeries === 'hard-30') {
    list = list.filter(m => m.id.startsWith('mock-hard-'));
  } else if (subSeries === 'med-30') {
    list = list.filter(m => m.id.startsWith('mock-med-'));
  } else if (subSeries === 'easy-30') {
    list = list.filter(m => m.id.startsWith('mock-easy-') && !m.id.startsWith('mock-easy1-'));
  } else if (subSeries === 'easy1-30') {
    list = list.filter(m => m.id.startsWith('mock-easy1-'));
  } else if (subSeries === 'flm-20') {
    list = list.filter(m => m.id.startsWith('mock-flm-'));
  } else if (subSeries === 'cat-10') {
    list = list.filter(m => m.id.startsWith('mock-cat'));
  } else if (subSeries === 'go-mocks') {
    list = list.filter(m => m.id.startsWith('mock-go-') || m.id.startsWith('mock-go25-'));
  } else if (subSeries === 'go-aim') {
    list = list.filter(m => m.id.includes('-aim-'));
  } else if (subSeries === 'go-ts25-mg') {
    list = list.filter(m => m.id.startsWith('mock-go-ts25-mg'));
  } else if (subSeries === 'go25-mg') {
    list = list.filter(m => m.id.startsWith('mock-go25-mg'));
  } else if (subSeries === 'me-mocks') {
    list = list.filter(m => m.id.startsWith('mock-me24-') || m.id.startsWith('mock-me23-'));
  } else if (subSeries === 'me-2024') {
    list = list.filter(m => m.id.startsWith('mock-me24-'));
  } else if (subSeries === 'me-2023') {
    list = list.filter(m => m.id.startsWith('mock-me23-'));
  } else if (subSeries === 'me-adv') {
    list = list.filter(m => m.id.includes('-f-adv'));
  } else if (subSeries === 'me-bsc') {
    list = list.filter(m => m.id.includes('-f-bsc'));
  } else if (subSeries === 'me-aim') {
    list = list.filter(m => m.id.includes('-mock-'));
  } else if (subSeries === 'practice-sets') {
    list = list.filter(m => m.type === 'practice-set');
  }



  // 2. Search query filter

  if (query) {

    list = list.filter(m =>

      (m.name && m.name.toLowerCase().includes(query)) ||

      (m.desc && m.desc.toLowerCase().includes(query)) ||

      (m.tier && m.tier.toLowerCase().includes(query)) ||

      (m.provider && m.provider.toLowerCase().includes(query)) ||

      (m.id && m.id.toLowerCase().includes(query))

    );

  }



  const diffRank = { 'easy': 1, 'medium': 2, 'hard': 3 };



  if (currentSort === 'easy-first') {

    list.sort((a, b) => {

      const da = diffRank[a.difficulty] || 2;

      const db = diffRank[b.difficulty] || 2;

      if (da !== db) return da - db;

      return (a.rating || 5) - (b.rating || 5);

    });

  } else if (currentSort === 'hard-first') {

    list.sort((a, b) => {

      const da = diffRank[a.difficulty] || 2;

      const db = diffRank[b.difficulty] || 2;

      if (da !== db) return db - da;

      return (b.rating || 5) - (a.rating || 5);

    });

  } else if (currentSort === 'rating-desc') {

    list.sort((a, b) => (b.rating || 0) - (a.rating || 0));

  } else if (currentSort === 'rating-asc') {

    list.sort((a, b) => (a.rating || 0) - (b.rating || 0));

  } else if (currentSort === 'name-asc') {

    list.sort((a, b) => a.name.localeCompare(b.name, undefined, { numeric: true, sensitivity: 'base' }));

  }



  return list;

}




function setMockViewMode(mode) {
  state.mockViewMode = mode;
  try { localStorage.setItem('gate_mock_view_mode', mode); } catch(e) {}
  const c = document.getElementById('mock-tab-content');
  if (c) {
    const tab = state.mockTab || 'all';
    const fullMocks = MOCK_TESTS.filter(m => m.type === 'full' || m.type === 'practice-set');
    c.innerHTML = getMockTabHTML(tab, fullMocks);
    renderMath(c);
  }
}

function togglePinMock(mockId, evt) {
  if (evt) evt.stopPropagation();
  if (!state.pinnedMocks) state.pinnedMocks = new Set();
  if (state.pinnedMocks.has(mockId)) {
    state.pinnedMocks.delete(mockId);
    showToast('Mock removed from target list', 'info');
  } else {
    state.pinnedMocks.add(mockId);
    showToast('Mock added to ⭐ Target Mocks!', 'success');
  }
  try {
    localStorage.setItem('gate_pinned_mocks', JSON.stringify([...state.pinnedMocks]));
  } catch(e) {}
  const c = document.getElementById('mock-tab-content');
  if (c) {
    const tab = state.mockTab || 'all';
    const fullMocks = MOCK_TESTS.filter(m => m.type === 'full' || m.type === 'practice-set');
    c.innerHTML = getMockTabHTML(tab, fullMocks);
    renderMath(c);
  }
}

function openMockRetakeCompare(mockId, evt) {
  if (evt) evt.stopPropagation();
  const matchingIndices = [];
  state.testSessions.forEach((s, idx) => {
    if (s.mockId === mockId) matchingIndices.push(idx);
  });
  if (matchingIndices.length < 2) {
    showToast('Complete this mock at least twice to compare retake progress!', 'info');
    return;
  }
  openCompareModal();
  const selectA = document.getElementById('compare-test-a');
  const selectB = document.getElementById('compare-test-b');
  if (selectA && selectB) {
    selectA.value = matchingIndices[0];
    selectB.value = matchingIndices[matchingIndices.length - 1];
    updateComparisonView();
  }
}

function buildMockCompactList(mocks) {
  return `<div class="mock-compact-list">${mocks.map(m => {
    const past = state.testSessions.filter(s => s.mockId === m.id);
    const best = past.length ? Math.max(...past.map(s => s.percentage)) : null;
    const questionsCount = getMockQuestions(m.id).length || m.questions;
    const diffLabel = (m.difficulty || 'medium').toUpperCase();
    const isPinned = state.pinnedMocks && state.pinnedMocks.has(m.id);

    let providerBadge = '';
    const provName = m.provider || (m.tier && m.tier.includes('Comprehensive') ? 'Comprehensive Series' : (m.tier && (m.tier.includes('All-India') || m.tier.includes('National')) ? 'All-India Series' : null));
    if (provName) {
      let icon = provName.includes('Comprehensive') ? '📘' : provName.includes('GO') ? '🌐' : '🏆';
      providerBadge = `<span class="q-badge" style="font-size:10px;padding:2px 6px;font-weight:600">${icon} ${provName}</span>`;
    }

    return `<div class="mock-compact-row" onclick="viewMockPaper('${m.id}')">
      <div class="mock-compact-main">
        <button class="mock-pin-btn ${isPinned ? 'pinned' : 'unpinned'}" onclick="togglePinMock('${m.id}', event)" title="${isPinned ? 'Unpin Mock' : 'Pin to Target Mocks'}" type="button">
          ${isPinned ? '⭐' : '☆'}
        </button>
        <div style="min-width:65px">
          <span class="mock-compact-title">${m.name}</span>
        </div>
        ${providerBadge}
        <span class="q-badge ${m.difficulty || 'medium'}" style="font-size:10px;padding:2px 6px">${diffLabel}${m.rating ? ` ${m.rating.toFixed(1)}/10` : ''}</span>
        <span class="mock-compact-desc" title="${escapeHtml(m.desc)}">${m.desc}</span>
      </div>
      <div class="mock-compact-meta">
        <span>📚 ${questionsCount} Qs</span>
        <span>⏱️ ${m.duration}m</span>
        <span>🏅 ${m.marks} M</span>
        ${best !== null ? `<span style="color:var(--green);font-weight:700">🏆 ${best}%</span>` : ''}
        ${past.length >= 2 ? `<button class="btn btn-secondary btn-sm" onclick="openMockRetakeCompare('${m.id}', event)" title="Compare your ${past.length} attempts" style="font-size:10px;padding:2px 6px" type="button">📊 Retakes (${past.length})</button>` : ''}
      </div>
      <div class="mock-compact-actions" onclick="event.stopPropagation()">
        <button class="btn btn-secondary btn-sm" onclick="viewMockPaper('${m.id}')" style="font-size:11px;padding:4px 8px" type="button">📄 Paper</button>
        <button class="btn btn-primary btn-sm" onclick="startMockTest('${m.id}')" style="font-size:11px;padding:4px 10px" type="button">▶ Start</button>
      </div>
    </div>`;
  }).join('')}</div>`;
}

function setMockSort(sortVal) {

  state.mockSort = sortVal;

  const c = document.getElementById('mock-tab-content');

  if (c) {

    const tab = state.mockTab || 'all';

    const fullMocks = MOCK_TESTS.filter(m => m.type === 'full' || m.type === 'practice-set');

    c.innerHTML = getMockTabHTML(tab, fullMocks);

    renderMath(c);

  }

}



function buildMockLevelFilterBar(fullMocks) {

  const currentLvl = state.mockLevelFilter || 'all';

  const currentSort = state.mockSort || 'default';

  const easyCount = fullMocks.filter(m => m.difficulty === 'easy').length;

  const medCount  = fullMocks.filter(m => m.difficulty === 'medium').length;

  const hardCount = fullMocks.filter(m => m.difficulty === 'hard').length;



  return `

    <div class="filter-bar" style="margin-bottom:16px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px">

      <div style="display:flex;flex-wrap:wrap;gap:8px;align-items:center">

        <button class="chip ${currentLvl === 'all' ? 'active' : ''}" onclick="setMockLevelFilter('all')" type="button">All Levels (${fullMocks.length})</button>

        <button class="chip ${currentLvl === 'easy' ? 'active' : ''}" onclick="setMockLevelFilter('easy')" style="${currentLvl === 'easy' ? 'border-color:var(--green);color:var(--green);background:var(--green-soft)' : ''}" type="button">🟢 Easy / Foundational (${easyCount})</button>

        <button class="chip ${currentLvl === 'medium' ? 'active' : ''}" onclick="setMockLevelFilter('medium')" style="${currentLvl === 'medium' ? 'border-color:var(--yellow);color:var(--yellow);background:var(--yellow-soft)' : ''}" type="button">🟡 Moderate / Standard (${medCount})</button>

        <button class="chip ${currentLvl === 'hard' ? 'active' : ''}" onclick="setMockLevelFilter('hard')" style="${currentLvl === 'hard' ? 'border-color:var(--red);color:var(--red);background:var(--red-soft)' : ''}" type="button">🔴 Hard / Rank Booster (${hardCount})</button>

      </div>



      <div style="display:flex;align-items:center;gap:8px">

        <label style="font-size:12px;color:var(--text-secondary);font-weight:600;white-space:nowrap">Sort by:</label>

        <select class="form-select form-select-sm" style="width:auto;min-width:185px;padding:5px 10px;font-size:12px;background:var(--bg-card);border:1px solid var(--border);border-radius:6px;color:var(--text-primary);cursor:pointer" onchange="setMockSort(this.value)">

          <option value="default" ${currentSort === 'default' ? 'selected' : ''}>Default Order</option>

          <option value="easy-first" ${currentSort === 'easy-first' ? 'selected' : ''}>Difficulty: Easy → Hard</option>

          <option value="hard-first" ${currentSort === 'hard-first' ? 'selected' : ''}>Difficulty: Hard → Easy</option>

          <option value="rating-desc" ${currentSort === 'rating-desc' ? 'selected' : ''}>Rating: High → Low</option>

          <option value="rating-asc" ${currentSort === 'rating-asc' ? 'selected' : ''}>Rating: Low → High</option>

          <option value="name-asc" ${currentSort === 'name-asc' ? 'selected' : ''}>Name: A → Z</option>

        </select>

      </div>

    </div>

  `;

}



function setMockLevelFilter(lvl) {

  state.mockLevelFilter = lvl;

  const c = document.getElementById('mock-tab-content');

  if (c && state.mockTab === 'full') {

    const fullMocks = MOCK_TESTS.filter(m => m.type === 'full');

    const filtered = getFilteredAndSortedMocks(fullMocks);

    c.innerHTML = `

      ${buildMockCalibrationGuide()}

      ${buildMockLevelFilterBar(fullMocks)}

      ${buildMockGrid(filtered)}

    `;

    renderMath(c);

  }

}



function renderMocks(c, params={}){

  if (state.activeMockPaper) {

    renderMockPaperView(c);

    return;

  }

  const activeTab = params.tab || state.mockTab || 'all';
  if (params.subSeries) {
    state.mockSubSeries = params.subSeries;
  } else if (params.tab && params.tab !== state.mockTab) {
    state.mockSubSeries = 'all';
  }
  state.mockTab = activeTab;



  const fullMocks = MOCK_TESTS.filter(m => m.type === 'full' || m.type === 'practice-set');

  const easyCount = fullMocks.filter(m => m.difficulty === 'easy').length;

  const medCount  = fullMocks.filter(m => m.difficulty === 'medium').length;

  const hardCount = fullMocks.filter(m => m.difficulty === 'hard').length;

  const psetsCount = MOCK_TESTS.filter(m => m.type === 'practice-set').length;
  const goCount = fullMocks.filter(m => m.id.startsWith('mock-go-') || m.id.startsWith('mock-go25-')).length;
  const meCount = fullMocks.filter(m => m.id.startsWith('mock-me24-') || m.id.startsWith('mock-me23-')).length;



  c.innerHTML = `

    <div class="tabs" id="mock-tabs">
      <button class="tab-btn ${activeTab==='all'?'active':''}" onclick="switchMockTab('all',this)" type="button">📋 All (${fullMocks.length})</button>
      <button class="tab-btn ${activeTab==='easy'?'active':''}" onclick="switchMockTab('easy',this)" type="button">🟢 Easy (${easyCount})</button>
      <button class="tab-btn ${activeTab==='medium'?'active':''}" onclick="switchMockTab('medium',this)" type="button">🟡 Medium (${medCount})</button>
      <button class="tab-btn ${activeTab==='hard'?'active':''}" onclick="switchMockTab('hard',this)" type="button">🔴 Hard (${hardCount})</button>
      <button class="tab-btn ${activeTab==='go'?'active':''}" onclick="switchMockTab('go',this)" type="button">🌐 National All-India Mocks (${goCount})</button>
      <button class="tab-btn ${activeTab==='comprehensive-mocks'?'active':''}" onclick="switchMockTab('comprehensive-mocks',this)" type="button">📘 Comprehensive Mocks (${meCount})</button>
      <button class="tab-btn ${activeTab==='practice-sets'?'active':''}" onclick="switchMockTab('practice-sets',this)" type="button">📝 Practice Sets (${psetsCount})</button>
      <button class="tab-btn ${activeTab==='subwise'?'active':''}" onclick="navigate('subject-tests')" type="button">🧪 Subject Tests (126)</button>
      <button class="tab-btn ${activeTab==='history'?'active':''}" onclick="switchMockTab('history',this)" type="button">📊 My History</button>
    </div>
    <div id="mock-tab-content">

      ${getMockTabHTML(activeTab, fullMocks)}

    </div>
    <div class="subject-tests-callout-banner" style="margin-top:28px;background:linear-gradient(135deg,rgba(108,99,255,0.12),rgba(168,85,247,0.08));border:1px solid rgba(108,99,255,0.25);border-radius:var(--radius);padding:20px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:14px">
      <div>
        <div style="font-weight:700;font-size:16px;color:var(--text-primary);display:flex;align-items:center;gap:8px">
          <span>🧪 Looking for Subject-Wise Tests?</span>
          <span class="q-badge" style="background:rgba(108,99,255,0.2);color:var(--accent);font-weight:700">126 Full Tests</span>
        </div>
        <div style="font-size:13px;color:var(--text-secondary);margin-top:4px">
          Practice 126 calibrated tests covering all GATE CS subjects including 100 comprehensive tests across Discrete Mathematics and Engineering Mathematics under timed simulation.
        </div>
      </div>
      <button class="btn btn-primary" onclick="navigate('subject-tests')" type="button">Explore Subject Tests →</button>
    </div>`;

  renderMath(c);

}



function getMockTabHTML(tab, fullMocks) {

  if (tab === 'all') {

    const filtered = getFilteredAndSortedMocks(fullMocks);

    return `${buildMockCalibrationGuide()}${buildMockSortBar(fullMocks, 'All Mocks')}${buildMockGrid(filtered)}`;

  }

  if (tab === 'easy') {

    const list = fullMocks.filter(m => m.difficulty === 'easy');

    const filtered = getFilteredAndSortedMocks(list);

    return `${buildMockCalibrationGuide()}${buildMockSortBar(list, 'Easy / Foundational')}${buildMockGrid(filtered)}`;

  }

  if (tab === 'medium') {

    const list = fullMocks.filter(m => m.difficulty === 'medium');

    const filtered = getFilteredAndSortedMocks(list);

    return `${buildMockCalibrationGuide()}${buildMockSortBar(list, 'Moderate / Standard')}${buildMockGrid(filtered)}`;

  }

  if (tab === 'hard') {

    const list = fullMocks.filter(m => m.difficulty === 'hard');

    const filtered = getFilteredAndSortedMocks(list);

    return `${buildMockCalibrationGuide()}${buildMockSortBar(list, 'Hard / Rank Booster')}${buildMockGrid(filtered)}`;

  }

    if (tab === 'go') {
    const list = fullMocks.filter(m => m.id.startsWith('mock-go-') || m.id.startsWith('mock-go25-'));
    const filtered = getFilteredAndSortedMocks(list);
    return `${buildMockCalibrationGuide()}${buildMockSortBar(list, 'All-India National Mocks')}${buildMockGrid(filtered)}`;
  }
  if (tab === 'comprehensive-mocks') {
    const list = fullMocks.filter(m => m.id.startsWith('mock-me24-') || m.id.startsWith('mock-me23-'));
    const filtered = getFilteredAndSortedMocks(list);
    return `${buildMockCalibrationGuide()}${buildMockSortBar(list, 'Comprehensive Full Syllabus Mocks')}${buildMockGrid(filtered)}`;
  }
  if (tab === 'practice-sets') {

    const list = MOCK_TESTS.filter(m => m.type === 'practice-set');

    return `${buildMockSortBar(list, 'Curated Practice Sets')}${buildMockGrid(list)}`;

  }

  if (tab === 'subwise') {

    return buildMockGrid(MOCK_TESTS.filter(m => m.type === 'subwise'));

  }

  if (tab === 'history') {

    return buildTestHistory();

  }

  return buildMockGrid(fullMocks);

}



function switchMockTab(tab, btn){
  if (state.mockTab !== tab) {
    state.mockSubSeries = 'all';
  }
  state.mockTab = tab;

  document.querySelectorAll('#mock-tabs .tab-btn').forEach(b => {

    const isTarget = btn ? (b === btn) : (b.getAttribute('onclick') || '').includes(`'${tab}'`);

    b.classList.toggle('active', !!isTarget);

  });

  const c = document.getElementById('mock-tab-content');

  if (!c) return;

  const fullMocks = MOCK_TESTS.filter(m => m.type === 'full' || m.type === 'practice-set');

  c.innerHTML = getMockTabHTML(tab, fullMocks);

  renderMath(c);

}



function buildMockSortBar(list, sectionName) {

  const currentSort = state.mockSort || 'default';

  const subSeries = state.mockSubSeries || 'all';

  const currentTab = state.mockTab || 'all';



  let pillsHtml = '';
  if (currentTab === 'medium') {
    pillsHtml = `
      <div class="mock-subseries-pills">
        <span style="font-size:11px;font-weight:700;color:var(--text-muted);text-transform:uppercase">Series:</span>
        <button class="mock-subseries-pill ${subSeries==='all'?'active':''}" onclick="setMockSubSeries('all')">All Medium (${list.length})</button>
        <button class="mock-subseries-pill ${subSeries==='pinned'?'active':''}" onclick="setMockSubSeries('pinned')">⭐ Target Mocks (${(state.pinnedMocks||new Set()).size})</button>
        <button class="mock-subseries-pill ${subSeries==='go-mocks'?'active':''}" onclick="setMockSubSeries('go-mocks')">🌐 All-India National Mocks</button>
        <button class="mock-subseries-pill ${subSeries==='me-mocks'?'active':''}" onclick="setMockSubSeries('me-mocks')">📘 Comprehensive Basic & Mocks</button>
        <button class="mock-subseries-pill ${subSeries==='med-30'?'active':''}" onclick="setMockSubSeries('med-30')">⚡ 30 Medium Series (30)</button>
        <button class="mock-subseries-pill ${subSeries==='flm-20'?'active':''}" onclick="setMockSubSeries('flm-20')">🏆 Compendium Mocks (10)</button>
        <button class="mock-subseries-pill ${subSeries==='cat-10'?'active':''}" onclick="setMockSubSeries('cat-10')">📚 Category Core CS (5)</button>
      </div>`;
  } else if (currentTab === 'hard') {
    pillsHtml = `
      <div class="mock-subseries-pills">
        <span style="font-size:11px;font-weight:700;color:var(--text-muted);text-transform:uppercase">Series:</span>
        <button class="mock-subseries-pill ${subSeries==='all'?'active':''}" onclick="setMockSubSeries('all')">All Hard (${list.length})</button>
        <button class="mock-subseries-pill ${subSeries==='hard-curated'?'active':''}" onclick="setMockSubSeries('hard-curated')">🔴 32 Hard Mocks Series (32)</button>
        <button class="mock-subseries-pill ${subSeries==='hard-30'?'active':''}" onclick="setMockSubSeries('hard-30')">🔥 30 Extreme Hard Series (30)</button>
        <button class="mock-subseries-pill ${subSeries==='pinned'?'active':''}" onclick="setMockSubSeries('pinned')">⭐ Target Mocks (${(state.pinnedMocks||new Set()).size})</button>
        <button class="mock-subseries-pill ${subSeries==='me-mocks'?'active':''}" onclick="setMockSubSeries('me-mocks')">📘 Comprehensive Advance (9)</button>
        <button class="mock-subseries-pill ${subSeries==='go-mocks'?'active':''}" onclick="setMockSubSeries('go-mocks')">🌐 All-India Series (10)</button>
        <button class="mock-subseries-pill ${subSeries==='flm-20'?'active':''}" onclick="setMockSubSeries('flm-20')">🏆 Compendium Hard Mocks (10)</button>
      </div>`;
  } else if (currentTab === 'easy') {
    pillsHtml = `
      <div class="mock-subseries-pills">
        <span style="font-size:11px;font-weight:700;color:var(--text-muted);text-transform:uppercase">Series:</span>
        <button class="mock-subseries-pill ${subSeries==='all'?'active':''}" onclick="setMockSubSeries('all')">All Easy (${list.length})</button>
        <button class="mock-subseries-pill ${subSeries==='pinned'?'active':''}" onclick="setMockSubSeries('pinned')">⭐ Target Mocks (${(state.pinnedMocks||new Set()).size})</button>
        <button class="mock-subseries-pill ${subSeries==='me-mocks'?'active':''}" onclick="setMockSubSeries('me-mocks')">📘 Comprehensive Basic (1)</button>
        <button class="mock-subseries-pill ${subSeries==='easy-30'?'active':''}" onclick="setMockSubSeries('easy-30')">🌟 30 Easy Series (Set 1) (30)</button>
        <button class="mock-subseries-pill ${subSeries==='easy1-30'?'active':''}" onclick="setMockSubSeries('easy1-30')">✨ 30 Easy Series (Set 2) (30)</button>
        <button class="mock-subseries-pill ${subSeries==='cat-10'?'active':''}" onclick="setMockSubSeries('cat-10')">📚 Category Topic Sets (5)</button>
      </div>`;
  } else if (currentTab === 'go') {
    pillsHtml = `
      <div class="mock-subseries-pills">
        <span style="font-size:11px;font-weight:700;color:var(--text-muted);text-transform:uppercase">Series:</span>
        <button class="mock-subseries-pill ${subSeries==='all'?'active':''}" onclick="setMockSubSeries('all')">All National Mocks (${list.length})</button>
        <button class="mock-subseries-pill ${subSeries==='pinned'?'active':''}" onclick="setMockSubSeries('pinned')">⭐ Target Mocks (${(state.pinnedMocks||new Set()).size})</button>
        <button class="mock-subseries-pill ${subSeries==='go-aim'?'active':''}" onclick="setMockSubSeries('go-aim')">🎯 National Mock AIM (11)</button>
        <button class="mock-subseries-pill ${subSeries==='go-ts25-mg'?'active':''}" onclick="setMockSubSeries('go-ts25-mg')">⚡ Full Mock GATE (10)</button>
        <button class="mock-subseries-pill ${subSeries==='go25-mg'?'active':''}" onclick="setMockSubSeries('go25-mg')">🌐 National Series (6)</button>
      </div>`;
  } else if (currentTab === 'comprehensive-mocks') {
    pillsHtml = `
      <div class="mock-subseries-pills">
        <span style="font-size:11px;font-weight:700;color:var(--text-muted);text-transform:uppercase">Series:</span>
        <button class="mock-subseries-pill ${subSeries==='all'?'active':''}" onclick="setMockSubSeries('all')">All Comprehensive Mocks (${list.length})</button>
        <button class="mock-subseries-pill ${subSeries==='pinned'?'active':''}" onclick="setMockSubSeries('pinned')">⭐ Target Mocks (${(state.pinnedMocks||new Set()).size})</button>
        <button class="mock-subseries-pill ${subSeries==='me-2024'?'active':''}" onclick="setMockSubSeries('me-2024')">📘 2024 Series (10)</button>
        <button class="mock-subseries-pill ${subSeries==='me-2023'?'active':''}" onclick="setMockSubSeries('me-2023')">📙 2023 Series (11)</button>
        <button class="mock-subseries-pill ${subSeries==='me-adv'?'active':''}" onclick="setMockSubSeries('me-adv')">🔴 Advance Level (8)</button>
        <button class="mock-subseries-pill ${subSeries==='me-bsc'?'active':''}" onclick="setMockSubSeries('me-bsc')">🟡 Basic Level (8)</button>
        <button class="mock-subseries-pill ${subSeries==='me-aim'?'active':''}" onclick="setMockSubSeries('me-aim')">🏆 National Mocks (5)</button>
      </div>`;
  } else if (currentTab === 'all') {
    pillsHtml = `
      <div class="mock-subseries-pills">
        <span style="font-size:11px;font-weight:700;color:var(--text-muted);text-transform:uppercase">Series:</span>
        <button class="mock-subseries-pill ${subSeries==='all'?'active':''}" onclick="setMockSubSeries('all')">All (${list.length})</button>
        <button class="mock-subseries-pill ${subSeries==='pinned'?'active':''}" onclick="setMockSubSeries('pinned')">⭐ Target Mocks (${(state.pinnedMocks||new Set()).size})</button>
        <button class="mock-subseries-pill ${subSeries==='go-mocks'?'active':''}" onclick="setMockSubSeries('go-mocks')">🌐 All-India National Mocks (27)</button>
        <button class="mock-subseries-pill ${subSeries==='me-mocks'?'active':''}" onclick="setMockSubSeries('me-mocks')">📘 Comprehensive Mocks (21)</button>
        <button class="mock-subseries-pill ${subSeries==='hard-30'?'active':''}" onclick="setMockSubSeries('hard-30')">🔥 30 Extreme Hard Series</button>
        <button class="mock-subseries-pill ${subSeries==='med-30'?'active':''}" onclick="setMockSubSeries('med-30')">⚡ 30 Medium Series</button>
        <button class="mock-subseries-pill ${subSeries==='easy-30'?'active':''}" onclick="setMockSubSeries('easy-30')">🌟 30 Easy Series (Set 1)</button>
        <button class="mock-subseries-pill ${subSeries==='easy1-30'?'active':''}" onclick="setMockSubSeries('easy1-30')">✨ 30 Easy Series (Set 2)</button>
        <button class="mock-subseries-pill ${subSeries==='flm-20'?'active':''}" onclick="setMockSubSeries('flm-20')">🏆 20 Compendium Mocks</button>
        <button class="mock-subseries-pill ${subSeries==='cat-10'?'active':''}" onclick="setMockSubSeries('cat-10')">📚 Category Mocks</button>
      </div>`;
  }

  return `
    <div class="mock-controls-bar">

      <div class="mock-controls-top">

        <div class="mock-search-box">

          <span class="search-icon">🔍</span>

          <input type="text" class="search-input" placeholder="Search mock tests by name, rating, #..."

            value="${escapeHtml(state.mockSearch || '')}"

            oninput="updateMockSearch(this.value)" />

        </div>

        <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap">

          <div class="btn-group" style="display:inline-flex;border:1px solid var(--border);border-radius:6px;overflow:hidden">
            <button class="btn btn-sm ${state.mockViewMode==='compact'?'btn-secondary':'btn-primary'}" style="padding:4px 9px;font-size:12px" onclick="setMockViewMode('grid')" title="Detailed Grid View" type="button">⊞ Grid</button>
            <button class="btn btn-sm ${state.mockViewMode==='compact'?'btn-primary':'btn-secondary'}" style="padding:4px 9px;font-size:12px" onclick="setMockViewMode('compact')" title="Compact List View" type="button">☰ List</button>
          </div>

          <label style="font-size:12px;color:var(--text-secondary);font-weight:600;white-space:nowrap">Sort by:</label>

          <select class="form-select form-select-sm" style="width:auto;min-width:180px;padding:6px 10px;font-size:12px;background:var(--bg-input);border:1px solid var(--border);border-radius:6px;color:var(--text-primary);cursor:pointer" onchange="setMockSort(this.value)">

            <option value="default" ${currentSort === 'default' ? 'selected' : ''}>Default Order</option>

            <option value="easy-first" ${currentSort === 'easy-first' ? 'selected' : ''}>Difficulty: Easy → Hard</option>

            <option value="hard-first" ${currentSort === 'hard-first' ? 'selected' : ''}>Difficulty: Hard → Easy</option>

            <option value="rating-desc" ${currentSort === 'rating-desc' ? 'selected' : ''}>Rating: High → Low</option>

            <option value="rating-asc" ${currentSort === 'rating-asc' ? 'selected' : ''}>Rating: Low → High</option>

            <option value="name-asc" ${currentSort === 'name-asc' ? 'selected' : ''}>Name: A → Z</option>

          </select>

        </div>

      </div>

      ${pillsHtml}

    </div>

  `;

}



function updateMockSearch(val) {

  state.mockSearch = val;

  const c = document.getElementById('mock-tab-content');

  if (c) {

    const tab = state.mockTab || 'all';

    const fullMocks = MOCK_TESTS.filter(m => m.type === 'full' || m.type === 'practice-set');

    c.innerHTML = getMockTabHTML(tab, fullMocks);

    renderMath(c);

  }

}



function setMockSubSeries(sub) {

  state.mockSubSeries = sub;

  const c = document.getElementById('mock-tab-content');

  if (c) {

    const tab = state.mockTab || 'all';

    const fullMocks = MOCK_TESTS.filter(m => m.type === 'full' || m.type === 'practice-set');

    c.innerHTML = getMockTabHTML(tab, fullMocks);

    renderMath(c);

  }

}



function buildMockGrid(mocks){
  if (!mocks.length) return '<div class="empty-state"><div class="empty-state-icon">📭</div><div class="empty-state-title">No tests available for selected filter</div><div class="empty-state-sub">Try selecting "All" or another tab.</div></div>';

  if (state.mockViewMode === 'compact') {
    return buildMockCompactList(mocks);
  }

  return `<div class="mock-grid">${mocks.map(m=>{
    const past = state.testSessions.filter(s => s.mockId === m.id);
    const best = past.length ? Math.max(...past.map(s => s.percentage)) : null;
    const questionsCount = getMockQuestions(m.id).length || m.questions;
    const totalPages = Math.ceil(questionsCount / 20) || 1;
    const diffLabel = m.difficulty ? m.difficulty.toUpperCase() : 'MEDIUM';
    const ratingBadge = m.rating ? `<span class="q-badge" style="background:rgba(245,158,11,0.14);color:#f59e0b;border:1px solid rgba(245,158,11,0.3);font-weight:700">⭐ ${m.rating.toFixed(1)}/10</span>` : '';
    const targetsRow = (m.cutoff && m.air100) ? `
      <div class="mock-targets-banner">
        <span>🎯 <strong>Cutoff:</strong> ${m.cutoff} M</span>
        <span>🏆 <strong>AIR &lt; 100:</strong> ${m.air100} M</span>
      </div>` : '';
    const badgeType = m.type === 'practice-set' ? '📝 Practice Set' : m.type === 'full' ? '🏆 Full Mock' : '📂 Subject Mock';

    let providerBadge = '';
    const provName = m.provider || (m.tier && m.tier.includes('Comprehensive') ? 'Comprehensive Series' : (m.tier && (m.tier.includes('All-India') || m.tier.includes('National')) ? 'All-India Series' : null));
    if (provName) {
      let style = 'background:rgba(100,116,139,0.12);color:#64748b;border:1px solid rgba(100,116,139,0.3);';
      let icon = '📚';
      if (provName.includes('Comprehensive')) {
        style = 'background:rgba(59,130,246,0.14);color:#3b82f6;border:1px solid rgba(59,130,246,0.35);';
        icon = '📘';
      } else if (provName.includes('All-India')) {
        style = 'background:rgba(16,185,129,0.14);color:#10b981;border:1px solid rgba(16,185,129,0.35);';
        icon = '🌐';
      } else if (provName.includes('National')) {
        style = 'background:rgba(20,184,166,0.14);color:#14b8a6;border:1px solid rgba(20,184,166,0.35);';
        icon = '🌐';
      } else if (provName.includes('Official')) {
        style = 'background:rgba(239,68,68,0.14);color:#ef4444;border:1px solid rgba(239,68,68,0.35);';
        icon = '🏛️';
      } else if (provName.includes('Compendium')) {
        style = 'background:rgba(168,85,247,0.14);color:#a855f7;border:1px solid rgba(168,85,247,0.35);';
        icon = '🏆';
      } else if (provName.includes('Standard Series')) {
        style = 'background:rgba(245,158,11,0.14);color:#f59e0b;border:1px solid rgba(245,158,11,0.35);';
        icon = '⚡';
      } else if (provName.includes('Easy Series')) {
        style = 'background:rgba(34,197,94,0.14);color:#22c55e;border:1px solid rgba(34,197,94,0.35);';
        icon = '🌟';
      } else if (provName.includes('Category')) {
        style = 'background:rgba(99,102,241,0.14);color:#6366f1;border:1px solid rgba(99,102,241,0.35);';
        icon = '📚';
      }
      providerBadge = `<span class="q-badge" style="${style}font-weight:700">${icon} ${provName}</span>`;
    }

    return `<div class="mock-card">
      <div>
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;flex-wrap:wrap;gap:6px">
          <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap">
            <div class="mock-type-badge ${m.type}">${badgeType}</div>
            ${providerBadge}
          </div>
          <div style="display:flex;align-items:center;gap:6px">
            <button class="mock-pin-btn ${state.pinnedMocks && state.pinnedMocks.has(m.id) ? 'pinned' : 'unpinned'}" onclick="togglePinMock('${m.id}', event)" title="${state.pinnedMocks && state.pinnedMocks.has(m.id) ? 'Unpin Mock' : 'Pin to Target Mocks'}" type="button">
              ${state.pinnedMocks && state.pinnedMocks.has(m.id) ? '⭐' : '☆'}
            </button>
            <span class="q-badge ${m.difficulty || 'medium'}">${diffLabel}</span>
            ${ratingBadge}
          </div>
        </div>
        <div class="mock-title">${m.name}</div>
        <div class="text-sm text-muted" style="margin-bottom:8px;line-height:1.5">${m.desc}</div>
        ${targetsRow}
        <div class="mock-meta">
          <div class="mock-meta-item">📚 ${questionsCount} Questions</div>
          <div class="mock-meta-item">⏱️ ${m.duration} Min</div>
          <div class="mock-meta-item">🏅 ${m.marks} Marks</div>
          ${best !== null ? `<div class="mock-meta-item" style="color:var(--green);font-weight:600">🏆 Best: ${best}%</div>` : ''}
          ${past.length >= 2 ? `<button class="btn btn-secondary btn-sm" onclick="openMockRetakeCompare('${m.id}', event)" title="Compare your ${past.length} attempts" style="font-size:11px;padding:2px 7px;margin-left:4px" type="button">📊 Retakes (${past.length})</button>` : ''}
        </div>
      </div>
      <div class="mock-card-actions">
        <button class="btn btn-secondary btn-sm" onclick="viewMockPaper('${m.id}')" title="Browse questions in sets of 20 per page with solutions" type="button">📖 Practice Paper (20/page)</button>
        <button class="btn btn-primary btn-sm" onclick="startMockTest('${m.id}')" title="Start timed exam simulation" type="button">▶ Timed Exam</button>
      </div>
      ${past.length ? `<div class="text-sm text-muted mt-2">Attempted ${past.length} time${past.length > 1 ? 's' : ''}</div>` : ''}
    </div>`;
  }).join('')}</div>`;
}



// ─── FULL-LENGTH PREVIOUS YEAR EXAMS (PYQ EXAMS SECTION) ────────────────────

function renderPyqExams(c) {

  if (state.activeMockPaper) {

    renderMockPaperView(c);

    return;

  }

  const filteredExams = getFilteredAndSortedPyqExams();

  c.innerHTML = `

    <div class="section-header">

      <div class="section-title">Full-Length PYQ Exams <span>${FULL_LENGTH_PYQ_EXAMS.length} Official Papers</span></div>

    </div>

    <p class="text-muted text-sm" style="margin-bottom:14px">

      Take official, full-length year-wise Previous Year Question papers in a realistic 180-minute timed exam environment. Includes countdown timer, virtual calculator, TCS iON palette, and instant score analysis.

    </p>

    ${buildPyqExamsFilterBar()}

    ${buildPyqExamsGrid(filteredExams)}

  `;

  renderMath(c);

}



function getFilteredAndSortedPyqExams() {

  const era = state.pyqExamEraFilter || 'all';

  const diff = state.pyqExamDiffFilter || 'all';

  const sort = state.pyqExamSort || 'year-desc';



  let list = FULL_LENGTH_PYQ_EXAMS.slice();



  // 1. Era filter

  if (era === 'recent') {

    list = list.filter(e => typeof e.year === 'number' && e.year >= 2020);

  } else if (era === 'decade') {

    list = list.filter(e => (typeof e.year === 'number' && e.year >= 2014 && e.year <= 2019) || e.id.includes('decade'));

  } else if (era === 'classic') {

    list = list.filter(e => typeof e.year === 'number' && e.year <= 2013);

  }



  // 2. Difficulty filter

  if (diff !== 'all') {

    list = list.filter(e => e.difficulty === diff);

  }



  // 3. Sort

  const diffRank = { 'easy': 1, 'medium': 2, 'hard': 3 };

  if (sort === 'year-desc') {

    list.sort((a, b) => {

      const ya = typeof a.year === 'number' ? a.year : 2024;

      const yb = typeof b.year === 'number' ? b.year : 2024;

      if (yb !== ya) return yb - ya;

      return a.name.localeCompare(b.name);

    });

  } else if (sort === 'year-asc') {

    list.sort((a, b) => {

      const ya = typeof a.year === 'number' ? a.year : 2024;

      const yb = typeof b.year === 'number' ? b.year : 2024;

      if (ya !== yb) return ya - yb;

      return a.name.localeCompare(b.name);

    });

  } else if (sort === 'difficulty-asc') {

    list.sort((a, b) => (diffRank[a.difficulty] || 2) - (diffRank[b.difficulty] || 2));

  } else if (sort === 'difficulty-desc') {

    list.sort((a, b) => (diffRank[b.difficulty] || 2) - (diffRank[a.difficulty] || 2));

  } else if (sort === 'rating-desc') {

    list.sort((a, b) => (b.rating || 0) - (a.rating || 0));

  }



  return list;

}



function setPyqExamEraFilter(era) {

  state.pyqExamEraFilter = era;

  const c = document.getElementById('page-content');

  if (c && state.currentPage === 'pyq-exams') renderPyqExams(c);

}



function setPyqExamDiffFilter(diff) {

  state.pyqExamDiffFilter = diff;

  const c = document.getElementById('page-content');

  if (c && state.currentPage === 'pyq-exams') renderPyqExams(c);

}



function setPyqExamSort(sortVal) {

  state.pyqExamSort = sortVal;

  const c = document.getElementById('page-content');

  if (c && state.currentPage === 'pyq-exams') renderPyqExams(c);

}



function buildPyqExamsFilterBar() {

  const currentEra = state.pyqExamEraFilter || 'all';

  const currentDiff = state.pyqExamDiffFilter || 'all';

  const currentSort = state.pyqExamSort || 'year-desc';



  return `

    <div class="filter-bar" style="margin-bottom:16px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px">

      <div style="display:flex;flex-wrap:wrap;gap:8px;align-items:center">

        <button class="chip ${currentEra === 'all' ? 'active' : ''}" onclick="setPyqExamEraFilter('all')" type="button">

          All Years (${FULL_LENGTH_PYQ_EXAMS.length})

        </button>

        <button class="chip ${currentEra === 'recent' ? 'active' : ''}" onclick="setPyqExamEraFilter('recent')" type="button">

          🔥 Recent (2020–2026)

        </button>

        <button class="chip ${currentEra === 'decade' ? 'active' : ''}" onclick="setPyqExamEraFilter('decade')" type="button">

          📅 Past Decade (2014–2019)

        </button>

        <button class="chip ${currentEra === 'classic' ? 'active' : ''}" onclick="setPyqExamEraFilter('classic')" type="button">

          🏛️ Classic (2011–2013)

        </button>

      </div>



      <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">

        <div style="display:flex;align-items:center;gap:6px">

          <label style="font-size:12px;color:var(--text-secondary);font-weight:600">Difficulty:</label>

          <select class="form-select form-select-sm" style="width:auto;padding:5px 10px;font-size:12px;background:var(--bg-card);border:1px solid var(--border);border-radius:6px;color:var(--text-primary);cursor:pointer" onchange="setPyqExamDiffFilter(this.value)">

            <option value="all" ${currentDiff === 'all' ? 'selected' : ''}>All Difficulties</option>

            <option value="easy" ${currentDiff === 'easy' ? 'selected' : ''}>🟢 Easy</option>

            <option value="medium" ${currentDiff === 'medium' ? 'selected' : ''}>🟡 Medium</option>

            <option value="hard" ${currentDiff === 'hard' ? 'selected' : ''}>🔴 Hard</option>

          </select>

        </div>



        <div style="display:flex;align-items:center;gap:6px">

          <label style="font-size:12px;color:var(--text-secondary);font-weight:600">Sort:</label>

          <select class="form-select form-select-sm" style="width:auto;padding:5px 10px;font-size:12px;background:var(--bg-card);border:1px solid var(--border);border-radius:6px;color:var(--text-primary);cursor:pointer" onchange="setPyqExamSort(this.value)">

            <option value="year-desc" ${currentSort === 'year-desc' ? 'selected' : ''}>Year: Newest → Oldest</option>

            <option value="year-asc" ${currentSort === 'year-asc' ? 'selected' : ''}>Year: Oldest → Newest</option>

            <option value="difficulty-asc" ${currentSort === 'difficulty-asc' ? 'selected' : ''}>Difficulty: Easy → Hard</option>

            <option value="difficulty-desc" ${currentSort === 'difficulty-desc' ? 'selected' : ''}>Difficulty: Hard → Easy</option>

            <option value="rating-desc" ${currentSort === 'rating-desc' ? 'selected' : ''}>Rating: High → Low</option>

          </select>

        </div>

      </div>

    </div>

  `;

}



function buildPyqExamsGrid(exams) {

  if (!exams.length) {

    return '<div class="empty-state"><div class="empty-state-icon">📭</div><div class="empty-state-title">No PYQ exams match your filter</div><div class="empty-state-sub">Try selecting "All Years" or "All Difficulties".</div></div>';

  }

  return `<div class="mock-grid">${exams.map(exam => {

    const past = state.testSessions.filter(s => s.mockId === exam.id);

    const best = past.length ? Math.max(...past.map(s => s.percentage)) : null;

    const diffLabel = (exam.difficulty || 'medium').toUpperCase();

    const ratingBadge = exam.rating ? `<span class="q-badge" style="background:rgba(245,158,11,0.14);color:#f59e0b;border:1px solid rgba(245,158,11,0.3);font-weight:700">⭐ ${exam.rating.toFixed(1)}/10</span>` : '';

    const targetsRow = (exam.cutoff && exam.air100) ? `

      <div class="mock-targets-banner">

        <span>🎯 <strong>Cutoff:</strong> ${exam.cutoff} M</span>

        <span>🏆 <strong>AIR &lt; 100:</strong> ${exam.air100} M</span>

      </div>` : '';

    return `

      <div class="mock-card">

        <div>

          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px">

            <div class="mock-type-badge full">📅 GATE ${exam.year} ${exam.set ? '• ' + exam.set : ''}</div>

            <div style="display:flex;align-items:center;gap:6px">

              <span class="q-badge ${exam.difficulty || 'medium'}">${diffLabel}</span>

              ${ratingBadge}

            </div>

          </div>

          <div class="mock-title">${exam.name}</div>

          <div style="font-size:12px;font-weight:600;color:var(--accent);margin-bottom:6px">🏛️ ${exam.institute || 'Official GATE Exam'}</div>

          <div class="text-sm text-muted" style="margin-bottom:8px">${exam.desc}</div>

          ${targetsRow}

          <div class="mock-meta">

            <div class="mock-meta-item">📚 ${exam.questions || 65} Questions</div>

            <div class="mock-meta-item">⏱️ ${exam.duration || 180} Min</div>

            <div class="mock-meta-item">🏅 ${exam.marks || 100} Marks</div>

            ${best !== null ? `<div class="mock-meta-item" style="color:var(--green);font-weight:600">🏆 Best: ${best}%</div>` : ''}

          </div>

        </div>

        <div class="mock-card-actions">

          <button class="btn btn-primary btn-sm" onclick="startMockTest('${exam.id}')" title="Start 180-min official timed exam" type="button">▶ Start Timed Exam</button>

          <button class="btn btn-secondary btn-sm" onclick="viewMockPaper('${exam.id}')" title="Browse questions in sets of 20 per page with solutions" type="button">📖 Review Paper (20/page)</button>

        </div>

        ${past.length ? `<div class="text-sm text-muted mt-2">Attempted ${past.length} time${past.length > 1 ? 's' : ''}</div>` : ''}

      </div>

    `;

  }).join('')}</div>`;

}



function renderPracticePapers(c){

  renderMocks(c, { tab: 'practice-sets' });

}



function buildPracticePapersSection() {

  const psets = MOCK_TESTS.filter(m => m.type === 'practice-set');

  return `

    <div style="margin-bottom:14px;color:var(--text-secondary);font-size:13px">

      Curated multi-subject practice sets and comprehensive test papers with full solutions.

    </div>

    ${buildMockGrid(psets)}

  `;

}

// ─── SUBJECT-WISE TESTS SECTION ───────────────────────────────────────────

function renderSubjectTests(c, params={}) {
  if (state.activeMockPaper) {
    renderMockPaperView(c);
    return;
  }

  const selectedSubject = params.subject || state.subjectTestFilter || 'all';
  const selectedDiff = state.subjectTestDiffFilter || 'all';
  const selectedLevel = state.subjectTestLevelFilter || 'all';
  const search = (state.subjectTestSearch || '').trim().toLowerCase();

  state.subjectTestFilter = selectedSubject;

  const allSubTests = MOCK_TESTS.filter(m => m.type === 'subwise');

  let filtered = allSubTests.slice();
  if (selectedSubject !== 'all') {
    filtered = filtered.filter(m => m.subject === selectedSubject);
  }
  if (selectedDiff !== 'all') {
    filtered = filtered.filter(m => m.difficulty === selectedDiff);
  }
  if (selectedLevel !== 'all') {
    filtered = filtered.filter(m => (m.level || 'Foundational') === selectedLevel);
  }
  if (search) {
    filtered = filtered.filter(m =>
      (m.name || '').toLowerCase().includes(search) ||
      (m.subject || '').toLowerCase().includes(search) ||
      (m.desc || '').toLowerCase().includes(search) ||
      (m.stage || '').toLowerCase().includes(search)
    );
  }

  const uniqueSubjects = [
    'Operating Systems', 'Algorithms', 'Computer Networks', 'DBMS',
    'Theory of Computation', 'Computer Organization', 'Data Structures',
    'Digital Logic', 'Discrete Mathematics', 'Engineering Mathematics',
    'Compiler Design', 'C Programming', 'Aptitude'
  ];

  const totalSubQuestions = allSubTests.reduce((sum, m) => sum + (m.questions || 0), 0);

  c.innerHTML = `
    <div class="section-header">
      <div class="section-title">🧪 Subject-Wise Tests <span>${allSubTests.length} Calibrated Tests • 13 Core Subjects (${totalSubQuestions.toLocaleString()} Questions)</span></div>
      <button class="btn btn-secondary btn-sm" onclick="navigate('mocks')">Full Mocks Hub →</button>
    </div>

    <p class="text-muted text-sm" style="margin-bottom:16px;line-height:1.5">
      Topic-focused, timed subject examination papers modeled after official GATE sectional tests. Practice in a realistic 50–180 minute TCS iON timed test environment with virtual calculator, question palette, and instantaneous score telemetry.
    </p>

    <!-- Quick Telemetry Box -->
    <div class="subject-tests-telemetry-grid">
      <div class="stat-card" style="padding:14px 18px">
        <div style="font-size:24px">🧪</div>
        <div>
          <div style="font-size:18px;font-weight:700">${allSubTests.length} Subject Tests</div>
          <div style="font-size:11px;color:var(--text-muted)">26 Core GATE + 100 Subject Test Series</div>
        </div>
      </div>
      <div class="stat-card" style="padding:14px 18px">
        <div style="font-size:24px">📚</div>
        <div>
          <div style="font-size:18px;font-weight:700">${totalSubQuestions.toLocaleString()} Questions</div>
          <div style="font-size:11px;color:var(--text-muted)">100% Verified with full derivations</div>
        </div>
      </div>
      <div class="stat-card" style="padding:14px 18px">
        <div style="font-size:24px">⏱️</div>
        <div>
          <div style="font-size:18px;font-weight:700">50–180 Minutes</div>
          <div style="font-size:11px;color:var(--text-muted)">High-pressure sectional drills</div>
        </div>
      </div>
      <div class="stat-card" style="padding:14px 18px">
        <div style="font-size:24px">🎯</div>
        <div>
          <div style="font-size:18px;font-weight:700">TCS iON Simulation</div>
          <div style="font-size:11px;color:var(--text-muted)">Auto-save & detailed derivations</div>
        </div>
      </div>
    </div>

    <!-- Filter & Sort Bar -->
    <div class="subject-test-filter-bar">
      <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;flex:1">
        <div style="position:relative;flex:1;min-width:220px">
          <input type="text" class="search-input" style="width:100%;padding:8px 12px 8px 34px;border-radius:var(--radius-sm);background:var(--bg-input);border:1px solid var(--border);color:var(--text-primary);font-size:13px" placeholder="Search subject tests by topic, concept..." value="${escapeHtml(state.subjectTestSearch || '')}" oninput="handleSubjectTestSearch(this.value)" />
          <span style="position:absolute;left:10px;top:50%;transform:translateY(-50%);font-size:14px;color:var(--text-muted)">🔍</span>
        </div>
        <select class="filter-select" onchange="setSubjectTestSubject(this.value)" style="padding:7px 12px;font-size:12px;background:var(--bg-input);color:var(--text-primary);border:1px solid var(--border);border-radius:var(--radius-sm)">
          <option value="all" ${selectedSubject === 'all' ? 'selected' : ''}>All 13 Subjects (${allSubTests.length})</option>
          ${uniqueSubjects.map(sub => {
            const count = allSubTests.filter(m => m.subject === sub).length;
            return `<option value="${escapeHtml(sub)}" ${selectedSubject === sub ? 'selected' : ''}>${sub} (${count})</option>`;
          }).join('')}
        </select>
        <select class="filter-select" onchange="setSubjectTestDiff(this.value)" style="padding:7px 12px;font-size:12px;background:var(--bg-input);color:var(--text-primary);border:1px solid var(--border);border-radius:var(--radius-sm)">
          <option value="all" ${selectedDiff === 'all' ? 'selected' : ''}>All Difficulties</option>
          <option value="easy" ${selectedDiff === 'easy' ? 'selected' : ''}>🟢 Easy</option>
          <option value="medium" ${selectedDiff === 'medium' ? 'selected' : ''}>🟡 Medium</option>
          <option value="hard" ${selectedDiff === 'hard' ? 'selected' : ''}>🔴 Hard</option>
        </select>
        <select class="filter-select" onchange="setSubjectTestLevel(this.value)" style="padding:7px 12px;font-size:12px;background:var(--bg-input);color:var(--text-primary);border:1px solid var(--border);border-radius:var(--radius-sm)">
          <option value="all" ${selectedLevel === 'all' ? 'selected' : ''}>All Test Types & Levels</option>
          <option value="Foundational" ${selectedLevel === 'Foundational' ? 'selected' : ''}>🌟 Foundational (Set 1)</option>
          <option value="Advanced Booster" ${selectedLevel === 'Advanced Booster' ? 'selected' : ''}>🚀 Advanced Booster (Set 2)</option>
          <option value="Subject Test Series" ${selectedLevel === 'Subject Test Series' ? 'selected' : ''}>🧪 Subject Test Series (100 Tests)</option>
        </select>
      </div>
      <div style="font-size:12px;color:var(--text-muted);white-space:nowrap">
        Showing <strong>${filtered.length}</strong> of ${allSubTests.length} tests
      </div>
    </div>

    <!-- Subject Quick Chips -->
    <div class="subject-quick-chips" style="display:flex;gap:6px;overflow-x:auto;padding-bottom:10px;margin-bottom:16px">
      <button class="chip ${selectedSubject === 'all' ? 'active' : ''}" onclick="setSubjectTestSubject('all')" type="button">All Subjects</button>
      ${uniqueSubjects.map(sub => {
        const isActive = selectedSubject === sub;
        return `<button class="chip ${isActive ? 'active' : ''}" onclick="setSubjectTestSubject('${sub}')" type="button">${sub}</button>`;
      }).join('')}
    </div>

    <!-- Subject Tests Grid -->
    ${buildSubjectTestsGrid(filtered)}
  `;

  renderMath(c);
}

function setSubjectTestSubject(sub) {
  state.subjectTestFilter = sub;
  const c = document.getElementById('page-content');
  if (c && state.currentPage === 'subject-tests') renderSubjectTests(c);
}

function setSubjectTestDiff(diff) {
  state.subjectTestDiffFilter = diff;
  const c = document.getElementById('page-content');
  if (c && state.currentPage === 'subject-tests') renderSubjectTests(c);
}

function setSubjectTestLevel(level) {
  state.subjectTestLevelFilter = level;
  const c = document.getElementById('page-content');
  if (c && state.currentPage === 'subject-tests') renderSubjectTests(c);
}

function handleSubjectTestSearch(val) {
  state.subjectTestSearch = val;
  const c = document.getElementById('page-content');
  if (c && state.currentPage === 'subject-tests') renderSubjectTests(c);
}

function buildSubjectTestsGrid(mocks) {
  if (!mocks.length) {
    return `<div class="empty-state">
      <div class="empty-state-icon">📭</div>
      <div class="empty-state-title">No subject tests match your filters</div>
      <div class="empty-state-sub">Try selecting "All Subjects" or clearing your search term.</div>
      <button class="btn btn-secondary btn-sm" onclick="setSubjectTestSubject('all');setSubjectTestDiff('all');setSubjectTestLevel('all');handleSubjectTestSearch('');" style="margin-top:10px" type="button">Reset All Filters</button>
    </div>`;
  }

  return `<div class="mock-grid">${mocks.map(m => {
    const past = state.testSessions.filter(s => s.mockId === m.id);
    const best = past.length ? Math.max(...past.map(s => s.percentage)) : null;
    const questionsCount = getMockQuestions(m.id).length || m.questions;
    const diffLabel = (m.difficulty || 'medium').toUpperCase();
    const ratingBadge = m.rating ? `<span class="q-badge" style="background:rgba(245,158,11,0.14);color:#f59e0b;border:1px solid rgba(245,158,11,0.3);font-weight:700">⭐ ${m.rating.toFixed(1)}/10</span>` : '';
    let levelLabel = '🌟 Foundational';
    let levelStyle = 'background:rgba(34,197,94,0.14);color:#22c55e;border:1px solid rgba(34,197,94,0.35)';

    if (m.level === 'Advanced Booster') {
      levelLabel = '🚀 Advanced Booster';
      levelStyle = 'background:rgba(239,68,68,0.14);color:#ef4444;border:1px solid rgba(239,68,68,0.35)';
    } else if (m.level === 'Subject Test Series') {
      levelLabel = '🧪 Subject Test Series';
      levelStyle = 'background:rgba(99,102,241,0.14);color:#6366f1;border:1px solid rgba(99,102,241,0.35)';
    }

    return `<div class="mock-card">
      <div>
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;flex-wrap:wrap;gap:6px">
          <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap">
            <span class="q-badge" style="background:rgba(108,99,255,0.15);color:var(--accent);border:1px solid rgba(108,99,255,0.3);font-weight:700">📚 ${escapeHtml(m.subject || 'Core CS')}</span>
            <span class="q-badge" style="${levelStyle};font-weight:700">${levelLabel}</span>
          </div>
          <div style="display:flex;align-items:center;gap:6px">
            <span class="q-badge ${m.difficulty || 'medium'}">${diffLabel}</span>
            ${ratingBadge}
          </div>
        </div>
        <div class="mock-title">${escapeHtml(m.name)}</div>
        <div class="text-sm text-muted" style="margin-bottom:12px;line-height:1.5">${escapeHtml(m.desc)}</div>
        <div class="mock-meta">
          <div class="mock-meta-item">📚 ${questionsCount} Questions</div>
          <div class="mock-meta-item">⏱️ ${m.duration} Min</div>
          <div class="mock-meta-item">🏅 ${m.marks} Marks</div>
          ${best !== null ? `<div class="mock-meta-item" style="color:var(--green);font-weight:600">🏆 Best: ${best}%</div>` : ''}
        </div>
      </div>
      <div class="mock-card-actions">
        <button class="btn btn-secondary btn-sm" onclick="viewMockPaper('${m.id}')" title="Browse all questions in 20/page review format" type="button">📖 Practice Paper (20/page)</button>
        <button class="btn btn-primary btn-sm" onclick="startMockTest('${m.id}')" title="Start timed sectional exam" type="button">▶ Start Timed Exam</button>
      </div>
      ${past.length ? `<div class="text-sm text-muted mt-2">Attempted ${past.length} time${past.length > 1 ? 's' : ''}</div>` : ''}
    </div>`;
  }).join('')}</div>`;
}

// ─── REPEATING PATTERNS HUB & ARCHIVAL QUESTION BANK ───────────────────────

function getRepeatingPatternsData() {
  if (typeof window.GATE_REPEATING_PATTERNS !== 'undefined' && Array.isArray(window.GATE_REPEATING_PATTERNS) && window.GATE_REPEATING_PATTERNS.length) {
    return window.GATE_REPEATING_PATTERNS;
  }
  return state.repeatingPatterns || [];
}

async function ensureRepeatingPatternsLoaded() {
  if (typeof window.GATE_REPEATING_PATTERNS !== 'undefined' && Array.isArray(window.GATE_REPEATING_PATTERNS) && window.GATE_REPEATING_PATTERNS.length) {
    return window.GATE_REPEATING_PATTERNS;
  }
  try {
    const res = await fetch('./data/gate_pattern_master_index.json');
    if (res.ok) {
      const data = await res.json();
      window.GATE_REPEATING_PATTERNS = data;
      state.repeatingPatterns = data;
      return data;
    }
  } catch (e) {
    console.warn('[Patterns] Could not fetch gate_pattern_master_index.json:', e);
  }
  return [];
}

function formatPatternSourceLink(raw) {
  if (!raw) return '<span style="color:var(--text-muted)">Official GATE Examination Archive</span>';
  return raw.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer" style="color:var(--accent);text-decoration:underline;font-size:11px">$1</a>');
}

function renderRepeatingPatterns(c, params={}) {
  const activeTab = params.tab || state.patternActiveTab || 'patterns';
  state.patternActiveTab = activeTab;

  const patterns = getRepeatingPatternsData();

  if (!patterns.length) {
    ensureRepeatingPatternsLoaded().then(loaded => {
      if (loaded && loaded.length) {
        const el = document.getElementById('page-content');
        if (el && state.currentPage === 'patterns') renderRepeatingPatterns(el, params);
      }
    });
  }

  const selectedSubject = state.patternSubject || 'all';
  const selectedRecurrence = state.patternRecurrence || 'all';
  const selectedSort = state.patternSort || 'years-desc';
  const search = (state.patternSearch || '').trim().toLowerCase();

  let filtered = patterns.slice();

  if (selectedSubject !== 'all') {
    filtered = filtered.filter(p => p.subject === selectedSubject);
  }

  if (selectedRecurrence !== 'all') {
    const minYears = parseInt(selectedRecurrence, 10);
    if (!isNaN(minYears)) {
      filtered = filtered.filter(p => p.distinctYears >= minYears);
    }
  }

  if (search) {
    filtered = filtered.filter(p =>
      (p.name || '').toLowerCase().includes(search) ||
      (p.id || '').toLowerCase().includes(search) ||
      (p.subject || '').toLowerCase().includes(search) ||
      (p.chapter || '').toLowerCase().includes(search)
    );
  }

  // Sorting
  if (selectedSort === 'years-desc') {
    filtered.sort((a, b) => (b.distinctYears - a.distinctYears) || (b.totalQuestions - a.totalQuestions));
  } else if (selectedSort === 'questions-desc') {
    filtered.sort((a, b) => (b.totalQuestions - a.totalQuestions) || (b.distinctYears - a.distinctYears));
  } else if (selectedSort === 'recency-desc') {
    filtered.sort((a, b) => (b.lastAppearance || '').localeCompare(a.lastAppearance || '') || (b.distinctYears - a.distinctYears));
  } else if (selectedSort === 'id-asc') {
    filtered.sort((a, b) => (a.id || '').localeCompare(b.id || ''));
  }

  const uniqueSubjects = [
    'Discrete Mathematics', 'Computer Organization & Architecture', 'Algorithms',
    'Operating Systems', 'Computer Networks', 'Engineering Mathematics',
    'Digital Logic', 'Programming & Data Structures', 'Theory of Computation',
    'Databases / DBMS', 'General Aptitude', 'Compiler Design'
  ];

  c.innerHTML = `
    <!-- Hero / Header -->
    <div class="section-header">
      <div class="section-title">🔁 GATE CSE Repeating Patterns Hub (1983–2026) <span>338 Recurring Patterns • 4,910 Total PYQs</span></div>
      <div style="display:flex;gap:8px">
        <button class="btn btn-secondary btn-sm" onclick="navigate('pyqs')">Topic PYQs →</button>
        <button class="btn btn-secondary btn-sm" onclick="navigate('subject-tests')">🧪 Subject Tests →</button>
      </div>
    </div>

    <p class="text-muted text-sm" style="margin-bottom:20px;line-height:1.5">
      Empirical pattern-detection intelligence covering 44 examination years (1983–2026). A pattern is included if and only if GATE CS tested that exact underlying concept or problem-solving formula across at least 4 distinct examination years.
    </p>

    <!-- Top Two Primary Download Resources Requested by User -->
    <div class="pattern-resources-grid">
      <div class="pattern-resource-card" style="--card-accent:#f59e0b">
        <div>
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px">
            <span class="q-badge" style="background:rgba(245,158,11,0.18);color:#f59e0b;font-weight:700">🔁 466 PAGES • SOLVED PATTERNS</span>
            <span style="font-size:11px;color:var(--text-muted);font-weight:600">8.7 MB PDF</span>
          </div>
          <div style="font-size:17px;font-weight:700;color:var(--text-primary);margin-bottom:6px">GATE CSE Same-Pattern Questions (1983–2026)</div>
          <div style="font-size:12px;color:var(--text-secondary);line-height:1.5;margin-bottom:14px">
            Complete academic publication with 300+ recurring question patterns, 4,910 previous year questions, and step-by-step mathematical derivations. Includes the Master Pattern Index.
          </div>
        </div>
        <div style="display:flex;gap:8px;flex-wrap:wrap">
          <a href="assets/resources/GATE_CSE_Same_Pattern_Questions_1983_2026.pdf" download="GATE_CSE_Same_Pattern_Questions_1983_2026.pdf" class="btn btn-primary btn-sm" style="flex:1;min-width:140px;justify-content:center">
            📥 Download 466p PDF
          </a>
          <a href="assets/resources/GATE_CSE_Same_Pattern_Questions_1983_2026.pdf" target="_blank" rel="noopener noreferrer" class="btn btn-secondary btn-sm" style="justify-content:center">
            📖 Open in Tab
          </a>
          <a href="assets/resources/GATE_CSE_Pattern_Master_Index_1983_2026.csv" download="GATE_CSE_Pattern_Master_Index_1983_2026.csv" class="btn btn-secondary btn-sm" style="justify-content:center" title="Download Raw Master Index CSV (115 KB)">
            📊 CSV Index
          </a>
        </div>
      </div>

      <div class="pattern-resource-card" style="--card-accent:#6c63ff">
        <div>
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px">
            <span class="q-badge" style="background:rgba(108,99,255,0.18);color:var(--accent);font-weight:700">🏛️ 562 PAGES • 44-YEAR ARCHIVE</span>
            <span style="font-size:11px;color:var(--text-muted);font-weight:600">2.4 MB PDF</span>
          </div>
          <div style="font-size:17px;font-weight:700;color:var(--text-primary);margin-bottom:6px">GATE CSE Question Bank (1983–2026 Consolidated)</div>
          <div style="font-size:12px;color:var(--text-secondary);line-height:1.5;margin-bottom:14px">
            Complete consolidated 44-year archival master reference edition covering all 7 historical batches (1983 to 2026). Includes official answer keys, verified derivations, and disputed/MTA register.
          </div>
        </div>
        <div style="display:flex;gap:8px;flex-wrap:wrap">
          <a href="assets/resources/GATE_CSE_Question_Bank_1983_2026_Consolidated.pdf" download="GATE_CSE_Question_Bank_1983_2026_Consolidated.pdf" class="btn btn-primary btn-sm" style="flex:1;min-width:140px;justify-content:center">
            📥 Download 562p PDF
          </a>
          <a href="assets/resources/GATE_CSE_Question_Bank_1983_2026_Consolidated.pdf" target="_blank" rel="noopener noreferrer" class="btn btn-secondary btn-sm" style="justify-content:center">
            📖 Open in Tab
          </a>
          <button class="btn btn-secondary btn-sm" onclick="switchPatternTab('archival')" type="button" style="justify-content:center">
            📜 Batch Matrix
          </button>
        </div>
      </div>
    </div>

    <!-- View Mode Switcher -->
    <div class="tabs" style="margin-bottom:18px">
      <button class="tab-btn ${activeTab === 'patterns' ? 'active' : ''}" onclick="switchPatternTab('patterns')" type="button">
        🔁 All 338 Recurring Patterns (${patterns.length})
      </button>
      <button class="tab-btn ${activeTab === 'top10' ? 'active' : ''}" onclick="switchPatternTab('top10')" type="button">
        ⭐ Top 10 Most Repeated Patterns
      </button>
      <button class="tab-btn ${activeTab === 'archival' ? 'active' : ''}" onclick="switchPatternTab('archival')" type="button">
        🏛️ 44-Year Archival Batches (1983–2026)
      </button>
    </div>

    <div id="pattern-tab-content">
      ${activeTab === 'top10' ? buildPatternTop10HTML(patterns) : activeTab === 'archival' ? buildArchivalBankSectionHTML() : buildPatternBrowserHTML(filtered, patterns, uniqueSubjects, selectedSubject, selectedRecurrence, selectedSort)}
    </div>
  `;

  renderMath(c);
}

function switchPatternTab(tab) {
  state.patternActiveTab = tab;
  const c = document.getElementById('page-content');
  if (c && state.currentPage === 'patterns') renderRepeatingPatterns(c, { tab });
}

function setPatternSubject(sub) {
  state.patternSubject = sub;
  const c = document.getElementById('page-content');
  if (c && state.currentPage === 'patterns') renderRepeatingPatterns(c);
}

function setPatternRecurrence(rec) {
  state.patternRecurrence = rec;
  const c = document.getElementById('page-content');
  if (c && state.currentPage === 'patterns') renderRepeatingPatterns(c);
}

function setPatternSort(sortVal) {
  state.patternSort = sortVal;
  const c = document.getElementById('page-content');
  if (c && state.currentPage === 'patterns') renderRepeatingPatterns(c);
}

function handlePatternSearch(val) {
  state.patternSearch = val;
  const c = document.getElementById('page-content');
  if (c && state.currentPage === 'patterns') renderRepeatingPatterns(c);
}

function buildPatternBrowserHTML(filtered, allPatterns, uniqueSubjects, selectedSubject, selectedRecurrence, selectedSort) {
  return `
    <!-- Filter Bar -->
    <div class="subject-test-filter-bar">
      <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;flex:1">
        <div style="position:relative;flex:1;min-width:240px">
          <input type="text" class="search-input" style="width:100%;padding:8px 12px 8px 34px;border-radius:var(--radius-sm);background:var(--bg-input);border:1px solid var(--border);color:var(--text-primary);font-size:13px" placeholder="Search by topic, formula, algorithm, pattern ID (e.g. COA-001, Cache, DFA)..." value="${escapeHtml(state.patternSearch || '')}" oninput="handlePatternSearch(this.value)" />
          <span style="position:absolute;left:10px;top:50%;transform:translateY(-50%);font-size:14px;color:var(--text-muted)">🔍</span>
        </div>
        <select class="filter-select" onchange="setPatternSubject(this.value)" style="padding:7px 12px;font-size:12px;background:var(--bg-input);color:var(--text-primary);border:1px solid var(--border);border-radius:var(--radius-sm)">
          <option value="all" ${selectedSubject === 'all' ? 'selected' : ''}>All 12 Subjects (${allPatterns.length})</option>
          ${uniqueSubjects.map(sub => {
            const count = allPatterns.filter(p => p.subject === sub).length;
            return `<option value="${escapeHtml(sub)}" ${selectedSubject === sub ? 'selected' : ''}>${sub} (${count})</option>`;
          }).join('')}
        </select>
        <select class="filter-select" onchange="setPatternRecurrence(this.value)" style="padding:7px 12px;font-size:12px;background:var(--bg-input);color:var(--text-primary);border:1px solid var(--border);border-radius:var(--radius-sm)">
          <option value="all" ${selectedRecurrence === 'all' ? 'selected' : ''}>All Recurrences (≥ 4 Years)</option>
          <option value="15" ${selectedRecurrence === '15' ? 'selected' : ''}>🔥 Ultra High (≥ 15 Years)</option>
          <option value="10" ${selectedRecurrence === '10' ? 'selected' : ''}>⚡ High (≥ 10 Years)</option>
          <option value="6" ${selectedRecurrence === '6' ? 'selected' : ''}>📚 Medium (≥ 6 Years)</option>
          <option value="4" ${selectedRecurrence === '4' ? 'selected' : ''}>Standard (≥ 4 Years)</option>
        </select>
        <select class="filter-select" onchange="setPatternSort(this.value)" style="padding:7px 12px;font-size:12px;background:var(--bg-input);color:var(--text-primary);border:1px solid var(--border);border-radius:var(--radius-sm)">
          <option value="years-desc" ${selectedSort === 'years-desc' ? 'selected' : ''}>Sort: Most Years Asked</option>
          <option value="questions-desc" ${selectedSort === 'questions-desc' ? 'selected' : ''}>Sort: Most Total Questions</option>
          <option value="recency-desc" ${selectedSort === 'recency-desc' ? 'selected' : ''}>Sort: Most Recent (GATE 2026 first)</option>
          <option value="id-asc" ${selectedSort === 'id-asc' ? 'selected' : ''}>Sort: Pattern ID</option>
        </select>
      </div>
      <div style="font-size:12px;color:var(--text-muted);white-space:nowrap">
        Showing <strong>${filtered.length}</strong> of ${allPatterns.length} patterns
      </div>
    </div>

    <!-- Subject Quick Chips -->
    <div class="subject-quick-chips" style="display:flex;gap:6px;overflow-x:auto;padding-bottom:10px;margin-bottom:16px">
      <button class="chip ${selectedSubject === 'all' ? 'active' : ''}" onclick="setPatternSubject('all')" type="button">All Subjects</button>
      ${uniqueSubjects.map(sub => {
        const isActive = selectedSubject === sub;
        return `<button class="chip ${isActive ? 'active' : ''}" onclick="setPatternSubject('${sub}')" type="button">${sub}</button>`;
      }).join('')}
    </div>

    <!-- Patterns Grid -->
    ${buildPatternCardsGrid(filtered)}
  `;
}

function buildPatternCardsGrid(patterns) {
  if (!patterns.length) {
    return `<div class="empty-state">
      <div class="empty-state-icon">🔍</div>
      <div class="empty-state-title">No patterns match your search</div>
      <div class="empty-state-sub">Try searching for broader keywords like "tree", "memory", "graph", or select "All Subjects".</div>
      <button class="btn btn-secondary btn-sm" onclick="setPatternSubject('all');setPatternRecurrence('all');handlePatternSearch('');" style="margin-top:10px" type="button">Reset Filters</button>
    </div>`;
  }

  return `<div class="patterns-grid">${patterns.map(p => {
    const isUltra = p.distinctYears >= 15;
    const isHigh = p.distinctYears >= 10;
    const freqColor = isUltra ? '#ef4444' : isHigh ? '#f59e0b' : '#3b82f6';
    const years = Array.isArray(p.allYears) ? p.allYears : [];

    return `<div class="pattern-card">
      <div>
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;flex-wrap:wrap;gap:6px">
          <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap">
            <span class="q-badge" style="background:rgba(108,99,255,0.18);color:var(--accent);border:1px solid rgba(108,99,255,0.4);font-weight:700">${escapeHtml(p.id)}</span>
            <span class="q-badge" style="background:var(--bg-input);color:var(--text-secondary);border:1px solid var(--border)">${escapeHtml(p.subject)}</span>
          </div>
          <span class="q-badge" style="background:rgba(245,158,11,0.12);color:${freqColor};border:1px solid ${freqColor}40;font-weight:700">
            🔥 ${p.distinctYears} Distinct Years
          </span>
        </div>

        <div style="font-weight:700;font-size:14px;color:var(--text-primary);line-height:1.4;margin-bottom:6px">
          ${escapeHtml(p.name)}
        </div>

        <div style="font-size:11px;color:var(--text-muted);margin-bottom:10px">
          📂 <strong>Chapter:</strong> ${escapeHtml(p.chapter || 'Core Chapter')}
        </div>

        <div class="mock-meta" style="margin-bottom:10px">
          <div class="mock-meta-item">📚 ${p.totalQuestions} Solved PYQs</div>
          <div class="mock-meta-item">📅 Last: GATE ${escapeHtml(p.lastAppearance || '2026')}</div>
        </div>

        <div style="font-size:11px;font-weight:700;color:var(--text-muted);margin-bottom:4px">
          Years Asked (${years.length}):
        </div>
        <div class="pattern-years-wrap">
          ${years.map(yr => {
            const isRecent = parseInt(yr, 10) >= 2020;
            return `<span class="pattern-year-pill ${isRecent ? 'recent' : ''}">${escapeHtml(yr)}</span>`;
          }).join('')}
        </div>
      </div>

      <div style="margin-top:14px;border-top:1px solid var(--border);padding-top:10px">
        <div style="font-size:11px;color:var(--text-muted);margin-bottom:8px;overflow:hidden;text-overflow:ellipsis">
          🔗 <strong>Source:</strong> ${formatPatternSourceLink(p.sourceLink)}
        </div>
        <div style="display:flex;gap:6px">
          <button class="btn btn-secondary btn-sm" onclick="navigate('practice',{subject:'${escapeHtml(p.subject)}'})" style="flex:1;justify-content:center" type="button">
            ✏️ Practice ${escapeHtml(p.subject.split(' ')[0])}
          </button>
          <a href="assets/resources/GATE_CSE_Same_Pattern_Questions_1983_2026.pdf" target="_blank" rel="noopener noreferrer" class="btn btn-primary btn-sm" style="justify-content:center" title="Open Solved Pattern Book">
            📖 View PDF
          </a>
        </div>
      </div>
    </div>`;
  }).join('')}</div>`;
}

function buildPatternTop10HTML(patterns) {
  const top10 = patterns.slice().sort((a, b) => (b.distinctYears - a.distinctYears) || (b.totalQuestions - a.totalQuestions)).slice(0, 10);

  return `
    <div style="margin-bottom:18px">
      <div style="font-weight:700;font-size:16px;color:var(--text-primary);margin-bottom:4px">
        🏆 Top 10 Most Frequently Repeated GATE CSE Question Patterns (1983–2026)
      </div>
      <div style="font-size:12px;color:var(--text-muted)">
        Ranked by the total number of distinct examination years in which this exact mathematical or algorithmic procedure appeared on the official paper.
      </div>
    </div>

    <div class="pattern-top10-grid">
      ${top10.map((p, idx) => {
        const pct = Math.round((p.distinctYears / 44) * 100);
        return `<div class="pattern-top10-card">
          <div>
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px">
              <span class="q-badge" style="background:rgba(245,158,11,0.2);color:#f59e0b;font-weight:800;font-size:12px">Rank #${idx + 1}</span>
              <span class="q-badge" style="background:rgba(108,99,255,0.18);color:var(--accent);font-weight:700">${escapeHtml(p.id)}</span>
            </div>
            <div style="font-weight:700;font-size:14px;color:var(--text-primary);margin-bottom:4px;line-height:1.4">
              ${escapeHtml(p.name)}
            </div>
            <div style="font-size:11px;color:var(--text-muted);margin-bottom:8px">
              📚 ${escapeHtml(p.subject)} • ${escapeHtml(p.chapter)}
            </div>

            <div style="margin-bottom:10px">
              <div style="display:flex;justify-content:space-between;font-size:11px;font-weight:600;margin-bottom:4px">
                <span>🔥 ${p.distinctYears} Distinct Years</span>
                <span>${p.totalQuestions} Questions</span>
              </div>
              <div style="height:6px;border-radius:99px;background:var(--bg-input);overflow:hidden">
                <div style="width:${pct}%;height:100%;background:linear-gradient(90deg,#f59e0b,#ef4444);border-radius:99px"></div>
              </div>
            </div>
          </div>
          <div style="display:flex;gap:6px;margin-top:10px">
            <button class="btn btn-secondary btn-sm" onclick="navigate('practice',{subject:'${escapeHtml(p.subject)}'})" style="flex:1;justify-content:center" type="button">
              ✏️ Practice Subject
            </button>
            <a href="assets/resources/GATE_CSE_Same_Pattern_Questions_1983_2026.pdf" target="_blank" rel="noopener noreferrer" class="btn btn-primary btn-sm" style="justify-content:center">
              📖 Open PDF
            </a>
          </div>
        </div>`;
      }).join('')}
    </div>
  `;
}

function buildArchivalBankSectionHTML() {
  const batches = [
    { num: 1, years: '1983–1990', name: 'Historical Papers (Pre-Digital Era)', count: '52 Solved Questions', desc: 'Subjective derivations, paper-pencil analytical questions from early IISc/IIT papers.', color: '#6c63ff' },
    { num: 2, years: '1991–2000', name: 'Historical Subjective & Early MCQ Era', count: '111 Solved Questions', desc: 'Transition from subjective proofs to standardized objective 1-mark & 2-mark formats.', color: '#3b82f6' },
    { num: 3, years: '2001–2005', name: 'Historical Objective Master Era', count: '10 Solved Questions', desc: 'Fully standardized single-correct MCQs across all 11 core computer science streams.', color: '#10b981' },
    { num: 4, years: '2006–2010', name: 'Pre-CBT & IT Stream Merger Era', count: '12 Solved Questions', desc: 'Common CS & IT papers, linked answer questions, and common data question sets.', color: '#eab308' },
    { num: 5, years: '2011–2015', name: 'OMR-to-CBT Multi-Session Transition', count: '20 Solved Questions', desc: 'Launch of online Computer-Based Testing (CBT) and introduction of Numerical Answer Types (NAT).', color: '#f97316' },
    { num: 6, years: '2016–2020', name: 'Modern Online Examination Era', count: '20 Solved Questions', desc: 'Multi-set normalized CBT papers with official virtual calculator integration.', color: '#ec4899' },
    { num: 7, years: '2021–2026', name: 'Recent MSQ + NAT + MCQ Benchmark Era', count: '650 Solved Questions', desc: 'Modern pattern introducing Multiple Select Questions (MSQ) with zero negative marking alongside NATs.', color: '#14b8a6' }
  ];

  return `
    <div style="margin-bottom:20px">
      <div style="font-weight:700;font-size:16px;color:var(--text-primary);margin-bottom:4px">
        🏛️ Archival Question Bank (1983–2026 Consolidated Edition)
      </div>
      <div style="font-size:12px;color:var(--text-muted);line-height:1.5">
        562 Pages • 55 Official Exam Papers • Synthesizing all 7 historical execution batches. Every question, answer key, and solution derivation was cross-checked across official organizing institutes.
      </div>
    </div>

    <!-- Telemetry Cards -->
    <div class="subject-tests-telemetry-grid">
      <div class="stat-card" style="padding:14px 18px">
        <div style="font-size:24px">📑</div>
        <div>
          <div style="font-size:18px;font-weight:700">562 Pages</div>
          <div style="font-size:11px;color:var(--text-muted)">Complete Consolidated Reference Book</div>
        </div>
      </div>
      <div class="stat-card" style="padding:14px 18px">
        <div style="font-size:24px">🏛️</div>
        <div>
          <div style="font-size:18px;font-weight:700">55 Official Papers</div>
          <div style="font-size:11px;color:var(--text-muted)">1983 through 2026 archival scope</div>
        </div>
      </div>
      <div class="stat-card" style="padding:14px 18px">
        <div style="font-size:24px">🔢</div>
        <div>
          <div style="font-size:18px;font-weight:700">493 MCQs • 189 MSQs</div>
          <div style="font-size:11px;color:var(--text-muted)">Plus 190 NATs and historical proofs</div>
        </div>
      </div>
      <div class="stat-card" style="padding:14px 18px">
        <div style="font-size:24px">⚖️</div>
        <div>
          <div style="font-size:18px;font-weight:700">MTA Audit Included</div>
          <div style="font-size:11px;color:var(--text-muted)">Official Marks-to-All register reconciled</div>
        </div>
      </div>
    </div>

    <!-- Batches Grid -->
    <div style="font-weight:700;font-size:14px;color:var(--text-primary);margin:16px 0 10px">
      📅 7-Batch Historical Execution Architecture (1983–2026)
    </div>
    <div class="archival-batches-grid">
      ${batches.map(b => `
        <div class="archival-batch-card" style="border-left:4px solid ${b.color}">
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:4px">
            <span class="q-badge" style="background:${b.color}20;color:${b.color};font-weight:700">Batch ${b.num}: ${b.years}</span>
            <span style="font-size:11px;font-weight:700;color:var(--text-primary)">${b.count}</span>
          </div>
          <div style="font-weight:700;font-size:13px;color:var(--text-primary);margin-bottom:4px">${b.name}</div>
          <div style="font-size:11px;color:var(--text-secondary);line-height:1.4">${b.desc}</div>
        </div>
      `).join('')}
    </div>

    <!-- Download & Actions Footer -->
    <div style="background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius);padding:18px;margin-top:20px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:14px">
      <div>
        <div style="font-weight:700;font-size:15px;color:var(--text-primary)">📥 Download 562-Page Archival Compilation PDF</div>
        <div style="font-size:12px;color:var(--text-muted);margin-top:2px">Instant offline PDF reference with clickable table of contents, derivations, and answer keys.</div>
      </div>
      <div style="display:flex;gap:8px">
        <a href="assets/resources/GATE_CSE_Question_Bank_1983_2026_Consolidated.pdf" download="GATE_CSE_Question_Bank_1983_2026_Consolidated.pdf" class="btn btn-primary btn-sm">
          📥 Download PDF (2.4 MB)
        </a>
        <a href="assets/resources/GATE_CSE_Question_Bank_1983_2026_Consolidated.pdf" target="_blank" rel="noopener noreferrer" class="btn btn-secondary btn-sm">
          📖 View in Browser
        </a>
      </div>
    </div>
  `;
}

function viewMockPaper(mockId, page=1){

  state.activeMockPaper = {

    mockId,

    page: page || 1,

    pageSize: 20

  };

  const c = document.getElementById('page-content');

  renderMockPaperView(c);

}



function renderMockPaperView(c){

  if (!state.activeMockPaper) {

    navigate('mocks');

    return;

  }

  const { mockId, page, pageSize: rawPageSize } = state.activeMockPaper;

  const mock = MOCK_TESTS.find(m => m.id === mockId) || FULL_LENGTH_PYQ_EXAMS.find(e => e.id === mockId) || PRACTICE_PAPERS.find(p => p.id === mockId);

  const questions = getMockQuestions(mockId);

  state.practiceQueue = questions; // Load into practice queue



  const totalCount = questions.length;

  const pageSize = rawPageSize === 'all' ? (totalCount || 1) : parseInt(rawPageSize, 10);

  const totalPages = Math.max(1, Math.ceil(totalCount / pageSize));

  const currentPage = Math.min(Math.max(1, page), totalPages);

  state.activeMockPaper.page = currentPage;



  const startIndex = (currentPage - 1) * pageSize;

  const endIndex = Math.min(startIndex + pageSize, totalCount);

  const pageItems = questions.slice(startIndex, endIndex);



  const title = mock ? mock.name : 'Practice Paper';

  const isMockTest = !!MOCK_TESTS.find(m => m.id === mockId);



  const paginationArgs = {

    currentPage,

    totalPages,

    totalCount,

    startIndex: totalCount > 0 ? startIndex + 1 : 0,

    endIndex,

    pageSize: rawPageSize,

    onPageChangeFn: 'setMockPaperPage',

    onPageSizeChangeFn: 'setMockPaperPageSize'

  };



  c.innerHTML = `

    <div class="breadcrumb">

      <span class="breadcrumb-item" onclick="closeMockPaperView()" style="cursor:pointer;color:var(--accent)">← Back to All ${isMockTest ? 'Mocks' : 'Practice Papers'}</span>

      <span class="breadcrumb-sep">›</span>

      <span class="breadcrumb-item active">${title}</span>

    </div>



    <div class="section-header" style="flex-wrap:wrap;gap:12px">

      <div>

        <div class="section-title">${title} <span>${totalCount} questions • 20/page</span></div>

        <div class="text-sm text-muted" style="margin-top:4px">

          ${mock?.subject ? `Subject: ${mock.subject}` : 'Full GATE CSE Mock Paper'} • Page ${currentPage} of ${totalPages}

        </div>

      </div>

      <div style="display:flex;gap:10px;flex-wrap:wrap">

        <button class="btn btn-secondary btn-sm" onclick="startMockPaperPractice()">▶ Practice All (${totalCount} Qs)</button>

        ${isMockTest ? `<button class="btn btn-primary btn-sm" onclick="startMockTest('${mockId}')">⏱ Start Timed Exam</button>` : ''}

      </div>

    </div>



    ${!totalCount

      ? `<div class="empty-state">

           <div class="empty-state-icon">📭</div>

           <div class="empty-state-title">No questions found for this paper</div>

           <button class="btn btn-secondary mt-4" onclick="closeMockPaperView()">Back</button>

         </div>`

      : `${buildPaginationHTML({ ...paginationArgs, isTop: true })}

         <div class="pyq-grid" id="mock-questions-grid">

           ${pageItems.map((q, idx) => `

             <div class="pyq-item" onclick="openSingleQuestion('${q.id}')">

               <div class="pyq-item-year" style="font-size:11px">

                 ${state.attempts.find(a => a.questionId === q.id)?.correct ? '✅' : state.attempts.find(a => a.questionId === q.id) ? '❌' : '⬜'}<br/>

                 <span style="font-size:10px;color:var(--text-muted)">${q.type?.toUpperCase()}</span>

               </div>

               <div class="pyq-item-content">

                 <div class="pyq-item-question">

                   <strong style="color:var(--accent);margin-right:6px">Q${startIndex + idx + 1}.</strong>${formatQuestionContent(q.question)}

                 </div>

                 <div class="pyq-item-meta">

                   <span class="chip">${q.subject}</span>

                   ${q.topic ? `<span class="chip">${q.topic}</span>` : ''}

                   <span class="q-badge ${q.difficulty}">${q.difficulty}</span>

                   <span class="chip">${q.marks}m</span>

                   <button class="btn btn-secondary btn-sm" style="margin-left:auto;padding:2px 8px;font-size:11px" onclick="event.stopPropagation();openSingleQuestion('${q.id}')">Solve →</button>

                 </div>

               </div>

             </div>

           `).join('')}

         </div>

         ${buildPaginationHTML({ ...paginationArgs, isTop: false })}`

    }

  `;

}



function setMockPaperPage(page){

  if (!state.activeMockPaper) return;

  state.activeMockPaper.page = page;

  renderMockPaperView(document.getElementById('page-content'));

  const el = document.getElementById('mock-questions-grid');

  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });

}



function setMockPaperPageSize(sz){

  if (!state.activeMockPaper) return;

  state.activeMockPaper.pageSize = sz === 'all' ? 'all' : parseInt(sz, 10);

  state.activeMockPaper.page = 1;

  renderMockPaperView(document.getElementById('page-content'));

}



function closeMockPaperView(){

  const mockId = state.activeMockPaper?.mockId || '';

  state.activeMockPaper = null;

  if (mockId.startsWith('pyq-exam-') || state.currentPage === 'pyq-exams') {

    navigate('pyq-exams');

  } else {

    navigate('mocks');

  }

}



function startMockPaperPractice(){

  if (!state.activeMockPaper) return;

  const questions = getMockQuestions(state.activeMockPaper.mockId);

  if (!questions.length) return;

  state.practiceQueue = [...questions];

  state.currentQuestion = 0;

  renderPracticeQuestion();

}



function startPracticePaperDirect(paperId){

  const questions = getMockQuestions(paperId);

  if (!questions.length) return;

  state.practiceQueue = [...questions];

  state.currentQuestion = 0;

  renderPracticeQuestion();

}



function buildTestHistory(){

  if (!state.testSessions.length) return `<div class="empty-state"><div class="empty-state-icon">📊</div><div class="empty-state-title">No history yet</div></div>`;

  return `<div style="display:flex;flex-direction:column;gap:12px">

    ${[...state.testSessions].reverse().map(s=>`

      <div class="card">

        <div style="display:flex;justify-content:space-between;align-items:center">

          <div><div style="font-weight:700">${s.name}</div><div class="text-sm text-muted">${new Date(s.date).toLocaleString()}</div></div>

          <div style="text-align:right"><div style="font-size:24px;font-weight:800;color:var(--accent)">${s.percentage}%</div><div class="text-sm text-muted">${s.score}/${s.maxScore} marks</div></div>

        </div>

        <div class="divider"></div>

        <div style="display:flex;gap:20px">

          <span class="text-sm text-green">✅ ${s.correct} Correct</span>

          <span class="text-sm text-red">❌ ${s.wrong} Wrong</span>

          <span class="text-sm">⏭ ${s.skipped} Skipped</span>

          <span class="text-sm">⏱ ${fmtH(s.timeTaken)}</span>

        </div>

      </div>`).join('')}

  </div>`;

}



// ─── MOCK TEST ENGINE ────────────────────────────────────────────────────────

let mockTimerInterval=null;



function startMockTest(mockId){

  const mock = MOCK_TESTS.find(m => m.id === mockId) || FULL_LENGTH_PYQ_EXAMS.find(e => e.id === mockId) || PRACTICE_PAPERS.find(p => p.id === mockId);

  if (!mock) return;

  let questions=getMockQuestions(mockId);

  if (!questions.length){showToast('No questions available! Upload questions first.','error');return;}

  state.activeTest={

    mockId,mock,questions,

    answers:new Array(questions.length).fill(null),

    marked:new Set(),

    visited:new Set([0]),

    currentQ:0, timeLeft:mock.duration*60, submitted:false,

    timePerQ:new Array(questions.length).fill(0),

    tabSwitches:0,

  };

  saveExamAutoSaveState();

  renderTestMode();

}



function renderTestMode(){

  const {mock,questions,timeLeft}=state.activeTest;

  const ov=document.getElementById('test-overlay');

  ov.innerHTML=`

    <div class="test-topbar">

      <div class="test-topbar-left">

        <button class="btn btn-danger btn-sm" onclick="confirmSubmitTest()">Submit Test</button>

        <div class="test-title" title="${mock.name}">${mock.name}${mock.provider ? ` <span style="font-size:12px;opacity:0.85;font-weight:500">(${mock.provider})</span>` : ''}</div>

      </div>

      <div class="test-topbar-right">

        <div class="test-autosave-badge" id="test-autosave-badge" title="Response auto-saved to device">☁️ <span id="test-autosave-time">Saved</span></div>

        <button class="btn btn-secondary btn-sm" onclick="openExamQuestionPaper()" type="button" title="View Full Question Paper (Read-Only)">📄 <span class="hide-xs">Paper</span></button>

        <button class="btn btn-secondary btn-sm" onclick="openExamInstructions()" type="button" title="Official GATE Exam Instructions">ℹ️ <span class="hide-xs">Inst</span></button>

        <button class="btn btn-secondary btn-sm" id="exam-fullscreen-btn" onclick="toggleExamFullscreen()" type="button" title="Toggle Fullscreen Exam Mode (F)">⛶ <span class="hide-xs">Fullscreen</span></button>

        <button class="btn btn-secondary btn-sm" onclick="toggleGateCalc()" type="button" title="GATE Virtual Calculator (C)">🧮 <span class="hide-xs">Calc</span></button>

        <button class="btn btn-secondary btn-sm" id="exam-chime-btn" onclick="toggleExamChimes()" type="button" title="Toggle Exam Countdown Chimes">${chimesEnabled ? '🔔' : '🔕'} <span class="hide-xs">Chimes</span></button>

        <button class="btn btn-secondary btn-sm" onclick="toggleShortcutsModal()" type="button" title="Shortcuts (?)">⌨️</button>

        <div id="test-timer-display" class="test-timer-display">${fmtH(timeLeft)}</div>

        <button class="btn btn-secondary btn-sm test-palette-toggle" onclick="toggleTestPalette()" type="button" title="Question Palette">

          🎨 <span class="hide-xs">Palette</span>

        </button>

      </div>

    </div>

    ${questions.length >= 65 ? `
    <div class="test-section-bar" id="test-section-bar">
      <div class="test-section-tab ${state.activeTest.currentQ < 10 ? 'active' : ''}" id="sec-tab-ga" onclick="switchTestSection('ga')">
        <span class="sec-name">Section 1: General Aptitude (GA)</span>
        <span class="sec-meta">Q1–Q10 • 15 Marks</span>
      </div>
      <div class="test-section-tab ${state.activeTest.currentQ >= 10 ? 'active' : ''}" id="sec-tab-cs" onclick="switchTestSection('cs')">
        <span class="sec-name">Section 2: Computer Science & IT (CS)</span>
        <span class="sec-meta">Q11–Q65 • 85 Marks</span>
      </div>
    </div>` : ''}

    <div class="test-content">

      <div class="palette-backdrop" id="palette-backdrop" onclick="toggleTestPalette()"></div>

      <div class="test-sidebar" id="test-sidebar">

        <div class="test-sidebar-header">

          <div class="section-title" style="font-size:13px">TCS iON Question Palette</div>

          <button class="palette-close-btn" onclick="toggleTestPalette()" type="button">✕</button>

        </div>

        <div class="palette-legend-5" id="palette-legend-container">

          <div class="palette-legend-item-5"><div class="legend-shape" style="background:#22c55e"></div>Answered (<span id="cnt-ans">0</span>)</div>

          <div class="palette-legend-item-5"><div class="legend-shape" style="background:#ef4444"></div>Not Answered (<span id="cnt-notans">0</span>)</div>

          <div class="palette-legend-item-5"><div class="legend-shape" style="background:var(--bg-input);border:1px solid var(--border)"></div>Not Visited (<span id="cnt-notvis">0</span>)</div>

          <div class="palette-legend-item-5"><div class="legend-shape" style="background:#8b5cf6"></div>Marked (<span id="cnt-marked">0</span>)</div>

          <div class="palette-legend-item-5"><div class="legend-shape" style="background:#8b5cf6;border:2px solid #22c55e"></div>Ans & Marked (<span id="cnt-ansmarked">0</span>)</div>

        </div>

        <div class="question-palette" id="q-palette">

          ${questions.map((_,i)=>`<button class="palette-btn not-visited" id="pb-${i}" onclick="jumpToTestQ(${i})">${i+1}</button>`).join('')}

        </div>

      </div>

      <div class="test-main" id="test-q-main"></div>

    </div>`;

  ov.classList.add('active');

  renderTestQuestion();

  updatePaletteStates();

  startMockTimer();

  saveExamAutoSaveState();

}



function renderTestQuestion(){

  const {questions,currentQ,answers}=state.activeTest;

  const q=questions[currentQ]; const ans=answers[currentQ];

  practiceSelectedOpts=new Set(ans&&q.type!=='nat'?(Array.isArray(ans)?ans:[ans]):[]);

  const labels=['A','B','C','D','E'];

  const sel=new Set(ans!==null?(Array.isArray(ans)?ans:[ans]):[]);

  const isBookmarked = state.bookmarks?.has(q.id);

  const main=document.getElementById('test-q-main');

  if (!main) return;

  main.innerHTML=`

    <div class="question-progress-bar"><div class="question-progress-fill" style="width:${(currentQ/questions.length)*100}%"></div></div>

    <div class="question-card">

      <div class="question-header">

        <div class="question-meta">

          <span class="q-badge ${q.type}">${q.type?.toUpperCase()}</span>

          <span class="q-badge ${q.difficulty}">${q.difficulty}</span>

          ${q.topic?`<span class="chip">${q.topic}</span>`:''}

          ${q.subject?`<span class="chip">${q.subject}</span>`:''}

        </div>

        <div style="display:flex;align-items:center;gap:8px">

          <button class="star-btn ${isBookmarked ? 'bookmarked' : ''}" data-qid="${q.id}" onclick="toggleBookmark('${q.id}')" title="${isBookmarked ? 'Remove Bookmark' : 'Add Bookmark'}" type="button">

            ${isBookmarked ? '⭐' : '☆'}

          </button>

          <span class="chip ${q.type === 'mcq' ? 'penalty-chip' : 'zero-penalty-chip'}" title="${q.type === 'mcq' ? `Negative mark penalty: ${(q.marks/3).toFixed(2)} marks for wrong answer` : 'Zero negative marking for this question'}">+${q.marks} / ${q.type === 'mcq' ? `-${(q.marks/3).toFixed(2)}` : '0 penalty'}</span>

        </div>

      </div>

      <div class="question-number">Q${currentQ+1} of ${questions.length}</div>

      <div class="question-text">${formatQuestionContent(q.question)}</div>

      ${q.type==='nat'

        ? `<div class="nat-wrapper">

             <div class="nat-input-wrapper">

               <input type="text" inputmode="decimal" class="nat-input" id="nat-answer" placeholder="Enter answer"

                 value="${ans!==null&&ans!==undefined?ans:''}" ${state.examStrictMode ? 'readonly="readonly" style="cursor:not-allowed"' : ''} oninput="saveNATAnswer(this.value)"/>

               ${state.examStrictMode ? '<span class="chip" style="font-size:10px;color:var(--green)">🔒 Strict: Keypad Enforced</span>' : ''}

             </div>

             ${buildNatKeypadHTML()}

           </div>`

        : (!q.options || q.options.length === 0)
          ? `<div class="notice-box info" style="margin:12px 0;padding:12px 16px;background:rgba(255,160,0,0.08);border:1px solid rgba(255,160,0,0.3);border-radius:8px">
               ℹ️ <strong>Figure/Diagram Reference:</strong> The options for this question require visual diagrams from the official GATE paper.
             </div>`
          : `<div class="options-list">${(q.options||[]).map((opt,i)=>`

             <div class="option-item ${sel.has(i)?'selected':''}" data-idx="${i}">

               <div class="option-label">${labels[i]}</div>

               <div class="option-text">${formatQuestionContent(opt)}</div>

             </div>`).join('')}</div>`}

    </div>

    <div class="question-actions">

      <button class="btn btn-primary" onclick="saveAndNextTestQ()">Save & Next →</button>

      <button class="btn btn-secondary" onclick="markForReview()">🔖 Mark</button>

      <button class="btn btn-secondary" onclick="jumpToNextUnanswered()" title="Jump to Next Unanswered Question (U)" type="button">⏩ Unanswered (U)</button>

      <button class="btn btn-secondary" onclick="jumpToNextMarked()" title="Jump to Next Marked for Review (M)" type="button">🔖 Next Marked (M)</button>

      <button class="btn btn-secondary" onclick="clearTestResponse()">Clear</button>

      ${currentQ>0?`<button class="btn btn-secondary" onclick="jumpToTestQ(${currentQ-1})">← Prev</button>`:''}

    </div>`;

  updatePaletteBtn(currentQ,'current');

  document.querySelectorAll('.option-item').forEach(item=>{

    item.addEventListener('click',()=>{

      const idx=parseInt(item.dataset.idx);

      if (q.type==='msq'){

        if(practiceSelectedOpts.has(idx)){practiceSelectedOpts.delete(idx);item.classList.remove('selected');}

        else{practiceSelectedOpts.add(idx);item.classList.add('selected');}

      } else {

        document.querySelectorAll('.option-item').forEach(i=>i.classList.remove('selected'));

        practiceSelectedOpts.clear(); practiceSelectedOpts.add(idx); item.classList.add('selected');

      }

    });

  });

  renderMath(main);



  // Mobile swipe left/right navigation

  let touchStartX = 0, touchStartY = 0;

  main.ontouchstart = (e) => {

    if (e.touches && e.touches[0]) {

      touchStartX = e.touches[0].screenX;

      touchStartY = e.touches[0].screenY;

    }

  };

  main.ontouchend = (e) => {

    if (e.changedTouches && e.changedTouches[0]) {

      const dx = e.changedTouches[0].screenX - touchStartX;

      const dy = e.changedTouches[0].screenY - touchStartY;

      if (Math.abs(dx) > 60 && Math.abs(dy) < 55) {

        if (dx < 0) {

          saveAndNextTestQ(); // Swiped left -> Next

        } else if (state.activeTest && state.activeTest.currentQ > 0) {

          jumpToTestQ(state.activeTest.currentQ - 1); // Swiped right -> Prev

        }

      }

    }

  };



}



function saveNATAnswer(v){ state.activeTest.answers[state.activeTest.currentQ]=v!==''?parseFloat(v):null; updatePaletteBtn(state.activeTest.currentQ,'attempted'); }

function saveAndNextTestQ(){

  if (!state.activeTest) return;

  const {questions,currentQ}=state.activeTest; const q=questions[currentQ];

  if (q.type==='nat'){const inp=document.getElementById('nat-answer');state.activeTest.answers[currentQ]=inp?.value?.trim()!==''?parseFloat(inp.value):null;}

  else{const a=[...practiceSelectedOpts];state.activeTest.answers[currentQ]=a.length?a:null;}

  if (!state.activeTest.visited) state.activeTest.visited = new Set([0]);

  state.activeTest.visited.add(currentQ);

  if (currentQ<questions.length-1){

    state.activeTest.currentQ++;

    state.activeTest.visited.add(state.activeTest.currentQ);

    renderTestQuestion();

  } else {

    confirmSubmitTest();

  }

  updatePaletteStates();

  saveExamAutoSaveState();

}

function markForReview(){

  if (!state.activeTest) return;

  const {currentQ,marked}=state.activeTest;

  if (marked.has(currentQ)) marked.delete(currentQ); else marked.add(currentQ);

  if (!state.activeTest.visited) state.activeTest.visited = new Set([0]);

  state.activeTest.visited.add(currentQ);

  updatePaletteStates();

  saveExamAutoSaveState();

}

function clearTestResponse(){

  if (!state.activeTest) return;

  state.activeTest.answers[state.activeTest.currentQ]=null; practiceSelectedOpts=new Set();

  document.querySelectorAll('.option-item').forEach(i=>i.classList.remove('selected'));

  const n=document.getElementById('nat-answer'); if(n) n.value='';

  if (!state.activeTest.visited) state.activeTest.visited = new Set([0]);

  state.activeTest.visited.add(state.activeTest.currentQ);

  updatePaletteStates();

  saveExamAutoSaveState();

}

function jumpToTestQ(i){

  if (!state.activeTest || i < 0 || i >= state.activeTest.questions.length) return;

  const {currentQ,questions}=state.activeTest; const q=questions[currentQ];

  if(q && q.type!=='nat'){const a=[...practiceSelectedOpts];state.activeTest.answers[currentQ]=a.length?a:null;}

  if (!state.activeTest.visited) state.activeTest.visited = new Set([0]);

  state.activeTest.visited.add(currentQ);

  state.activeTest.currentQ=i;

  state.activeTest.visited.add(i);

  const tabGa = document.getElementById('sec-tab-ga');
  const tabCs = document.getElementById('sec-tab-cs');
  if (tabGa && tabCs) {
    tabGa.classList.toggle('active', i < 10);
    tabCs.classList.toggle('active', i >= 10);
  }

  renderTestQuestion();

  updatePaletteStates();

  saveExamAutoSaveState();

  if (window.innerWidth <= 768) {

    document.getElementById('test-sidebar')?.classList.remove('mobile-open');

    document.getElementById('palette-backdrop')?.classList.remove('active');

  }

}

function updatePaletteBtn(i,cls){ const b=document.getElementById(`pb-${i}`); if(!b) return; b.className='palette-btn'; if(cls) b.classList.add(cls); }

function confirmSubmitTest(){ if(confirm('Submit the test now?')) submitMockTest(); }



async function submitMockTest(){

  playUiSuccessChime();

  stopMockTimer();

  clearExamAutoSave();

  const {mock,questions,answers,timeLeft}=state.activeTest;

  state.activeTest.submitted=true;

  let score=0,correct=0,wrong=0,skipped=0;

  const answeredAttempts = [];



  questions.forEach((q,i)=>{

    const a=answers[i];

    if(a===null||a===undefined||(Array.isArray(a)&&!a.length)){skipped++;return;}

    let ok=false;

    if(q.type==='nat'){const v=parseFloat(a),e=q.correct[0];ok=v>=(q.natRange?.min??e)&&v<=(q.natRange?.max??e);}

    else{const s=(Array.isArray(a)?a:[a]).sort((x,y)=>x-y),e=[...q.correct].sort((x,y)=>x-y);ok=s.length===e.length&&s.every((v,idx)=>v===e[idx]);}

    if(ok){correct++;score+=q.marks;}else{wrong++;score-=q.marks===2?2/3:1/3;}



    const qDwellSec = (state.activeTest.timePerQ && state.activeTest.timePerQ[i]) || Math.round((mock.duration * 60 - timeLeft) / Math.max(1, questions.length));

    answeredAttempts.push({

      questionId: q.id,

      correct: ok,

      timeMs: qDwellSec * 1000,

      date: Date.now(),

      uid: uid()

    });

  });



  const maxScore=questions.reduce((s,q)=>s+q.marks,0);

  const pct=Math.max(0,Math.round((score/maxScore)*100));

  const session={mockId:mock.id,name:mock.name,provider:mock.provider||'',date:Date.now(),score:Math.max(0,parseFloat(score.toFixed(2))),maxScore,percentage:pct,correct,wrong,skipped,timeTaken:mock.duration*60-timeLeft,timePerQ:[...(state.activeTest.timePerQ||[])],tabSwitches:state.activeTest.tabSwitches||0};

  

  await persistSession(session);

  // Persist each answered question attempt to sync Dashboard Tests Completed, Questions Attempted, and Accuracy

  for (const att of answeredAttempts) {

    await persistAttempt(att);

  }



  document.getElementById('test-overlay').innerHTML='';

  document.getElementById('test-overlay').classList.remove('active');

  showTestResult(session,questions,answers);

  // Update SRS for all answered questions

  questions.forEach(function(q, i) {

    var a = answers[i];

    if (a === null || (Array.isArray(a) && !a.length) || !q || !q.id) return;

    var ok = false;

    if (q.type === 'nat') { var v=parseFloat(a), e=q.correct[0]; ok=v>=(q.natRange&&q.natRange.min!=null?q.natRange.min:e)&&v<=(q.natRange&&q.natRange.max!=null?q.natRange.max:e); }

    else { var s=(Array.isArray(a)?a:[a]).slice().sort(function(x,y){return x-y}), c=q.correct.slice().sort(function(x,y){return x-y}); ok=s.length===c.length&&s.every(function(v,idx){return v===c[idx];}); }

    updateSRSAfterAttempt(q.id, ok);

  });

}



function startMockTimer(){

  stopMockTimer();

  mockTimerInterval=setInterval(()=>{

    if(!state.activeTest||state.activeTest.submitted){stopMockTimer();return;}

    state.activeTest.timeLeft--;

    if (!state.activeTest.timePerQ) state.activeTest.timePerQ = new Array(state.activeTest.questions.length).fill(0);

    const curQ = state.activeTest.currentQ || 0;

    state.activeTest.timePerQ[curQ] = (state.activeTest.timePerQ[curQ] || 0) + 1;

    

    // Auto-save exam every 5 seconds

    if (state.activeTest.timeLeft % 5 === 0) saveExamAutoSaveState();



    // Exam pacing countdown chimes & Invigilator Milestone Notices

    if (state.activeTest.timeLeft === 3600) {

      triggerPacingChime('60min');

      showExamMilestoneNotice('⏳ INVIGILATOR NOTICE: 1 Hour Remaining', 'Pacing recommendation: You should have answered ~45 questions by now.');

    } else if (state.activeTest.timeLeft === 1800) {

      triggerPacingChime('30min');

      showExamMilestoneNotice('⚠️ INVIGILATOR NOTICE: 30 Minutes Remaining', 'Time to review "Marked for Review" questions and high-confidence NATs.');

    } else if (state.activeTest.timeLeft === 600) {

      triggerPacingChime('10min');

      showExamMilestoneNotice('🚨 INVIGILATOR NOTICE: 10 Minutes Remaining', 'Final lock-in phase. Verify all numerical keypad entries.');

    } else if (state.activeTest.timeLeft === 120) {

      triggerPacingChime('2min');

      showExamMilestoneNotice('⚡ 2 MINUTES REMAINING', 'Test will automatically submit when timer reaches 00:00:00.');

    }



    const el=document.getElementById('test-timer-display');

    if(el){el.textContent=fmtH(state.activeTest.timeLeft);el.className='test-timer-display';if(state.activeTest.timeLeft<=300)el.classList.add('warning');if(state.activeTest.timeLeft<=60)el.classList.add('danger');}

    if(state.activeTest.timeLeft<=0) submitMockTest();

  },1000);

}

function stopMockTimer(){ if(mockTimerInterval){clearInterval(mockTimerInterval);mockTimerInterval=null;} }



// ─── RESULT SCREEN ───────────────────────────────────────────────────────────

function showTestResult(session,questions,answers){

  state.activeTestResults = { session, questions, answers };

  const ov=document.getElementById('result-overlay');

  const pct=session.percentage;

  const grade=pct>=85?'🏆 Excellent':pct>=70?'🌟 Good':pct>=50?'📈 Average':'📚 Need More Practice';

  const labels=['A','B','C','D','E'];

  const times = session.timePerQ || new Array(questions.length).fill(0);

  const totalSec = session.timeTaken || times.reduce((a,b)=>a+b, 0) || 1;

  const avgSec = Math.round(totalSec / Math.max(1, questions.length));



  // Compute pacing stats

  let correctSec = 0, wrongSec = 0, skipSec = 0, overtimeCount = 0;

  questions.forEach((q, i) => {

    const a = answers[i];

    const isSkip = a === null || (Array.isArray(a) && !a.length);

    const qSec = times[i] || 0;

    if (qSec > 210) overtimeCount++;

    if (isSkip) {

      skipSec += qSec;

    } else {

      let isOk = false;

      if (q.type === 'nat') {

        const v = parseFloat(a), e = q.correct[0];

        isOk = v >= (q.natRange?.min ?? e) && v <= (q.natRange?.max ?? e);

      } else {

        const s = (Array.isArray(a) ? a : [a]).sort((x, y) => x - y), e = [...q.correct].sort((x, y) => x - y);

        isOk = s.length === e.length && s.every((v, idx) => v === e[idx]);

      }

      if (isOk) correctSec += qSec;

      else wrongSec += qSec;

    }

  });



  const avgCorrect = session.correct > 0 ? Math.round(correctSec / session.correct) : 0;

  const avgWrong = session.wrong > 0 ? Math.round(wrongSec / session.wrong) : 0;



  // Predictor calculation for this test

  const pred = calculateGatePrediction(session.score, state.predictedCategory || 'GEN');



  ov.innerHTML=`

    <div class="result-hero">

      <div class="result-score-ring" style="--pct:${pct}">

        <div class="result-score-inner">

          <div class="result-score-pct">${pct}%</div>

          <div class="result-score-label">Score</div>

        </div>

      </div>

      <div class="result-title">${grade}</div>

      <div class="result-subtitle">${session.name}${session.provider ? ` • ${session.provider}` : ''}</div>

      <div class="result-stats">

        <div class="result-stat"><div class="result-stat-value" style="color:var(--green)">${session.correct}</div><div class="result-stat-label">Correct</div></div>

        <div class="result-stat"><div class="result-stat-value" style="color:var(--red)">${session.wrong}</div><div class="result-stat-label">Wrong</div></div>

        <div class="result-stat"><div class="result-stat-value" style="color:var(--text-muted)">${session.skipped}</div><div class="result-stat-label">Skipped</div></div>

        <div class="result-stat"><div class="result-stat-value">${session.score}/${session.maxScore}</div><div class="result-stat-label">Marks</div></div>

        <div class="result-stat"><div class="result-stat-value">${fmtH(session.timeTaken)}</div><div class="result-stat-label">Time</div></div>

        ${session.tabSwitches > 0 ? `<div class="result-stat"><div class="result-stat-value" style="color:var(--red)">${session.tabSwitches}</div><div class="result-stat-label">Tab Switches</div></div>` : ''}

      </div>

      <div style="margin-top:20px;display:flex;gap:12px;justify-content:center;flex-wrap:wrap">

        <button class="btn btn-white" onclick="closeResult()">🏠 Home</button>

        <button class="btn btn-outline-white" onclick="navigate('mocks')">🎯 All Tests</button>

        <button class="btn btn-secondary btn-sm" onclick="printTestReport()" style="background:rgba(255,255,255,0.15);color:#fff">🖨️ Print / Save PDF</button>

        <button class="btn btn-secondary btn-sm" onclick="navigate('mistakes')" style="background:rgba(239,68,68,0.2);color:#ff8888">📖 Review Mistakes</button>

      </div>

    </div>

    <div class="result-content">

      <!-- ── QUESTION-WISE TIME & PACING ANALYTICS ── -->

      <div class="section-title mb-2">⏱️ Question-Wise Pacing Analytics</div>

      <div class="pacing-analytics-grid">

        <div class="pacing-stat-card">

          <div class="pacing-stat-val">${fmtSec(avgSec)}</div>

          <div class="pacing-stat-lbl">Avg Time / Question</div>

        </div>

        <div class="pacing-stat-card">

          <div class="pacing-stat-val" style="color:var(--green)">${fmtSec(avgCorrect)}</div>

          <div class="pacing-stat-lbl">Avg on Correct Qs</div>

        </div>

        <div class="pacing-stat-card">

          <div class="pacing-stat-val" style="color:var(--red)">${fmtSec(avgWrong)}</div>

          <div class="pacing-stat-lbl">Avg on Incorrect Qs</div>

        </div>

        <div class="pacing-stat-card">

          <div class="pacing-stat-val" style="color:${overtimeCount > 5 ? 'var(--red)' : 'var(--accent)'}">${overtimeCount} Qs</div>

          <div class="pacing-stat-lbl">Pacing Warnings (>3.5m)</div>

        </div>

      </div>



      <!-- ── ESTIMATED GATE SCORE & RANK PREDICTION ── -->

      <div class="predictor-card" style="margin-top:16px">

        <div class="predictor-card-header">

          <div class="predictor-title">🎯 Estimated GATE Performance Predictor</div>

          <span class="badge" style="background:rgba(108,99,255,0.2);color:var(--accent)">Based on this Test</span>

        </div>

        <div class="predictor-output-grid">

          <div class="predictor-output-box">

            <div style="font-size:11px;color:var(--text-muted);font-weight:700;text-transform:uppercase">Estimated GATE Score</div>

            <div class="predictor-score-huge">${pred.score} <span style="font-size:14px;color:var(--text-muted);font-weight:600">/ 1000</span></div>

          </div>

          <div class="predictor-output-box">

            <div style="font-size:11px;color:var(--text-muted);font-weight:700;text-transform:uppercase">Estimated All India Rank (AIR)</div>

            <div class="predictor-air-huge" style="color:${pred.airBadgeClass}">${pred.air}</div>

          </div>

        </div>

        <div class="predictor-eligibility-badge">${pred.eligibility}</div>

      </div>



      ${buildQuestionTimeHeatmapHTML(session, questions, answers)}

      ${buildNegativeMarksAuditHTML(session, questions, answers)}

      ${buildGaussianBellCurveSVG(session.score, session.maxScore)}

      ${buildSectionAnalysisHTML(session, questions, answers)}

      ${buildLossDiagnosisHTML(session, questions, answers)}

      ${buildQuadrantAnalysisHTML()}

      <div style="display:flex;gap:10px;margin:20px 0 16px 0;flex-wrap:wrap">

        <button class="btn btn-primary btn-sm" onclick="exportReviewWorksheetPDF()" type="button" style="display:inline-flex;align-items:center;gap:6px">

          📄 Print 2-Column PDF Practice Worksheet

        </button>

        <button class="btn btn-secondary btn-sm" onclick="printTestReport()" type="button" style="display:inline-flex;align-items:center;gap:6px">

          🖨️ Print Test Report

        </button>

        <button class="btn btn-secondary btn-sm copy-scorecard-btn" onclick="copyScorecardToClipboard()" type="button">

          📋 Copy Scorecard

        </button>

      </div>

      <div class="section-title mb-4" style="margin-top:14px">Detailed Question Review</div>

      <div class="result-review-filters" style="display:flex;gap:8px;margin-bottom:16px;flex-wrap:wrap">
        <button class="chip active" id="rf-all" onclick="filterResultReview('all', this)" type="button">All (${questions.length})</button>
        <button class="chip" id="rf-wrong" onclick="filterResultReview('wrong', this)" type="button" style="color:var(--red);border-color:rgba(239,68,68,0.4)">❌ Wrong (${session.incorrectCount})</button>
        <button class="chip" id="rf-skip" onclick="filterResultReview('skip', this)" type="button" style="color:var(--text-muted)">⚪ Unattempted (${session.unattemptedCount})</button>
        <button class="chip" id="rf-correct" onclick="filterResultReview('correct', this)" type="button" style="color:var(--green);border-color:rgba(34,197,94,0.4)">✅ Correct (${session.correctCount})</button>
        <button class="chip" id="rf-overtime" onclick="filterResultReview('overtime', this)" type="button" style="color:var(--accent);border-color:rgba(108,99,255,0.4)">⏱️ Overtime >3.5m (${overtimeCount})</button>
      </div>

      ${questions.map((q,i)=>{

        const a=answers[i]; const skip=a===null||(Array.isArray(a)&&!a.length);

        let ok=false;

        if(!skip){if(q.type==='nat'){const v=parseFloat(a),e=q.correct[0];ok=v>=(q.natRange?.min??e)&&v<=(q.natRange?.max??e);}else{const s=(Array.isArray(a)?a:[a]).sort((x,y)=>x-y),e=[...q.correct].sort((x,y)=>x-y);ok=s.length===e.length&&s.every((v,idx)=>v===e[idx]);}}

        const clr=skip?'var(--text-muted)':ok?'var(--green)':'var(--red)';

        const lbl=skip?'⚪ Skipped':ok?'✅ Correct':'❌ Wrong';

        const yourAns=skip?'Not attempted':q.type==='nat'?`${a}`:(Array.isArray(a)?a:[a]).map(i=>labels[i]+'.'+(q.options?.[i]||'')).join(', ');

        const corrAns=q.type==='nat'?`${q.correct[0]}`:q.correct.map(i=>labels[i]+'.'+(q.options?.[i]||'')).join(', ');

        const qSec = times[i] || 0;

        const timeCls = qSec <= 90 ? 'time-spent-fast' : qSec <= 210 ? 'time-spent-optimal' : 'time-spent-warning';

        const isBmk = state.bookmarks?.has(q.id);



        return `<div class="card mb-4 review-q-card" id="result-q-${i}" data-review-status="${skip ? 'skip' : ok ? 'correct' : 'wrong'}" data-overtime="${qSec > 210 ? '1' : '0'}" style="border-left:3px solid ${clr}">

          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;flex-wrap:wrap;gap:8px">

            <div style="display:flex;align-items:center;gap:8px">

              <span class="chip">Q${i+1}</span>

              <span class="chip chip-info">${q.subject}</span>

              <span class="time-spent-badge ${timeCls}">⏱️ ${fmtSec(qSec)}${qSec > 210 ? ' • Overtime' : ''}</span>

            </div>

            <div style="display:flex;align-items:center;gap:8px">

              <button class="btn btn-secondary btn-sm" onclick="promptQuestionNote('${q.id}')" style="padding:2px 8px;font-size:11px" type="button">

                📝 ${state.questionNotes?.[q.id] ? 'Edit Note' : 'Add Note'}

              </button>

              <button class="btn btn-secondary btn-sm" onclick="openPlaylistModal('${q.id}')" style="padding:2px 8px;font-size:11px" title="Add to Smart Playlist" type="button">

                🗂️ Playlist

              </button>

              <button class="btn btn-secondary btn-sm" onclick="toggleBookmark('${q.id}'); this.innerHTML = state.bookmarks.has('${q.id}') ? '⭐ Bookmarked' : '☆ Star';" style="padding:2px 8px;font-size:11px" type="button">

                ${isBmk ? '⭐ Bookmarked' : '☆ Star'}

              </button>

              <span style="font-size:13px;font-weight:700;color:${clr}">${lbl}</span>

            </div>

          </div>

          <div style="font-size:14px;line-height:1.7;margin-bottom:12px;font-weight:500">${formatQuestionContent(q.question)}</div>

          <div style="font-size:13px;color:var(--text-secondary);margin-bottom:4px">Your: <strong>${formatQuestionContent(yourAns)}</strong></div>

          ${!ok?`<div style="font-size:13px;color:var(--green);margin-bottom:8px">Correct: <strong>${formatQuestionContent(corrAns)}</strong></div>`:''}

          <div class="explanation-box show" style="display:block">

            ${buildConfidenceSelectorHTML(q.id)}

            ${buildExpectedValueCardHTML(q)}

            ${q.type === 'nat' ? buildNatToleranceHTML(q) : ''}

            ${buildMultiMethodExplanationHTML(q)}

            ${buildStudentShortcutNoteHTML(q.id)}

          </div>

          ${!ok ? buildErrorTagButtonsHTML(q.id, state.errorTags?.[q.id]) : ''}

          ${state.questionNotes?.[q.id] ? `

            <div class="question-note-box">

              <div class="question-note-header">

                <span>📌 PERSONAL REVISION NOTE:</span>

                <button class="btn btn-secondary btn-sm" onclick="promptQuestionNote('${q.id}')" style="padding:1px 6px;font-size:10px">Edit</button>

              </div>

              <div>${escapeHtml(state.questionNotes[q.id])}</div>

            </div>` : ''}

        </div>`;

      }).join('')}

    </div>`;

  ov.classList.add('active'); ov.scrollTop=0;

  renderMath(ov);

  setTimeout(() => highlightCodeBlocks(ov), 200);

}



function closeResult(){

  const ov=document.getElementById('result-overlay');

  ov.innerHTML=''; ov.classList.remove('active'); navigate('dashboard');

}



// ─── GATE CSE SYLLABUS TOPIC NORMALIZER & TAXONOMY ────────────────────────────

function getTopicPYQChapter(q) {

  if (!q) return 'General Core CSE';

  if (q._topicChapter) return q._topicChapter;

  

  const sub = q.subject || 'General';

  const top = (q.topic || '').trim();

  const txt = ((q.question || '') + ' ' + (q.explanation || '')).toLowerCase();

  

  let chapter = 'General Core CSE';

  

  if (sub === 'Operating Systems') {

    if (/deadlock|banker|resource allocation graph/i.test(top) || /deadlock|banker|circular wait/i.test(txt)) {

      chapter = 'Deadlocks & Resource Allocation';

    } else if (/schedul|round robin|fcfs|sjf|srtf|priority|preempt/i.test(top) || /cpu scheduling|arrival time|burst time|turnaround/i.test(txt)) {

      chapter = 'CPU Scheduling & Process Dispatching';

    } else if (/synchron|semaphore|mutex|critical section|peterson|producer/i.test(top) || /semaphore|critical section|mutex|producer-consumer/i.test(txt)) {

      chapter = 'Process Synchronization & Concurrency';

    } else if (/virtual memory|replacement|lru|fifo|belady|thrashing/i.test(top) || /tlb|page fault|page table|page replacement|inverted page|virtual address/i.test(txt)) {

      chapter = 'Virtual Memory & Page Replacement';

    } else if (/paging|memory management|segmentation|fragmentation|buddy|allocation/i.test(top) || /memory allocation|internal fragmentation|external fragmentation/i.test(txt)) {

      chapter = 'Main Memory & Paging Schemes';

    } else if (/disk|file|i\/o|cylinder|seek|sstf|scan|c-scan|inode/i.test(top) || /disk scheduling|seek time|inode|file system|directory/i.test(txt)) {

      chapter = 'File Systems & Disk Scheduling';

    } else if (/fork|thread|process|system call/i.test(top) || /fork\(\)|exec\(\)|zombie|orphan|system call/i.test(txt)) {

      chapter = 'Processes, Threads & System Calls';

    } else {

      chapter = 'OS Architecture & Core Concepts';

    }

  } else if (sub === 'DBMS') {

    if (/b\+ tree|b-tree|index|hash index/i.test(top) || /b\+ tree|indexing|b-tree|dense index|sparse index/i.test(txt)) {

      chapter = 'Indexing, B-Trees & B+ Trees';

    } else if (/normal|functional depend|lossless|dependency preserv|3nf|bcnf|2nf/i.test(top) || /functional dependency|canonical cover|minimal cover|lossless decomposition|3nf|bcnf/i.test(txt)) {

      chapter = 'Functional Dependencies & Normalization';

    } else if (/transact|concurren|serializ|recover|acid|timestamp|2pl|two-phase/i.test(top) || /serializable|conflict serializable|view serializable|two-phase locking|acid|deadlock in dbms/i.test(txt)) {

      chapter = 'Transactions & Concurrency Control';

    } else if (/sql|query|join|group by|having|aggregate/i.test(top) || /select |from |where |group by|having|count\(/i.test(txt)) {

      chapter = 'SQL Queries & Relational Operations';

    } else if (/relational algebra|relational calculus|tuple relational|domain relational/i.test(top) || /relational algebra|projection|selection|cross product|natural join|tuple relational/i.test(txt)) {

      chapter = 'Relational Algebra & Calculus';

    } else if (/er model|entity|relationship|cardinality|weak entity/i.test(top) || /er diagram|entity relationship|cardinality ratio|weak entity/i.test(txt)) {

      chapter = 'ER Modeling & Relational Schema Design';

    } else {

      chapter = 'DBMS Architecture & Query Processing';

    }

  } else if (sub === 'Algorithms') {

    if (/asymptotic|complexity|recurren|master theorem|big-o|growth/i.test(top) || /asymptotic|time complexity|recurrence relation|master theorem|order of growth/i.test(txt)) {

      chapter = 'Asymptotic Analysis & Recurrences';

    } else if (/sort|median|order statistic|quick sort|merge sort|heap sort|counting sort/i.test(top) || /sorting|quicksort|mergesort|heapsort|selection sort|insertion sort|inversion/i.test(txt)) {

      chapter = 'Sorting, Searching & Order Statistics';

    } else if (/graph|mst|dijkstra|bellman|spanning tree|shortest path|kruskal|prim|bfs|dfs|topological/i.test(top) || /shortest path|minimum spanning tree|dijkstra|kruskal|prim|dag|topological sort/i.test(txt)) {

      chapter = 'Graph Algorithms & Shortest Paths';

    } else if (/dynamic programming|optimal substructure|memoiz|lcs|matrix chain|knapsack/i.test(top) || /dynamic programming|memoization|longest common subsequence|0\/1 knapsack|matrix chain/i.test(txt)) {

      chapter = 'Dynamic Programming & Memoization';

    } else if (/greedy|huffman|activity selection|interval/i.test(top) || /greedy algorithm|huffman coding|fractional knapsack|job sequencing/i.test(txt)) {

      chapter = 'Greedy Algorithms & Design';

    } else if (/np-complete|np-hard|polynomial|reduction|sat|clique|vertex cover/i.test(top) || /np-complete|np-hard|polynomial time reduction|3-sat|independent set/i.test(txt)) {

      chapter = 'NP-Completeness & Complexity Classes';

    } else if (/divide and conquer|strassen/i.test(top) || /divide and conquer/i.test(txt)) {

      chapter = 'Divide & Conquer Strategies';

    } else if (/software|waterfall|srs|agile|coupling|cohesion|testing/i.test(txt)) {

      chapter = 'Software Engineering (Legacy GATE)';

    } else if (/html|css|javascript|web|http|url/i.test(txt)) {

      chapter = 'Web Technologies (Legacy GATE)';

    } else {

      chapter = 'Advanced Algorithm Design & Mixed';

    }

  } else if (sub === 'Theory of Computation') {

    if (/regular expression|dfa|nfa|finite automata|minimization/i.test(top) || /dfa|nfa|finite automaton|regular expression|minimal dfa|state minimization/i.test(txt)) {

      chapter = 'Finite Automata & Regular Expressions';

    } else if (/regular language|pumping lemma for regular|closure of regular/i.test(top) || /regular language|pumping lemma|closure properties.*regular/i.test(txt)) {

      chapter = 'Regular Languages & Properties';

    } else if (/cfg|context-free grammar|grammar|ambiguity|derivation/i.test(top) || /context-free grammar|cfg|ambiguous grammar|chomsky normal form|greibach/i.test(txt)) {

      chapter = 'Context-Free Grammars & Ambiguity';

    } else if (/pda|pushdown|context-free language|cfl|dcfl/i.test(top) || /pushdown automata|pda|dcfl|deterministic context-free/i.test(txt)) {

      chapter = 'Pushdown Automata & Context-Free Languages';

    } else if (/turing|decidab|undecidab|halting|recursive|recursively enumerable/i.test(top) || /turing machine|undecidable|decidable|halting problem|recursively enumerable/i.test(txt)) {

      chapter = 'Turing Machines & Decidability';

    } else if (/chomsky hierarchy|closure properties/i.test(top) || /chomsky hierarchy|closure properties/i.test(txt)) {

      chapter = 'Chomsky Hierarchy & Closure Properties';

    } else {

      chapter = 'TOC Formal Models & Automata';

    }

  } else if (sub === 'Computer Networks') {

    if (/ip addressing|subnet|cidr|ipv4|ipv6|routing|network layer/i.test(top) || /ip address|subnet mask|cidr|routing table|distance vector|link state|ospf|bgp/i.test(txt)) {

      chapter = 'Network Layer, IPv4/v6 & Routing';

    } else if (/tcp|udp|transport layer|congestion|flow control|window/i.test(top) || /tcp|udp|congestion control|sliding window|slow start|congestion avoidance|three-way handshake/i.test(txt)) {

      chapter = 'Transport Layer, TCP & Congestion Control';

    } else if (/data link|framing|sliding window|error|crc|hamming|flow control/i.test(top) || /framing|crc|hamming code|go-back-n|selective repeat|stop and wait/i.test(txt)) {

      chapter = 'Data Link Layer & Flow/Error Control';

    } else if (/mac|csma\/cd|aloha|ethernet|collision/i.test(top) || /csma\/cd|carrier sense|aloha|backoff|collision detection|transmission time/i.test(txt)) {

      chapter = 'MAC Sublayer, Ethernet & CSMA/CD';

    } else if (/application layer|dns|http|smtp|ftp|security|cryptography|rsa/i.test(top) || /dns|http|smtp|ftp|rsa|public key|cipher|firewall/i.test(txt)) {

      chapter = 'Application Layer Protocols & Network Security';

    } else {

      chapter = 'Network Architecture & Protocols';

    }

  } else if (sub === 'Computer Organization') {

    if (/cache|memory hierarchy|direct mapped|set associative|hit ratio|replacement/i.test(top) || /cache memory|hit ratio|miss penalty|tag bits|set-associative|write-through/i.test(txt)) {

      chapter = 'Cache Memory & Memory Hierarchy';

    } else if (/pipelin|hazard|speedup|branch|forwarding/i.test(top) || /pipeline|hazard|speedup|clock cycle|stalls|forwarding/i.test(txt)) {

      chapter = 'Instruction Pipelining & Hazards';

    } else if (/addressing mode|instruction set|isa|format|opcode/i.test(top) || /addressing mode|instruction format|opcode|effective address/i.test(txt)) {

      chapter = 'Instruction Formats & Addressing Modes';

    } else if (/interrupt|i\/o|dma|programmed i\/o/i.test(top) || /interrupt|dma|vectored interrupt|cycle stealing|i\/o interface/i.test(txt)) {

      chapter = 'I/O Organization, Interrupts & DMA';

    } else if (/floating point|ieee 754|alu|arithmetic/i.test(top) || /ieee 754|floating point|mantissa|exponent|booth/i.test(txt)) {

      chapter = 'Data Representation & Computer Arithmetic';

    } else if (/control unit|datapath|microprogramm/i.test(top) || /control unit|microprogrammed|hardwired|datapath/i.test(txt)) {

      chapter = 'CPU Datapath & Control Unit Design';

    } else {

      chapter = 'Computer Organization & Architecture';

    }

  } else if (sub === 'Data Structures') {

    if (/bst|binary search tree|avl|b-tree|balanced/i.test(top) || /binary search tree|bst|avl tree|rotation|balanced tree/i.test(txt)) {

      chapter = 'Binary Search Trees & Balanced BSTs';

    } else if (/tree|binary tree|traversal|inorder|preorder|postorder/i.test(top) || /binary tree|inorder|preorder|postorder|tree traversal/i.test(txt)) {

      chapter = 'Binary Trees & Tree Traversals';

    } else if (/heap|priority queue/i.test(top) || /binary heap|max heap|min heap|heapify|priority queue/i.test(txt)) {

      chapter = 'Heaps & Priority Queues';

    } else if (/stack|queue/i.test(top) || /stack|queue|push|pop|lifo|fifo|postfix|infix/i.test(txt)) {

      chapter = 'Stacks, Queues & Evaluation of Expressions';

    } else if (/hash|collision|probe/i.test(top) || /hash table|hashing|collision resolution|chaining|open addressing/i.test(txt)) {

      chapter = 'Hash Tables & Collision Resolution';

    } else if (/linked list|singly|doubly|circular/i.test(top) || /linked list|pointer to next|node/i.test(txt)) {

      chapter = 'Linked Lists & Dynamic Structures';

    } else if (/graph/i.test(top) || /adjacency matrix|adjacency list|graph representation/i.test(txt)) {

      chapter = 'Graph Representations';

    } else {

      chapter = 'Core Data Structures & Abstract Types';

    }

  } else if (sub === 'Digital Logic') {

    if (/boolean|k-map|minimization|sop|pos/i.test(top) || /boolean algebra|k-map|karnaugh|sop|pos|minterm|maxterm|prime implicant/i.test(txt)) {

      chapter = 'Boolean Algebra & K-Map Minimization';

    } else if (/number system|conversion|2's complement|1's complement|binary/i.test(top) || /2's complement|binary number|hexadecimal|excess-3|gray code|number system/i.test(txt)) {

      chapter = 'Number Systems & Binary Representations';

    } else if (/combinational|multiplexer|decoder|adder|demux/i.test(top) || /multiplexer|mux|decoder|full adder|half adder|priority encoder/i.test(txt)) {

      chapter = 'Combinational Logic & Circuits (MUX, Decoders)';

    } else if (/sequential|flip-flop|latch|state machine|setup|hold/i.test(top) || /flip-flop|jk flip-flop|d flip-flop|setup time|hold time|state transition/i.test(txt)) {

      chapter = 'Sequential Circuits & Flip-Flops';

    } else if (/counter|register|shift register/i.test(top) || /counter|mod-|ripple counter|synchronous counter|johnson counter|shift register/i.test(txt)) {

      chapter = 'Registers & Synchronous/Asynchronous Counters';

    } else {

      chapter = 'Digital Logic & Switching Circuits';

    }

  } else if (sub === 'Compiler Design') {

    if (/lexical|token|regex|scanner/i.test(top) || /lexical analysis|token|lex|lexeme|scanner/i.test(txt)) {

      chapter = 'Lexical Analysis & Token Generation';

    } else if (/pars|lr|ll|first and follow|slr|lalr|clr/i.test(top) || /ll\(1\)|lr\(0\)|slr|lalr|clr|shift-reduce|first.*follow|parsing table/i.test(txt)) {

      chapter = 'Parsing Techniques (LL, LR, SLR, LALR)';

    } else if (/syntax directed|sdt|attribute|synthesized|inherited/i.test(top) || /syntax-directed|sdt|s-attributed|l-attributed|semantic action/i.test(txt)) {

      chapter = 'Syntax Directed Translation (SDT)';

    } else if (/intermediate code|three address|quadruple|triple/i.test(top) || /intermediate code|three-address code|3ac|quadruple|triple/i.test(txt)) {

      chapter = 'Intermediate Code Generation (TAC)';

    } else if (/optimization|basic block|flow graph|dead code|loop/i.test(top) || /code optimization|basic block|control flow graph|dead code elimination|constant folding/i.test(txt)) {

      chapter = 'Code Optimization & Flow Graphs';

    } else if (/symbol table|runtime|activation record/i.test(top) || /symbol table|activation record|runtime environment/i.test(txt)) {

      chapter = 'Symbol Tables & Runtime Environments';

    } else {

      chapter = 'Compiler Phases & Architecture';

    }

  } else if (sub === 'Discrete Mathematics') {

    if (/graph theory|planar|euler|hamilton|coloring|chromatic|bipartite/i.test(top) || /graph theory|planar graph|chromatic number|eulerian|bipartite graph|clique|degree/i.test(txt)) {

      chapter = 'Graph Theory & Invariants';

    } else if (/relation|function|poset|lattice|equivalence|partial order/i.test(top) || /equivalence relation|partial order|poset|hasse diagram|lattice|bijective|injective/i.test(txt)) {

      chapter = 'Sets, Relations, Functions & Lattices';

    } else if (/logic|proposition|predicate|tautology|quantifier|valid/i.test(top) || /propositional logic|truth table|tautology|predicate logic|first order logic|well formed formula/i.test(txt)) {

      chapter = 'Propositional & First-Order Predicate Logic';

    } else if (/group|algebraic|monoid|semigroup|ring|field/i.test(top) || /group theory|abelian group|cyclic group|monoid|subgroup|isomorphism/i.test(txt)) {

      chapter = 'Group Theory & Algebraic Structures';

    } else if (/combinatorics|counting|pigeonhole|recurrence|permutation/i.test(top) || /combinatorics|pigeonhole principle|permutation|combination|recurrence relation|generating function/i.test(txt)) {

      chapter = 'Combinatorics & Recurrence Relations';

    } else {

      chapter = 'Discrete Structures & Core Concepts';

    }

  } else if (sub === 'Engineering Mathematics') {

    if (/linear algebra|matrix|matrices|determinant|rank|system of linear|eigen/i.test(top) || /eigenvalue|eigenvector|rank of matrix|determinant|system of linear equations|cayley-hamilton/i.test(txt)) {

      chapter = 'Linear Algebra, Matrices & Eigenvalues';

    } else if (/probability|bayes|distribution|random variable|poisson|normal|exponential/i.test(top) || /probability|conditional probability|bayes theorem|poisson distribution|variance|expectation/i.test(txt)) {

      chapter = 'Probability Distributions & Statistics';

    } else if (/calculus|limit|continuity|derivative|integral|maxima|minima/i.test(top) || /calculus|limit|continuous|derivative|integral|maxima and minima|mean value theorem/i.test(txt)) {

      chapter = 'Calculus: Limits, Integrals & Optimization';

    } else if (/numerical method|newton-raphson|simpson|trapezoidal/i.test(top) || /numerical methods|newton-raphson|simpson|trapezoidal|bisection/i.test(txt)) {

      chapter = 'Numerical Methods & Approximations';

    } else {

      chapter = 'Engineering Mathematics Foundations';

    }

  } else if (sub === 'C Programming') {

    if (/pointer|pointer arithmetic|array of pointer/i.test(top) || /pointer|dereference|\*p|pointer arithmetic|malloc|calloc/i.test(txt)) {

      chapter = 'Pointers, Memory Allocation & Arrays';

    } else if (/recursion|recursive/i.test(top) || /recursion|recursive function|base condition/i.test(txt)) {

      chapter = 'Recursion & Function Call Stacks';

    } else if (/output|predict output|printf/i.test(top) || /printf|output of the following program|what does the following program print/i.test(txt)) {

      chapter = 'Output Prediction & Code Analysis';

    } else if (/operator|precedence|bitwise|expression/i.test(top) || /operator precedence|bitwise operator|associativity/i.test(txt)) {

      chapter = 'Operators, Precedence & Bitwise Manipulation';

    } else if (/structure|union|enum|typedef/i.test(top) || /struct |union |typedef/i.test(txt)) {

      chapter = 'Structures, Unions & User-Defined Types';

    } else {

      chapter = 'C Language Fundamentals & Control Flow';

    }

  } else if (sub === 'Aptitude') {

    if (/verbal|grammar|english|sentence|comprehension|vocabulary/i.test(top) || /antonym|synonym|grammatically correct|comprehension|blank|sentence/i.test(txt)) {

      chapter = 'Verbal Ability & English Comprehension';

    } else if (/data interpretation|chart|graph|table/i.test(top) || /bar chart|pie chart|table shows|data interpretation/i.test(txt)) {

      chapter = 'Data Interpretation & Graphs';

    } else if (/spatial|folding|paper|cube|rotation/i.test(top) || /paper folding|mirror image|rotation|cube/i.test(txt)) {

      chapter = 'Spatial Aptitude & Visual Reasoning';

    } else {

      chapter = 'Quantitative Aptitude & Logical Reasoning';

    }

  } else {

    chapter = top || 'General Core CSE';

  }

  

  q._topicChapter = chapter;

  return chapter;

}



const TOPIC_SUBJECT_META = {

  'Operating Systems':       { icon: '⚙️', color: '#3b82f6' },

  'Algorithms':              { icon: '🧮', color: '#a855f7' },

  'DBMS':                    { icon: '🗄️', color: '#22c55e' },

  'Computer Networks':       { icon: '🌐', color: '#06b6d4' },

  'Computer Organization':   { icon: '💻', color: '#f97316' },

  'Theory of Computation':   { icon: '🔣', color: '#ec4899' },

  'Data Structures':         { icon: '🌲', color: '#10b981' },

  'Digital Logic':           { icon: '🔌', color: '#f59e0b' },

  'Discrete Mathematics':    { icon: '🧩', color: '#6366f1' },

  'Engineering Mathematics': { icon: '📐', color: '#14b8a6' },

  'Compiler Design':         { icon: '🛠️', color: '#ef4444' },

  'C Programming':           { icon: '💻', color: '#2563eb' },

  'Aptitude':                { icon: '🎯', color: '#f43f5e' },

};



function getTopicSubjectMeta(sub) {

  return TOPIC_SUBJECT_META[sub] || { icon: '📖', color: 'var(--accent)' };

}



// ─── TOPIC-WISE PYQs MAIN RENDERER ───────────────────────────────────────────

function renderPYQs(c) {

  if (!c) c = document.getElementById('page-content');

  if (!c) return;

  

  const seenCids = new Set();
  const pyqs = state.questions.filter(q => {
    if (q.category !== 'pyq') return false;
    const cid = q.canonicalId || q.id;
    if (seenCids.has(cid)) return false;
    seenCids.add(cid);
    return true;
  });

  const activeTab = state.topicPyqTab || 'chapters'; // 'chapters' or 'list'

  

  // Tab 1: Topic-Wise Chapters View

  if (activeTab === 'chapters') {

    c.innerHTML = buildTopicWiseChaptersHTML(pyqs);

  } else if (activeTab === 'heatmap') {

    // Tab 2: High-Yield Weightage Heatmap & Topic Trend Engine

    c.innerHTML = buildGateWeightageHeatmapHTML(pyqs);

  } else {

    // Tab 3: Classic Flat List View

    c.innerHTML = buildClassicPyqListHTML(pyqs);

  }

  

  renderMath(c);

}



function buildTopicWiseChaptersHTML(pyqs) {

  const selectedSub = state.selectedTopicPyqSubject || 'all';

  const searchTerm = (state.topicPyqSearch || '').trim().toLowerCase();

  const diffFilter = state.topicPyqDifficulty || 'all';

  const typeFilter = state.topicPyqType || 'all';



  // 1. Compute Subject Totals

  const subjectCounts = {};

  const allSubjects = [

    'Operating Systems', 'Algorithms', 'DBMS', 'Computer Networks',

    'Computer Organization', 'Theory of Computation', 'Data Structures',

    'Digital Logic', 'Discrete Mathematics', 'Engineering Mathematics',

    'Compiler Design', 'C Programming', 'Aptitude'

  ];

  allSubjects.forEach(s => { subjectCounts[s] = 0; });

  

  pyqs.forEach(q => {

    const s = q.subject || 'General';

    subjectCounts[s] = (subjectCounts[s] || 0) + 1;

  });



  // 2. Group Questions by (Subject, Chapter)

  const chapterMap = new Map();

  pyqs.forEach(q => {

    const sub = q.subject || 'General';

    const chap = getTopicPYQChapter(q);

    const key = `${sub}:::${chap}`;

    

    if (!chapterMap.has(key)) {

      chapterMap.set(key, {

        subject: sub,

        chapter: chap,

        key,

        questions: [],

        minYear: q.year || 2025,

        maxYear: q.year || 2000,

        marks1: 0,

        marks2: 0,

        mcqCount: 0,

        msqCount: 0,

        natCount: 0,

      });

    }

    

    const entry = chapterMap.get(key);

    entry.questions.push(q);

    const yr = parseInt(q.year, 10);

    if (!isNaN(yr)) {

      if (yr < entry.minYear) entry.minYear = yr;

      if (yr > entry.maxYear) entry.maxYear = yr;

    }

    if ((q.marks || 1) === 2) entry.marks2++; else entry.marks1++;

    if (q.type === 'nat') entry.natCount++;

    else if (q.type === 'msq') entry.msqCount++;

    else entry.mcqCount++;

  });



  // 3. User Attempt Stats

  const attemptedQIds = new Set(state.attempts.map(a => a.questionId));

  const correctQIds = new Set(state.attempts.filter(a => a.correct).map(a => a.questionId));

  

  let totalAttemptedInPyqs = 0;

  let totalCorrectInPyqs = 0;

  pyqs.forEach(q => {

    if (attemptedQIds.has(q.id)) {

      totalAttemptedInPyqs++;

      if (correctQIds.has(q.id)) totalCorrectInPyqs++;

    }

  });

  const overallAcc = totalAttemptedInPyqs > 0 ? Math.round((totalCorrectInPyqs / totalAttemptedInPyqs) * 100) : 0;



  // 4. Filter Chapters by Selected Subject & Search & Filters

  let chaptersList = Array.from(chapterMap.values());

  if (selectedSub !== 'all') {

    chaptersList = chaptersList.filter(ch => ch.subject === selectedSub);

  }

  if (searchTerm) {

    chaptersList = chaptersList.filter(ch => 

      ch.chapter.toLowerCase().includes(searchTerm) ||

      ch.subject.toLowerCase().includes(searchTerm) ||

      ch.questions.some(q => (q.question && q.question.toLowerCase().includes(searchTerm)))

    );

  }

  if (diffFilter !== 'all') {

    chaptersList = chaptersList.filter(ch => ch.questions.some(q => q.difficulty === diffFilter));

  }

  if (typeFilter !== 'all') {

    chaptersList = chaptersList.filter(ch => ch.questions.some(q => q.type === typeFilter));

  }



  // Sort chapters by total questions descending

  chaptersList.sort((a, b) => b.questions.length - a.questions.length);



  return `

    <!-- Hero / Header -->

    <div class="topic-pyq-hero">

      <div class="topic-pyq-header-row">

        <div class="topic-pyq-title-wrap">

          <h2><span>📑</span> GATE CSE Topic-Wise PYQs</h2>

          <div class="topic-pyq-subtitle">

            Practice previous year questions organized strictly chapter-by-chapter across the entire GATE CSE syllabus. Drill authentic 1990–2025 questions with worked KaTeX solutions, instant feedback, and automatic Mistake Vault sync.

          </div>

        </div>

        <div class="topic-pyq-view-toggle">

          <button class="topic-pyq-tab-btn active" onclick="setTopicPyqTab('chapters')" type="button">

            <span>📑</span> Topic-Wise

          </button>

          <button class="topic-pyq-tab-btn" onclick="setTopicPyqTab('heatmap')" type="button">

            <span>🔥</span> Weightage Heatmap

          </button>

          <button class="topic-pyq-tab-btn" onclick="setTopicPyqTab('list')" type="button">
            <span>📋</span> All PYQs List
          </button>
          <button class="topic-pyq-tab-btn" onclick="navigate('patterns')" type="button">
            <span>🔁</span> 338 Repeating Patterns
          </button>
          <button class="topic-pyq-tab-btn" onclick="navigate('patterns',{tab:'archival'})" type="button">
            <span>📜</span> 44-Yr Archival Bank
          </button>
        </div>
      </div>

      <!-- 1983-2026 Archival & Patterns Callout -->
      <div style="background:linear-gradient(135deg,rgba(245,158,11,0.12),rgba(108,99,255,0.08));border:1px solid rgba(245,158,11,0.25);border-radius:var(--radius);padding:14px 18px;margin-bottom:16px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px">
        <div style="display:flex;align-items:center;gap:12px">
          <span style="font-size:26px">🔁</span>
          <div>
            <div style="font-weight:700;font-size:14px;color:var(--text-primary);display:flex;align-items:center;gap:6px">
              <span>GATE CSE Same-Pattern Detector (1983–2026)</span>
              <span class="q-badge" style="background:rgba(245,158,11,0.2);color:#f59e0b;font-weight:700">338 Patterns • 4,910 PYQs</span>
            </div>
            <div style="font-size:12px;color:var(--text-secondary);margin-top:2px">
              Discover which exact concepts repeat across ≥ 4 distinct GATE years. Download the 466-page Solved Pattern Book and 562-page Archival Question Bank PDF.
            </div>
          </div>
        </div>
        <div style="display:flex;gap:8px">
          <button class="btn btn-primary btn-sm" onclick="navigate('patterns')">Explore Patterns Hub →</button>
          <a href="assets/resources/GATE_CSE_Question_Bank_1983_2026_Consolidated.pdf" download class="btn btn-secondary btn-sm" title="Download Consolidated 1983-2026 PDF">📥 44-Yr PDF</a>
        </div>
      </div>



      <!-- Quick Metrics Bar -->

      <div class="topic-pyq-stats-grid">

        <div class="topic-pyq-stat-card">

          <div class="topic-stat-icon">📚</div>

          <div class="topic-stat-info">

            <div class="stat-num">13</div>

            <div class="stat-label">Core Subjects</div>

          </div>

        </div>

        <div class="topic-pyq-stat-card">

          <div class="topic-stat-icon">📑</div>

          <div class="topic-stat-info">

            <div class="stat-num">${chapterMap.size}</div>

            <div class="stat-label">Syllabus Chapters</div>

          </div>

        </div>

        <div class="topic-pyq-stat-card">

          <div class="topic-stat-icon">🎯</div>

          <div class="topic-stat-info">

            <div class="stat-num">${pyqs.length}</div>

            <div class="stat-label">Authentic PYQs</div>

          </div>

        </div>

        <div class="topic-pyq-stat-card">

          <div class="topic-stat-icon">📈</div>

          <div class="topic-stat-info">

            <div class="stat-num">${totalAttemptedInPyqs} / ${pyqs.length}</div>

            <div class="stat-label">Solved (${overallAcc}% Acc)</div>

          </div>

        </div>

      </div>

    </div>



    <!-- Subject Selector Pills -->

    <div class="topic-subject-pills-bar">

      <button class="topic-subject-pill ${selectedSub === 'all' ? 'active' : ''}" onclick="setTopicPyqSubject('all')" type="button">

        ⚡ All Subjects <span class="topic-pill-count">${pyqs.length}</span>

      </button>

      ${allSubjects.map(sub => {

        const meta = getTopicSubjectMeta(sub);

        const cnt = subjectCounts[sub] || 0;

        return `

          <button class="topic-subject-pill ${selectedSub === sub ? 'active' : ''}" onclick="setTopicPyqSubject('${escapeHtml(sub)}')" type="button">

            <span>${meta.icon}</span> ${sub} <span class="topic-pill-count">${cnt}</span>

          </button>

        `;

      }).join('')}

    </div>



    <!-- Toolbar: Search, Filters & Random Drill -->

    <div class="topic-pyq-toolbar">

      <div class="topic-search-wrap">

        <span class="topic-search-icon">🔍</span>

        <input type="text" placeholder="Search chapters (e.g. CPU Scheduling, Paging, B+ Trees, Master Theorem...)"

          value="${escapeHtml(state.topicPyqSearch || '')}"

          oninput="updateTopicPyqSearch(this.value)" />

      </div>



      <select class="filter-select" onchange="setTopicPyqDifficulty(this.value)" style="min-width:140px">

        <option value="all" ${diffFilter === 'all' ? 'selected' : ''}>All Difficulties</option>

        <option value="easy" ${diffFilter === 'easy' ? 'selected' : ''}>🟢 Easy</option>

        <option value="medium" ${diffFilter === 'medium' ? 'selected' : ''}>🟡 Medium</option>

        <option value="hard" ${diffFilter === 'hard' ? 'selected' : ''}>🔴 Hard</option>

      </select>



      <select class="filter-select" onchange="setTopicPyqType(this.value)" style="min-width:130px">

        <option value="all" ${typeFilter === 'all' ? 'selected' : ''}>All Formats</option>

        <option value="mcq" ${typeFilter === 'mcq' ? 'selected' : ''}>MCQ (Single)</option>

        <option value="msq" ${typeFilter === 'msq' ? 'selected' : ''}>MSQ (Multi)</option>

        <option value="nat" ${typeFilter === 'nat' ? 'selected' : ''}>NAT (Numeric)</option>

      </select>



      <button class="btn btn-secondary btn-sm" onclick="launchRandomTopicDrill()" type="button" title="Pick a random topic and drill immediately">

        🎲 Random Chapter Drill

      </button>

      <button class="btn btn-secondary btn-sm" onclick="printSyllabusWallSheet()" type="button" title="Print 1-Page Physical Wall Cheat Sheet">

        🖨️ 87-Chapter Wall Sheet

      </button>

    </div>



    <!-- Topic Cards Grid -->

    ${!chaptersList.length ? `

      <div class="empty-state">

        <div class="empty-state-icon">🔍</div>

        <div class="empty-state-title">No chapters found</div>

        <div class="empty-state-sub">Try adjusting your search query or subject filters above.</div>

      </div>

    ` : `

      <div class="topic-cards-grid">

        ${chaptersList.map(ch => {

          const subMeta = getTopicSubjectMeta(ch.subject);

          const isExpanded = state.topicPyqExpandedTopic === ch.key;

          const totalQ = ch.questions.length;

          

          let attemptedInTopic = 0;

          let correctInTopic = 0;

          ch.questions.forEach(q => {

            if (attemptedQIds.has(q.id)) {

              attemptedInTopic++;

              if (correctQIds.has(q.id)) correctInTopic++;

            }

          });

          const pct = Math.round((attemptedInTopic / totalQ) * 100);

          const acc = attemptedInTopic > 0 ? Math.round((correctInTopic / attemptedInTopic) * 100) : 0;

          const yearSpan = ch.minYear === ch.maxYear ? `${ch.minYear}` : `${ch.minYear} – ${ch.maxYear}`;



          return `

            <div class="topic-card" id="tc-${encodeURIComponent(ch.key)}">

              <div>

                <div class="topic-card-top">

                  <span class="topic-card-subject-chip" style="background:${subMeta.color}22; color:${subMeta.color}">

                    ${subMeta.icon} ${ch.subject}

                  </span>

                  <span class="topic-card-year-badge">📅 ${yearSpan}</span>

                </div>

                <div class="topic-card-title">${escapeHtml(ch.chapter)}</div>

                

                <div class="topic-card-chips-row">

                  <span class="topic-meta-chip highlight"><strong>${totalQ}</strong> Questions</span>

                  ${ch.marks2 > 0 ? `<span class="topic-meta-chip">${ch.marks2} × 2M</span>` : ''}

                  ${ch.marks1 > 0 ? `<span class="topic-meta-chip">${ch.marks1} × 1M</span>` : ''}

                  ${ch.natCount > 0 ? `<span class="topic-meta-chip">${ch.natCount} NAT</span>` : ''}

                  ${ch.msqCount > 0 ? `<span class="topic-meta-chip">${ch.msqCount} MSQ</span>` : ''}

                </div>



                <div class="topic-progress-wrap">

                  <div class="topic-progress-labels">

                    <span>Mastery Progress</span>

                    <span>${attemptedInTopic} / ${totalQ} Solved (${acc}% Acc)</span>

                  </div>

                  <div class="topic-progress-bar-bg">

                    <div class="topic-progress-bar-fill" style="width: ${pct}%"></div>

                  </div>

                </div>

              </div>



              <div>

                <div class="topic-card-actions">

                  <button class="topic-btn-practice" onclick="startTopicPYQPractice('${escapeHtml(ch.subject)}', '${escapeHtml(ch.chapter)}')" type="button">

                    <span>▶</span> Practice Chapter (${totalQ})

                  </button>

                  <button class="topic-btn-browse" onclick="toggleTopicPYQDrawer('${escapeHtml(ch.key)}')" type="button">

                    <span>${isExpanded ? '▲' : '👁️'}</span> ${isExpanded ? 'Hide' : 'Questions'}

                  </button>

                </div>



                ${isExpanded ? `

                  <div class="topic-questions-drawer">

                    ${ch.questions.map((q, qIdx) => {

                      const isBmk = state.bookmarks?.has(q.id);

                      return `

                        <div class="topic-drawer-item">

                          <div class="topic-drawer-qinfo">

                            <div class="topic-drawer-badges">

                              <span class="chip" style="font-size:10px;padding:1px 5px">Q${qIdx + 1}</span>

                              <span class="chip" style="font-size:10px;padding:1px 5px">${q.year || 'GATE'}</span>

                              <span class="chip" style="font-size:10px;padding:1px 5px">${q.marks || 1}m</span>

                              <span class="q-badge ${q.type}" style="font-size:9px;padding:1px 4px">${q.type?.toUpperCase()}</span>

                              <span class="q-badge ${q.difficulty}" style="font-size:9px;padding:1px 4px">${q.difficulty}</span>

                            </div>

                            <div class="topic-drawer-qtext">${formatQuestionContent(q.question?.slice(0, 110) || '')}...</div>

                          </div>

                          <div style="display:flex;align-items:center;gap:6px;flex-shrink:0">

                            <button class="star-btn ${isBmk ? 'bookmarked' : ''}" onclick="toggleBookmark('${q.id}'); this.innerHTML = state.bookmarks.has('${q.id}') ? '⭐' : '☆';" style="font-size:14px" type="button">

                              ${isBmk ? '⭐' : '☆'}

                            </button>

                            <button class="btn btn-secondary btn-sm" onclick="openPlaylistModal('${q.id}')" style="padding:2px 6px;font-size:11px" title="Add to Smart Playlist" type="button">

                              🗂️

                            </button>

                            <button class="btn btn-secondary btn-sm" onclick="openSingleQuestion('${q.id}')" style="padding:2px 8px;font-size:11px" type="button">

                              Solve →

                            </button>

                          </div>

                        </div>

                      `;

                    }).join('')}

                  </div>

                ` : ''}

              </div>

            </div>

          `;

        }).join('')}

      </div>

    `}

  `;

}



function buildClassicPyqListHTML(pyqs) {

  const f = state.pyqFilters;

  let filtered = [...pyqs];

  if (f.year !== 'all') filtered = filtered.filter(q => q.year == f.year);

  if (f.subject !== 'all') filtered = filtered.filter(q => q.subject === f.subject);

  if (state.pyqSearch && state.pyqSearch.trim()) {

    const term = state.pyqSearch.trim().toLowerCase();

    filtered = filtered.filter(q =>

      (q.question && q.question.toLowerCase().includes(term)) ||

      (q.topic && q.topic.toLowerCase().includes(term)) ||

      (q.subject && q.subject.toLowerCase().includes(term))

    );

  }

  state.practiceQueue = filtered;

  const subs = ['all', ...new Set(pyqs.map(q => q.subject).filter(Boolean))];



  const totalCount = filtered.length;

  const pageSize = state.pyqPageSize === 'all' ? (totalCount || 1) : parseInt(state.pyqPageSize, 10);

  const totalPages = Math.max(1, Math.ceil(totalCount / pageSize));

  if (state.pyqPage > totalPages) state.pyqPage = totalPages;

  if (state.pyqPage < 1) state.pyqPage = 1;



  const startIndex = (state.pyqPage - 1) * pageSize;

  const endIndex = Math.min(startIndex + pageSize, totalCount);

  const pageItems = filtered.slice(startIndex, endIndex);



  const paginationArgs = {

    currentPage: state.pyqPage,

    totalPages,

    totalCount,

    startIndex: totalCount > 0 ? startIndex + 1 : 0,

    endIndex,

    pageSize: state.pyqPageSize,

    onPageChangeFn: 'setPYQPage',

    onPageSizeChangeFn: 'setPYQPageSize'

  };



  return `

    <div class="topic-pyq-hero" style="padding:16px 20px;margin-bottom:18px">

      <div class="topic-pyq-header-row" style="margin-bottom:0">

        <div>

          <h2 style="font-size:20px;margin-bottom:2px"><span>📋</span> All GATE CSE PYQs (Flat Search & Filter)</h2>

          <div class="topic-pyq-subtitle" style="font-size:13px">

            Displaying ${totalCount} questions. Filter by exact exam year, subject, or keywords.

          </div>

        </div>

        <div class="topic-pyq-view-toggle">

          <button class="topic-pyq-tab-btn" onclick="setTopicPyqTab('chapters')" type="button">

            <span>📑</span> Topic-Wise

          </button>

          <button class="topic-pyq-tab-btn" onclick="setTopicPyqTab('heatmap')" type="button">

            <span>🔥</span> Weightage Heatmap

          </button>

          <button class="topic-pyq-tab-btn active" onclick="setTopicPyqTab('list')" type="button">
            <span>📋</span> All PYQs List
          </button>
          <button class="topic-pyq-tab-btn" onclick="navigate('patterns')" type="button">
            <span>🔁</span> 338 Repeating Patterns
          </button>
          <button class="topic-pyq-tab-btn" onclick="navigate('patterns',{tab:'archival'})" type="button">
            <span>📜</span> 44-Yr Archival Bank
          </button>

        </div>

      </div>

    </div>



    <div class="section-header">

      <div class="section-title">Previous Year Questions <span>${totalCount} questions</span></div>

      <button class="btn btn-primary btn-sm" onclick="startPYQPractice()" ${!filtered.length ? 'disabled' : ''}>▶ Practice These</button>

    </div>

    <div class="filter-bar">

      <select class="filter-select" onchange="updatePYQFilter('year',this.value)">

        <option value="all">All Years</option>

        ${PYQ_YEARS.map(y => `<option value="${y}" ${f.year == y ? 'selected' : ''}>${y}</option>`).join('')}

      </select>

      <select class="filter-select" onchange="updatePYQFilter('subject',this.value)">

        ${subs.map(s => `<option value="${s}" ${f.subject === s ? 'selected' : ''}>${s === 'all' ? 'All Subjects' : s}</option>`).join('')}

      </select>

      <input type="text" class="search-input" placeholder="🔍 Search PYQs..."

        value="${escapeHtml(state.pyqSearch || '')}"

        oninput="updatePYQSearch(this.value)" />

    </div>

    ${!totalCount

      ? `<div class="empty-state"><div class="empty-state-icon">📅</div><div class="empty-state-title">No PYQs found</div><div class="empty-state-sub">Upload questions with category="pyq" and a year field.</div></div>`

      : `${buildPaginationHTML({ ...paginationArgs, isTop: true })}

         <div class="pyq-grid" id="pyq-questions-grid">${pageItems.map((q, idx) => {

           const isBookmarked = state.bookmarks?.has(q.id);

           return `

          <div class="pyq-item" onclick="openSingleQuestion('${q.id}')">

            <div class="pyq-item-year">${q.year || 'PYQ'}</div>

            <div class="pyq-item-content">

              <div class="pyq-item-question">

                <strong style="color:var(--accent);margin-right:6px">Q${startIndex + idx + 1}.</strong>${formatQuestionContent(q.question)}

              </div>

              <div class="pyq-item-meta">

                <span class="chip">${q.subject}</span>

                ${q.topic ? `<span class="chip">${q.topic}</span>` : ''}

                <span class="q-badge ${q.type}">${q.type?.toUpperCase()}</span>

                <span class="chip">${q.marks || 1}m</span>

                <button class="star-btn ${isBookmarked ? 'bookmarked' : ''}" style="margin-left:auto" data-qid="${q.id}" onclick="event.stopPropagation(); toggleBookmark('${q.id}')" title="${isBookmarked ? 'Remove Bookmark' : 'Add Bookmark'}" type="button">

                  ${isBookmarked ? '⭐' : '☆'}

                </button>

                <button class="btn btn-secondary btn-sm" style="padding:2px 8px;font-size:11px" onclick="event.stopPropagation();openSingleQuestion('${q.id}')">Solve →</button>

              </div>

            </div>

          </div>`;

         }).join('')}</div>

         ${buildPaginationHTML({ ...paginationArgs, isTop: false })}`

    }

  `;

}



function setTopicPyqTab(tab) {

  state.topicPyqTab = tab;

  renderPYQs(document.getElementById('page-content'));

}



function setTopicPyqSubject(sub) {

  state.selectedTopicPyqSubject = sub;

  state.topicPyqExpandedTopic = null;

  renderPYQs(document.getElementById('page-content'));

}



let topicSearchTimer = null;

function updateTopicPyqSearch(val) {

  state.topicPyqSearch = val;

  clearTimeout(topicSearchTimer);

  topicSearchTimer = setTimeout(() => {

    renderPYQs(document.getElementById('page-content'));

  }, 180);

}



function setTopicPyqDifficulty(diff) {

  state.topicPyqDifficulty = diff;

  renderPYQs(document.getElementById('page-content'));

}



function setTopicPyqType(type) {

  state.topicPyqType = type;

  renderPYQs(document.getElementById('page-content'));

}



function toggleTopicPYQDrawer(chapterKey) {

  state.topicPyqExpandedTopic = state.topicPyqExpandedTopic === chapterKey ? null : chapterKey;

  renderPYQs(document.getElementById('page-content'));

}



function startTopicPYQPractice(subject, chapter) {

  const seenCids = new Set();
  const pyqs = state.questions.filter(q => {
    if (q.category !== 'pyq') return false;
    const cid = q.canonicalId || q.id;
    if (seenCids.has(cid)) return false;
    seenCids.add(cid);
    return true;
  });

  const matching = pyqs.filter(q => {

    if (subject && q.subject !== subject) return false;

    return getTopicPYQChapter(q) === chapter;

  });



  if (!matching.length) {

    showToast(`No questions found for ${chapter}`, 'error');

    return;

  }



  state.practiceQueue = [...matching];

  state.currentQuestion = 0;

  practiceSelectedOpts = new Set();

  showToast(`Starting practice: ${chapter} (${matching.length} Questions)`, 'info', 2000);

  startPracticeMode();

}



function launchRandomTopicDrill() {

  const seenCids = new Set();
  const pyqs = state.questions.filter(q => {
    if (q.category !== 'pyq') return false;
    const cid = q.canonicalId || q.id;
    if (seenCids.has(cid)) return false;
    seenCids.add(cid);
    return true;
  });

  const selectedSub = state.selectedTopicPyqSubject || 'all';

  let eligible = pyqs;

  if (selectedSub !== 'all') {

    eligible = eligible.filter(q => q.subject === selectedSub);

  }



  const chaptersMap = new Map();

  eligible.forEach(q => {

    const ch = getTopicPYQChapter(q);

    const key = `${q.subject || 'General'}:::${ch}`;

    if (!chaptersMap.has(key)) chaptersMap.set(key, { subject: q.subject, chapter: ch, questions: [] });

    chaptersMap.get(key).questions.push(q);

  });



  const allKeys = Array.from(chaptersMap.keys());

  if (!allKeys.length) {

    showToast('No topics available for drill', 'error');

    return;

  }



  const randKey = allKeys[Math.floor(Math.random() * allKeys.length)];

  const pick = chaptersMap.get(randKey);

  startTopicPYQPractice(pick.subject, pick.chapter);

}



function updatePYQFilter(k,v){

  state.pyqFilters[k]=v;

  state.pyqPage=1;

  renderPYQs(document.getElementById('page-content'));

}



function setPYQPage(p){

  state.pyqPage = p;

  renderPYQs(document.getElementById('page-content'));

  const el = document.getElementById('pyq-questions-grid');

  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });

}



function setPYQPageSize(sz){

  state.pyqPageSize = sz === 'all' ? 'all' : parseInt(sz, 10);

  state.pyqPage = 1;

  renderPYQs(document.getElementById('page-content'));

}



let pyqSearchTimer = null;

function updatePYQSearch(val){

  state.pyqSearch = val;

  state.pyqPage = 1;

  clearTimeout(pyqSearchTimer);

  pyqSearchTimer = setTimeout(() => {

    renderPYQs(document.getElementById('page-content'));

  }, 200);

}



function startPYQPractice(){

  let qs=state.questions.filter(q=>q.category==='pyq');

  if(state.pyqFilters.year!=='all') qs=qs.filter(q=>q.year==state.pyqFilters.year);

  if(state.pyqFilters.subject!=='all') qs=qs.filter(q=>q.subject===state.pyqFilters.subject);

  if(state.pyqSearch && state.pyqSearch.trim()){

    const term=state.pyqSearch.trim().toLowerCase();

    qs=qs.filter(q=>

      (q.question && q.question.toLowerCase().includes(term)) ||

      (q.topic && q.topic.toLowerCase().includes(term)) ||

      (q.subject && q.subject.toLowerCase().includes(term))

    );

  }

  state.practiceQueue=[...qs]; state.currentQuestion=0; renderPracticeQuestion();

}



// ─── PERFORMANCE ─────────────────────────────────────────────────────────────

function buildSamePatternRecurrencePerformanceHTML() {
  const patternsCount = (window.GATE_PATTERN_INDEX && window.GATE_PATTERN_INDEX.length) || 338;
  return `
    <div class="card mb-6" style="background:linear-gradient(135deg, rgba(245, 158, 11, 0.08) 0%, rgba(239, 68, 68, 0.04) 100%);border:1px solid rgba(245, 158, 11, 0.35);border-radius:14px;padding:22px 24px;box-shadow:0 4px 20px rgba(0,0,0,0.06);position:relative;overflow:hidden">
      <div style="position:absolute;top:-18px;right:-18px;width:120px;height:120px;background:radial-gradient(circle, rgba(245, 158, 11, 0.2) 0%, transparent 70%);border-radius:50%;pointer-events:none"></div>
      
      <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:14px;margin-bottom:16px">
        <div>
          <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">
            <span style="font-size:24px;line-height:1">🔁</span>
            <h2 style="font-size:1.25rem;font-weight:700;margin:0;color:var(--text-primary);letter-spacing:-0.01em">
              1983–2026 Same Pattern Recurrence Intelligence
            </h2>
            <span style="font-size:11px;padding:3px 8px;border-radius:20px;background:#f59e0b;color:#fff;font-weight:700;text-transform:uppercase;letter-spacing:0.04em">
              High-Yield 338 Patterns
            </span>
          </div>
          <p style="margin:0;font-size:13.5px;color:var(--text-secondary);max-width:760px;line-height:1.5">
            Empirical historical pattern analysis across <strong>43 years</strong> of GATE CSE papers. Over 80% of scoring opportunities in GATE repeat foundational analytical problem structures.
          </p>
        </div>

        <div style="display:flex;align-items:center;gap:10px">
          <button class="btn btn-primary" onclick="navigate('patterns')" style="background:#f59e0b;border-color:#d97706;color:#fff;font-weight:600;display:inline-flex;align-items:center;gap:8px;padding:9px 18px;border-radius:8px;box-shadow:0 2px 8px rgba(245,158,11,0.35);cursor:pointer">
            <span>Explore 338 Repeating Patterns</span>
            <span>➔</span>
          </button>
        </div>
      </div>

      <!-- Quick Pattern Metric Highlights -->
      <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(180px, 1fr));gap:14px;margin-bottom:18px">
        <div style="background:var(--bg-surface, #fff);border:1px solid var(--border-color, #e2e8f0);border-radius:10px;padding:12px 14px">
          <div style="font-size:11.5px;color:var(--text-muted);font-weight:600;text-transform:uppercase;margin-bottom:4px">Verified Patterns</div>
          <div style="font-size:22px;font-weight:800;color:#f59e0b">${patternsCount} Identified</div>
          <div style="font-size:11px;color:var(--text-secondary);margin-top:2px">Catalogued 1983–2026</div>
        </div>
        <div style="background:var(--bg-surface, #fff);border:1px solid var(--border-color, #e2e8f0);border-radius:10px;padding:12px 14px">
          <div style="font-size:11.5px;color:var(--text-muted);font-weight:600;text-transform:uppercase;margin-bottom:4px">Analyzed Questions</div>
          <div style="font-size:22px;font-weight:800;color:var(--accent, #3b82f6)">1,280+ Problems</div>
          <div style="font-size:11px;color:var(--text-secondary);margin-top:2px">Cross-referenced across years</div>
        </div>
        <div style="background:var(--bg-surface, #fff);border:1px solid var(--border-color, #e2e8f0);border-radius:10px;padding:12px 14px">
          <div style="font-size:11.5px;color:var(--text-muted);font-weight:600;text-transform:uppercase;margin-bottom:4px">Historical Scope</div>
          <div style="font-size:22px;font-weight:800;color:#10b981">43 Years</div>
          <div style="font-size:11px;color:var(--text-secondary);margin-top:2px">1983 through 2026</div>
        </div>
        <div style="background:var(--bg-surface, #fff);border:1px solid var(--border-color, #e2e8f0);border-radius:10px;padding:12px 14px">
          <div style="font-size:11.5px;color:var(--text-muted);font-weight:600;text-transform:uppercase;margin-bottom:4px">Repeat Confidence</div>
          <div style="font-size:22px;font-weight:800;color:#8b5cf6">~78% Recurring</div>
          <div style="font-size:11px;color:var(--text-secondary);margin-top:2px">Guaranteed concept coverage</div>
        </div>
      </div>

      <!-- High-Frequency Recurrence Radar Highlights -->
      <div style="background:var(--bg-surface, #fff);border:1px solid var(--border-color, #e2e8f0);border-radius:10px;padding:14px 16px">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;flex-wrap:wrap;gap:8px">
          <span style="font-size:13px;font-weight:700;color:var(--text-primary);display:inline-flex;align-items:center;gap:6px">
            <span>🔥</span> Top Repeating Themes in GATE CSE History
          </span>
          <span style="font-size:11.5px;color:var(--text-muted)">Mastery of these focus areas guarantees 35+ marks</span>
        </div>
        <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(220px, 1fr));gap:10px">
          <div style="font-size:12px;padding:8px 12px;border-radius:8px;background:rgba(245,158,11,0.08);border-left:3px solid #f59e0b">
            <strong>Divide-and-Conquer & Recurrences</strong>
            <div style="color:var(--text-muted);font-size:11px;margin-top:2px">Algorithms • 38 recorded repeats</div>
          </div>
          <div style="font-size:12px;padding:8px 12px;border-radius:8px;background:rgba(59,130,246,0.08);border-left:3px solid #3b82f6">
            <strong>Regular Languages & Closure Properties</strong>
            <div style="color:var(--text-muted);font-size:11px;margin-top:2px">Theory of Computation • 34 recorded repeats</div>
          </div>
          <div style="font-size:12px;padding:8px 12px;border-radius:8px;background:rgba(16,185,129,0.08);border-left:3px solid #10b981">
            <strong>Cache Mapping & Address Bits Tagging</strong>
            <div style="color:var(--text-muted);font-size:11px;margin-top:2px">Computer Organization • 31 recorded repeats</div>
          </div>
          <div style="font-size:12px;padding:8px 12px;border-radius:8px;background:rgba(139,92,246,0.08);border-left:3px solid #8b5cf6">
            <strong>Conflict Serializability & 2PL Schedules</strong>
            <div style="color:var(--text-muted);font-size:11px;margin-top:2px">DBMS • 28 recorded repeats</div>
          </div>
        </div>
      </div>

      <!-- Quick Download Links -->
      <div style="display:flex;justify-content:flex-end;align-items:center;gap:16px;margin-top:12px;font-size:12px;flex-wrap:wrap">
        <a href="assets/resources/GATE_CSE_Same_Pattern_Questions_1983_2026.pdf" target="_blank" download style="color:var(--accent);text-decoration:none;display:inline-flex;align-items:center;gap:5px;font-weight:600">
          <span>📄</span> Download Same Pattern PDF (466 Pages)
        </a>
        <span style="color:var(--text-muted)">•</span>
        <a href="assets/resources/GATE_CSE_Pattern_Master_Index_1983_2026.csv" download style="color:var(--accent);text-decoration:none;display:inline-flex;align-items:center;gap:5px;font-weight:600">
          <span>📊</span> Download Pattern Master Index CSV
        </a>
      </div>
    </div>
  `;
}

function renderPerformance(c){

  const {attempted,correct,accuracy}=getStats();

  const subData=SUBJECTS.map(s=>({name:s.name,color:s.color,...getSubjectStats(s.name)})).filter(s=>s.total>0);

  c.innerHTML=`

    ${buildSamePatternRecurrencePerformanceHTML()}

    ${buildPredictorCardHTML(null, state.predictedCategory)}

    ${buildSyllabusCoverageAuditHTML()}

    ${buildMasteryRadarChartSVG()}

    ${buildSpeedAccuracyScatterSVG()}

    ${buildMasteryMatrixHTML()}

    ${buildQuadrantAnalysisHTML()}

    ${buildDataPortabilityCardHTML()}

    <div class="stats-grid" style="margin-bottom:28px">

      <div class="stat-card"><div class="stat-icon">📝</div><div class="stat-label">Total Attempted</div><div class="stat-value">${attempted}</div></div>

      <div class="stat-card"><div class="stat-icon">✅</div><div class="stat-label">Total Correct</div><div class="stat-value" style="color:var(--green)">${correct}</div></div>

      <div class="stat-card"><div class="stat-icon">🎯</div><div class="stat-label">Overall Accuracy</div><div class="stat-value" style="color:var(--accent)">${accuracy}%</div></div>

      <div class="stat-card"><div class="stat-icon">🏆</div><div class="stat-label">Tests Taken</div><div class="stat-value">${state.testSessions.length}</div></div>

    </div>

    ${!subData.length

      ? `<div class="empty-state"><div class="empty-state-icon">📊</div><div class="empty-state-title">No data yet</div><div class="empty-state-sub">Start practicing to see your analytics here.</div></div>`

      : `<div class="perf-grid">

           <div class="card">

             <div class="card-header"><div class="card-title">📊 Accuracy by Subject</div></div>

             <div class="chart-wrapper"><canvas id="subjectChart"></canvas></div>

           </div>

           <div class="card">

             <div class="card-header"><div class="card-title">📈 Subject-wise Progress</div></div>

             <div class="subject-perf-list" style="max-height:260px;overflow-y:auto">

               ${subData.map(s=>`<div class="subject-perf-item">

                 <div class="subject-perf-header"><span style="font-weight:600">${s.name}</span><span class="text-sm text-muted">${s.doneCount}/${s.total} • ${s.accuracy}%</span></div>

                 <div class="subject-perf-bar"><div class="subject-perf-fill" style="width:${s.accuracy}%;background:${s.color}"></div></div>

               </div>`).join('')}

             </div>

           </div>

         </div>

         <div class="card mt-6">

           <div class="card-header"><div class="card-title">📅 Recent Activity</div></div>

           ${!state.attempts.length

             ? `<div class="empty-state" style="padding:20px"><div class="empty-state-sub">No activity yet</div></div>`

             : `<div style="display:flex;flex-direction:column;gap:8px">

                 ${[...state.attempts].reverse().slice(0,10).map(att=>{

                   const q=state.questions.find(x=>x.id===att.questionId);

                   if(!q) return '';

                   return `<div style="display:flex;align-items:center;justify-content:space-between;padding:10px;background:var(--bg-input);border-radius:var(--radius-sm)">

                     <div><div class="text-sm fw-700">${q.subject} — ${q.topic||'General'}</div>

                     <div class="text-sm text-muted" style="margin-top:2px">${q.question.substring(0,60)}…</div></div>

                     <div style="display:flex;align-items:center;gap:10px">

                       <span class="text-sm text-muted">⏱ ${fmt(Math.round(att.timeMs/1000))}</span>

                       <span style="font-size:18px">${att.correct?'✅':'❌'}</span>

                     </div>

                   </div>`;

                 }).filter(Boolean).join('')}

               </div>`}

         </div>`}`;



  if (subData.length && window.Chart) {

    setTimeout(()=>{

      const ctx=document.getElementById('subjectChart');

      if (!ctx) return;

      // Destroy any existing chart instance to prevent double-render

      const existing=Chart.getChart(ctx);

      if (existing) existing.destroy();

      new Chart(ctx,{

        type:'bar',

        data:{

          labels:subData.map(s=>s.name.split(' ').slice(0,2).join(' ')),

          datasets:[{

            label:'Accuracy (%)',

            data:subData.map(s=>s.accuracy),

            backgroundColor:subData.map(s=>s.color+'aa'),

            borderColor:subData.map(s=>s.color),

            borderWidth:2,

            borderRadius:6,

          }]

        },

        options:{

          responsive:true,

          maintainAspectRatio:false,

          plugins:{legend:{display:false}},

          scales:{

            y:{max:100,grid:{color:'rgba(255,255,255,0.05)'},ticks:{color:'#9090b0'}},

            x:{grid:{display:false},ticks:{color:'#9090b0',font:{size:10}}}

          }

        }

      });

    },100);

  }

}



// ─── UPLOAD ──────────────────────────────────────────────────────────────────

function renderUpload(c){

  const currentUid = uid();

  const myQuestions = currentUid ? state.questions.filter(q => q.uploadedBy === currentUid) : [];

  c.innerHTML=`

    <div class="tabs" id="upload-tabs">

      <button class="tab-btn active" onclick="switchUploadTab('json',this)">📁 Upload JSON</button>

      <button class="tab-btn" onclick="switchUploadTab('manual',this)">✏️ Add Manually</button>

      ${state.isAdmin

        ? `<button class="tab-btn" onclick="switchUploadTab('manage',this)">🗂️ Manage All (${state.questions.length})</button>`

        : `<button class="tab-btn" onclick="switchUploadTab('my-uploads',this)">📝 My Contributions (${myQuestions.length})</button>`}

    </div>

    <div id="upload-content">${buildJSONUploadUI()}</div>`;

}



function switchUploadTab(tab,btn){

  if (tab === 'manage' && !state.isAdmin) {

    showToast('⚠️ Admin privileges required to manage questions', 'error');

    return;

  }

  document.querySelectorAll('#upload-tabs .tab-btn').forEach(b=>b.classList.remove('active'));

  btn.classList.add('active');

  const c=document.getElementById('upload-content');

  if(tab==='json')       c.innerHTML=buildJSONUploadUI();

  if(tab==='manual')     c.innerHTML=buildManualForm();

  if(tab==='manage')     c.innerHTML=buildManageUI();

  if(tab==='my-uploads') c.innerHTML=buildMyContributionsUI();

}

function buildMyContributionsUI(){

  const currentUid = uid();

  const myQuestions = currentUid ? state.questions.filter(q => q.uploadedBy === currentUid) : [];

  if (!myQuestions.length) {

    return `

      <div class="empty-state">

        <div class="empty-state-icon">✍️</div>

        <div class="empty-state-title">No contributed questions yet</div>

        <div class="empty-state-sub">Have unique practice problems or verified GATE PYQs? Add them via <strong>Add Manually</strong> or <strong>Upload JSON</strong>. Your personal submissions will appear here!</div>

        <button class="btn btn-primary btn-sm mt-3" onclick="switchUploadTab('manual', document.querySelectorAll('#upload-tabs .tab-btn')[1])">+ Add Question Now</button>

      </div>`;

  }

  return `

    <div class="card">

      <div class="card-header">

        <div class="card-title">📝 My Contributed Questions (${myQuestions.length})</div>

        <span class="chip" style="background:var(--green-soft);color:var(--green)">✓ Available in Practice Mode</span>

      </div>

      <div style="display:flex;flex-direction:column;gap:8px;max-height:60vh;overflow-y:auto">

        ${myQuestions.map(q => `

          <div style="display:flex;align-items:flex-start;gap:12px;padding:12px;background:var(--bg-input);border-radius:var(--radius-sm)">

            <div style="flex:1">

              <div class="text-sm fw-700">${escapeHtml(q.subject || 'General')} — ${escapeHtml(q.topic||'General')} <span class="q-badge ${q.type}" style="margin-left:6px">${(q.type||'').toUpperCase()}</span></div>

              <div class="text-sm text-muted" style="margin-top:3px;line-height:1.5">${escapeHtml((q.question||'').substring(0,90))}${(q.question||'').length>90?'...':''}</div>

            </div>

            <div style="display:flex;gap:6px;flex-shrink:0;align-items:center">

              <span class="chip">${escapeHtml(q.category||'subject')}</span>

              <button class="btn btn-danger btn-sm" onclick="handleDeleteMyQ('${escapeHtml(q.id)}')" title="Delete this contribution">🗑</button>

            </div>

          </div>

        `).join('')}

      </div>

    </div>`;

}

async function handleDeleteMyQ(id){

  const currentUid = uid();

  const q = state.questions.find(x => x.id === id);

  if (!q) return;

  if (!state.isAdmin && q.uploadedBy !== currentUid) {

    showToast('⚠️ You can only delete your own contributed questions', 'error');

    return;

  }

  if (!confirm('Remove this question from your contributions?')) return;

  await removeQuestion(id);

  showToast('Question removed from contributions', 'info');

  const c = document.getElementById('upload-content');

  if (c) c.innerHTML = buildMyContributionsUI();

  const myTab = document.querySelectorAll('#upload-tabs .tab-btn')[2];

  const myQs = currentUid ? state.questions.filter(x => x.uploadedBy === currentUid) : [];

  if (myTab && !state.isAdmin) myTab.textContent = `📝 My Contributions (${myQs.length})`;

}



function buildJSONUploadUI(){

  return `

    <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px">

      <div>

        <div class="card mb-4">

          <div class="card-header">

            <div class="card-title">📁 Upload JSON File</div>

            ${USE_FB?`<span class="chip" style="background:var(--green-soft);color:var(--green)">☁ Shared for all users</span>`:''}

          </div>

          <div class="upload-zone" id="upload-zone" onclick="document.getElementById('file-input').click()"

               ondragover="event.preventDefault();this.classList.add('dragover')"

               ondragleave="this.classList.remove('dragover')"

               ondrop="handleDrop(event)">

            <span class="upload-zone-icon">📂</span>

            <div class="upload-zone-title">Drop your JSON file here</div>

            <div class="upload-zone-sub">or click to browse • Duplicates auto-skipped</div>

          </div>

          <input type="file" id="file-input" accept=".json" class="hidden" onchange="handleFileUpload(this)"/>

          <div class="flex gap-2 mt-4" style="flex-wrap:wrap">

            <button class="btn btn-primary" onclick="document.getElementById('file-input').click()">📂 Choose File</button>

            <button class="btn btn-secondary" onclick="downloadSampleJSON()">⬇ Sample JSON</button>

            ${state.isAdmin ? `

              <button class="btn btn-secondary" onclick="ingestEasyMocks()" style="background:rgba(99,102,241,0.15);color:var(--primary);border-color:var(--primary)">⚡ Ingest 30 Easy Mocks (Set 1) (1,950 Q)</button>
              <button class="btn btn-secondary" onclick="ingestEasy1Mocks()" style="background:rgba(16,185,129,0.15);color:var(--success);border-color:var(--success)">⚡ Ingest 30 Easy Mocks (Set 2) (1,950 Q)</button>

              <button class="btn btn-secondary" onclick="ingestMediumMocks()" style="background:rgba(234,179,8,0.15);color:var(--yellow);border-color:var(--yellow)">⚡ Ingest 30 Medium Mocks (1,950 Q)</button>
              <button class="btn btn-secondary" onclick="ingestHardMocks()" style="background:rgba(239,68,68,0.15);color:var(--danger);border-color:var(--danger)">⚡ Ingest 30 Hard Mocks (1,950 Q)</button>

              ${USE_FB ? `<button class="btn btn-secondary" onclick="pushAllQuestionsToCloud()" style="background:rgba(20,184,166,0.15);color:var(--teal);border-color:var(--teal)">☁️ Push Questions to Cloud (${state.questions.length})</button>` : ''}

            ` : ''}

          </div>

        </div>

        <div class="card">

          <div class="card-header"><div class="card-title">📊 Question Library</div></div>

          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">

            ${['subject','mock','pyq'].map(cat=>{

              const count=state.questions.filter(q=>q.category===cat||(!q.category&&cat==='subject')).length;

              const icons={subject:'📚',mock:'🎯',pyq:'📅'};

              return `<div class="stat-card" style="padding:14px"><div class="stat-label">${icons[cat]} ${cat.charAt(0).toUpperCase()+cat.slice(1)}</div><div class="stat-value" style="font-size:22px">${count}</div></div>`;

            }).join('')}

            <div class="stat-card" style="padding:14px"><div class="stat-label">📝 Total</div><div class="stat-value" style="font-size:22px">${state.questions.length}</div></div>

          </div>

          <div class="divider"></div>

          ${state.isAdmin ? `<button class="btn btn-danger btn-sm" onclick="clearAllQuestions()">🗑️ Clear All Questions</button>` : ''}

        </div>

      </div>

      <div class="card">

        <div class="card-header"><div class="card-title">📄 JSON Schema</div></div>

        <div class="schema-box">

<span class="schema-comment">// Duplicate check: by ID and question text similarity</span>

[{

  <span class="schema-key">"id"</span>: <span class="schema-string">"q001"</span>,

  <span class="schema-key">"type"</span>: <span class="schema-string">"mcq"</span>,       <span class="schema-comment">// mcq|msq|nat|tf</span>

  <span class="schema-key">"category"</span>: <span class="schema-string">"subject"</span>, <span class="schema-comment">// subject|mock|pyq</span>

  <span class="schema-key">"subject"</span>: <span class="schema-string">"Data Structures"</span>,

  <span class="schema-key">"topic"</span>: <span class="schema-string">"Trees"</span>,

  <span class="schema-key">"difficulty"</span>: <span class="schema-string">"medium"</span>,

  <span class="schema-key">"year"</span>: <span class="schema-string">2023</span>,

  <span class="schema-key">"mockId"</span>: <span class="schema-string">"mock-full-001"</span>,

  <span class="schema-key">"question"</span>: <span class="schema-string">"Question text"</span>,

  <span class="schema-key">"options"</span>: [<span class="schema-string">"A"</span>,<span class="schema-string">"B"</span>,<span class="schema-string">"C"</span>,<span class="schema-string">"D"</span>],

  <span class="schema-key">"correct"</span>: [0],

  <span class="schema-key">"natRange"</span>: {<span class="schema-key">"min"</span>:42,<span class="schema-key">"max"</span>:42},

  <span class="schema-key">"explanation"</span>: <span class="schema-string">"..."</span>,

  <span class="schema-key">"marks"</span>: 1

}]</div>

      </div>

    </div>`;

}



let optRowCount=4;

function buildManualForm(){

  optRowCount=4;

  return `

    <div class="card" style="max-width:800px">

      <div class="card-header"><div class="card-title">✏️ Add New Question</div></div>

      <div class="form-grid">

        <div class="form-group"><label class="form-label">Type *</label>

          <select class="form-select" id="f-type" onchange="onTypeChange()">

            <option value="mcq">MCQ (Single correct)</option>

            <option value="msq">MSQ (Multiple correct)</option>

            <option value="nat">NAT (Numerical)</option>

            <option value="tf">True / False</option>

          </select></div>

        <div class="form-group"><label class="form-label">Category *</label>

          <select class="form-select" id="f-category" onchange="onCategoryChange()">

            <option value="subject">Subject Practice</option>

            <option value="mock">Mock Test</option>

            <option value="pyq">PYQ</option>

            <option value="test_series">Test Series</option>

          </select></div>

        <div class="form-group"><label class="form-label">Subject *</label>

          <select class="form-select" id="f-subject">

            ${SUBJECTS.map(s=>`<option value="${s.name}">${s.name}</option>`).join('')}

          </select></div>

        <div class="form-group"><label class="form-label">Topic</label>

          <input type="text" class="form-input" id="f-topic" placeholder="e.g., Trees, Scheduling"/></div>

        <div class="form-group"><label class="form-label">Difficulty</label>

          <select class="form-select" id="f-difficulty">

            <option value="easy">Easy</option><option value="medium" selected>Medium</option><option value="hard">Hard</option>

          </select></div>

        <div class="form-group"><label class="form-label">Marks</label>

          <select class="form-select" id="f-marks"><option value="1">1 Mark</option><option value="2">2 Marks</option></select></div>

        <div class="form-group" id="f-year-group" style="display:none"><label class="form-label">Year (PYQ)</label>

          <input type="number" class="form-input" id="f-year" placeholder="e.g., 2023"/></div>

        <div class="form-group" id="f-mockid-group" style="display:none"><label class="form-label">Mock ID</label>

          <select class="form-select" id="f-mockid">${MOCK_TESTS.map(m=>`<option value="${m.id}">${m.name}</option>`).join('')}</select></div>

        <div class="form-group full"><label class="form-label">Question Text *</label>

          <textarea class="form-textarea" id="f-question" placeholder="Enter your question here..."></textarea></div>

        <div class="form-group full" id="f-options-group"><label class="form-label">Options (select correct answer)</label>

          <div class="options-editor" id="options-editor">

            ${[0,1,2,3].map(i=>`<div class="option-editor-row">

              <input type="radio" name="correct-opt" value="${i}" ${i===0?'checked':''}/>

              <input type="text" class="option-editor-input" id="opt-text-${i}" placeholder="Option ${String.fromCharCode(65+i)}"/>

            </div>`).join('')}

          </div>

          <button class="btn btn-secondary btn-sm mt-2" onclick="addOptRow()">+ Add Option</button></div>

        <div class="form-group full" id="f-nat-group" style="display:none"><label class="form-label">Correct Answer Range (NAT)</label>

          <div style="display:flex;gap:12px">

            <div class="form-group" style="flex:1"><label class="form-label">Min</label><input type="number" class="form-input" id="f-nat-min" step="any"/></div>

            <div class="form-group" style="flex:1"><label class="form-label">Max</label><input type="number" class="form-input" id="f-nat-max" step="any"/></div>

          </div></div>

        <div class="form-group full"><label class="form-label">Explanation</label>

          <textarea class="form-textarea" id="f-explanation" placeholder="Explain the correct answer..." style="min-height:80px"></textarea></div>

        <div class="form-group full" style="display:flex;gap:12px;justify-content:flex-end">

          <button class="btn btn-secondary" onclick="clearManualForm()">Clear</button>

          <button class="btn btn-primary" onclick="submitManualQuestion()">+ Add Question</button>

        </div>

      </div>

    </div>`;

}



function buildManageUI(){

  if (!state.isAdmin) {

    return `<div class="empty-state"><div class="empty-state-icon">🔒</div><div class="empty-state-title">Admin Privileges Required</div><div class="empty-state-sub">Only verified administrators can manage the question bank.</div></div>`;

  }

  if (!state.questions.length) return `<div class="empty-state"><div class="empty-state-icon">📭</div><div class="empty-state-title">No questions yet</div></div>`;

  return `<div class="card"><div class="card-header"><div class="card-title">All Questions (${state.questions.length})</div>${state.isAdmin ? `<button class="btn btn-danger btn-sm" onclick="clearAllQuestions()">🗑️ Clear All</button>` : ''}</div>

    <div style="display:flex;flex-direction:column;gap:8px;max-height:60vh;overflow-y:auto">

      ${state.questions.map(q=>`

        <div style="display:flex;align-items:flex-start;gap:12px;padding:12px;background:var(--bg-input);border-radius:var(--radius-sm)">

          <div style="flex:1">

            <div class="text-sm fw-700">${escapeHtml(q.subject || 'General')} — ${escapeHtml(q.topic||'General')} <span class="q-badge ${q.type}" style="margin-left:6px">${(q.type||'').toUpperCase()}</span></div>

            <div class="text-sm text-muted" style="margin-top:3px;line-height:1.5">${escapeHtml((q.question||'').substring(0,80))}${(q.question||'').length>80?'...':''}</div>

          </div>

          <div style="display:flex;gap:6px;flex-shrink:0">

            <span class="chip">${escapeHtml(q.category||'subject')}</span>

            ${state.isAdmin ? `<button class="btn btn-danger btn-sm" onclick="handleDeleteQ('${escapeHtml(q.id)}')">🗑</button>` : ''}

          </div>

        </div>`).join('')}

    </div></div>`;

}



function onTypeChange(){

  const t=document.getElementById('f-type')?.value;

  document.getElementById('f-options-group').style.display=t==='nat'?'none':'block';

  document.getElementById('f-nat-group').style.display=t==='nat'?'block':'none';

  if(t==='tf'){

    document.getElementById('options-editor').innerHTML=`

      <div class="option-editor-row"><input type="radio" name="correct-opt" value="0" checked/><input type="text" class="option-editor-input" value="True" readonly/></div>

      <div class="option-editor-row"><input type="radio" name="correct-opt" value="1"/><input type="text" class="option-editor-input" value="False" readonly/></div>`;

  }

}

function onCategoryChange(){

  const cat=document.getElementById('f-category')?.value;

  document.getElementById('f-year-group').style.display=cat==='pyq'?'block':'none';

  document.getElementById('f-mockid-group').style.display=cat==='mock'?'block':'none';

}

function addOptRow(){

  const ed=document.getElementById('options-editor'),t=document.getElementById('f-type')?.value,i=optRowCount++;

  const row=document.createElement('div'); row.className='option-editor-row';

  row.innerHTML=`<input type="${t==='msq'?'checkbox':'radio'}" name="correct-opt" value="${i}"/><input type="text" class="option-editor-input" placeholder="Option ${String.fromCharCode(65+(i%26))}"/>`;

  ed.appendChild(row);

}



async function submitManualQuestion(){

  const type=document.getElementById('f-type')?.value;

  const cat=document.getElementById('f-category')?.value;

  const subject=document.getElementById('f-subject')?.value;

  const topic=document.getElementById('f-topic')?.value?.trim()||null;

  const diff=document.getElementById('f-difficulty')?.value;

  const marks=parseInt(document.getElementById('f-marks')?.value);

  const question=document.getElementById('f-question')?.value?.trim();

  const expl=document.getElementById('f-explanation')?.value?.trim()||'';

  if (!question){showToast('Please enter question text','error');return;}



  let options=[],correct=[],natRange=null;

  if (type==='nat'){

    const mn=parseFloat(document.getElementById('f-nat-min')?.value);

    const mx=parseFloat(document.getElementById('f-nat-max')?.value);

    if (isNaN(mn)||isNaN(mx)){showToast('Enter valid NAT answer range','error');return;}

    natRange={min:mn,max:mx}; correct=[mn];

  } else {

    document.getElementById('options-editor')?.querySelectorAll('.option-editor-row').forEach((row,i)=>{

      const inp=row.querySelector('.option-editor-input');

      const chk=row.querySelector('input[type="radio"],input[type="checkbox"]');

      if (inp?.value?.trim()){options.push(inp.value.trim());if(chk?.checked) correct.push(i);}

    });

    if (options.length<2){showToast('Add at least 2 options','error');return;}

    if (!correct.length){showToast('Select the correct option(s)','error');return;}

  }



  const finalType = type === 'tf' ? 'mcq' : type;

  const q={

    id:'q'+Date.now()+Math.random().toString(36).slice(2,6),

    type: finalType,

    category:cat,subject,topic,difficulty:diff,marks,question,explanation:expl,

    options,correct,natRange,

    year: cat==='pyq'?parseInt(document.getElementById('f-year')?.value)||null:null,

    mockId:cat==='mock'?document.getElementById('f-mockid')?.value:null,

    uploadedBy: uid(),

    source: state.isAdmin ? 'official' : 'community',

    createdAt: new Date().toISOString(),

  };



  // Duplicate check

  const {dupe,reason}=isDuplicate(q);

  if (dupe){showToast(`⚠️ Duplicate detected: ${reason}`,'error',4000);return;}



  await persistQuestion(q);

  showToast(`✅ Question added to ${cat} bank!`,'success');

  clearManualForm();

}



function clearManualForm(){

  ['f-question','f-explanation','f-topic'].forEach(id=>{const el=document.getElementById(id);if(el)el.value='';});

  document.getElementById('options-editor')?.querySelectorAll('.option-editor-input').forEach(i=>i.value='');

}



function handleFileUpload(input){

  const file=input.files[0]; if(!file) return;

  const reader=new FileReader();

  reader.onload=e=>{

    try{

      const d=JSON.parse(e.target.result);

      bulkImportQuestions(Array.isArray(d)?d:[d]);

    }catch(err){

      showToast('❌ Invalid JSON: '+err.message,'error');

    }

    input.value=''; // Reset so re-uploading the same file works

  };

  reader.readAsText(file);

}



function handleDrop(e){

  e.preventDefault(); document.getElementById('upload-zone')?.classList.remove('dragover');

  const file=e.dataTransfer.files[0]; if(!file) return;

  const reader=new FileReader();

  reader.onload=ev=>{

    try{

      const d=JSON.parse(ev.target.result);

      bulkImportQuestions(Array.isArray(d)?d:[d]);

    }catch(err){

      showToast('❌ Invalid JSON: '+err.message,'error');

    }

  };

  reader.readAsText(file);

}



async function handleDeleteQ(id){

  if (!state.isAdmin) {

    showToast('⚠️ Admin privileges required to delete questions', 'error');

    return;

  }

  await removeQuestion(id);

  showToast('Question deleted','info');

  const c = document.getElementById('upload-content');

  if (c) c.innerHTML=buildManageUI();

  const manageBtn = document.querySelector('#upload-tabs .tab-btn:last-child');

  if (manageBtn) manageBtn.textContent=`🗂️ Manage (${state.questions.length})`;

}



function downloadSampleJSON(){

  try {

    const data = (state.questions && state.questions.length) ? state.questions : [{

      id: "sample_001",

      type: "mcq",

      category: "pyq",

      year: 2024,

      subject: "Algorithms",

      topic: "Asymptotic Analysis",

      difficulty: "easy",

      marks: 1,

      question: "Sample GATE question text...",

      options: ["Option A", "Option B", "Option C", "Option D"],

      correct: [0],

      explanation: "Step-by-step solution..."

    }];

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });

    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');

    a.href = url;

    a.download = 'sample_questions.json';

    document.body.appendChild(a);

    a.click();

    setTimeout(() => {

      document.body.removeChild(a);

      URL.revokeObjectURL(url);

    }, 150);

    showToast('✅ Sample JSON downloaded!', 'success');

  } catch(err) {

    fetch('./data/sample_questions.json')

      .then(r => r.json())

      .then(data => {

        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });

        const url = URL.createObjectURL(blob);

        const a = document.createElement('a');

        a.href = url;

        a.download = 'sample_questions.json';

        document.body.appendChild(a);

        a.click();

        setTimeout(() => {

          document.body.removeChild(a);

          URL.revokeObjectURL(url);

        }, 150);

        showToast('✅ Sample JSON downloaded!', 'success');

      })

      .catch(() => showToast('Could not download sample', 'error'));

  }

}



// ─── TOAST ───────────────────────────────────────────────────────────────────

function showToast(msg,type='info',duration=3500){

  const c=document.getElementById('toast-container');

  const t=document.createElement('div');

  t.className=`toast ${type}`; t.innerHTML=msg; c.appendChild(t);

  setTimeout(()=>{t.style.animation='toastOut 0.3s ease forwards';setTimeout(()=>t.remove(),300);},duration);

}



// ─── UTILS ───────────────────────────────────────────────────────────────────

function shuffleArr(arr){ for(let i=arr.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[arr[i],arr[j]]=[arr[j],arr[i]];}return arr; }



// ─── INIT ─────────────────────────────────────────────────────────────────────



// ── SECONDS FORMATTER HELPER ──

function fmtSec(sec) {

  sec = Math.max(0, parseInt(sec) || 0);

  const m = Math.floor(sec / 60);

  const s = sec % 60;

  if (m === 0) return `${s}s`;

  return `${m}m ${s < 10 ? '0' : ''}${s}s`;

}



// ── FULLSCREEN EXAM MODE ──

function toggleExamFullscreen() {

  if (!document.fullscreenElement) {

    document.documentElement.requestFullscreen?.().then(() => {

      updateFullscreenBtn(true);

    }).catch(err => {

      console.warn('[Exam] Fullscreen request:', err);

    });

  } else {

    document.exitFullscreen?.().then(() => {

      updateFullscreenBtn(false);

    }).catch(err => {

      console.warn('[Exam] Exit fullscreen:', err);

    });

  }

}



function updateFullscreenBtn(isFull) {

  const btn = document.getElementById('exam-fullscreen-btn');

  if (btn) {

    btn.innerHTML = isFull

      ? '🗗 <span class="hide-xs">Exit Fullscreen</span>'

      : '⛶ <span class="hide-xs">Fullscreen</span>';

  }

}



document.addEventListener('fullscreenchange', () => {

  updateFullscreenBtn(!!document.fullscreenElement);

});



// Proctored Exam Focus / Tab Switch Alert

document.addEventListener('visibilitychange', () => {

  if (document.visibilityState === 'hidden' && state.activeTest && !state.activeTest.submitted) {

    state.activeTest.tabSwitches = (state.activeTest.tabSwitches || 0) + 1;

    showToast(`⚠️ Exam Alert: Tab switch detected (#${state.activeTest.tabSwitches})! Maintain full focus on the exam.`, 'error');

  }

});



// ── PRINT / SAVE TEST REPORT ──

function printTestReport() {

  window.print();

}



// ── DRAGGABLE GATE CALCULATOR ──

function setupCalcDraggable() {

  const modal = document.getElementById('gate-calc-modal');

  const handle = document.getElementById('calc-drag-handle');

  if (!modal || !handle || modal._dragInitialized) return;

  modal._dragInitialized = true;



  let isDragging = false;

  let startX = 0, startY = 0, initialLeft = 0, initialTop = 0;



  handle.addEventListener('pointerdown', (e) => {

    if (e.target.closest('.calc-close-btn') || e.target.closest('button')) return;

    isDragging = true;

    modal.classList.add('is-dragging');

    const rect = modal.getBoundingClientRect();

    startX = e.clientX;

    startY = e.clientY;

    initialLeft = rect.left;

    initialTop = rect.top;

    modal.style.right = 'auto';

    modal.style.bottom = 'auto';

    modal.style.transform = 'none';

    modal.style.left = `${initialLeft}px`;

    modal.style.top = `${initialTop}px`;

    try { handle.setPointerCapture(e.pointerId); } catch(err) {}

  });



  window.addEventListener('pointermove', (e) => {

    if (!isDragging) return;

    const dx = e.clientX - startX;

    const dy = e.clientY - startY;

    const newLeft = Math.max(10, Math.min(window.innerWidth - modal.offsetWidth - 10, initialLeft + dx));

    const newTop = Math.max(10, Math.min(window.innerHeight - modal.offsetHeight - 10, initialTop + dy));

    modal.style.left = `${newLeft}px`;

    modal.style.top = `${newTop}px`;

  });



  window.addEventListener('pointerup', () => {

    if (isDragging) {

      isDragging = false;

      modal.classList.remove('is-dragging');

    }

  });

}



// ── OFFICIAL GATE SCORE & AIR PREDICTOR ENGINE ──

function calculateGatePrediction(marks, category = 'GEN') {

  marks = Math.max(0, Math.min(100, parseFloat(marks) || 0));

  const Mq = category === 'SC' ? 20.0 : category === 'OBC' ? 26.5 : 29.5;

  const Mt = 78.5;

  const Sq = 350;

  const St = 900;

  let score = 0;

  if (marks < Mq) {

    score = Math.round(Sq * (marks / Mq));

  } else {

    score = Math.min(1000, Math.round(Sq + (St - Sq) * ((marks - Mq) / (Mt - Mq))));

  }



  let air = '';

  let eligibility = '';

  let airBadgeClass = '#22c55e';



  if (score >= 900) {

    air = 'AIR 1 – 100';

    eligibility = 'Top 100 Ranker! Direct interview-exempt admission to IISc Bangalore & IIT Bombay (M.Tech CSE / Direct PhD) and Top PSUs (IOCL, ONGC, NTPC).';

  } else if (score >= 800) {

    air = 'AIR 101 – 450';

    eligibility = 'Top Tier IIT CSE: IIT Delhi, IIT Madras, IIT Kanpur, IIT Kharagpur (M.Tech CSE / AI & Data Science). PSU Shortlisting Guaranteed.';

  } else if (score >= 700) {

    air = 'AIR 451 – 1,200';

    eligibility = 'Established IITs & Top NITs: IIT Roorkee, IIT Guwahati, IIT Hyderabad, NIT Trichy, NIT Surathkal, IIIT Bangalore / Hyderabad.';

  } else if (score >= 600) {

    air = 'AIR 1,201 – 2,800';

    eligibility = 'Top NITs & Newer IITs: NIT Warangal, NIT Calicut, VNIT, MNIT, IIT BHU, IIT Gandhinagar, IIT Ropar.';

  } else if (score >= 500) {

    air = 'AIR 2,801 – 5,500';

    eligibility = 'Good NITs & Central Universities: NIT Durgapur, NIT Jalandhar, NIT Silchar, BITS Pilani (Higher Degree).';

  } else if (score >= 350) {

    air = 'AIR 5,501 – 15,000';

    eligibility = 'GATE Qualified. Eligible for CCMT counseling across Tier-2/3 NITs, IIEST, State Engineering Colleges, and stipend M.Tech.';

    airBadgeClass = '#f59e0b';

  } else {

    air = 'Below Qualifying Cutoff';

    eligibility = 'Marks below estimated cutoff. Continue practicing foundational mocks and high-weightage core CS topics.';

    airBadgeClass = '#ef4444';

  }



  return { marks, score, air, eligibility, category, airBadgeClass, isQualified: marks >= Mq };

}



function buildPredictorCardHTML(marksVal, catVal) {

  const latestSession = state.testSessions?.[state.testSessions.length - 1];

  const defaultMarks = marksVal !== null && marksVal !== undefined ? marksVal : (latestSession ? latestSession.score : 55);

  const cat = catVal || state.predictedCategory || 'GEN';

  const pred = calculateGatePrediction(defaultMarks, cat);



  return `

    <div class="predictor-card" id="gate-predictor-container">

      <div class="predictor-card-header">

        <div class="predictor-title">

          <span>🎯 Official GATE Score & Rank Simulator</span>

          <span class="badge" style="background:rgba(108,99,255,0.2);color:var(--accent);font-size:11px">IISc/IIT Model</span>

        </div>

        <div style="display:flex;align-items:center;gap:8px">

          <label style="font-size:12px;color:var(--text-secondary);font-weight:600">Category:</label>

          <select class="form-select form-select-sm" style="width:auto;padding:4px 8px;font-size:12px;background:var(--bg-input);border:1px solid var(--border);border-radius:6px;color:var(--text-primary)" onchange="updatePredictorCategory(this.value)">

            <option value="GEN" ${cat==='GEN'?'selected':''}>General / EWS (Cutoff ~29.5)</option>

            <option value="OBC" ${cat==='OBC'?'selected':''}>OBC-NCL (Cutoff ~26.5)</option>

            <option value="SC" ${cat==='SC'?'selected':''}>SC / ST / PwD (Cutoff ~20.0)</option>

          </select>

        </div>

      </div>



      <div class="predictor-slider-container">

        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">

          <span style="font-size:13px;font-weight:600;color:var(--text-secondary)">Target Exam Marks (out of 100):</span>

          <span style="font-size:18px;font-weight:900;color:var(--accent)">${pred.marks} / 100</span>

        </div>

        <input type="range" class="predictor-slider" min="0" max="100" step="0.5" value="${pred.marks}" oninput="updatePredictorMarks(this.value)" />

      </div>



      <div class="predictor-output-grid">

        <div class="predictor-output-box">

          <div style="font-size:11px;color:var(--text-muted);font-weight:700;text-transform:uppercase">Simulated GATE Score</div>

          <div class="predictor-score-huge">${pred.score} <span style="font-size:14px;color:var(--text-muted);font-weight:600">/ 1000</span></div>

        </div>

        <div class="predictor-output-box">

          <div style="font-size:11px;color:var(--text-muted);font-weight:700;text-transform:uppercase">Estimated All India Rank (AIR)</div>

          <div class="predictor-air-huge" style="color:${pred.airBadgeClass}">${pred.air}</div>

        </div>

      </div>

      <div class="predictor-eligibility-badge" style="background:${pred.isQualified ? 'rgba(34,197,94,0.15)' : 'rgba(239,68,68,0.15)'};color:${pred.airBadgeClass}">

        ${pred.eligibility}

      </div>

    </div>`;

}



function updatePredictorMarks(val) {

  state.predictedMarks = parseFloat(val);

  const container = document.getElementById('gate-predictor-container');

  if (container) {

    container.outerHTML = buildPredictorCardHTML(state.predictedMarks, state.predictedCategory);

  }

}



function updatePredictorCategory(cat) {

  state.predictedCategory = cat;

  const container = document.getElementById('gate-predictor-container');

  if (container) {

    container.outerHTML = buildPredictorCardHTML(state.predictedMarks, state.predictedCategory);

  }

}



// ── MISTAKE VAULT & REVISION NOTEBOOK VIEW ──

function getMistakeData() {

  const latestAttemptMap = new Map();

  state.attempts.forEach(a => {

    if (!latestAttemptMap.has(a.questionId) || a.date > latestAttemptMap.get(a.questionId).date) {

      latestAttemptMap.set(a.questionId, a);

    }

  });



  const allMistakeQIds = new Set();

  state.attempts.filter(a => a.correct === false).forEach(a => allMistakeQIds.add(a.questionId));



  const unresolved = [];

  const resolved = [];



  allMistakeQIds.forEach(id => {

    const q = state.questions.find(x => x.id === id);

    if (!q) return;

    const latest = latestAttemptMap.get(id);

    if (latest && latest.correct === true) {

      resolved.push({ q, latest });

    } else {

      unresolved.push({ q, latest });

    }

  });



  const bookmarked = [];

  if (state.bookmarks) {

    state.bookmarks.forEach(id => {

      const q = state.questions.find(x => x.id === id);

      if (q) bookmarked.push(q);

    });

  }



  return { unresolved, resolved, bookmarked, totalMistakes: allMistakeQIds.size };

}



function renderMistakes(c) {

  const { unresolved, resolved, bookmarked, totalMistakes } = getMistakeData();

  const subFilter = state.mistakeSubject || 'all';

  const statusFilter = state.mistakeStatus || 'unresolved';

  const tagFilter = state.mistakeTagFilter || 'all';

  const search = (state.mistakeSearch || '').trim().toLowerCase();



  let displayed = [];

  if (statusFilter === 'unresolved') {

    displayed = unresolved.map(item => item.q);

  } else if (statusFilter === 'resolved') {

    displayed = resolved.map(item => item.q);

  } else if (statusFilter === 'bookmarked') {

    displayed = bookmarked;

  } else {

    // all recorded mistakes

    const map = new Map();

    [...unresolved, ...resolved].forEach(item => map.set(item.q.id, item.q));

    displayed = Array.from(map.values());

  }



  if (subFilter !== 'all') {

    displayed = displayed.filter(q => q.subject === subFilter);

  }

  if (tagFilter !== 'all') {

    if (tagFilter === 'untagged') {

      displayed = displayed.filter(q => !state.errorTags?.[q.id]);

    } else {

      displayed = displayed.filter(q => state.errorTags?.[q.id] === tagFilter);

    }

  }

  if (search) {

    displayed = displayed.filter(q =>

      (q.question && q.question.toLowerCase().includes(search)) ||

      (q.topic && q.topic.toLowerCase().includes(search)) ||

      (q.subject && q.subject.toLowerCase().includes(search))

    );

  }



  const subjectsWithMistakes = Array.from(new Set([...unresolved, ...resolved].map(item => item.q.subject))).sort();



  c.innerHTML = `

    <!-- ── MISTAKE HERO BANNER ── -->

    <div class="mistake-hero">

      <div class="mistake-hero-text">

        <h2>📖 Mistake Vault & Weakness Diagnostic</h2>

        <p>Every mistake in your mock exams and practice drills is recorded here automatically. Turn your past errors into guaranteed marks on exam day with targeted re-drills.</p>

      </div>

      <div class="mistake-stats-pills">

        <div class="mistake-stat-pill">

          <span class="mistake-stat-pill-val" style="color:#ef4444">${unresolved.length}</span>

          <span class="mistake-stat-pill-lbl">Unresolved</span>

        </div>

        <div class="mistake-stat-pill">

          <span class="mistake-stat-pill-val" style="color:#22c55e">${resolved.length}</span>

          <span class="mistake-stat-pill-lbl">Mastered</span>

        </div>

        <div class="mistake-stat-pill">

          <span class="mistake-stat-pill-val" style="color:#f59e0b">${bookmarked.length}</span>

          <span class="mistake-stat-pill-lbl">Starred</span>

        </div>

        <div class="mistake-stat-pill">

          <span class="mistake-stat-pill-val" style="color:var(--accent)">${totalMistakes}</span>

          <span class="mistake-stat-pill-lbl">Total Vault</span>

        </div>

      </div>

    </div>



    <!-- ── CONTROLS & ACTION BAR ── -->

    <div class="mistake-controls-bar">

      <div class="mistake-filters-group">

        <button class="btn btn-primary btn-sm" onclick="startMistakeReTest()" style="font-weight:700" type="button" ${!unresolved.length ? 'disabled' : ''}>

          🔥 Re-Test My Mistakes (${Math.min(15, unresolved.length)} Qs)

        </button>

        <div style="display:flex;align-items:center;gap:6px">

          <button class="btn btn-secondary btn-sm ${statusFilter==='unresolved'?'btn-primary':''}" onclick="setMistakeStatusFilter('unresolved')">Unresolved (${unresolved.length})</button>

          <button class="btn btn-secondary btn-sm ${statusFilter==='bookmarked'?'btn-primary':''}" onclick="setMistakeStatusFilter('bookmarked')">⭐ Starred (${bookmarked.length})</button>

          <button class="btn btn-secondary btn-sm ${statusFilter==='resolved'?'btn-primary':''}" onclick="setMistakeStatusFilter('resolved')">✅ Mastered (${resolved.length})</button>

          <button class="btn btn-secondary btn-sm ${statusFilter==='all'?'btn-primary':''}" onclick="setMistakeStatusFilter('all')">All (${totalMistakes})</button>

        </div>

      </div>

      <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap">

        <input type="text" class="search-input" placeholder="Search mistakes by keyword..."

          style="padding:6px 12px;font-size:12px;width:200px"

          value="${escapeHtml(state.mistakeSearch || '')}"

          oninput="updateMistakeSearch(this.value)" />

        <select class="form-select form-select-sm" style="width:auto;padding:6px 10px;font-size:12px;background:var(--bg-input);border:1px solid var(--border);border-radius:6px;color:var(--text-primary)" onchange="setMistakeSubjectFilter(this.value)">

          <option value="all" ${subFilter==='all'?'selected':''}>All Subjects (${subjectsWithMistakes.length})</option>

          ${subjectsWithMistakes.map(s => `<option value="${escapeHtml(s)}" ${subFilter===s?'selected':''}>${escapeHtml(s)}</option>`).join('')}

        </select>

        <select class="form-select form-select-sm" style="width:auto;padding:6px 10px;font-size:12px;background:var(--bg-input);border:1px solid var(--border);border-radius:6px;color:var(--text-primary)" onchange="setMistakeTagFilter(this.value)">

          <option value="all" ${tagFilter==='all'?'selected':''}>All Root Causes</option>

          <option value="silly" ${tagFilter==='silly'?'selected':''}>🟡 Silly Mistakes</option>

          <option value="misread" ${tagFilter==='misread'?'selected':''}>🔴 Misread Questions</option>

          <option value="concept" ${tagFilter==='concept'?'selected':''}>🟣 Conceptual Gaps</option>

          <option value="formula" ${tagFilter==='formula'?'selected':''}>🔵 Formula Forgotten</option>

          <option value="time" ${tagFilter==='time'?'selected':''}>⏳ Time Pressure</option>

          <option value="untagged" ${tagFilter==='untagged'?'selected':''}>⚪ Untagged</option>

        </select>

      </div>

    </div>



    <!-- ── MISTAKE QUESTIONS LIST ── -->

    ${!displayed.length ? `

      <div class="empty-state">

        <div class="empty-state-icon">🎉</div>

        <div class="empty-state-title">No mistakes matching your filter</div>

        <div class="empty-state-sub">Keep solving full mock tests and practicing questions to track weak areas!</div>

      </div>

    ` : `

      <div class="mistake-list">

        ${displayed.map((q, idx) => {

          const isBmk = state.bookmarks?.has(q.id);

          const att = state.attempts.find(a => a.questionId === q.id);

          const timeSec = att?.timeMs ? Math.round(att.timeMs / 1000) : 0;

          const labels = ['A','B','C','D'];

          return `

            <div class="mistake-card">

              <div class="mistake-card-top">

                <div class="mistake-meta-tags">

                  <span class="mistake-tag mistake-tag-danger">Missed</span>

                  <span class="mistake-tag mistake-tag-subject">${escapeHtml(q.subject)}</span>

                  ${q.topic ? `<span class="chip" style="font-size:11px">${escapeHtml(q.topic)}</span>` : ''}

                  <span class="chip" style="font-size:11px">${q.type?.toUpperCase()} • ${q.marks} Mark${q.marks>1?'s':''}</span>

                  ${timeSec > 0 ? `<span class="mistake-tag mistake-tag-dwell">⏱️ ${fmtSec(timeSec)}</span>` : ''}

                </div>

                <div style="display:flex;align-items:center;gap:8px">

                  <button class="btn btn-secondary btn-sm" onclick="openPlaylistModal('${q.id}')" style="padding:3px 8px;font-size:11px" title="Add to Smart Playlist" type="button">

                    🗂️ Playlist

                  </button>

                  <button class="btn btn-secondary btn-sm" onclick="toggleBookmark('${q.id}'); renderMistakes(document.getElementById('page-content'));" style="padding:3px 8px;font-size:11px" type="button">

                    ${isBmk ? '⭐ Starred' : '☆ Star'}

                  </button>

                  <button class="btn btn-secondary btn-sm" onclick="markMistakeResolved('${q.id}')" style="padding:3px 8px;font-size:11px;color:#22c55e" type="button">

                    ✅ Mark Mastered

                  </button>

                </div>

              </div>

              <div style="font-size:14px;line-height:1.7;margin-bottom:12px;font-weight:500">

                <strong style="color:var(--accent);margin-right:6px">Q${idx + 1}.</strong>${formatQuestionContent(q.question)}

              </div>

              ${q.options && q.options.length ? `

                <div class="options-list mb-3">

                  ${q.options.map((opt, oIdx) => {

                    const isCorrect = q.correct?.includes(oIdx);

                    return `<div class="option-item ${isCorrect ? 'correct' : ''}" style="cursor:default">

                      <div class="option-marker">${labels[oIdx]}</div>

                      <div class="option-text">${formatQuestionContent(opt)}</div>

                    </div>`;

                  }).join('')}

                </div>

              ` : `

                <div style="font-size:13px;color:var(--green);margin-bottom:8px">

                  Correct Answer: <strong>${q.correct?.[0] !== undefined ? q.correct[0] : (q.natRange ? `${q.natRange.min} - ${q.natRange.max}` : '')}</strong>

                </div>

              `}

              <div class="mistake-solution-box">

                <div style="font-weight:700;color:var(--accent);margin-bottom:4px">💡 Step-by-Step Explanation:</div>

                ${buildMultiMethodExplanationHTML(q)}

                ${buildStudentShortcutNoteHTML(q.id)}

              </div>

              ${buildErrorTagButtonsHTML(q.id, state.errorTags?.[q.id])}

            </div>

          `;

        }).join('')}

      </div>

    `}

  `;

}



function setMistakeStatusFilter(st) {

  state.mistakeStatus = st;

  renderMistakes(document.getElementById('page-content'));

}



function setMistakeSubjectFilter(sub) {

  state.mistakeSubject = sub;

  renderMistakes(document.getElementById('page-content'));

}



function updateMistakeSearch(term) {

  state.mistakeSearch = term;

  renderMistakes(document.getElementById('page-content'));

}



async function markMistakeResolved(qId) {

  const att = {

    questionId: qId,

    correct: true,

    timeMs: 60000,

    date: Date.now(),

    uid: uid()

  };

  await persistAttempt(att);

  showToast('Question marked as mastered!', 'success');

  renderMistakes(document.getElementById('page-content'));

}



function startMistakeReTest() {

  const { unresolved } = getMistakeData();

  if (!unresolved.length) {

    showToast('No unresolved mistakes found! Great job!', 'info');

    return;

  }

  const pool = unresolved.map(item => item.q);

  const selected = shuffleArr([...pool]).slice(0, 15);

  state.practiceQueue = selected;

  state.currentQuestion = 0;

  state.practiceAnswered = false;

  state.practiceSelected = null;

  state.activeMockPaper = null;

  state.activeTest = null;

  navigate('practice');

  showToast(`Launched Mistake Drill with ${selected.length} questions!`, 'success');

}



// ── PWA INSTALLATION HELPER ──

window.deferredPwaPrompt = null;

window.addEventListener('beforeinstallprompt', (e) => {

  e.preventDefault();

  window.deferredPwaPrompt = e;

  const btn = document.getElementById('pwa-install-btn');

  if (btn) btn.style.display = 'inline-flex';

});



function triggerPwaInstall() {

  if (window.deferredPwaPrompt) {

    window.deferredPwaPrompt.prompt();

    window.deferredPwaPrompt.userChoice.then(choice => {

      if (choice.outcome === 'accepted') {

        showToast('Thank you for installing GATE CSE App!', 'success');

      }

      window.deferredPwaPrompt = null;

      const btn = document.getElementById('pwa-install-btn');

      if (btn) btn.style.display = 'none';

    });

  } else {

    showToast('Offline app is ready! Access offline practice anytime from browser menu.', 'info');

  }

}





// ═════════════════════════════════════════════════════════════════════════════

// ── SEVEN HIGH-IMPACT ENGINE UPGRADES ──

// ═════════════════════════════════════════════════════════════════════════════



// ── 1. EXAM CRASH PROTECTION & AUTO-SAVE RECOVERY ──

const AUTOSAVE_TEST_KEY = 'gate_active_test_autosave_v1';



function saveExamAutoSaveState() {

  if (!state.activeTest || state.activeTest.submitted) return;

  try {

    const copy = {

      mockId: state.activeTest.mockId,

      mock: state.activeTest.mock,

      answers: state.activeTest.answers,

      marked: Array.from(state.activeTest.marked || []),

      visited: Array.from(state.activeTest.visited || [state.activeTest.currentQ || 0]),

      currentQ: state.activeTest.currentQ || 0,

      timeLeft: state.activeTest.timeLeft,

      timePerQ: state.activeTest.timePerQ || [],

      tabSwitches: state.activeTest.tabSwitches || 0,

      savedAt: Date.now()

    };

    localStorage.setItem(AUTOSAVE_TEST_KEY, JSON.stringify(copy));

    const timeEl = document.getElementById('test-autosave-time');
    const badgeEl = document.getElementById('test-autosave-badge');
    if (timeEl) {
      const d = new Date();
      timeEl.textContent = d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    }
    if (badgeEl) {
      badgeEl.classList.remove('autosave-pulse');
      void badgeEl.offsetWidth;
      badgeEl.classList.add('autosave-pulse');
    }

  } catch(e) {}

}



function clearExamAutoSave() {

  try { localStorage.removeItem(AUTOSAVE_TEST_KEY); } catch(e) {}

}



function checkExamAutoSaveRecovery() {

  try {

    const raw = localStorage.getItem(AUTOSAVE_TEST_KEY);

    if (!raw) return;

    const data = JSON.parse(raw);

    if (!data || !data.mockId || data.timeLeft <= 10) {

      clearExamAutoSave();

      return;

    }

    showResumeExamModal(data);

  } catch(e) {}

}



function showResumeExamModal(data) {

  let modal = document.getElementById('resume-exam-modal');

  if (!modal) {

    modal = document.createElement('div');

    modal.id = 'resume-exam-modal';

    modal.className = 'resume-modal-backdrop';

    document.body.appendChild(modal);

  }

  const mockName = data.mock?.name || 'In-Progress Exam';

  const minLeft = Math.round(data.timeLeft / 60);

  const agoMin = Math.max(1, Math.round((Date.now() - (data.savedAt || Date.now())) / 60000));

  modal.innerHTML = `

    <div class="resume-modal-card">

      <div class="resume-modal-title">

        <span>🔄 Unfinished Exam Detected</span>

      </div>

      <div class="resume-modal-body">

        You have an active in-progress attempt for <strong>${escapeHtml(mockName)}</strong> with <strong>${minLeft} minutes</strong> remaining (saved ${agoMin} minute${agoMin>1?'s':''} ago). Would you like to resume where you left off?

      </div>

      <div class="resume-modal-actions">

        <button class="btn btn-secondary btn-sm" onclick="discardSavedExam()" type="button">Discard</button>

        <button class="btn btn-primary btn-sm" onclick="resumeSavedExam()" type="button" style="font-weight:700">Resume Exam</button>

      </div>

    </div>

  `;

  modal.style.display = 'flex';

}



function resumeSavedExam() {

  try {

    const raw = localStorage.getItem(AUTOSAVE_TEST_KEY);

    if (!raw) return;

    const data = JSON.parse(raw);

    document.getElementById('resume-exam-modal')?.remove();

    const mock = data.mock || MOCK_TESTS.find(m => m.id === data.mockId) || FULL_LENGTH_PYQ_EXAMS.find(e => e.id === data.mockId);

    const questions = getMockQuestions(data.mockId);

    if (!questions.length) { showToast('Unable to resume: questions not found', 'error'); clearExamAutoSave(); return; }

    state.activeTest = {

      mockId: data.mockId,

      mock,

      questions,

      answers: data.answers || new Array(questions.length).fill(null),

      marked: new Set(data.marked || []),

      visited: new Set(data.visited || [data.currentQ || 0]),

      currentQ: data.currentQ || 0,

      timeLeft: data.timeLeft,

      timePerQ: data.timePerQ || new Array(questions.length).fill(0),

      tabSwitches: data.tabSwitches || 0,

      submitted: false

    };

    renderTestMode();

    showToast('Resumed in-progress exam successfully!', 'success');

  } catch(e) {

    console.error(e);

    clearExamAutoSave();

  }

}



function discardSavedExam() {

  clearExamAutoSave();

  document.getElementById('resume-exam-modal')?.remove();

  showToast('Unfinished exam discarded.', 'info');

}



// ── 2. TCS iON 5-STATE QUESTION PALETTE ENGINE ──

function updatePaletteStates() {

  if (!state.activeTest) return;

  const { questions, currentQ, answers, marked, visited } = state.activeTest;

  let ansCount = 0, notAnsCount = 0, notVisCount = 0, markedCount = 0, ansMarkedCount = 0;



  for (let i = 0; i < questions.length; i++) {

    const a = answers[i];

    const hasAns = a !== null && a !== undefined && (!Array.isArray(a) || a.length > 0);

    const isMarked = marked.has(i);

    const isVisited = visited ? visited.has(i) : true;

    const btn = document.getElementById(`pb-${i}`);



    let stateCls = 'not-visited';

    if (hasAns && isMarked) {

      stateCls = 'ans-marked';

      ansMarkedCount++;

    } else if (isMarked) {

      stateCls = 'marked';

      markedCount++;

    } else if (hasAns) {

      stateCls = 'answered';

      ansCount++;

    } else if (isVisited) {

      stateCls = 'not-answered';

      notAnsCount++;

    } else {

      stateCls = 'not-visited';

      notVisCount++;

    }



    if (btn) {

      btn.className = `palette-btn ${stateCls}${i === currentQ ? ' current' : ''}`;

    }

  }



  const cAns = document.getElementById('cnt-ans');

  const cNotAns = document.getElementById('cnt-notans');

  const cNotVis = document.getElementById('cnt-notvis');

  const cMarked = document.getElementById('cnt-marked');

  const cAnsMarked = document.getElementById('cnt-ansmarked');

  if (cAns) cAns.textContent = ansCount;

  if (cNotAns) cNotAns.textContent = notAnsCount;

  if (cNotVis) cNotVis.textContent = notVisCount;

  if (cMarked) cMarked.textContent = markedCount;

  if (cAnsMarked) cAnsMarked.textContent = ansMarkedCount;

}



// ── 3. GATE SYLLABUS MASTERY MATRIX & WEIGHTAGE HEATMAP ──

function buildMasteryMatrixHTML() {

  const map = new Map(state.attempts.map(a => [a.questionId, a]));



  function getPillarStats(predicate) {

    const qs = state.questions.filter(predicate);

    const attempted = qs.filter(q => map.has(q.id));

    const correct = attempted.filter(q => map.get(q.id)?.correct);

    const acc = attempted.length > 0 ? Math.round((correct.length / attempted.length) * 100) : 0;

    return { total: qs.length, attempted: attempted.length, correct: correct.length, acc };

  }



  const gaStats = getPillarStats(q => q.subject === 'Aptitude' || q.subject === 'General Aptitude');

  const emStats = getPillarStats(q => ['Engineering Mathematics', 'Discrete Mathematics'].includes(q.subject));

  const csStats = getPillarStats(q => q.subject !== 'Aptitude' && q.subject !== 'General Aptitude' && !['Engineering Mathematics', 'Discrete Mathematics'].includes(q.subject));



  // Compute Projected Marks

  const gaProj = ((gaStats.acc / 100) * 15).toFixed(1);

  const emProj = ((emStats.acc / 100) * 13).toFixed(1);

  const csProj = ((csStats.acc / 100) * 72).toFixed(1);

  const totalProj = (parseFloat(gaProj) + parseFloat(emProj) + parseFloat(csProj)).toFixed(1);



  function getBadge(acc, att) {

    if (att === 0) return `<span class="mastery-status-badge" style="background:rgba(255,255,255,0.08);color:var(--text-muted)">Unattempted</span>`;

    if (acc >= 75) return `<span class="mastery-status-badge mastery-strong">🟢 Strong Mastery</span>`;

    if (acc >= 50) return `<span class="mastery-status-badge mastery-mod">🟡 Moderate</span>`;

    return `<span class="mastery-status-badge mastery-risk">🔴 High-Risk Area</span>`;

  }



  return `

    <div class="mastery-matrix-card">

      <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;margin-bottom:12px">

        <div>

          <div style="font-size:16px;font-weight:800;color:#fff">🗺️ GATE Syllabus Mastery Matrix & Weightage Heatmap</div>

          <div class="text-sm text-muted">Accuracy mapped against standard 100-mark GATE CS distribution.</div>

        </div>

        <div style="background:rgba(108,99,255,0.15);padding:6px 14px;border-radius:20px;border:1px solid rgba(108,99,255,0.3);font-size:13px;font-weight:700;color:var(--accent)">

          Projected GATE Marks: <span style="font-size:16px;color:#fff">${totalProj}</span> / 100

        </div>

      </div>



      <div class="mastery-pillars-grid">

        <!-- Pillar 1: General Aptitude -->

        <div class="mastery-pillar-box">

          <div class="mastery-pillar-top">

            <span class="mastery-pillar-title">1. General Aptitude (GA)</span>

            <span class="mastery-pillar-weight">15 Marks Weight</span>

          </div>

          <div class="mastery-pillar-meter">

            <div class="mastery-pillar-fill" style="width:${gaStats.acc}%;background:#22c55e"></div>

          </div>

          <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:8px">

            <span class="text-muted">${gaStats.attempted}/${gaStats.total} Qs Attempted</span>

            <span style="font-weight:700;color:${gaStats.acc>=75?'#22c55e':gaStats.acc>=50?'#f59e0b':'#ef4444'}">${gaStats.acc}% Accuracy</span>

          </div>

          <div style="display:flex;justify-content:space-between;align-items:center">

            ${getBadge(gaStats.acc, gaStats.attempted)}

            <span style="font-size:11.5px;color:var(--text-secondary)">Proj: <strong>${gaProj}</strong>/15 M</span>

          </div>

        </div>



        <!-- Pillar 2: Engineering & Discrete Math -->

        <div class="mastery-pillar-box">

          <div class="mastery-pillar-top">

            <span class="mastery-pillar-title">2. Engg & Discrete Math</span>

            <span class="mastery-pillar-weight">13 Marks Weight</span>

          </div>

          <div class="mastery-pillar-meter">

            <div class="mastery-pillar-fill" style="width:${emStats.acc}%;background:#3b82f6"></div>

          </div>

          <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:8px">

            <span class="text-muted">${emStats.attempted}/${emStats.total} Qs Attempted</span>

            <span style="font-weight:700;color:${emStats.acc>=75?'#22c55e':emStats.acc>=50?'#f59e0b':'#ef4444'}">${emStats.acc}% Accuracy</span>

          </div>

          <div style="display:flex;justify-content:space-between;align-items:center">

            ${getBadge(emStats.acc, emStats.attempted)}

            <span style="font-size:11.5px;color:var(--text-secondary)">Proj: <strong>${emProj}</strong>/13 M</span>

          </div>

        </div>



        <!-- Pillar 3: Core Computer Science -->

        <div class="mastery-pillar-box">

          <div class="mastery-pillar-top">

            <span class="mastery-pillar-title">3. Core Computer Science</span>

            <span class="mastery-pillar-weight">72 Marks Weight</span>

          </div>

          <div class="mastery-pillar-meter">

            <div class="mastery-pillar-fill" style="width:${csStats.acc}%;background:var(--accent)"></div>

          </div>

          <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:8px">

            <span class="text-muted">${csStats.attempted}/${csStats.total} Qs Attempted</span>

            <span style="font-weight:700;color:${csStats.acc>=75?'#22c55e':csStats.acc>=50?'#f59e0b':'#ef4444'}">${csStats.acc}% Accuracy</span>

          </div>

          <div style="display:flex;justify-content:space-between;align-items:center">

            ${getBadge(csStats.acc, csStats.attempted)}

            <span style="font-size:11.5px;color:var(--text-secondary)">Proj: <strong>${csProj}</strong>/72 M</span>

          </div>

        </div>

      </div>

    </div>

  `;

}



// ── 4. CUSTOM MOCK EXAM & PRACTICE DRILL GENERATOR ──

function toggleCustomDrillModal(open) {

  let modal = document.getElementById('custom-drill-modal');

  if (!modal) {

    modal = document.createElement('div');

    modal.id = 'custom-drill-modal';

    modal.className = 'drill-modal-backdrop';

    document.body.appendChild(modal);

  }

  if (!open) {

    modal.style.display = 'none';

    return;

  }

  const allSubs = Array.from(new Set(state.questions.map(q => q.subject).filter(Boolean))).sort();

  modal.innerHTML = `

    <div class="drill-modal-card">

      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">

        <div style="font-size:17px;font-weight:800;color:#fff">🎛️ Custom Drill & Exam Generator</div>

        <button class="btn btn-secondary btn-sm" onclick="toggleCustomDrillModal(false)" type="button">✕</button>

      </div>

      <p class="text-sm text-muted" style="margin-bottom:14px">

        Craft your own personalized test session from our database of ${state.questions.length.toLocaleString()} authentic questions.

      </p>



      <div style="margin-bottom:14px">

        <div style="display:flex;justify-content:space-between;align-items:center">

          <label style="font-size:12px;font-weight:700;color:var(--text-secondary)">Select Target Subjects:</label>

          <button class="btn btn-secondary btn-sm" onclick="toggleSelectAllDrillSubjects()" style="padding:2px 8px;font-size:11px" type="button">Toggle All</button>

        </div>

        <div class="drill-subject-grid" id="drill-subject-grid">

          ${allSubs.map(s => `

            <div class="drill-subject-item selected" data-sub="${escapeHtml(s)}" onclick="this.classList.toggle('selected')">

              <span>📚</span><span>${escapeHtml(s)}</span>

            </div>

          `).join('')}

        </div>

      </div>



      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:14px">

        <div>

          <label style="font-size:12px;font-weight:700;color:var(--text-secondary);display:block;margin-bottom:4px">Question Type:</label>

          <select class="form-select form-select-sm" id="drill-type" style="width:100%;padding:6px;background:var(--bg-input);border:1px solid var(--border);border-radius:6px;color:#fff">

            <option value="all">All Types (MCQ, MSQ, NAT)</option>

            <option value="mcq">MCQs Only</option>

            <option value="msq">MSQs Only</option>

            <option value="nat">NATs Only</option>

          </select>

        </div>

        <div>

          <label style="font-size:12px;font-weight:700;color:var(--text-secondary);display:block;margin-bottom:4px">Difficulty Tier:</label>

          <select class="form-select form-select-sm" id="drill-diff" style="width:100%;padding:6px;background:var(--bg-input);border:1px solid var(--border);border-radius:6px;color:#fff">

            <option value="all">Mixed (Balanced GATE CS)</option>

            <option value="easy">Easy (Foundational)</option>

            <option value="medium">Medium (Standard GATE)</option>

            <option value="hard">Hard (Rank Booster)</option>

          </select>

        </div>

      </div>



      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:20px">

        <div>

          <label style="font-size:12px;font-weight:700;color:var(--text-secondary);display:block;margin-bottom:4px">Number of Questions:</label>

          <select class="form-select form-select-sm" id="drill-count" style="width:100%;padding:6px;background:var(--bg-input);border:1px solid var(--border);border-radius:6px;color:#fff">

            <option value="15">15 Questions (Quick Drill)</option>

            <option value="30">30 Questions (Half-Length)</option>

            <option value="65">65 Questions (Full-Length Exam)</option>

          </select>

        </div>

        <div>

          <label style="font-size:12px;font-weight:700;color:var(--text-secondary);display:block;margin-bottom:4px">Mode:</label>

          <select class="form-select form-select-sm" id="drill-mode" style="width:100%;padding:6px;background:var(--bg-input);border:1px solid var(--border);border-radius:6px;color:#fff">

            <option value="timed">Timed Exam Mode (Countdown)</option>

            <option value="practice">Practice Mode (Instant Solutions)</option>

          </select>

        </div>

      </div>



      <div style="display:flex;justify-content:flex-end;gap:10px">

        <button class="btn btn-secondary btn-sm" onclick="toggleCustomDrillModal(false)" type="button">Cancel</button>

        <button class="btn btn-primary btn-sm" onclick="launchCustomDrill()" style="font-weight:700" type="button">🚀 Launch Custom Session</button>

      </div>

    </div>

  `;

  modal.style.display = 'flex';

}



function toggleSelectAllDrillSubjects() {

  const items = document.querySelectorAll('.drill-subject-item');

  const allSel = Array.from(items).every(i => i.classList.contains('selected'));

  items.forEach(i => i.classList.toggle('selected', !allSel));

}



function launchCustomDrill() {

  const selectedSubs = Array.from(document.querySelectorAll('.drill-subject-item.selected')).map(i => i.dataset.sub);

  if (!selectedSubs.length) {

    showToast('Please select at least one subject!', 'error');

    return;

  }

  const type = document.getElementById('drill-type')?.value || 'all';

  const diff = document.getElementById('drill-diff')?.value || 'all';

  const count = parseInt(document.getElementById('drill-count')?.value || '15', 10);

  const mode = document.getElementById('drill-mode')?.value || 'timed';



  let pool = state.questions.filter(q => selectedSubs.includes(q.subject));

  if (type !== 'all') pool = pool.filter(q => q.type === type);

  if (diff !== 'all') pool = pool.filter(q => q.difficulty === diff);



  if (!pool.length) {

    showToast('No questions match this combination! Try relaxing the filters.', 'error');

    return;

  }



  const selectedQs = shuffleArr([...pool]).slice(0, count);

  toggleCustomDrillModal(false);



  if (mode === 'practice') {

    state.practiceQueue = selectedQs;

    state.currentQuestion = 0;

    state.practiceAnswered = false;

    state.activeMockPaper = null;

    state.activeTest = null;

    navigate('practice');

    showToast(`Started custom practice drill with ${selectedQs.length} questions!`, 'success');

  } else {

    const customMock = {

      id: `custom-mock-${Date.now()}`,

      name: `Custom Drill (${selectedQs.length} Qs)`,

      duration: Math.max(20, Math.round(selectedQs.length * 2.75)),

      marks: selectedQs.reduce((s, q) => s + (q.marks || 1), 0),

      difficulty: diff === 'all' ? 'medium' : diff,

      type: 'full'

    };

    state.activeTest = {

      mockId: customMock.id,

      mock: customMock,

      questions: selectedQs,

      answers: new Array(selectedQs.length).fill(null),

      marked: new Set(),

      visited: new Set([0]),

      currentQ: 0,

      timeLeft: customMock.duration * 60,

      submitted: false,

      timePerQ: new Array(selectedQs.length).fill(0),

      tabSwitches: 0

    };

    renderTestMode();

    showToast(`Started custom timed exam (${customMock.duration} min)!`, 'success');

  }

}



// ── 5. USER DATA PORTABILITY (EXPORT & RESTORE PROGRESS) ──

function buildDataPortabilityCardHTML() {

  return `

    <div class="data-portability-card">

      <div>

        <div style="font-size:15px;font-weight:800;color:#fff">💾 1-Click Data Backup & Device Portability</div>

        <div class="text-sm text-muted" style="margin-top:2px">

          Export your test sessions, accuracy history, bookmarks, and revision notes to backup or transfer across devices.

        </div>

      </div>

      <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap">

        <button class="btn btn-primary btn-sm" onclick="exportGateProfileBackup()" style="font-weight:700" type="button">

          📦 Export Full Profile (.gatebackup)

        </button>

        <button class="btn btn-secondary btn-sm" onclick="triggerRestoreProfileBackup()" style="font-weight:700;border-color:var(--accent);color:var(--accent)" type="button">

          📥 Restore (.gatebackup)

        </button>

        <button class="btn btn-secondary btn-sm" onclick="exportUserData()" style="font-weight:700" type="button">

          📥 Export Progress (JSON)

        </button>

        <button class="btn btn-secondary btn-sm" onclick="triggerRestoreFilePrompt()" style="font-weight:700;border-color:var(--accent);color:var(--accent)" type="button">

          📤 Restore From File

        </button>

      </div>

    </div>

  `;

}



function exportUserData() {

  try {

    const payload = {

      app: 'GATE CSE Platform',

      version: 'v5.5',

      exportDate: new Date().toISOString(),

      testSessions: state.testSessions || [],

      attempts: state.attempts || [],

      bookmarks: Array.from(state.bookmarks || []),

      questionNotes: state.questionNotes || {},

      flashcardStats: state.flashcardStats || {},

      errorTags: state.errorTags || {},

      playlists: state.playlists || {}

    };

    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });

    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');

    a.href = url;

    a.download = `gate_cse_progress_${new Date().toISOString().slice(0, 10)}.json`;

    a.click();

    URL.revokeObjectURL(url);

    showToast('Progress exported successfully! File downloaded.', 'success');

  } catch(e) {

    showToast('Export failed: ' + e.message, 'error');

  }

}



function triggerRestoreFilePrompt() {

  document.getElementById('restore-progress-file-input')?.click();

}



function handleRestoreProgressFile(event) {

  const file = event.target?.files?.[0];

  if (!file) return;

  const reader = new FileReader();

  reader.onload = (e) => {

    try {

      const data = JSON.parse(e.target.result);

      if (!data || !Array.isArray(data.attempts)) {

        showToast('Invalid backup file format.', 'error');

        return;

      }

      // Merge test sessions

      const existingSesIds = new Set((state.testSessions || []).map(s => s.id));

      (data.testSessions || []).forEach(s => {

        if (!existingSesIds.has(s.id)) state.testSessions.push(s);

      });



      // Merge attempts

      const attMap = new Map(state.attempts.map(a => [a.questionId, a]));

      (data.attempts || []).forEach(a => {

        if (!attMap.has(a.questionId) || a.date > attMap.get(a.questionId).date) {

          attMap.set(a.questionId, a);

        }

      });

      state.attempts = Array.from(attMap.values());



      // Merge bookmarks

      (data.bookmarks || []).forEach(b => state.bookmarks.add(b));

      if (data.errorTags) state.errorTags = { ...(state.errorTags || {}), ...data.errorTags };

      if (data.playlists) state.playlists = { ...(state.playlists || {}), ...data.playlists };



      // Merge notes

      state.questionNotes = Object.assign({}, state.questionNotes || {}, data.questionNotes || {});

      state.flashcardStats = Object.assign({}, state.flashcardStats || {}, data.flashcardStats || {});

      try { localStorage.setItem('gate_formula_flashcards_srs', JSON.stringify(state.flashcardStats)); } catch(e){}



      saveCache();

      showToast(`Restored ${data.attempts.length} attempts and ${data.testSessions?.length || 0} sessions!`, 'success');

      renderPage(state.currentPage || 'performance', state.currentParams || {});

    } catch(err) {

      showToast('Error parsing file: ' + err.message, 'error');

    }

  };

  reader.readAsText(file);

  event.target.value = '';

}



// ── 6. PERSONAL QUESTION REVISION NOTES (SCRATCHPAD) ──

function promptQuestionNote(qId) {

  if (!state.questionNotes) state.questionNotes = {};

  const current = state.questionNotes[qId] || '';

  const note = prompt('Enter your personal revision note or mnemonic for this question:', current);

  if (note === null) return; // User cancelled

  saveQuestionNote(qId, note);

  if (state.currentPage === 'mistakes') {

    renderMistakes(document.getElementById('page-content'));

  } else if (state.currentPage === 'practice') {

    renderPractice(document.getElementById('page-content'));

  }

}



function saveQuestionNote(qId, noteText) {

  if (!state.questionNotes) state.questionNotes = {};

  if (noteText && noteText.trim()) {

    state.questionNotes[qId] = noteText.trim();

    showToast('Personal revision note saved!', 'success');

  } else {

    delete state.questionNotes[qId];

    showToast('Personal revision note deleted.', 'info');

  }

  try {

    localStorage.setItem('gate_question_notes', JSON.stringify(state.questionNotes));

  } catch(e) {}

}



// ── 7. EXAM PACING WEB AUDIO COUNTDOWN CHIMES ──

let examAudioCtx = null;

let chimesEnabled = localStorage.getItem('gate_exam_chimes') !== 'false';



function getExamAudioCtx() {

  if (!examAudioCtx) {

    examAudioCtx = new (window.AudioContext || window.webkitAudioContext)();

  }

  return examAudioCtx;

}



function toggleExamChimes() {

  chimesEnabled = !chimesEnabled;

  try { localStorage.setItem('gate_exam_chimes', chimesEnabled ? 'true' : 'false'); } catch(e) {}

  const btn = document.getElementById('exam-chime-btn');

  if (btn) btn.innerHTML = `${chimesEnabled ? '🔔' : '🔕'} <span class="hide-xs">Chimes</span>`;

  showToast(chimesEnabled ? '🔔 Exam Countdown Chimes Enabled' : '🔕 Exam Countdown Chimes Muted', 'info');

}



function playChimeTone(freq, duration, delay = 0) {

  if (!chimesEnabled) return;

  try {

    const ctx = getExamAudioCtx();

    if (ctx.state === 'suspended') ctx.resume();

    const osc = ctx.createOscillator();

    const gain = ctx.createGain();

    osc.type = 'sine';

    osc.frequency.setValueAtTime(freq, ctx.currentTime + delay);

    gain.gain.setValueAtTime(0.12, ctx.currentTime + delay);

    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + delay + duration);

    osc.connect(gain);

    gain.connect(ctx.destination);

    osc.start(ctx.currentTime + delay);

    osc.stop(ctx.currentTime + delay + duration);

  } catch(e) {}

}



function triggerPacingChime(type) {

  if (type === '60min') {

    playChimeTone(520, 0.4);

  } else if (type === '30min') {

    playChimeTone(659, 0.3, 0);

    playChimeTone(520, 0.4, 0.35);

  } else if (type === '5min') {

    playChimeTone(880, 0.25, 0);

    playChimeTone(659, 0.25, 0.28);

    playChimeTone(880, 0.35, 0.56);

  }

}



async function bootApp(user) {
  initSoundFxState();
  currentUser = user;

  if (user) {
    state.isGuest = false;
    if (checkIsAdminUser(user)) {
      state.isAdmin = true;
    } else if (USE_FB && typeof db !== 'undefined') {
      try {
        const d = await getDoc(doc(db, 'admins', user.uid));
        state.isAdmin = d.exists();
      } catch(e) {
        state.isAdmin = false;
      }
    } else {
      state.isAdmin = false;
    }
  } else {
    state.isAdmin = false;
    state.isGuest = true;
    setSyncStatus(navigator.onLine ? 'online' : 'offline');
    const lMsg = document.getElementById('loading-msg');
    if (lMsg) lMsg.textContent = 'Preparing question bank…';
  }
  updateTopbarUser();

  // 1. Instantly load cached user attempts/sessions and IndexedDB questions
  await loadCache();

  // In guest mode, if questions are already present in memory/cache, release loading screen immediately
  if (!user && state.questions && state.questions.length > 500) {
    const ls = document.getElementById('loading-screen');
    if (ls) ls.style.display = 'none';
    const pc = document.getElementById('page-content');
    if (pc) pc.classList.remove('hidden');
  }

  // 2. Fetch master static questions from ./data/sample_questions.json (6,218+ questions,

  //    including all 30 easy mocks and PYQs) and merge with state.questions

  await loadMasterStaticQuestions();



  // 3. If Firebase is active and user is signed in, fetch cloud questions & user data from Firestore
  if (user && USE_FB) {
    const lMsg = document.getElementById('loading-msg');
    if (lMsg) lMsg.textContent = 'Syncing questions with cloud…';
    const ok = await loadFromFirestore();
    if (ok) {
      setupListeners();
    } else {
      setSyncStatus('offline');
      if (lMsg) lMsg.textContent = 'Using local question bank…';
    }
  } else {
    state.isGuest = !user;
    setSyncStatus(navigator.onLine ? 'online' : 'offline');
    if (USE_FB && !user) {
      // Non-blocking background fetch of public community questions for guest
      fsAll(qCol()).then(cloudQs => {
        if (cloudQs && cloudQs.length) {
          state.questions = mergeQuestionArrays(state.questions, cloudQs);
          saveCache();
        }
      }).catch(() => {});
    }
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

  setupCalcDraggable();

  initExamCountdownAndStreak();

  checkExamAutoSaveRecovery();

  applyThemeMode(state.themeMode || 'dark');

  updateSidebarSubjectProgress();

  navigate('dashboard');

}



function setupMobileMenu() {

  const menuBtn  = document.getElementById('menu-toggle-btn');

  const closeBtn = document.getElementById('sidebar-close-btn');

  const backdrop = document.getElementById('sidebar-backdrop');

  const sidebar  = document.getElementById('sidebar');



  function openSidebar() {

    sidebar?.classList.add('mobile-open');

    backdrop?.classList.add('active');

    document.body.style.overflow = 'hidden';

  }



  function closeSidebar() {

    sidebar?.classList.remove('mobile-open');

    backdrop?.classList.remove('active');

    document.body.style.overflow = '';

  }



  function toggleSidebar() {

    if (sidebar?.classList.contains('mobile-open')) {

      closeSidebar();

    } else {

      openSidebar();

    }

  }



  // Remove existing listeners by replacing onclick/events

  if (menuBtn)  menuBtn.onclick  = toggleSidebar;

  if (closeBtn) closeBtn.onclick = closeSidebar;

  if (backdrop) backdrop.onclick = closeSidebar;



  window.closeMobileSidebar  = closeSidebar;

  window.openMobileSidebar   = openSidebar;

  window.toggleMobileSidebar = toggleSidebar;

}



// ─── GATE VIRTUAL SCIENTIFIC CALCULATOR ENGINE (TCS iON Pattern) ─────────────

const calcState = {

  expr: '',

  display: '0',

  angle: 'deg', // 'deg' | 'rad'

  memory: 0,

  hasMemory: false,

  newNumber: true,

  isOpen: false

};



function toggleGateCalc(force) {

  const modal = document.getElementById('gate-calc-modal');

  const backdrop = document.getElementById('calc-modal-backdrop');

  if (!modal) return;

  const shouldOpen = typeof force === 'boolean' ? force : !calcState.isOpen;

  calcState.isOpen = shouldOpen;

  modal.classList.toggle('active', shouldOpen);

  backdrop?.classList.toggle('active', shouldOpen);

  if (shouldOpen) {

    updateCalcUI();

  }

}



function setCalcAngle(angle) {

  calcState.angle = angle;

  updateCalcUI();

}



function updateCalcUI() {

  const exprEl = document.getElementById('calc-expr');

  const dispEl = document.getElementById('calc-display');

  const memEl = document.getElementById('calc-mem-indicator');

  const degRadio = document.getElementById('calc-deg');

  const radRadio = document.getElementById('calc-rad');

  if (exprEl) exprEl.textContent = calcState.expr;

  if (dispEl) dispEl.textContent = calcState.display;

  if (memEl) memEl.textContent = calcState.hasMemory ? `M = ${calcState.memory}` : '';

  if (degRadio) degRadio.checked = calcState.angle === 'deg';

  if (radRadio) radRadio.checked = calcState.angle === 'rad';

}



function calcInput(ch) {
  playUiClickSound();

  if (ch === 'pi') {

    calcState.display = Math.PI.toString();

    calcState.newNumber = true;

    updateCalcUI();

    return;

  }

  if (ch === 'e') {

    calcState.display = Math.E.toString();

    calcState.newNumber = true;

    updateCalcUI();

    return;

  }

  if (['+', '-', '*', '/', '^', '%', '(', ')'].includes(ch)) {

    if (ch === '(' || ch === ')') {

      calcState.expr += (calcState.expr ? ' ' : '') + ch;

    } else {

      calcState.expr += (calcState.expr ? ' ' : '') + calcState.display + ' ' + (ch === '^' ? '^' : ch);

      calcState.newNumber = true;

    }

    updateCalcUI();

    return;

  }

  if (ch === '.') {

    if (calcState.newNumber) {

      calcState.display = '0.';

      calcState.newNumber = false;

    } else if (!calcState.display.includes('.')) {

      calcState.display += '.';

    }

    updateCalcUI();

    return;

  }

  // Digits 0-9

  if (calcState.newNumber || calcState.display === '0') {

    calcState.display = ch;

    calcState.newNumber = false;

  } else {

    calcState.display += ch;

  }

  updateCalcUI();

}



function calcClear() {

  calcState.expr = '';

  calcState.display = '0';

  calcState.newNumber = true;

  updateCalcUI();

}



function calcClearEntry() {

  calcState.display = '0';

  calcState.newNumber = true;

  updateCalcUI();

}



function calcBackspace() {

  if (calcState.newNumber) return;

  if (calcState.display.length > 1) {

    calcState.display = calcState.display.slice(0, -1);

  } else {

    calcState.display = '0';

    calcState.newNumber = true;

  }

  updateCalcUI();

}



function calcMem(op) {

  const val = parseFloat(calcState.display) || 0;

  switch (op) {

    case 'MC':

      calcState.memory = 0;

      calcState.hasMemory = false;

      break;

    case 'MR':

      if (calcState.hasMemory) {

        calcState.display = calcState.memory.toString();

        calcState.newNumber = true;

      }

      break;

    case 'MS':

      calcState.memory = val;

      calcState.hasMemory = true;

      break;

    case 'M+':

      calcState.memory += val;

      calcState.hasMemory = true;

      break;

    case 'M-':

      calcState.memory -= val;

      calcState.hasMemory = true;

      break;

  }

  updateCalcUI();

}



function calcFn(fn) {
  playUiClickSound();

  const val = parseFloat(calcState.display) || 0;

  const toRad = deg => (deg * Math.PI) / 180;

  const toDeg = rad => (rad * 180) / Math.PI;

  let res = 0;



  try {

    switch (fn) {

      case 'sin':

        res = Math.sin(calcState.angle === 'deg' ? toRad(val) : val);

        break;

      case 'cos':

        res = Math.cos(calcState.angle === 'deg' ? toRad(val) : val);

        break;

      case 'tan':

        res = Math.tan(calcState.angle === 'deg' ? toRad(val) : val);

        break;

      case 'asin':

        res = Math.asin(val);

        if (calcState.angle === 'deg') res = toDeg(res);

        break;

      case 'acos':

        res = Math.acos(val);

        if (calcState.angle === 'deg') res = toDeg(res);

        break;

      case 'atan':

        res = Math.atan(val);

        if (calcState.angle === 'deg') res = toDeg(res);

        break;

      case 'sinh':

        res = Math.sinh(val);

        break;

      case 'cosh':

        res = Math.cosh(val);

        break;

      case 'tanh':

        res = Math.tanh(val);

        break;

      case 'ln':

        if (val <= 0) throw new Error('Invalid Input');

        res = Math.log(val);

        break;

      case 'log10':

        if (val <= 0) throw new Error('Invalid Input');

        res = Math.log10(val);

        break;

      case 'log2':

        if (val <= 0) throw new Error('Invalid Input');

        res = Math.log2(val);

        break;

      case 'exp':

        res = Math.exp(val);

        break;

      case 'pow10':

        res = Math.pow(10, val);

        break;

      case 'sqrt':

        if (val < 0) throw new Error('Invalid Input');

        res = Math.sqrt(val);

        break;

      case 'cbrt':

        res = Math.cbrt(val);

        break;

      case 'sqr':

        res = Math.pow(val, 2);

        break;

      case 'inv':

        if (val === 0) throw new Error('Divide by zero');

        res = 1 / val;

        break;

      case 'fact':

        if (val < 0 || !Number.isInteger(val)) throw new Error('Invalid Input');

        res = 1;

        for (let i = 2; i <= Math.min(val, 170); i++) res *= i;

        break;

      case 'abs':

        res = Math.abs(val);

        break;

      case 'sign':

        res = -val;

        break;

      default:

        return;

    }

    if (Math.abs(res) < 1e-12) res = 0;

    calcState.display = Number(res.toFixed(10)).toString();

    calcState.newNumber = true;

  } catch(e) {

    calcState.display = 'Error';

    calcState.newNumber = true;

  }

  updateCalcUI();

}



function calcEval() {
  playUiClickSound();

  try {

    let fullExpr = (calcState.expr ? calcState.expr + ' ' : '') + calcState.display;

    if (!fullExpr.trim()) return;



    let safeStr = fullExpr

      .replace(/\^/g, '**')

      .replace(/×/g, '*')

      .replace(/÷/g, '/')

      .replace(/−/g, '-');



    if (!/^[0-9+\-*/().%\s*]+$/.test(safeStr)) {

      throw new Error('Invalid Expression');

    }



    const result = Function(`'use strict'; return (${safeStr})`)();

    if (!isFinite(result) || isNaN(result)) {

      calcState.display = 'Error';

    } else {

      let rounded = Number(result.toFixed(10));

      calcState.expr = fullExpr + ' =';

      calcState.display = rounded.toString();

    }

    calcState.newNumber = true;

  } catch(e) {

    calcState.display = 'Error';

    calcState.newNumber = true;

  }

  updateCalcUI();

}



// ─── KEYBOARD SHORTCUTS & MODAL ──────────────────────────────────────────────

let shortcutsModalOpen = false;



function toggleShortcutsModal(force) {

  const modal = document.getElementById('shortcuts-modal');

  const backdrop = document.getElementById('shortcuts-modal-backdrop');

  if (!modal) return;

  shortcutsModalOpen = typeof force === 'boolean' ? force : !shortcutsModalOpen;

  modal.classList.toggle('active', shortcutsModalOpen);

  backdrop?.classList.toggle('active', shortcutsModalOpen);

}



let shortcutsInitialized = false;



// ─── 8. FORMULA FLASHCARDS (SPACED REPETITION) ENGINE ─────────────────────────

const FORMULA_FLASHCARDS = [

  {

    id: 'card-masters-theorem',

    subject: 'Algorithms',

    topic: 'Asymptotic Analysis & Recurrences',

    title: "Master's Theorem Recurrence Bounds",

    question: "Given recurrence $T(n) = a T(n/b) + \\Theta(n^k \\log^p n)$ with $a \\ge 1, b > 1, k \\ge 0$. What are the exact 3 cases and boundary conditions?",

    hintText: "Compare $\\log_b a$ with $k$ (the polynomial exponent of $f(n)$). If $k = \\log_b a$, check the logarithmic power $p$.",

    formulaHTML: `

      <div style="margin-bottom:8px"><strong>Standard Form:</strong> $T(n) = a T(n/b) + \\Theta(n^k \\log^p n)$</div>

      <div style="background:rgba(0,0,0,0.25);padding:10px;border-radius:6px;font-size:13px;line-height:1.7;margin-bottom:8px">

        <div><strong>Case 1 ($k < \\log_b a$):</strong> $T(n) = \\Theta(n^{\\log_b a})$ (Leaf/Tree-heavy)</div>

        <div><strong>Case 2 ($k = \\log_b a$):</strong>

          <ul style="margin:4px 0 4px 18px;padding:0">

            <li>$p > -1 \\implies T(n) = \\Theta(n^{\\log_b a} \\log^{p+1} n)$</li>

            <li>$p = -1 \\implies T(n) = \\Theta(n^{\\log_b a} \\log \\log n)$</li>

            <li>$p < -1 \\implies T(n) = \\Theta(n^{\\log_b a})$</li>

          </ul>

        </div>

        <div><strong>Case 3 ($k > \\log_b a$):</strong> (Root-heavy, with regularity $a f(n/b) \\le c f(n)$ for $c < 1$):

          <ul style="margin:4px 0 4px 18px;padding:0">

            <li>$p \\ge 0 \\implies T(n) = \\Theta(n^k \\log^p n)$</li>

            <li>$p < 0 \\implies T(n) = \\Theta(n^k)$</li>

          </ul>

        </div>

      </div>

      <div style="font-size:12px;color:#f87171">⚠️ <strong>GATE Trap:</strong> Does NOT apply if $f(n)$ is non-polynomial or the ratio is non-polynomial (e.g. $T(n) = 2T(n/2) + n/\\log n$, use recursion tree $\\Theta(n \\log \\log n)$).</div>

    `,

    keywords: ['master', 'recurrence', 'divide and conquer', 'algorithm', 'asymptotic', 'complexity', 'o(n', 'theta(']

  },

  {

    id: 'card-graph-invariants',

    subject: 'Discrete Mathematics',

    topic: 'Graph Theory & Planarity',

    title: 'Graph Invariants & Planar Graph Formulas',

    question: "What are the core invariants for Planar Graphs, Handshaking Lemma, and Spanning Tree counts in $K_n$ and $K_{m,n}$?",

    hintText: "Use Euler's formula $V - E + R = 2$. For planar graphs with region degree $\\ge 3$, remember $3R \\le 2E \\implies E \\le 3V - 6$.",

    formulaHTML: `

      <div style="background:rgba(0,0,0,0.25);padding:10px;border-radius:6px;font-size:13px;line-height:1.7;margin-bottom:8px">

        <div><strong>1. Handshaking Lemma:</strong> $\\sum_{v \\in V} \\deg(v) = 2|E|$. Total odd degree vertices is always <em>even</em>.</div>

        <div><strong>2. Euler's Planar Formula:</strong> For connected planar graph: $V - E + R = 2$. (For $k$ components: $V - E + R = 1 + k$).</div>

        <div><strong>3. Edge Bounds in Planar Graphs:</strong>

          <ul style="margin:4px 0 4px 18px;padding:0">

            <li>Standard (region degree $\\ge 3$): $E \\le 3V - 6$ (and min degree $\\delta(G) \\le 5$)</li>

            <li>Triangle-Free / Bipartite (region degree $\\ge 4$): $E \\le 2V - 4$</li>

          </ul>

        </div>

        <div><strong>4. Spanning Trees (Cayley's Formula):</strong>

          <ul style="margin:4px 0 4px 18px;padding:0">

            <li>Complete Graph $K_n$: $n^{n-2}$ spanning trees.</li>

            <li>Complete Bipartite $K_{m,n}$: $m^{n-1} \\cdot n^{m-1}$ spanning trees.</li>

          </ul>

        </div>

        <div><strong>5. Eulerian Conditions:</strong> Circuit $\\iff$ connected and <em>all</em> vertices have even degree. Path $\\iff$ connected and exactly 0 or 2 vertices have odd degree.</div>

      </div>

      <div style="font-size:12px;color:#f87171">⚠️ <strong>GATE Trap:</strong> Kuratowski's Theorem: A graph is planar $\\iff$ it does NOT contain a subgraph homeomorphic to $K_5$ or $K_{3,3}$.</div>

    `,

    keywords: ['graph', 'planar', 'euler', 'spanning tree', 'degree', 'vertex', 'edge', 'bipartite', 'handshaking', 'chromatic']

  },

  {

    id: 'card-cpu-scheduling',

    subject: 'Operating Systems',

    topic: 'CPU Scheduling & Metrics',

    title: 'CPU Scheduling Metrics & Waiting Time Bounds',

    question: "What are the exact formulas for Turnaround Time, Waiting Time, Response Time, and Round Robin max waiting time bounds?",

    hintText: "Turnaround Time is total lifecycle: Completion - Arrival. Waiting Time is idle time: Turnaround - Burst.",

    formulaHTML: `

      <div style="background:rgba(0,0,0,0.25);padding:10px;border-radius:6px;font-size:13px;line-height:1.7;margin-bottom:8px">

        <div><strong>1. Turnaround Time ($TAT$):</strong> $TAT = \\text{Completion Time (CT)} - \\text{Arrival Time (AT)}$</div>

        <div><strong>2. Waiting Time ($WT$):</strong> $WT = TAT - \\text{Burst Time (BT)}$</div>

        <div><strong>3. Response Time ($RT$):</strong> $RT = \\text{Time of First CPU Allotment} - AT$</div>

        <div><strong>4. Round Robin Bound:</strong> For $n$ active processes with time quantum $q$:

          <ul style="margin:4px 0 4px 18px;padding:0">

            <li>Maximum wait time between turns for a process: $(n - 1) \\cdot q$</li>

            <li>If context switch overhead is $s$, effective quantum is $q + s$, CPU efficiency = $\\frac{q}{q + s}$</li>

          </ul>

        </div>

        <div><strong>5. Convoy Effect:</strong> Under FCFS, short processes get delayed behind a long CPU-burst process $\\implies$ high average waiting time.</div>

        <div><strong>6. Optimality:</strong> SJF (non-preemptive) & SRTF (preemptive) guarantee the theoretical <em>minimum average waiting time</em>.</div>

      </div>

      <div style="font-size:12px;color:#f87171">⚠️ <strong>GATE Trap:</strong> In Round Robin, if a process arrives at time $t$ while an executing process's quantum expires at time $t$, by convention the newly arrived process is added to the ready queue <em>before</em> the preempted process!</div>

    `,

    keywords: ['cpu', 'scheduling', 'turnaround', 'waiting time', 'burst', 'round robin', 'fcfs', 'sjf', 'srtf', 'gantt']

  },

  {

    id: 'card-subnetting-rules',

    subject: 'Computer Networks',

    topic: 'IPv4 Addressing & CIDR Subnetting',

    title: 'IPv4 CIDR Subnetting & Mask Calculations',

    question: "For an IPv4 CIDR prefix $/n$, what are the exact rules for total addresses, usable hosts, network ID, and broadcast address?",

    hintText: "With $n$ network bits, there are $32 - n$ host bits. Total IPs = $2^{32-n}$, subtract 2 for network & broadcast IDs.",

    formulaHTML: `

      <div style="background:rgba(0,0,0,0.25);padding:10px;border-radius:6px;font-size:13px;line-height:1.7;margin-bottom:8px">

        <div><strong>1. Total Addresses:</strong> $2^{32 - n}$ addresses</div>

        <div><strong>2. Usable Host Addresses:</strong> $2^{32 - n} - 2$

          <div style="font-size:12px;color:var(--text-muted);margin-left:14px">• Excluded: All-0s host ID (Network Address), All-1s host ID (Directed Broadcast)</div>

          <div style="font-size:12px;color:var(--text-muted);margin-left:14px">• Exceptions: $/31$ (2 usable, RFC 3021 point-to-point) and $/32$ (single loopback host)</div>

        </div>

        <div><strong>3. Network Address:</strong> $\\text{IP Address} \\text{ BITWISE-AND } \\text{Subnet Mask}$</div>

        <div><strong>4. Directed Broadcast Address:</strong> $\\text{Network Address} \\text{ BITWISE-OR } (\\sim\\text{Subnet Mask})$</div>

        <div><strong>5. Subnetting from $/n$:</strong> Borrowing $k$ host bits creates $2^k$ subnets, each with $/ (n + k)$ mask and $2^{32 - n - k} - 2$ usable hosts.</div>

        <div><strong>6. Quick CIDR Host Table:</strong>

          <span style="font-family:monospace;font-size:12px">/24 $\\to$ 254 | /25 $\\to$ 126 | /26 $\\to$ 62 | /27 $\\to$ 30 | /28 $\\to$ 14 | /29 $\\to$ 6 | /30 $\\to$ 2</span>

        </div>

      </div>

      <div style="font-size:12px;color:#f87171">⚠️ <strong>GATE Trap:</strong> Limited Broadcast address is $255.255.255.255$ (never routed across routers). Directed broadcast is specific to the subnet (host bits all 1).</div>

    `,

    keywords: ['subnet', 'cidr', 'ipv4', 'mask', 'broadcast', 'host', 'network address', 'ip address', 'classful', 'routing']

  },

  {

    id: 'card-emat-vm',

    subject: 'Operating Systems',

    topic: 'Virtual Memory & Paging',

    title: 'Effective Memory Access Time (EMAT)',

    question: "What is the formula for EMAT with a TLB and $k$-level page tables, and how is it modified when accounting for page fault rate $p$?",

    hintText: "On a TLB hit, time is $t_{TLB} + t_{mem}$. On a TLB miss with $k$ levels, you access memory $k$ times for page tables + 1 time for actual data.",

    formulaHTML: `

      <div style="background:rgba(0,0,0,0.25);padding:10px;border-radius:6px;font-size:13px;line-height:1.7;margin-bottom:8px">

        <div><strong>1. Basic TLB Paging EMAT ($h$ = hit ratio):</strong>

          $$\\text{EMAT} = h \\cdot (t_{\\text{TLB}} + t_{\\text{mem}}) + (1 - h) \\cdot (t_{\\text{TLB}} + (k + 1) \\cdot t_{\\text{mem}})$$

          <div style="font-size:12px;color:var(--text-muted);margin-left:14px">($k = 1$ for single-level paging $\\implies t_{\\text{TLB}} + 2 \\cdot t_{\\text{mem}}$ on miss)</div>

        </div>

        <div><strong>2. EMAT with Page Faults ($p$ = page fault probability):</strong>

          $$\\text{EMAT} = (1 - p) \\cdot \\text{EMAT}_{\\text{no-fault}} + p \\cdot \\text{Page Fault Service Time (PFST)}$$

        </div>

        <div><strong>3. Page Table Size:</strong>

          $$\\text{Page Table Size} = \\text{Number of Entries} \\times \\text{Page Table Entry (PTE) Size}$$

          $$\\text{Number of Entries} = \\frac{\\text{Virtual Address Space (VAS)}}{\\text{Page Size}}$$

        </div>

      </div>

      <div style="font-size:12px;color:#f87171">⚠️ <strong>GATE Trap:</strong> Check whether TLB search is performed concurrently with cache or sequentially before memory lookup. In inverted page tables, entry count equals the number of physical frames, not virtual pages!</div>

    `,

    keywords: ['emat', 'tlb', 'paging', 'virtual memory', 'page fault', 'pte', 'frame', 'page table']

  },

  {

    id: 'card-amat-cache',

    subject: 'Computer Organization & Architecture',

    topic: 'Memory Hierarchy & Cache Mapping',

    title: 'Average Memory Access Time (AMAT) & Cache Address Splits',

    question: "What is AMAT and how are Tag, Set-Index, and Word-Offset bit widths calculated for Direct and $k$-way associative caches?",

    hintText: "AMAT = Hit Time + Miss Rate $\\times$ Miss Penalty. For address bits, start from Block Offset = $\\log_2(\\text{Block Size})$.",

    formulaHTML: `

      <div style="background:rgba(0,0,0,0.25);padding:10px;border-radius:6px;font-size:13px;line-height:1.7;margin-bottom:8px">

        <div><strong>1. AMAT Formula:</strong>

          $$\\text{AMAT} = t_{\\text{hit}} + \\text{Miss Rate} \\times \\text{Miss Penalty}$$

          <div style="font-size:12px;color:var(--text-muted);margin-left:14px">With 2 levels (L1, L2): $\\text{AMAT} = t_{L1} + m_{L1} \\times (t_{L2} + m_{L2} \\times t_{\\text{main}})$</div>

        </div>

        <div><strong>2. Address Bit Fields (Total $n$ bits for byte-addressable):</strong>

          <ul style="margin:4px 0 4px 18px;padding:0">

            <li>$\\text{Block/Byte Offset (BO)} = \\log_2(\\text{Block Size in bytes})$</li>

            <li>$\\text{Set Index Bits (SI)} = \\log_2(\\text{Number of Sets})$</li>

            <li>$\\text{Tag Bits} = n - \\text{Set Index} - \\text{Block Offset}$</li>

          </ul>

        </div>

        <div><strong>3. Set Calculations by Mapping:</strong>

          <ul style="margin:4px 0 4px 18px;padding:0">

            <li>Direct Mapped: $\\text{Sets} = \\text{Total Lines} \\implies \\text{SI} = \\log_2(\\text{Lines})$</li>

            <li>$k$-way Associative: $\\text{Sets} = \\frac{\\text{Total Lines}}{k} \\implies \\text{SI} = \\log_2(\\text{Sets})$</li>

            <li>Fully Associative: $\\text{Sets} = 1 \\implies \\text{SI} = 0$, all remaining bits are Tag!</li>

          </ul>

        </div>

      </div>

      <div style="font-size:12px;color:#f87171">⚠️ <strong>GATE Trap:</strong> Total cache memory size includes Tag directory overhead: $\\text{Tag Directory} = \\text{Lines} \\times (\\text{Tag bits} + \\text{Valid bit} + \\text{Dirty bit})$.</div>

    `,

    keywords: ['cache', 'amat', 'tag', 'set index', 'block offset', 'associative', 'hit rate', 'miss rate', 'memory hierarchy']

  },

  {

    id: 'card-pipeline-speedup',

    subject: 'Computer Organization & Architecture',

    topic: 'Instruction Pipelining',

    title: 'Pipeline Speedup, Stalls & CPI Formulas',

    question: "What is the speedup of a $k$-stage pipeline for $n$ instructions with stall cycles, and what is its asymptotic limit?",

    hintText: "Unpipelined time is $n \\cdot k \\cdot \\tau$. Pipelined time is $(k + n - 1 + \\text{Stalls}) \\cdot \\tau$. Take ratio as $n \\to \\infty$.",

    formulaHTML: `

      <div style="background:rgba(0,0,0,0.25);padding:10px;border-radius:6px;font-size:13px;line-height:1.7;margin-bottom:8px">

        <div><strong>1. Execution Times (clock cycle $\\tau$):</strong>

          $$\\text{Non-pipelined: } T_n = n \\cdot k \\cdot \\tau$$

          $$\\text{Pipelined: } T_p = (k + n - 1 + \\text{Stalls}) \\cdot \\tau$$

        </div>

        <div><strong>2. Speedup ($S$):</strong>

          $$S = \\frac{T_n}{T_p} = \\frac{n \\cdot k}{k + n - 1 + \\text{Stalls}} \\xrightarrow{n \\to \\infty} \\frac{k}{1 + \\text{Stalls per instruction}}$$

        </div>

        <div><strong>3. Pipeline CPI & Throughput:</strong>

          $$\\text{CPI} = 1 + \\frac{\\text{Total Stall Cycles}}{n}$$

          $$\\text{Throughput} = \\frac{n}{(k + n - 1 + \\text{Stalls}) \\cdot \\tau} \\xrightarrow{n \\to \\infty} \\frac{1}{\\text{CPI} \\cdot \\tau}$$

        </div>

      </div>

      <div style="font-size:12px;color:#f87171">⚠️ <strong>GATE Trap:</strong> Stage cycle time $\\tau$ is determined by the slowest stage plus buffer delay: $\\tau = \\max(\\text{stage delays}) + \\text{register delay}$.</div>

    `,

    keywords: ['pipeline', 'speedup', 'cpi', 'stall', 'hazard', 'clock cycle', 'throughput', 'instruction']

  },

  {

    id: 'card-dbms-normal-forms',

    subject: 'Databases (DBMS)',

    topic: 'Normalization & Functional Dependencies',

    title: 'DBMS Normal Forms Hierarchy & Lossless Join',

    question: "What are the exact tests for 1NF, 2NF, 3NF, BCNF, and the mathematical test for Lossless Decomposition?",

    hintText: "For 3NF: $X \\to Y \\implies X$ is Superkey OR $Y$ is Prime. For BCNF: $X$ MUST be a Superkey. For lossless join: $R_1 \\cap R_2$ must be superkey of $R_1$ or $R_2$.",

    formulaHTML: `

      <div style="background:rgba(0,0,0,0.25);padding:10px;border-radius:6px;font-size:13px;line-height:1.7;margin-bottom:8px">

        <div><strong>1. Normal Form Requirements for non-trivial $X \\to Y$:</strong>

          <ul style="margin:4px 0 4px 18px;padding:0">

            <li><strong>1NF:</strong> All attribute values are atomic (no composite/multivalued attributes).</li>

            <li><strong>2NF:</strong> 1NF + No partial dependency (no proper subset of any candidate key determines a non-prime attribute).</li>

            <li><strong>3NF:</strong> 2NF + For every $X \\to Y$, either $X$ is a superkey OR $Y$ is a prime attribute.</li>

            <li><strong>BCNF:</strong> For every $X \\to Y$, $X$ <em>must</em> be a superkey.</li>

          </ul>

        </div>

        <div><strong>2. Lossless-Join Decomposition Test:</strong>

          $$R_1 \\bowtie R_2 = R \\iff (R_1 \\cap R_2 \\to R_1) \\in F^+ \\quad\\lor\\quad (R_1 \\cap R_2 \\to R_2) \\in F^+$$

          <div style="font-size:12px;color:var(--text-muted);margin-left:14px">(The common attribute must be a candidate key of at least one relation)</div>

        </div>

        <div><strong>3. Preservation Guarantee:</strong> 3NF always guarantees both <em>Lossless Join</em> and <em>Dependency Preservation</em>. BCNF guarantees Lossless Join, but dependency preservation is <strong>not</strong> always possible.</div>

      </div>

      <div style="font-size:12px;color:#f87171">⚠️ <strong>GATE Trap:</strong> Every binary relation with functional dependencies is always in BCNF and lossless! Prime attributes can be part of ANY candidate key.</div>

    `,

    keywords: ['normal form', '2nf', '3nf', 'bcnf', 'functional dependency', 'lossless', 'dependency preservation', 'superkey', 'candidate key']

  },

  {

    id: 'card-toc-closure',

    subject: 'Theory of Computation',

    topic: 'Chomsky Hierarchy & Closure Properties',

    title: 'Chomsky Hierarchy & Language Closure Properties',

    question: "Which language families in the Chomsky hierarchy are closed under Union, Intersection, Complement, and Concatenation?",

    hintText: "Regular is closed under EVERYTHING. CFL is NOT closed under Intersection or Complement (intersection of 2 CFLs can be non-CFL).",

    formulaHTML: `

      <div style="background:rgba(0,0,0,0.25);padding:10px;border-radius:6px;font-size:13px;line-height:1.7;margin-bottom:8px">

        <div><strong>1. Chomsky Hierarchy Containment:</strong>

          $$\\text{Regular (Type 3)} \\subset \\text{DCFL} \\subset \\text{CFL (Type 2)} \\subset \\text{CSL (Type 1)} \\subset \\text{Recursive} \\subset \\text{RE (Type 0)}$$

        </div>

        <div><strong>2. Major Closure Properties Matrix:</strong>

          <table style="width:100%;font-size:12px;border-collapse:collapse;margin-top:6px;text-align:center">

            <tr style="border-bottom:1px solid var(--border);color:var(--accent)">

              <th style="text-align:left">Language Class</th><th>Union</th><th>Intersection</th><th>Complement</th><th>Kleene *</th>

            </tr>

            <tr style="border-bottom:1px solid rgba(255,255,255,0.05)">

              <td style="text-align:left;font-weight:600">Regular</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td>

            </tr>

            <tr style="border-bottom:1px solid rgba(255,255,255,0.05)">

              <td style="text-align:left;font-weight:600">DCFL</td><td>❌</td><td>❌</td><td>✅</td><td>❌</td>

            </tr>

            <tr style="border-bottom:1px solid rgba(255,255,255,0.05)">

              <td style="text-align:left;font-weight:600">CFL</td><td>✅</td><td>❌</td><td>❌</td><td>✅</td>

            </tr>

            <tr style="border-bottom:1px solid rgba(255,255,255,0.05)">

              <td style="text-align:left;font-weight:600">Recursive</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td>

            </tr>

            <tr>

              <td style="text-align:left;font-weight:600">RE</td><td>✅</td><td>✅</td><td>❌</td><td>✅</td>

            </tr>

          </table>

        </div>

      </div>

      <div style="font-size:12px;color:#f87171">⚠️ <strong>GATE Trap:</strong> Intersection of a CFL with a Regular language is <em>always a CFL</em> ($L_{\\text{CFL}} \\cap L_{\\text{REG}} = \\text{CFL}$).</div>

    `,

    keywords: ['chomsky', 'closure', 'regular', 'cfl', 'dcfl', 'context-free', 'decidable', 'recursive', 'turing', 'pumping lemma']

  }

];



function getMatchingFlashcard(q) {

  if (!q) return FORMULA_FLASHCARDS[0];

  const qText = ((q.question || '') + ' ' + (q.topic || '') + ' ' + (q.subject || '')).toLowerCase();

  for (const card of FORMULA_FLASHCARDS) {

    if (card.keywords && card.keywords.some(k => qText.includes(k.toLowerCase()))) {

      return card;

    }

  }

  const subMatch = FORMULA_FLASHCARDS.find(c => c.subject.toLowerCase() === (q.subject || '').toLowerCase());

  if (subMatch) return subMatch;

  return FORMULA_FLASHCARDS[0];

}



function getMatchingFlashcardId(q) {

  return getMatchingFlashcard(q).id;

}



function buildQuestionHintHTML(q) {

  const card = getMatchingFlashcard(q);

  return `

    <div class="practice-hint-header">

      <div class="practice-hint-title">💡 <span>Concept Hint & Relevant Formula</span></div>

      <button class="palette-close-btn" onclick="togglePracticeHint(false)" type="button" style="font-size:12px">✕</button>

    </div>

    <div class="practice-hint-body">

      <div style="margin-bottom:6px;font-size:12.5px;color:var(--text-muted)">

        <span class="chip" style="font-size:11px">${card.subject}</span>

        <strong>${card.title}</strong>

      </div>

      <div style="margin-bottom:8px">${card.hintText}</div>

      <div style="background:var(--bg-card);border:1px solid rgba(108,99,255,0.25);border-radius:6px;padding:8px 12px;font-size:12.5px">

        ${card.formulaHTML}

      </div>

    </div>

    <div class="practice-hint-actions">

      <button class="btn btn-primary btn-sm" onclick="openFormulaFlashcardsModal('${card.id}')" type="button">📇 Open Spaced Repetition Flashcard</button>

      <button class="btn btn-secondary btn-sm" onclick="togglePracticeHint(false)" type="button">Got it 👍</button>

    </div>

  `;

}



function togglePracticeHint(forceState) {

  const box = document.getElementById('practice-hint-box');

  if (!box) return;

  const isHidden = box.style.display === 'none' || !box.style.display;

  const show = forceState !== undefined ? forceState : isHidden;

  box.style.display = show ? 'block' : 'none';

  if (show) {

    renderMath(box);

  }

}



let flashcardModalOpen = false;

let activeDeck = [...FORMULA_FLASHCARDS];

let currentCardIndex = 0;

let isCardFlipped = false;



function toggleFormulaFlashcards(isOpen, targetCardId) {

  flashcardModalOpen = isOpen !== undefined ? isOpen : !flashcardModalOpen;

  const modal = document.getElementById('flashcard-modal-backdrop');

  if (!modal) return;

  modal.classList.toggle('active', flashcardModalOpen);



  if (flashcardModalOpen) {

    filterFlashcardDeck();

    if (targetCardId) {

      const idx = activeDeck.findIndex(c => c.id === targetCardId);

      if (idx !== -1) currentCardIndex = idx;

    }

    isCardFlipped = false;

    renderActiveFlashcard();

  }

}



function openFormulaFlashcardsModal(targetCardId) {

  toggleFormulaFlashcards(true, targetCardId);

}



function renderActiveFlashcard() {

  if (!activeDeck.length) {

    activeDeck = [...FORMULA_FLASHCARDS];

    currentCardIndex = 0;

  }

  if (currentCardIndex >= activeDeck.length) currentCardIndex = 0;

  if (currentCardIndex < 0) currentCardIndex = activeDeck.length - 1;



  const card = activeDeck[currentCardIndex];

  const srs = state.flashcardStats?.[card.id] || { status: 'due', reps: 0 };

  const srsLabel = srs.status === 'mastered' ? '🟢 Mastered' : srs.status === 'learning' ? '🟡 In Progress' : '🔴 Due for Review';



  // Front Face

  const frontEl = document.getElementById('fc-face-front');

  if (frontEl) {

    frontEl.innerHTML = `

      <div>

        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px">

          <span class="flashcard-subject-chip">${card.subject}</span>

          <span class="flashcard-srs-status-tag ${srs.status}">${srsLabel}</span>

        </div>

        <div class="flashcard-concept-title">${card.title}</div>

        <div class="flashcard-prompt-text">${card.question}</div>

      </div>

      <div class="flashcard-flip-prompt">

        <span>🔄 Click card or press <strong>Space</strong> to reveal formula</span>

        <span style="font-size:11px;color:var(--text-muted)">Repetitions: ${srs.reps || 0}</span>

      </div>

    `;

  }



  // Back Face

  const backEl = document.getElementById('fc-face-back');

  if (backEl) {

    backEl.innerHTML = `

      <div>

        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px">

          <span class="flashcard-subject-chip" style="background:rgba(34,197,94,0.15);color:#22c55e">${card.subject} • Solution</span>

          <span class="flashcard-srs-status-tag ${srs.status}">${srsLabel}</span>

        </div>

        <div class="flashcard-concept-title" style="color:#22c55e">${card.title}</div>

        <div class="flashcard-formula-content">${card.formulaHTML}</div>

      </div>

      <div class="flashcard-srs-controls">

        <span style="font-size:12px;font-weight:600;color:var(--text-muted)">Rate recall:</span>

        <div class="flashcard-srs-buttons">

          <button class="srs-btn srs-btn-again" onclick="rateFlashcard('again')" title="Review soon (Key 1)">🔴 Hard (1)</button>

          <button class="srs-btn srs-btn-good" onclick="rateFlashcard('good')" title="Good recall (Key 2)">🟡 Good (2)</button>

          <button class="srs-btn srs-btn-mastered" onclick="rateFlashcard('mastered')" title="Mastered (Key 3)">🟢 Mastered (3)</button>

        </div>

      </div>

    `;

  }



  // Counter

  const badge = document.getElementById('fc-counter-badge');

  if (badge) {

    badge.textContent = `Card ${currentCardIndex + 1} of ${activeDeck.length}`;

  }



  // Ensure card flip state is synced

  const inner = document.getElementById('active-flashcard-inner');

  if (inner) inner.classList.toggle('is-flipped', isCardFlipped);



  // Render KaTeX in the modal

  const modal = document.getElementById('flashcard-modal-card');

  if (modal) renderMath(modal);

}



function flipActiveFlashcard() {

  isCardFlipped = !isCardFlipped;

  const inner = document.getElementById('active-flashcard-inner');

  if (inner) inner.classList.toggle('is-flipped', isCardFlipped);

}



function navFlashcard(delta) {

  isCardFlipped = false;

  const inner = document.getElementById('active-flashcard-inner');

  if (inner) inner.classList.remove('is-flipped');

  currentCardIndex += delta;

  renderActiveFlashcard();

}



function shuffleFlashcardDeck() {

  for (let i = activeDeck.length - 1; i > 0; i--) {

    const j = Math.floor(Math.random() * (i + 1));

    [activeDeck[i], activeDeck[j]] = [activeDeck[j], activeDeck[i]];

  }

  currentCardIndex = 0;

  isCardFlipped = false;

  renderActiveFlashcard();

  showToast('Flashcard deck shuffled! 🔀', 'info');

}



function rateFlashcard(rating) {

  if (!activeDeck[currentCardIndex]) return;

  const card = activeDeck[currentCardIndex];

  if (!state.flashcardStats) state.flashcardStats = {};

  const current = state.flashcardStats[card.id] || { reps: 0 };



  if (rating === 'again') {

    state.flashcardStats[card.id] = { status: 'learning', reps: 0, lastReviewed: Date.now() };

    showToast('Marked for review soon! ⏳', 'warning');

  } else if (rating === 'good') {

    state.flashcardStats[card.id] = { status: 'learning', reps: (current.reps || 0) + 1, lastReviewed: Date.now() };

    showToast('Good job! Progress saved. 👍', 'info');

  } else if (rating === 'mastered') {

    state.flashcardStats[card.id] = { status: 'mastered', reps: (current.reps || 0) + 2, lastReviewed: Date.now() };

    showToast('Mastered formula! 🟢', 'success');

  }



  try {

    localStorage.setItem('gate_formula_flashcards_srs', JSON.stringify(state.flashcardStats));

  } catch(e) {}



  setTimeout(() => {

    navFlashcard(1);

  }, 250);

}



function filterFlashcardDeck() {

  const subFilter = document.getElementById('fc-subject-filter')?.value || 'all';

  const srsFilter = document.getElementById('fc-srs-filter')?.value || 'all';



  let list = [...FORMULA_FLASHCARDS];

  if (subFilter !== 'all') {

    list = list.filter(c => c.subject === subFilter);

  }

  if (srsFilter !== 'all') {

    list = list.filter(c => {

      const s = state.flashcardStats?.[c.id]?.status || 'due';

      return s === srsFilter;

    });

  }



  activeDeck = list.length ? list : [...FORMULA_FLASHCARDS];

  currentCardIndex = 0;

  isCardFlipped = false;

  renderActiveFlashcard();

}





function setupKeyboardShortcuts() {

  if (shortcutsInitialized) return;

  shortcutsInitialized = true;



  document.addEventListener('keydown', e => {

    const activeTag = document.activeElement?.tagName;

    if (activeTag === 'INPUT' || activeTag === 'TEXTAREA' || document.activeElement?.isContentEditable) {

      if (e.key === 'Escape') {

        document.activeElement.blur();

      }

      return;

    }



    if (e.key === 'Escape') {

      if (document.getElementById('global-search-modal')?.classList.contains('active')) { closeGlobalSearch(); return; }

      if (flashcardModalOpen) { toggleFormulaFlashcards(false); return; }

      if (calcState.isOpen) { toggleGateCalc(false); return; }

      if (shortcutsModalOpen) { toggleShortcutsModal(false); return; }
      if (document.getElementById('diagram-lightbox-card')?.classList.contains('active')) { closeDiagramLightbox(); return; }
      if (document.getElementById('exam-qp-modal')?.classList.contains('active')) { closeExamQuestionPaper(); return; }
      if (document.getElementById('exam-instructions-modal')?.classList.contains('active')) { closeExamInstructions(); return; }
      if (document.getElementById('custom-test-modal')?.classList.contains('active')) { toggleCustomTestModal(false); return; }

      const palette = document.getElementById('test-sidebar');

      if (palette?.classList.contains('mobile-palette-open')) {

        toggleTestPalette();

        return;

      }

      return;

    }



    if (state.activeTest) {

      if (e.key === 'u' || e.key === 'U') {

        e.preventDefault();

        jumpToNextUnanswered();

        return;

      }

      if (e.key === 'm' || e.key === 'M') {

        e.preventDefault();

        jumpToNextMarked();

        return;

      }

    }



    if (e.key === '/') {

      e.preventDefault();

      openGlobalSearch();

      return;

    }



    if (e.key === 'c' || e.key === 'C') {

      e.preventDefault();

      toggleGateCalc();

      return;

    }



    if (e.key === '?') {

      e.preventDefault();

      toggleShortcutsModal();

      return;

    }



    if (flashcardModalOpen) {

      if (e.key === ' ' || e.key === 'Spacebar') {

        e.preventDefault();

        flipActiveFlashcard();

        return;

      }

      if (e.key === 'ArrowRight') {

        e.preventDefault();

        navFlashcard(1);

        return;

      }

      if (e.key === 'ArrowLeft') {

        e.preventDefault();

        navFlashcard(-1);

        return;

      }

      if (e.key === '1') {

        e.preventDefault();

        rateFlashcard('again');

        return;

      }

      if (e.key === '2') {

        e.preventDefault();

        rateFlashcard('good');

        return;

      }

      if (e.key === '3') {

        e.preventDefault();

        rateFlashcard('mastered');

        return;

      }

    }



    if (e.key === 'h' || e.key === 'H') {

      e.preventDefault();

      if (document.getElementById('practice-hint-box')) {

        togglePracticeHint();

      } else {

        openFormulaFlashcardsModal();

      }

      return;

    }



    if (e.key === 'p' || e.key === 'P') {

      const palette = document.getElementById('test-sidebar');

      if (palette) {

        e.preventDefault();

        toggleTestPalette();

        return;

      }

    }



    const testActive = document.getElementById('test-overlay')?.classList.contains('active');



    // ─── TEST MODE SHORTCUTS ───

    if (testActive && state.activeTest) {

      const currentQ = state.activeTest.currentQ;

      const q = state.activeTest.questions[currentQ];



      const optKeys = { '1':0, '2':1, '3':2, '4':3, 'a':0, 'b':1, 'c':2, 'd':3, 'A':0, 'B':1, 'C':2, 'D':3 };

      if (e.key in optKeys && q && q.type !== 'nat') {

        e.preventDefault();

        const idx = optKeys[e.key];

        const optElements = document.querySelectorAll('.option-item');

        if (optElements[idx]) {

          optElements[idx].click();

        }

        return;

      }



      if (e.key === 'Enter' || ((e.key === 's' || e.key === 'S') && e.altKey)) {

        e.preventDefault();

        saveAndNextTestQ();

        return;

      }

      if ((e.key === 'm' || e.key === 'M') && e.altKey) {

        e.preventDefault();

        markForReview();

        return;

      }

      if ((e.key === 'c' || e.key === 'C') && e.altKey) {

        e.preventDefault();

        clearTestResponse();

        return;

      }

      if ((e.key === 'q' || e.key === 'Q') && e.altKey) {

        e.preventDefault();

        const qpModal = document.getElementById('exam-qp-modal');

        if (qpModal && qpModal.classList.contains('active')) closeExamQuestionPaper();

        else openExamQuestionPaper();

        return;

      }

      if ((e.key === 'i' || e.key === 'I') && e.altKey) {

        e.preventDefault();

        const instModal = document.getElementById('exam-instructions-modal');

        if (instModal && instModal.classList.contains('active')) closeExamInstructions();

        else openExamInstructions();

        return;

      }

      if (e.key === 't' || e.key === 'T') { if (!isTyping) { toggleThemeMode(); e.preventDefault(); } }

      if (e.key === 'r' || e.key === 'R') { if (!isTyping && state.currentPage === 'practice') { openRandomQuestion(); e.preventDefault(); } }

      if (e.key === 'w' || e.key === 'W') { if (!isTyping) { toggleScribblePad(); e.preventDefault(); } }

      if (e.key === 'z' || e.key === 'Z') { if (!isTyping) { toggleZenMode(); e.preventDefault(); } }

      

      

      

      if (e.key === 'f' || e.key === 'F') {

        if (!e.ctrlKey && !e.metaKey && !e.altKey && !['INPUT','TEXTAREA'].includes(e.target?.tagName)) {

          e.preventDefault();

          toggleExamFullscreen();

          return;

        }

      }



      if (e.key === 'm' || e.key === 'M') {

        e.preventDefault();

        markForReview();

        return;

      }



      if (e.key === 'b' || e.key === 'B') {

        e.preventDefault();

        if (q) toggleBookmark(q.id);

        return;

      }



      if (e.key === 'Backspace') {

        e.preventDefault();

        clearTestResponse();

        return;

      }



      if (e.key === 'ArrowRight') {

        if (currentQ < state.activeTest.questions.length - 1) {

          e.preventDefault();

          jumpToTestQ(currentQ + 1);

        }

        return;

      }

      if (e.key === 'ArrowLeft') {

        if (currentQ > 0) {

          e.preventDefault();

          jumpToTestQ(currentQ - 1);

        }

        return;

      }

    }



    // ─── PRACTICE MODE SHORTCUTS ───

    if (testActive && !state.activeTest && state.practiceQueue.length) {

      const q = state.practiceQueue[state.currentQuestion];



      const optKeys = { '1':0, '2':1, '3':2, '4':3, 'a':0, 'b':1, 'c':2, 'd':3, 'A':0, 'B':1, 'C':2, 'D':3 };

      if (e.key in optKeys && q && q.type !== 'nat' && !state.practiceAnswered) {

        e.preventDefault();

        const idx = optKeys[e.key];

        const optElements = document.querySelectorAll('.option-item');

        if (optElements[idx]) {

          optElements[idx].click();

        }

        return;

      }



      if (e.key === 'Enter') {

        e.preventDefault();

        if (!state.practiceAnswered) {

          submitPracticeAnswer();

        } else {

          nextPracticeQuestion();

        }

        return;

      }



      if ((e.key === 's' || e.key === 'S') && !state.practiceAnswered) {

        e.preventDefault();

        skipQuestion();

        return;

      }



      if (e.key === 'b' || e.key === 'B') {

        e.preventDefault();

        if (q) toggleBookmark(q.id);

        return;

      }



      if (e.key === 'ArrowRight' || e.key === ' ') {

        e.preventDefault();

        if (state.currentQuestion < state.practiceQueue.length - 1) {

          nextPracticeQuestion();

        }

        return;

      }



      if (e.key === 'ArrowLeft') {

        e.preventDefault();

        if (state.currentQuestion > 0) {

          prevPracticeQuestion();

        }

        return;

      }

    }

  });

}





// ================================================================

// THEME MODE

// ================================================================

function applyThemeMode(mode) {

  state.themeMode = mode || 'dark';

  document.body.classList.remove('light-mode', 'high-contrast-mode');

  if (state.themeMode === 'light') {

    document.body.classList.add('light-mode');

  } else if (state.themeMode === 'high-contrast') {

    document.body.classList.add('high-contrast-mode');

  }

  const icon = document.getElementById('theme-toggle-icon');

  if (icon) {

    icon.textContent = state.themeMode === 'light' ? '☀️' : (state.themeMode === 'high-contrast' ? '⚡' : '🌙');

  }

  const btn = document.getElementById('theme-toggle-btn');

  if (btn) {

    const title = state.themeMode === 'light' ? 'Theme: Light (Click for High-Contrast)' : (state.themeMode === 'high-contrast' ? 'Theme: High-Contrast (Click for Dark)' : 'Theme: Dark (Click for Light)');

    btn.title = `${title} (T)`;

    btn.setAttribute('aria-label', title);

  }

  try { localStorage.setItem('gate_theme_mode', state.themeMode); } catch(e) {}

}



function toggleThemeMode() {

  const nextMode = state.themeMode === 'dark' ? 'light' : (state.themeMode === 'light' ? 'high-contrast' : 'dark');

  applyThemeMode(nextMode);

  showToast(`Theme switched to ${nextMode.toUpperCase()}`, 'info', 2000);

}



// ================================================================

// COPY QUESTION TEXT

// ================================================================

function copyQuestionText(qId, btn) {

  const q = state.questions.find(x => x.id === qId);

  if (!q) return;

  const labels = ['A', 'B', 'C', 'D', 'E'];

  const opts = (q.options || []).map((o, i) => `${labels[i]}) ${o}`).join('\n');

  const ans = q.type === 'nat'

    ? `Answer: ${q.correct[0]}`

    : `Answer: ${(q.correct || []).map(i => labels[i]).join(', ')}`;

  const text = [q.question, opts ? '\n' + opts : '', '\n' + ans].filter(Boolean).join('\n').trim();

  const doCopy = () => {

    const ta = document.createElement('textarea');

    ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0';

    document.body.appendChild(ta); ta.select(); document.execCommand('copy');

    document.body.removeChild(ta);

  };

  (navigator.clipboard ? navigator.clipboard.writeText(text).catch(doCopy) : Promise.resolve(doCopy()))

    .then(() => {

      if (btn) { const orig = btn.innerHTML; btn.textContent = 'Copied!'; setTimeout(() => btn.innerHTML = orig, 2000); }

    });

}



// ================================================================

// REPORT QUESTION

// ================================================================

function openReportModal(qId) {

  document.getElementById('report-q-modal')?.remove();

  document.getElementById('report-q-backdrop')?.remove();

  const bd = Object.assign(document.createElement('div'), { className: 'report-modal-backdrop', id: 'report-q-backdrop' });

  bd.onclick = closeReportModal;

  const reasons = ['Wrong answer or explanation', 'Typo or formatting error', 'Ambiguous question', 'Duplicate question', 'Off-syllabus topic', 'Other'];

  const modal = Object.assign(document.createElement('div'), { className: 'report-modal', id: 'report-q-modal' });

  modal.innerHTML = `

    <div style="font-weight:700;font-size:15px;margin-bottom:12px">Report Question</div>

    <div style="font-size:12px;color:var(--text-muted);margin-bottom:10px">Select a reason:</div>

    ${reasons.map(r => `<label style="display:flex;align-items:center;gap:8px;font-size:13px;cursor:pointer;margin-bottom:8px"><input type="radio" name="report-reason" value="${r}" style="accent-color:var(--accent)"> ${r}</label>`).join('')}

    <textarea id="report-extra" placeholder="Additional details (optional)..." style="width:100%;margin:10px 0 14px;padding:8px;border-radius:6px;border:1px solid var(--border);background:var(--bg-input);color:var(--text-primary);font-size:12px;resize:vertical;min-height:56px"></textarea>

    <div style="display:flex;gap:8px;justify-content:flex-end">

      <button class="btn btn-secondary btn-sm" onclick="closeReportModal()" type="button">Cancel</button>

      <button class="btn btn-primary btn-sm" onclick="submitReport('${qId}')" type="button">Submit</button>

    </div>`;

  document.body.appendChild(bd);

  document.body.appendChild(modal);

}



function closeReportModal() {

  document.getElementById('report-q-modal')?.remove();

  document.getElementById('report-q-backdrop')?.remove();

}



function submitReport(qId) {

  const reason = document.querySelector('input[name="report-reason"]:checked')?.value;

  if (!reason) { showToast('Please select a reason', 'warning'); return; }

  const extra = document.getElementById('report-extra')?.value || '';

  if (!state.reportedQuestions) state.reportedQuestions = {};

  state.reportedQuestions[qId] = { reason, extra, ts: Date.now() };

  saveCache();

  closeReportModal();

  showToast('Report submitted. Thank you!', 'success');

}



// ================================================================

// SRS (SPACED REPETITION) FOR PRACTICE QUESTIONS

// ================================================================

function getSRSDueCount() {

  const now = Date.now();

  return Object.values(state.srsQueue || {}).filter(s => s.nextReview <= now).length;

}



function updateSRSAfterAttempt(qId, correct) {

  if (!state.srsQueue) state.srsQueue = {};

  const q = state.srsQueue[qId] || { nextReview: 0, interval: 1, ef: 2.5, reps: 0 };

  const grade = correct ? 5 : 1;

  if (grade >= 3) {

    q.reps = (q.reps || 0) + 1;

    q.interval = q.reps === 1 ? 1 : q.reps === 2 ? 6 : Math.round((q.interval || 1) * q.ef);

  } else {

    q.reps = 0; q.interval = 1;

  }

  q.ef = Math.max(1.3, (q.ef || 2.5) + (0.1 - (5 - grade) * (0.08 + (5 - grade) * 0.02)));

  q.nextReview = Date.now() + (q.interval || 1) * 86400000;

  state.srsQueue[qId] = q;

  saveCache();

}



function startSRSReviewSession() {

  const now = Date.now();

  const dueIds = Object.entries(state.srsQueue || {})

    .filter(([, s]) => s.nextReview <= now).map(([id]) => id);

  if (!dueIds.length) { showToast('No questions due for review!', 'success'); return; }

  const dueQs = dueIds.map(id => state.questions.find(q => q.id === id)).filter(Boolean);

  if (!dueQs.length) { showToast('Questions not found in bank', 'warning'); return; }

  state.practiceQueue = dueQs;

  state.currentQuestion = 0;

  state.practiceAnswered = false;

  navigate('practice-mode');

  renderPracticeQuestion();

  showToast(`SRS Review: ${dueQs.length} questions due`, 'info', 3000);

}



// ================================================================

// SIDEBAR SUBJECT PROGRESS & SRS BADGE

// ================================================================

let sidebarSubjectsCollapsed = true;



// ── TOPBAR TOOLS DROPDOWN ──

function toggleTopbarToolsMenu(e) {

  if (e) e.stopPropagation();

  const m = document.getElementById('topbar-tools-menu');

  if (m) m.style.display = m.style.display === 'flex' ? 'none' : 'flex';

}



function closeTopbarToolsMenu() {

  const m = document.getElementById('topbar-tools-menu');

  if (m) m.style.display = 'none';

}



  // Direct guest URL support for instant testing & embedding

  if (new URLSearchParams(window.location.search).get('guest') === '1') {

    setTimeout(() => {

      const btn = document.querySelector('[onclick*="continueAsGuest"]');

      if (btn) btn.click();

      else if (typeof window.continueAsGuest === 'function') window.continueAsGuest();

    }, 1200);

  }



document.addEventListener('click', (e) => {

  if (!e.target.closest('.topbar-dropdown-container')) {

    closeTopbarToolsMenu();

  }

});



function toggleSidebarSubjects() {

  sidebarSubjectsCollapsed = !sidebarSubjectsCollapsed;

  const list = document.getElementById('sidebar-subjects-list');

  const toggle = document.getElementById('sidebar-sub-toggle');

  if (list) list.style.display = sidebarSubjectsCollapsed ? 'none' : 'flex';

  if (toggle) toggle.textContent = sidebarSubjectsCollapsed ? '▸' : '▾';

}



function updateSidebarSubjectProgress() {

  const list = document.getElementById('sidebar-subjects-list');

  if (!list) return;

  list.innerHTML = SUBJECTS.map(sub => {

    const s = getSubjectStats(sub.name);

    const acc = s.total > 0 && s.doneCount > 0 ? `${s.accuracy}%` : '0%';

    const pctColor = s.accuracy >= 70 ? 'var(--green)' : (s.accuracy >= 50 ? 'var(--yellow)' : 'var(--text-muted)');

    return `

      <div class="sidebar-sub-item" onclick="navigate('practice',{subject:'${sub.name.replace(/'/g, "\\'")}'})" title="${sub.name}: ${s.doneCount}/${s.total} attempted (${acc})">

        <div style="display:flex;align-items:center;gap:6px;min-width:0;flex:1">

          <span style="font-size:12px">${sub.icon}</span>

          <span class="sidebar-sub-name">${sub.name}</span>

        </div>

        <span class="sidebar-sub-pct" style="color:${pctColor}">${acc}</span>

      </div>`;

  }).join('');

}



function updateSRSBadge() {

  const count = getSRSDueCount();

  const badge = document.getElementById('sidebar-srs-badge');

  if (badge) {

    badge.textContent = count > 0 ? `${count} DUE` : '';

    badge.style.display = count > 0 ? 'inline-flex' : 'none';

  }

}



// ================================================================

// WEAK TOPIC AUTO-DIAGNOSIS

// ================================================================

function getWeakTopics(topN) {

  topN = topN || 5;

  const map = {};

  state.attempts.forEach(a => {

    const q = state.questions.find(x => x.id === a.questionId);

    if (!q || !q.topic) return;

    const k = q.subject + '|' + q.topic;

    if (!map[k]) map[k] = { subject: q.subject, topic: q.topic, total: 0, correct: 0 };

    map[k].total++;

    if (a.correct) map[k].correct++;

  });

  return Object.values(map)

    .filter(t => t.total >= 3)

    .map(t => ({ ...t, accuracy: Math.round(t.correct / t.total * 100) }))

    .sort((a, b) => a.accuracy - b.accuracy)

    .slice(0, topN);

}



function buildFocusZoneHTML() {

  const weak = getWeakTopics(5);

  const srsCount = getSRSDueCount();

  if (!weak.length && !srsCount) return '';

  const srsBanner = srsCount > 0 ? `

    <div class="srs-review-banner">

      <div>

        <div style="font-size:13px;font-weight:700">\uD83D\uDD01 <strong>${srsCount}</strong> questions due for spaced review</div>

        <div style="font-size:11px;color:var(--text-muted)">Built up from your incorrect & flagged answers</div>

      </div>

      <button class="btn btn-primary btn-sm" onclick="startSRSReviewSession()" type="button">Start Review</button>

    </div>` : '';

  if (!weak.length) return srsBanner ? `<div class="focus-zone-widget">${srsBanner}</div>` : '';

  const chips = weak.map(t =>

    `<div class="focus-chip" onclick="navigate('practice',{subject:'${t.subject.replace(/'/g,"\\'")}',topic:'${t.topic.replace(/'/g,"\\'")}'})" title="${t.subject}: ${t.topic} — ${t.accuracy}% accuracy">

      <span>${t.subject.split(' ').slice(-1)[0]}: ${t.topic.length > 22 ? t.topic.slice(0,20)+'...' : t.topic}</span>

      <span class="focus-chip-pct">${t.accuracy}%</span>

    </div>`).join('');

  return `<div class="focus-zone-widget">

    <div class="focus-zone-header">

      <div class="focus-zone-title">\uD83C\uDFAF Focus Zone \u2014 Drill These Today</div>

      <span style="font-size:11px;color:var(--text-muted)">\u22653 attempts each</span>

    </div>

    ${srsBanner}

    <div style="font-size:12px;color:var(--text-muted);margin-bottom:6px">Weakest topics (lowest accuracy):</div>

    <div class="focus-zone-chips">${chips}</div>

  </div>`;

}



// ================================================================

// STUDY PLANNER

// ================================================================

// Interactive Daily Targets

function toggleStudyTarget(idx) {

  if (!state.studyPlannerTargets || !state.studyPlannerTargets[idx]) return;

  state.studyPlannerTargets[idx].done = !state.studyPlannerTargets[idx].done;

  saveCache();

  renderDashboard(document.getElementById('page-content'));

}



function addStudyTargetPrompt() {

  const txt = prompt('Enter a topic for today (e.g. Dijkstra, Virtual Memory, Cache):');

  if (!txt || !txt.trim()) return;

  if (!state.studyPlannerTargets) state.studyPlannerTargets = [];

  state.studyPlannerTargets.push({ text: txt.trim(), done: false, date: new Date().toISOString().slice(0, 10) });

  saveCache();

  renderDashboard(document.getElementById('page-content'));

  showToast('Target topic added! 🎯', 'success');

}



function deleteStudyTarget(idx) {

  if (!state.studyPlannerTargets || !state.studyPlannerTargets[idx]) return;

  state.studyPlannerTargets.splice(idx, 1);

  saveCache();

  renderDashboard(document.getElementById('page-content'));

}



function addQuickTarget(topic) {

  if (!state.studyPlannerTargets) state.studyPlannerTargets = [];

  if (state.studyPlannerTargets.some(t => t.text === topic)) {

    showToast('Topic already in daily targets', 'info');

    return;

  }

  state.studyPlannerTargets.push({ text: topic, done: false, date: new Date().toISOString().slice(0, 10) });

  saveCache();

  renderDashboard(document.getElementById('page-content'));

  showToast(`Added "${topic}" to today's targets! 🎯`, 'success');

}



function buildStudyPlannerHTML() {

  const today = new Date();

  const todayStr = today.toISOString().slice(0, 10);

  const todayAtts = state.attempts.filter(a => {

    const ts = a.ts || a.timestamp || 0;

    return new Date(ts).toISOString().slice(0, 10) === todayStr;

  });

  const todayCount = todayAtts.length;

  const todayCorrect = todayAtts.filter(a => a.correct).length;

  const goal = state.dailyGoal || 20;

  const goalPct = Math.min(100, Math.round(todayCount / goal * 100));

  const todayTests = state.testSessions.filter(s => {

    const ts = s.endTime || s.timestamp || 0;

    return new Date(ts).toISOString().slice(0, 10) === todayStr;

  }).length;



  // Neglected subjects (no practice in last 7 days)

  const cutoff = Date.now() - 7 * 86400000;

  const recentSubs = new Set(state.attempts

    .filter(a => (a.ts || a.timestamp || 0) > cutoff)

    .map(a => { const q = state.questions.find(x => x.id === a.questionId); return q && q.subject; })

    .filter(Boolean));

  const neglected = SUBJECTS.filter(s => !recentSubs.has(s.name)).slice(0, 5);



  // 30-day heatmap

  const heat = {};

  state.attempts.forEach(a => {

    const dk = new Date(a.ts || a.timestamp || 0).toISOString().slice(0, 10);

    heat[dk] = (heat[dk] || 0) + 1;

  });

  const cells = [];

  for (let i = 29; i >= 0; i--) {

    const d = new Date(Date.now() - i * 86400000);

    const dk = d.toISOString().slice(0, 10);

    const cnt = heat[dk] || 0;

    const lv = cnt === 0 ? 0 : cnt < 5 ? 1 : cnt < 15 ? 2 : cnt < 25 ? 3 : 4;

    const lbl = dk === todayStr ? `Today: ${cnt} Qs` : `${dk}: ${cnt} Qs`;

    cells.push(`<div class="heatmap-cell" data-count="${lv}" title="${lbl}"></div>`);

  }



  const targets = (state.studyPlannerTargets || []);

  const targetsHtml = targets.length

    ? `<div class="study-targets-list">

        ${targets.map((t, idx) => `

          <div class="study-target-item ${t.done ? 'completed' : ''}">

            <label style="display:flex;align-items:center;gap:8px;cursor:pointer;flex:1">

              <input type="checkbox" ${t.done ? 'checked' : ''} onchange="toggleStudyTarget(${idx})" style="accent-color:var(--green)">

              <span>${escapeHtml(t.text)}</span>

            </label>

            <div style="display:flex;align-items:center;gap:6px">

              <button class="btn btn-secondary btn-sm" onclick="navigate('practice',{search:'${escapeHtml(t.text).replace(/'/g, "\\'")}'})" style="padding:2px 8px;font-size:10px" type="button">Practice</button>

              <button class="study-target-del-btn" onclick="deleteStudyTarget(${idx})" title="Delete target" type="button">✕</button>

            </div>

          </div>

        `).join('')}

       </div>`

    : `<div style="font-size:12px;color:var(--text-muted);padding:8px 0">No daily topics set yet. Click "+ Add Topic" or pick a high-yield suggestion below:</div>`;



  const suggestedTopics = ['Dijkstra & Shortest Paths', 'Virtual Memory & Paging', 'Cache Mapping & Hit Ratio', 'Pipelining & Hazards', 'Relational Algebra & SQL'];



  const neglectedHtml = neglected.length

    ? `<div class="neglected-subjects">

         <div class="neglected-subjects-title">⚠️ Not practiced in last 7 days:</div>

         <div class="neglected-chips">${neglected.map(s =>

           `<div class="neglected-chip" onclick="navigate('practice',{subject:'${s.name.replace(/'/g,"\\'")}'})">${s.icon} ${s.name.split(' ')[0]}</div>`).join('')}

         </div>

       </div>`

    : `<div style="font-size:12px;color:var(--green);margin-top:8px">✅ Great! You’ve practiced all subjects this week.</div>`;



  return `<div class="planner-widget">

    <div class="planner-header">

      <div>

        <div class="planner-title">📅 Today’s Study Plan & Daily Targets</div>

        <div class="planner-date">${today.toLocaleDateString('en-IN', { weekday:'long', day:'numeric', month:'long' })}</div>

      </div>

      <div style="display:flex;gap:6px;align-items:center">

        <button class="btn btn-secondary btn-sm" onclick="promptChangeDailyGoal()" type="button" title="Change daily question goal">⚙ Goal: ${goal} Q/day</button>

        <button class="btn btn-primary btn-sm" onclick="addStudyTargetPrompt()" type="button">+ Add Topic</button>

      </div>

    </div>

    <div class="planner-goals-grid">

      <div class="planner-goal-card">

        <div class="planner-goal-value">${todayCount}</div>

        <div class="planner-goal-label">Questions Today</div>

        <div class="planner-progress-bar"><div class="planner-progress-fill" style="width:${goalPct}%"></div></div>

        <div class="planner-goal-sub">${goalPct}% of ${goal} goal</div>

      </div>

      <div class="planner-goal-card">

        <div class="planner-goal-value" style="color:var(--green)">${todayCount > 0 ? Math.round(todayCorrect / todayCount * 100) : 0}%</div>

        <div class="planner-goal-label">Today’s Accuracy</div>

        <div class="planner-goal-sub">${todayCorrect} correct / ${todayCount} done</div>

      </div>

      <div class="planner-goal-card">

        <div class="planner-goal-value" style="color:var(--yellow)">${todayTests}</div>

        <div class="planner-goal-label">Tests Today</div>

        <div class="planner-goal-sub">Full-length & subject</div>

      </div>

    </div>



    <!-- Daily Focus Targets -->

    <div style="margin-top:14px;background:var(--bg-input);padding:12px;border-radius:var(--radius-sm)">

      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px">

        <div style="font-size:12px;font-weight:700">🎯 Today’s Focus Targets (${targets.filter(t=>t.done).length}/${targets.length} completed)</div>

      </div>

      ${targetsHtml}

      <div style="display:flex;gap:4px;flex-wrap:wrap;margin-top:8px">

        <span style="font-size:11px;color:var(--text-muted);align-self:center">Suggestions:</span>

        ${suggestedTopics.map(t => `<button class="chip" onclick="addQuickTarget('${t.replace(/'/g, "\\'")}')" style="font-size:10px;padding:2px 8px" type="button">+ ${t}</button>`).join('')}

      </div>

    </div>



    ${neglectedHtml}

    <div style="margin-top:14px">

      <div style="font-size:11px;color:var(--text-muted);margin-bottom:5px">30-day practice streak heatmap (Hover for details)</div>

      <div class="heatmap-row">${cells.join('')}</div>

    </div>

  </div>`;

}



function promptChangeDailyGoal() {

  const val = prompt(`Daily goal is currently ${state.dailyGoal || 20} questions.\nEnter a new goal (5-100):`, state.dailyGoal || 20);

  if (!val) return;

  const n = parseInt(val, 10);

  if (isNaN(n) || n < 5 || n > 100) { showToast('Please enter a number between 5 and 100', 'warning'); return; }

  state.dailyGoal = n;

  saveCache();

  renderDashboard(document.getElementById('page-content'));

  showToast(`Daily goal updated to ${n} questions`, 'success');

}



// ================================================================

// SCORE HISTORY TIMELINE

// ================================================================

function buildScoreHistoryHTML() {

  const sessions = [...state.testSessions].sort((a, b) => (a.endTime || 0) - (b.endTime || 0));

  const pbs = { overall: 0, easy: 0, medium: 0, hard: 0, pyq: 0 };

  sessions.forEach(s => {

    const pct = s.percentage || 0;

    pbs.overall = Math.max(pbs.overall, pct);

    const mid = (s.mockId || '').toLowerCase();

    if (mid.includes('easy')) pbs.easy = Math.max(pbs.easy, pct);

    else if (mid.includes('medium')) pbs.medium = Math.max(pbs.medium, pct);

    else if (mid.includes('pyq') || mid.includes('gate-20')) pbs.pyq = Math.max(pbs.pyq, pct);

    else pbs.hard = Math.max(pbs.hard, pct);

  });



  const last10 = sessions.slice(-10);

  const chartLabels = JSON.stringify(last10.map(s => new Date(s.endTime || 0).toLocaleDateString('en-IN', { day:'2-digit', month:'short' })));

  const chartData = JSON.stringify(last10.map(s => s.percentage || 0));

  const pbChips = [

    pbs.overall ? `<div class="score-pb-chip">🥇 Overall Best: ${pbs.overall}%</div>` : '',

    pbs.easy ? `<div class="score-pb-chip" style="background:rgba(34,197,94,0.12);color:var(--green);border-color:var(--green)">🟢 Easy PB: ${pbs.easy}%</div>` : '',

    pbs.medium ? `<div class="score-pb-chip" style="background:rgba(234,179,8,0.12);color:#eab308;border-color:#eab308">🟡 Medium PB: ${pbs.medium}%</div>` : '',

    pbs.hard ? `<div class="score-pb-chip" style="background:rgba(239,68,68,0.12);color:var(--red);border-color:var(--red)">🔴 Hard PB: ${pbs.hard}%</div>` : '',

    pbs.pyq ? `<div class="score-pb-chip" style="background:rgba(56,189,248,0.12);color:#38bdf8;border-color:#38bdf8">📘 PYQ PB: ${pbs.pyq}%</div>` : '',

  ].filter(Boolean).join('');



  const airBenchmarks = [

    { bracket: '75+ Marks', rank: 'AIR 1 – 100', note: 'Top 0.1% • IISc Bangalore & Top 5 Old IITs M.Tech CSE' },

    { bracket: '60 – 74 Marks', rank: 'AIR 100 – 500', note: 'All Old IITs Direct Admission / PSU Shortlists' },

    { bracket: '45 – 59 Marks', rank: 'AIR 500 – 2,500', note: 'Top NITs (Trichy, Surathkal, Warangal), IIIT-H, IIIT-B' },

    { bracket: '32 – 44 Marks', rank: 'AIR 2,500 – 10,000', note: 'GATE Qualifying Range / Newer IITs & NITs' }

  ];



  return `<div class="score-history-card">

    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;flex-wrap:wrap;gap:8px">

      <div style="font-size:14px;font-weight:700">🏆 Mock Test Leaderboard & Score Trajectory</div>

      <span style="font-size:11px;color:var(--text-muted)">${sessions.length} Tests Recorded</span>

    </div>

    ${pbChips ? `<div class="score-pb-chips">${pbChips}</div>` : ''}

    ${sessions.length >= 2 ? `

      <div class="mini-chart-wrapper"><canvas id="score-history-chart"></canvas></div>

      <script>

      (function() {

        var attempt = 0;

        function tryDraw() {

          var ctx = document.getElementById('score-history-chart');

          if (!ctx || !window.Chart) { if (attempt++ < 20) setTimeout(tryDraw, 200); return; }

          var ex = Chart.getChart(ctx); if (ex) ex.destroy();

          new Chart(ctx, {

            type: 'line',

            data: { labels: ${chartLabels}, datasets: [{ label: 'Score %', data: ${chartData}, borderColor: '#6c63ff', backgroundColor: 'rgba(108,99,255,0.10)', borderWidth: 2, pointBackgroundColor: '#6c63ff', pointRadius: 4, fill: true, tension: 0.35 }] },

            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { min: 0, max: 100, grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#9090b0', font: { size: 10 } } }, x: { grid: { display: false }, ticks: { color: '#9090b0', font: { size: 10 } } } } }

          });

        }

        setTimeout(tryDraw, 200);

      })();

      </scr` + `ipt>

    ` : `<div style="font-size:12px;color:var(--text-muted);padding:14px;text-align:center;background:var(--bg-input);border-radius:var(--radius-sm);margin-top:10px">📈 Complete at least 2 tests to render your multi-test score trend line.</div>`}



    <!-- GATE CSE AIR Benchmark Brackets -->

    <div style="margin-top:14px;border-top:1px solid var(--border);padding-top:12px">

      <div style="font-size:12px;font-weight:700;margin-bottom:8px">🎯 Official GATE CSE Percentile & AIR Cutoff Brackets:</div>

      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:8px">

        ${airBenchmarks.map(b => `

          <div style="background:var(--bg-input);padding:8px 10px;border-radius:6px;border-left:3px solid var(--accent)">

            <div style="font-size:12px;font-weight:700;color:var(--text-primary)">${b.bracket} → <span style="color:var(--accent)">${b.rank}</span></div>

            <div style="font-size:10px;color:var(--text-muted);margin-top:2px">${b.note}</div>

          </div>

        `).join('')}

      </div>

    </div>

  </div>`;

}



// ================================================================

// SECTION-WISE MOCK ANALYTICS

// ================================================================

function buildSectionAnalysisHTML(session, questions, answers) {

  if (!questions || !questions.length) return '';

  const subMap = {};

  const SUBJ_COLOR = {};

  SUBJECTS.forEach(s => { SUBJ_COLOR[s.name] = s.color; });

  questions.forEach((q, i) => {

    const sub = q.subject || 'General';

    if (!subMap[sub]) subMap[sub] = { total: 0, attempted: 0, correct: 0, marks: 0, maxMarks: 0 };

    const marks = q.marks || 1;

    subMap[sub].total++;

    subMap[sub].maxMarks += marks;

    const a = answers[i];

    const skip = a === null || (Array.isArray(a) && !a.length);

    if (!skip) {

      subMap[sub].attempted++;

      let ok = false;

      if (q.type === 'nat') { const v=parseFloat(a),e=q.correct[0]; ok=v>=(q.natRange?.min??e)&&v<=(q.natRange?.max??e); }

      else { const s=(Array.isArray(a)?a:[a]).sort((x,y)=>x-y),e=[...q.correct].sort((x,y)=>x-y); ok=s.length===e.length&&s.every((v,idx)=>v===e[idx]); }

      if (ok) { subMap[sub].correct++; subMap[sub].marks += marks; }

      else { subMap[sub].marks = Math.max(-5, subMap[sub].marks - (marks === 2 ? 0.67 : 0.33)); }

    }

  });

  const sorted = Object.entries(subMap)

    .filter(([, v]) => v.maxMarks > 0)

    .sort(([, a], [, b]) => (b.marks / b.maxMarks) - (a.marks / a.maxMarks));

  const weakest = sorted.filter(([, v]) => v.maxMarks > 0 && (v.marks / v.maxMarks) < 0.4);

  const cards = sorted.map(([sub, v]) => {

    const pct = Math.max(0, Math.round(v.marks / v.maxMarks * 100));

    const color = SUBJ_COLOR[sub] || 'var(--accent)';

    return `<div class="section-analysis-card">

      <div class="section-analysis-subject">${sub.split(' ').slice(0, 2).join(' ')}</div>

      <div class="section-analysis-marks" style="color:${color}">${Math.round(v.marks * 10) / 10}/${v.maxMarks}m</div>

      <div style="font-size:10px;color:var(--text-muted)">${v.correct}/${v.attempted} attempted (${pct}%)</div>

      <div class="section-analysis-bar"><div class="section-analysis-fill" style="width:${pct}%;background:${color}"></div></div>

    </div>`;

  }).join('');

  const suggestion = weakest.length

    ? `<div class="section-suggest">

        <strong>Suggestion:</strong> Focus on ${weakest.slice(0, 2).map(([s]) => s).join(' & ')} (below 40% today).

        <button class="btn btn-secondary btn-sm" style="margin-left:8px;font-size:11px" onclick="navigate('practice',{subject:'${weakest[0][0].replace(/'/g,"\\'")}'})" type="button">Drill Now</button>

       </div>`

    : `<div style="font-size:12px;color:var(--green);margin-top:8px">\u2705 Solid performance across all subjects!</div>`;

  return `<div class="card" style="margin-bottom:20px">

    <div class="card-header"><div class="card-title">&#x1F4CA; Section-Wise Performance</div></div>

    <div class="section-analysis-grid">${cards}</div>

    ${suggestion}

  </div>`;

}



// ================================================================

// QUESTION-WISE TIME HEATMAP & BLACK HOLE INSPECTOR

// ================================================================

function buildQuestionTimeHeatmapHTML(session, questions, answers) {

  const times = session.timePerQ || new Array(questions.length).fill(0);

  const maxTime = Math.max(180, ...times);

  let blackHoles = 0;

  let fastestSec = 99999, fastestIdx = 0;

  let slowestSec = 0, slowestIdx = 0;



  questions.forEach((q, i) => {

    const t = times[i] || 0;

    if (t > 180) blackHoles++;

    if (t > 0 && t < fastestSec) { fastestSec = t; fastestIdx = i; }

    if (t > slowestSec) { slowestSec = t; slowestIdx = i; }

  });



  const bars = questions.map((q, i) => {

    const t = times[i] || 0;

    const a = answers[i];

    const isSkip = a === null || (Array.isArray(a) && !a.length);

    let ok = false;

    if (!isSkip) {

      if (q.type === 'nat') {

        const v = parseFloat(a), e = q.correct[0];

        ok = v >= (q.natRange?.min ?? e) && v <= (q.natRange?.max ?? e);

      } else {

        const s = (Array.isArray(a) ? a : [a]).slice().sort((x, y) => x - y), e = q.correct.slice().sort((x, y) => x - y);

        ok = s.length === e.length && s.every((v, idx) => v === e[idx]);

      }

    }

    const isBlackHole = t > 180;

    const fillCls = isBlackHole ? 'black-hole' : (isSkip ? 'skipped' : (ok ? 'correct' : 'wrong'));

    const heightPct = Math.min(100, Math.max(12, Math.round((t / maxTime) * 100)));

    const tooltip = `Q${i + 1}: ${fmtSec(t)} (${isSkip ? 'Skipped' : (ok ? 'Correct' : 'Wrong')}) ${isBlackHole ? '⚠️ TIME BLACK HOLE' : ''} — ${q.subject || ''}`;



    return `

      <div class="time-bar-col" onclick="scrollToResultQ(${i})" title="${tooltip}">

        <div class="time-bar-fill ${fillCls}" style="height:${heightPct}%"></div>

        <div class="time-bar-label">${i + 1}</div>

      </div>`;

  }).join('');



  return `

    <div class="time-heatmap-card">

      <div class="time-heatmap-header">

        <div>

          <div class="time-heatmap-title">⏱️ Question Time Distribution & Black Hole Inspector</div>

          <div style="font-size:11px;color:var(--text-muted);margin-top:2px">Click any bar to inspect question derivation below. Target pace: ≤ 150s/question.</div>

        </div>

        <div style="display:flex;gap:6px;flex-wrap:wrap">

          <span class="chip" style="font-size:11px">⚡ Fastest: Q${fastestIdx + 1} (${fmtSec(fastestSec === 99999 ? 0 : fastestSec)})</span>

          <span class="chip" style="font-size:11px">🐢 Slowest: Q${slowestIdx + 1} (${fmtSec(slowestSec)})</span>

          ${blackHoles > 0 ? `<span class="chip" style="background:rgba(239,68,68,0.2);color:var(--red);font-weight:700">🔥 ${blackHoles} Black Holes (>3m)</span>` : `<span class="chip" style="background:rgba(34,197,94,0.15);color:var(--green)">✅ Excellent Pacing</span>`}

        </div>

      </div>

      <div class="time-heatmap-bars-wrapper">

        <div class="time-heatmap-threshold-line" style="bottom:${Math.round((180 / maxTime) * 100)}%">

          <span class="time-heatmap-threshold-label">3m Limit</span>

        </div>

        ${bars}

      </div>

      <div style="display:flex;gap:12px;margin-top:10px;font-size:11px;color:var(--text-muted);flex-wrap:wrap">

        <span><strong style="color:var(--green)">■</strong> Correct (&lt;3m)</span>

        <span><strong style="color:var(--red)">■</strong> Incorrect (&lt;3m)</span>

        <span><strong style="color:#ff0055">■</strong> 🔥 Time Black Hole (&gt;3m)</span>

        <span><strong style="color:var(--border-light)">■</strong> Skipped</span>

      </div>

    </div>`;

}



function scrollToResultQ(idx) {

  const el = document.getElementById(`result-q-${idx}`);

  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });

}



// ================================================================

// RANDOM QUESTION

// ================================================================

function openRandomQuestion() {

  const pool = state.practiceQueue.length > 0 ? state.practiceQueue : state.questions;

  if (!pool.length) { showToast('No questions available', 'warning'); return; }

  const q = pool[Math.floor(Math.random() * pool.length)];

  openSingleQuestion(q.id);

}







// ════════════════════════════════════════════════════════════════

// 📝 VIRTUAL SCRIBBLE PAD (SCRATCHPAD CANVAS) ENGINE

// ════════════════════════════════════════════════════════════════

let scribblePadOpen = false;

let scribbleTool = 'pen';

let scribbleColor = '#6c63ff';

let scribbleGrid = false;

let scribbleDrawing = false;

let scribbleCtx = null;

let scribbleLastX = 0, scribbleLastY = 0;



function toggleScribblePad(force) {

  scribblePadOpen = typeof force === 'boolean' ? force : !scribblePadOpen;

  const card = document.getElementById('scribble-pad-card');

  const backdrop = document.getElementById('scribble-pad-backdrop');

  if (card) card.classList.toggle('active', scribblePadOpen);

  if (backdrop) backdrop.classList.toggle('active', scribblePadOpen);

  if (scribblePadOpen) {

    setTimeout(initScribblePadCanvas, 50);

  }

}



function initScribblePadCanvas() {

  const canvas = document.getElementById('scribble-canvas');

  const wrapper = document.getElementById('scribble-canvas-wrapper');

  if (!canvas || !wrapper) return;

  if (!scribbleCtx) {

    canvas.width = wrapper.clientWidth * window.devicePixelRatio || 600;

    canvas.height = wrapper.clientHeight * window.devicePixelRatio || 380;

    scribbleCtx = canvas.getContext('2d');

    scribbleCtx.scale(window.devicePixelRatio || 1, window.devicePixelRatio || 1);

    scribbleCtx.lineCap = 'round';

    scribbleCtx.lineJoin = 'round';



    const getPos = e => {

      const rect = canvas.getBoundingClientRect();

      const clientX = e.touches ? e.touches[0].clientX : e.clientX;

      const clientY = e.touches ? e.touches[0].clientY : e.clientY;

      return { x: clientX - rect.left, y: clientY - rect.top };

    };



    const startDraw = e => {

      scribbleDrawing = true;

      const pos = getPos(e);

      scribbleLastX = pos.x;

      scribbleLastY = pos.y;

    };



    const draw = e => {

      if (!scribbleDrawing || !scribbleCtx) return;

      e.preventDefault();

      const pos = getPos(e);

      scribbleCtx.beginPath();

      scribbleCtx.moveTo(scribbleLastX, scribbleLastY);

      scribbleCtx.lineTo(pos.x, pos.y);



      if (scribbleTool === 'eraser') {

        scribbleCtx.strokeStyle = '#14141c';

        scribbleCtx.lineWidth = 18;

      } else if (scribbleTool === 'highlighter') {

        scribbleCtx.strokeStyle = scribbleColor + '55';

        scribbleCtx.lineWidth = 14;

      } else {

        scribbleCtx.strokeStyle = scribbleColor;

        scribbleCtx.lineWidth = 2.5;

      }

      scribbleCtx.stroke();

      scribbleLastX = pos.x;

      scribbleLastY = pos.y;

    };



    const stopDraw = () => { scribbleDrawing = false; };



    canvas.addEventListener('mousedown', startDraw);

    canvas.addEventListener('mousemove', draw);

    window.addEventListener('mouseup', stopDraw);



    canvas.addEventListener('touchstart', startDraw, { passive: false });

    canvas.addEventListener('touchmove', draw, { passive: false });

    window.addEventListener('touchend', stopDraw);

  }

}



function setScribbleTool(tool) {

  scribbleTool = tool;

  document.querySelectorAll('.scribble-btn').forEach(b => b.classList.remove('active'));

  document.getElementById(`scribble-tool-${tool}`)?.classList.add('active');

}



function setScribbleColor(col, el) {

  scribbleColor = col;

  document.querySelectorAll('.scribble-color-dot').forEach(d => d.classList.remove('active'));

  if (el) el.classList.add('active');

  if (scribbleTool === 'eraser') setScribbleTool('pen');

}



function clearScribbleCanvas() {

  const canvas = document.getElementById('scribble-canvas');

  if (canvas && scribbleCtx) {

    scribbleCtx.clearRect(0, 0, canvas.width, canvas.height);

  }

}



function toggleScribbleGrid() {

  scribbleGrid = !scribbleGrid;

  const wrapper = document.getElementById('scribble-canvas-wrapper');

  if (wrapper) wrapper.classList.toggle('grid-paper', scribbleGrid);

}



// ════════════════════════════════════════════════════════════════

// 🛡️ TCS iON EXAM STRICT MODE

// ════════════════════════════════════════════════════════════════

function toggleExamStrictMode() {

  state.examStrictMode = !state.examStrictMode;

  const btn = document.getElementById('exam-strict-btn');

  if (btn) {

    btn.innerHTML = state.examStrictMode ? '🛡️ Strict: ON' : '🛡️ Strict: OFF';

    btn.style.color = state.examStrictMode ? 'var(--green)' : 'inherit';

  }

  showToast(state.examStrictMode

    ? '🛡️ TCS iON Exam Strict Mode Active: Fullscreen lock & Mouse-only keypad enforced!'

    : 'Exam Strict Mode Deactivated', 'info', 3000);

}



// ════════════════════════════════════════════════════════════════

// 💸 NEGATIVE MARKS AUDIT & LOST RANK RECOVERY SIMULATOR

// ════════════════════════════════════════════════════════════════

function buildNegativeMarksAuditHTML(session, questions, answers) {

  if (!questions || !questions.length) return '';

  let penaltyTotal = 0;

  let wrongMcqs = 0;

  const subjectPenalties = {};



  questions.forEach((q, i) => {

    const a = answers[i];

    const isSkip = a === null || (Array.isArray(a) && !a.length);

    if (!isSkip) {

      let ok = false;

      if (q.type === 'nat') {

        const v = parseFloat(a), e = q.correct[0];

        ok = v >= (q.natRange?.min ?? e) && v <= (q.natRange?.max ?? e);

      } else {

        const s = (Array.isArray(a) ? a : [a]).slice().sort((x, y) => x - y), e = q.correct.slice().sort((x, y) => x - y);

        ok = s.length === e.length && s.every((v, idx) => v === e[idx]);

      }

      if (!ok && q.type === 'mcq') {

        wrongMcqs++;

        const p = q.marks === 2 ? 0.67 : 0.33;

        penaltyTotal += p;

        const sub = q.subject || 'General';

        subjectPenalties[sub] = (subjectPenalties[sub] || 0) + p;

      }

    }

  });



  penaltyTotal = Math.round(penaltyTotal * 100) / 100;

  const potentialScore = Math.round((session.score + penaltyTotal) * 100) / 100;

  const curPred = calculateGatePrediction(session.score, state.predictedCategory || 'GEN');

  const potPred = calculateGatePrediction(potentialScore, state.predictedCategory || 'GEN');



  const gdi = Math.max(0, Math.min(100, Math.round(100 - (penaltyTotal / (session.maxScore || 100)) * 300)));

  const gdiBadge = gdi >= 85 ? '🎯 Disciplined Sniper' : (gdi >= 60 ? '🎲 Calculated Risk-Taker' : '⚠️ Aggressive Gambler');



  return `

    <div class="negative-marks-card">

      <div class="negative-marks-header">

        <div>

          <div style="font-size:15px;font-weight:700;display:flex;align-items:center;gap:6px">

            <span>💸 Negative Marks Audit & "Lost Rank" Simulator</span>

          </div>

          <div style="font-size:11px;color:var(--text-muted);margin-top:2px">Measure the exact AIR and score penalty suffered from guessing MCQs</div>

        </div>

        <span class="chip" style="font-weight:700;background:rgba(239,68,68,0.15);color:var(--red)">-${penaltyTotal} Marks Lost</span>

      </div>

      <div class="negative-marks-grid">

        <div class="negative-stat-box">

          <div class="negative-stat-val" style="color:var(--red)">-${penaltyTotal}m</div>

          <div class="negative-stat-lbl">Negative Penalty Paid</div>

          <div style="font-size:10px;color:var(--text-muted);margin-top:2px">${wrongMcqs} Incorrect MCQs</div>

        </div>

        <div class="negative-stat-box">

          <div class="negative-stat-val" style="color:var(--green)">${potentialScore}m</div>

          <div class="negative-stat-lbl">Score if Blind Guesses Skipped</div>

          <div style="font-size:10px;color:var(--green);margin-top:2px">+${penaltyTotal}m Free Jump</div>

        </div>

        <div class="negative-stat-box">

          <div class="negative-stat-val" style="color:var(--accent)">${potPred.air}</div>

          <div class="negative-stat-lbl">Recoverable AIR Bracket</div>

          <div style="font-size:10px;color:var(--accent);margin-top:2px">vs. Current ${curPred.air}</div>

        </div>

        <div class="negative-stat-box">

          <div class="negative-stat-val">${gdi}%</div>

          <div class="negative-stat-lbl">Guessing Discipline (GDI)</div>

          <div style="font-size:10px;font-weight:700;color:var(--accent);margin-top:2px">${gdiBadge}</div>

        </div>

      </div>

      <div class="negative-recovery-banner">

        💡 <strong>Tactical GATE Wisdom:</strong> If you had skipped those <strong>${wrongMcqs} incorrect MCQs</strong> instead of guessing, your score would be <strong>${potentialScore} marks</strong> instead of <strong>${session.score} marks</strong>, vaulting your rank into <strong>${potPred.air}</strong> (${potPred.eligibility})!

      </div>

    </div>`;

}



// ════════════════════════════════════════════════════════════════

// 👥 10,000-CANDIDATE GAUSSIAN BELL CURVE & PERCENTILE SIMULATOR

// ════════════════════════════════════════════════════════════════

function buildGaussianBellCurveSVG(score, maxScore) {

  score = score || 0;

  maxScore = maxScore || 100;

  const mu = 32.5; // Mean cutoff

  const sigma = 14.8; // Calibrated std dev for 120k GATE candidates

  const z = (score - mu) / sigma;



  // Error function approximation for Gaussian CDF

  const erf = x => {

    const a1 = 0.254829592, a2 = -0.284496736, a3 = 1.421413741, a4 = -1.453152027, a5 = 1.061405429, p = 0.3275911;

    const sign = x < 0 ? -1 : 1;

    x = Math.abs(x);

    const t = 1.0 / (1.0 + p * x);

    const y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * Math.exp(-x * x);

    return sign * y;

  };



  const percentile = Math.max(0.5, Math.min(99.9, Math.round((0.5 * (1 + erf(z / Math.SQRT2))) * 1000) / 10));

  const simRank = Math.max(1, Math.round(10000 * (1 - percentile / 100)));



  // Generate SVG curve points

  const points = [];

  const W = 600, H = 140, pad = 30;

  for (let m = 0; m <= 100; m += 2) {

    const zm = (m - mu) / sigma;

    const density = Math.exp(-0.5 * zm * zm) / (sigma * Math.sqrt(2 * Math.PI));

    const x = pad + (m / 100) * (W - 2 * pad);

    const y = H - (density / 0.028) * (H - 25);

    points.push(`${Math.round(x)},${Math.round(y)}`);

  }



  const userX = Math.round(pad + (Math.max(0, Math.min(100, score)) / 100) * (W - 2 * pad));

  const cutoffX = Math.round(pad + (mu / 100) * (W - 2 * pad));

  const top10X = Math.round(pad + (52 / 100) * (W - 2 * pad));

  const top1X = Math.round(pad + (68 / 100) * (W - 2 * pad));



  return `

    <div class="bell-curve-card">

      <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px">

        <div>

          <div style="font-size:15px;font-weight:700">👥 10,000-Candidate Synthetic Cohort Bell Curve</div>

          <div style="font-size:11px;color:var(--text-muted);margin-top:2px">Calibrated Gaussian distribution of all-India test-takers</div>

        </div>

        <div style="display:flex;gap:6px">

          <span class="chip" style="font-weight:700;color:var(--accent);border-color:var(--accent)">Top ${(100 - percentile).toFixed(1)}%</span>

          <span class="chip" style="font-weight:700;color:var(--green)">Simulated Rank: ~${simRank} / 10k</span>

        </div>

      </div>

      <div class="bell-curve-wrapper">

        <svg viewBox="0 0 ${W} ${H}" preserveAspectRatio="none">

          <defs>

            <linearGradient id="bellGrad" x1="0%" y1="0%" x2="0%" y2="100%">

              <stop offset="0%" stop-color="#6c63ff" stop-opacity="0.4"/>

              <stop offset="100%" stop-color="#6c63ff" stop-opacity="0.02"/>

            </linearGradient>

          </defs>

          <path d="M ${pad},${H} L ${points.join(' L ')} L ${W - pad},${H} Z" fill="url(#bellGrad)"/>

          <path d="M ${points.join(' L ')}" fill="none" stroke="#6c63ff" stroke-width="2.5"/>



          <!-- Benchmark Lines -->

          <line x1="${cutoffX}" y1="20" x2="${cutoffX}" y2="${H}" stroke="#eab308" stroke-dasharray="3,3" stroke-width="1"/>

          <text x="${cutoffX}" y="15" fill="#eab308" font-size="9" text-anchor="middle">Cutoff (32.5)</text>



          <line x1="${top10X}" y1="25" x2="${top10X}" y2="${H}" stroke="#38bdf8" stroke-dasharray="3,3" stroke-width="1"/>

          <text x="${top10X}" y="20" fill="#38bdf8" font-size="9" text-anchor="middle">Top 10% (52m)</text>



          <line x1="${top1X}" y1="30" x2="${top1X}" y2="${H}" stroke="#22c55e" stroke-dasharray="3,3" stroke-width="1"/>

          <text x="${top1X}" y="25" fill="#22c55e" font-size="9" text-anchor="middle">Top 1% (68m)</text>



          <!-- Candidate Pin -->

          <line x1="${userX}" y1="10" x2="${userX}" y2="${H}" stroke="#ef4444" stroke-width="2.5"/>

          <circle cx="${userX}" cy="10" r="4.5" fill="#ef4444"/>

          <text x="${userX}" y="6" fill="#ef4444" font-size="10" font-weight="bold" text-anchor="middle">YOU (${score}m)</text>

        </svg>

      </div>

      <div style="font-size:12px;color:var(--text-muted);display:flex;justify-content:space-between;flex-wrap:wrap;gap:6px">

        <span>0 Marks (Bottom)</span>

        <span>${percentile}% of aspirants scored below you</span>

        <span>100 Marks (AIR 1)</span>

      </div>

    </div>`;

}



// ════════════════════════════════════════════════════════════════

// 🗺️ OFFICIAL IIT MADRAS 87-CHAPTER SYLLABUS COVERAGE AUDIT

// ════════════════════════════════════════════════════════════════

function buildSyllabusCoverageAuditHTML() {

  const attemptedMap = new Set(state.attempts.map(a => {

    const q = state.questions.find(x => x.id === a.questionId);

    return q ? (q.subject + '|' + (q.topic || 'General')) : null;

  }).filter(Boolean));



  // Extract all unique chapters

  const allChapters = new Set();

  state.questions.forEach(q => {

    if (q && q.subject && q.topic) {

      allChapters.add(q.subject + '|' + q.topic);

    }

  });



  const totalChapCount = Math.max(87, allChapters.size);

  const touchedCount = attemptedMap.size;

  const pct = Math.min(100, Math.round((touchedCount / totalChapCount) * 100));



  // Find unexplored chapters

  const unexplored = Array.from(allChapters).filter(c => !attemptedMap.has(c)).slice(0, 10);



  return `

    <div class="syllabus-coverage-card">

      <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px">

        <div>

          <div style="font-size:15px;font-weight:700">🗺️ Official IIT Madras 87-Chapter Syllabus Coverage</div>

          <div style="font-size:11px;color:var(--text-muted);margin-top:2px">Audit your syllabus depth across all 13 GATE CS subjects</div>

        </div>

        <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">

          <button class="btn btn-secondary btn-sm" onclick="printSyllabusWallSheet()" style="font-size:11px;padding:3px 8px" type="button" title="Print 1-Page Physical Wall Poster">🖨️ 1-Page Wall Sheet</button>

          <span style="font-size:14px;font-weight:800;color:var(--accent)">${pct}% Coverage</span>

          <span style="font-size:11px;color:var(--text-muted)">(${touchedCount}/${totalChapCount} Chapters)</span>

        </div>

      </div>

      <div class="syllabus-coverage-bar">

        <div class="syllabus-coverage-fill" style="width:${pct}%"></div>

      </div>

      ${unexplored.length ? `

        <div style="font-size:12px;font-weight:700;color:var(--text-secondary);margin-top:8px">⚠️ Unexplored Topics (Zero Attempts):</div>

        <div class="unexplored-chips-grid">

          ${unexplored.map(c => {

            const [sub, top] = c.split('|');

            return `<div class="unexplored-chip" onclick="drillUnexploredChapters('${sub.replace(/'/g, "\\'")}', '${top.replace(/'/g, "\\'")}')" title="Practice ${top} (${sub})">

              <span>${sub.split(' ').slice(-1)[0]}: ${top}</span>

            </div>`;

          }).join('')}

        </div>

      ` : '<div style="font-size:12px;color:var(--green)">🎉 Magnificent! You have practiced every chapter of the official GATE syllabus!</div>'}

    </div>`;

}



function drillUnexploredChapters(sub, topic) {

  navigate('practice', { subject: sub, topic: topic, status: 'unattempted' });

}



// ════════════════════════════════════════════════════════════════

// 🔄 CONVERT MISTAKES INTO CUSTOM FLASHCARDS

// ════════════════════════════════════════════════════════════════

function convertMistakesToFlashcards() {

  const { unresolved } = getMistakeData();

  if (!unresolved.length) {

    showToast('No unresolved mistakes in vault! 🎉', 'success');

    return;

  }



  state.customMistakeCards = unresolved.map((item, idx) => {

    const q = item.q;

    const labels = ['A', 'B', 'C', 'D', 'E'];

    const corrAns = q.type === 'nat' ? `${q.correct[0]}` : q.correct.map(i => labels[i]).join(', ');

    return {

      id: `mistake-card-${q.id}`,

      subject: q.subject,

      topic: q.topic || 'Mistake Vault',

      title: `Mistake #${idx + 1}: ${q.topic || q.subject}`,

      question: q.question,

      hintText: `Correct Answer: ${corrAns}. Error Tag: ${state.errorTags?.[q.id] || 'Conceptual'}`,

      formulaHTML: `

        <div style="margin-bottom:8px"><strong>Correct Key:</strong> ${corrAns}</div>

        <div style="font-size:13px;line-height:1.7;margin-bottom:8px">${q.explanation || 'Review the conceptual principle carefully.'}</div>

        <div style="font-size:11px;color:var(--red)">⚠️ Personal Mistake from: ${q.subject}</div>

      `,

      keywords: [q.subject.toLowerCase(), (q.topic||'').toLowerCase()]

    };

  });



  saveCache();

  openFormulaFlashcardsModal(state.customMistakeCards[0].id);

  showToast(`Converted ${unresolved.length} mistakes into interactive flashcards! 🔄`, 'success', 3000);

}



// ════════════════════════════════════════════════════════════════

// ⚡ TIMED SECTION SPRINTS (SUBJECT TEST GENERATOR)

// ════════════════════════════════════════════════════════════════

function openSprintModal() {

  const modal = document.getElementById('sprint-modal');

  const backdrop = document.getElementById('sprint-modal-backdrop');

  const body = document.getElementById('sprint-modal-body');

  if (!modal || !body) return;



  body.innerHTML = `

    <div class="sprint-option-row">

      <label>Select Subject</label>

      <select class="filter-select" id="sprint-sub-select" style="width:100%">

        <option value="all">Full GATE CS (Mixed Sprint)</option>

        ${SUBJECTS.map(s => `<option value="${s.name}">${s.name}</option>`).join('')}

      </select>

    </div>

    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:14px">

      <div class="sprint-option-row">

        <label>Question Count</label>

        <select class="filter-select" id="sprint-count-select" style="width:100%">

          <option value="10">10 Questions</option>

          <option value="15" selected>15 Questions (Standard Section)</option>

          <option value="20">20 Questions</option>

          <option value="25">25 Questions</option>

        </select>

      </div>

      <div class="sprint-option-row">

        <label>Time Limit</label>

        <select class="filter-select" id="sprint-time-select" style="width:100%">

          <option value="15">15 Minutes (Speed Run)</option>

          <option value="30" selected>30 Minutes (Recommended)</option>

          <option value="45">45 Minutes (Thorough Analysis)</option>

        </select>

      </div>

    </div>

    <div class="sprint-option-row">

      <label>Difficulty Tier</label>

      <select class="filter-select" id="sprint-diff-select" style="width:100%">

        <option value="all">Balanced GATE CS (Easy + Medium + Hard)</option>

        <option value="easy">Foundational (Easy)</option>

        <option value="medium">Standard GATE (Medium)</option>

        <option value="hard">Rank Booster (Hard)</option>

      </select>

    </div>

    <div style="display:flex;gap:10px;justify-content:flex-end;margin-top:18px">

      <button class="btn btn-secondary btn-sm" onclick="toggleSprintModal(false)" type="button">Cancel</button>

      <button class="btn btn-primary btn-sm" onclick="handleLaunchSprintFromModal()" type="button">⚡ Launch Sprint Exam</button>

    </div>`;



  modal.classList.add('active');

  backdrop?.classList.add('active');

}



function toggleSprintModal(open) {

  document.getElementById('sprint-modal')?.classList.toggle('active', !!open);

  document.getElementById('sprint-modal-backdrop')?.classList.toggle('active', !!open);

}



function handleLaunchSprintFromModal() {

  const sub = document.getElementById('sprint-sub-select')?.value || 'all';

  const cnt = parseInt(document.getElementById('sprint-count-select')?.value || '15', 10);

  const time = parseInt(document.getElementById('sprint-time-select')?.value || '30', 10);

  const diff = document.getElementById('sprint-diff-select')?.value || 'all';

  toggleSprintModal(false);

  launchSectionSprint(sub, cnt, time, diff);

}



function launchSectionSprint(sub, qCount, durationMins, difficulty) {

  let pool = [...state.questions];

  if (sub !== 'all') pool = pool.filter(q => q.subject === sub);

  if (difficulty !== 'all') pool = pool.filter(q => q.difficulty === difficulty);



  if (!pool.length) {

    showToast('No matching questions found for this sprint', 'warning');

    return;

  }



  const selected = shuffleArr(pool).slice(0, Math.min(qCount, pool.length));

  const sprintId = `sprint-${Date.now()}`;

  const sprintMock = {

    id: sprintId,

    name: `⚡ ${sub === 'all' ? 'GATE CS' : sub} Sprint (${selected.length} Qs • ${durationMins}m)`,

    questions: selected.length,

    duration: durationMins,

    marks: selected.reduce((s, q) => s + (q.marks || 1), 0),

    isSprint: true

  };



  state.activeTest = {

    mockId: sprintId,

    mock: sprintMock,

    questions: selected,

    currentQ: 0,

    answers: new Array(selected.length).fill(null),

    reviews: new Array(selected.length).fill(false),

    timeLeft: durationMins * 60,

    timePerQ: new Array(selected.length).fill(0),

    startTime: Date.now(),

    tabSwitches: 0,

    submitted: false

  };



  document.getElementById('test-overlay').classList.add('active');

  renderTestMode();

  startMockTimer();

  showToast(`⚡ Sprint started: ${selected.length} Qs in ${durationMins} mins!`, 'info', 3000);

}



// ════════════════════════════════════════════════════════════════

// ⚖️ MOCK VS MOCK SIDE-BY-SIDE COMPARISON

// ════════════════════════════════════════════════════════════════

function openCompareModal() {

  const modal = document.getElementById('compare-modal');

  const backdrop = document.getElementById('compare-modal-backdrop');

  const body = document.getElementById('compare-modal-body');

  if (!modal || !body) return;



  const sessions = state.testSessions;

  if (sessions.length < 2) {

    showToast('Complete at least 2 mock tests to enable side-by-side comparison', 'warning');

    return;

  }



  body.innerHTML = `

    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:14px">

      <div>

        <label style="font-size:11px;font-weight:700;color:var(--text-muted)">Baseline Test (A)</label>

        <select class="filter-select" id="compare-test-a" onchange="updateComparisonView()" style="width:100%">

          ${sessions.map((s, i) => `<option value="${i}" ${i === 0 ? 'selected' : ''}>${s.name} (${s.percentage}%)</option>`).join('')}

        </select>

      </div>

      <div>

        <label style="font-size:11px;font-weight:700;color:var(--text-muted)">Comparison Test (B)</label>

        <select class="filter-select" id="compare-test-b" onchange="updateComparisonView()" style="width:100%">

          ${sessions.map((s, i) => `<option value="${i}" ${i === sessions.length - 1 ? 'selected' : ''}>${s.name} (${s.percentage}%)</option>`).join('')}

        </select>

      </div>

    </div>

    <div id="compare-results-container"></div>`;



  modal.classList.add('active');

  backdrop?.classList.add('active');

  updateComparisonView();

}



function toggleCompareModal(open) {

  document.getElementById('compare-modal')?.classList.toggle('active', !!open);

  document.getElementById('compare-modal-backdrop')?.classList.toggle('active', !!open);

}



function updateComparisonView() {

  const container = document.getElementById('compare-results-container');

  const idxA = parseInt(document.getElementById('compare-test-a')?.value || '0', 10);

  const idxB = parseInt(document.getElementById('compare-test-b')?.value || '1', 10);

  const sA = state.testSessions[idxA];

  const sB = state.testSessions[idxB];

  if (!container || !sA || !sB) return;



  const deltaScore = Math.round((sB.score - sA.score) * 10) / 10;

  const deltaPct = sB.percentage - sA.percentage;



  container.innerHTML = `

    <table class="compare-table">

      <thead>

        <tr>

          <th>Metric</th>

          <th>Test A (${sA.name.slice(0, 20)}...)</th>

          <th>Test B (${sB.name.slice(0, 20)}...)</th>

          <th>Delta (B - A)</th>

        </tr>

      </thead>

      <tbody>

        <tr>

          <td><strong>Marks Scored</strong></td>

          <td>${sA.score}/${sA.maxScore}</td>

          <td>${sB.score}/${sB.maxScore}</td>

          <td style="color:${deltaScore >= 0 ? 'var(--green)' : 'var(--red)'};font-weight:700">${deltaScore >= 0 ? '+' : ''}${deltaScore}m</td>

        </tr>

        <tr>

          <td><strong>Percentage</strong></td>

          <td>${sA.percentage}%</td>

          <td>${sB.percentage}%</td>

          <td style="color:${deltaPct >= 0 ? 'var(--green)' : 'var(--red)'};font-weight:700">${deltaPct >= 0 ? '+' : ''}${deltaPct}%</td>

        </tr>

        <tr>

          <td><strong>Correct Qs</strong></td>

          <td>${sA.correct}</td>

          <td>${sB.correct}</td>

          <td>${sB.correct - sA.correct >= 0 ? '+' : ''}${sB.correct - sA.correct}</td>

        </tr>

        <tr>

          <td><strong>Wrong Qs</strong></td>

          <td>${sA.wrong}</td>

          <td>${sB.wrong}</td>

          <td>${sB.wrong - sA.wrong}</td>

        </tr>

        <tr>

          <td><strong>Time Taken</strong></td>

          <td>${fmtH(sA.timeTaken || 0)}</td>

          <td>${fmtH(sB.timeTaken || 0)}</td>

          <td>${(sB.timeTaken || 0) > (sA.timeTaken || 0) ? '+' : ''}${Math.round(((sB.timeTaken||0)-(sA.timeTaken||0))/60)}m</td>

        </tr>

      </tbody>

    </table>`;

}



// ════════════════════════════════════════════════════════════════

// 🧘 ZEN / DISTRACTION-FREE MODE

// ════════════════════════════════════════════════════════════════

function toggleZenMode(force) {

  state.zenMode = typeof force === 'boolean' ? force : !state.zenMode;

  document.body.classList.toggle('zen-mode', state.zenMode);

  showToast(state.zenMode

    ? 'Zen Mode Enabled 🧘 (Press Z or Esc to return)'

    : 'Zen Mode Disabled', 'info', 2000);

}



// ════════════════════════════════════════════════════════════════

// 📦 1-CLICK PROFILE BACKUP & RESTORE (.gatebackup)

// ════════════════════════════════════════════════════════════════

function exportGateProfileBackup() {

  const profile = {

    version: '6.0',

    exportDate: new Date().toISOString(),

    timestamp: Date.now(),

    uid: uid(),

    attempts: state.attempts || [],

    testSessions: state.testSessions || [],

    srsQueue: state.srsQueue || {},

    bookmarks: Array.from(state.bookmarks || []),

    questionNotes: state.questionNotes || {},

    errorTags: state.errorTags || {},

    studyPlannerTargets: state.studyPlannerTargets || [],

    playlists: state.playlists || {},

    dailyGoal: state.dailyGoal || 20,

    themeMode: state.themeMode || 'dark',

    customMistakeCards: state.customMistakeCards || []

  };



  const blob = new Blob([JSON.stringify(profile, null, 2)], { type: 'application/json' });

  const a = document.createElement('a');

  a.href = URL.createObjectURL(blob);

  a.download = `gate_cse_profile_backup_${new Date().toISOString().slice(0, 10)}.gatebackup`;

  document.body.appendChild(a);

  a.click();

  document.body.removeChild(a);

  showToast('Profile backup (.gatebackup) exported successfully! 📦', 'success');

}



function triggerRestoreProfileBackup() {

  document.getElementById('restore-profile-backup-input')?.click();

}



function handleRestoreProfileBackupFile(event) {

  const file = event.target.files?.[0];

  if (!file) return;

  const reader = new FileReader();

  reader.onload = async e => {

    try {

      const data = JSON.parse(e.target.result);

      if (Array.isArray(data.attempts)) state.attempts = data.attempts;

      if (Array.isArray(data.testSessions)) state.testSessions = data.testSessions;

      if (data.srsQueue) state.srsQueue = data.srsQueue;

      if (Array.isArray(data.bookmarks)) state.bookmarks = new Set(data.bookmarks);

      if (data.questionNotes) state.questionNotes = data.questionNotes;

      if (data.errorTags) state.errorTags = data.errorTags;

      if (data.studyPlannerTargets) state.studyPlannerTargets = data.studyPlannerTargets;

      if (data.playlists) state.playlists = data.playlists;

      if (data.dailyGoal) state.dailyGoal = data.dailyGoal;

      if (data.themeMode) applyThemeMode(data.themeMode);

      if (data.customMistakeCards) state.customMistakeCards = data.customMistakeCards;



      saveCache();

      updateSidebarSubjectProgress();

      renderPage(state.currentPage);

      showToast('Profile restored successfully! All data recovered. ✅', 'success', 3500);

    } catch(err) {

      showToast('Failed to parse backup file. Please select a valid .gatebackup file.', 'error');

    }

  };

  reader.readAsText(file);

}



// Backward compatibility aliases for verification suites

const showMockRatingMatrix = toggleCalibrationTable;

const closeMockModal = toggleCalibrationTable;



async function init() {

  setupNetworkListeners();

  setupMobileMenu();

  setupKeyboardShortcuts();



  const isGuestMode = new URLSearchParams(window.location.search).get('guest') === '1' ||
                      (typeof sessionStorage !== 'undefined' && sessionStorage.getItem('gate_is_guest') === '1');
  if (isGuestMode) {
    state.isGuest = true;
    setSyncStatus(navigator.onLine ? 'online' : 'offline');
    const ls = document.getElementById('loading-screen');
    if (ls) ls.style.display = 'none';
    const pc = document.getElementById('page-content');
    if (pc) pc.classList.remove('hidden');
    await continueAsGuest();
    return;
  }



  // If loading screen is still visible after 1.5s (due to slow network/offline), show guest button

  setTimeout(() => {
    const btn = document.getElementById('loading-guest-btn');
    if (btn && document.getElementById('loading-screen')?.style.display !== 'none') {
      btn.style.display = 'inline-flex';
      const triggerLg = (e) => {
        if (e) { e.preventDefault(); e.stopPropagation(); }
        continueAsGuest(btn);
      };
      btn.addEventListener('click', triggerLg);
      btn.addEventListener('touchend', triggerLg);
    }
  }, 1500);



  if (USE_FB && auth) {

    setSyncStatus('connecting');



    // Safety timeout: If Firebase auth hangs or takes > 3.5s, fall back to login page

    const authTimeoutTimer = setTimeout(() => {
      const ls = document.getElementById('loading-screen');
      if (ls && ls.style.display !== 'none') {
        if (state.isGuest || (typeof sessionStorage !== 'undefined' && sessionStorage.getItem('gate_is_guest') === '1')) {
          ls.style.display = 'none';
          document.getElementById('page-content')?.classList.remove('hidden');
          return;
        }
        console.warn('[Auth] Auth check timeout, displaying login screen');
        ls.style.display = 'none';
        document.getElementById('page-content')?.classList.remove('hidden');
        renderLoginPage();
      }
    }, 3500);



    // Handle Google redirect result BEFORE setting up onAuthStateChanged

    // Use timeout to prevent hanging when offline or slow connection

    let redirectError = null;

    try {

      await Promise.race([

        getRedirectResult(auth),

        new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), 4000))

      ]);

    } catch(e) {

      if (e.message !== 'timeout') {

        redirectError = e;

        console.warn('Redirect result error:', e.code, e.message);

      }

    }



    onAuthStateChanged(auth, async user => {

      clearTimeout(authTimeoutTimer);

      if (user) {
        state.isGuest = false;
        try { sessionStorage.removeItem('gate_is_guest'); } catch(e){}
        removeLoginPage();

        await bootApp(user);

      } else {
        if (state.isGuest || (typeof sessionStorage !== 'undefined' && sessionStorage.getItem('gate_is_guest') === '1')) {
          const ls = document.getElementById('loading-screen');
          if (ls) ls.style.display = 'none';
          const pc = document.getElementById('page-content');
          if (pc) pc.classList.remove('hidden');
          return;
        }

        // Logged out — show login page

        teardownListeners();

        state.attempts=[]; state.testSessions=[];

        document.getElementById('loading-screen').style.display = 'none';

        document.getElementById('page-content').classList.remove('hidden');

        renderLoginPage();



        // If Google redirect failed, show a clear error message

        if (redirectError) {

          setTimeout(() => {

            const err = document.getElementById('auth-error');

            if (!err) return;

            if (redirectError.code === 'auth/unauthorized-domain') {

              err.textContent = '⚠️ Google Sign-In failed: this domain is not yet authorized. Please use Email & Password login for now, or wait 5 minutes and try again.';

            } else {

              err.textContent = '⚠️ Google Sign-In failed: ' + (redirectError.message || redirectError.code);

            }

            err.className = 'auth-error show';

            redirectError = null;

          }, 300);

        }

      }

    });

  } else {

    // No Firebase — boot directly as guest
    state.isGuest = true;

    setSyncStatus(navigator.onLine ? 'online' : 'offline');

    await bootApp(null);

  }

}



if (document.readyState === 'loading') {

  document.addEventListener('DOMContentLoaded', init);

} else {

  init();

}



// ═════════════════════════════════════════════════════════════════════════════

// 1. POST-EXAM LOSS DIAGNOSIS & ROOT-CAUSE ERROR TAGGING ENGINE

// ═════════════════════════════════════════════════════════════════════════════

function setErrorTag(qId, tag) {

  if (!qId) return;

  if (!state.errorTags) state.errorTags = {};

  if (state.errorTags[qId] === tag) {

    delete state.errorTags[qId];

  } else {

    state.errorTags[qId] = tag;

  }

  try {

    localStorage.setItem('gate_question_error_tags', JSON.stringify(state.errorTags));

  } catch(e) {}

  

  // Update error tag button UI in place

  const grp = document.getElementById(`error-tag-group-${qId}`);

  if (grp) {

    grp.outerHTML = buildErrorTagButtonsHTML(qId, state.errorTags[qId]);

  }

  

  // Update loss diagnosis box if present

  const lossBox = document.getElementById('loss-diagnosis-container');

  if (lossBox && state.activeTestResults) {

    const { session, questions, answers } = state.activeTestResults;

    lossBox.outerHTML = buildLossDiagnosisHTML(session, questions, answers);

  }

}



function buildErrorTagButtonsHTML(qId, currentTag) {

  const tags = [

    { id: 'silly', label: '🟡 Silly Error' },

    { id: 'misread', label: '🔴 Misread Q' },

    { id: 'concept', label: '🟣 Concept Gap' },

    { id: 'formula', label: '🔵 Formula Forgot' },

    { id: 'time', label: '⏳ Time Rushed' }

  ];

  return `

    <div class="error-tag-group" id="error-tag-group-${qId}">

      <span class="error-tag-prompt">Root Cause:</span>

      ${tags.map(t => `

        <button class="error-tag-btn ${t.id} ${currentTag === t.id ? 'active' : ''}" 

          onclick="setErrorTag('${qId}', '${t.id}')" 

          title="Tag error as ${t.label}" 

          type="button">

          ${t.label}

        </button>

      `).join('')}

    </div>

  `;

}



function getLossDiagnosis(session, questions, answers) {

  let sillyLost = 0, misreadLost = 0, conceptLost = 0, formulaLost = 0, timeLost = 0, untaggedLost = 0;

  let totalNegativeBleed = 0;

  let wrongCount = 0;



  (questions || []).forEach((q, i) => {

    const a = (answers && answers[i] !== undefined) ? answers[i] : null;

    const skip = a === null || a === undefined || (Array.isArray(a) && !a.length);

    let ok = false;

    if (!skip) {

      if (q.type === 'nat') {

        const v = parseFloat(a), e = q.correct[0];

        ok = v >= (q.natRange?.min ?? e) && v <= (q.natRange?.max ?? e);

      } else {

        const s = (Array.isArray(a) ? a : [a]).sort((x, y) => x - y);

        const e = [...q.correct].sort((x, y) => x - y);

        ok = s.length === e.length && s.every((v, idx) => v === e[idx]);

      }

    }



    if (!ok) {

      wrongCount++;

      const qMarks = q.marks || 1;

      const neg = (!skip && q.type !== 'nat') ? (qMarks === 2 ? 2/3 : 1/3) : 0;

      totalNegativeBleed += neg;

      const loss = qMarks + neg;

      const tag = state.errorTags?.[q.id];



      if (tag === 'silly') sillyLost += loss;

      else if (tag === 'misread') misreadLost += loss;

      else if (tag === 'concept') conceptLost += loss;

      else if (tag === 'formula') formulaLost += loss;

      else if (tag === 'time') timeLost += loss;

      else untaggedLost += loss;

    }

  });



  const unforcedLost = sillyLost + misreadLost;

  const currentScore = session ? session.score : 0;

  const maxScore = session ? session.maxScore : 100;

  const potentialScore = Math.min(maxScore, parseFloat((currentScore + unforcedLost).toFixed(2)));



  return {

    sillyLost: parseFloat(sillyLost.toFixed(2)),

    misreadLost: parseFloat(misreadLost.toFixed(2)),

    conceptLost: parseFloat(conceptLost.toFixed(2)),

    formulaLost: parseFloat(formulaLost.toFixed(2)),

    timeLost: parseFloat(timeLost.toFixed(2)),

    untaggedLost: parseFloat(untaggedLost.toFixed(2)),

    unforcedLost: parseFloat(unforcedLost.toFixed(2)),

    totalNegativeBleed: parseFloat(totalNegativeBleed.toFixed(2)),

    currentScore,

    potentialScore,

    wrongCount

  };

}



function buildLossDiagnosisHTML(session, questions, answers) {

  const diag = getLossDiagnosis(session, questions, answers);

  return `

    <div class="loss-diagnosis-card" id="loss-diagnosis-container">

      <div class="loss-diagnosis-header">

        <div class="loss-diagnosis-title">

          <span>🎯 Post-Exam Loss Diagnosis & Root Cause Analysis</span>

          <span class="badge" style="background:rgba(245,158,11,0.2);color:#fbbf24;font-size:11px">Mark Bleed Audit</span>

        </div>

        <div class="text-sm text-muted">Tag incorrect questions below to refine root causes</div>

      </div>



      <div class="loss-score-projection-grid">

        <div class="loss-projection-box">

          <div class="loss-proj-lbl">Actual Score</div>

          <div class="loss-proj-val" style="color:var(--text-primary)">${diag.currentScore}</div>

        </div>

        <div class="loss-projection-box" style="border-color:rgba(34,197,94,0.4)">

          <div class="loss-proj-lbl" style="color:#22c55e">Potential Score (No Unforced Slips)</div>

          <div class="loss-proj-val" style="color:#22c55e">+${diag.unforcedLost} → ${diag.potentialScore}</div>

        </div>

        <div class="loss-projection-box" style="border-color:rgba(239,68,68,0.4)">

          <div class="loss-proj-lbl" style="color:#f87171">Negative Marks Bleed (MCQs)</div>

          <div class="loss-proj-val" style="color:#f87171">-${diag.totalNegativeBleed} M</div>

        </div>

      </div>



      <div class="loss-tag-chips-grid">

        <div class="loss-tag-chip-stat">

          <span class="loss-tag-chip-name" style="color:#fbbf24">🟡 Silly Errors</span>

          <span class="loss-tag-chip-val" style="color:#fbbf24">-${diag.sillyLost} M</span>

        </div>

        <div class="loss-tag-chip-stat">

          <span class="loss-tag-chip-name" style="color:#f87171">🔴 Misread Questions</span>

          <span class="loss-tag-chip-val" style="color:#f87171">-${diag.misreadLost} M</span>

        </div>

        <div class="loss-tag-chip-stat">

          <span class="loss-tag-chip-name" style="color:#c084fc">🟣 Concept Gaps</span>

          <span class="loss-tag-chip-val" style="color:#c084fc">-${diag.conceptLost} M</span>

        </div>

        <div class="loss-tag-chip-stat">

          <span class="loss-tag-chip-name" style="color:#60a5fa">🔵 Formula Forgotten</span>

          <span class="loss-tag-chip-val" style="color:#60a5fa">-${diag.formulaLost} M</span>

        </div>

        <div class="loss-tag-chip-stat">

          <span class="loss-tag-chip-name" style="color:#f472b6">⏳ Time Pressure</span>

          <span class="loss-tag-chip-val" style="color:#f472b6">-${diag.timeLost} M</span>

        </div>

      </div>

    </div>

  `;

}



function setMistakeTagFilter(val) {

  state.mistakeTagFilter = val;

  renderMistakes(document.getElementById('page-content'));

}



// ═════════════════════════════════════════════════════════════════════════════

// 2. GATE PYQ WEIGHTAGE HEATMAP & TOPIC TREND ENGINE

// ═════════════════════════════════════════════════════════════════════════════

function buildGateWeightageHeatmapHTML(pyqs) {

  const chapterStats = new Map();

  const subStats = new Map();

  

  pyqs.forEach(q => {

    const sub = q.subject || 'General';

    const chName = getTopicPYQChapter(q);

    const marks = q.marks || 1;

    const year = parseInt(q.year, 10) || 2020;

    

    // Sub

    if (!subStats.has(sub)) subStats.set(sub, { sub, totalQs: 0, totalMarks: 0, modernMarks: 0 });

    const sObj = subStats.get(sub);

    sObj.totalQs++;

    sObj.totalMarks += marks;

    if (year >= 2015) sObj.modernMarks += marks;



    // Chapter

    const key = `${sub}:::${chName}`;

    if (!chapterStats.has(key)) {

      chapterStats.set(key, { sub, chapter: chName, totalQs: 0, totalMarks: 0, m1: 0, m2: 0, modernQs: 0, questions: [] });

    }

    const cObj = chapterStats.get(key);

    cObj.totalQs++;

    cObj.totalMarks += marks;

    if (marks === 2) cObj.m2++; else cObj.m1++;

    if (year >= 2015) cObj.modernQs++;

    cObj.questions.push(q);

  });



  const sortedChapters = Array.from(chapterStats.values()).sort((a, b) => b.totalMarks - a.totalMarks);

  const sortedSubs = Array.from(subStats.values()).sort((a, b) => (b.modernMarks / 11) - (a.modernMarks / 11));

  const maxSubAvg = Math.max(...sortedSubs.map(s => s.modernMarks / 11), 1);



  return `

    <div class="heatmap-hero">

      <div class="heatmap-hero-text">

        <h2><span>🔥</span> GATE CSE PYQ Weightage Heatmap & Topic Trend Engine</h2>

        <p>

          Data-driven weightage analysis generated across all 2,224 authentic GATE CSE Previous Year Questions (1990–2025). Discover which subjects and chapters yield the highest return on study time for GATE.

        </p>

      </div>

      <div style="display:flex;gap:10px;flex-wrap:wrap">

        <button class="btn btn-primary" onclick="launchHighYieldDrill()" type="button" style="font-weight:700">

          ⚡ Launch High-Yield Drill (Top 15 Topics)

        </button>

        <button class="topic-pyq-tab-btn" onclick="setTopicPyqTab('chapters')" type="button">

          <span>📑</span> Back to Chapters

        </button>

      </div>

    </div>



    <!-- Subject Annual Marks Bar Chart -->

    <div class="card mb-4">

      <div class="card-header">

        <div class="card-title">📊 Average Annual Marks per Subject (GATE 2015–2025 Modern Era)</div>

      </div>

      <div class="heatmap-sub-bars-grid">

        ${sortedSubs.map(s => {

          const avgM = (s.modernMarks / 11).toFixed(1);

          const pct = Math.round(( (s.modernMarks / 11) / maxSubAvg ) * 100);

          return `

            <div class="heatmap-sub-bar-card">

              <div class="heatmap-sub-header">

                <span>${escapeHtml(s.sub)}</span>

                <span style="color:var(--accent)">~${avgM} Marks / Yr</span>

              </div>

              <div class="heatmap-bar-track">

                <div class="heatmap-bar-fill" style="width:${pct}%;background:var(--accent)"></div>

              </div>

              <div class="heatmap-sub-meta">

                <span>${s.totalQs} PYQs Total</span>

                <span>${s.totalMarks} Marks (1990–2025)</span>

              </div>

            </div>

          `;

        }).join('')}

      </div>

    </div>



    <!-- Top High-Yield Chapters Leaderboard -->

    <div class="card">

      <div class="card-header" style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px">

        <div class="card-title">🏆 Top 25 Highest-Yield Syllabus Chapters Ranked by Total GATE Marks</div>

        <span class="badge" style="background:rgba(239,68,68,0.2);color:#f87171">High Priority Revision</span>

      </div>

      <div style="overflow-x:auto">

        <table class="calibration-table" style="width:100%">

          <thead>

            <tr>

              <th>Rank</th>

              <th>Chapter / Topic</th>

              <th>Subject</th>

              <th>Yield Tier</th>

              <th>Total Marks</th>

              <th>PYQs</th>

              <th>1M / 2M Split</th>

              <th>Action</th>

            </tr>

          </thead>

          <tbody>

            ${sortedChapters.slice(0, 25).map((ch, idx) => {

              const tierClass = idx < 10 ? 'yield-critical' : idx < 20 ? 'yield-high' : 'yield-regular';

              const tierLabel = idx < 10 ? '🔥 Critical' : idx < 20 ? '⚡ High' : '📘 Standard';

              return `

                <tr>

                  <td style="font-weight:800;color:var(--text-muted)">#${idx + 1}</td>

                  <td style="font-weight:700;color:var(--text-primary)">${escapeHtml(ch.chapter)}</td>

                  <td><span class="chip" style="font-size:11px">${escapeHtml(ch.sub)}</span></td>

                  <td><span class="yield-badge ${tierClass}">${tierLabel}</span></td>

                  <td style="font-weight:800;color:var(--accent)">${ch.totalMarks} M</td>

                  <td>${ch.totalQs}</td>

                  <td>${ch.m1} × 1M | ${ch.m2} × 2M</td>

                  <td>

                    <button class="btn btn-secondary btn-sm" onclick="startTopicPYQPractice('${escapeHtml(ch.sub)}', '${escapeHtml(ch.chapter)}')" style="padding:2px 8px;font-size:11px" type="button">

                      ▶ Drill

                    </button>

                  </td>

                </tr>

              `;

            }).join('')}

          </tbody>

        </table>

      </div>

    </div>

  `;

}



function launchHighYieldDrill() {

  const pyqs = state.questions.filter(q => q.category === 'pyq');

  const chapterMap = new Map();

  pyqs.forEach(q => {

    const key = `${q.subject || 'General'}:::${getTopicPYQChapter(q)}`;

    if (!chapterMap.has(key)) chapterMap.set(key, []);

    chapterMap.get(key).push(q);

  });

  const sortedKeys = Array.from(chapterMap.keys()).sort((a, b) => chapterMap.get(b).length - chapterMap.get(a).length).slice(0, 15);

  const selected = [];

  sortedKeys.forEach(k => {

    const list = chapterMap.get(k);

    if (list && list.length) {

      selected.push(list[Math.floor(Math.random() * list.length)]);

    }

  });

  if (selected.length) {

    startPracticeMode(selected);

    showToast(`⚡ Loaded 15-Question High-Yield PYQ Drill!`, 'success');

  }

}



// ═════════════════════════════════════════════════════════════════════════════

// 3. SPEED VS ACCURACY 4-QUADRANT MATRIX (TIME-SINK DETECTOR)

// ═════════════════════════════════════════════════════════════════════════════

function buildQuadrantAnalysisHTML() {

  const attempts = state.attempts || [];

  if (!attempts.length) {

    return '';

  }



  const THRESHOLD_SEC = 100;

  let q1SweetSpot = 0;   // Fast & Correct

  let q2SlowCorrect = 0; // Slow & Correct

  let q3RashError = 0;   // Fast & Incorrect (<= 60s)

  let q4BlackHole = 0;   // Slow & Incorrect (>= 180s)

  let blackHoleSec = 0;



  attempts.forEach(att => {

    const sec = att.timeMs ? Math.round(att.timeMs / 1000) : 60;

    if (att.correct) {

      if (sec <= THRESHOLD_SEC) q1SweetSpot++;

      else q2SlowCorrect++;

    } else {

      if (sec <= 60) q3RashError++;

      if (sec >= 180) {

        q4BlackHole++;

        blackHoleSec += sec;

      }

    }

  });



  const blackHoleMin = (blackHoleSec / 60).toFixed(1);



  return `

    <div class="quadrant-matrix-container">

      <div class="quadrant-matrix-header">

        <div>

          <div style="font-size:15px;font-weight:800;color:#fff">⏱️ Speed vs Accuracy Matrix (Quadrant Analysis)</div>

          <div class="text-sm text-muted" style="margin-top:2px">Categorizes your question-solving pacing against correctness to detect time-sink traps.</div>

        </div>

        <span class="badge" style="background:rgba(108,99,255,0.2);color:var(--accent)">Pacing Diagnostics</span>

      </div>



      <div class="quadrant-matrix-grid">

        <!-- Q1: Sweet Spot -->

        <div class="quadrant-card q-sweet-spot">

          <div class="quadrant-card-header">

            <span class="quadrant-card-title" style="color:#22c55e">🟢 Sweet Spot (Fast & Correct)</span>

            <span class="quadrant-card-count" style="color:#22c55e">${q1SweetSpot}</span>

          </div>

          <div class="quadrant-card-desc">Solved in under ${THRESHOLD_SEC}s with 100% accuracy. Confident mastery. Maintain momentum!</div>

        </div>



        <!-- Q2: Slow & Accurate -->

        <div class="quadrant-card q-slow-acc">

          <div class="quadrant-card-header">

            <span class="quadrant-card-title" style="color:#60a5fa">🟡 Under-Confident (Slow & Correct)</span>

            <span class="quadrant-card-count" style="color:#60a5fa">${q2SlowCorrect}</span>

          </div>

          <div class="quadrant-card-desc">Accurate, but took >${THRESHOLD_SEC}s. Conceptual clarity is there, but needs shortcut formulas to save time.</div>

        </div>



        <!-- Q3: Rash Errors -->

        <div class="quadrant-card q-rash-err">

          <div class="quadrant-card-header">

            <span class="quadrant-card-title" style="color:#fbbf24">🟠 Rash Errors (Fast & Wrong)</span>

            <span class="quadrant-card-count" style="color:#fbbf24">${q3RashError}</span>

          </div>

          <div class="quadrant-card-desc">Answered in under 60s and missed. High probability of silly mistakes, misreading NOT/EXCEPT, or premature clicks.</div>

        </div>



        <!-- Q4: The Black Hole -->

        <div class="quadrant-card q-black-hole">

          <div class="quadrant-card-header">

            <span class="quadrant-card-title" style="color:#f87171">🔴 The Black Hole (Slow & Wrong)</span>

            <span class="quadrant-card-count" style="color:#f87171">${q4BlackHole}</span>

          </div>

          <div class="quadrant-card-desc">Double-loss danger! Spent >3 minutes per question AND incurred negative marks. Must learn to skip these in GATE.</div>

        </div>

      </div>



      ${q4BlackHole > 0 ? `

        <div class="blackhole-alert-banner">

          <span>⚠️ <strong>Time-Sink Warning:</strong> You burned <strong>${blackHoleMin} minutes</strong> on Black Hole questions. Skipping these will save ~${Math.round(q4BlackHole * 1.33)} marks!</span>

          <button class="btn btn-secondary btn-sm" onclick="drillBlackHoleQuestions()" style="font-weight:700;color:#f87171;border-color:rgba(239,68,68,0.4)" type="button">

            🔥 Re-Attempt Black Holes (${q4BlackHole} Qs)

          </button>

        </div>

      ` : ''}

    </div>

  `;

}



function drillBlackHoleQuestions() {

  const attempts = state.attempts || [];

  const blackHoleQIds = new Set(

    attempts.filter(a => !a.correct && a.timeMs >= 180000).map(a => a.questionId)

  );

  const qs = state.questions.filter(q => blackHoleQIds.has(q.id));

  if (qs.length) {

    startPracticeMode(qs.slice(0, 15));

    showToast(`Loaded ${Math.min(15, qs.length)} Black Hole questions with a 2-min drill cap!`, 'info');

  } else {

    showToast('No Black Hole questions recorded yet!', 'info');

  }

}



// ═════════════════════════════════════════════════════════════════════════════

// 4. SMART PLAYLISTS & REVISION BUCKETS

// ═════════════════════════════════════════════════════════════════════════════

function initDefaultPlaylists() {

  if (!state.playlists) state.playlists = {};

  if (!state.playlists['smart-nats']) {

    state.playlists['smart-nats'] = {

      id: 'smart-nats',

      name: '🎯 Tricky NAT Questions',

      desc: 'Numerical Answer Type questions with no negative marks for precise calculation practice.',

      icon: '🎯',

      color: '#3b82f6',

      isSmart: true,

      qIds: []

    };

  }

  if (!state.playlists['smart-high-yield']) {

    state.playlists['smart-high-yield'] = {

      id: 'smart-high-yield',

      name: '🔥 High-Yield Rapid Fire',

      desc: 'Top recurring GATE concepts across Cache, Master Theorem, Relational Algebra, and Subnetting.',

      icon: '🔥',

      color: '#f97316',

      isSmart: true,

      qIds: []

    };

  }

  if (!state.playlists['smart-last-week']) {

    state.playlists['smart-last-week'] = {

      id: 'smart-last-week',

      name: '🚀 Last 7 Days Revision',

      desc: 'Selected high-confidence questions to review in the final countdown week.',

      icon: '🚀',

      color: '#10b981',

      isSmart: false,

      qIds: []

    };

  }

}



function openPlaylistModal(qId) {

  state.activePlaylistModalQ = qId;

  initDefaultPlaylists();

  const body = document.getElementById('playlist-modal-body');

  if (!body) return;



  const pls = Object.values(state.playlists);

  body.innerHTML = `

    <div style="font-size:12px;color:var(--text-secondary);margin-bottom:8px">

      Select playlists to add or remove this question:

    </div>

    ${pls.map(p => {

      const isMember = (p.qIds || []).includes(qId);

      return `

        <label class="playlist-select-item">

          <input type="checkbox" ${isMember ? 'checked' : ''} onchange="toggleQuestionInPlaylist('${p.id}', '${qId}', this.checked)" />

          <span style="font-size:16px">${p.icon}</span>

          <div style="flex:1">

            <div style="font-size:13px;font-weight:700">${escapeHtml(p.name)}</div>

            <div style="font-size:11px;color:var(--text-muted)">${(p.qIds || []).length} questions</div>

          </div>

        </label>

      `;

    }).join('')}

    <div style="margin-top:12px;padding-top:10px;border-top:1px dashed var(--border)">

      <div style="font-size:12px;font-weight:700;margin-bottom:6px">Create New Playlist:</div>

      <div style="display:flex;gap:6px">

        <input type="text" id="new-playlist-input" placeholder="e.g. My Weak Graph Problems" class="search-input" style="flex:1;font-size:12px;padding:5px 8px" />

        <button class="btn btn-primary btn-sm" onclick="handleCreatePlaylistFromModal()" type="button">+ Create</button>

      </div>

    </div>

  `;



  document.getElementById('playlist-modal')?.classList.add('active');

  document.getElementById('playlist-modal-backdrop')?.classList.add('active');

}



function closePlaylistModal() {

  state.activePlaylistModalQ = null;

  document.getElementById('playlist-modal')?.classList.remove('active');

  document.getElementById('playlist-modal-backdrop')?.classList.remove('active');

}



function toggleQuestionInPlaylist(pId, qId, checked) {

  initDefaultPlaylists();

  const p = state.playlists[pId];

  if (!p) return;

  if (!p.qIds) p.qIds = [];

  if (checked) {

    if (!p.qIds.includes(qId)) p.qIds.push(qId);

    showToast(`Added to "${p.name}"`, 'success');

  } else {

    p.qIds = p.qIds.filter(id => id !== qId);

    showToast(`Removed from "${p.name}"`, 'info');

  }

  try {

    localStorage.setItem('gate_custom_playlists', JSON.stringify(state.playlists));

  } catch(e) {}

}



function handleCreatePlaylistFromModal() {

  const inp = document.getElementById('new-playlist-input');

  const name = inp?.value?.trim();

  if (!name) return;

  const id = 'pl_' + Date.now();

  state.playlists[id] = {

    id,

    name,

    desc: 'Custom playlist created by user',

    icon: '📁',

    color: '#8b5cf6',

    isSmart: false,

    qIds: state.activePlaylistModalQ ? [state.activePlaylistModalQ] : []

  };

  try {

    localStorage.setItem('gate_custom_playlists', JSON.stringify(state.playlists));

  } catch(e) {}

  showToast(`Created playlist "${name}"!`, 'success');

  if (state.activePlaylistModalQ) {

    openPlaylistModal(state.activePlaylistModalQ);

  }

}



function deletePlaylist(pId) {

  if (confirm('Delete this custom playlist?')) {

    delete state.playlists[pId];

    try {

      localStorage.setItem('gate_custom_playlists', JSON.stringify(state.playlists));

    } catch(e) {}

    renderPlaylists();

    showToast('Playlist deleted', 'info');

  }

}



function startPlaylistPractice(pId, shuffle = false) {

  initDefaultPlaylists();

  const p = state.playlists[pId];

  if (!p) return;

  let qs = [];

  if (p.isSmart && p.id === 'smart-nats') {

    qs = state.questions.filter(q => q.type === 'nat').slice(0, 25);

  } else if (p.isSmart && p.id === 'smart-high-yield') {

    const pyqs = state.questions.filter(q => q.category === 'pyq');

    const chMap = new Map();

    pyqs.forEach(q => {

      const k = getTopicPYQChapter(q);

      if (!chMap.has(k)) chMap.set(k, []);

      chMap.get(k).push(q);

    });

    const topKeys = Array.from(chMap.keys()).slice(0, 15);

    topKeys.forEach(k => {

      const l = chMap.get(k);

      if (l && l.length) qs.push(l[0]);

    });

  } else {

    const qIds = new Set(p.qIds || []);

    qs = state.questions.filter(q => qIds.has(q.id));

  }



  if (!qs.length) {

    showToast('Playlist has no questions yet! Click 🗂️ on any question to add it.', 'warning');

    return;

  }

  if (shuffle) {

    qs = [...qs].sort(() => Math.random() - 0.5);

  }

  startPracticeMode(qs);

  showToast(`▶ Starting Practice: ${p.name} (${qs.length} Qs)`, 'success');

}



function renderPlaylists(c) {

  if (!c) c = document.getElementById('page-content');

  if (!c) return;

  initDefaultPlaylists();



  const pls = Object.values(state.playlists);

  const attMap = new Map(state.attempts.map(a => [a.questionId, a]));



  c.innerHTML = `

    <div class="playlists-hero">

      <div>

        <h2 style="font-size:20px;font-weight:800;color:#10b981;margin-bottom:6px">🗂️ Smart Playlists & Revision Buckets</h2>

        <p style="font-size:13px;color:var(--text-secondary);max-width:650px;line-height:1.5">

          Curate custom question collections for rapid revision, targeted drills, and final-week sprints. Add any question to a playlist with one click.

        </p>

      </div>

      <button class="btn btn-primary" onclick="openPlaylistModal('')" style="font-weight:700" type="button">

        ➕ Create New Playlist

      </button>

    </div>



    <div class="playlists-grid">

      ${pls.map(p => {

        let count = (p.qIds || []).length;

        if (p.isSmart && p.id === 'smart-nats') count = state.questions.filter(q => q.type === 'nat').length;

        if (p.isSmart && p.id === 'smart-high-yield') count = 15;

        

        const solved = (p.qIds || []).filter(id => attMap.has(id)).length;

        const pct = count > 0 ? Math.round((solved / count) * 100) : 0;



        return `

          <div class="playlist-card" style="border-top:3px solid ${p.color}">

            <div class="playlist-card-top">

              <div class="playlist-card-title-row">

                <div class="playlist-title">

                  <span>${p.icon}</span>

                  <span>${escapeHtml(p.name)}</span>

                </div>

                ${p.isSmart ? `<span class="badge" style="background:rgba(16,185,129,0.2);color:#10b981;font-size:10px">SMART</span>` : ''}

              </div>

              <div class="playlist-desc">${escapeHtml(p.desc)}</div>

              

              <div style="display:flex;justify-content:space-between;font-size:11px;color:var(--text-muted);margin-bottom:6px">

                <span>${count} Questions</span>

                <span>${solved} Solved (${pct}%)</span>

              </div>

              <div class="topic-progress-bar-wrap" style="height:6px">

                <div class="topic-progress-bar-fill" style="width:${pct}%;background:${p.color}"></div>

              </div>

            </div>



            <div class="playlist-actions-row">

              <button class="btn btn-primary btn-sm" onclick="startPlaylistPractice('${p.id}', false)" style="flex:1" type="button">

                ▶ Practice

              </button>

              <button class="btn btn-secondary btn-sm" onclick="startPlaylistPractice('${p.id}', true)" title="Shuffle order" type="button">

                🔀

              </button>

              ${!p.isSmart ? `

                <button class="btn btn-danger btn-sm" onclick="deletePlaylist('${p.id}')" title="Delete playlist" type="button">

                  🗑

                </button>

              ` : ''}

            </div>

          </div>

        `;

      }).join('')}

    </div>

  `;

  renderMath(c);

}



// ═════════════════════════════════════════════════════════════════════════════

// 5. MULTI-METHOD EXPLANATIONS & STUDENT SHORTCUT NOTES

// ═════════════════════════════════════════════════════════════════════════════

function setMethodTab(qId, methodKey) {

  if (!state.activeMethodTab) state.activeMethodTab = {};

  state.activeMethodTab[qId] = methodKey;

  const pane1 = document.getElementById(`method-pane-std-${qId}`);

  const pane2 = document.getElementById(`method-pane-short-${qId}`);

  const btn1 = document.getElementById(`method-btn-std-${qId}`);

  const btn2 = document.getElementById(`method-btn-short-${qId}`);

  if (pane1 && pane2) {

    if (methodKey === 'short') {

      pane1.style.display = 'none';

      pane2.style.display = 'block';

      btn1?.classList.remove('active');

      btn2?.classList.add('active');

    } else {

      pane1.style.display = 'block';

      pane2.style.display = 'none';

      btn1?.classList.add('active');

      btn2?.classList.remove('active');

    }

  }

}



function buildMultiMethodExplanationHTML(q) {

  if (!q) return '';

  const expl = q.explanation || 'No explanation provided.';

  const topic = (q.topic || '').toLowerCase();



  let shortcutInsight = '';

  if (topic.includes('master') || expl.includes('Master') || expl.includes('T(n) =')) {

    shortcutInsight = `

      <div style="background:rgba(245,158,11,0.1);border-left:3px solid #f59e0b;padding:8px 10px;margin-bottom:8px;border-radius:4px">

        <strong>⚡ Master's Shortcut:</strong> Compare $f(n)$ with $n^{\\log_b a}$.

        <br/>• If $f(n) = O(n^{\\log_b a - \\epsilon}) \implies T(n) = \Theta(n^{\\log_b a})$.

        <br/>• If $f(n) = \Theta(n^{\\log_b a}) \implies T(n) = \Theta(n^{\\log_b a} \log n)$.

        <br/>• If $f(n) = \Omega(n^{\\log_b a + \\epsilon}) \implies T(n) = \Theta(f(n))$.

      </div>

    `;

  } else if (topic.includes('cache') || expl.includes('cache') || expl.includes('tag')) {

    shortcutInsight = `

      <div style="background:rgba(59,130,246,0.1);border-left:3px solid #3b82f6;padding:8px 10px;margin-bottom:8px;border-radius:4px">

        <strong>⚡ Cache Address Field Shortcut:</strong>

        <br/>Address Bits = Tag Bits + Set/Index Bits + Block Offset.

        <br/>$\\text{Index Bits} = \log_2(\\text{Number of Sets})$, $\\text{Offset Bits} = \log_2(\\text{Block Size in Bytes})$.

      </div>

    `;

  } else if (topic.includes('pipeline') || expl.includes('pipeline') || expl.includes('hazard')) {

    shortcutInsight = `

      <div style="background:rgba(16,185,129,0.1);border-left:3px solid #10b981;padding:8px 10px;margin-bottom:8px;border-radius:4px">

        <strong>⚡ Pipelining Speedup Shortcut:</strong>

        <br/>$\\text{Speedup } S = \frac{n \cdot k}{k + n - 1}$ for $n$ instructions on $k$ stages. For large $n$, $S \to k$.

      </div>

    `;

  } else if (topic.includes('subnet') || expl.includes('CIDR') || expl.includes('subnet')) {

    shortcutInsight = `

      <div style="background:rgba(168,85,247,0.1);border-left:3px solid #a855f7;padding:8px 10px;margin-bottom:8px;border-radius:4px">

        <strong>⚡ Subnetting Shortcut:</strong>

        <br/>Usable Hosts = $2^{(32 - \\text{prefix})} - 2$ (subtract Network & Broadcast).

      </div>

    `;

  }



  const activeMethod = (state.activeMethodTab && state.activeMethodTab[q.id]) || 'std';



  return `

    <div class="multi-method-tabs">

      <button class="method-tab-btn ${activeMethod === 'std' ? 'active' : ''}" id="method-btn-std-${q.id}" onclick="setMethodTab('${q.id}', 'std')" type="button">

        📘 Method 1: Standard Solution

      </button>

      <button class="method-tab-btn ${activeMethod === 'short' ? 'active' : ''}" id="method-btn-short-${q.id}" onclick="setMethodTab('${q.id}', 'short')" type="button">

        ⚡ Method 2: Shortcut / Direct Rule

      </button>

    </div>

    <div class="method-content-pane" id="method-pane-std-${q.id}" style="display:${activeMethod === 'std' ? 'block' : 'none'}">

      ${formatQuestionContent(expl)}

    </div>

    <div class="method-content-pane" id="method-pane-short-${q.id}" style="display:${activeMethod === 'short' ? 'block' : 'none'}">

      ${shortcutInsight ? shortcutInsight : `<p style="color:var(--text-secondary);font-size:12px;margin-bottom:6px">Direct formula and elimination check: verify boundary conditions and option substitution.</p>`}

      ${formatQuestionContent(expl)}

    </div>

  `;

}



function saveStudentQuestionNote(qId, text) {

  if (!state.questionNotes) state.questionNotes = {};

  state.questionNotes[qId] = text;

  try {

    localStorage.setItem('gate_question_notes', JSON.stringify(state.questionNotes));

  } catch(e) {}

  const prev = document.getElementById(`student-note-preview-${qId}`);

  if (prev) {

    prev.innerHTML = text ? `<strong>Preview:</strong> ${formatQuestionContent(text)}` : '';

    renderMath(prev);

  }

}



function buildStudentShortcutNoteHTML(qId) {

  const current = state.questionNotes?.[qId] || '';

  return `

    <div class="student-note-container">

      <div class="student-note-header">

        <span>📝 My Shortcut / Personal Derivation Note (KaTeX Supported):</span>

        <span style="font-size:10px;color:var(--text-muted)">Auto-saved</span>

      </div>

      <textarea class="student-note-textarea" 

        placeholder="Type your personal mnemonic, shortcut trick, or formula e.g. $T(n) = \Theta(n^{\\log_b a})$..." 

        oninput="saveStudentQuestionNote('${qId}', this.value)">${escapeHtml(current)}</textarea>

      <div class="student-note-preview" id="student-note-preview-${qId}">

        ${current ? `<strong>Preview:</strong> ${formatQuestionContent(current)}` : ''}

      </div>

    </div>

  `;

}





// ─── EXAM COUNTDOWN & DAILY STUDY STREAK ENGINE ─────────────────────────────

function getExamCountdownData() {

  const now = new Date();

  let targetYear = now.getFullYear();

  let targetDate = new Date(targetYear, 1, 6, 9, 0, 0); // First Saturday of February 9:00 AM

  if (now > targetDate) {

    targetYear++;

    targetDate = new Date(targetYear, 1, 6, 9, 0, 0);

  }

  const diffMs = targetDate - now;

  const days = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  return { days, targetYear };

}



function initExamCountdownAndStreak() {

  const cdEl = document.getElementById('countdown-text');

  if (cdEl) {

    const cd = getExamCountdownData();

    cdEl.textContent = `GATE ${cd.targetYear}: ${cd.days}d`;

  }



  try {

    const raw = localStorage.getItem('gate_daily_streak_v1');

    state.dailyStreak = raw ? JSON.parse(raw) : { lastDate: '', streak: 0, todayCount: 0, goal: 20 };

  } catch(e) {

    state.dailyStreak = { lastDate: '', streak: 0, todayCount: 0, goal: 20 };

  }



  const todayStr = new Date().toISOString().slice(0, 10);

  if (state.dailyStreak.lastDate !== todayStr) {

    const yesterday = new Date(Date.now() - 86400000).toISOString().slice(0, 10);

    if (state.dailyStreak.lastDate !== yesterday && state.dailyStreak.lastDate !== '') {

      state.dailyStreak.streak = 0;

    }

    state.dailyStreak.lastDate = todayStr;

    state.dailyStreak.todayCount = 0;

    saveDailyStreak();

  }

  updateStreakUI();

}



function recordDailyAttemptForStreak() {

  if (!state.dailyStreak) initExamCountdownAndStreak();

  state.dailyStreak.todayCount = (state.dailyStreak.todayCount || 0) + 1;

  if (state.dailyStreak.todayCount === state.dailyStreak.goal) {

    state.dailyStreak.streak = (state.dailyStreak.streak || 0) + 1;

    showToast(`🔥 Daily Goal Reached! ${state.dailyStreak.streak}-day streak!`, 'success');

  }

  saveDailyStreak();

  updateStreakUI();

}



function saveDailyStreak() {

  try {

    localStorage.setItem('gate_daily_streak_v1', JSON.stringify(state.dailyStreak));

  } catch(e) {}

}



function updateStreakUI() {

  const stEl = document.getElementById('streak-text');

  if (stEl && state.dailyStreak) {

    const { streak, todayCount, goal } = state.dailyStreak;

    stEl.textContent = `${streak}d (${todayCount}/${goal} Q)`;

  }

}



// ─── UNIVERSAL GLOBAL QUESTION SEARCH (21,502 QUESTIONS) ──────────────────────

function openGlobalSearch() {

  const modal = document.getElementById('global-search-modal');

  const backdrop = document.getElementById('global-search-backdrop');

  const input = document.getElementById('global-search-input');

  const countBadge = document.getElementById('global-search-count');

  const totalQs = (state.questions && state.questions.length) ? state.questions.length.toLocaleString() : '32,383';

  if (countBadge && (!state.globalSearchQuery || !state.globalSearchQuery.trim())) {

    countBadge.textContent = `${totalQs} questions indexed`;

  }

  if (modal && backdrop) {

    modal.classList.add('active');

    backdrop.classList.add('active');

    if (input) {

      input.placeholder = `Search ${totalQs} questions by topic, algorithm, theorem, keyword (Press /)...`;

      input.value = state.globalSearchQuery || '';

      input.focus();

      input.select();

      if (input.value) handleGlobalSearchInput(input.value);

    }

  }

}



function closeGlobalSearch() {

  const modal = document.getElementById('global-search-modal');

  const backdrop = document.getElementById('global-search-backdrop');

  if (modal && backdrop) {

    modal.classList.remove('active');

    backdrop.classList.remove('active');

  }

}



let globalSearchDebounceTimer = null;

function handleGlobalSearchInput(query) {

  state.globalSearchQuery = query;

  clearTimeout(globalSearchDebounceTimer);

  globalSearchDebounceTimer = setTimeout(() => {

    executeGlobalSearch(query);

  }, 150);

}



function setGlobalSearchFilter(type, btn) {

  state.globalSearchFilter = type;

  document.querySelectorAll('.global-search-filters .chip').forEach(c => c.classList.remove('active'));

  if (btn) btn.classList.add('active');

  executeGlobalSearch(state.globalSearchQuery || '');

}



function executeGlobalSearch(rawQuery) {

  const container = document.getElementById('global-search-results');

  const countEl = document.getElementById('global-search-count');

  if (!container) return;



  const qStr = (rawQuery || '').trim().toLowerCase();

  const filterType = state.globalSearchFilter || 'all';
  const filterSubject = state.globalSearchSubject || 'all';



  if (!qStr) {

    container.innerHTML = `

      <div style="padding:32px 16px;text-align:center;color:var(--text-muted);font-size:13px">

        Search ${state.questions.length.toLocaleString()} questions by theorem, concept, formula, or code snippet (e.g. <em>Dijkstra, LRU, B+ Tree, Pipelining, Master Theorem</em>)

      </div>`;

    if (countEl) countEl.textContent = `${(state.questions || []).length} questions indexed`;

    return;

  }



  const terms = qStr.split(/\s+/).filter(Boolean);

  let matches = (state.questions || []).filter(q => {

    if (filterType !== 'all' && q.type !== filterType) return false;
    if (filterSubject !== 'all' && q.subject !== filterSubject) return false;

    const hay = q._searchHaystack || ((q.question || '') + ' ' + (q.subject || '') + ' ' + (q.topic || '') + ' ' + (q.explanation || '')).toLowerCase();

    return terms.every(t => hay.includes(t));

  });



  if (countEl) {

    countEl.textContent = `${matches.length} matching questions found`;

  }



  if (!matches.length) {

    container.innerHTML = `

      <div style="padding:32px 16px;text-align:center;color:var(--text-muted)">

        <div style="font-size:24px;margin-bottom:8px">🔍</div>

        <div>No questions found matching "<strong>${escapeHtml(rawQuery)}</strong>"</div>

        <div style="font-size:12px;margin-top:4px">Try searching for broader terms like "scheduling", "cache", "sorting", or "grammar".</div>

      </div>`;

    return;

  }



  const displayList = matches.slice(0, 25);

  container.innerHTML = displayList.map((q, idx) => {

    const snippet = (q.question || '').replace(/\s+/g, ' ').slice(0, 140);

    return `

      <div class="search-result-item" onclick="startSingleQuestionPractice('${q.id}')">

        <div class="search-result-meta">

          <span class="q-badge ${q.type}">${q.type?.toUpperCase()}</span>

          <span class="q-badge ${q.difficulty}">${q.difficulty}</span>

          <span class="chip">${escapeHtml(q.subject || 'CS')}</span>

          ${q.topic ? `<span class="chip chip-info">${escapeHtml(q.topic)}</span>` : ''}

          <span style="margin-left:auto;color:var(--text-muted);font-size:10px">#${idx + 1}</span>

        </div>

        <div class="search-result-snippet">${escapeHtml(snippet)}...</div>

        <div style="display:flex;justify-content:flex-end;gap:8px;margin-top:6px">

          <button class="btn btn-secondary btn-sm" onclick="event.stopPropagation(); openPlaylistModal('${q.id}')" style="padding:2px 8px;font-size:11px" type="button">

            🗂️ Playlist

          </button>

          <button class="btn btn-primary btn-sm" onclick="event.stopPropagation(); startSingleQuestionPractice('${q.id}')" style="padding:2px 8px;font-size:11px" type="button">

            ▶ Practice Now

          </button>

        </div>

      </div>

    `;

  }).join('');

}



function startSingleQuestionPractice(qid) {

  closeGlobalSearch();

  const q = (state.questions || []).find(item => item.id === qid);

  if (!q) return;

  state.practiceQueue = [q];

  state.currentQuestion = 0;

  state.practiceMode = true;

  state.practiceAnswered = false;

  practiceSelectedOpts = new Set();

  const ov = document.getElementById('test-overlay');

  if (ov) {

    ov.classList.add('active');

    renderPracticeQuestion();

    renderMath(ov);

  }

}



// ─── 10-SPOKE SUBJECT MASTERY RADAR CHART (IIT MADRAS SPECIFICATION) ─────────

function buildMasteryRadarChartSVG() {

  const subjects10 = [

    { key: 'Engineering Mathematics', label: 'Engg Math & DM' },

    { key: 'Digital Logic', label: 'Digital Logic' },

    { key: 'Computer Organization', label: 'COA' },

    { key: 'Data Structures', label: 'C & Data Structures' },

    { key: 'Algorithms', label: 'Algorithms' },

    { key: 'Theory of Computation', label: 'TOC' },

    { key: 'Compiler Design', label: 'Compiler Design' },

    { key: 'Operating Systems', label: 'Operating Systems' },

    { key: 'DBMS', label: 'DBMS' },

    { key: 'Computer Networks', label: 'Networks' }

  ];



  const totalSpokes = subjects10.length;

  const cx = 200, cy = 200, R = 130;

  const rings = [0.2, 0.4, 0.6, 0.8, 1.0];



  const ringsSVG = rings.map(rPct => {

    const pts = [];

    for (let i = 0; i < totalSpokes; i++) {

      const angle = (Math.PI * 2 / totalSpokes) * i - Math.PI / 2;

      const x = cx + R * rPct * Math.cos(angle);

      const y = cy + R * rPct * Math.sin(angle);

      pts.push(`${x.toFixed(1)},${y.toFixed(1)}`);

    }

    return `<polygon points="${pts.join(' ')}" class="radar-grid-ring" />

            <text x="${cx + 4}" y="${(cy - R * rPct + 10).toFixed(1)}" fill="rgba(255,255,255,0.25)" font-size="8">${Math.round(rPct * 100)}%</text>`;

  }).join('');



  const spokesSVG = subjects10.map((s, i) => {

    const angle = (Math.PI * 2 / totalSpokes) * i - Math.PI / 2;

    const x = cx + R * Math.cos(angle);

    const y = cy + R * Math.sin(angle);

    const lx = cx + (R + 24) * Math.cos(angle);

    const ly = cy + (R + 18) * Math.sin(angle);

    return `

      <line x1="${cx}" y1="${cy}" x2="${x.toFixed(1)}" y2="${y.toFixed(1)}" class="radar-spoke" />

      <text x="${lx.toFixed(1)}" y="${ly.toFixed(1)}" class="radar-label">${s.label}</text>

    `;

  }).join('');



  const polygonPoints = [];

  const dataPoints = [];

  const legendRows = [];



  subjects10.forEach((s, i) => {

    const st = getSubjectStats(s.key);

    const acc = st.doneCount > 0 ? st.accuracy : 45;

    const rPct = Math.max(0.15, Math.min(1.0, acc / 100));

    const angle = (Math.PI * 2 / totalSpokes) * i - Math.PI / 2;

    const x = cx + R * rPct * Math.cos(angle);

    const y = cy + R * rPct * Math.sin(angle);

    polygonPoints.push(`${x.toFixed(1)},${y.toFixed(1)}`);

    dataPoints.push(`<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="3.5" class="radar-point"><title>${s.label}: ${acc}% Accuracy (${st.doneCount} Qs)</title></circle>`);

    

    const tierBadge = acc >= 75 ? '🟢 Strong' : acc >= 50 ? '🟡 Average' : '🔴 Focus Area';

    legendRows.push(`

      <div class="radar-legend-item">

        <span style="font-weight:600;color:var(--text-primary)">${s.label}</span>

        <div style="display:flex;align-items:center;gap:8px">

          <span style="font-weight:800;color:var(--accent)">${acc}%</span>

          <span style="font-size:10px">${tierBadge}</span>

        </div>

      </div>

    `);

  });



  return `

    <div class="radar-chart-card">

      <div class="card-header" style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px">

        <div class="card-title">🕸️ 10-Spoke Subject Mastery Radar (IIT Madras Curriculum)</div>

        <span class="badge" style="background:rgba(108,99,255,0.2);color:var(--accent)">360° Syllabus Depth</span>

      </div>

      <div class="radar-chart-container">

        <div class="radar-svg-wrap">

          <svg class="radar-svg" viewBox="0 0 400 400">

            ${ringsSVG}

            ${spokesSVG}

            <polygon points="${polygonPoints.join(' ')}" class="radar-polygon" />

            ${dataPoints.join('')}

          </svg>

        </div>

        <div class="radar-legend-list">

          <div style="font-size:12px;color:var(--text-muted);margin-bottom:4px">Topic-by-topic accuracy profile:</div>

          ${legendRows.join('')}

        </div>

      </div>

    </div>

  `;

}



// ─── OPTION ELIMINATION & EXPECTED VALUE (E) RISK ANALYZER ────────────────────

function setQuestionConfidence(qid, level) {

  if (!state.confidenceTags) state.confidenceTags = {};

  if (state.confidenceTags[qid] === level) {

    delete state.confidenceTags[qid];

  } else {

    state.confidenceTags[qid] = level;

  }

  try {

    localStorage.setItem('gate_cse_confidence_tags', JSON.stringify(state.confidenceTags));

  } catch(e) {}



  const wrap = document.getElementById(`conf-selector-${qid}`);

  if (wrap) {

    wrap.outerHTML = buildConfidenceSelectorHTML(qid);

  }

}



function buildConfidenceSelectorHTML(qid) {

  const current = state.confidenceTags?.[qid] || '';

  return `

    <div class="confidence-selector" id="conf-selector-${qid}">

      <span class="conf-label">🎯 Confidence:</span>

      <div class="conf-btn-group">

        <button class="conf-btn conf-high ${current === 'high' ? 'active' : ''}" onclick="setQuestionConfidence('${qid}', 'high')" type="button" title="100% Sure / Confident">

          🟢 Sure

        </button>

        <button class="conf-btn conf-educated ${current === 'educated' ? 'active' : ''}" onclick="setQuestionConfidence('${qid}', 'educated')" type="button" title="Eliminated 1 or 2 options (50:50 guess)">

          🟡 50:50 Guess

        </button>

        <button class="conf-btn conf-blind ${current === 'blind' ? 'active' : ''}" onclick="setQuestionConfidence('${qid}', 'blind')" type="button" title="Blind Guess / Intuition">

          🔴 Blind Guess

        </button>

      </div>

    </div>

  `;

}



function getExpectedValueAnalysis(q) {

  const marks = q.marks || 1;

  const isMcq = q.type === 'mcq';

  const isMsqOrNat = q.type === 'msq' || q.type === 'nat';



  if (isMsqOrNat) {

    return {

      type: q.type.toUpperCase(),

      penalty: 0,

      ev0: (1 / 4) * marks,

      ev1: (1 / 3) * marks,

      ev2: (1 / 2) * marks,

      recommendation: '✅ ZERO NEGATIVE PENALTY: Guessing never loses marks in MSQs & NATs! Always attempt.'

    };

  }



  const neg = marks === 2 ? 2 / 3 : 1 / 3;

  const ev0 = (1 / 4) * marks - (3 / 4) * neg;

  const ev1 = (1 / 3) * marks - (2 / 3) * neg;

  const ev2 = (1 / 2) * marks - (1 / 2) * neg;



  return {

    type: 'MCQ',

    penalty: -neg,

    ev0: Number(ev0.toFixed(2)),

    ev1: Number(ev1.toFixed(2)),

    ev2: Number(ev2.toFixed(2)),

    recommendation: ev2 > 0 ? '💡 MATHEMATICAL EDGE: If you eliminate 2 options, Expected Value is +' + ev2.toFixed(2) + ' marks. Statistically you must attempt!' : 'Neutral expected value.'

  };

}



function buildExpectedValueCardHTML(q) {

  const ev = getExpectedValueAnalysis(q);

  return `

    <div class="ev-card">

      <div class="ev-header">

        <span class="ev-title">⚖️ Option Elimination & Expected Value (E) Analyzer</span>

        <span class="chip" style="font-size:10px">${escapeHtml(ev.type)} (${q.marks}M)</span>

      </div>

      <div style="font-size:11px;color:var(--text-secondary);line-height:1.4">

        ${escapeHtml(ev.recommendation)}

      </div>

      <div class="ev-matrix-grid">

        <div class="ev-stat-box">

          <div class="ev-stat-val" style="color:${ev.ev0 >= 0 ? '#4ade80' : '#f87171'}">${ev.ev0 >= 0 ? '+' : ''}${ev.ev0} M</div>

          <div class="ev-stat-lbl">Blind Guess (4 Choices)</div>

        </div>

        <div class="ev-stat-box">

          <div class="ev-stat-val" style="color:#facc15">+${ev.ev1} M</div>

          <div class="ev-stat-lbl">1 Option Eliminated</div>

        </div>

        <div class="ev-stat-box">

          <div class="ev-stat-val" style="color:#4ade80;font-weight:900">+${ev.ev2} M</div>

          <div class="ev-stat-lbl">2 Options Eliminated (50:50)</div>

        </div>

      </div>

    </div>

  `;

}



// ─── 60-SECOND FORMULA BLITZ SPEED RECALL MODE ──────────────────────────────

let blitzTimerInterval = null;

let blitzCurrentIndex = 0;

let blitzScore = 0;

let blitzStreak = 0;

let blitzTimeRemaining = 60;

let blitzDeck = [];



function startFormulaBlitz() {

  const backdrop = document.getElementById('flashcard-modal-backdrop');

  if (backdrop) backdrop.classList.add('active');

  const modal = document.getElementById('flashcard-modal-card');

  if (!modal) return;

  

  blitzDeck = [...(FORMULA_FLASHCARDS || [])].sort(() => Math.random() - 0.5);

  if (!blitzDeck.length) {

    showToast('No flashcards loaded in deck', 'error');

    return;

  }

  blitzScore = 0;

  blitzStreak = 0;

  blitzTimeRemaining = 60;

  blitzCurrentIndex = 0;



  renderFormulaBlitzView();



  clearInterval(blitzTimerInterval);

  blitzTimerInterval = setInterval(() => {

    blitzTimeRemaining--;

    const timeFill = document.getElementById('blitz-timer-fill');

    const timeText = document.getElementById('blitz-time-text');

    if (timeFill) timeFill.style.width = `${(blitzTimeRemaining / 60) * 100}%`;

    if (timeText) timeText.textContent = `⏳ ${blitzTimeRemaining}s`;



    if (blitzTimeRemaining <= 0) {

      finishFormulaBlitz();

    }

  }, 1000);

}



function renderFormulaBlitzView() {

  const modal = document.getElementById('flashcard-modal-card');

  if (!modal) return;



  const card = blitzDeck[blitzCurrentIndex % blitzDeck.length] || { topic: 'Core Formula', formula: 'Formula Recall' };



  modal.innerHTML = `

    <div class="flashcard-modal-header">

      <div class="flashcard-modal-title">⚡ 60-Second Formula Blitz</div>

      <button class="shortcuts-close-btn" onclick="stopFormulaBlitz()" type="button">✕ Exit Blitz</button>

    </div>

    <div class="blitz-view-container">

      <div style="display:flex;justify-content:space-between;align-items:center;font-size:13px;font-weight:700">

        <span id="blitz-time-text" style="color:#f87171">⏳ ${blitzTimeRemaining}s</span>

        <span style="color:#eab308">🔥 Streak: ${blitzStreak}</span>

        <span style="color:var(--accent)">Score: ${blitzScore} pts</span>

      </div>

      <div class="blitz-timer-bar">

        <div class="blitz-timer-fill" id="blitz-timer-fill" style="width:${(blitzTimeRemaining / 60) * 100}%"></div>

      </div>

      <div class="blitz-card-topic">${escapeHtml(card.topic)}</div>

      <div class="blitz-card-formula" id="blitz-formula-content">${escapeHtml(card.title || card.topic)}: Can you recall the invariant / formula?</div>

      <button class="btn btn-secondary btn-sm" onclick="revealBlitzFormula()" id="blitz-reveal-btn" type="button" style="align-self:center;padding:4px 12px">

        👁️ Peek Formula Solution

      </button>

      <div class="blitz-actions">

        <button class="btn btn-danger" onclick="advanceBlitzCard(false)" style="padding:10px 24px;font-weight:700" type="button">

          ❌ Blank / Forgot

        </button>

        <button class="btn btn-success" onclick="advanceBlitzCard(true)" style="padding:10px 24px;font-weight:700" type="button">

          ✅ Recalled It! (+10 pts)

        </button>

      </div>

    </div>

  `;

}



function revealBlitzFormula() {

  const card = blitzDeck[blitzCurrentIndex % blitzDeck.length];

  const box = document.getElementById('blitz-formula-content');

  const btn = document.getElementById('blitz-reveal-btn');

  if (box && card) {

    box.innerHTML = formatQuestionContent(card.formula || card.details || card.title);

    renderMath(box);

    if (btn) btn.style.display = 'none';

  }

}



function advanceBlitzCard(known) {

  if (known) {

    blitzScore += 10 + Math.min(blitzStreak * 2, 10);

    blitzStreak++;

  } else {

    blitzStreak = 0;

  }

  blitzCurrentIndex++;

  renderFormulaBlitzView();

}



function finishFormulaBlitz() {

  clearInterval(blitzTimerInterval);

  const modal = document.getElementById('flashcard-modal-card');

  if (!modal) return;

  modal.innerHTML = `

    <div class="flashcard-modal-header">

      <div class="flashcard-modal-title">🏁 Blitz Complete!</div>

      <button class="shortcuts-close-btn" onclick="stopFormulaBlitz()" type="button">✕</button>

    </div>

    <div class="blitz-view-container">

      <div class="blitz-score-badge">🏆 ${blitzScore} PTS</div>

      <div style="font-size:15px;color:var(--text-secondary);font-weight:600">

        You rapidly evaluated ${blitzCurrentIndex} core formulas in 60 seconds!

      </div>

      <div style="display:flex;justify-content:center;gap:12px;margin-top:12px">

        <button class="btn btn-primary" onclick="startFormulaBlitz()" type="button">🔄 Play Again</button>

        <button class="btn btn-secondary" onclick="stopFormulaBlitz()" type="button">Back to Deck</button>

      </div>

    </div>

  `;

}



function stopFormulaBlitz() {

  clearInterval(blitzTimerInterval);

  renderActiveFlashcard();

}



// ─── NAT PRECISION & ROUNDING TRAP INSPECTOR ─────────────────────────────────

function buildNatToleranceHTML(q) {

  if (q.type !== 'nat') return '';

  const range = q.natRange || { min: q.correct[0], max: q.correct[0] };

  const exact = q.correct[0];

  const isRange = range.min !== range.max;

  

  return `

    <div class="nat-tolerance-box">

      <div class="nat-tolerance-header">

        <span>🎯 Numerical Acceptance Bounds:</span>

        <span style="font-family:monospace;font-size:13px;font-weight:800;color:#38bdf8">

          ${isRange ? `[${range.min}, ${range.max}]` : `${exact}`}

        </span>

      </div>

      <div class="nat-trap-alert">

        <strong>⚠️ Rounding Trap Advisory:</strong> GATE marks strictly on acceptance boundaries. Never truncate or round intermediate floats; carry full machine precision and round only your final result.

      </div>

    </div>

  `;

}



// ─── 2-COLUMN PRINTABLE PRACTICE WORKSHEET GENERATOR ─────────────────────────

function generatePrintableWorksheet(questions, title = 'GATE CSE Practice Worksheet') {

  const container = document.getElementById('printable-worksheet-container');

  if (!container) return;



  const qs = questions || (state.questions || []).slice(0, 30);

  const labels = ['(A)', '(B)', '(C)', '(D)'];



  container.innerHTML = `

    <div class="ws-header">

      <div>

        <div class="ws-title">🎯 ${escapeHtml(title)}</div>

        <div class="ws-meta">GATE CSE Aspirant Platform • Organizing Institute Standards (IIT Madras) • Total Questions: ${qs.length}</div>

      </div>

      <div style="text-align:right">

        <div class="ws-meta"><strong>Date:</strong> ________________</div>

        <div class="ws-meta"><strong>Score:</strong> _____ / ${qs.reduce((acc, q) => acc + (q.marks || 1), 0)} M</div>

      </div>

    </div>



    <div class="ws-grid">

      ${qs.map((q, idx) => `

        <div class="ws-q-item">

          <div class="ws-q-num">Q${idx + 1}. [${q.type?.toUpperCase()} | ${q.marks} Mark${q.marks > 1 ? 's' : ''}] [${escapeHtml(q.subject || 'CS')}]</div>

          <div style="margin-bottom:6px">${formatQuestionContent(q.question)}</div>

          ${q.type === 'nat'

            ? `<div style="margin-top:6px;font-family:monospace">Answer: [ _______________ ]</div>`

            : `<div class="ws-options">

                ${(q.options || []).map((opt, oIdx) => `

                  <div class="ws-opt">

                    <span class="ws-box"></span>

                    <span>${labels[oIdx]} ${formatQuestionContent(opt)}</span>

                  </div>

                `).join('')}

               </div>`

          }

        </div>

      `).join('')}

    </div>



    <div class="ws-page-break"></div>



    <div class="ws-header">

      <div class="ws-title">📝 Answer Key & Solutions: ${escapeHtml(title)}</div>

      <div class="ws-meta">For Self-Evaluation Only</div>

    </div>



    <table class="ws-key-table">

      <thead>

        <tr>

          <th style="width:40px">Q#</th>

          <th style="width:60px">Type</th>

          <th style="width:80px">Correct</th>

          <th>Explanation Summary</th>

        </tr>

      </thead>

      <tbody>

        ${qs.map((q, idx) => {

          const corr = q.type === 'nat' ? `${q.correct[0]}` : q.correct.map(c => labels[c]).join(', ');

          const expl = (q.explanation || 'Direct derivation.').slice(0, 150);

          return `

            <tr>

              <td><strong>Q${idx + 1}</strong></td>

              <td>${q.type?.toUpperCase()}</td>

              <td style="font-weight:700">${corr}</td>

              <td>${escapeHtml(expl)}...</td>

            </tr>

          `;

        }).join('')}

      </tbody>

    </table>

  `;



  renderMath(container);

  setTimeout(() => {

    window.print();

  }, 200);

}



function exportReviewWorksheetPDF() {

  if (state.activeTestResults?.questions) {

    generatePrintableWorksheet(state.activeTestResults.questions, 'GATE Mock Exam Review Worksheet');

  } else if (state.practiceQueue?.length) {

    generatePrintableWorksheet(state.practiceQueue, 'GATE CSE Practice Drill Worksheet');

  } else {

    generatePrintableWorksheet((state.questions || []).slice(0, 25), 'GATE CSE High-Yield Drill Worksheet');

  }

}



// ─── EXPOSE FUNCTIONS TO GLOBAL SCOPE ────────────────────────────────────────

// app.js is an ES module — functions are NOT on window by default.

// Any function called from an inline onclick="fn()" must be on window.



// ================================================================

// 💎 CHERRY ON TOP MICRO-IMPROVEMENTS & AUDIO ENGINE

// ================================================================



const BOOKMARK_TAG_META = {

  trap: { label: 'Conceptual Trap', color: '#ef4444', icon: '🔴' },

  calc: { label: 'Calculation Heavy', color: '#f59e0b', icon: '🟡' },

  exam: { label: 'Pre-Exam Revise', color: '#10b981', icon: '🟢' }

};



// ── 🔊 TACTILE AUDIO & SOUND FX ENGINE (Web Audio API) ─────────

let soundFxCtx = null;

function getSoundFxCtx() {

  if (!soundFxCtx) {

    const AudioCtx = window.AudioContext || window.webkitAudioContext;

    if (AudioCtx) soundFxCtx = new AudioCtx();

  }

  if (soundFxCtx && soundFxCtx.state === 'suspended') {

    soundFxCtx.resume().catch(() => {});

  }

  return soundFxCtx;

}



function initSoundFxState() {

  try {

    const saved = localStorage.getItem('gate_sound_fx');

    state.soundFxEnabled = saved !== 'false';

  } catch(e) {

    state.soundFxEnabled = true;

  }

  updateSoundFxButtonUI();

}



function toggleSoundFx() {

  state.soundFxEnabled = !state.soundFxEnabled;

  try {

    localStorage.setItem('gate_sound_fx', state.soundFxEnabled ? 'true' : 'false');

  } catch(e) {}

  updateSoundFxButtonUI();

  if (state.soundFxEnabled) playUiClickSound();

  showToast(state.soundFxEnabled ? '🔊 Audio FX: Enabled' : '🔇 Audio FX: Muted', 'info', 2000);

}



function updateSoundFxButtonUI() {

  const btn = document.getElementById('sound-fx-btn');

  const icon = document.getElementById('sound-fx-icon');

  if (icon) icon.textContent = state.soundFxEnabled ? '🔊' : '🔇';

  if (btn) btn.title = state.soundFxEnabled ? 'Sound FX Enabled (Click to Mute)' : 'Sound FX Muted (Click to Enable)';

}



function playUiClickSound() {

  if (!state.soundFxEnabled) return;

  try {

    const ctx = getSoundFxCtx();

    if (!ctx) return;

    const osc = ctx.createOscillator();

    const gain = ctx.createGain();

    osc.type = 'triangle';

    osc.frequency.setValueAtTime(850, ctx.currentTime);

    osc.frequency.exponentialRampToValueAtTime(350, ctx.currentTime + 0.025);

    gain.gain.setValueAtTime(0.04, ctx.currentTime);

    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.025);

    osc.connect(gain);

    gain.connect(ctx.destination);

    osc.start();

    osc.stop(ctx.currentTime + 0.026);

  } catch(e) {}

}



function playUiSuccessChime() {

  if (!state.soundFxEnabled) return;

  try {

    const ctx = getSoundFxCtx();

    if (!ctx) return;

    const notes = [523.25, 659.25, 783.99]; // C5, E5, G5

    notes.forEach((freq, i) => {

      const osc = ctx.createOscillator();

      const gain = ctx.createGain();

      const startTime = ctx.currentTime + i * 0.12;

      osc.type = 'sine';

      osc.frequency.setValueAtTime(freq, startTime);

      gain.gain.setValueAtTime(0.09, startTime);

      gain.gain.exponentialRampToValueAtTime(0.001, startTime + 0.28);

      osc.connect(gain);

      gain.connect(ctx.destination);

      osc.start(startTime);

      osc.stop(startTime + 0.3);

    });

  } catch(e) {}

}



function playUiWarningChime() {

  if (!state.soundFxEnabled) return;

  try {

    const ctx = getSoundFxCtx();

    if (!ctx) return;

    [659.25, 523.25].forEach((freq, i) => {

      const osc = ctx.createOscillator();

      const gain = ctx.createGain();

      const startTime = ctx.currentTime + i * 0.16;

      osc.type = 'sine';

      osc.frequency.setValueAtTime(freq, startTime);

      gain.gain.setValueAtTime(0.12, startTime);

      gain.gain.exponentialRampToValueAtTime(0.001, startTime + 0.22);

      osc.connect(gain);

      gain.connect(ctx.destination);

      osc.start(startTime);

      osc.stop(startTime + 0.25);

    });

  } catch(e) {}

}



// ── ⏰ EXAM COUNTDOWN MILESTONE BANNER NOTICES ─────────────────

function showExamMilestoneNotice(title, subtitle) {

  playUiWarningChime();

  let banner = document.getElementById('exam-milestone-banner');

  if (!banner) {

    banner = document.createElement('div');

    banner.id = 'exam-milestone-banner';

    banner.className = 'exam-milestone-banner';

    document.body.appendChild(banner);

  }

  banner.innerHTML = `

    <div>

      <div class="exam-milestone-title">${title}</div>

      <div class="exam-milestone-subtitle">${subtitle}</div>

    </div>

    <button class="btn btn-secondary btn-sm" onclick="this.parentElement.remove()" style="padding:2px 8px;font-size:11px" type="button">✕ Dismiss</button>

  `;

  setTimeout(() => {

    if (banner && banner.parentNode) banner.remove();

  }, 7500);

}



// ── 🏷️ MULTI-COLORED BOOKMARK TAGS ENGINE ─────────────────────

function setBookmarkTag(questionId, tag, event) {

  if (event) event.stopPropagation();

  closeAllBookmarkTagPickers();

  if (!questionId) return;

  if (!tag) {

    state.bookmarks.delete(questionId);

    delete state.bookmarkTags[questionId];

    showToast('Removed from bookmarks', 'info');

  } else {

    state.bookmarks.add(questionId);

    state.bookmarkTags[questionId] = tag;

    const meta = BOOKMARK_TAG_META[tag] || BOOKMARK_TAG_META.exam;

    showToast(`Saved as ${meta.icon} ${meta.label}`, 'success');

  }

  saveBookmarks();

  debouncedIdbSaveUserData();

  updateBookmarkUIElements(questionId);

  if (state.currentPage === 'practice' && state.practiceFilters.status === 'bookmarked') {

    renderPractice(document.getElementById('page-content'));

  }

}



function openBookmarkTagPicker(questionId, event) {

  if (event) event.stopPropagation();

  closeAllBookmarkTagPickers();

  const target = event.currentTarget || event.target;

  const rect = target.getBoundingClientRect();



  const pop = document.createElement('div');

  pop.id = `bookmark-tag-picker-${questionId}`;

  pop.className = 'bookmark-tag-picker-popover';

  pop.style.top = `${rect.bottom + window.scrollY + 6}px`;

  pop.style.left = `${Math.max(10, rect.left + window.scrollX - 40)}px`;



  pop.innerHTML = `

    <div style="font-size:10px;font-weight:700;color:var(--text-muted);padding:2px 6px;text-transform:uppercase">Choose Bookmark Tag:</div>

    <button class="bookmark-tag-picker-btn" onclick="setBookmarkTag('${questionId}', 'trap', event)" type="button">

      🔴 <span>Conceptual Trap</span>

    </button>

    <button class="bookmark-tag-picker-btn" onclick="setBookmarkTag('${questionId}', 'calc', event)" type="button">

      🟡 <span>Calculation Heavy</span>

    </button>

    <button class="bookmark-tag-picker-btn" onclick="setBookmarkTag('${questionId}', 'exam', event)" type="button">

      🟢 <span>Pre-Exam Revise</span>

    </button>

    <div style="border-top:1px solid var(--border);margin:2px 0"></div>

    <button class="bookmark-tag-picker-btn" onclick="setBookmarkTag('${questionId}', null, event)" style="color:var(--red)" type="button">

      🗑️ <span>Remove Bookmark</span>

    </button>

  `;

  document.body.appendChild(pop);



  setTimeout(() => {

    window.addEventListener('click', closeAllBookmarkTagPickers, { once: true });

  }, 50);

}



function closeAllBookmarkTagPickers() {

  document.querySelectorAll('.bookmark-tag-picker-popover').forEach(el => el.remove());

}



function updateBookmarkUIElements(questionId) {

  const isBookmarked = state.bookmarks.has(questionId);

  const tag = state.bookmarkTags[questionId] || 'exam';

  const meta = BOOKMARK_TAG_META[tag] || BOOKMARK_TAG_META.exam;



  document.querySelectorAll(`.star-btn[data-qid="${questionId}"]`).forEach(btn => {

    btn.classList.toggle('bookmarked', isBookmarked);

    btn.innerHTML = isBookmarked ? '⭐' : '☆';

  });



  document.querySelectorAll(`.bookmark-tag-badge[data-qid="${questionId}"]`).forEach(badge => {

    if (!isBookmarked) {

      badge.style.display = 'none';

    } else {

      badge.style.display = 'inline-flex';

      badge.className = `bookmark-tag-badge tag-${tag}`;

      badge.innerHTML = `${meta.icon} ${meta.label}`;

    }

  });

}



function setBookmarkTagFilter(tag) {

  state.activeBookmarkTag = tag;

  if (state.currentPage === 'practice') {

    state.practicePage = 1;

    renderPractice(document.getElementById('page-content'));

  }

}



// ── 💡 FORMULA HINT PEEK (Practice Mode Only) ─────────────────

function getFormulaHintForQuestion(q) {

  if (!q) return null;

  if (Array.isArray(FORMULA_FLASHCARDS) && FORMULA_FLASHCARDS.length > 0) {

    const card = FORMULA_FLASHCARDS.find(c => {

      const matchSub = (c.subject || '').toLowerCase() === (q.subject || '').toLowerCase();

      const matchTopic = q.topic && c.topic && (q.topic.toLowerCase().includes(c.topic.toLowerCase()) || c.topic.toLowerCase().includes(q.topic.toLowerCase()));

      return matchSub && matchTopic;

    }) || FORMULA_FLASHCARDS.find(c => (c.subject || '').toLowerCase() === (q.subject || '').toLowerCase());



    if (card) {

      return {

        title: card.title,

        hint: card.hintText || 'Apply the standard governing formula for this topic.',

        formula: card.formulaHTML

      };

    }

  }



  // Subject-level default formulas

  const subFallbacks = {

    'Algorithms': { title: "Master's Theorem & Asymptotic Bounds", hint: "Check recurrence $T(n) = aT(n/b) + \\Theta(n^k \\log^p n)$ cases or loop bounding.", formula: "<div>Case 1: $k < \\log_b a \\implies T(n) = \\Theta(n^{\\log_b a})$<br/>Case 2: $k = \\log_b a \\implies T(n) = \\Theta(n^k \\log^{p+1} n)$</div>" },

    'Operating Systems': { title: "CPU Scheduling & Virtual Memory", hint: "Turnaround Time = Completion - Arrival. Page Fault Effective Access Time $EAT = m + (1-p)m + p \\cdot S$.", formula: "<div>$EAT = (1 - p) \\cdot t_m + p \\cdot t_{\\text{fault}}$</div>" },

    'Computer Networks': { title: "Bandwidth-Delay & Sliding Window Efficiency", hint: "Efficiency $\\eta = \\frac{W}{1 + 2a}$ where $a = \\frac{T_p}{T_t} = \\frac{\\text{Propagation Delay}}{\\text{Transmission Delay}}$.", formula: "<div>Transmission Time $T_t = \\frac{L}{B}$, Propagation Time $T_p = \\frac{d}{v}$</div>" },

    'Database Management Systems': { title: "Normalization & Serializability", hint: "Check Conflict Serializability precedence graph. Check Candidate keys via attribute closure $(X)^+$.", formula: "<div>Precedence graph acyclic $\\implies$ Conflict Serializable. BCNF: $X \\to Y \\implies X$ is Superkey.</div>" },

    'Theory of Computation': { title: "Pumping Lemma & Language Hierarchy", hint: "Regular: $w = xyz$ where $|xy| \\le p, |y| \\ge 1$. CFL: $w = uvxyz$.", formula: "<div>Finite State $\\implies$ Regular. Single Stack $\\implies$ CFL. 2-Stack / Turing $\\implies$ CSL / RE.</div>" },

    'Computer Organization & Architecture': { title: "Pipelining Speedup & Cache Mapping", hint: "Speedup $S = \\frac{n \\cdot k}{k + n - 1}$ for $n$ instructions, $k$ pipeline stages.", formula: "<div>Cache size = sets $\\times$ lines $\\times$ block size. Tag bits = Memory bits - (Set + Offset bits).</div>" }

  };



  return subFallbacks[q.subject] || {

    title: `${q.subject || 'GATE CSE'} Core Formula`,

    hint: `Focus on fundamental theorems and standard definitions in ${q.subject || 'this domain'}.`,

    formula: "<div>Double-check boundary constraints, NAT precision, and zero-index conditions.</div>"

  };

}



function toggleFormulaHint(questionId) {

  playUiClickSound();

  const box = document.getElementById(`formula-hint-box-${questionId}`);

  if (!box) return;

  const isHidden = box.style.display === 'none' || !box.style.display;

  if (!isHidden) {

    box.style.display = 'none';

    return;

  }

  const q = (state.practiceQueue && state.practiceQueue[state.currentQuestion]) || state.questions.find(x => x.id === questionId);

  const hintData = getFormulaHintForQuestion(q);

  if (!hintData) return;



  box.innerHTML = `

    <div class="formula-hint-title">💡 ${hintData.title}</div>

    <div class="formula-hint-content">

      <div style="font-size:12px;margin-bottom:6px;color:var(--text-secondary)"><strong>Strategy Hint:</strong> ${hintData.hint}</div>

      <div style="background:var(--bg-card);border:1px solid var(--border);border-radius:6px;padding:8px 10px;font-size:12.5px">

        ${hintData.formula}

      </div>

    </div>

  `;

  box.style.display = 'block';

  renderMath(box);

}



// ── 🖨️ 1-PAGE PRINTABLE 87-CHAPTER WALL CHEAT SHEET ──────────

function printSyllabusWallSheet() {

  playUiClickSound();

  const printEl = document.getElementById('printable-syllabus-sheet');

  if (!printEl) return;



  // Group questions by subject -> topic

  const subjectMap = {};

  SUBJECTS.forEach(s => { subjectMap[s.name] = new Set(); });



  state.questions.forEach(q => {

    if (q && q.subject && q.topic) {

      if (!subjectMap[q.subject]) subjectMap[q.subject] = new Set();

      subjectMap[q.subject].add(q.topic);

    }

  });



  const attemptMap = new Map();

  state.attempts.forEach(a => {

    const q = state.questions.find(x => x.id === a.questionId);

    if (q && q.subject && q.topic) {

      const key = `${q.subject}|${q.topic}`;

      const rec = attemptMap.get(key) || { total: 0, correct: 0 };

      rec.total++;

      if (a.correct) rec.correct++;

      attemptMap.set(key, rec);

    }

  });



  let rows = '';

  let chapterIndex = 1;



  Object.keys(subjectMap).forEach(subName => {

    const topics = Array.from(subjectMap[subName]);

    topics.forEach((topic, tIdx) => {

      const key = `${subName}|${topic}`;

      const st = attemptMap.get(key) || { total: 0, correct: 0 };

      const acc = st.total > 0 ? Math.round((st.correct / st.total) * 100) : 0;

      const statusIcon = st.total === 0 ? '⚪ Fresh' : acc >= 75 ? '🟢 Mastered' : acc >= 50 ? '🟡 Moderate' : '🔴 Weak';



      rows += `

        <tr>

          <td style="text-align:center;font-weight:700">${chapterIndex++}</td>

          <td style="font-weight:600">${tIdx === 0 ? `<strong>${subName}</strong>` : ''}</td>

          <td>${topic}</td>

          <td style="text-align:center">${st.total}</td>

          <td style="text-align:center">${acc}%</td>

          <td style="text-align:center">${statusIcon}</td>

          <td style="text-align:center;font-size:12px;color:#888">[ &nbsp; ]</td>

        </tr>`;

    });

  });



  printEl.innerHTML = `

    <div style="margin-bottom:10px;border-bottom:2px solid #333;padding-bottom:6px;display:flex;justify-content:space-between;align-items:flex-end">

      <div>

        <div style="font-size:16px;font-weight:900;letter-spacing:0.5px">🎯 GATE CSE 2026 — OFFICIAL 87-CHAPTER SYLLABUS WALL TRACKER</div>

        <div style="font-size:10px;color:#555">Physical Study Desk Audit Sheet • Generated from Live Attempt Telemetry • Target Mastery: ≥75%</div>

      </div>

      <div style="font-size:10px;text-align:right">

        Date: ${new Date().toLocaleDateString()}<br/>

        Total Attempts: ${state.attempts.length}

      </div>

    </div>

    <table class="wall-sheet-table">

      <thead>

        <tr>

          <th style="width:25px;text-align:center">#</th>

          <th style="width:140px">GATE Subject</th>

          <th>Syllabus Chapter / Micro-Topic</th>

          <th style="width:40px;text-align:center">Solved</th>

          <th style="width:40px;text-align:center">Acc%</th>

          <th style="width:70px;text-align:center">Status</th>

          <th style="width:35px;text-align:center">Done</th>

        </tr>

      </thead>

      <tbody>

        ${rows}

      </tbody>

    </table>

    <div style="margin-top:10px;font-size:8.5px;color:#666;display:flex;justify-content:space-between">

      <span>Legend: 🟢 Mastered (≥75% Acc) • 🟡 Moderate (50-74%) • 🔴 Weak (&lt;50%) • ⚪ Fresh</span>

      <span>IIT Madras GATE CSE Syllabus Standard • Keep on Study Wall</span>

    </div>

  `;



  document.body.classList.add('printing-wall-sheet');

  window.print();

  setTimeout(() => {

    document.body.classList.remove('printing-wall-sheet');

  }, 1000);

}



// ── 📊 SOLVE SPEED VS ACCURACY SCATTER PLOT ───────────────────

function buildSpeedAccuracyScatterSVG() {

  const subjectsData = SUBJECTS.map(s => {

    const stats = getSubjectStats(s.name);

    // Calculate average solving time in seconds

    let totalDwell = 0, dwellCount = 0;

    state.attempts.forEach(a => {

      const q = state.questions.find(x => x.id === a.questionId);

      if (q && q.subject === s.name && a.dwellSec) {

        totalDwell += a.dwellSec;

        dwellCount++;

      }

    });

    const avgSec = dwellCount > 0 ? Math.round(totalDwell / dwellCount) : (stats.doneCount > 0 ? 115 : 0);

    return {

      name: s.name,

      color: s.color || '#6c63ff',

      accuracy: stats.accuracy,

      avgSec: Math.min(240, Math.max(30, avgSec)),

      doneCount: stats.doneCount

    };

  }).filter(s => s.doneCount > 0);



  if (subjectsData.length === 0) {

    return `

      <div class="scatter-card">

        <div style="font-size:14px;font-weight:700;margin-bottom:4px">📊 Solving Pace vs Accuracy Quadrant Map</div>

        <div style="font-size:12px;color:var(--text-muted)">Practice at least 5 questions across subjects to unlock your real-time speed vs accuracy scatter diagnostic.</div>

      </div>`;

  }



  const svgW = 600, svgH = 320;

  const padLeft = 45, padRight = 20, padTop = 30, padBottom = 40;

  const plotW = svgW - padLeft - padRight;

  const plotH = svgH - padTop - padBottom;



  // Midpoint dividers: 140s on X axis (0 to 240), 70% on Y axis (0 to 100)

  const midX = padLeft + (140 / 240) * plotW;

  const midY = padTop + ((100 - 70) / 100) * plotH;



  const dots = subjectsData.map(s => {

    const cx = padLeft + (s.avgSec / 240) * plotW;

    const cy = padTop + ((100 - s.accuracy) / 100) * plotH;

    const r = Math.min(13, Math.max(6, 6 + Math.log2(s.doneCount + 1) * 1.6));

    const title = `${s.name}: ${s.accuracy}% Accuracy • Avg Pace: ${s.avgSec}s/Q • ${s.doneCount} attempts`;



    return `

      <g>

        <circle class="scatter-dot" cx="${cx}" cy="${cy}" r="${r}" fill="${s.color}" fill-opacity="0.85" stroke="#fff" stroke-width="1.5">

          <title>${title}</title>

        </circle>

        <text x="${cx}" y="${cy - r - 4}" text-anchor="middle" font-size="9" font-weight="700" fill="var(--text-primary)">

          ${s.name.split(' ')[0]}

        </text>

      </g>`;

  }).join('');



  return `

    <div class="scatter-card">

      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;flex-wrap:wrap;gap:8px">

        <div>

          <div style="font-size:15px;font-weight:700">📊 Solving Pace vs Accuracy Quadrant Diagnostic</div>

          <div style="font-size:11px;color:var(--text-muted);margin-top:2px">Interactive scatter map. Target: Bullseye Top-Left (Fast ≤140s & Accurate ≥70%).</div>

        </div>

        <span class="chip" style="font-size:11px;background:rgba(108,99,255,0.15);color:var(--accent)">${subjectsData.length} Subjects Active</span>

      </div>

      <div class="scatter-svg-wrapper">

        <svg viewBox="0 0 ${svgW} ${svgH}" width="100%" height="320" style="background:var(--bg-input);border-radius:8px">

          <!-- Quadrant Backdrops -->

          <!-- Top Left: Bullseye -->

          <rect x="${padLeft}" y="${padTop}" width="${midX - padLeft}" height="${midY - padTop}" fill="rgba(16, 185, 129, 0.08)" />

          <text x="${padLeft + 8}" y="${padTop + 14}" font-size="10" font-weight="700" fill="#10b981">🎯 BULLSEYE (Fast & Accurate)</text>



          <!-- Top Right: Careful -->

          <rect x="${midX}" y="${padTop}" width="${plotW - (midX - padLeft)}" height="${midY - padTop}" fill="rgba(59, 130, 246, 0.06)" />

          <text x="${midX + 8}" y="${padTop + 14}" font-size="10" font-weight="700" fill="#3b82f6">⏱️ CAREFUL (Accurate, Slow)</text>



          <!-- Bottom Left: Rushed Traps -->

          <rect x="${padLeft}" y="${midY}" width="${midX - padLeft}" height="${plotH - (midY - padTop)}" fill="rgba(239, 68, 68, 0.08)" />

          <text x="${padLeft + 8}" y="${padTop + plotH - 8}" font-size="10" font-weight="700" fill="#ef4444">⚠️ RUSHED TRAPS (Fast & Careless)</text>



          <!-- Bottom Right: Struggling -->

          <rect x="${midX}" y="${midY}" width="${plotW - (midX - padLeft)}" height="${plotH - (midY - padTop)}" fill="rgba(245, 158, 11, 0.06)" />

          <text x="${midX + 8}" y="${padTop + plotH - 8}" font-size="10" font-weight="700" fill="#f59e0b">🐢 NEEDS DRILL (Slow & Low Acc)</text>



          <!-- Dividing Grid Lines -->

          <line x1="${midX}" y1="${padTop}" x2="${midX}" y2="${padTop + plotH}" stroke="var(--border)" stroke-dasharray="4,4" stroke-width="1.5" />

          <line x1="${padLeft}" y1="${midY}" x2="${padLeft + plotW}" y2="${midY}" stroke="var(--border)" stroke-dasharray="4,4" stroke-width="1.5" />



          <!-- X & Y Axes -->

          <line x1="${padLeft}" y1="${padTop + plotH}" x2="${padLeft + plotW}" y2="${padTop + plotH}" stroke="var(--text-muted)" stroke-width="1" />

          <line x1="${padLeft}" y1="${padTop}" x2="${padLeft}" y2="${padTop + plotH}" stroke="var(--text-muted)" stroke-width="1" />



          <!-- Axis Labels -->

          <text x="${svgW / 2}" y="${svgH - 8}" text-anchor="middle" font-size="11" font-weight="600" fill="var(--text-secondary)">Pacing per Question (Seconds) →</text>

          <text x="12" y="${svgH / 2}" text-anchor="middle" font-size="11" font-weight="600" fill="var(--text-secondary)" transform="rotate(-90 12,${svgH / 2})">Accuracy % →</text>



          <!-- Ticks -->

          <text x="${padLeft}" y="${padTop + plotH + 16}" font-size="9" fill="var(--text-muted)">0s</text>

          <text x="${midX}" y="${padTop + plotH + 16}" text-anchor="middle" font-size="9" fill="var(--text-muted)">140s (Target)</text>

          <text x="${padLeft + plotW}" y="${padTop + plotH + 16}" text-anchor="end" font-size="9" fill="var(--text-muted)">240s</text>



          <text x="${padLeft - 6}" y="${padTop + plotH}" text-anchor="end" font-size="9" fill="var(--text-muted)">0%</text>

          <text x="${padLeft - 6}" y="${midY + 3}" text-anchor="end" font-size="9" fill="var(--text-muted)">70%</text>

          <text x="${padLeft - 6}" y="${padTop + 4}" text-anchor="end" font-size="9" fill="var(--text-muted)">100%</text>



          <!-- Subject Scatter Dots -->

          ${dots}

        </svg>

      </div>

    </div>`;

}



// ── ⚡ DEBOUNCED IDB USER STATE PERSISTENCE ───────────────────

let idbSaveDebounceTimer = null;

function debouncedIdbSaveUserData() {

  if (idbSaveDebounceTimer) clearTimeout(idbSaveDebounceTimer);

  idbSaveDebounceTimer = setTimeout(() => {

    idbSaveUserData(state.attempts, state.testSessions, state.srsQueue).catch(() => {});

  }, 400);

}





// ================================================================

// 🧮 TCS iON VIRTUAL NUMERIC KEYPAD & READINESS BENCHMARK ENGINE

// ================================================================



function buildNatKeypadHTML() {

  return `

    <div class="tcs-nat-keypad" id="tcs-nat-keypad">

      <div style="font-size:11px;font-weight:700;color:var(--text-muted);margin-bottom:8px;display:flex;justify-content:space-between;align-items:center">

        <span>TCS iON Virtual Keypad</span>

        <span style="font-size:10px;color:var(--accent)">On-Screen NAT</span>

      </div>

      <div class="tcs-keypad-grid">

        <button type="button" class="tcs-key-btn" onclick="inputNatKey('7')">7</button>

        <button type="button" class="tcs-key-btn" onclick="inputNatKey('8')">8</button>

        <button type="button" class="tcs-key-btn" onclick="inputNatKey('9')">9</button>

        <button type="button" class="tcs-key-btn" onclick="inputNatKey('4')">4</button>

        <button type="button" class="tcs-key-btn" onclick="inputNatKey('5')">5</button>

        <button type="button" class="tcs-key-btn" onclick="inputNatKey('6')">6</button>

        <button type="button" class="tcs-key-btn" onclick="inputNatKey('1')">1</button>

        <button type="button" class="tcs-key-btn" onclick="inputNatKey('2')">2</button>

        <button type="button" class="tcs-key-btn" onclick="inputNatKey('3')">3</button>

        <button type="button" class="tcs-key-btn" onclick="inputNatKey('0')">0</button>

        <button type="button" class="tcs-key-btn" onclick="inputNatKey('.')">.</button>

        <button type="button" class="tcs-key-btn" onclick="inputNatKey('-')">-</button>

      </div>

      <div class="tcs-keypad-actions">

        <button type="button" class="tcs-key-action-btn backspace-btn" onclick="inputNatKey('backspace')">⌫ Backspace</button>

        <button type="button" class="tcs-key-action-btn clear-btn" onclick="inputNatKey('clear')">✕ Clear</button>

      </div>

    </div>`;

}



function inputNatKey(key) {

  playUiClickSound();

  const inp = document.getElementById('nat-answer');

  if (!inp) return;

  if (key === 'clear') {

    inp.value = '';

  } else if (key === 'backspace') {

    inp.value = inp.value.slice(0, -1);

  } else if (key === '.') {

    if (!inp.value.includes('.')) inp.value += '.';

  } else if (key === '-') {

    if (inp.value === '') inp.value = '-';

    else if (inp.value.startsWith('-')) inp.value = inp.value.slice(1);

    else inp.value = '-' + inp.value;

  } else {

    inp.value += key;

  }

  inp.dispatchEvent(new Event('input', { bubbles: true }));

  if (typeof saveNATAnswer === 'function') saveNATAnswer(inp.value);

  if (typeof saveExamAutoSaveState === 'function') saveExamAutoSaveState();

}



// ── ⏩ EXAM PACING JUMP SHORTCUTS (Next Unanswered & Next Marked) ─

function jumpToNextUnanswered() {

  if (!state.activeTest) return;

  const { questions, answers, currentQ } = state.activeTest;

  const n = questions.length;

  for (let step = 1; step < n; step++) {

    const idx = (currentQ + step) % n;

    const a = answers[idx];

    const isUnanswered = a === null || a === undefined || (Array.isArray(a) && !a.length);

    if (isUnanswered) {

      jumpToTestQ(idx);

      showToast(`Jumped to Unanswered Q${idx + 1}`, 'info', 1500);

      return;

    }

  }

  showToast('🎉 All questions have been answered!', 'success', 2000);

}



function jumpToNextMarked() {

  if (!state.activeTest) return;

  const { questions, marked, currentQ } = state.activeTest;

  if (!marked || !marked.size) {

    showToast('No questions currently Marked for Review', 'info', 2000);

    return;

  }

  const n = questions.length;

  for (let step = 1; step < n; step++) {

    const idx = (currentQ + step) % n;

    if (marked.has(idx)) {

      jumpToTestQ(idx);

      showToast(`Jumped to Marked Q${idx + 1}`, 'info', 1500);

      return;

    }

  }

  showToast('Already on the only marked question', 'info', 1500);

}



// ── 🎯 GATE 2026 COMPREHENSIVE READINESS BENCHMARK ────────────

function buildGateReadinessCardHTML() {

  const { attempted, accuracy } = getStats();

  if (attempted < 3) return '';



  // 1. Syllabus coverage out of 87 chapters

  const touchedChapters = new Set();

  state.attempts.forEach(a => {

    const q = state.questions.find(x => x.id === a.questionId);

    if (q && q.subject && q.topic) touchedChapters.add(`${q.subject}|${q.topic}`);

  });

  const coveragePct = Math.min(100, Math.round((touchedChapters.size / 87) * 100));



  // 2. Accuracy score (Target >= 75%)

  const accScore = accuracy;



  // 3. Pacing efficiency

  let totalDwell = 0, countDwell = 0;

  state.attempts.forEach(a => {

    if (a.dwellSec) { totalDwell += a.dwellSec; countDwell++; }

  });

  const avgDwell = countDwell > 0 ? Math.round(totalDwell / countDwell) : 115;

  const pacingScore = Math.max(20, Math.min(100, Math.round(100 - Math.max(0, avgDwell - 140) * 0.6)));



  // 4. Streak consistency

  const streak = state.dailyStreak || 1;

  const consistencyScore = Math.min(100, streak * 20);



  // Overall readiness index: 35% Coverage + 35% Accuracy + 15% Pacing + 15% Consistency

  const readinessIndex = Math.min(100, Math.round(

    coveragePct * 0.35 +

    accScore * 0.35 +

    pacingScore * 0.15 +

    consistencyScore * 0.15

  ));



  let tierLabel = '📚 Foundation Stage';

  let tierColor = '#6c63ff';

  let tierAirEst = 'Target: Build Subject Depth';

  if (readinessIndex >= 82) {

    tierLabel = '🏆 Tier-1 Contender (Top 100 AIR)';

    tierColor = 'var(--green)';

    tierAirEst = 'IISc Bangalore / IIT Bombay / IIT Delhi Contender';

  } else if (readinessIndex >= 68) {

    tierLabel = '🌟 Tier-2 Range (Top 500 AIR)';

    tierColor = '#3b82f6';

    tierAirEst = 'Older IITs (IITM / IITK / IITKgp) Direct M.Tech';

  } else if (readinessIndex >= 50) {

    tierLabel = '📈 Competitive Range (Top 2,000 AIR)';

    tierColor = 'var(--accent)';

    tierAirEst = 'Newer IITs / Top NITs (Trichy / Surathkal / Warangal)';

  }



  return `

    <div class="gate-readiness-card">

      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;flex-wrap:wrap;gap:8px">

        <div>

          <div style="font-size:16px;font-weight:800;letter-spacing:0.3px">🎯 GATE 2026 Readiness Benchmark</div>

          <div style="font-size:11px;color:var(--text-muted);margin-top:2px">Holistic multi-pillar AI readiness evaluation based on ${attempted} attempted questions</div>

        </div>

        <span class="chip" style="background:rgba(255,255,255,0.08);color:${tierColor};font-weight:700;font-size:12px">${tierLabel}</span>

      </div>

      <div class="readiness-grid">

        <div class="readiness-ring-wrapper">

          <svg viewBox="0 0 120 120" width="110" height="110">

            <circle cx="60" cy="60" r="50" fill="none" stroke="var(--bg-input)" stroke-width="10" />

            <circle cx="60" cy="60" r="50" fill="none" stroke="${tierColor}" stroke-width="10"

              stroke-dasharray="314.16" stroke-dashoffset="${314.16 * (1 - readinessIndex / 100)}"

              stroke-linecap="round" transform="rotate(-90 60 60)" style="transition:stroke-dashoffset 0.8s ease" />

            <text x="60" y="56" text-anchor="middle" font-size="24" font-weight="900" fill="var(--text-primary)">${readinessIndex}%</text>

            <text x="60" y="74" text-anchor="middle" font-size="10" font-weight="700" fill="var(--text-muted)">READINESS</text>

          </svg>

          <div style="font-size:10.5px;color:var(--text-muted);margin-top:6px;text-align:center">${tierAirEst}</div>

        </div>

        <div class="readiness-pillars">

          <div class="readiness-pillar-row">

            <span class="readiness-pillar-label">🗺️ Syllabus Depth</span>

            <div class="readiness-pillar-bar-bg"><div class="readiness-pillar-bar-fill" style="width:${coveragePct}%;background:#6c63ff"></div></div>

            <span class="readiness-pillar-val">${coveragePct}%</span>

          </div>

          <div class="readiness-pillar-row">

            <span class="readiness-pillar-label">🎯 Attempt Accuracy</span>

            <div class="readiness-pillar-bar-bg"><div class="readiness-pillar-bar-fill" style="width:${accScore}%;background:var(--green)"></div></div>

            <span class="readiness-pillar-val">${accScore}%</span>

          </div>

          <div class="readiness-pillar-row">

            <span class="readiness-pillar-label">⚡ Pacing Efficiency</span>

            <div class="readiness-pillar-bar-bg"><div class="readiness-pillar-bar-fill" style="width:${pacingScore}%;background:#3b82f6"></div></div>

            <span class="readiness-pillar-val">${avgDwell}s/Q</span>

          </div>

          <div class="readiness-pillar-row">

            <span class="readiness-pillar-label">🔥 Practice Consistency</span>

            <div class="readiness-pillar-bar-bg"><div class="readiness-pillar-bar-fill" style="width:${consistencyScore}%;background:#f59e0b"></div></div>

            <span class="readiness-pillar-val">${streak}d Streak</span>

          </div>

        </div>

      </div>

    </div>`;

}



// ── ⚡ PRE-INDEXING FOR INSTANT GLOBAL SEARCH (10x Speedup) ───

function indexQuestionsForSearch(qs) {

  if (!Array.isArray(qs)) return;

  for (let i = 0; i < qs.length; i++) {

    const q = qs[i];

    if (!q._searchHaystack) {

      q._searchHaystack = ((q.question || '') + ' ' + (q.subject || '') + ' ' + (q.topic || '') + ' ' + (q.explanation || '')).toLowerCase();

    }

  }

}





// ================================================================

// 🛡️ DATA INTEGRITY & ANSWER KEY VALIDATION ENGINE

// ================================================================



function hasUsableAnswerKey(q) {

  if (!q) return false;

  if (q.type === 'nat') {

    return (Array.isArray(q.correct) && q.correct.length > 0 && typeof q.correct[0] === 'number') ||

           (q.natRange && typeof q.natRange.min === 'number' && typeof q.natRange.max === 'number');

  }

  return Array.isArray(q.correct) && q.correct.length > 0 && Array.isArray(q.options) && q.options.length > 0;

}



function evaluateQuestionAnswer(q, userAns) {

  if (!hasUsableAnswerKey(q)) {

    return { evaluated: false, correct: false, isUnscored: true };

  }

  if (userAns === null || userAns === undefined || (Array.isArray(userAns) && !userAns.length)) {

    return { evaluated: true, correct: false, skipped: true };

  }

  if (q.type === 'nat') {

    const v = parseFloat(userAns);

    if (isNaN(v)) return { evaluated: true, correct: false };

    const e = Array.isArray(q.correct) && q.correct.length > 0 ? q.correct[0] : null;

    const min = q.natRange?.min ?? e;

    const max = q.natRange?.max ?? e;

    const isOk = min !== null && max !== null && v >= min && v <= max;

    return { evaluated: true, correct: isOk };

  } else {

    const sel = (Array.isArray(userAns) ? userAns : [userAns]).slice().sort((a,b)=>a-b);

    const exp = (Array.isArray(q.correct) ? q.correct : [q.correct]).slice().sort((a,b)=>a-b);

    const isOk = sel.length === exp.length && sel.every((val, i) => val === exp[i]);

    return { evaluated: true, correct: isOk };

  }

}



// Content-hash deterministic ID generator for uploads (SHA-256)

async function contentId(q) {

  const canon = s => (s ?? '').toString().normalize('NFKC').toLowerCase().replace(/\s+/g, ' ').trim();

  const key = [

    canon(q.question),

    ...(q.options || []).map(canon).sort(),

    q.type || 'mcq'

  ].join('|');

  const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(key));

  return 'q_' + [...new Uint8Array(buf)].slice(0, 12).map(b => b.toString(16).padStart(2, '0')).join('');

}



// Numbers-aware and operator-preserving fuzzy near-duplicate check

function nearDuplicate(a, b) {

  if (!a || !b) return false;

  // If numeric values differ, it is a numerical variant, NOT a duplicate

  const getNumbers = s => ((s || '').match(/-?\d+(\.\d+)?/g) || []).join(',');

  if (getNumbers(a.question) !== getNumbers(b.question)) return false;



  // If options differ, it is a different question

  const optKey = q => (q.options || []).map(o => (o || '').trim().toLowerCase()).sort().join('|');

  if (optKey(a) !== optKey(b)) return false;



  // Jaccard similarity over word tokens preserving math operators

  const tokens = s => new Set((s || '').toLowerCase().match(/[a-z0-9_+\-<>=^/]+/g) || []);

  const tA = tokens(a.question);

  const tB = tokens(b.question);

  if (!tA.size || !tB.size) return false;

  let intersection = 0;

  tA.forEach(t => { if (tB.has(t)) intersection++; });

  const union = tA.size + tB.size - intersection;

  return (intersection / union) >= 0.88;

}




// ─── TCS iON SECTION SWITCHING & REVIEW FILTERING ────────────────────────────
function switchTestSection(sec) {
  if (!state.activeTest || !state.activeTest.questions) return;
  const targetQ = sec === 'ga' ? 0 : 10;
  if (targetQ < state.activeTest.questions.length) {
    jumpToTestQ(targetQ);
  }
}

function filterResultReview(status, btnEl) {
  document.querySelectorAll('.result-review-filters .chip').forEach(c => c.classList.remove('active'));
  if (btnEl) btnEl.classList.add('active');
  const cards = document.querySelectorAll('.review-q-card');
  cards.forEach(card => {
    if (status === 'all') {
      card.style.display = 'block';
    } else if (status === 'overtime') {
      card.style.display = card.getAttribute('data-overtime') === '1' ? 'block' : 'none';
    } else {
      card.style.display = card.getAttribute('data-review-status') === status ? 'block' : 'none';
    }
  });
}

function openCustomTestModal() {
  toggleCustomDrillModal(true);
}

function toggleCustomTestModal(open) {
  toggleCustomDrillModal(open);
}



// ─── TCS iON QUESTION PAPER FULL OVERVIEW ────────────────────────────────────
function openExamQuestionPaper() {
  if (!state.activeTest || !state.activeTest.questions) {
    showToast('No active exam paper to display', 'info');
    return;
  }
  const modal = document.getElementById('exam-qp-modal');
  const backdrop = document.getElementById('exam-qp-backdrop');
  const title = document.getElementById('exam-qp-title');
  if (title && state.activeTest.mock) {
    title.textContent = `${state.activeTest.mock.name} — Full Question Paper`;
  }
  renderExamQuestionPaper('all');
  if (modal && backdrop) {
    modal.classList.add('active');
    backdrop.classList.add('active');
  }
}

function closeExamQuestionPaper() {
  const modal = document.getElementById('exam-qp-modal');
  const backdrop = document.getElementById('exam-qp-backdrop');
  if (modal) modal.classList.remove('active');
  if (backdrop) backdrop.classList.remove('active');
}

function filterExamQuestionPaper(sec, btnEl) {
  const filters = document.getElementById('exam-qp-filters');
  if (filters && btnEl) {
    filters.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
    btnEl.classList.add('active');
  }
  renderExamQuestionPaper(sec);
}

function renderExamQuestionPaper(filter = 'all') {
  const body = document.getElementById('exam-qp-body');
  if (!body || !state.activeTest || !state.activeTest.questions) return;
  const questions = state.activeTest.questions;
  const labels = ['A', 'B', 'C', 'D', 'E'];

  let items = questions.map((q, idx) => ({ q, idx }));
  if (filter === 'ga') {
    items = items.filter(it => it.idx < 10);
  } else if (filter === 'cs') {
    items = items.filter(it => it.idx >= 10);
  }

  body.innerHTML = items.map(({ q, idx }) => `
    <div class="exam-qp-item" id="qp-item-${idx}">
      <div class="exam-qp-item-meta">
        <div style="display:flex;align-items:center;gap:8px">
          <span class="chip" style="font-weight:700">Q${idx + 1}</span>
          <span class="chip chip-info">${idx < 10 && questions.length >= 65 ? 'General Aptitude' : q.subject || 'CS'}</span>
          <span class="q-badge ${q.type}">${q.type?.toUpperCase()}</span>
          <span class="chip ${q.type === 'mcq' ? 'penalty-chip' : 'zero-penalty-chip'}">+${q.marks} / ${q.type === 'mcq' ? `-${(q.marks/3).toFixed(2)}` : '0 penalty'}</span>
        </div>
        <button class="btn btn-primary btn-sm" onclick="closeExamQuestionPaper(); jumpToTestQ(${idx});" type="button" style="padding:3px 10px;font-size:12px;font-weight:700">
          ▶ Jump to Q${idx + 1}
        </button>
      </div>
      <div class="exam-qp-qtext">${formatQuestionContent(q.question)}</div>
      ${q.options && q.options.length ? `
        <div class="exam-qp-options">
          ${q.options.map((opt, optIdx) => `
            <div style="font-size:13px;padding:6px 10px;background:var(--bg-card);border:1px solid var(--border);border-radius:8px">
              <strong>${labels[optIdx]}.</strong> ${formatQuestionContent(opt)}
            </div>
          `).join('')}
        </div>` : ''}
    </div>
  `).join('');

  if (window.renderMath) renderMath(body);
}

// ─── TCS iON EXAM INSTRUCTIONS ───────────────────────────────────────────────
function openExamInstructions() {
  const modal = document.getElementById('exam-inst-modal');
  const backdrop = document.getElementById('exam-inst-backdrop');
  if (modal && backdrop) {
    modal.classList.add('active');
    backdrop.classList.add('active');
  }
}

function closeExamInstructions() {
  const modal = document.getElementById('exam-inst-modal');
  const backdrop = document.getElementById('exam-inst-backdrop');
  if (modal) modal.classList.remove('active');
  if (backdrop) backdrop.classList.remove('active');
}

// ─── DIAGRAM LIGHTBOX (CLICK-TO-ZOOM) ────────────────────────────────────────
let currentLightboxScale = 1;

function openDiagramLightbox(src, title) {
  const modal = document.getElementById('diagram-lightbox-card');
  const backdrop = document.getElementById('diagram-lightbox-backdrop');
  const img = document.getElementById('diagram-lightbox-img');
  const titleEl = document.getElementById('diagram-lightbox-title');
  if (!modal || !backdrop || !img) return;

  img.src = src;
  currentLightboxScale = 1;
  img.style.transform = `scale(1)`;
  if (titleEl && title) titleEl.textContent = `🔍 ${title}`;

  modal.classList.add('active');
  backdrop.classList.add('active');
}

function closeDiagramLightbox() {
  const modal = document.getElementById('diagram-lightbox-card');
  const backdrop = document.getElementById('diagram-lightbox-backdrop');
  if (modal) modal.classList.remove('active');
  if (backdrop) backdrop.classList.remove('active');
}

function zoomDiagramLightbox(delta) {
  const img = document.getElementById('diagram-lightbox-img');
  if (!img) return;
  currentLightboxScale = Math.max(0.4, Math.min(3.5, currentLightboxScale + delta));
  img.style.transform = `scale(${currentLightboxScale})`;
}

function resetDiagramLightboxZoom() {
  const img = document.getElementById('diagram-lightbox-img');
  if (!img) return;
  currentLightboxScale = 1;
  img.style.transform = `scale(1)`;
}

// Global click delegate for diagram images
document.addEventListener('click', (e) => {
  const target = e.target;
  if (target && target.tagName === 'IMG' && (target.closest('.q-diagram-container') || target.closest('.question-text') || target.closest('.option-text'))) {
    e.preventDefault();
    openDiagramLightbox(target.src, target.alt || 'GATE Diagram');
  }
});

// ─── 1-CLICK SHAREABLE PERFORMANCE SCORECARD ────────────────────────────────
function copyScorecardToClipboard() {
  if (!state.activeTestResults) return;
  const { session } = state.activeTestResults;
  const pred = calculateGatePrediction(session.score);
  const acc = session.attemptedCount > 0 ? Math.round((session.correctCount / session.attemptedCount) * 100) : 0;
  
  const text = `🎯 GATE Mock Exam Scorecard: ${session.mockName || 'GATE Full Mock'}\n` +
               `📊 Marks: ${session.score} / ${session.totalMarks || 100} (${session.percentage}%)\n` +
               `🏆 Estimated AIR: ${pred.air} (Score: ${pred.score}/1000)\n` +
               `✅ Correct: ${session.correctCount} | ❌ Wrong: ${session.incorrectCount} | ⚪ Skipped: ${session.unattemptedCount}\n` +
               `⚡ Accuracy: ${acc}%\n` +
               `⏱️ Duration: ${fmtH(session.timeSpentSeconds || 0)}\n` +
               `🔗 Practiced on GATE CSE Platform (${(state.questions && state.questions.length ? state.questions.length.toLocaleString() : "32,383")} Questions & TCS iON Simulator)`;

  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text).then(() => {
      showToast('📋 Scorecard copied to clipboard!', 'success');
    }).catch(() => {
      showToast('Failed to copy scorecard to clipboard', 'error');
    });
  } else {
    showToast('Clipboard API unavailable in this browser', 'info');
  }
}

// ─── GLOBAL SEARCH SUBJECT FILTER ───────────────────────────────────────────
function setGlobalSearchSubject(sub) {
  state.globalSearchSubject = sub;
  const input = document.getElementById('global-search-input');
  if (input) executeGlobalSearch(input.value);
}

Object.assign(window, {
  openExamQuestionPaper,

  closeExamQuestionPaper,

  filterExamQuestionPaper,

  renderExamQuestionPaper,

  openExamInstructions,

  closeExamInstructions,

  openDiagramLightbox,

  closeDiagramLightbox,

  zoomDiagramLightbox,

  resetDiagramLightboxZoom,

  copyScorecardToClipboard,

  setGlobalSearchSubject,

  switchTestSection,

  filterResultReview,

  openCustomTestModal,

  toggleCustomTestModal,


  ADMIN_EMAILS,

  checkIsAdminUser,

  hasUsableAnswerKey,

  evaluateQuestionAnswer,

  contentId,

  nearDuplicate,

  buildNatKeypadHTML,

  inputNatKey,

  jumpToNextUnanswered,

  jumpToNextMarked,

  buildGateReadinessCardHTML,

  indexQuestionsForSearch,

  toggleSoundFx,

  playUiClickSound,

  playUiSuccessChime,

  playUiWarningChime,

  showExamMilestoneNotice,

  setBookmarkTag,

  openBookmarkTagPicker,

  closeAllBookmarkTagPickers,

  setBookmarkTagFilter,

  getFormulaHintForQuestion,

  toggleFormulaHint,

  printSyllabusWallSheet,

  buildSpeedAccuracyScatterSVG,

  debouncedIdbSaveUserData,



  // Elite Tier Improvements Exports

  toggleScribblePad,

  initScribblePadCanvas,

  setScribbleTool,

  setScribbleColor,

  clearScribbleCanvas,

  toggleScribbleGrid,

  toggleExamStrictMode,

  buildNegativeMarksAuditHTML,

  buildGaussianBellCurveSVG,

  buildSyllabusCoverageAuditHTML,

  drillUnexploredChapters,

  convertMistakesToFlashcards,

  openSprintModal,

  toggleSprintModal,

  handleLaunchSprintFromModal,

  launchSectionSprint,

  openCompareModal,

  toggleCompareModal,

  updateComparisonView,

  toggleZenMode,

  exportGateProfileBackup,

  triggerRestoreProfileBackup,

  handleRestoreProfileBackupFile,



  // v6.0 Comprehensive Enhancements Exports

  applyThemeMode,

  toggleThemeMode,

  openReportModal,

  closeReportModal,

  submitReport,

  openRandomQuestion,

  copyQuestionText,

  promptChangeDailyGoal,

  startSRSReviewSession,

  getSRSDueCount,

  updateSRSAfterAttempt,

  getWeakTopics,

  buildFocusZoneHTML,

  buildStudyPlannerHTML,

  buildScoreHistoryHTML,

  buildSectionAnalysisHTML,

  buildQuestionTimeHeatmapHTML,

  scrollToResultQ,

  toggleSidebarSubjects,

  toggleTopbarToolsMenu,

  closeTopbarToolsMenu,

  updateSidebarSubjectProgress,

  toggleStudyTarget,

  addStudyTargetPrompt,

  deleteStudyTarget,

  addQuickTarget,

  highlightCodeBlocks,

  showMockRatingMatrix,

  closeMockModal,

  state,

  MOCK_TESTS,

  getMockQuestions,

  formatQuestionContent,

  renderMath,

  updateMockSearch,

  setMockSubSeries,
  setMockViewMode,
  togglePinMock,
  openMockRetakeCompare,

  // Navigation & Mobile

  navigate,

  toggleMobileSidebar: () => window.toggleMobileSidebar?.(),

  closeMobileSidebar:  () => window.closeMobileSidebar?.(),

  openMobileSidebar:   () => window.openMobileSidebar?.(),



  // Practice & Pagination

  updateFilter,

  togglePracticePyqFilter,

  updatePracticeSort,

  resetPracticeQuickFilters,

  isQuestionPyq,

  updatePracticeSearch,

  setPracticePage,

  setPracticePageSize,

  startPracticeMode,

  openSingleQuestion,

  prevPracticeQuestion,

  nextPracticeQuestion,

  submitPracticeAnswer,

  skipQuestion,

  jumpToPracticeQ,

  closePracticeMode,

  toggleTestPalette,



  // Bookmarks & Star

  toggleBookmark,



  // GATE Virtual Scientific Calculator

  toggleGateCalc,

  setCalcAngle,

  calcInput,

  calcClear,

  calcClearEntry,

  calcBackspace,

  calcMem,

  calcFn,

  calcEval,



  // Keyboard Shortcuts Modal

  toggleShortcutsModal,



  // Seven High-Impact Upgrades

  saveExamAutoSaveState,

  clearExamAutoSave,

  resumeSavedExam,

  discardSavedExam,

  updatePaletteStates,

  buildMasteryMatrixHTML,

  buildDataPortabilityCardHTML,

  toggleCustomDrillModal,

  toggleSelectAllDrillSubjects,

  launchCustomDrill,

  exportUserData,

  triggerRestoreFilePrompt,

  handleRestoreProgressFile,

  promptQuestionNote,

  saveQuestionNote,

  toggleExamChimes,



  // Formula Flashcards (Spaced Repetition)

  FORMULA_FLASHCARDS,

  getMatchingFlashcard,

  getMatchingFlashcardId,

  buildQuestionHintHTML,

  togglePracticeHint,

  toggleFormulaFlashcards,

  openFormulaFlashcardsModal,

  renderActiveFlashcard,

  flipActiveFlashcard,

  navFlashcard,

  shuffleFlashcardDeck,

  rateFlashcard,

  filterFlashcardDeck,









  // Topic-Wise GATE CSE PYQs Hub

  // Elite GATE Intelligence Modules

  setErrorTag,

  buildErrorTagButtonsHTML,

  getLossDiagnosis,

  buildLossDiagnosisHTML,

  setMistakeTagFilter,

  buildGateWeightageHeatmapHTML,

  launchHighYieldDrill,

  buildQuadrantAnalysisHTML,

  drillBlackHoleQuestions,

  initDefaultPlaylists,

  openPlaylistModal,

  closePlaylistModal,

  toggleQuestionInPlaylist,

  handleCreatePlaylistFromModal,

  deletePlaylist,

  startPlaylistPractice,

  renderPlaylists,

  setMethodTab,

  buildMultiMethodExplanationHTML,

  saveStudentQuestionNote,

  buildStudentShortcutNoteHTML,



  getTopicPYQChapter,

  setTopicPyqTab,

  setTopicPyqSubject,

  updateTopicPyqSearch,

  setTopicPyqDifficulty,

  setTopicPyqType,

  toggleSyllabusGuide,

  filterSyllabusCategory,

  filterSyllabusSearch,

  jumpToSubjectPYQs,

  buildOfficialSyllabusGuideHTML,



  // Strategic Intelligence & Enhanced Mastery

  getExamCountdownData,

  initExamCountdownAndStreak,

  recordDailyAttemptForStreak,

  openGlobalSearch,

  closeGlobalSearch,

  handleGlobalSearchInput,

  setGlobalSearchFilter,

  executeGlobalSearch,

  startSingleQuestionPractice,

  buildMasteryRadarChartSVG,

  setQuestionConfidence,

  buildConfidenceSelectorHTML,

  getExpectedValueAnalysis,

  buildExpectedValueCardHTML,

  startFormulaBlitz,

  renderFormulaBlitzView,

  revealBlitzFormula,

  advanceBlitzCard,

  finishFormulaBlitz,

  stopFormulaBlitz,

  buildNatToleranceHTML,

  generatePrintableWorksheet,

  exportReviewWorksheetPDF,

  toggleTopicPYQDrawer,

  startTopicPYQPractice,

  launchRandomTopicDrill,



  // Advanced Improvements & Simulators

  toggleExamFullscreen,

  printTestReport,

  setupCalcDraggable,

  calculateGatePrediction,

  buildPredictorCardHTML,

  updatePredictorMarks,

  updatePredictorCategory,

  renderMistakes,

  setMistakeStatusFilter,

  setMistakeSubjectFilter,

  updateMistakeSearch,

  markMistakeResolved,

  startMistakeReTest,

  triggerPwaInstall,



  // Mock Paper & Practice Papers

  setMockSort,

  toggleCalibrationTable,

  viewMockPaper,

  setMockPaperPage,

  setMockPaperPageSize,

  closeMockPaperView,

  startMockPaperPractice,

  startPracticePaperDirect,

  renderPracticePapers,

  renderPyqExams,

  setPyqExamEraFilter,

  setPyqExamDiffFilter,

  setPyqExamSort,

  // Subject Tests
  renderSubjectTests,
  setSubjectTestSubject,
  setSubjectTestDiff,
  setSubjectTestLevel,
  handleSubjectTestSearch,
  buildSubjectTestsGrid,

  // Repeating Patterns Hub & Archival Question Bank
  renderRepeatingPatterns,
  switchPatternTab,
  setPatternSubject,
  setPatternRecurrence,
  setPatternSort,
  handlePatternSearch,



  // PYQs & Pagination

  updatePYQFilter,

  updatePYQSearch,

  setPYQPage,

  setPYQPageSize,

  startPYQPractice,



  // Test engine

  startMockTest,

  saveAndNextTestQ,

  markForReview,

  clearTestResponse,

  jumpToTestQ,

  confirmSubmitTest,

  submitMockTest,

  switchMockTab,

  setMockLevelFilter,

  saveNATAnswer,

  closeResult,



  // Upload

  switchUploadTab,

  handleFileUpload,

  handleDrop,

  handleDeleteQ,

  downloadSampleJSON,

  onTypeChange,

  onCategoryChange,

  addOptRow,

  submitManualQuestion,

  clearManualForm,

  clearAllQuestions,

  handleDeleteMyQ,



  // Auth & Init

  handleSignOut,

  bootApp,

  removeLoginPage,

  continueAsGuest,

});



