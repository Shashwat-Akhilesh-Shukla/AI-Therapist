import React, { useEffect, useRef, useState } from 'react'
import Message from './Message'

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL
console.log('BACKEND_URL in Chat.js:', BACKEND_URL)

export default function Chat({ chats, currentChatId, setCurrentChatId, updateChats, token, onStreamComplete }) {
  const [text, setText] = useState('')
  const [attachingFile, setAttachingFile] = useState(null)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [error, setError] = useState('')
  const [fileInfo, setFileInfo] = useState(null)
  const [isStreaming, setIsStreaming] = useState(false)
  const inputRef = useRef(null)
  const messagesRef = useRef(null)

  const current = chats.find(c => c.id === currentChatId) || { id: null, messages: [] }

  useEffect(() => { if (currentChatId && !current) console.warn('No current chat') }, [currentChatId])

  function pushMessage(role, content, extra = {}) {
    updateChats(prev => prev.map(c => c.id === currentChatId ? { ...c, messages: [...c.messages, { id: role + '-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9), role, content, ...extra }] } : c))
  }

  useEffect(() => {
    // auto-scroll to bottom when messages change
    const el = messagesRef.current
    if (el) el.scrollTop = el.scrollHeight
  }, [chats, currentChatId])

  async function send() {
    console.log('[send] called', { text, fileInfo: fileInfo ? { filename: fileInfo.filename } : null })
    if (!text && !fileInfo) return
    if (isStreaming) return // Prevent sending while streaming

    // Build message to display in UI (do NOT include extracted text)
    const displayedMessage = text || (fileInfo ? `Uploaded file: ${fileInfo.filename}` : '')

    // Store the current chat ID before any updates
    const originalChatId = currentChatId

    pushMessage('user', displayedMessage, { file: fileInfo })
    setText('')

    // Prepare payload for backend — include conversation_id and doc_id
    const payload = { message: displayedMessage }

    // Pass conversation_id if not a temporary chat
    const currentChat = chats.find(c => c.id === currentChatId)
    if (currentChat && !currentChat.isTemp) {
      payload.conversation_id = currentChatId
    }

    if (fileInfo && fileInfo.doc_id) { payload.doc_id = fileInfo.doc_id }


    // Create placeholder AI message for streaming with guaranteed unique ID
    const aiMessageId = 'ai-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9)
    console.log(`[send] Creating AI message ${aiMessageId} in chat ${currentChatId}`)
    updateChats(prev => prev.map(c => c.id === currentChatId ? { ...c, messages: [...c.messages, { id: aiMessageId, role: 'ai', content: '', streaming: true }] } : c))

    setIsStreaming(true)

    // Helper function to update only the chat containing our specific message
    // This prevents updates from affecting other chats even if IDs match
    const updateMessageInChat = (updateFn) => {
      updateChats(prev => prev.map(c => {
        // Find the chat that contains our message
        const hasMessage = c.messages.some(m => m.id === aiMessageId)
        if (hasMessage) {
          console.log(`[updateMessageInChat] Updating message ${aiMessageId} in chat ${c.id}`)
          return updateFn(c)
        }
        return c
      }))
    }

    // Call backend streaming chat endpoint
    try {
      const res = await fetch(`${BACKEND_URL}/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      })

      if (!res.ok) {
        const errorText = await res.text()
        updateMessageInChat(c => ({
          ...c,
          messages: c.messages.map(m =>
            m.id === aiMessageId ? { ...m, content: 'Error: ' + errorText, streaming: false } : m
          )
        }))
        setIsStreaming(false)
        return
      }

      // Read streaming response
      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      let fullResponse = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() // Keep incomplete line in buffer

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))

              if (data.type === 'chunk') {
                // Append chunk to message - update only the chat containing this message
                fullResponse += data.content
                updateMessageInChat(c => ({
                  ...c,
                  messages: c.messages.map(m =>
                    m.id === aiMessageId ? { ...m, content: fullResponse } : m
                  )
                }))
              } else if (data.type === 'done') {
                // Stream complete, update conversation ID if new
                if (data.conversation_id && data.conversation_id !== originalChatId) {
                  console.log('[send] Backend created new conversation:', data.conversation_id)
                  const newConversationId = data.conversation_id

                  // Update the chat ID and mark as not temp - only for the chat with our message
                  updateChats(prev => prev.map(c => {
                    const hasMessage = c.messages.some(m => m.id === aiMessageId)
                    if (hasMessage) {
                      console.log(`[send] Updating chat ID from ${c.id} to ${newConversationId}`)
                      return { ...c, id: newConversationId, isTemp: false }
                    }
                    return c
                  }))

                  // Update current chat ID only if we're still viewing this chat
                  if (currentChatId === originalChatId) {
                    setCurrentChatId(newConversationId)
                  }
                }

                // Mark message as complete
                updateMessageInChat(c => ({
                  ...c,
                  messages: c.messages.map(m =>
                    m.id === aiMessageId ? { ...m, streaming: false } : m
                  )
                }))

                // Trigger message reload from backend to sync state
                if (onStreamComplete && data.conversation_id) {
                  console.log('[send] Triggering message reload after streaming complete')
                  // Small delay to ensure backend has finished writing
                  setTimeout(() => {
                    onStreamComplete(data.conversation_id)
                  }, 100)
                }
              } else if (data.type === 'error') {
                updateMessageInChat(c => ({
                  ...c,
                  messages: c.messages.map(m =>
                    m.id === aiMessageId ? { ...m, content: 'Error: ' + data.message, streaming: false } : m
                  )
                }))
              }
            } catch (e) {
              console.error('[send] Failed to parse SSE data:', e)
            }
          }
        }
      }
    } catch (err) {
      console.error('[send] Streaming error:', err)
      updateMessageInChat(c => ({
        ...c,
        messages: c.messages.map(m =>
          m.id === aiMessageId ? { ...m, content: 'Error: ' + String(err), streaming: false } : m
        )
      }))
    } finally {
      setIsStreaming(false)
    }
  }

  function uploadFileWithProgress(file, onProgress) {
    return new Promise((resolve, reject) => {
      console.log('[uploadFileWithProgress] starting', { filename: file.name, url: `${BACKEND_URL}/upload_pdf` })
      const form = new FormData()
      form.append('file', file)

      const xhr = new XMLHttpRequest()
      xhr.open('POST', `${BACKEND_URL}/upload_pdf`)
      xhr.setRequestHeader('Authorization', `Bearer ${token}`)
      console.log('[uploadFileWithProgress] XHR opened')

      xhr.upload.onprogress = function (e) {
        if (e.lengthComputable) {
          const pct = Math.round((e.loaded / e.total) * 100)
          console.log('[xhr.progress]', pct + '%')
          onProgress(pct)
        } else {
          console.log('[xhr.progress] indeterminate')
          onProgress(5)
        }
      }

      xhr.onload = function () {
        console.log('[xhr.onload]', xhr.status, xhr.responseText.substring(0, 100))
        if (xhr.status >= 200 && xhr.status < 300) {
          try { onProgress(100) } catch (e) { }
          try { const json = JSON.parse(xhr.responseText); resolve(json) } catch (e) { resolve({ status: 'processing' }) }
        } else {
          reject(new Error(`Upload failed (${xhr.status})`))
        }
      }

      xhr.onerror = function () {
        console.error('[xhr.onerror]')
        reject(new Error('Network error during upload'))
      }
      console.log('[xhr.send] sending form...')
      xhr.send(form)
    })
  }

  function onFileChange(e) {
    const f = e.target.files?.[0]
    if (f) {
      console.log('[onFileChange] file selected:', f.name)
      setAttachingFile(f)
      // Immediately start uploading in the background
      uploadFileWithProgress(f, (pct) => setUploadProgress(pct))
        .then(j => {
          console.log('[onFileChange] upload completed')
          // store doc_id returned by backend; do NOT store extracted text in frontend
          setFileInfo({
            filename: f.name,
            uploadStatus: j.status || 'processing',
            doc_id: j.doc_id || null
          })
        })
        .catch(err => {
          const msg = err && err.message ? err.message : String(err)
          console.error('[onFileChange] upload failed:', msg)
          setError('Upload failed: ' + msg)
        })
        .finally(() => {
          setUploadProgress(0)
        })
    }
  }

  return (
    <main className="chat-main">
      <div className="messages" ref={messagesRef}>
        {current.messages && current.messages.map(m => <Message key={m.id} m={m} />)}
      </div>

      {/* Attachment bar sits just above the composer, similar to ChatGPT */}
      {attachingFile && (
        <div className="attachment-bar">
          <div
            className="progress-circle"
            style={{ background: `conic-gradient(var(--accent) ${uploadProgress * 3.6}deg, rgba(255,255,255,0.06) ${uploadProgress * 3.6}deg)` }}
          >
            <div className="progress-inner">{uploadProgress}%</div>
          </div>
          <div className="attachment-name">{attachingFile.name}</div>
          <div style={{ flex: 1 }} />
          <button className="btn small" onClick={() => { setAttachingFile(null); setUploadProgress(0); setFileInfo(null) }}>Remove</button>
        </div>
      )}

      <div className="composer">
        <label className="attach">
          📎
          <input type="file" accept="application/pdf" onChange={onFileChange} />
        </label>
        {error && (
          <div className="toast error">
            {error} <button onClick={() => setError('')} className="btn small">Dismiss</button>
          </div>
        )}
        <input
          ref={inputRef}
          className="text-input"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder={attachingFile ? `Attached: ${attachingFile.name}` : 'Type a message...'}
          onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send() } }}
          disabled={isStreaming}
        />
        <button className="btn send" onClick={send} disabled={isStreaming}>{isStreaming ? 'Streaming...' : 'Send'}</button>
      </div>
    </main>
  )
}
