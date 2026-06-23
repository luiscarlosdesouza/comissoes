<div data-cad-msg-container data-timeout="{{ (int) config('laravel-usp-theme.cadastros_auxiliares_mensagens_timeout', 5) }}">
</div>

<script>
  (function () {
    const container = document.querySelector('[data-cad-msg-container]');
    if (!container) return;

    const timeoutSeconds = Number(container.dataset.timeout || 0);
    const useAutoDismiss = timeoutSeconds > 0;

    const endpoint = @json(route('usp-theme.cadastros-auxiliares.mensagens-proxy'));
    const isAuth = @json(auth()->check());
    const refreshSeconds = Number(@json(config('laravel-usp-theme.cadastros_auxiliares_mensagens_refresh', 30)) || 30);
    const refreshMs = refreshSeconds * 1000;
    const timeoutMs = timeoutSeconds * 1000;

    let lastSignature = '';

    const removeLater = (alert) => {
      if (!useAutoDismiss) {
        return;
      }

      setTimeout(() => {
        alert.remove();
      }, timeoutMs);
    };

    const deveExibirMensagem = (mensagem) => {
      if (mensagem.ativo === false) {
        return false;
      }

      const publico = mensagem.publico;

      if (publico === false) {
        return isAuth;
      }

      if (Array.isArray(publico)) {
        const normalizados = publico
          .map((item) => String(item || '').trim().toLowerCase().replace('á', 'a'))
          .filter(Boolean);

        if (normalizados.includes('usuario')) {
          return isAuth;
        }
      }

      if (typeof publico === 'string' && publico.trim() !== '') {
        const normalizados = publico
          .split(',')
          .map((item) => String(item || '').trim().toLowerCase().replace('á', 'a'))
          .filter(Boolean);

        if (normalizados.includes('usuario')) {
          return isAuth;
        }
      }

      return true;
    };

    const criarAlert = (mensagem) => {
      const classe = ({
        erro: 'danger',
        aviso: 'warning',
        sucesso: 'success',
        info: 'info'
      })[mensagem.tipo || 'info'] || 'info';

      const alert = document.createElement('div');
      alert.className = `alert alert-${classe} alert-dismissible`;
      alert.setAttribute('data-cad-msg-alert', '1');

      if (mensagem.titulo) {
        const strong = document.createElement('strong');
        strong.textContent = mensagem.titulo;
        alert.appendChild(strong);
        alert.appendChild(document.createElement('br'));
      }

      const conteudo = document.createElement('span');
      conteudo.innerHTML = String(mensagem.conteudo || '');
      alert.appendChild(conteudo);

      const closeButton = document.createElement('button');
      closeButton.type = 'button';
      closeButton.className = 'close';
      closeButton.setAttribute('aria-label', 'Fechar');
      closeButton.innerHTML = '<span aria-hidden="true">&times;</span>';
      closeButton.addEventListener('click', () => alert.remove());
      alert.appendChild(closeButton);

      removeLater(alert);
      return alert;
    };

    const renderizarMensagens = (mensagens) => {
      const visiveis = mensagens.filter((mensagem) => deveExibirMensagem(mensagem));
      const assinatura = JSON.stringify(visiveis.map((mensagem) => [
        mensagem.id,
        mensagem.updated_at,
        mensagem.ativo,
        mensagem.titulo,
        mensagem.conteudo,
        mensagem.tipo,
        mensagem.publico,
      ]));

      const possuiAlertsRenderizados = container.querySelector('[data-cad-msg-alert]') !== null;

      if (assinatura === lastSignature && possuiAlertsRenderizados) {
        return;
      }

      lastSignature = assinatura;
      container.innerHTML = '';

      visiveis.forEach((mensagem) => {
        container.appendChild(criarAlert(mensagem));
      });
    };

    if (!endpoint) {
      return;
    }

    const atualizarMensagens = () => {
      const urlObj = new URL(endpoint, window.location.origin);
      urlObj.searchParams.set('_t', String(Date.now()));
      const url = urlObj.toString();

      fetch(url, { headers: { Accept: 'application/json' } })
        .then((response) => (response.ok ? response.json() : []))
        .then((mensagens) => {
          if (!Array.isArray(mensagens)) {
            return;
          }

          renderizarMensagens(mensagens);
        })
        .catch(() => {
        });
    };

    atualizarMensagens();
    setInterval(atualizarMensagens, refreshMs);
  })();
</script>
