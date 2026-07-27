// Subject selection
const subjects = document.querySelectorAll('.subject');
const subjectInput = document.getElementById('subjectInput');
subjects.forEach(btn => {
  btn.addEventListener('click', () => {
    subjects.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    subjectInput.value = btn.dataset.value;
  });
});

// Smooth scroll for CTA
const startBtn = document.getElementById('startBtn');
const startCTA = document.getElementById('startCTA');
const formSection = document.getElementById('form');
[startBtn, startCTA].forEach(el => el && el.addEventListener('click', (e) => {
  e.preventDefault();
  formSection.scrollIntoView({behavior:'smooth', block:'start'});
}));

// Drag and drop helpers
function setupDropzone(dropId, fileInputId, previewId){
  const dropzone = document.getElementById(dropId);
  const fileInput = document.getElementById(fileInputId);
  const preview = document.getElementById(previewId);

  ['dragenter','dragover'].forEach(ev => {
    dropzone.addEventListener(ev, (e)=>{e.preventDefault();dropzone.classList.add('drag');});
  });
  ['dragleave','drop'].forEach(ev => {
    dropzone.addEventListener(ev, (e)=>{e.preventDefault();dropzone.classList.remove('drag');});
  });

  dropzone.addEventListener('drop', (e)=>{
    const f = e.dataTransfer.files && e.dataTransfer.files[0];
    if(f) fileInput.files = e.dataTransfer.files; handleFiles(fileInput, preview);
  });

  dropzone.addEventListener('click', ()=> fileInput.click());
  fileInput.addEventListener('change', ()=> handleFiles(fileInput, preview));
}

function handleFiles(fileInput, preview){
  preview.innerHTML = '';
  const files = Array.from(fileInput.files || []);
  files.forEach((file, idx)=>{
    if(!file.type.startsWith('image/')) return;
    const reader = new FileReader();
    reader.onload = (ev)=>{
      const wrap = document.createElement('div'); wrap.className='thumb';
      const img = document.createElement('img'); img.src = ev.target.result;
      const remove = document.createElement('div'); remove.className='remove'; remove.innerText='×';
      remove.title = '삭제';
      remove.addEventListener('click', ()=>{
        // remove this file from input
        const dt = new DataTransfer();
        Array.from(fileInput.files).forEach((f,i)=>{ if(i!==idx) dt.items.add(f); });
        fileInput.files = dt.files; handleFiles(fileInput, preview);
      });
      wrap.appendChild(img); wrap.appendChild(remove); preview.appendChild(wrap);
    };
    reader.readAsDataURL(file);
  });
}

setupDropzone('problemDrop','problemFile','problemPreview');
setupDropzone('solutionDrop','solutionFile','solutionPreview');

// Form submission & simulated analysis
const analyzeBtn = document.getElementById('analyzeBtn');
const resultPanel = document.getElementById('result');
const resultBody = document.getElementById('resultBody');
const analysisForm = document.getElementById('analysisForm');
const newAnalysis = document.getElementById('newAnalysis');

function showSpinner(target){
  target.innerHTML = '<div style="display:flex;gap:12px;align-items:center"><div class="spinner"></div><div>AI가 분석중입니다...</div></div>';
}

analyzeBtn.addEventListener('click', async ()=>{
  // basic validation
  if(!subjectInput.value){ alert('과목을 선택하세요.'); return; }
  if(!document.getElementById('correctAnswer').value.trim() || !document.getElementById('myAnswer').value.trim()){ alert('정답과 내 답을 입력해주세요.'); return; }

  analyzeBtn.disabled = true; analyzeBtn.innerText = '분석 중...';
  showSpinner(resultBody);
  resultPanel.hidden = false;

  const formData = new FormData();
  formData.append('subject', subjectInput.value);
  formData.append('correct', document.getElementById('correctAnswer').value.trim());
  formData.append('mine', document.getElementById('myAnswer').value.trim());
  formData.append('mySolution', document.getElementById('mySolution').value.trim());
  formData.append('question', document.getElementById('question').value.trim());
  const probFile = document.getElementById('problemFile').files[0];
  const solFile = document.getElementById('solutionFile').files[0];
  if(probFile) formData.append('problemFile', probFile);
  if(solFile) formData.append('solutionFile', solFile);

  try{
    const resp = await fetch('/api/analyze', { method:'POST', body: formData });
    const data = await resp.json();
    if(resp.ok && data.ok){
      if(data.demo){
        // provider not configured on server — show demo
        const d = data.analysis;
        resultBody.innerHTML = `<div class="result-summary"><p><strong>과목:</strong> ${escapeHtml(d.subject)}</p><h4>요약</h4><p>${escapeHtml(d.summary)}</p><h4>권장</h4><ul>${d.recommendations.map(r=>`<li>${escapeHtml(r)}</li>`).join('')}</ul></div>`;
      } else {
        // show raw provider payload (you can customize parsing per provider)
        resultBody.innerHTML = `<pre style="white-space:pre-wrap">${escapeHtml(JSON.stringify(data.provider, null, 2))}</pre>`;
      }
    } else {
      resultBody.innerHTML = `<div class="small-muted">서버 에러: ${escapeHtml(data.error || 'Unknown')}</div>`;
    }
  }catch(err){
    // network or fetch error — fallback to local simulation
    resultBody.innerHTML = `<div class="small-muted">요청 실패: ${escapeHtml(err.message)}. 로컬 시뮬레이션으로 대체합니다.</div>`;
    await new Promise(res=>setTimeout(res,800));
    const subject = subjectInput.value;
    const correct = document.getElementById('correctAnswer').value.trim();
    const mine = document.getElementById('myAnswer').value.trim();
    const mySol = document.getElementById('mySolution').value.trim();
    const question = document.getElementById('question').value.trim();
    const analysisHtml = `
      <div class="result-summary">
        <p><strong>과목:</strong> ${subject}</p>
        <p><strong>정답:</strong> ${correct} &nbsp; <strong>내 답:</strong> ${mine}</p>
        <hr />
        <h4>오답 원인 (예시)</h4>
        <p>계산 실수 또는 풀이 단계 누락으로 보입니다. 주요 단계에서의 연산과 단위 검토가 필요합니다.</p>
        <h4>개선 포인트</h4>
        <ul>
          <li>풀이의 각 단계에 이유를 적어 검증 루틴을 만드세요.</li>
          <li>유사 문제 3문제를 반복 연습해 개념을 확립하세요.</li>
        </ul>
        ${question?`<h4>질문에 대한 메모</h4><p>${escapeHtml(question)}</p>`:''}
        ${mySol?`<h4>내 풀이 요약</h4><p class="small-muted">${escapeHtml(mySol)}</p>`:''}
      </div>
    `;
    resultBody.innerHTML += analysisHtml;
  } finally{
    analyzeBtn.disabled = false; analyzeBtn.innerText = 'AI 오답 분석 시작 🚀';
  }
});

newAnalysis.addEventListener('click', ()=>{
  resultPanel.hidden = true; resultBody.innerHTML = '';
  analysisForm.reset();
  subjectInput.value=''; subjects.forEach(b=>b.classList.remove('active'));
  document.getElementById('problemPreview').innerHTML='';
  document.getElementById('solutionPreview').innerHTML='';
  window.scrollTo({top:document.getElementById('form').offsetTop-20, behavior:'smooth'});
});

// Render detailed feedback: summary, comparison, recommendations
function renderDetailedResult(obj){
  // obj may be demo analysis or provider payload structure
  // Normalize
  const subject = obj.subject || (obj.provider && obj.provider.subject) || '미지정';
  const summary = obj.summary || (obj.provider && obj.provider.summary) || '요약 정보를 생성할 수 없습니다.';
  const recs = obj.recommendations || (obj.provider && obj.provider.recommendations) || [];
  // Steps: try to get structured steps, otherwise fabricate from text
  let correctSteps = [];
  let mySteps = [];
  if(obj.correctSteps) correctSteps = obj.correctSteps;
  if(obj.mySteps) mySteps = obj.mySteps;
  // fallback: try splitting mySolution into lines
  if(!mySteps.length && (obj.mySolution || obj.provider && obj.provider.mySolution)){
    const s = obj.mySolution || (obj.provider && obj.provider.mySolution) || '';
    mySteps = s.split(/\n+/).map(l=>l.trim()).filter(Boolean);
  }
  // If no correctSteps, create a mock correct steps based on length of mySteps or 3 default
  if(!correctSteps.length){
    if(mySteps.length){ correctSteps = mySteps.map((_,i)=>`정답 풀이 단계 ${i+1}: 핵심 연산/논리`);} else { correctSteps = ['정답 풀이 단계 1: 핵심 개념 적용','정답 풀이 단계 2: 계산/추론','정답 풀이 단계 3: 결과 정리']; }
  }

  // Build HTML
  const maxLen = Math.max(correctSteps.length, mySteps.length);
  let compHtml = '<div class="comparison">';
  compHtml += '<div class="row header"><div class="cell">정답 풀이</div><div class="cell">내 풀이</div></div>';
  for(let i=0;i<maxLen;i++){
    const a = correctSteps[i] || '';
    const b = mySteps[i] || '';
    const cls = (a && b && a.trim()===b.trim()) ? 'step-ok' : (b? 'step-miss' : '');
    compHtml += `<div class="row"><div class="cell ${cls}">${escapeHtml(a||'—')}</div><div class="cell ${cls}">${escapeHtml(b||'—')}</div></div>`;
  }
  compHtml += '</div>';

  const recHtml = recs.length ? `<div class="exercise-list"><h4>추천 연습</h4>` + recs.map(r=>`<div class="exercise">${escapeHtml(r)}</div>`).join('') + `</div>` : '';

  const html = `
    <div class="feedback-card">
      <div class="meta">
        <div style="display:flex;gap:12px;align-items:center;margin-bottom:8px"><div class="badge">${escapeHtml(subject)}</div><div style="font-weight:700">AI 분석 요약</div></div>
        <p class="small-muted">${escapeHtml(summary)}</p>
        ${recHtml}
      </div>
    </div>
    ${compHtml}
  `;

  resultBody.innerHTML = html;
}

// Small download handler for report (JSON)
document.getElementById('downloadReport').addEventListener('click', ()=>{
  const content = resultBody.innerText || resultBody.innerHTML || '';
  const blob = new Blob([content], {type:'text/plain;charset=utf-8'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a'); a.href = url; a.download = 'ai_analysis.txt'; document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(url);
});

function escapeHtml(str){ return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

// Accessibility: allow keyboard subject selection
subjects.forEach((s, i)=>{
  s.setAttribute('tabindex',0);
  s.addEventListener('keydown', e=>{ if(e.key==='Enter' || e.key===' ') s.click(); });
});

// small UX: clicking anywhere on header CTA scrolls to form
document.querySelectorAll('.nav .btn, .nav a').forEach(a=> a.addEventListener('click', (e)=>{ if(a.id!=='startCTA') return; e.preventDefault(); formSection.scrollIntoView({behavior:'smooth'}); }));
