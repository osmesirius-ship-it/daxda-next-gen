/**
 * DAXDA AmbientCDS Simulator Client App
 * Controls real-time simulation across AWS EUM SMS, RCS, WhatsApp, and SES.
 */

document.addEventListener('DOMContentLoaded', () => {
  const btnFullFlow = document.getElementById('btn-full-flow');
  const btnReset = document.getElementById('btn-reset');
  const btnStep1 = document.getElementById('btn-step1');
  const btnStep2 = document.getElementById('btn-step2');
  const btnStep3 = document.getElementById('btn-step3');
  const btnStep4 = document.getElementById('btn-step4');

  const smsFeed = document.getElementById('sms-feed');
  const rcsFeed = document.getElementById('rcs-feed');
  const waFeed = document.getElementById('wa-feed');
  const emailFeed = document.getElementById('email-feed');
  const bedrockLogs = document.getElementById('bedrock-logs');
  const governanceLogs = document.getElementById('governance-logs');

  const waInput = document.getElementById('wa-input');
  const waSend = document.getElementById('wa-send');

  const patChannel = document.getElementById('pat-channel');
  const patStatus = document.getElementById('pat-status');

  function addLog(box, text, color = '#a5f3fc') {
    const div = document.createElement('div');
    const time = new Date().toLocaleTimeString();
    div.innerHTML = `<span style="color:#64748b;">[${time}]</span> <span style="color:${color};">${text}</span>`;
    box.appendChild(div);
    box.scrollTop = box.scrollHeight;
  }

  async function fetchState() {
    try {
      const res = await fetch('/api/state');
      const data = await res.json();
      renderState(data);
    } catch (e) {
      console.error('Error fetching state', e);
    }
  }

  function renderState(data) {
    const s = data.session;
    patChannel.textContent = s.current_channel;
    patStatus.textContent = s.status;

    // 1. Render SMS
    if (data.sms_messages && data.sms_messages.length > 0) {
      smsFeed.innerHTML = '';
      data.sms_messages.forEach(m => {
        const b = document.createElement('div');
        b.className = m.direction === 'OUTBOUND' ? 'bubble bubble-outbound-sms' : 'bubble bubble-inbound';
        b.innerHTML = `<div>${m.body}</div><div class="bubble-time">AWS EUM • ${new Date(m.timestamp * 1000).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})}</div>`;
        smsFeed.appendChild(b);
      });
      smsFeed.scrollTop = smsFeed.scrollHeight;
    }

    // 2. Render RCS
    if (data.rcs_messages && data.rcs_messages.length > 0) {
      rcsFeed.innerHTML = '';
      data.rcs_messages.forEach(m => {
        if (m.type === 'RICH_CARD') {
          const card = document.createElement('div');
          card.className = 'rcs-card-box';
          let chipsHtml = '';
          m.chips.forEach(c => {
            chipsHtml += `<button class="rcs-chip-btn" data-postback="${c.postback}">${c.text}</button>`;
          });
          card.innerHTML = `
            <div class="rcs-card-media">💊</div>
            <div class="rcs-card-content">
              <h4>${m.title}</h4>
              <p>${m.description}</p>
              <div class="rcs-chips-group">${chipsHtml}</div>
            </div>
          `;
          rcsFeed.appendChild(card);

          // Add click listeners to RCS chips
          card.querySelectorAll('.rcs-chip-btn').forEach(btn => {
            btn.addEventListener('click', () => {
              const postback = btn.getAttribute('data-postback');
              if (postback === 'switch_to_whatsapp') {
                triggerStep3();
              } else if (postback === 'pickup_today_main_st') {
                triggerStep4();
              } else {
                alert(`RCS Action Triggered: ${btn.textContent}`);
              }
            });
          });
        }
      });
      rcsFeed.scrollTop = rcsFeed.scrollHeight;
    }

    // 3. Render WhatsApp
    if (data.whatsapp_messages && data.whatsapp_messages.length > 0) {
      waFeed.innerHTML = '';
      data.whatsapp_messages.forEach(m => {
        const b = document.createElement('div');
        b.className = m.direction === 'OUTBOUND' ? 'wa-bubble-out' : 'wa-bubble-in';
        let buttonsHtml = '';
        if (m.buttons && m.buttons.length > 0) {
          buttonsHtml = '<div class="wa-btn-group">';
          m.buttons.forEach(btn => {
            buttonsHtml += `<button class="wa-quick-btn" data-btn-id="${btn.id}">${btn.title}</button>`;
          });
          buttonsHtml += '</div>';
        }
        b.innerHTML = `<div>${m.text.replace(/\n/g, '<br>')}</div>${buttonsHtml}`;
        waFeed.appendChild(b);

        b.querySelectorAll('.wa-quick-btn').forEach(qb => {
          qb.addEventListener('click', () => {
            const btnId = qb.getAttribute('data-btn-id');
            if (btnId === 'confirm_pickup_5pm') {
              triggerStep4();
            } else if (btnId === 'ask_side_effects') {
              sendPatientQuery("Can I consume alcohol with Metformin?");
            } else {
              sendPatientQuery("I need to upload my new prescription insurance card.");
            }
          });
        });
      });
      waFeed.scrollTop = waFeed.scrollHeight;
    }

    // 4. Render SES Email
    if (data.ses_emails && data.ses_emails.length > 0) {
      emailFeed.innerHTML = '';
      data.ses_emails.forEach(e => {
        const item = document.createElement('div');
        item.className = 'email-rendered-box';
        item.innerHTML = `
          <div style="font-weight:700; color:#38bdf8; margin-bottom:4px;">✉️ ${e.subject}</div>
          <div style="font-size:11px; color:#94a3b8; margin-bottom:12px;">From: prescriptions@care.daxda.ai &bull; To: ${e.recipient}</div>
          <div class="email-passcode-badge">
            <div style="font-size:10px; color:#94a3b8;">SHOW AT PHARMACY COUNTER</div>
            <div class="email-passcode-text">${e.passcode}</div>
            <div style="font-size:11px; color:#38bdf8; margin-top:4px;">Ready: Today 5:00 PM – 7:30 PM</div>
          </div>
          <div style="font-size:11px; line-height:1.5; color:#cbd5e1;">
            <strong>Medication:</strong> Metformin HCL 500mg<br>
            <strong>Location:</strong> Walgreens Pharmacy #4192 (120 Main St)<br>
            <strong>Physician:</strong> Dr. Nicole S. (NPI Verified)
          </div>
          <div style="margin-top:12px; font-size:9.5px; color:#64748b; word-break:break-all; font-family:monospace;">
            SHA-256 Audit: ${e.audit_sha256}
          </div>
        `;
        emailFeed.appendChild(item);
      });
      emailFeed.scrollTop = emailFeed.scrollHeight;
    }
  }

  // Action Triggers
  async function triggerStep1() {
    addLog(bedrockLogs, "[CDS EUM SMS] Dispatching proactive adherence notification...", "#38bdf8");
    addLog(governanceLogs, "[DAXDA Sentinel] Evaluating outbound SMS: PHI de-identification verified (ALLOW)", "#4ade80");
    await fetch('/api/flow/step1_sms', { method: 'POST' });
    await fetchState();
  }

  async function triggerStep2() {
    addLog(bedrockLogs, "[CDS EUM RCS] Escalating SMS interaction to rich card carousel...", "#a855f7");
    await fetch('/api/flow/step2_rcs', { method: 'POST' });
    await fetchState();
  }

  async function triggerStep3() {
    addLog(bedrockLogs, "[Bedrock AgentCore] Routing context to AWS EUM WhatsApp. Preserving prior SMS & RCS state.", "#22c55e");
    await fetch('/api/flow/step3_whatsapp', { method: 'POST' });
    await fetchState();
  }

  async function triggerStep4() {
    addLog(bedrockLogs, "[Bedrock ActionGroup] schedule_pickup_slot executed for 5:00 PM.", "#eab308");
    addLog(governanceLogs, "[DAXDA Sentinel] Prescribing doctor NPI checked; generating SHA-256 receipt.", "#4ade80");
    addLog(bedrockLogs, "[Amazon SES] Delivering formal prescription receipt and QR code to email.", "#38bdf8");
    await fetch('/api/flow/step4_ses', { method: 'POST' });
    await fetchState();
  }

  async function sendPatientQuery(text) {
    addLog(bedrockLogs, `[WhatsApp Inbound] Patient query received: "${text}"`, "#93c5fd");
    const res = await fetch('/api/agent/interact', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text, channel: 'WHATSAPP' })
    });
    const data = await res.json();
    addLog(bedrockLogs, `[Bedrock Reasoning] Action: ${data.action_taken || 'conversational_response'} (Latency: ${data.latency_ms}ms)`, "#34d399");
    if (data.governance) {
      addLog(governanceLogs, `[DAXDA Sentinel] Disposition: ${data.governance.disposition} | Receipt: ${data.governance.audit_receipt.slice(0, 16)}...`, "#4ade80");
    }
    await fetchState();
  }

  // Hook up buttons
  btnStep1.addEventListener('click', triggerStep1);
  btnStep2.addEventListener('click', triggerStep2);
  btnStep3.addEventListener('click', triggerStep3);
  btnStep4.addEventListener('click', triggerStep4);

  document.getElementById('sms-reply-1').addEventListener('click', () => {
    triggerStep2();
  });
  document.getElementById('sms-reply-2').addEventListener('click', () => {
    triggerStep3();
  });

  waSend.addEventListener('click', () => {
    const val = waInput.value.trim();
    if (val) {
      sendPatientQuery(val);
      waInput.value = '';
    }
  });

  waInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      waSend.click();
    }
  });

  btnFullFlow.addEventListener('click', async () => {
    btnFullFlow.disabled = true;
    btnFullFlow.textContent = "Running Omnichannel Sequence...";
    await triggerStep1();
    setTimeout(async () => {
      await triggerStep2();
      setTimeout(async () => {
        await triggerStep3();
        setTimeout(async () => {
          await triggerStep4();
          btnFullFlow.disabled = false;
          btnFullFlow.textContent = "⚡ Run Full Omnichannel Journey";
        }, 1500);
      }, 1500);
    }, 1500);
  });

  btnReset.addEventListener('click', () => {
    window.location.reload();
  });

  // Initial load
  fetchState();
  setInterval(fetchState, 3000);
});
