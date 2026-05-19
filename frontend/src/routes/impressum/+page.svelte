<svelte:head>
  <title>Impressum – Meeting-Zusammenfassung</title>
</svelte:head>

<div class="wrapper">
  <div class="content">
    <a href="/" class="back">&larr; Zurück zur Demo</a>

    <h1>Impressum</h1>
    <p>Angaben gemäß §5 TMG</p>

    <section>
      <h2>Verantwortlich</h2>
      <p>
        Desmond Wong<br>
        Lichtenbroicher Weg 29<br>
        40472 Düsseldorf<br>
        Deutschland
      </p>
      <p>E-Mail: <a href="mailto:desmond.wong@autonomika.de">desmond.wong@autonomika.de</a></p>
    </section>

    <hr>

    <h1>Datenschutzerklärung</h1>

    <section>
      <h2>Erhobene Daten</h2>
      <p>Diese Website setzt keine Tracking-Cookies und verwendet keine Analyse-Tools. Es werden keine personenbezogenen Nutzerdaten dauerhaft gespeichert.</p>
    </section>

    <section>
      <h2>Nutzung der KI-Funktion</h2>
      <p>Die eingegebenen Meeting-Transcripts werden zur Analyse an die Groq Cloud API (Groq Inc., 101 2nd St, San Francisco, CA 94105, USA) übermittelt. Die Verarbeitung erfolgt auf US-amerikanischen Servern. Es werden keine Eingaben dauerhaft gespeichert. Bitte geben Sie keine echten personenbezogenen Daten oder vertrauliche Meeting-Inhalte ein.</p>
    </section>

    <section>
      <h2>Ihre Rechte</h2>
      <p>Sie haben jederzeit das Recht auf Auskunft, Berichtigung und Löschung Ihrer personenbezogenen Daten. Kontakt: <a href="mailto:desmond.wong@autonomika.de">desmond.wong@autonomika.de</a></p>
      <p>Aufsichtsbehörde: Landesbeauftragte für Datenschutz und Informationsfreiheit NRW (<a href="https://www.ldi.nrw.de" target="_blank" rel="noopener">ldi.nrw.de</a>).</p>
    </section>

    <section>
      <h2>Haftungsausschluss</h2>
      <p>Dies ist eine Demonstrations-Anwendung. Für die Richtigkeit der KI-generierten Zusammenfassungen wird keine Gewähr übernommen.</p>
    </section>
  </div>
</div>

<style>
  .wrapper { min-height: 100vh; background: #162032; color: #cbd5e1; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; padding: 2rem 1rem; }
  .content { max-width: 680px; margin: 0 auto; }
  .back { display: inline-block; color: #64748b; text-decoration: none; font-size: 0.85rem; margin-bottom: 2rem; }
  .back:hover { color: #94a3b8; }
  h1 { font-size: 1.6rem; font-weight: 700; color: #f1f5f9; margin-bottom: 0.25rem; }
  h1 + p { font-size: 0.8rem; color: #475569; margin-bottom: 1.75rem; }
  h2 { font-size: 1rem; font-weight: 600; color: #e2e8f0; margin-bottom: 0.5rem; }
  section { margin-bottom: 1.5rem; }
  p { font-size: 0.88rem; line-height: 1.7; color: #94a3b8; margin-bottom: 0.6rem; }
  a { color: #fbbf24; text-decoration: none; }
  a:hover { text-decoration: underline; }
  hr { border: none; border-top: 1px solid #243447; margin: 2.5rem 0; }
</style>
