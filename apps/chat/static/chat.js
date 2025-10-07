async function fetchModels() {
  try {
    const res = await fetch('/chat/models', { credentials: 'same-origin' });
    const data = await res.json();
    const sel = document.getElementById('modelSelect');
    sel.innerHTML = '';
    // Ollama often returns { models: { data: [ {id: 'llama3:latest', ...}, ... ], object: 'list' } }
    // Prefer flattened ids array if provided by server
    if (data.ids && Array.isArray(data.ids)) {
      data.ids.forEach(id => {
        const opt = document.createElement('option');
        opt.value = id;
        opt.textContent = id;
        sel.appendChild(opt);
      });
    } else if (data.models) {
      // models.data[] with id
      if (data.models.data && Array.isArray(data.models.data)) {
        data.models.data.forEach(m => {
          const id = m.id || m.name || JSON.stringify(m);
          const opt = document.createElement('option');
          opt.value = id;
          opt.textContent = id;
          sel.appendChild(opt);
        });
      } else if (Array.isArray(data.models)) {
        // fallback: models is an array
        data.models.forEach(m => {
          const id = m.id || m.name || m;
          const opt = document.createElement('option');
          opt.value = id;
          opt.textContent = id;
          sel.appendChild(opt);
        });
      } else if (typeof data.models === 'string') {
        const opt = document.createElement('option'); opt.value = data.models; opt.textContent = data.models; sel.appendChild(opt);
      } else {
        const opt = document.createElement('option'); opt.textContent = 'No models found'; sel.appendChild(opt);
      }
    } else if (data.error) {
      const selEl = document.getElementById('modelSelect');
      const opt = document.createElement('option'); opt.textContent = 'Error fetching models'; selEl.appendChild(opt);
    }
    // select first available model if present
    const selEl = document.getElementById('modelSelect');
    if (selEl.options.length > 0) selEl.selectedIndex = 0;
  } catch (err) {
    const sel = document.getElementById('modelSelect');
    sel.innerHTML = '';
    const opt = document.createElement('option'); opt.textContent = 'Error fetching models'; sel.appendChild(opt);
    console.error('fetchModels error', err);
  }
}

function appendMessage(role, text, imgSrc) {
  const w = document.getElementById('chatWindow');
  
  // Remove empty state if it exists
  const emptyState = w.querySelector('.empty-state');
  if (emptyState) {
    emptyState.remove();
  }
  
  const messageDiv = document.createElement('div');
  messageDiv.className = `message-${role} mb-3`;
  messageDiv.style.display = 'flex';
  messageDiv.style.justifyContent = role === 'user' ? 'flex-end' : 'flex-start';
  
  const bubble = document.createElement('div');
  bubble.className = 'message-bubble';
  bubble.style.whiteSpace = 'pre-wrap';
  bubble.innerText = text;
  
  messageDiv.appendChild(bubble);
  
  if (imgSrc) {
    const img = document.createElement('img');
    img.src = imgSrc;
    img.style.maxWidth = '200px';
    img.style.marginTop = '0.5rem';
    img.style.borderRadius = '8px';
    bubble.appendChild(document.createElement('br'));
    bubble.appendChild(img);
  }
  
  w.appendChild(messageDiv);
  w.scrollTop = w.scrollHeight;
}

document.addEventListener('DOMContentLoaded', () => {
  fetchModels();
  document.getElementById('refreshModels').addEventListener('click', fetchModels);

  // Conversation history array
  let conversationHistory = [];
  let currentSessionId = null;

  // Sidebar toggle functionality
  const sidebar = document.getElementById('chatSidebar');
  const sidebarToggle = document.getElementById('sidebarToggle');
  
  sidebarToggle.addEventListener('click', () => {
    sidebar.classList.toggle('collapsed');
    // Save preference to localStorage
    localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
  });

  // Restore sidebar state from localStorage
  if (localStorage.getItem('sidebarCollapsed') === 'true') {
    sidebar.classList.add('collapsed');
  }

  // Restore current session from localStorage
  const savedSessionId = localStorage.getItem('currentSessionId');
  if (savedSessionId) {
    currentSessionId = savedSessionId;
  }

  // Load chat sessions on page load
  loadChatSessions();
  
  // Load the saved session if it exists, otherwise create a new one
  if (currentSessionId) {
    loadSession(currentSessionId).catch(() => {
      // If loading fails (session doesn't exist or permission denied), clear it and create new
      console.log('Failed to load saved session, creating new one...');
      localStorage.removeItem('currentSessionId');
      currentSessionId = null;
      createNewSession();
    });
  } else {
    // No saved session, create a new one automatically
    createNewSession();
  }

  // Helper function to create a new session
  async function createNewSession() {
    try {
      console.log('🔄 Requesting new chat session...');
      const resp = await fetch('/chat/sessions', {
        method: 'POST',
        credentials: 'same-origin',
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await resp.json();
      console.log('📥 Session creation response:', data);
      
      if (data.session_id) {
        currentSessionId = data.session_id;
        localStorage.setItem('currentSessionId', currentSessionId);
        conversationHistory = [];
        clearChatWindow();
        loadChatSessions(); // Refresh sidebar
        console.log('✅ New session created:', currentSessionId);
      } else if (data.error) {
        console.error('❌ Session creation failed:', data.error);
      }
    } catch (err) {
      console.error('❌ Error creating new chat:', err);
    }
  }

  // New chat button
  document.getElementById('newChatBtn').addEventListener('click', () => {
    createNewSession();
  });

  // Load chat sessions list
  async function loadChatSessions() {
    try {
      const resp = await fetch('/chat/sessions', {
        credentials: 'same-origin'
      });
      const data = await resp.json();
      const container = document.getElementById('chatSessions');
      
      if (!data.sessions || data.sessions.length === 0) {
        container.innerHTML = '<div class="text-center text-muted py-4"><small>No chat history yet</small></div>';
        return;
      }
      
      container.innerHTML = '';
      data.sessions.forEach(sess => {
        const item = document.createElement('div');
        item.className = 'session-item';
        if (sess.session_id === currentSessionId) {
          item.classList.add('active');
        }
        
        const updatedDate = new Date(sess.updated_at);
        const timeAgo = getTimeAgo(updatedDate);
        
        item.innerHTML = `
          <div class="session-item-title">${sess.title || 'New Chat'}</div>
          <div class="session-item-meta">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
            <span>${sess.message_count || 0} • ${timeAgo}</span>
          </div>
          <button class="btn btn-sm session-delete" onclick="deleteSession(event, '${sess.session_id}')">×</button>
        `;
        
        item.addEventListener('click', (e) => {
          if (!e.target.closest('.session-delete')) {
            loadSession(sess.session_id);
          }
        });
        
        container.appendChild(item);
      });
    } catch (err) {
      console.error('Error loading sessions:', err);
    }
  }

  // Load a specific session
  async function loadSession(sessionId) {
    try {
      const resp = await fetch(`/chat/sessions/${sessionId}`, {
        credentials: 'same-origin'
      });
      const data = await resp.json();
      
      currentSessionId = sessionId;
      localStorage.setItem('currentSessionId', currentSessionId);
      conversationHistory = data.messages || [];
      
      // Clear and repopulate chat window
      const chatWindow = document.getElementById('chatWindow');
      chatWindow.innerHTML = '';
      
      conversationHistory.forEach(msg => {
        appendMessage(msg.role, msg.content);
      });
      
      // Update active session in sidebar
      loadChatSessions(); // Refresh to update active state
    } catch (err) {
      console.error('Error loading session:', err);
    }
  }

  // Delete session
  window.deleteSession = async function(event, sessionId) {
    event.stopPropagation();
    if (!confirm('Delete this chat?')) return;
    
    try {
      const resp = await fetch(`/chat/sessions/${sessionId}`, {
        method: 'DELETE',
        credentials: 'same-origin'
      });
      
      if (resp.ok) {
        if (sessionId === currentSessionId) {
          currentSessionId = null;
          conversationHistory = [];
          clearChatWindow();
        }
        loadChatSessions();
      }
    } catch (err) {
      console.error('Error deleting session:', err);
    }
  };

  // Helper: time ago
  function getTimeAgo(date) {
    const seconds = Math.floor((new Date() - date) / 1000);
    if (seconds < 60) return 'just now';
    if (seconds < 3600) return Math.floor(seconds / 60) + 'm ago';
    if (seconds < 86400) return Math.floor(seconds / 3600) + 'h ago';
    return Math.floor(seconds / 86400) + 'd ago';
  }

  // Helper: clear chat window
  function clearChatWindow() {
    const chatWindow = document.getElementById('chatWindow');
    chatWindow.innerHTML = `
      <div class="empty-state">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>
        <p>Start a conversation by typing a message below</p>
      </div>
    `;
  }

  // Clear chat button
  document.getElementById('clearChat').addEventListener('click', () => {
    if (confirm('Clear current chat (not saved)?')) {
      conversationHistory = [];
      currentSessionId = null;
      localStorage.removeItem('currentSessionId');
      clearChatWindow();
    }
  });

  // Send on Enter key
  document.getElementById('messageInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      document.getElementById('sendBtn').click();
    }
  });

  document.getElementById('sendBtn').addEventListener('click', async () => {
    const input = document.getElementById('messageInput');
    const fileInput = document.getElementById('fileInput');
    const model = document.getElementById('modelSelect').value;
    const text = input.value.trim();
    if (!text && fileInput.files.length === 0) return;

    // Process file before clearing
    let imageBase64 = null;
    if (fileInput.files.length > 0) {
      const file = fileInput.files[0];
      const b = await file.arrayBuffer();
      const u8 = new Uint8Array(b);
      const binary = Array.from(u8).map(n => String.fromCharCode(n)).join('');
      imageBase64 = btoa(binary);
    }

    // Create session if needed BEFORE sending message
    if (!currentSessionId) {
      try {
        console.log('⚠️ No session ID found, creating new session...');
        const sessionResp = await fetch('/chat/sessions', {
          method: 'POST',
          credentials: 'same-origin',
          headers: { 'Content-Type': 'application/json' }
        });
        const sessionData = await sessionResp.json();
        console.log('📥 Session creation response:', sessionData);
        
        if (sessionData.session_id) {
          currentSessionId = sessionData.session_id;
          localStorage.setItem('currentSessionId', currentSessionId);
          // Immediately refresh sidebar to show new chat
          loadChatSessions();
          console.log('✅ Session created successfully:', currentSessionId);
        } else {
          throw new Error(sessionData.error || 'Failed to create session');
        }
      } catch (err) {
        console.error('❌ Error creating session:', err);
        appendMessage('assistant', 'Error: Could not create chat session - ' + err.message);
        return; // Don't send message if session creation fails
      }
    } else {
      console.log('✅ Using existing session:', currentSessionId);
    }

    // Show message in UI
    appendMessage('user', text || '[image]');

    // Add user message to conversation history
    conversationHistory.push({
      role: 'user',
      content: text || '[image]'
    });

    // Clear inputs immediately
    input.value = '';
    fileInput.value = '';

    const payload = { 
      model, 
      message: text, 
      image: imageBase64,
      history: conversationHistory,  // Send full conversation history
      session_id: currentSessionId   // Include session ID for persistence
    };
    
    // Debug logging
    console.log('Sending message with payload:', {
      model: model,
      message_length: text.length,
      session_id: currentSessionId,
      history_length: conversationHistory.length
    });
    
    try {
      const resp = await fetch('/chat/message', {
        method: 'POST',
        credentials: 'same-origin',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      let data;
      try {
        data = await resp.json();
      } catch (e) {
        appendMessage('assistant', 'Invalid response from server');
        return;
      }
      if (!resp.ok) {
        const errMsg = data && data.error ? data.error : ('HTTP ' + resp.status);
        appendMessage('assistant', 'Error: ' + errMsg);
      } else if (data.error) {
        appendMessage('assistant', 'Error: ' + data.error);
      } else {
        // Ollama returns structured chat output; attempt to extract text
        let reply = '';
        if (data.output) reply = data.output;
        else if (data.choices && data.choices[0] && data.choices[0].message) reply = data.choices[0].message.content;
        else reply = JSON.stringify(data);
        appendMessage('assistant', reply);
        
        // Add assistant response to conversation history
        conversationHistory.push({
          role: 'assistant',
          content: reply
        });

        // Refresh sessions list to show updated timestamp and message count
        loadChatSessions();
      }
    } catch (e) {
      appendMessage('assistant', 'Request failed: ' + e.message);
    }
  });
});
