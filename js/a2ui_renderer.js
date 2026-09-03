/**
 * A2UI PROTOCOL (v0.9) GENERATIVE UI RENDERER
 * Converts declarative JSON schemas from Gemini / Antigravity into live interactive widgets
 */

class A2UIRenderer {
  constructor() {
    this.handlers = {};
  }

  render(containerId, schema) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = '';
    const element = this.buildComponent(schema);
    container.appendChild(element);
  }

  buildComponent(schema) {
    const { type, props = {}, children = [] } = schema;

    let el;
    switch (type) {
      case 'Card':
        el = document.createElement('div');
        el.className = 'a2ui-card';
        if (props.title) {
          const head = document.createElement('div');
          head.className = 'a2ui-header';
          head.innerHTML = `
            <div style="font-weight:700; color:#fff; font-size:15px;">${props.title}</div>
            ${props.badge ? `<span class="a2ui-tag">${props.badge}</span>` : ''}
          `;
          el.appendChild(head);
        }
        if (props.description) {
          const desc = document.createElement('p');
          desc.style.cssText = 'font-size:13px; color:var(--text-muted); margin-bottom:14px;';
          desc.innerText = props.description;
          el.appendChild(desc);
        }
        break;

      case 'MetricRow':
        el = document.createElement('div');
        el.style.cssText = 'display:flex; justify-content:space-between; align-items:center; background:rgba(0,0,0,0.2); padding:10px 14px; border-radius:10px; margin-bottom:10px; border:1px solid var(--border-glass);';
        el.innerHTML = `
          <span style="font-size:13px; color:var(--text-muted);">${props.label}</span>
          <span style="font-weight:700; font-family:var(--font-mono); color:${props.color || 'var(--emerald-400)'};">${props.value}</span>
        `;
        break;

      case 'ActionButton':
        el = document.createElement('button');
        el.className = `btn ${props.variant === 'primary' ? 'btn-primary' : props.variant === 'indigo' ? 'btn-indigo' : 'btn-secondary'} btn-sm`;
        el.innerHTML = `${props.icon ? props.icon + ' ' : ''}${props.label}`;
        if (props.action) {
          el.onclick = () => {
            if (props.confirm) {
              if (confirm(props.confirm)) {
                this.executeAction(props.action, props.payload);
              }
            } else {
              this.executeAction(props.action, props.payload);
            }
          };
        }
        break;

      case 'ButtonGroup':
        el = document.createElement('div');
        el.style.cssText = 'display:flex; gap:10px; margin-top:14px; flex-wrap:wrap;';
        break;

      case 'ProgressBar':
        el = document.createElement('div');
        el.style.cssText = 'margin:12px 0;';
        const progress = Math.min(100, Math.max(0, props.value || 0));
        el.innerHTML = `
          <div style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:4px;">
            <span style="color:var(--text-muted);">${props.label || ''}</span>
            <span style="font-family:var(--font-mono); color:var(--emerald-400); font-weight:700;">${progress}%</span>
          </div>
          <div style="width:100%; height:8px; background:var(--bg-tertiary); border-radius:4px; overflow:hidden;">
            <div style="width:${progress}%; height:100%; background:linear-gradient(90deg, var(--emerald-500), var(--cyan-400)); border-radius:4px; transition: width 0.6s ease;"></div>
          </div>
        `;
        break;

      case 'AlertBanner':
        el = document.createElement('div');
        const isSuccess = props.status === 'success';
        el.style.cssText = `background:${isSuccess ? 'rgba(16, 185, 129, 0.1)' : 'rgba(99, 102, 241, 0.1)'}; border:1px solid ${isSuccess ? 'rgba(16, 185, 129, 0.3)' : 'rgba(99, 102, 241, 0.3)'}; border-radius:10px; padding:12px 16px; font-size:13px; color:#fff; margin-bottom:12px; display:flex; align-items:center; gap:10px;`;
        el.innerHTML = `<span>${props.icon || '🛡️'}</span> <div>${props.message}</div>`;
        break;

      default:
        el = document.createElement('div');
    }

    if (children && children.length > 0) {
      children.forEach(childSchema => {
        el.appendChild(this.buildComponent(childSchema));
      });
    }

    return el;
  }

  executeAction(actionName, payload) {
    if (this.handlers[actionName]) {
      this.handlers[actionName](payload);
    } else {
      console.log(`[A2UI Action Triggered] ${actionName}:`, payload);
      alert(`[A2UI Действие Выполнено] ${actionName}\nПараметры: ${JSON.stringify(payload, null, 2)}`);
    }
  }

  registerHandler(actionName, fn) {
    this.handlers[actionName] = fn;
  }
}

window.A2UIRenderer = new A2UIRenderer();
