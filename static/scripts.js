const api = {
    async get(path) {
        const r = await fetch(path);
        if (!r.ok) throw new Error(await r.text());
        return r.json();
    },
    async post(path, body) {
        const r = await fetch(path, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(body),
        });
        if (!r.ok) throw new Error(await r.text());
        return r.json();
    },
};

function el(tag, attrs = {}, children = []) {
    const n = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
        if (k === 'class') n.className = v;
        else if (k === 'text') n.textContent = v;
        else n.setAttribute(k, v);
    }
    for (const c of children) n.appendChild(c);
    return n;
}

async function refreshCharacters() {
    const chars = await api.get('/api/characters');
    const list = document.getElementById('character-list');
    list.innerHTML = '';
    for (const c of chars) {
        const card = el('div', {class: 'card'});
        card.appendChild(el('h3', {text: c.name}));
        card.appendChild(el('p', {text: `HP ${c.health}/${c.max_health}`}));
        card.appendChild(el('p', {text: `STR ${c.strength} · AGI ${c.agility}`}));
        if (c.special_skills.length) {
            card.appendChild(el('p', {text: 'Skills: ' + c.special_skills.join(', ')}));
        }
        list.appendChild(card);
    }
    // populate match selects
    for (const id of ['fighter_a', 'fighter_b']) {
        const sel = document.querySelector(`select[name="${id}"]`);
        const prev = sel.value;
        sel.innerHTML = '';
        for (const c of chars) {
            const opt = el('option', {value: c.name, text: c.name});
            sel.appendChild(opt);
        }
        if (prev) sel.value = prev;
    }
    // populate tournament fighters checkboxes
    const fs = document.getElementById('tournament-fighters');
    fs.querySelectorAll('label').forEach(n => n.remove());
    for (const c of chars) {
        const label = el('label');
        const cb = el('input', {type: 'checkbox', name: 'fighters', value: c.name});
        label.appendChild(cb);
        label.appendChild(document.createTextNode(' ' + c.name));
        fs.appendChild(label);
    }
}

async function refreshTournaments() {
    const ts = await api.get('/api/tournaments');
    const list = document.getElementById('tournament-list');
    list.innerHTML = '';
    for (const t of ts) {
        const wrap = el('div', {class: 'card'});
        wrap.appendChild(el('h3', {text: `${t.name} (${t.format})`}));
        wrap.appendChild(el('p', {text: `Champion: ${t.champion || '—'}`}));
        t.bracket.forEach((rnd, i) => {
            wrap.appendChild(el('h4', {text: `Round ${i + 1}`}));
            for (const m of rnd) {
                const p = el('p', {text: `${m.fighter_a} vs ${m.fighter_b} → ${m.winner}`});
                wrap.appendChild(p);
            }
        });
        list.appendChild(wrap);
    }
}

function formData(form) {
    const data = {};
    for (const [k, v] of new FormData(form).entries()) {
        if (data[k] !== undefined) {
            if (!Array.isArray(data[k])) data[k] = [data[k]];
            data[k].push(v);
        } else {
            data[k] = v;
        }
    }
    return data;
}

document.getElementById('create-character-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const d = formData(e.target);
    try {
        await api.post('/api/characters', d);
        e.target.reset();
        await refreshCharacters();
    } catch (err) {
        alert('Create failed: ' + err.message);
    }
});

document.getElementById('match-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const d = formData(e.target);
    const out = document.getElementById('match-result');
    out.innerHTML = '';
    try {
        const r = await api.post('/api/match', d);
        out.appendChild(el('h3', {text: `Winner: ${r.winner}`}));
        for (const line of r.log) {
            out.appendChild(el('div', {text: line}));
        }
    } catch (err) {
        out.textContent = 'Match failed: ' + err.message;
    }
});

document.getElementById('tournament-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const d = formData(e.target);
    const fighters = Array.from(
        e.target.querySelectorAll('input[name="fighters"]:checked')
    ).map(i => i.value);
    try {
        await api.post('/api/tournaments', {
            name: d.name,
            format: d.format,
            fighters,
        });
        e.target.reset();
        await refreshTournaments();
    } catch (err) {
        alert('Tournament failed: ' + err.message);
    }
});

(async () => {
    await refreshCharacters();
    await refreshTournaments();
})();