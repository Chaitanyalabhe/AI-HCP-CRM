import { useState, useRef, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import axios from 'axios';
import { updateForm } from '../store/interactionSlice';
import { API_URL } from '../config';
import './InteractionForm.css';

export default function InteractionForm() {
  const dispatch = useDispatch();
  const form = useSelector((state) => state.interaction);
  const messagesEndRef = useRef(null);

  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      text: 'Log interaction details here (e.g., "Met Dr. Smith, discussed Product X efficacy, positive sentiment, shared brochure") or ask for help.',
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    const userText = input.trim();
    setMessages((p) => [...p, { role: 'user', text: userText }]);
    setInput('');
    setLoading(true);
    try {
      const baseUrl = (API_URL || '').replace(/\/+$/, '');
      const res = await axios.post(`${baseUrl}/chat`, { message: userText });
      const { response, form_data } = res.data;
      if (form_data && Object.keys(form_data).length > 0) dispatch(updateForm(form_data));
      setMessages((p) => [...p, { role: 'assistant', text: response || 'Form updated!' }]);
    } catch (err) {
      const status = err?.response?.status;
      const detail =
        err?.response?.data?.detail ||
        (typeof err?.response?.data === 'string' ? err.response.data : null) ||
        err?.message;
      setMessages((p) => [
        ...p,
        {
          role: 'assistant',
          text: `⚠️ Backend error (${API_URL})${status ? ` [HTTP ${status}]` : ''}${detail ? `: ${detail}` : ''
            }`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const materialsValue = Array.isArray(form.materials_shared)
    ? form.materials_shared.join(', ')
    : form.materials_shared || '';

  const samplesValue = Array.isArray(form.samples_distributed)
    ? form.samples_distributed.join(', ')
    : form.samples_distributed || '';

  const sentimentOptions = [
    { value: 'Positive', emoji: '😊', color: '#16a34a' },
    { value: 'Neutral',  emoji: '😐', color: '#d97706' },
    { value: 'Negative', emoji: '😞', color: '#dc2626' },
  ];

  const suggestedFollowUps = [
    'Schedule follow-up meeting in 2 weeks',
    'Send OncoBoost Phase III PDF',
    'Add Dr. Sharma to advisory board invite list',
  ];

  return (
    <div className="hcp-root">

      {/* ══════════════════════════════════
          LEFT PANEL — scrollable form
      ══════════════════════════════════ */}
      <div className="left-panel">

        <h1 className="page-title">Log HCP Interaction</h1>

        {/* ── CARD: Interaction Details ── */}
        <div className="card">
          <p className="card-title">Interaction Details</p>

          {/* HCP Name + Interaction Type */}
          <div className="grid-2">
            <div>
              <label className="field-label">HCP Name</label>
              <input
                readOnly
                value={form.hcp_name}
                placeholder="Search or select HCP..."
                className="field-input"
              />
            </div>
            <div>
              <label className="field-label">Interaction Type</label>
              <div className="select-wrapper">
                <select
                  disabled
                  value={form.interaction_type}
                  className="field-input"
                  style={{ paddingRight: '32px', appearance: 'none' }}
                >
                  {['Meeting', 'Call', 'Email', 'Conference', 'Virtual'].map((t) => (
                    <option key={t}>{t}</option>
                  ))}
                </select>
                <span className="select-arrow">▼</span>
              </div>
            </div>
          </div>

          {/* Date + Time */}
          <div className="grid-2">
            <div>
              <label className="field-label">Date</label>
              <input readOnly value={form.date} className="field-input" />
            </div>
            <div>
              <label className="field-label">Time</label>
              <input readOnly value={form.time} className="field-input" />
            </div>
          </div>

          {/* Attendees */}
          <div style={{ marginBottom: '14px' }}>
            <label className="field-label">Attendees</label>
            <input
              readOnly
              value={form.attendees}
              placeholder="Enter names or search..."
              className="field-input"
            />
          </div>

          {/* Topics Discussed */}
          <div style={{ marginBottom: '10px' }}>
            <label className="field-label">Topics Discussed</label>
            <div className="textarea-wrapper">
              <textarea
                readOnly
                value={form.topics_discussed}
                placeholder="Enter key discussion points..."
                className="field-input field-textarea field-textarea-topics"
              />
              <span className="icon-mic">🎤</span>
              <span className="icon-edit">✏️</span>
            </div>
          </div>

          {/* Voice note button */}
          <button className="voice-btn">
            ⚙️ Summarize from Voice Note (Requires Consent)
          </button>
        </div>

        {/* ── CARD: Materials / Samples ── */}
        <div className="card">
          <p className="card-title">Materials Shared / Samples Distributed</p>

          {/* Materials Shared */}
          <div className="material-box">
            <div className="material-box-header">
              <span className="material-box-title">Materials Shared</span>
              <button className="small-btn">🔍 Search/Add</button>
            </div>
            <p className={`material-box-text ${materialsValue ? 'filled' : 'empty'}`}>
              {materialsValue || 'No materials added.'}
            </p>
          </div>

          {/* Samples Distributed */}
          <div className="material-box">
            <div className="material-box-header">
              <span className="material-box-title">Samples Distributed</span>
              <button className="small-btn">⊕ Add Sample</button>
            </div>
            <p className={`material-box-text ${samplesValue ? 'filled' : 'empty'}`}>
              {samplesValue || 'No samples added.'}
            </p>
          </div>
        </div>

        {/* ── CARD: Sentiment ── */}
        <div className="card">
          <label className="field-label" style={{ marginBottom: '14px' }}>
            Observed/Inferred HCP Sentiment
          </label>
          <div className="sentiment-row">
            {sentimentOptions.map(({ value, emoji, color }) => {
              const isActive = form.sentiment === value;
              return (
                <label key={value} className="sentiment-label">
                  <div
                    className="radio-circle"
                    style={{ border: `2px solid ${isActive ? color : '#d1d5db'}` }}
                  >
                    {isActive && (
                      <div className="radio-dot" style={{ background: color }} />
                    )}
                  </div>
                  <span className="sentiment-emoji">{emoji}</span>
                  <span style={{ color: isActive ? color : '#374151' }}>{value}</span>
                </label>
              );
            })}
          </div>
        </div>

        {/* ── CARD: Outcomes + Follow-up ── */}
        <div className="card">

          {/* Outcomes */}
          <div style={{ marginBottom: '14px' }}>
            <label className="field-label">Outcomes</label>
            <div className="textarea-wrapper">
              <textarea
                readOnly
                value={form.outcomes || ''}
                placeholder="Key outcomes or agreements..."
                className="field-input field-textarea field-textarea-sm"
              />
              <span className="icon-edit">✏️</span>
            </div>
          </div>

          {/* Follow-up Actions */}
          <div style={{ marginBottom: '14px' }}>
            <label className="field-label">Follow-up Actions</label>
            <div className="textarea-wrapper">
              <textarea
                readOnly
                value={form.next_steps || ''}
                placeholder="Enter next steps or tasks..."
                className="field-input field-textarea field-textarea-sm"
              />
              <span className="icon-edit">✏️</span>
            </div>
          </div>

          {/* AI Suggested Follow-ups */}
          <div>
            <p className="suggested-title">AI Suggested Follow-ups:</p>
            {suggestedFollowUps.map((s, i) => (
              <p
                key={i}
                className="suggested-item"
                onClick={() =>
                  dispatch(
                    updateForm({
                      next_steps: (form.next_steps ? form.next_steps + '\n' : '') + s,
                    })
                  )
                }
              >
                + {s}
              </p>
            ))}
          </div>
        </div>

      </div>
      {/* END LEFT */}

      {/* ══════════════════════════════════
          RIGHT PANEL — AI Assistant
      ══════════════════════════════════ */}
      <div className="right-panel">

        {/* Header */}
        <div className="ai-header">
          <div className="ai-header-inner">
            <div className="ai-avatar">🤖</div>
            <div>
              <p className="ai-name">AI Assistant</p>
              <p className="ai-subtitle">Log interaction via chat</p>
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="messages-area">
          {messages.map((msg, i) => (
            <div key={i} className={`message-bubble ${msg.role}`}>
              {msg.text}
            </div>
          ))}

          {loading && (
            <div className="loading-dots">
              <span className="d1">●</span>
              <span className="d2">●</span>
              <span className="d3">●</span>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input bar */}
        <div className="input-bar">
          <div className="input-row">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  sendMessage();
                }
              }}
              placeholder="Describe interaction..."
              disabled={loading}
              className="chat-input"
            />
            <button
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              className={`log-btn ${loading || !input.trim() ? 'disabled' : 'active'}`}
            >
              ▲ Log
            </button>
          </div>
        </div>

      </div>
      {/* END RIGHT */}

    </div>
  );
}