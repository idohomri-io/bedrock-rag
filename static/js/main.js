document.addEventListener('DOMContentLoaded', () => {
    const q = document.getElementById('q')
    const askBtn = document.getElementById('askBtn')
    const statusEl = document.getElementById('status')
    const answerEl = document.getElementById('answer')

    // Only initialize if we're on the index page
    if (!q || !askBtn || !statusEl || !answerEl) {
        return
    }

    function setStatus(text) {
        statusEl.textContent = text || ''
    }

    function setAnswer(text) {
        answerEl.textContent = text || ''
    }

    function renderSources(sources) {
        const el = document.getElementById('sources')
        if (!el) return

        el.innerHTML = ''

        if (!Array.isArray(sources) || sources.length === 0) {
            el.textContent = 'No sources returned.'
            return
        }

        sources.forEach((s, idx) => {
            const wrapper = document.createElement('div')
            wrapper.className = 'source-item'

            const meta = document.createElement('div')
            meta.className = 'source-meta'
            meta.textContent = s.source
                ? `#${idx + 1} • ${s.source}`
                : `#${idx + 1}`

            const text = document.createElement('pre')
            text.className = 'source-text'
            text.textContent = s.text || ''

            wrapper.appendChild(meta)
            wrapper.appendChild(text)
            el.appendChild(wrapper)
        })
    }

    async function ask() {
        const question = (q.value || '').trim()
        if (!question) {
            setStatus('Please write a question.')
            return
        }

        askBtn.disabled = true
        setStatus('Thinking...')
        setAnswer('')

        try {
            const res = await fetch('/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question }),
            })

            const data = await res.json()

            if (!res.ok) {
                setStatus('Error')
                setAnswer(data.error || 'Unknown error')
                return
            }

            setStatus('Done')
            // setAnswer(data.answer || '')

            setAnswer(data.answer || '')
            renderSources(data.sources)
        } catch (err) {
            setStatus('Error')
            setAnswer(err.message || String(err))
        } finally {
            askBtn.disabled = false
        }
    }

    askBtn.addEventListener('click', ask)
    q.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
            ask()
        }
    })

    // Handle conversation starter chips
    const starterChips = document.querySelectorAll('.starter-chip')
    starterChips.forEach((chip) => {
        chip.addEventListener('click', () => {
            const question = chip.getAttribute('data-question')
            if (question) {
                q.value = question
                q.focus()
                // Optional: auto-submit after a short delay
                setTimeout(() => {
                    ask()
                }, 300)
            }
        })
    })
})
