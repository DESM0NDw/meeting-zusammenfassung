<script lang="ts">
  import '../app.css';

  type TodoItem = { text: string; assignee: string; priority: string };
  type Result = { summary: string; decisions: string[]; todos: TodoItem[] };

  let transcript = $state('');
  let loading = $state(false);
  let result = $state<Result | null>(null);
  let error = $state('');
  let transcribing = $state(false);
  let audioFileName = $state('');
  let draggingAudio = $state(false);
  let inputPath = $state<'audio' | 'transcript' | null>(null);

  const PRIORITY_ORDER: Record<string, number> = { Hoch: 0, Mittel: 1, Niedrig: 2 };
  const PRIORITY_CLASS: Record<string, string> = { Hoch: 'prio-high', Mittel: 'prio-mid', Niedrig: 'prio-low' };

  async function summarize() {
    if (!transcript.trim() || loading) return;
    loading = true;
    result = null;
    error = '';

    try {
      const res = await fetch('/api/summarize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ transcript }),
      });

      if (!res.ok) throw new Error();
      result = await res.json();
    } catch {
      error = 'Fehler bei der Analyse. Bitte erneut versuchen.';
    } finally {
      loading = false;
    }
  }

  function onKeydown(e: KeyboardEvent) {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') summarize();
  }

  const AUDIO_EXAMPLES = [
    { id: 'sprint',   label: 'Sprint Planning' },
    { id: 'strategy', label: 'Q3-Strategie' },
    { id: 'retro',    label: 'Retrospektive' },
  ];

  let playingId = $state<string | null>(null);
  let audioPlayer: HTMLAudioElement | null = null;

  function togglePlay(id: string) {
    if (playingId === id) {
      audioPlayer?.pause();
      playingId = null;
    } else {
      audioPlayer?.pause();
      audioPlayer = new Audio(`/audio/${id}.mp3`);
      audioPlayer.onended = () => playingId = null;
      audioPlayer.play();
      playingId = id;
    }
  }

  async function transcribeAudioExample(id: string) {
    audioPlayer?.pause();
    playingId = null;
    const res = await fetch(`/audio/${id}.mp3`);
    const blob = await res.blob();
    const file = new File([blob], `${id}.mp3`, { type: 'audio/mpeg' });
    await transcribeAudio(file);
  }

  async function transcribeAudio(file: File) {
    if (transcribing || loading) return;
    transcribing = true;
    inputPath = 'audio';
    audioFileName = file.name;
    result = null;
    error = '';
    try {
      const formData = new FormData();
      formData.append('file', file);
      const res = await fetch('/api/transcribe', { method: 'POST', body: formData });
      if (res.status === 413) { error = 'Datei zu groß (max. 25 MB).'; return; }
      if (!res.ok) throw new Error();
      const data = await res.json();
      transcript = data.transcript;
    } catch {
      error = 'Fehler bei der Transkription. Bitte erneut versuchen.';
      audioFileName = '';
    } finally {
      transcribing = false;
    }
  }

  function onAudioDrop(e: DragEvent) {
    e.preventDefault();
    draggingAudio = false;
    const file = e.dataTransfer?.files[0];
    if (file && file.type.startsWith('audio/')) transcribeAudio(file);
  }

  function onAudioInput(e: Event) {
    const file = (e.target as HTMLInputElement).files?.[0];
    if (file) transcribeAudio(file);
  }
</script>

<svelte:head>
  <title>Meeting-Zusammenfassung — KI Demo</title>
</svelte:head>

<div class="wrapper">

  <header>
    <div class="header-inner">
      <div class="header-left">
        <div class="icon">
          <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M18 18.72a9.094 9.094 0 0 0 3.741-.479 3 3 0 0 0-4.682-2.72m.94 3.198.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0 1 12 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 0 1 6 18.719m12 0a5.971 5.971 0 0 0-.941-3.197m0 0A5.995 5.995 0 0 0 12 12.75a5.995 5.995 0 0 0-5.058 2.772m0 0a3 3 0 0 0-4.681 2.72 8.986 8.986 0 0 0 3.74.477m.94-3.197a5.971 5.971 0 0 0-.94 3.197M15 6.75a3 3 0 1 1-6 0 3 3 0 0 1 6 0Zm6 3a2.25 2.25 0 1 1-4.5 0 2.25 2.25 0 0 1 4.5 0Zm-13.5 0a2.25 2.25 0 1 1-4.5 0 2.25 2.25 0 0 1 4.5 0Z" />
          </svg>
        </div>
        <div>
          <h1>Meeting-Zusammenfassung</h1>
          <p class="subtitle">Entscheidungen und To-Dos automatisch aus jedem Gesprächsprotokoll</p>
        </div>
      </div>
      <div class="header-right">
        <span class="demo-badge"><span class="pulse"></span>DEMO</span>
        <a href="https://desmond.autonomika.de" class="back-link" target="_blank">
          <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5 3 12m0 0 7.5-7.5M3 12h18" />
          </svg>
          Portfolio
        </a>
      </div>
    </div>
  </header>

  <div class="flow-bar">
    <p class="flow-label">Zwei Wege, eine Analyse:</p>
    <div class="flow-diagram">
      <div class="flow-inputs">
        <div class="flow-step {transcribing ? 'active' : ''} {audioFileName && !transcribing ? 'done' : ''}">
          <svg class="step-icon" width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 18.75a6 6 0 0 0 6-6v-1.5m-6 7.5a6 6 0 0 1-6-6v-1.5m6 7.5v3.75m-3.75 0h7.5M12 15.75a3 3 0 0 1-3-3V4.5a3 3 0 1 1 6 0v8.25a3 3 0 0 1-3 3Z" />
          </svg>
          <span class="step-label">Audio</span>
        </div>
        <span class="flow-or">oder</span>
        <div class="flow-step {inputPath === 'transcript' && !!transcript.trim() ? 'active' : ''} {inputPath === 'transcript' && (loading || !!result) ? 'done' : ''}">
          <svg class="step-icon" width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
          </svg>
          <span class="step-label">Transcript</span>
        </div>
      </div>
      <div class="flow-merge">→</div>
      <div class="flow-common">
        <div class="flow-step {loading ? 'active' : ''} {!!result ? 'done' : ''}">
          <svg class="step-icon" width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
          </svg>
          <span class="step-label">KI analysiert</span>
        </div>
        <div class="flow-arrow {!!result ? 'done' : ''}">→</div>
        <div class="flow-step {!!result ? 'done' : ''}">
          <svg class="step-icon" width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
          </svg>
          <span class="step-label">Ergebnis</span>
        </div>
      </div>
    </div>
    <p class="flow-hint">Audio wird transkribiert oder Transcript direkt einfügen. Beide Wege laufen in dieselbe Analyse.</p>
  </div>

  <main>
    <div class="content">

      <div class="input-panel">
        <div class="panel-header">
          <h2>Meeting-Transcript</h2>
          <span class="panel-hint">Ctrl+Enter zum Analysieren</span>
        </div>

        <div class="audio-examples-row">
          <span class="examples-label">Beispiele:</span>
          <div class="audio-example-list">
            {#each AUDIO_EXAMPLES as ex}
              <div class="audio-example-item">
                <button class="play-btn {playingId === ex.id ? 'playing' : ''}" onclick={() => togglePlay(ex.id)} title={playingId === ex.id ? 'Pause' : 'Abspielen'}>
                  {#if playingId === ex.id}
                    <svg width="12" height="12" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>
                    </svg>
                  {:else}
                    <svg width="12" height="12" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M8 5v14l11-7z"/>
                    </svg>
                  {/if}
                </button>
                <span class="audio-label">{ex.label}</span>
                <button class="transcribe-btn" onclick={() => transcribeAudioExample(ex.id)} disabled={transcribing || loading}>
                  <svg width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 18.75a6 6 0 0 0 6-6v-1.5m-6 7.5a6 6 0 0 1-6-6v-1.5m6 7.5v3.75m-3.75 0h7.5M12 15.75a3 3 0 0 1-3-3V4.5a3 3 0 1 1 6 0v8.25a3 3 0 0 1-3 3Z" />
                  </svg>
                  Transkribieren
                </button>
              </div>
            {/each}
          </div>
        </div>

        <label class="dropzone-label">Audio hochladen</label>
        <label
          class="dropzone {draggingAudio ? 'drag-over' : ''} {transcribing ? 'busy' : ''}"
          ondragover={(e) => { e.preventDefault(); draggingAudio = true; }}
          ondragleave={() => draggingAudio = false}
          ondrop={onAudioDrop}
          role="button"
          tabindex="0"
        >
          {#if transcribing}
            <span class="spinner-dark"></span>
            <span>Transkribiere <strong>{audioFileName}</strong>…</span>
          {:else if audioFileName}
            <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5" style="color:#22c55e;flex-shrink:0">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
            </svg>
            <span style="color:#22c55e">{audioFileName} — Transkript übernommen</span>
          {:else}
            <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5" style="flex-shrink:0">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 18.75a6 6 0 0 0 6-6v-1.5m-6 7.5a6 6 0 0 1-6-6v-1.5m6 7.5v3.75m-3.75 0h7.5M12 15.75a3 3 0 0 1-3-3V4.5a3 3 0 1 1 6 0v8.25a3 3 0 0 1-3 3Z" />
            </svg>
            <span>Audio ablegen oder <u>klicken</u> — MP3, M4A, WAV · max. 25 MB</span>
          {/if}
          <input type="file" accept="audio/*" style="display:none" onchange={onAudioInput} disabled={transcribing || loading} />
        </label>

        <div class="field">
          <label for="transcript">Transcript</label>
          <textarea
            id="transcript"
            placeholder="Meeting-Transcript hier einfügen..."
            bind:value={transcript}
            onkeydown={onKeydown}
            oninput={() => { if (!audioFileName) inputPath = 'transcript'; }}
            disabled={loading}
            rows="16"
          ></textarea>
        </div>

        <button class="analyze-btn" onclick={summarize} disabled={loading || !transcript.trim()}>
          {#if loading}
            <span class="spinner"></span>
            Analysiere...
          {:else}
            <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09Z" />
            </svg>
            Meeting zusammenfassen
          {/if}
        </button>
        <div class="warn-box">
          <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" style="flex-shrink:0;margin-top:1px">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" />
          </svg>
          <span>Eingaben werden zur Verarbeitung an <strong>Groq (USA)</strong> übermittelt und können dort gespeichert werden. Bitte <strong>keine echten oder vertraulichen Meeting-Daten</strong> eingeben.</span>
        </div>
      </div>

      <div class="result-panel">
        <div class="panel-header">
          <h2>Analyse-Ergebnis</h2>
        </div>

        {#if error}
          <div class="error">{error}</div>
        {:else if result}
          <div class="result">

            <div class="result-section">
              <h3>Zusammenfassung</h3>
              <p class="summary-text">{result.summary}</p>
            </div>

            <div class="result-section">
              <h3>
                <svg width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
                </svg>
                Entscheidungen ({result.decisions.length})
              </h3>
              <ul class="decision-list">
                {#each result.decisions as decision}
                  <li>
                    <span class="decision-dot"></span>
                    <span>{decision}</span>
                  </li>
                {/each}
              </ul>
            </div>

            <div class="result-section">
              <div class="todos-header">
                <h3>
                  <svg width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 6.75h12M8.25 12h12m-12 5.25h12M3.75 6.75h.007v.008H3.75V6.75Zm.375 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0ZM3.75 12h.007v.008H3.75V12Zm.375 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm-.375 5.25h.007v.008H3.75v-.008Zm.375 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Z" />
                  </svg>
                  To-Dos ({result.todos.length})
                </h3>
                <button class="copy-btn" onclick={() => {
                  const text = result!.todos.map(t => `[ ] ${t.text} (${t.assignee})`).join('\n');
                  navigator.clipboard.writeText(text);
                }}>
                  <svg width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M15.666 3.888A2.25 2.25 0 0 0 13.5 2.25h-3c-1.03 0-1.9.693-2.166 1.638m7.332 0c.055.194.084.4.084.612v0a.75.75 0 0 1-.75.75H9a.75.75 0 0 1-.75-.75v0c0-.212.03-.418.084-.612m7.332 0c.646.049 1.288.11 1.927.184 1.1.128 1.907 1.077 1.907 2.185V19.5a2.25 2.25 0 0 1-2.25 2.25H6.75A2.25 2.25 0 0 1 4.5 19.5V6.257c0-1.108.806-2.057 1.907-2.185a48.208 48.208 0 0 1 1.927-.184" />
                  </svg>
                  Kopieren
                </button>
              </div>
              <ul class="todo-list">
                {#each result.todos.slice().sort((a, b) => (PRIORITY_ORDER[a.priority] ?? 1) - (PRIORITY_ORDER[b.priority] ?? 1)) as todo}
                  <li class="todo-item">
                    <span class="todo-check">
                      <svg width="12" height="12" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                      </svg>
                    </span>
                    <span class="todo-text">{todo.text}</span>
                    <span class="priority-badge {PRIORITY_CLASS[todo.priority] ?? 'prio-mid'}">{todo.priority}</span>
                    <span class="assignee-badge">{todo.assignee}</span>
                  </li>
                {/each}
              </ul>
            </div>

          </div>
        {:else}
          <div class="empty-state">
            <svg width="40" height="40" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1">
              <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
            </svg>
            <p>Transcript eingeben und analysieren</p>
            <p class="empty-hint">Oder ein Beispiel oben auswählen</p>
          </div>
        {/if}
      </div>

    </div>
  </main>

  <footer>
    Demo von <a href="https://desmond.autonomika.de" target="_blank">Desmond Wong</a>
    &middot; Stack: Groq &middot; llama-3.1-8b &middot; SvelteKit
    &middot; <a href="/impressum">Impressum & Datenschutz</a>
  </footer>

</div>

<style>
  .wrapper { min-height: 100vh; display: flex; flex-direction: column; background: #0c0c0c; }

  header {
    position: sticky; top: 0; z-index: 20;
    background: rgba(12,12,12,0.95); backdrop-filter: blur(8px);
    border-bottom: 1px solid #1e1e1e;
  }
  .header-inner {
    max-width: 1200px; margin: 0 auto; padding: 0 1.25rem;
    height: 52px; display: flex; align-items: center; justify-content: space-between;
  }
  .header-left { display: flex; align-items: center; gap: 0.75rem; }
  .icon {
    width: 34px; height: 34px; border-radius: 9px; flex-shrink: 0;
    background: rgba(34,211,238,0.1); color: #22d3ee;
    display: flex; align-items: center; justify-content: center;
  }
  h1 { font-size: 0.95rem; font-weight: 700; color: #f1f5f9; }
  .subtitle { font-size: 0.7rem; color: #94a3b8; }
  .header-right { display: flex; align-items: center; gap: 0.75rem; }
  .demo-badge {
    display: inline-flex; align-items: center; gap: 5px;
    font-size: 0.68rem; font-weight: 700; letter-spacing: 0.05em;
    color: #22d3ee; background: rgba(34,211,238,0.1);
    border: 1px solid rgba(34,211,238,0.2); padding: 2px 8px; border-radius: 999px;
  }
  .pulse { width: 5px; height: 5px; border-radius: 50%; background: #22d3ee; animation: pulse 1.5s ease-in-out infinite; }
  @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }
  .back-link {
    display: inline-flex; align-items: center; gap: 4px;
    font-size: 0.72rem; color: #94a3b8; text-decoration: none; transition: color 0.15s;
  }
  .back-link:hover { color: #94a3b8; }

  .flow-bar {
    background: #111; border-bottom: 1px solid #1e1e1e;
    padding: 0.75rem 1.25rem; display: flex; flex-direction: column; align-items: center;
  }
  .flow-label { font-size: 0.75rem; color: #b0bfcc; margin-bottom: 0.5rem; }
  .flow-diagram { display: flex; align-items: center; gap: 0.6rem; flex-wrap: wrap; justify-content: center; }
  .flow-inputs { display: flex; flex-direction: column; align-items: stretch; gap: 0.3rem; }
  .flow-or { font-size: 0.65rem; color: #475569; text-align: center; font-style: italic; }
  .flow-merge { font-size: 0.75rem; color: #475569; flex-shrink: 0; }
  .flow-common { display: flex; align-items: center; gap: 0.5rem; }
  .flow-step {
    display: flex; align-items: center; gap: 0.4rem;
    background: #0c0c0c; border: 1px solid #1e1e1e;
    border-radius: 8px; padding: 0.35rem 0.65rem;
    font-size: 0.82rem; color: #b0bfcc; transition: all 0.3s;
  }
  .flow-step.active { border-color: #22d3ee; color: #22d3ee; background: rgba(34,211,238,0.06); }
  .flow-step.done { border-color: #22c55e; color: #22c55e; background: rgba(34,197,94,0.06); }
  .step-icon { flex-shrink: 0; }
  .flow-arrow { font-size: 0.75rem; color: #475569; transition: color 0.3s; }
  .flow-arrow.done { color: #22c55e; }
  .flow-hint { font-size: 0.73rem; color: #94a3b8; margin-top: 0.5rem; text-align: center; }

  main { flex: 1; max-width: 1200px; width: 100%; margin: 0 auto; padding: 1.25rem; }
  .content { display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem; }

  .input-panel, .result-panel {
    background: #111; border: 1px solid #1e1e1e; border-radius: 14px;
    padding: 1.25rem; display: flex; flex-direction: column; gap: 1rem;
  }
  .panel-header { display: flex; align-items: center; justify-content: space-between; }
  h2 { font-size: 0.9rem; font-weight: 700; color: #f1f5f9; }
  .panel-hint { font-size: 0.73rem; color: #94a3b8; }

  .examples { display: flex; flex-direction: column; gap: 0.4rem; }
  .examples-label { font-size: 0.75rem; color: #b0bfcc; }
  .example-chips { display: flex; flex-wrap: wrap; gap: 0.4rem; }
  .example-chip {
    font-size: 0.8rem; color: #b0bfcc; background: #0c0c0c;
    border: 1px solid #252525; padding: 0.25rem 0.6rem; border-radius: 999px;
    cursor: pointer; transition: all 0.15s; text-align: left;
  }
  .example-chip:hover { background: #1a1a1a; color: #f1f5f9; border-color: #22d3ee; }

  .field { display: flex; flex-direction: column; gap: 0.35rem; }
  label { font-size: 0.82rem; color: #c8d8e4; font-weight: 500; }
  textarea {
    background: #0c0c0c; border: 1px solid #252525; color: #e2e8f0;
    border-radius: 10px; padding: 0.55rem 0.85rem; font-size: 0.83rem;
    outline: none; transition: border-color 0.15s; resize: vertical;
    font-family: inherit;
  }
  textarea:focus { border-color: #22d3ee; }
  textarea::placeholder { color: #475569; }
  textarea:disabled { opacity: 0.5; }

  .analyze-btn {
    display: flex; align-items: center; justify-content: center; gap: 0.5rem;
    background: #22d3ee; color: #000; border: none;
    border-radius: 10px; padding: 0.65rem 1rem; font-size: 0.85rem; font-weight: 600;
    cursor: pointer; transition: background 0.15s;
  }
  .analyze-btn:hover:not(:disabled) { background: #06b6d4; }
  .analyze-btn:disabled { opacity: 0.4; cursor: default; }
  .spinner {
    width: 14px; height: 14px; border: 2px solid rgba(0,0,0,0.3);
    border-top-color: #000; border-radius: 50%; animation: spin 0.7s linear infinite;
  }
  @keyframes spin { to { transform: rotate(360deg); } }
  .warn-box {
    display: flex; align-items: flex-start; gap: 0.5rem;
    background: rgba(251,191,36,0.06); border: 1px solid rgba(251,191,36,0.2);
    border-radius: 8px; padding: 0.6rem 0.75rem;
    font-size: 0.75rem; color: #b8900a; line-height: 1.5;
  }
  .warn-box strong { color: #d4a820; }

  .result { display: flex; flex-direction: column; gap: 1.25rem; }
  .result-section { display: flex; flex-direction: column; gap: 0.5rem; }
  .result-section h3 {
    font-size: 0.76rem; font-weight: 600; color: #b0bfcc;
    text-transform: uppercase; letter-spacing: 0.05em;
    display: flex; align-items: center; gap: 0.35rem;
  }
  .summary-text { font-size: 0.92rem; color: #e2eaf2; line-height: 1.65; }

  .decision-list { list-style: none; display: flex; flex-direction: column; gap: 0.5rem; }
  .decision-list li {
    display: flex; align-items: flex-start; gap: 0.6rem;
    background: #0c0c0c; border: 1px solid #1e1e1e; border-radius: 9px;
    padding: 0.55rem 0.75rem; font-size: 0.9rem; color: #e2eaf2; line-height: 1.5;
  }
  .decision-dot {
    width: 7px; height: 7px; border-radius: 50%; background: #60a5fa;
    flex-shrink: 0; margin-top: 0.35rem;
  }

  .todos-header { display: flex; align-items: center; justify-content: space-between; }
  .copy-btn {
    display: inline-flex; align-items: center; gap: 4px;
    font-size: 0.68rem; color: #475569; background: #111;
    border: 1px solid #252525; border-radius: 6px; padding: 2px 8px;
    cursor: pointer; transition: all 0.15s;
  }
  .copy-btn:hover { color: #94a3b8; border-color: #333; }

  .todo-list { list-style: none; display: flex; flex-direction: column; gap: 0.45rem; }
  .todo-item {
    display: flex; align-items: center; gap: 0.6rem;
    background: #0c0c0c; border: 1px solid #1e1e1e; border-radius: 9px;
    padding: 0.5rem 0.75rem;
  }
  .todo-check {
    width: 20px; height: 20px; border-radius: 50%; flex-shrink: 0;
    background: rgba(34,197,94,0.1); border: 1px solid rgba(34,197,94,0.25);
    color: #22c55e; display: flex; align-items: center; justify-content: center;
  }
  .todo-text { font-size: 0.9rem; color: #e2eaf2; flex: 1; line-height: 1.4; }
  .priority-badge {
    font-size: 0.7rem; font-weight: 700; flex-shrink: 0;
    padding: 2px 7px; border-radius: 999px;
  }
  .prio-high { color: #f87171; background: rgba(248,113,113,0.1); border: 1px solid rgba(248,113,113,0.25); }
  .prio-mid  { color: #22d3ee; background: rgba(34,211,238,0.1);  border: 1px solid rgba(34,211,238,0.25);  }
  .prio-low  { color: #4ade80; background: rgba(74,222,128,0.1);  border: 1px solid rgba(74,222,128,0.25);  }

  .assignee-badge {
    font-size: 0.73rem; font-weight: 600; flex-shrink: 0;
    color: #22d3ee; background: rgba(34,211,238,0.1);
    border: 1px solid rgba(34,211,238,0.2); padding: 2px 8px; border-radius: 999px;
  }

  .empty-state {
    flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center;
    gap: 0.75rem; color: #475569; padding: 3rem 1rem; text-align: center;
  }
  .empty-state p { font-size: 0.85rem; }
  .empty-hint { font-size: 0.72rem; color: #475569; }

  .error { background: rgba(248,113,113,0.08); border: 1px solid rgba(248,113,113,0.2); color: #f87171; border-radius: 10px; padding: 0.75rem; font-size: 0.83rem; }

  footer { text-align: center; font-size: 0.68rem; color: #475569; padding: 0.6rem; border-top: 1px solid #1e1e1e; }
  footer a { color: #64748b; text-decoration: none; }
  footer a:hover { color: #94a3b8; }

  .audio-examples-row { display: flex; flex-direction: column; gap: 0.4rem; }
  .audio-example-list { display: flex; flex-wrap: wrap; gap: 0.4rem; }
  .audio-example-item { display: flex; align-items: center; gap: 0.4rem; background: #0c0c0c; border: 1px solid #252525; border-radius: 999px; padding: 0.2rem 0.6rem 0.2rem 0.3rem; }
  .audio-label { font-size: 0.78rem; color: #b0bfcc; }
  .play-btn {
    width: 28px; height: 28px; border-radius: 50%; flex-shrink: 0;
    background: #252525; border: 1px solid #333; color: #94a3b8;
    display: flex; align-items: center; justify-content: center;
    cursor: pointer; transition: all 0.15s;
  }
  .play-btn:hover { background: #334d6b; color: #e2e8f0; }
  .play-btn.playing { background: rgba(34,211,238,0.15); border-color: rgba(34,211,238,0.4); color: #22d3ee; }
  .transcribe-btn {
    display: inline-flex; align-items: center; gap: 0.25rem;
    font-size: 0.72rem; font-weight: 500;
    color: #94a3b8; background: #111; border: 1px solid #252525;
    padding: 0.15rem 0.5rem; border-radius: 999px;
    cursor: pointer; transition: all 0.15s; white-space: nowrap;
  }
  .transcribe-btn:hover:not(:disabled) { color: #22d3ee; border-color: rgba(34,211,238,0.4); background: rgba(34,211,238,0.06); }
  .transcribe-btn:disabled { opacity: 0.4; cursor: default; }

  .dropzone-label { font-size: 0.82rem; color: #c8d8e4; font-weight: 500; }
  .dropzone {
    display: flex; align-items: center; justify-content: center; gap: 0.6rem;
    border: 2px dashed #4a6080; border-radius: 10px; padding: 1rem 1rem;
    font-size: 0.82rem; color: #b0bfcc; cursor: pointer;
    transition: all 0.2s; text-align: center; background: rgba(255,255,255,0.02);
  }
  .dropzone:hover, .dropzone.drag-over {
    border-color: #22d3ee; color: #e2e8f0; background: rgba(34,211,238,0.05);
  }
  .dropzone.busy { cursor: default; border-color: #333; color: #94a3b8; }
  .spinner-dark {
    width: 14px; height: 14px; border: 2px solid rgba(148,163,184,0.2);
    border-top-color: #94a3b8; border-radius: 50%; animation: spin 0.7s linear infinite; flex-shrink: 0;
  }

  @media (max-width: 768px) {
    .content { grid-template-columns: 1fr; }
    .subtitle { display: none; }
    .flow-diagram { gap: 0.3rem; }
    .flow-common .flow-arrow { display: none; }
  }
</style>
