import { useEffect, useState } from 'react'

import './App.css'

import ReactMarkdown from 'react-markdown'

import remarkGfm from 'remark-gfm'

type Page = 'Chat' | 'History' | 'Documents' | 'Help & About'

type Message = {

  role: 'user' | 'assistant'

  text: string

  sources?: { source?: string | null; page?: number | null }[]

}

type HistoryItem = {

  id: number | string

  question: string

  answer: string

  created_at: string

}

const documents = [

  {

    name: 'Undergraduate — Malaysian',

    file: 'IIUM_TUITION FEES MALAYSIAN UNDERGRADUATED.pdf',

    group: 'Undergraduate',

    audience: 'Malaysian',

  },

  {

    name: 'Undergraduate — International',

    file: 'IIUM_TUITION FEES INTERNATIONAL UNDERGRADUATED.pdf',

    group: 'Undergraduate',

    audience: 'International',

  },

  {

    name: "Master's — Malaysian",

    file: 'IIUM_TUITION FEES MALAYSIAN MASTER.pdf',

    group: "Master's",

    audience: 'Malaysian',

  },

  {

    name: "Master's — International",

    file: 'IIUM_TUITION FEES INTERNATIONAL MASTER.pdf',

    group: "Master's",

    audience: 'International',

  },

]

const suggestions = [

  'What are the graduation requirements?',

  'How do I apply for leave of absence?',

  'What are the rules for course registration?',

]

function cleanAnswer(text: string): string {
  return text
    // Convert escaped Markdown bold into normal Markdown
    .replace(/\\\*\\\*/g, '**')
    // Remove citations because sources are displayed separately
    .replace(/【[^】]*】/g, '')
    // Remove extra citation-only lines
    .replace(/^\s*>>.*$/gm, '')
    // Remove excessive blank lines
    .replace(/\n{3,}/g, '\n\n')
    .trim()
}

function formatHistoryAnswer(text: string): string {
  if (!text) return ''
  return text
    // Convert citations like 【1†page 8】 or 【page 8】 to [Page 8]
    .replace(/【\d*†?page\s*(\d+)】/gi, '[Page $1]')
    // Convert general source tokens like 【1†source】 if present
    .replace(/【[^】]*】/g, '')
    // Fix unescaped markdown bold tokens if any
    .replace(/\\\*\\\*/g, '**')
    // Remove excessive trailing newlines
    .replace(/\n{3,}/g, '\n\n')
    .trim()
}

function App() {

  const [page, setPage] = useState<Page>('Chat')

  const [language, setLanguage] = useState<'EN' | 'BM'>('EN')

  const [question, setQuestion] = useState('')

  const [messages, setMessages] = useState<Message[]>([])

  const [notice, setNotice] = useState('')

  const [loading, setLoading] = useState(false)

  const [historyRecords, setHistoryRecords] = useState<HistoryItem[]>([])

  const [historyLoading, setHistoryLoading] = useState(false)

  const [historyError, setHistoryError] = useState('')

  const [historyReload, setHistoryReload] = useState(0)

  const [documentSearch, setDocumentSearch] = useState('')

  const [documentLevel, setDocumentLevel] = useState('All')

  const [documentAudience, setDocumentAudience] = useState('All')

  const isBM = language === 'BM'

  const filteredDocuments = documents.filter((doc) => {

    const searchText = documentSearch.toLowerCase().trim()

    const matchesSearch =

      !searchText ||

      doc.name.toLowerCase().includes(searchText) ||

      doc.file.toLowerCase().includes(searchText)

    const matchesLevel =

      documentLevel === 'All' || doc.group === documentLevel

    const matchesAudience =

      documentAudience === 'All' ||

      doc.audience === documentAudience

    return matchesSearch && matchesLevel && matchesAudience

  })

  useEffect(() => {

    if (page !== 'History') return

    let cancelled = false

    async function loadHistory() {

      setHistoryLoading(true)

      setHistoryError('')

      try {

        const response = await fetch(

          'http://127.0.0.1:8000/history?limit=20'

        )

        if (!response.ok) {

          throw new Error(`Server error: ${response.status}`)

        }

        const data = await response.json()

        if (!cancelled) {

          setHistoryRecords(

            Array.isArray(data.history) ? data.history : []

          )

        }

      } catch (error) {

        console.error('Failed to load history:', error)

        if (!cancelled) {

          setHistoryError(

            isBM

              ? 'Tidak dapat memuatkan sejarah. Pastikan backend sedang berjalan.'

              : 'Could not load history. Please make sure the backend is running.'

          )

        }

      } finally {

        if (!cancelled) {

          setHistoryLoading(false)

        }

      }

    }

    loadHistory()

    return () => {

      cancelled = true

    }

  }, [page, historyReload, isBM])

  async function sendQuestion(value = question) {

    const trimmed = value.trim()

    if (!trimmed || loading) return

    setMessages((current) => [

      ...current,

      { role: 'user', text: trimmed },

    ])

    setQuestion('')

    setNotice('')

    setLoading(true)

    try {

      const response = await fetch('http://127.0.0.1:8000/ask', {

        method: 'POST',

        headers: {

          'Content-Type': 'application/json',

        },

        body: JSON.stringify({ query: trimmed }),

      })

      if (!response.ok) {

        throw new Error(`Server error: ${response.status}`)

      }

      const data = await response.json()

      setMessages((current) => [

        ...current,

        {

          role: 'assistant',

          text: data.answer ?? 'No answer was returned.',

          sources: data.sources ?? [],

        },

      ])

    } catch (error) {

      console.error('Failed to get an answer:', error)

      setNotice(

        isBM

          ? 'Tidak dapat menyambung ke pelayan. Pastikan backend sedang berjalan.'

          : 'Could not connect to the server. Please make sure the backend is running.'

      )

    } finally {

      setLoading(false)

    }

  }

  function startNewChat() {
    if (loading) return

    if (messages.length > 0) {
      const confirmed = window.confirm(
        isBM
          ? 'Mulakan sembang baharu? Mesej pada skrin ini akan dikosongkan, tetapi sejarah yang telah disimpan tidak akan dipadam.'
          : 'Start a new chat? Messages on this screen will be cleared, but saved history will not be deleted.',
      )

      if (!confirmed) return
    }

    setMessages([])
    setQuestion('')
    setNotice('')
  }

  const navItems: { name: Page; icon: string; description: string }[] = [

    { name: 'Chat', icon: '✳', description: isBM ? 'Tanya tentang polisi' : 'Ask about policies' },

    { name: 'History', icon: '◷', description: isBM ? 'Soalan terdahulu' : 'Your previous questions' },

    { name: 'Documents', icon: '▤', description: isBM ? 'Polisi universiti' : 'University policies' },

    { name: 'Help & About', icon: '?', description: isBM ? 'Panduan dan maklumat' : 'Guidance and information' },

  ]

  return (

    <div className="app-shell">

      <aside className="sidebar">

        <div className="brand">

          <div className="logo-box">
            <img src="/images/iium-logo.png" alt="IIUM Logo" />
          </div>

          <div className="brand-copy">

            <strong>Policy Assistant</strong>

            <span>STUDENT SUPPORT</span>

          </div>

        </div>

        <div className="sidebar-label">{isBM ? 'MENU UTAMA' : 'MAIN MENU'}</div>

        <nav className="navigation">

          {navItems.map((item) => (

            <button

              key={item.name}

              className={`nav-item ${page === item.name ? 'active' : ''}`}

              onClick={() => {

                setPage(item.name)

                setNotice('')

              }}

            >

              <span className="nav-icon">{item.icon}</span>

              <span className="nav-copy">

                <strong>

                  {isBM

                    ? ({ Chat: 'Sembang', History: 'Sejarah', Documents: 'Dokumen', 'Help & About': 'Bantuan & Maklumat' } as Record<Page, string>)[item.name]

                    : item.name}

                </strong>

                <small>{item.description}</small>

              </span>

              {page === item.name && <span className="active-dot" />}

            </button>

          ))}

        </nav>

        <div className="sidebar-spacer" />

        <div className="privacy-card">

          <div className="privacy-icon">✦</div>

          <strong>{isBM ? 'Panduan yang lebih jelas' : 'Clarity for every student'}</strong>

          <p>

            {isBM

              ? 'Cari panduan berdasarkan dokumen polisi universiti.'

              : 'Find guidance based on university policy documents.'}

          </p>

        </div>



      </aside>

      <main className="main-area">

        <header className="topbar">

          <div className="breadcrumb">

            <span>IIUM</span>

            <span className="breadcrumb-slash">/</span>

            <strong>{page}</strong>

          </div>

          <div className="topbar-right">

            <span className="topbar-status"><span className="status-dot" /> {isBM ? 'Sistem Dalam Talian' : 'System Online'}</span>

            <div className="language-switch" aria-label="Language">

              <button className={language === 'EN' ? 'selected' : ''} onClick={() => setLanguage('EN')}>EN</button>

              <button className={language === 'BM' ? 'selected' : ''} onClick={() => setLanguage('BM')}>BM</button>

            </div>

          </div>

        </header>

        <div className="page-content">

          {page === 'Chat' && (

            <section className="chat-page">

              <div className="welcome-badge"><span>✦</span> {isBM ? 'PEMBANTU POLISI IIUM' : 'IIUM POLICY ASSISTANT'}</div>

              <h1>

                {isBM ? 'Assalamualaikum,' : 'Assalamualaikum,'}<br />

                <span>{isBM ? 'ada yang boleh saya bantu?' : 'how can I help you today?'}</span>

              </h1>

              <p className="welcome-description">

                {isBM

                  ? 'Tanya soalan tentang polisi akademik IIUM dan dapatkan panduan berdasarkan dokumen universiti.'

                  : 'Ask questions about IIUM academic policies and get guidance based on university documents.'}

              </p>

              <div className="chat-workspace">

                <div className="workspace-heading">

                  <div className="workspace-icon">✳</div>

                  <div>

                    <strong>{isBM ? 'Apa yang ingin anda ketahui?' : 'What would you like to know?'}</strong>

                    <p>{isBM ? 'Pilih soalan atau taip pertanyaan anda.' : 'Choose a suggested question or type your own.'}</p>

                  </div>

                </div>

                <div className="chat-actions">
                  <button
                    type="button"
                    className="chat-action-button"
                    onClick={startNewChat}
                    disabled={loading}
                    title={isBM ? 'Mulakan sembang baharu' : 'Start a new chat'}
                  >
                    <span aria-hidden="true">＋</span>
                    {isBM ? 'Sembang baharu' : 'New Chat'}
                  </button>

                </div>

                {messages.length === 0 ? (

                  <div className="suggestion-list">

                    {suggestions.map((item, index) => (

                      <button key={item} className="suggestion" onClick={() => sendQuestion(item)}>

                        <span className="suggestion-number">0{index + 1}</span>

                        <span>{isBM

                          ? [

                              'Apakah syarat untuk bergraduasi?',

                              'Bagaimanakah saya memohon cuti?',

                              'Apakah peraturan pendaftaran kursus?',

                            ][index]

                          : item}</span>

                        <span className="suggestion-arrow">↗</span>

                      </button>

                    ))}

                  </div>

                ) : (

          <div className="message-list">

            {messages.map((message, index) => (

              <div

                className={`message-row ${message.role}`}

                key={`${index}-${message.role}`}

              >

                {message.role === 'assistant' && (

                  <div className="message-avatar ai-avatar">✳</div>

                )}

                <div className="message-content">

                  <small className="message-label">

                    {message.role === 'user'

                      ? (isBM ? 'ANDA' : 'YOU')

                      : 'IIUM AI ASSISTANT'}

                  </small>

                  <div className="message-bubble">

                    {message.role === 'assistant' ? (

                      <div className="markdown-answer">

                        <ReactMarkdown

                          remarkPlugins={[remarkGfm]}

                          components={{

                            a: ({ href, children }) => (

                              <a

                                href={href}

                                target="_blank"

                                rel="noreferrer"

                              >

                                {children}

                              </a>

                            ),

                          }}

                        >

                          {cleanAnswer(message.text)}

                        </ReactMarkdown>

                      </div>

                    ) : (

                      <p>{message.text}</p>

                    )}

                  </div>

                  {message.role === 'assistant' &&

                    message.sources &&

                    message.sources.length > 0 && (

                      <div className="message-sources">

                        <strong>{isBM ? 'Sumber rujukan' : 'Sources'}</strong>

                        {message.sources.map((source, sourceIndex) => (

                          <a

                            className="source-item source-link"

                            key={`${source.source}-${source.page}-${sourceIndex}`}

                            href={`/documents/${encodeURIComponent(source.source ?? '')}${

                              source.page != null ? `#page=${source.page}` : ''

                            }`}

                            target="_blank"

                            rel="noreferrer"

                          >

                            <span className="source-icon">PDF</span>

                            <span>

                              {source.source ?? 'Policy document'}

                              {source.page != null ? ` · Page ${source.page}` : ''}

                            </span>

                          </a>

                        ))}

                      </div>

                    )}

                </div>

                {message.role === 'user' && (

                  <div className="message-avatar user-avatar">Y</div>

                )}

              </div>

            ))}

            {loading && (

              <div className="message-row assistant">

                <div className="message-avatar ai-avatar">✳</div>

                <div className="message-content">

                  <small className="message-label">IIUM AI ASSISTANT</small>

                  <div className="message-bubble loading-bubble">

                    <span className="loading-dot" />

                    <span className="loading-dot" />

                    <span className="loading-dot" />

                    <span className="loading-text">

                      {isBM ? 'Sedang menyediakan jawapan...' : 'Thinking...'}

                    </span>

                  </div>

                </div>

              </div>

            )}

            {notice && <p className="connection-note">{notice}</p>}

          </div>

                )}

                <form className="composer" onSubmit={(event) => { event.preventDefault(); sendQuestion() }}>

                  <textarea

                    value={question}

                    onChange={(event) => setQuestion(event.target.value)}

                    onKeyDown={(event) => {

                      if (event.key === 'Enter' && !event.shiftKey) {

                        event.preventDefault()

                        sendQuestion()

                      }

                    }}

                    placeholder={isBM ? 'Tanya soalan tentang polisi IIUM...' : 'Ask anything about IIUM policies...'}

                    rows={2}

                    aria-label="Your policy question"

                  />

                  <div className="composer-bottom">

                    <span>↳ {isBM ? 'Jawapan berdasarkan dokumen polisi' : 'Answers grounded in policy documents'}</span>

                    <button type="submit" className="send-button" disabled={!question.trim()}>

                      {isBM ? 'Hantar soalan' : 'Ask question'} <span>↑</span>

                    </button>

                  </div>

                </form>

                <div className="disclaimer">✦ {isBM ? 'Sila sahkan keputusan penting dengan pihak universiti.' : 'Please confirm important decisions with the university.'}</div>

              </div>

              <div className="bottom-note"><span>IIUM</span> · International Islamic University Malaysia</div>

            </section>

          )}

          {page === 'History' && (

            <div className="history-page">

              <div className="history-heading">

                <div>

                  <p className="history-eyebrow">

                    {isBM ? 'ARKIB PERBUALAN' : 'CONVERSATION ARCHIVE'}

                  </p>

                  <h2>

                    {isBM ? 'Sejarah Soalan' : 'Your Question History'}

                  </h2>

                  <p className="history-description">

                    {isBM

                      ? 'Lihat soalan dan jawapan yang pernah anda hantar.'

                      : 'Review your previous questions and AI answers.'}

                  </p>

                </div>

                <button

                  type="button"

                  className="history-refresh"

                  onClick={() => setHistoryReload((current) => current + 1)}

                  disabled={historyLoading}

                >

                  {historyLoading

                    ? (isBM ? 'Memuatkan...' : 'Loading...')

                    : (isBM ? '↻ Muat semula' : '↻ Refresh')}

                </button>

              </div>

              {historyLoading && historyRecords.length === 0 && (

                <div className="history-status">

                  {isBM

                    ? 'Sedang memuatkan sejarah soalan...'

                    : 'Loading your question history...'}

                </div>

              )}

              {historyError && (

                <div className="history-error">

                  <p>{historyError}</p>

                  <button

                    type="button"

                    className="history-refresh"

                    onClick={() => setHistoryReload((current) => current + 1)}

                  >

                    {isBM ? 'Cuba lagi' : 'Try again'}

                  </button>

                </div>

              )}

              {!historyLoading &&

                !historyError &&

                historyRecords.length === 0 && (

                  <div className="history-empty">

                    <div className="history-empty-icon">◷</div>

                    <h3>

                      {isBM ? 'Belum ada sejarah' : 'No history yet'}

                    </h3>

                    <p>

                      {isBM

                        ? 'Soalan yang anda hantar akan muncul di sini.'

                        : 'Questions you ask the assistant will appear here.'}

                    </p>

                    <button

                      type="button"

                      className="history-refresh"

                      onClick={() => setPage('Chat')}

                    >

                      {isBM ? 'Mula bertanya' : 'Ask a question'}

                    </button>

                  </div>

                )}

              {historyRecords.length > 0 && (

                              <div className="history-list">

                                {historyRecords.map((item) => (

                                  <article className="history-item" key={item.id}>

                                    <div className="history-item-top">

                                      <span className="history-tag">

                                        {isBM ? 'SOALAN' : 'QUESTION'}

                                      </span>

                                      <time className="history-date">

                                        {item.created_at &&

                                          !Number.isNaN(Date.parse(item.created_at))

                                          ? new Date(item.created_at).toLocaleString(

                                              isBM ? 'ms-MY' : 'en-MY',

                                              {

                                                dateStyle: 'medium',

                                                timeStyle: 'short',

                                              }

                                            )

                                          : ''}

                                      </time>

                                    </div>

                                    <h3 className="history-question">{item.question}</h3>

                                    <div className="history-answer-label">

                                      {isBM ? 'JAWAPAN AI' : 'AI ANSWER'}

                                    </div>

                                    {/* Render Formatted Markdown & Tables */}

                                    <div className="markdown-answer history-answer-markdown">

                                      {item.answer ? (

                                        <ReactMarkdown remarkPlugins={[remarkGfm]}>

                                          {formatHistoryAnswer(item.answer)}

                                        </ReactMarkdown>

                                      ) : (

                                        <p>{isBM ? 'Tiada jawapan disimpan.' : 'No saved answer.'}</p>

                                      )}

                                    </div>

                                    {/* Action Row */}
                                    <div className="history-action-row">
                                      <button
                                        type="button"
                                        className="history-action-btn primary"
                                        onClick={() => {
                                          setQuestion(item.question)
                                          setPage('Chat')
                                        }}
                                      >
                                        <span>↩</span> {isBM ? 'Tanya Semula' : 'Ask Again'}
                                      </button>

                                      <button
                                        type="button"
                                        className="history-action-btn"
                                        onClick={() => {
                                          navigator.clipboard.writeText(`Q: ${item.question}\n\nA: ${item.answer}`)
                                          alert(isBM ? 'Disalin ke papan klip!' : 'Copied to clipboard!')
                                        }}
                                      >
                                        <span>📋</span> {isBM ? 'Salin' : 'Copy'}
                                      </button>

                                      <button
                                        type="button"
                                        className="history-action-btn delete disabled"
                                        onClick={() => {
                                          alert(
                                            isBM
                                              ? 'Fungsi padam belum diaktifkan. Perlu disepadukan dengan pangkalan data backend.'
                                              : 'Delete function is disabled pending backend database integration.'
                                          )
                                        }}
                                        title={isBM ? 'Memerlukan integrasi backend' : 'Requires backend integration'}
                                      >
                                        <span>🗑️</span> {isBM ? 'Padam' : 'Delete'}
                                      </button>
                                    </div>

                                  </article>

                                ))}

                              </div>

                            )}

            </div>

          )}

          {page === 'Documents' && (

            <div className="documents-page">

              <div className="documents-heading">

                <p className="documents-eyebrow">

                  {isBM ? 'PUSAT DOKUMEN' : 'DOCUMENT LIBRARY'}

                </p>

                <h2>

                  {isBM ? 'Dokumen IIUM' : 'IIUM Documents'}

                </h2>

                <p>

                  {isBM

                    ? 'Cari dan rujuk dokumen yuran pengajian.'

                    : 'Find and view the tuition fee documents used by the assistant.'}

                </p>

              </div>

              <div className="documents-controls">

                <input

                  className="documents-search"

                  type="search"

                  placeholder={isBM ? 'Cari dokumen...' : 'Search documents...'}

                  value={documentSearch}

                  onChange={(event) => setDocumentSearch(event.target.value)}

                />

                <select

                  className="documents-filter"

                  value={documentLevel}

                  onChange={(event) => setDocumentLevel(event.target.value)}

                  aria-label="Filter by study level"

                >

                  <option value="All">{isBM ? 'Semua peringkat' : 'All study levels'}</option>

                  <option value="Undergraduate">Undergraduate</option>

                  <option value="Master's">Master's</option>

                </select>

                <select

                  className="documents-filter"

                  value={documentAudience}

                  onChange={(event) => setDocumentAudience(event.target.value)}

                  aria-label="Filter by student type"

                >

                  <option value="All">{isBM ? 'Semua pelajar' : 'All students'}</option>

                  <option value="Malaysian">{isBM ? 'Pelajar Malaysia' : 'Malaysian'}</option>

                  <option value="International">{isBM ? 'Pelajar antarabangsa' : 'International'}</option>

                </select>

              </div>

              <p className="documents-count">

                {filteredDocuments.length}{' '}

                {isBM ? 'dokumen ditemui' : 'documents found'}

              </p>

              {filteredDocuments.length === 0 ? (

                <div className="documents-empty">

                  {isBM

                    ? 'Tiada dokumen yang sepadan. Cuba carian atau penapis lain.'

                    : 'No matching documents. Try another search or filter.'}

                </div>

              ) : (

                <div className="documents-grid">

                  {filteredDocuments.map((doc) => (

                    <article className="document-card" key={doc.file}>

                      <div className="document-card-top">

                        <div className="document-pdf-icon">PDF</div>

                        <span className="document-type">

                          {doc.group}

                        </span>

                      </div>

                      <h3>{doc.name}</h3>

                      <p className="document-audience">

                        {doc.audience === 'Malaysian'

                          ? (isBM ? 'Pelajar Malaysia' : 'Malaysian students')

                          : (isBM ? 'Pelajar antarabangsa' : 'International students')}

                      </p>

                      <p className="document-filename">{doc.file}</p>

                      <a

                        className="document-view-button"

                        href={`/documents/${encodeURIComponent(doc.file)}`}

                        target="_blank"

                        rel="noreferrer"

                      >

                        <span>{isBM ? 'Lihat PDF' : 'View PDF'}</span>

                        <span aria-hidden="true">↗</span>

                      </a>

                    </article>

                  ))}

                </div>

              )}

            </div>

          )}

          {page === 'Help & About' && (

            <section className="inner-page">

              <div className="welcome-badge">HERE TO HELP</div>

              <h1>{isBM ? 'Bantuan & maklumat' : 'Help & about'}</h1>

              <p className="welcome-description">

                {isBM ? 'Maklumat ringkas tentang pembantu polisi IIUM.' : 'A quick guide to using the IIUM Policy Assistant.'}

              </p>

              <div className="help-grid">

                <div className="content-card">

                  <div className="help-icon">01</div>

                  <h3>{isBM ? 'Tanya soalan' : 'Ask a question'}</h3>

                  <p>{isBM ? 'Gunakan bahasa yang mudah dan nyatakan situasi anda.' : 'Describe your policy question clearly and include relevant details.'}</p>

                </div>

                <div className="content-card">

                  <div className="help-icon">02</div>

                  <h3>{isBM ? 'Semak sumber' : 'Check the sources'}</h3>

                  <p>{isBM ? 'Rujuk dokumen rasmi untuk mengesahkan maklumat.' : 'Verify important details against official university policy documents.'}</p>

                </div>

                <div className="content-card">

                  <div className="help-icon">03</div>

                  <h3>{isBM ? 'Perlu bantuan lanjut?' : 'Need more help?'}</h3>

                  <p>{isBM ? 'Hubungi pejabat universiti yang berkaitan untuk pengesahan.' : 'Contact the relevant IIUM office for official clarification.'}</p>

                </div>

              </div>

              <div className="about-note">
                <strong>{isBM ? 'Tentang projek ini' : 'About this project'}</strong>
                <p>
                  {isBM
                    ? 'IIUM Policy Assistant ialah sistem berasaskan AI yang dibangunkan sebagai Projek Tahun Akhir. Dengan menggunakan teknologi Retrieval-Augmented Generation (RAG), sistem ini memudahkan pengguna mencari dan memahami dokumen polisi universiti. Sistem ini bukan pengganti nasihat rasmi daripada pihak universiti.'
                    : 'IIUM Policy Assistant is an AI-powered system developed as a Final Year Project. Using Retrieval-Augmented Generation (RAG), it helps users find and understand university policy documents. This system is not a replacement for official university advice.'}
                </p>
              </div>

            </section>

          )}

        </div>

      </main>

    </div>

  )

}

export default App
